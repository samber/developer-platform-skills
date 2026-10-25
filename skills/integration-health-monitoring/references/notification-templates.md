# Notification Templates

Contact resolution, the notice payload, and one template per ladder rung.

## Contents

- Contact resolution procedure
- The notice payload
- Cadence rules
- Templates

## Contact resolution procedure

1. Pull every contact on record for the integration: developer account, app owner, emergency or technical contact, billing contact.
2. Add the installing customers' admins for fleet apps and plugins. Several providers fall back to the customer side when the developer is silent: the merchant, workspace admin, tenant admin, org admin or site admin.
3. Put the confirmation request inside the first notice, sent on notice day. Never hold the notice for verification: the window belongs to the policy.
4. Record bounces, auto-replies and "left the company" replies as unverified.
5. Escalate unverified rows to the commercial owner, then to the customer admin.
6. Write the verification date on the census row. Re-verify at each new sunset; contacts rot between them.

Shared mailboxes and bot accounts receive notices nobody reads: one provider's per-token emails went to the bot account that held the token. Ask for a human contact when the address on file is a service account.

## The notice payload

Every notice, on every rung, carries:

- Integration identity, in the partner's own terms: app name, key prefix, client ID.
- The surface: endpoint, field, version, auth method or payload version.
- Evidence: call count over the lookback, last-seen time, one sample request ID.
- The break date, in UTC, and what happens on it: error code, or fall-forward behavior.
- The replacement and the migration guide link.
- How to acknowledge, and how to dispute the attribution.

## Cadence rules

- Send targeted email monthly per integration still calling. One provider started every 3 days per token and moved to monthly: high cadence reads as spam and gets filtered.
- Stop the cadence for a row once it acknowledges; switch to a reminder only if calls continue past the date it gave.
- Stop entirely when calls reach zero across the full lookback.
- Short windows: follow the compression rule in SKILL.md step 7.
- Never mail integrations that never called the surface. A blast to every developer trains the affected few to ignore the next notice.

## Templates

**Confirmation request (standing practice, between sunsets):**

```
Subject: Confirm the owner of Ledgerline Sync (client ID cl_7f3a...)

We use this address to warn you before changes that could break Ledgerline Sync.
Reply "confirmed" if you maintain it, or send the address of whoever does.
No reply in 14 days and we will route future notices to your account's admin.
```

**Targeted email (default rung):**

```
Subject: [Action needed by 2027-03-31] Ledgerline Sync still calls /v1/invoices

Your integration Ledgerline Sync (client ID cl_7f3a...) called GET /v1/invoices
312 times in the last 12 months, most recently on 2026-12-29 (request req_8c1e...).

/v1/invoices stops responding on 2027-03-31 00:00 UTC and will return 410 Gone.
Replacement: /v2/invoices. Migration guide: <link>.

Reply to confirm you own this integration and the date you expect to ship the
change. If this is not your integration, reply "not mine" and we will correct it.
```

**In-response warning (default rung, alongside email):**

```
Deprecation: @1767225600
Sunset: Wed, 31 Mar 2027 00:00:00 GMT
Link: <https://docs.example.com/migrate/invoices-v2>; rel="deprecation"
```

Pair the headers with a short warning in the response body when your consumers read bodies more than headers.

**Customer-admin notice:**

```
Subject: An app installed in your account will stop syncing invoices on 2027-03-31

Ledgerline Sync, installed in your account, uses an API we retire on 2027-03-31.
We have notified its developer. After that date the app will stop syncing invoices
unless they update it. You can contact the developer, check for an app update, or
plan a replacement.
```

Clear this template with legal or partner management first: it tells a partner's customer about the partner's integration.

**Brownout announcement:**

```
Scheduled brownouts for /v1/invoices: 2027-02-03 from 14:00 UTC for 4 h,
2027-02-17 from 14:00 UTC for 12 h, 2027-03-03 from 14:00 UTC for 24 h.
During each window /v1/invoices returns 410 Gone, as it will after removal, with
"temporary brownout" and this schedule in the error body, and Cache-Control: no-store.
Permanent removal: 2027-03-31.
```

**Dashboard drift report (one row per surface, per integration):**

```
Surface            Calls (365 d)  Last seen    Sample request  Breaks on    Replacement
GET /v1/invoices   312            2026-12-29   req_8c1e...     2027-03-31   /v2/invoices
Webhook payload v1 1 endpoint     live         ep_44a0...      2027-06-30   payload v2
[Dispute this attribution]  [Mark as migrated - we confirm every job moved]
```

**Named outreach brief (what the partner or account manager brings to the call):**

- The census row: surfaces, call counts, last seen, installs affected, break date.
- Two sample request IDs the partner's engineer can look up.
- The replacement, the guide, and the person on your side who answers technical questions.
- The exception path and its conditions, offered only if the date cannot be met.
- The ask: a named owner and a ship date, written into the census row after the call.

**Exception grant:**

```
Exception for Ledgerline Sync on /v1/invoices until 2027-05-31.
Reason: year-end close runs in April. Owner: <name>. No further extension.
```
