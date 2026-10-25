# Signal Catalog

Forward-risk signals, how to compute each, and the census row they feed.

## Contents

- Forward-risk signals
- Resolving the served version
- Attribution fields
- First census query
- Census row fields
- Good and bad census rows
- Partner-visible versus internal

## Forward-risk signals

| Signal | Computed from | Breaks when | Window |
|---|---|---|---|
| Deprecated-surface calls | Gateway route, field and auth-method tags, grouped by credential; GraphQL field usage per operation | The surface is removed | Longest business cycle |
| Served API version | Version resolved per request after default, client config and header | The version is retired | Longest business cycle |
| Push-destination version | Version configured on each webhook endpoint or event destination | The payload version stops rendering | Current config, no window |
| SDK version | Client header sent by your own SDKs | The SDK reaches end of life or pins a retired API version | Longest business cycle |
| Install release | Per-install app, plugin or connector version for fleet and self-hosted shapes | The fix ships but sites never upgrade | Current installs |
| Credential expiry | Expiry dates on keys, client secrets, certificates | The date passes | Current config, no window |
| Dormant credential | Last-used timestamp per credential | It resumes after a cutoff, or is abused while forgotten | Compare against the longest business cycle |

Real providers expose these per integration: Shopify's API Health report lists deprecated endpoints with last-detected timestamps over 7- and 30-day tabs; Meta's API Upgrade Tool shows affected methods and the share of calls affected over 7 days; Stripe's Workbench breaks down the versions recent requests specified; Salesforce's API usage event log carries API version, connected app and client name per call.

Two cautions from those tools:

- Short windows hide the low-volume integrations. Meta's tool returns nothing when an app made "too few" calls from the old version, which is exactly the integration most likely to be forgotten.
- Observed traffic lags code. HubSpot flags runtime calls to legacy endpoints "even if your codebase has been updated", so a partner who shipped a fix still shows until the old deploy stops running. Say so in the report, or the partner disputes it.

## Resolving the served version

Record the version the platform actually applied to each request, resolved in the same order your platform applies it. A typical order, close to Stripe's:

1. Explicit per-request version header.
2. A version bound to the client - an SDK release pin or, where the platform has one, an OAuth application's version.
3. The account's pinned version, set on its first request.

Then record separately, per integration:

- Each webhook endpoint or event destination's own version. Some cannot be changed after creation: moving one means a second destination on the new version, and during the overlap every event arrives twice, so the consumer's handler must be idempotent and tell the two endpoints apart.
- The SDK release for typed languages, which pins the version of its release date.
- Any client-side library with a fixed pairing to an API version.

## Attribution fields

Log on every request to a catalogued surface:

- Credential identity: key ID, OAuth client ID, app ID. Never the secret itself.
- Account or tenant the call acts on.
- Served version, resolved as above.
- Deprecated route or field tag, when the call touches one.
- SDK name and version header, when present.
- User-Agent, as a hint only.

The unattributed share is calls to a catalogued surface with no credential identity. Report it on every census.

## First census query

Answer "who is behind the residue" before anything else. Group calls to the old surface by credential over the longest business cycle, then join:

- first and last call on the old surface, and first call on the replacement, per credential
- owner account, integration shape, installs or accounts behind it
- contacts and their verification date

Output one row per credential, sorted by end customers affected. Credentials with zero recent calls but live keys go in the same table, flagged dormant. Calls with no credential go in one summary row: count per week and the top client fingerprints.

## Census row fields

| Field | Why it is there |
|---|---|
| Integration identity | The unit the ladder escalates |
| Integration shape | Single-account, fleet app, or plugin/agency: decides the contact chain |
| Risk row from the catalog | Ties the row to a break date |
| Calls in lookback | Shows activity, never readiness on its own |
| First replacement call | Starts the lookback clock for the first migrated rule |
| Owner confirmation, date | The second migrated rule: every job moved, in writing |
| Last seen | Separates dormant from active |
| End customers affected | Installs or accounts behind this integration: the ranking key |
| Days to break | The second ranking key |
| Contacts and verification state | An unverified contact counts as none |
| Ladder rung reached, date | Drives the next escalation |
| Acknowledged, date | Stops escalation, starts migration tracking |
| Exception, expiry | Only from the exception register |
| Attribution disputed | Shared-token and reseller cases |

## Good and bad census rows

```
// ✓ Good - owner, blast radius, break date, verified contact, evidence the partner can check
app_7f3a "Ledgerline Sync" | fleet app | v1 /invoices sunset 2027-03-31 | 312 calls / 365 d | last seen 2026-12-29
| 2,140 installs | 96 days | tech: verified 2026-10-02; customer admins: 2,140 | rung: targeted email 2026-10-05
| ack: none | sample req_8c1e... | exception: none

// ✗ Bad - call share, no owner, 30-day window, nothing a partner can act on
v1 /invoices: 0.02% of traffic last 30 days, low priority
```

The bad row reads as nearly done. The good row shows one partner, thousands of installs, a year-end job that the 30-day window would have missed, and no acknowledgment yet.

## Partner-visible versus internal

Show the partner every field it can act on: the surface, its own call counts, last seen, sample request IDs, the break date, the replacement and guide. Keep internal: other partners' rows, the fleet burn-down, the blast-radius rank, and any internal priority. A partner shown its rank against named competitors turns an operational notice into a commercial dispute.

Never publish a blended health score in place of the specifics. A score tells the partner something is wrong and gives them nothing to fix.
