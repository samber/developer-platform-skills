**Do not wait until next quarter. Start today, with one action: freeze his access, then inventory his keys.**

Assumption: I could not ask the skill's clarifying questions. I assume Corvid Metrics owns these four credentials and the platform where they were issued. If a vendor issued them, the same plan holds. The inventory step becomes "ask the vendor for an audit list".

## Why "still works" is the problem

- A key that works after its owner leaves is the failure the skill calls "invisible infrastructure". It has no owner, no documented scope, and no expiry.
- Offboarding is the compromise case. The skill says revoke with zero grace and accept the downtime. It says to treat a production integration on a personal key as a standing incident.
- Unbounded exposure is the base case. GitGuardian found 64% of valid secrets leaked in 2022 were still valid years later. A leaked key is also invisible to you.
- Routine HR or IdP automation can delete his account at any time. If deletion kills his keys, Salesforce sync, billing, and both customer integrations fail together. No one would know why, and the fix would be under pressure instead of planned.
- He knows these keys exist, and nobody can see what he could see. That makes a silent loss of control likelier than a silent breach.

## Plan

**Today, about 2–4 hours**

1. Suspend his console, SSO, and VPN logins and revoke his sessions. Do not delete his user yet. Check first whether suspending kills his keys. If it does, do step 4 before suspending.
2. Build the inventory without a dashboard. Use these sources:
   - Secrets managers and CI variables.
   - Config of the four known consumers.
   - Gateway or access logs, grouped by key prefix or last four characters.
   - A DB query on `created_by`, if you own the platform.
   - A vendor support request for "all keys created by user X".
   - Scan git history for his commits.
3. For each key, record the consumer, the permissions it has, who owns the consumer, and when it was last used. Assume the four known keys are not the full list.
4. Create a service account or org-owned identity per integration. Use one key per service per environment, restrictive scopes, and an expiry. Keep his old keys active until cutover.

**This week, about 1–2 days for the four known integrations**

5. Cut over staging first, then production. Schedule the billing cron change away from a billing run. Watch last-used on the old key until it reaches zero traffic.
6. Revoke every key he created or could see, with zero grace. Disable first, wait 24–48 hours, then delete. Do not delete an old key before last-used shows zero.
7. Rotate every shared credential he could read. Check webhook secrets, DB passwords, the Salesforce connected-app secret and integration user, CI secrets, and cloud keys. Log every action with who, when, and why.

**Next quarter**

8. Build the missing admin view. It filters keys by creator or by who can see them. It shows label, owner, scope, last used, status, and expiry. Add mandatory expiry, expiry warnings, an audit log of create, use, rotate, and revoke, and default new production keys to service accounts. In the meantime, a saved query or script is enough.

## Customer-facing integrations

- If customers hold keys he created, revoking breaks them. Zero grace is the skill's default. Giving customers a short, noticed deadline of days is a deliberate deviation.
- The boss should decide that tradeoff and write it down. Do not drift into it.
- Billing and Salesforce are internal. Cut over and revoke on the schedule above.

## What to tell your boss

The choice is not "now versus next quarter". It is a one-day containment, a roughly two-week migration, and a quarter for the platform fixes. The fixes are the admin view, expiry, and service-account defaults. Until step 6, any single account deletion can cause a four-system outage, and a leaked key stays live.

**Next action:** open the secrets manager and CI variables, and list every key with his name or email on it. This takes about 20 minutes.