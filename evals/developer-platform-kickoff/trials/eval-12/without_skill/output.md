# Kestrel Billing: v1 sunset plan

**Today is 8 Oct 2026. The sunset is 1 Feb 2027, 116 days away.**

## Fix the date first

- 2 Aug plus six months is **2 Feb**, so 1 Feb breaks your own stated notice window by one day.
- Pick one of two fixes this week, before anyone outside notices:
  - Move the sunset to 2 Feb or later, and send a short correction.
  - Define the window as "at least 6 months, ending 1 Feb" and accept the one-day risk.
- I recommend moving to a date with real slack, such as end of February. Missing the gap costs one short email. Cutting off a customer inside your own notice window costs a trust problem and possibly a contract one.
- Also check your terms of service and any enterprise contracts for notice clauses. Some require notice by a named channel, not just email.

## What to set up

### 1. A daily v1 usage snapshot (scheduled job)

This is the foundation. Everything else depends on knowing who calls v1.

- Run it daily from gateway or access logs.
- Group by API key, then roll up to account:
  - Request count in the last 1, 7, and 30 days.
  - First seen, last seen, and top endpoints.
  - User-agent and SDK version.
  - Error rate.
- Write it to a table with one row per key per day, so you can see trends and not only the current state.
- Join it to your 260-integrator list and CRM contact. Tag each key with its account owner.

Check log retention first. If your logs expire in under 30 days, start archiving now.

### 2. Classification (same job, output as a report)

| Bucket | Rule | Action |
|---|---|---|
| Active | Calls in the last 7 days | Personal outreach |
| Dormant | Calls 8–60 days ago | One email, then re-check |
| Migrated | v2 traffic and no v1 traffic for 30 days | Close out |
| Unknown | v1 keys not mapped to any of the 260 | Investigate first |

The "unknown" bucket is the risky one. It includes:

- Keys from integrators who never got the email.
- Downstream customers of platforms and resellers.
- Shared or leaked keys.
- Old SDKs that call v1 without the customer knowing.

### 3. Email delivery audit (one-off, this week)

- Pull bounces, suppressions, and opens for the 2 Aug send.
- A bounced address means that integrator was not notified, so notice has not been given to them.
- Cross-check the recipient list against the account contacts in your database. Billing and technical contacts are often different people.

### 4. Make v1 announce its own deprecation

- Add `Deprecation` and `Sunset` response headers, plus a `Link` header to the migration guide, on every v1 response. Developers and monitoring tools see these without reading email.
- Add a `Warning` field or banner in the dashboard for accounts with active v1 keys.
- Keep the wording factual: the date, the migration link, and a contact address.

### 5. Brownouts (decide this week, run later)

Short scheduled outages of v1 are the best way to find the integrators who ignored email. Suggested schedule:

- Early December: 1 hour.
- Early January: 4 hours.
- Mid-January: 1 day.

Announce each one 2 weeks ahead. Brownout days will create a support spike, so staff for it.

### 6. Alerts and a weekly digest

- Weekly report to you:
  - Active v1 accounts, with the change since last week.
  - Top 10 by volume.
  - Accounts that have not been contacted.
- Alert on:
  - Any new v1 key created.
  - Any account whose v1 traffic goes up.

The new-key alert matters because someone onboarding on v1 now should be stopped. Consider blocking new v1 key creation.

### 7. Escalation ladder (written down now, run by the weekly job)

- **Days 116–90 (now to early Nov):** the first targeted email to every active account.
- **Days 90–60:** personal email from the account owner, plus a call offer to the top accounts by volume.
- **Days 60–30:** brownouts, and calls to every account that is still active.
- **Days 30–0:** daily list of what is left. Decide per account: extend, or cut off.
- **Cutoff:** use a staged shutdown. Return a clear `410 Gone` with a migration link. Do not return a generic 404 or timeout.

## What to work on this week

**Day 1 (Thu 8 Oct)**
1. Decide the date fix above.
2. Confirm gateway log retention, and start archiving if it is short.

**Day 2 (Fri 9 Oct)**
3. Build the first version of the usage query by hand, before automating anything. Just get the list of keys that called v1 in the last 30 days.
4. Do the email delivery audit.

**Day 3 (Mon 12 Oct)**
5. Map keys to accounts and contacts. List the unmapped keys.
6. Classify into the four buckets.

**Day 4 (Tue 13 Oct)**
7. Turn the query into the scheduled daily job and the weekly digest.
8. Ship the `Deprecation` and `Sunset` headers if your gateway supports them. Otherwise schedule it.

**Day 5 (Wed 14 Oct)**
9. Send the first targeted email to the active bucket. Name their endpoints and keys, and include a migration guide link and a named contact. If you changed the date, say so at the top.
10. Draft the brownout calendar and the cutoff plan for review.

## Open questions

These change the plan, so answer them early:

- Do webhooks, SDKs, or payment-provider integrations also carry a v1 dependency?
- Are there contractual SLAs with enterprise customers that outlast the sunset?
- Who owns migration support, and how many hours a week can they give?
- Is the v2 migration guide complete, and is there a feature gap that blocks anyone?

If you tell me your stack (gateway, log store, CRM), I can write the actual query and job definition.