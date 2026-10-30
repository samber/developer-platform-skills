**Verdict: NO-GO for Dec 1.** Keep Jan 15 and run the program below. The evidence you gave can't support a cut on either date, and Dec 1 collides with your own customers' calendars.

**Next action, under 2 hours:** run the census query in step 1, over at least 12 months of gateway logs, grouped by credential. I haven't seen your logs, so every line status below is unknown until you run it.

## Why Dec 1 fails

- **0.4% is a call share, not an owner count.** The gate reads integrations still on v1, not traffic. Big integrators migrated first (31% → 0.4%), so the calls curve falls early and looks finished long before the integrations curve does.
- **30 days is the wrong window.** Marketplace settlement runs monthly, quarterly and annually. A 30-day lookback counts a quarter-end or year-end job as migrated, and it breaks on its next run.
- **Dec 1 lands on the Nov 30 month-end exports.** It also cuts off every Dec 31 quarter-end and year-end run.
- **Jan 15 is also tight.** It leaves about two weeks after Dec 31. Year-end jobs that run later in January or Q1 will need per-integration exceptions.
- **Pulling the date in is a policy change, not a burn-down result.** Today is Oct 30. Dec 1 gives integrators 32 days, where they planned for 77. That cuts 45 days from a notice you published. A "nearly nobody left" call share never justifies this on its own.
- **A cut doesn't end the on-call cost.** After cutoff you keep the v1 code path deployable behind an allowlist for one full lookback. The saving is smaller than your VP expects.

## Readiness gate, status today

```
Surface: POST /v1/charges   Proposed: 2026-12-01   Announced: 2027-01-15
Verdict: NO-GO 2026-12-01. Jan 15 stays; revisit after census.

Line 1  top-tier not migrated (12-mo lookback, or written confirmation): UNKNOWN
Line 2  long-tail without verified contact: UNKNOWN
Line 3  unattributed v1 calls: must be 0 (authenticated surface); any >0 = gateway logging gap, fix first
Line 4  /v2/payment_intents met its SLO for migrated traffic, last several weeks, with headroom for residual load: UNKNOWN
Line 5  exceptions without owner, reason and expiry: 0 (no register yet)

Cost of waiting 6 weeks: <on-call weeks>.
Cost of cutting early: <customers x failed settlement runs>.
```

Line 4 also covers feature parity. Confirm payment_intents carries the marketplace flows: splits, payouts and reporting.

## Plan

I'm using today's date of Oct 30, 2026. The 77 days left is shorter than three monthly notice intervals, so notices follow the compressed schedule: send now, again at the midpoint, and one week before each brownout.

**Step 1 (Mon Nov 2): census and attribution**
1. Check log retention against the longest cycle (annual). If retention is shorter, mark those rows unknown, never migrated, and start retaining a full cycle now.
2. Group v1 charge calls by credential over that window. Join in:
   - first and last v1 call, and first v2 call
   - owner account and integration shape
   - installs behind it, and contacts with their verification date
3. Put dormant credentials in the same table, flagged dormant. Don't expire or revoke them in this program: the seasonal ones break.
4. Record the served version per request. Account default alone misses header pins, SDK pins and webhook endpoints.
5. Put calls with no credential in one summary row.
6. Sort by end customers affected, never by call volume.

**Step 2 (this week): close the door and send notice**
- New accounts, app registrations and webhook destinations get pinned to v2.
- Rotated keys, new tokens and new installs of existing apps keep v1 until their break date. Blocking them breaks integrators inside the window you promised.
- Flag directory listings that still call v1. Block new installs only after the surface passes its date.
- Add `Deprecation` and `Sunset` headers to every v1 response, with a pointer to the migration guide.
- Send the targeted email to every contact on file, with the confirmation request in the same message. Don't hold the notice for verification. Send to integrations that called v1, not to all developers.

Targeted email, normal prose because it goes to other people:

> Subject: [Action needed by 2027-01-15] <App name> still calls POST /v1/charges
>
> Your integration <App name> (client ID <id>) called POST /v1/charges <N> times in the last 12 months, most recently on <date> (request <req_id>).
>
> POST /v1/charges stops working on 2027-01-15 00:00 UTC and returns an error. Replacement: POST /v2/payment_intents. Migration guide: <link>.
>
> Reply to confirm you own this integration, and give the date you expect to ship the change. This includes month-end, quarter-end and year-end jobs. If this is not your integration, reply "not mine" and we will correct it.

**Step 3 (Nov 2–20): named outreach to the top tier**
- Top tier = partner apps and marketplace platforms. Rank by installs or sub-merchants, then add a commercial-weight column for contract terms and strategic accounts.
- Size it by the account-manager hours you have. Take rows from the top until the hours run out.
- One call per fleet app fixes every install. Each call needs:
  - the census row and two sample request IDs
  - the migration guide and a named engineer on your side
  - the ask: a named owner and a ship date, **in writing**, covering every job (month-end, quarter-end, year-end)
- Mark a row migrated only when one of two things holds:
  - no v1 call for a full lookback after its first v2 call, or
  - the owner's written confirmation that every job moved.
- Under an annual lookback, expect most top-tier rows to close on written confirmation or an exception.

**Step 4: customer-admin notice**
- Send it for apps whose developer stays unverified or silent. The admin can uninstall the app, push the vendor, or fix it themselves.
- Get legal or partner-management sign-off first. The notice tells a partner's customers about the partner's integration.

**Step 5: brownouts, only if line 4 holds**
- Proposed schedule, not yet announced:

| Window | Start | Length |
|---|---|---|
| 1 | Tue Nov 17, 14:00 UTC | 4 h |
| 2 | Tue Dec 8 | 12 h |
| 3 | Tue Jan 5 | 24 h |

- Announce each window in the changelog, the email and the error body, one week ahead.
- During each window return the final-state error. Put "temporary brownout" and the schedule in the error body, and send `Cache-Control: no-store`.
- Start inside working hours for the affected regions. Pause if the replacement has an incident.
- Check the brownouts against your SLA terms first.
- Brownouts can't catch quarter-end or year-end jobs that don't run in the window. That is why step 3's written confirmation matters more.

**Step 6: exceptions, not a global slip**
- Give each year-end closer an allowlist entry keyed to its credential. Record the owner, the reason, and a single expiry.
- Slip the date for everyone only if line 4 fails.

**Step 7: weekly burn-down**
- Track integrations remaining (top tier and long tail), calls, unattributed calls, and new integrations starting on v1 after the door closes. The target for new integrations is zero.
- Re-run the worksheet one week before each brownout and before Jan 15.
- Failed line 1 goes back to named outreach. Failed line 2 goes back to contact resolution. Failed line 3 goes to the logging fix.
- Keep the v1 code path behind the allowlist for one lookback after cutoff.
- A caller the census missed gets an emergency exception with a two-week expiry, never a global rollback.

## If your VP wants a lower on-call bill

These levers are my suggestions, not part of the skill:
- Freeze v1 code, so only security fixes ship.
- Page only on v1 errors for top-tier credentials.
- Let the Jan 15 date stand.

If the census shows every top-tier row closed and the gate passing, the VP can ask `api-versioning-policy` for an earlier date. The gate must pass at that date, for notice owners who actually received it.

## Questions that change this answer

1. Is Jan 15 fixed by contract or security, or just a choice?
2. Do you have a gateway tag per credential today, and what share of v1 calls carries none?
3. How many of the 60 partner apps are fleet apps, and what are their install counts?
4. What contact do you hold per app, and when did you last confirm it?
5. How many weeks of account-manager time can you spend?
6. Is the v2 SLO green for the last 6 weeks, and does it cover the marketplace settlement flows?

Answers to 1, 5 and 6 move the plan most: they set the brownout timing, the size of the top tier, and whether line 4 passes at all.