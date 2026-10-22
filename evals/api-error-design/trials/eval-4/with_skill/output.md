# Meterhaus error-code migration sketch

## Verdict on the plan

I wouldn't ship the plan as written. Renaming in place and deleting about a dozen codes in one release is a breaking change. The `api-error-design` stability contract says codes evolve by addition only: never rename, repurpose, or delete a shipped code. A code only disappears on a version boundary, through the deprecation machinery.

Updating the docs the same day doesn't help. Docs reach people, and the break happens in deployed code that no one is reading docs for.

- **What breaks:** after five years, with about 2,300 consumers, some integrations branch on `billing_failed`, `ERR_17` or `INVALID-METER`. `billing_failed` → `BILLING_FAILED` is a different string to every `==`, switch, dashboard filter and alert rule. Those clients break silently: the error falls into their default branch, and they retry or drop it.
- **The deletions are worse.** "Nobody should be using" isn't the same as "nobody is using". Check that with traffic data.

The goal (one consistent SCREAMING_SNAKE catalog) is right. Only the delivery mechanism changes: a dual-emit migration with a version boundary.

## Assumptions

I haven't seen your responses, so these need confirming. Question 3 matters most, because it decides how much of the surface is contract.

1. REST-only. That makes the code/subcode catalog the default rung. For about 60 to 100 codes in one team's hands it's reasonable, and a flat catalog is acceptable if each category has a single reason.
2. This is a retrofit, and the current envelope is custom. I don't know which field holds the code (`code`? `error`?) or whether it's consistent across endpoints.
3. The consumers are mostly third-party integrators, plus some machine callers. Design for them.
4. Question 6 is open: I need the ship date and how much client-visible migration you can spend.

## Step 0: Measure before deciding (week 0 to 2)

1. **Pull 5 to 10 real error responses** from different endpoints, including validation, auth, billing, meter and 5xx cases. Fill in the audit table (endpoint, status, envelope shape, code present, field detail, retry signal, documented, findings).
2. **Build the code inventory.** Every code, field and message string that ever shipped goes in as a row, from code search, API logs and old docs. Columns: `legacy_code`, HTTP status, trigger, 90-day emission count, number of distinct API keys that received it, and `new_code`.
3. **Classify each code from the real data:**
   - **Live:** emitted in the last 90 days. It gets a canonical code and is never dropped.
   - **Dead:** zero emissions across the whole retention window, and the trigger condition is unreachable in code. This is the only kind you may retire.
   - **Merge:** several legacy codes that mean the same thing, such as `ERR_17` and `INVALID-METER` if they are both "meter ID unknown". They map many-to-one.
4. **Check the dozen "nobody uses" codes** against emission counts per API key. Any code with consumers gets the full deprecation path below, or becomes an alias of a surviving code. Don't delete it.
5. **Ask the support and solutions teams** which codes big customers have asked about. Logs miss customers whose error path fires rarely (annual billing runs, say).

## Step 1: Target catalog

- **Taxonomy:** code/subcode, with every code pinned to one HTTP status, e.g. `BILLING_ERROR` (402) with subcodes `PAYMENT_FAILED`, `CARD_EXPIRED`, `PLAN_LIMIT_REACHED`.
- **Naming:** SCREAMING_SNAKE, ASCII, no digits-only codes. `ERR_17` carries no meaning and needs a descriptive successor.
- **Mapping rules:** `billing_failed` → `BILLING_FAILED`, `INVALID-METER` → `INVALID_METER`. Mechanical renames are fine only where the meaning is unchanged. If a legacy code covers two conditions, split it in the new catalog. The old code keeps pointing at the nearest new one.
- **Envelope:** RFC 9457 (`application/problem+json`) with extension members `code`, `errors[]`, `retryable`, `documentation_url` and `request_id`. Add `Retry-After` on 429 and 503. Return `X-Request-ID` on every response and echo it in the body. Emit the retry object explicitly on 500.
- **Catalog page:** one public page, one stable anchor per code, written before the code ships. For each code, state the status, cause, retryability, whether the message is safe for end users, and the fix path.
- **Contract line in the catalog:** `code` is stable and safe to branch on. `message` and `detail` are not contractual.
- **Gatekeeper:** one owner or review step. No code reaches production without a catalog entry. Lint the codebase for ad hoc error strings.

## Step 2: Dual-emit, additive only (release N)

Release N changes no existing value. It only adds:

- A new field carrying the canonical code, alongside the untouched legacy field. If today's field is `error_code`, add `code` (RFC 9457 extension member) next to it. If today's field is already named `code`, use a temporary name such as `canonical_code` and rename it on the new version. If you ship it under `code`, the legacy value has to move out of that field, and that is the breaking change we're avoiding.
- A `Deprecation` header on responses that carry a legacy code, plus `Sunset` once the date is set. `Link: rel="deprecation"` points to the migration guide.
- A published mapping table (`legacy_code` → `new_code`) as JSON and as a docs page, so clients can write the translation in ten minutes.
- The new catalog, with every legacy code listed as deprecated and its replacement.

Rule: existing consumers who change nothing see nothing different. Legacy values stay byte-identical, including for the dozen "dead" codes that live ones may still receive.

## Step 3: Version boundary (release N+1, or the new API version)

Tie the cutover to your API versioning policy, not to a calendar date alone.

- **New version (e.g. `v2`, or a date-pinned header version):** `code` is canonical-only. Legacy codes aren't emitted.
- **Old version:** frozen. It keeps emitting legacy values plus the additive canonical field.
- **Opt-in first.** New API keys get the new surface by default. Existing keys migrate when they choose to, or on the forced date.
- **Dead codes:** removed from the new version's catalog. They stay documented as retired, with the version they ended in, so a customer searching for one finds an answer.
- **Live codes marked "retire":** they get a replacement and a mapping. They don't get deleted.

## Step 4: Communicate and nudge

- **Announce at release N, not at cutover.** Use email to all 2,300 keys' technical contacts, the changelog, the status page and in-app notices. State the dates, what changes, what doesn't, and the mapping file.
- **Targeted outreach:** from emission data, list the API keys that still receive legacy codes. Contact the top consumers directly, starting with the largest by volume and revenue.
- **Per-key dashboard:** show each customer whether they ever received a deprecated code in the last 30 days, so they don't have to check their own logs.
- **Timeline (sketch, adjust to the question 6 answer):**

| When | What |
|---|---|
| T-0 | Release N: dual-emit, headers, mapping table, announcement |
| T+30d | Reminder, plus direct outreach to keys still on legacy |
| T+90d | New version available; new keys default to it |
| T+6 to 12 months | `Sunset` date for the old surface. Use the longer end for enterprise contracts. |

- **Size the sunset from data:** don't sunset until legacy-emission share is near zero, or the remaining keys have been contacted individually. If the numbers say a long tail will remain, extend the date. Don't break people to hit it.

## Step 5: Gates (must pass before each release)

1. **Envelope consistency:** one shape on 100% of endpoints and statuses. A single deviating endpoint fails.
2. **Catalog coverage:** zero codes observable in responses that are missing from the published catalog or from the endpoint's OpenAPI examples.
3. **Mapping completeness:** every legacy code from the inventory has exactly one replacement or a documented retirement.
4. **Compatibility test:** a recorded set of real error responses from the old surface, replayed against release N, must be unchanged in the legacy fields.
5. **OpenAPI:** each endpoint lists every status it returns, with one named example per error code.

## Step 6: Watch and roll back

- **Metrics:** share of responses carrying legacy codes, by API key and by code. Count of keys on the new surface. Support tickets that mention error codes, and the share carrying a request ID. Set the baseline from the first month.
- **Alert** on a spike in 4xx or retry volume from top consumers after any release step. That's the signature of a client that fell into its default branch.
- **Rollback:** because release N only adds fields, rollback is a revert with no client impact. The version boundary is where rollback gets expensive, which is why it's opt-in first.

## Summary of changes to your plan

| Your plan | Recommended |
|---|---|
| Rename in place | Add canonical codes alongside legacy ones, then cut over on a new version |
| Drop ~12 codes | Drop only codes with zero emissions across 90+ days. Alias or deprecate the rest. |
| Update docs the same day | Publish the mapping and catalog at release N, announce it, and give a sunset window |
| One release | Three phases: dual-emit, opt-in version, sunset |

## What I need from you

1. Five to ten real error payloads, so I can confirm the current envelope and field names.
2. Do you have a versioning mechanism today (URL, date header), and what's the deprecation policy in your contracts?
3. How long are API logs retained, and can you query emissions per code per API key?
4. Is there a hard date for this release? If so, I'd ship Step 2 on that date and leave Step 3 for later.
5. Are there contractual SLAs or enterprise customers who need a longer notice period?