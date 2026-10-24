# Sanity check: `new_ticket` fix plan

**Verdict:** Keep the sort and page-size fix and ship it. Drop the REST hook swap from this release, and don't run `migrate … 100` straight away. I answered from my knowledge of the Zapier platform, not live docs. Confirm the two items marked "verify" before acting.

## 1. Newest-first plus a bigger page: correct

Zapier expects polling triggers to return newest-first and dedupes on `id`. With oldest-first and 25 per page, a Monday burst pushes new tickets onto page 2. A non-paginating poll never reads page 2, so those tickets are missed. This diagnosis is probably right.

Before you ship:

- **Page size 200 is not lossless.** If more than 200 tickets arrive between polls, you lose some. Polling runs every 1 to 15 minutes depending on the customer's plan.
  - For a real fix, set `canPaginate: true` and use `z.cursor`. Zapier then fetches further pages until it reaches already-seen ids (verify in the CLI docs for your platform version).
  - This only works if the sort is strictly by creation time, newest first, not by `updated_at`.
- **Check the API's max page size and latency.** Polling requests time out at about 30 seconds.
- **Expect a one-time burst after migration.** If Zaps currently miss tickets, those tickets are not in their dedupe memory. The first newest-first poll of 200 can fire old tickets, which burns users' task quotas and may trigger emails or Slack messages to their customers.
  - Bound `performList` to a recent window (for example, created in the last N hours).
  - Test this on a staging Zap before migrating anyone.
- **Keep `id` stable and unique.** Dedupe depends on it.

## 2. Switching `new_ticket` to a REST hook in place: don't

This is the main flaw in the plan.

- **Existing Zaps never subscribe.** `performSubscribe` runs when a Zap is turned on or created. Migrating about 600 users' running Zaps from 1.4.0 to 1.4.1 does not call it. Those Zaps would have no webhook and would go silent, which is worse than missing some tickets today.
- **Changing trigger type is a breaking change.** Zapier's guidance is that migration is only for backward-compatible changes. A patch number like 1.4.1 also hides the severity.
- **Output shape must match exactly.** The hook payload has to produce the same fields as the polling items. Otherwise every existing field mapping, filter, and the four templates break.

Do this instead:

1. Keep `new_ticket` as polling and fix it (section 1).
2. Add a new trigger, `new_ticket_instant` ("New Ticket (Instant)"), as a REST hook in a later version.
3. Later, hide or deprecate the old key and tell users. Don't force-migrate them.

Requirements for the REST hook when you build it:

- `performSubscribe` stores the webhook `id` in `subscribeData`.
- `performUnsubscribe` deletes exactly that webhook. Your per-callback delete endpoint supports this.
- `perform` reads `bundle.cleanedRequest` and returns an array.
- `performList` returns newest-first sample data with the same shape as the hook payload.
- Verify webhook signatures and subscribe only to the ticket-created event.
- Confirm your API's webhook retry policy. With no polling fallback, a failed delivery is a lost ticket.
- Plan for orphaned webhooks when unsubscribe fails. Run a periodic cleanup.

## 3. Rollout timing and `migrate … 100`

Today is Friday 2026-10-23, so "tomorrow" is Saturday and the busy Monday follows right after.

- **Promotion of a public integration may need Zapier review (verify).** If so, "promote tomorrow morning" isn't in your hands.
- **Don't go straight to 100%.** The CLI supports `--user` for a single account and a percentage argument. Use them:
  1. Migrate a test account with `--user`.
  2. Migrate 10%, then watch errors, poll duration, and task counts.
  3. Migrate 50%, then 100%, ideally by Sunday evening.
- **Know your rollback.** Migrating back, `migrate 1.4.1 1.4.0`, should work, but check the docs first.
- **Don't bundle three changes.** Sort, page size, and trigger type in one release makes any regression hard to attribute. Ship the polling fix alone.

## 4. The four Zap templates

- If you keep `new_ticket` as polling, the templates keep working.
- If you later point them at `new_ticket_instant`, update and republish them. Zapier may review the changes.
- If you hide or deprecate `new_ticket`, confirm the templates still resolve. Hidden triggers can cause template problems.
- After promotion, build one Zap from each template and check that field mappings still fill in.

## Suggested sequence

1. **Tonight:** build 1.4.1 with newest-first, a bounded window, and a page-size cap (or `canPaginate`). Test with a staging Zap, including the first-poll burst check.
2. **Saturday:** promote if Zapier allows it. Then migrate one user, 10%, 50%, and 100% as above.
3. **Next sprint:** add `new_ticket_instant` as a separate trigger and test the subscribe, unsubscribe, and payload parity cases. Then update the templates.
4. **Later:** deprecate the polling key without forcing users off it.

Two questions would sharpen this: what filter does your list endpoint apply (status or time window), and does your webhook delivery retry on failure?