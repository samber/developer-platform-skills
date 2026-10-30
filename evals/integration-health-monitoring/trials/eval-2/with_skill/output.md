# Sanity check on the "92%" and the report Kestrel needs before announcing

**Verdict: the 92% can't support a retirement decision.** It may be accurate as a count, but it doesn't measure what you need. I couldn't see your data, so I haven't verified the number. I'm questioning what it measures.

## What the 92% measures

It is the share of active accounts whose default setting is on a newer version. Retiring 2024-06-01 depends on who is still served that version. The two can differ a lot.

1. **Account default is not the version served.** Kestrel customers can set a version in several places: the account default, a per-request header, the SDK release (Java, Go and Node pin the version of their release date), and each webhook endpoint separately. An account can show `default_version >= 2025-03-01` and still send 2024-06-01 in a header, run an old SDK, or receive 2024-06-01 payloads on a webhook. The report can't see any of that.
2. **The default is set at signup, so the figure is probably inflated by new accounts.** Every account created after 2025-03-01 passes the test without ever using 2024-06-01. The 92% counts them as migrated, but they never needed to migrate. The accounts that matter are the older ones.
   - Split the figure by signup cohort, and check whether the default can be changed after signup.
   - If it can't, then no account has migrated by changing it. Any real migration shows up in headers, SDKs or webhooks.
3. **"Active" probably hides seasonal integrations.** Check the window behind "active". Monthly invoicing, quarterly reporting and year-end close all call once and go quiet. A 30- or 90-day window drops them from the denominator, and they break on their next run after the cutoff.
4. **It counts accounts, not integrations or owners.** One partner app installed across 2,000 customer accounts is one fix and 2,000 breakages. An account can also run several integrations (a Node service, a Java batch job, a webhook consumer), and only one needs to be on the old version for the account to break. "8% of accounts left" can mean dozens of integrations, or one very large one. Sunsets that went wrong were mostly judged on the share of traffic or accounts moved, while the remaining few integrations had unknown owners.
5. **The remaining 8% doesn't tell you who is on 2024-06-01.** Accounts with a default below 2025-03-01 may be on older versions or on versions between the two. Only the ones actually served 2024-06-01 matter.
6. **Nothing here establishes ownership or reachability.** An accounts table can't say whether the signup email still goes to a person who can act. Notices sent to the credential holder's address are a common failure: the person who must act is often two hops away.

**Don't use any of these to justify the date:**
- "92% migrated"
- "only 8% left"
- A call-volume share

## The report you need

Build a **census**: one row per integration identity (API key ID, OAuth client ID or app ID) per risk, not per account.

**Catalog of what breaks on the retirement date.** Each row needs the surface, the date and the replacement:

| Risk row | Signal |
|---|---|
| API requests served 2024-06-01 | Version resolved per request at the gateway (header, then SDK or client pin, then account default) |
| Webhook endpoints on 2024-06-01 payloads | Version configured on each endpoint. This is configuration, not traffic, so no window applies. |
| Java, Go and Node SDK releases pinned to 2024-06-01 | SDK name and version header on requests |
| Dormant credentials | Last-used date, compared against the longest business cycle |

**Fields per row:**
- Integration identity, integration shape (single-account, fleet app or partner, plugin or agency), and owner account.
- Calls in the lookback, first and last call on 2024-06-01, and first call on the replacement.
- Served version, split into header, SDK and default.
- Each webhook endpoint's version.
- End customers or installs behind it.
- Days to break.
- Contacts (technical, commercial, and customer admin for fleets) and the date each was last verified.
- Notice and ladder state, acknowledgment, exception and expiry, and a dispute flag.

**Lookback.** Set it to your longest business cycle, which is probably 12 months or more if year-end close runs through your API. Don't use 7, 30 or 90 days.
- Check log retention first. If it is shorter than the lookback, mark those rows **unknown**, never migrated, and start retaining for the full cycle now.

**"Migrated" definition.** A row counts as migrated only if one of these holds:
- There were no calls on 2024-06-01 for one full lookback after the first call on the replacement.
- The owner confirmed in writing that every job has moved.

One call on the new version proves nothing. A daily sync can move while a year-end job still calls the old version.

**Also report these separately:**
- **Unattributed share.** This is calls with no credential identity. On authenticated routes it should be zero, and any non-zero value is a logging gap to fix first. On public routes it is the floor of what you will break blind.
- **Dormant credentials.** List them with their last-seen date. Don't treat them as migrated, and don't expire them inside this program. Seasonal jobs would break, so route confirmed-abandoned ones to normal key revocation.
- **Shared tokens.** Agencies and resellers reuse partner tokens, so each report needs a "dispute this attribution" path.

**Ranking.** Bucket rows by days to break, then sort by end customers affected. Never sort by call volume. Add a commercial-weight column for contracts and strategic accounts.
- Split into a top tier (named outreach, sized by the hours you can spend) and a long tail (automated ladder).

**First query** (this answers "who is behind the residue"). Group gateway calls served 2024-06-01 by credential over the lookback. For each credential, join:
- first and last call on 2024-06-01
- first call on the replacement
- owner, integration shape, and accounts or installs behind it
- contacts and their verification date

Sort by end customers, and add live keys with zero recent calls flagged as dormant. Put calls with no credential into one summary row with weekly counts and top client fingerprints.

## What to do about the announcement

1. **Don't hold the announcement for the census.** The notice window belongs to your versioning policy. Send the first notice now to every contact on file, with an in-response `Deprecation`/`Sunset` header on 2024-06-01 responses. Put the ownership confirmation request in the same message.
2. **Stop new integrations starting on 2024-06-01.** New accounts, app registrations and webhook destinations get the replacement version by default. Keep rotated keys and new installs of existing apps on their current version until their break date.
3. **Check the window.** Today is 2026-10-30, so "end of next quarter" is about 2027-03-31, roughly five months away. If your published policy promised longer (large platforms publish about 12 to 24 months), shortening it is a policy change. Settle that before announcing.
4. **If five months is all you have,** use the compressed schedule: send at once, at the midpoint and one week before each brownout, and start named outreach for the top tier now.
5. **Ladder.** Send a targeted email monthly to each integration still calling, plus the in-response header. Do named outreach for every top-tier row. Add announced, escalating brownouts last (for example 4 hours, then 12, then 24), returning the final-state error with the schedule in the body and `Cache-Control: no-store`.

## The go/no-go gate

The decision-maker should see a line-by-line verdict, not a date and a percentage. All five lines must hold:

1. Every top-tier integration is migrated under the rule above, or covered by an exception.
2. Every long-tail integration is notified at a verified contact, or routed to its customer admin.
3. Unattributed calls are zero on authenticated routes and below a floor you defend on public ones.
4. The replacement version has met its service objective for several weeks (at least one brownout interval), with no open incident and headroom for the residual load.
5. Every exception has an owner, a reason and an expiry date.

Grant exceptions per credential, never a global extension. A global slip teaches every integrator that dates move.

Track two curves weekly: calls on 2024-06-01, and integrations still on it. The calls curve falls first and flatters progress. The gate reads the integrations curve.

## Questions that change the plan

1. Is every request tagged with a credential identity at the gateway, and does the gateway log the resolved version per request?
2. What is your longest business cycle, and how long do you retain logs?
3. Who builds against you: customers' own engineers, partner apps installed across many accounts, or plugins and agencies? Which of these exist?
4. What does "active" mean in the PM's report?
5. Can the default version be changed after signup, and which accounts have changed it?
6. What contact do you hold per integration, when was it last verified, and do you track bounces?
7. Is the 2027-03-31 date fixed by contract, security or cost? What can you spend: engineering weeks, a partner team's hours, an account manager per top integration?
8. What does retirement do: hard cutoff, or fall-forward to a newer version? That is a policy decision.
9. Is the replacement version stable and complete for the use cases that are migrating? If not, escalation past a reminder is unfair.

## Cheapest first step

Run the first census query on the gateway logs. It gives you per-credential rows and the unattributed share within days. If the logs don't carry the resolved version or the credential, fix that first, because every other number depends on it.