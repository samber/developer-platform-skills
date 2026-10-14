**Next action, today:** ask whoever signs breaking changes if the 1 Feb date holds (step 1 below). Then build the v1 caller report.

I couldn't interview you, so I'm working from stated assumptions. Section 6 lists the questions that would change the ranking.

## Route

**`api-versioning-policy`.** It owns notice windows, sunset signalling, enforcement and breaking-change governance. A sunset date moves it to rung 1.

**Gap:** the collection has no skill for tracking which callers are still on a deprecated version. `integration-error-observability` shows errors as they happen. It does not track version drift across the fleet. The v1 caller report below is therefore plain engineering, not a skill. The migration guide belongs to a sibling collection, not this one. I recommend installing `samber/developer-relations-skills` and using its `version-migration-guide`.

## 1. Check the date first

- **Notice window.** 2 Aug to 1 Feb is 183 days. Six calendar months from 2 Aug ends on 2 Feb, so 1 Feb may be one day short of your own stated policy.
- **Who counts.** Check how the policy counts: from send or from receipt, and whether bounced or role-mailbox recipients count. The date is a public commitment that legal and sales co-own, so don't decide it alone.
- **Cheapest fix.** Treat 1 Feb as the start of enforcement, not the hard-off.
- **Calendar collision.** 1 Feb 2027 is a Monday, and the first-of-month billing runs fire that morning. 31 Jan is the last month-end run before the cutoff.
- **Time left.** Today is 8 Oct, so 116 days remain.

## 2. What to set up: a nightly v1 caller report

This is a scheduled job over your gateway or access logs, with these steps:

1. **Group by caller.** Count every `/v1` request by API key or OAuth client ID. Record these columns:
   - endpoints hit
   - SDK or User-Agent version
   - first seen
   - last seen
   - request count
2. **Keep a permanent aggregate table.** Store the key, endpoint, first/last seen and count. It holds no payloads, so it survives log retention.
3. **Use a long lookback.** Billing integrators call on month-end, quarter-end and year-end cycles, and a 24-hour window misses them. You get only three full month-end observations before the cutoff (31 Oct, 30 Nov, 31 Dec). The 31 Jan run lands one day before the cutoff. Callers that only run at month-end may stay invisible until then.
4. **Join to your account list.** Sort callers into three groups:
   - in the 260 integrators who received the email
   - on v1 but not in the 260 (unknown owners)
   - in the 260 but silent for 90 days
5. **Diff against the previous run.** Alert on new v1 callers, since each one means a gap in your list. Mark callers who disappear as migrated.
6. **Output channel.** I need you to pick one: a pinned ticket in the platform team's tracker, plus one message in the platform channel. The report names integrators with their traffic, so the channel must be covered by your data policy.

**Rough time:** 2 to 3 hours for a one-off backfill if your logs are queryable. About a day to schedule it and add the diff.

## 3. This week (Thursday 8 Oct to Friday 16 Oct)

1. **Thu, 30 min.** Name the contract owner and the breaking-change signer. Put the 183-day question and the 1 Feb vs hard-off split to the signer.
2. **Thu to Fri.** Run the backfill and write the report. Output: v1 callers by key, endpoints and last seen.
3. **Fri.** Join the report to the 260 and sort callers into the three groups. List the v1 endpoints still called that have no v2 equivalent. Each one is a blocker that can move the date.
4. **Fri.** Draft one outreach message per active caller: their keys, endpoints, last-seen date, the sunset date and the migration guide link. Don't send it until the signer confirms the date.
5. **Mon, after sign-off.** Add `Deprecation` and `Sunset` headers to v1 responses (RFC 9745 / 8594). Callers who ignore email then get a machine-readable signal. The `Sunset` value must match the confirmed date. Ship it behind a feature flag. About half a day.

## 4. Short-list, highest value per unit of effort first

**Re-rank:** the announced sunset (Q5b) moved `api-versioning-policy` and `integration-error-observability` to the top. The rest keep their default order.

1. **`api-versioning-policy`.** Attacks: an enforcement plan that doesn't exist yet, plus a date that may fall short of your own policy. Cost: one session, plus sign-off outside engineering.
2. **`integration-error-observability`.** Attacks: you can't enforce a cutoff without knowing who still calls v1. Cost: low if you stay on the partner-notification and fleet-view parts. A new log store is a surface you then run forever.
3. **`public-api-design-review`.** Attacks: moving 260 integrators onto a v2 with design flaws means a second break. Cost: one session over an existing spec, no deploy.
4. **`api-error-design`.** Attacks: v1 callers who hit a retired endpoint need a clear, machine-readable "version retired, go here" error. Cost: one design session plus an additive backend change on the v1 error path.
5. **`api-reference-quality`.** Attacks: the v2 reference is the migration path, and gaps there stall migrations. Cost: near-free if a v2 spec is committed.

There is no chain this week, so I'm not inventing one.

## 5. Routines (dry run, nothing installed)

1. **Deprecation-window sweep → `api-versioning-policy`.** Weekly, Monday 09:00, until sunset. It counts remaining v1 callers by status (not contacted, contacted, acknowledged, migrated) and flags anyone behind. The skill anchors this a full notice period ahead of the cutoff, and 2 Aug has passed, so start it now. Output: a comment on the pinned ticket.
2. **Pre-release design review → `public-api-design-review`.** Event trigger on any v2 spec diff during the migration window. Output: a comment on the pull request. Skip it if you already run a weekly API review board.
3. **Kickoff re-invocation.** Fires on 2 Feb, then quarterly. Output: a diff to `developer-platform-context.md`. I'd pick this over a calendar date because it follows your own sunset date.

I did not propose the fleet-health review, because nobody owns contacting integrators yet.

## 6. Not now, and open questions

**Not now:**
- `sdk-portfolio-strategy`: after the report shows whether SDK versions drive v1 traffic.
- `api-idempotency-retry`: after the v2 design review flags retry or double-charge risk.
- Macro strategy, ecosystem and new-surface skills: after the sunset lands.

**Questions that would change the ranking:**
1. Who integrates: customers' own engineers, partners, or third-party app builders?
2. Who signs a breaking change, and who owns the contract day to day?
3. How much effort can you spend: hours, a week, or a standing few hours every week?
4. How long do your gateway logs retain data?

## 7. `developer-platform-context.md`

I didn't write this to disk because the working directory isn't the Kestrel Billing repo. Commit it at that repo's root:

```markdown
# Developer platform context - Kestrel Billing

## Audience
260 integrators (type unconfirmed).

## Surfaces
- /v1: sunset announced 2026-08-02, date 2027-02-01, under review (183-day notice, one day short of six calendar months).
- /v2: assumed live. Unconfirmed.

## Owners
- Contract owner: unconfirmed.
- Breaking-change signer: unconfirmed.

## Constraints (2026-10-08)
- Sunset 2027-02-01 (Monday). Standing horizon. Effort ceiling unconfirmed.

## In flight
- v1 caller report (nightly).
- Date sign-off.
- Sunset headers.

## Decided
- Sunset announced to all 260 integrators on 2026-08-02.

## Open
- Hard-off date.
- Owner of integrator follow-up.

## Session log
- 2026-10-08: cold start, routed to api-versioning-policy, gap named for v1 drift tracking.
```

**Memory:** I wrote none. If you add one, keep integrator names tied to traffic, keys and contract terms out of it. Show the diff before any commit.

**Next:** message the breaking-change signer with the 183-day question.