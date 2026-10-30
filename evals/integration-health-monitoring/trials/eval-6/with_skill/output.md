# Quillfeather integration health: what to track and what to show partners

Today is 2026-10-30. I'm assuming the Feb 14, April and June 30 dates fall in 2027. I applied the integration-health-monitoring skill and its three reference files. It says to interview first, so the open questions are at the end, and the plan below states the assumption it makes for each.

## Scope

The skill covers integrations that work today and will break on a known date. Your Datadog per-key error-rate monitors cover integrations failing now, which the skill assigns to `integration-error-observability`. Keep them. Don't fold them into this dashboard or into a blended score. After Feb 14 and after each cutoff, they tell you whether a break happened.

The dashboard answers a different question: who will break on which date, and who do we call.

## 1. Break-date catalog

This is the scope of the dashboard. Only signals that map to a row here get instrumented.

| # | Surface | Breaks | Days from today | Replacement | Who still depends on it |
|---|---|---|---|---|---|
| 1 | Webhook signing certificate rotation | Feb 14 | 107 | New cert, ideally with an overlap period | Every webhook endpoint that pins the old cert or key |
| 2 | iOS SDK 3.x end of life | April (exact date needed) | about 150 to 180 | Current SDK major | Every app shipping 3.x, per release and per install |
| 3 | Webhook payload v1 | Jun 30 | 243 | Payload v2 | Every webhook endpoint configured on v1 |

Rows 1 and 3 are not API calls. A traffic-only census would miss both. They live in webhook endpoint configuration and the signing setup.

Row 2 has no exact date yet. The skill says a risk without a date is not a health signal, so get one before April.

## 2. What the dashboard tracks

Use one row per integration per catalog row. The "identity" is the credential Quillfeather issued (API key ID, OAuth client ID or app ID), never the User-Agent.

**Row 1: certificate rotation**
- Per webhook endpoint, whether it will survive the rotation. The skill gives no signal for this one, because cert pinning isn't visible in traffic. Pick one of the options below.
  - **Overlap:** sign deliveries with both the old and new certs for a window.
  - **Test events:** send a test event signed with the new cert, and record whether the endpoint's response shows it verified the signature.
  - **Owner confirmation:** use the written confirmation from step 4 as the evidence.
- The migrated rule for this row is a verified test delivery or written confirmation. A delivery that happens to succeed proves nothing.

**Row 2: iOS SDK 3.x**
- SDK name and version from the client header, per credential and per app.
- Mobile apps pin the SDK to their release, and an end user's device decides when 3.x stops calling you. The skill says to promote SDK version as a signal in this case.
- Track both the share of active installs still on 3.x and the app-release version where 3.x is embedded.
- Observed traffic lags code. A partner who shipped a fix still shows as 3.x until old app versions stop running. Say so on the report, or the partner will dispute it.

**Row 3: payload v1**
- The version configured on each webhook endpoint, one row per endpoint. This is the cheapest signal, because it reads configuration you already store and needs no new request-path code.
- Do not use the account default. One partner can have an account on v2 and a single endpoint still on v1.
- Endpoints that cannot change version after creation need a second destination on v2. During the overlap every event arrives twice, so the partner's handler must be idempotent.

**Fields on every row**
- Integration identity, shape (single-account, fleet app or plugin/agency), and owner.
- Calls in the lookback, last seen, and one sample request ID.
- End customers affected, which is the ranking key, and days to break.
- Contacts and each one's verification date. An unverified contact counts as no contact.
- Ladder rung reached, acknowledgment date, exception and expiry, and a dispute flag.

**Two settings that change what the numbers mean**
- **Lookback:** use your longest business cycle, not 7 or 30 days. Scheduling partners may run annual or quarterly jobs. A 30-day window would count a partner as migrated when their next run would still break. Where log retention is shorter than the lookback, mark the row unknown, never migrated.
- **Dormant credentials:** list them with their last-seen date, flagged dormant. They are either seasonal or abandoned. Don't expire them inside this program.

**Unattributed share.** Track the share of calls to a catalogued surface that carry no credential identity. On authenticated surfaces any share above zero is a logging gap, so fix that first.

## 3. Which partners to call each week

1. **Bucket by days to break.** Feb 14 comes first, then April, then June 30. A credential or cert event next week outranks a version sunset next year.
2. **Sort within each bucket by end customers affected, never by call volume.** A scheduling platform's fleet partner makes few calls across thousands of customer accounts, and one conversation fixes all of them.
3. **Add a commercial-weight column** for contract terms, penalties and strategic accounts. It can promote a row into the top tier.
4. **Size the top tier by outreach hours, not by a percentage.** Take rows from the top until your weekly hours run out. Everything below gets the automated ladder.

The weekly call list is the top-tier rows that have not acknowledged or confirmed, in that order. Each line gets the named-outreach brief: census row, two sample request IDs, replacement and guide, and a named technical contact on your side. The ask is a named owner and a ship date, written back into the row.

Partners reachable only through a plugin or agency need a different path. The developer fixing the code is not the end, because each site upgrades on its own schedule. Track installs on the fixed release and plan a customer-admin notice as well.

## 4. What partners see

Show each partner only their own rows, with every field they can act on:

```
Surface                 Your usage            Last seen    Sample request  Breaks on    What to do
Webhook cert rotation   endpoint ep_44a0...   n/a          test_91b2...    2027-02-14   verify against new cert: <guide>
iOS SDK 3.x             app "X", 3.4.1        2026-10-28   req_8c1e...     April (TBC)  upgrade to 4.x: <guide>
Webhook payload v1      ep_44a0... on v1      live         ep_44a0...      2027-06-30   switch to payload v2: <guide>
[Dispute this attribution]   [Mark as migrated - we confirm every job moved]
```

- Show the surface, their own counts, last seen, a sample request ID, the break date, the replacement and the guide.
- Add a "dispute this attribution" path. Shared tokens and agency reuse make some rows wrong.
- Keep a "mark as migrated" action that requires them to confirm every job and endpoint moved. That confirmation is a valid migrated rule.
- Do not show other partners' rows, the fleet burn-down, the rank, or internal priority. A rank shown against named competitors turns an operational notice into a commercial dispute.
- Do not show a blended health score. It says something is wrong and gives the partner nothing to fix.

## 5. Notices and escalation

- **Notice day:** send the targeted email to every contact on file and add the in-response warning (`Deprecation` and `Sunset` headers). Put the confirmation request in the same email. Don't hold the notice for verification.
- **Contacts:** hold three roles per integration. They are the technical owner, the commercial owner, and for fleet or plugin shapes, the installing customer's admin. Route unverified rows to the commercial owner, then to the customer admin.
- **Email cadence:** monthly per integration still on the old surface, not weekly. Stop on acknowledgment, and stop when calls reach zero across the lookback. Never mail integrations that don't use the surface.
- **Every notice** carries the surface, identity, call count, last seen, a sample request ID, replacement, guide and break date in UTC. Include how to acknowledge and how to dispute.
- **Door-closing:** new integrations and new webhook destinations start on payload v2 and the current SDK. Keys rotated and installs of existing apps keep their current surface until their break date.
- **Brownouts:** last resort, announced and short. Return the final-state status with the schedule in the error body, and send `Cache-Control: no-store`. Run them only once the replacement is stable. This applies to the payload v1 row. A cert event can't brown out in a comparable way, so use test deliveries and the overlap period instead.

## 6. Readiness gate before each cutoff

Review it line by line, not as a percentage.

1. Every top-tier integration is migrated under the rule above or has an exception.
2. Every long-tail integration is notified at a verified contact or routed to its customer admin.
3. Unattributed calls are zero on authenticated surfaces and below a floor you defend on public ones.
4. The replacement has met its service objective over the last several weeks, with no open incident and headroom for the residual load.
5. Every exception has an owner, a reason and an expiry.

Grant exceptions per integration, keyed to the credential. Don't slip the date for everyone. Don't shorten a published date because the call share looks small.

## 7. Open questions

These would change the plan. Where I had to guess, the assumption is stated.

1. **What breaks on Feb 14?** I assumed that partners who pin the cert or public key fail verification. If they fetch keys from a JWKS or similar endpoint, the cert row is mostly an overlap and test-delivery check. What does your partner contract say about pinning?
2. **What is the exact April date for iOS SDK 3.x?** Without it, row 2 is not yet a health signal.
3. **Is every request tagged with a credential identity at the gateway?** What share carries none? I assumed full coverage for the authenticated API.
4. **Who builds against Quillfeather?** Customers' own engineers, partner apps across many accounts, or plugins and agencies? This decides the contact chain and whether a customer-admin notice is needed.
5. **What is the longest business cycle a partner runs on?** I assumed up to a year. A shorter cycle shortens the lookback.
6. **How do you reach partners today, how recently was each contact confirmed, and do you track bounces?**
7. **Is payload v2 complete for every event type and use case?** If not, escalation past a reminder is unfair.
8. **How much outreach time can the partner team spend each week?** That sets the size of the top tier.
9. **Are the three dates fixed by contract, security or cost?** If so, a brownout can come earlier for the payload row.