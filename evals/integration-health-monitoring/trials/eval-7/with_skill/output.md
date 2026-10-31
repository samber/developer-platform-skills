# Verdict: don't revoke the 1,400 keys this week, and close the new-key default to v1 first

Security is right that 1,400 dormant keys are attack surface. The plan has two problems:

- Revoking dormant keys doesn't do what you want.
- Leaving new keys on v1 undoes whatever it does achieve.

I haven't seen your data. Everything below follows from the plan as you wrote it, and the open questions are at the end.

## Do first: pin new integrations to v2

Today every new key starts on v1, so new integrations keep joining the surface you are retiring. Your integrations-still-on-v1 curve can rise while you drain it. Microsoft blocked new Azure AD Graph registrations after its cutoff and Shopify blocks new installs of apps calling unsupported resources, for the same reason.

- Default new accounts, new app registrations and new webhook destinations to v2 on notice day.
- Apply this to new integration identities only. Rotated keys, new tokens and new installs of an existing app keep that app's current version until its break date or an exception. Blocking them would break integrations inside the notice window you promised.
- If something really needs a new v1 key for backward compat, grant it a per-credential exception with an owner, a reason and an expiry. Don't keep a global v1 default.
- Report new integrations starting on v1 after the switch. The target is zero.

## Why revoking dormant keys doesn't shrink the residue

- **A dormant key makes no calls.** Revoking it doesn't reduce v1 traffic. It only removes a row from the census.
- **60 days is shorter than your business cycles.** Quarterly reporting, year-end close and annual renewals call once and go quiet. A key idle for 60 days is either abandoned or seasonal and about to resume on v1. Revocation breaks the seasonal ones with a 401, with no notice, no schedule and no date in the error body, and you have no contact to reach.
- **The dashboard would look clean without being safe.** Dormant keys are the integrations most likely to be forgotten. Deleting them hides the risk. The seasonal ones show up as post-cutoff breakage and as the "census misses" your next sunset has to explain.
- **A low call share doesn't mean you can cut off.** "Mostly long-tail" is a call-share statement. The gate reads integrations still on v1 with a verified owner, not calls.

## Plan for this week

Run two tracks. Don't merge them, because sunset work must never expire seasonal keys.

**Track 1: sunset census (v1)**

1. Build one row per credential. Group v1 calls over your longest business cycle, which could be 12 months. Join first and last call on v1, first call on v2, owner, integration shape (single account, fleet app or plugin), installs behind it, contacts and their verification date.
2. Put the 1,400 keys in the same table, flagged dormant with last-seen dates.
3. Check log retention. If it is shorter than the lookback, mark those rows unknown, never migrated, and start retaining for the full cycle now.
4. Send the first notice on notice day to every contact on file, with the ownership-confirmation request in the same message. Include the surface, the key prefix, the call count, the last-seen date, one sample request ID, the replacement, the guide and the break date. Don't hold the notice for verification.
5. Add an in-response warning (`Deprecation`, `Sunset` and `Link` headers) so traffic you can't attribute still sees it.
6. Give the top tier named outreach. Rank by end customers affected and days to break, never by call volume.

**Track 2: dormant-key hygiene (Security's goal, owned by key management)**

1. Split the 1,400 by last-seen date.
   - **Never used, or no call in 12+ months and no seasonal pattern:** candidates for abandonment.
   - **Called in the last 12 months:** possibly seasonal. Don't touch them yet.
2. Send each owner a confirmation request: "Confirm you own this key, or it will be disabled on <date>." No reply in 14 days routes future notices to the account admin.
3. Disable the unconfirmed keys with a reversible suspend rather than a delete. A suspended key can be restored in minutes if a seasonal job wakes up. Delete after a longer quiet period.
4. Treat a key as confirmed abandoned only with owner confirmation, or a full lookback of silence plus an unreachable owner. Hand those to the `api-auth-key-management` revocation flow.

This gives Security most of what it wants within weeks, with a recovery path.

## Dashboard

Show two curves and don't claim "clean":

- Calls on v1.
- Integrations still on v1, split into top tier and long tail, with dormant keys as their own flagged group.

The calls curve falls first and flatters progress. The integrations curve is the one the cutoff gate reads.

## Cutoff readiness against the gate

| Line | Check | Status from your message |
|---|---|---|
| 1 | Top-tier integrations migrated or covered by an exception | Unknown |
| 2 | Long-tail integrations notified at a verified contact or routed to the customer admin | Unknown |
| 3 | Unattributed calls are zero on authenticated surfaces | Unknown |
| 4 | v2 met its service objective for migrated traffic over several weeks, with headroom | Unknown |
| 5 | Every exception has an owner, reason and expiry | No register yet |

Run the gate before any cutoff or brownout. If v1 is not off yet, announce short brownouts, escalating in length, returning the final-state error with the schedule in the body. Grant exceptions per integration. Slip the date for everyone only if line 4 fails.

## Questions that change the plan

1. **Is the Feb 28 cutoff behind you or ahead?** "We sunset" and "v1 traffic is now mostly long-tail" read as past, but v1 still serves traffic. If the cutoff is still ahead, everything above applies. If it has passed, keep the old path deployable behind an allowlist, and give any missed top-tier integration an emergency exception with a two-week expiry instead of a global rollback.
2. **What is the longest cycle any integration runs on?** It sets the lookback.
3. **Is every v1 call tagged with a key, client or app ID?** What share carries none?
4. **Who builds against you, and how reliable are your contacts?** Customers' own engineers, partner fleet apps, or plugins and agencies. What is the bounce rate?
5. **Is v2 stable and feature-complete for the migrating use cases?** If not, no escalation past a reminder is fair.
6. **Is the Feb 28 date fixed by contract or security, or does it have slack?** What can you spend on outreach: engineering weeks, partner hours, account managers?
7. **Why do new keys default to v1?** Is it a real compat need for specific clients, or inertia?

## Next action

Flip the new-key default to v2 for new identities, with a per-credential exception list for any real compat need. Then pull last-seen dates for the 1,400 keys over at least 12 months.