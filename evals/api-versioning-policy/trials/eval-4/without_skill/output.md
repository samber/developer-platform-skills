# Deprecation Policy, Section 6: Enforcement of the v1 Sunset

**Read this first.** I changed one thing from your plan, and you should decide whether you accept it.

The plan was to route every `/v1` call to the `/v2` handler unchanged, "same request, new logic, no error." That can't hold as written. If v2 differs from v1 in any way (field names, units, pagination, auth scopes, fitment logic, price rounding, error shapes), a raw reroute means one of two things:

- **v1 clients get a v2-shaped response and fail to parse it.** That's the error you wanted to avoid, only harder to see: it happens inside the customer's code, and your logs show a 200.
- **v1 clients parse it fine and act on different data.** In a parts catalog that means a wrong fitment answer, a different price, or a different availability, and a wrong part gets ordered. That is worse than an error.

So this section keeps the head of support's goal (no customer sees a sunset error) and enforces it with a **v1 compatibility adapter** instead of a raw reroute. The adapter takes v1 requests, runs v2 logic, and returns the exact v1 response contract. Where that can't be done safely, it fails loudly and specifically, never silently.

Today is 2026-10-03. If October enforcement hasn't started, the verification gates in 6.4 must pass before it does. If it has, treat 6.4 as an immediate audit.

---

## 6. Enforcement

### 6.1 Principles

1. **Silent wrong data is worse than an explicit error.** The adapter may fail a request. It may never return a response that is plausible but not equivalent to v1.
2. **The v1 contract is frozen.** After the sunset date, `/v1` means "the behavior documented on the freeze date," whatever v2 does.
3. **The adapter is temporary and has its own end date** (6.9).
4. **Every v1 call is attributable** to a customer and key, so support can act before a customer notices.

### 6.2 Scope

- Applies to every path under `/v1`, for all customers, key types, and environments.
- Does not apply to `/v2`, which keeps its own policy.
- New API keys issued after [KEY-FREEZE DATE] cannot call `/v1`. Requests return `403` with code `v1_not_available_for_new_keys`.

### 6.3 Mechanism: compatibility adapter

From the enforcement date, `/v1/*` is served by the adapter. For each request it does the following:

1. **Translates the request.** It maps v1 parameters, headers, and body to the v2 input model.
2. **Runs v2 logic.** There is no second implementation of catalog logic to maintain.
3. **Translates the response back.** It emits the v1 schema: field names, types, units, pagination envelope, ordering, null handling, decimal formats, and error body format.
4. **Preserves v1 semantics** for status codes, idempotency, rate-limit headers, auth, and caching headers.

Rules:

- **Per-endpoint translators.** There is no generic "pass through to v2" fallback. An endpoint without a verified translator returns the error in 6.5. It does not fall through to the v2 handler.
- **Translator coverage is a release gate.** Every `/v1` route has a translator, a golden-fixture suite, and a named owner.
- **The adapter adds no new fields** to v1 bodies. Signalling goes in headers only (6.6).

### 6.4 Verification gates (all required before enforcement is enabled)

| Gate | Pass condition | Owner |
|---|---|---|
| Route inventory | Every `/v1` route observed in the last 90 days of traffic is listed and mapped to a translator | API team |
| Golden fixtures | For each route, recorded v1 responses replayed through the adapter match byte-for-byte after normalising declared non-deterministic fields (timestamps, request IDs) | API team |
| Shadow diff | Live v1 traffic mirrored to the adapter for a minimum of 14 days. The mismatch rate on business fields (part number, fitment, price, stock, currency) is **0** after triage. Any residual diff has a written, approved explanation. | API team + Data |
| Fitment and pricing audit | A sample of top-volume part lookups per customer segment is compared, v1 legacy versus adapter | Catalog team |
| Rollback drill | Disabling the adapter and restoring the legacy v1 path takes under 15 minutes, and the drill has been run once | SRE |
| Support runbook | Section 6.8 is published to support and tested with one simulated incident | Support |

If any gate fails, the sunset date moves. The adapter does not ship partially verified.

### 6.5 What the adapter does when it cannot translate safely

Some v1 behavior may have no v2 equivalent (a removed filter, a field v2 no longer computes). For those cases:

- The request fails with a **specific, actionable error**, never a generic `500` or `404`:
  - Status `422` (or `410` if the whole endpoint is retired).
  - Body in the **v1 error format**, so existing client error handlers still parse it.
  - Stable `code`, such as `v1_feature_unsupported`.
  - `message` naming the unsupported parameter or behavior.
  - `migration_url` pointing to the matching migration guide section.
- **The list of non-translatable behaviors is produced before enforcement** (it's an output of the 6.4 gates) and published in the migration guide. Nothing is first discovered by a customer in production.
- A customer hitting one of these is a **support-priority event** (6.8), not a routine error.

This is the only case where a customer can see an error because of the sunset. The head of support should sign off on the list. If it's empty, the "no errors" goal is met in full.

### 6.6 Signalling on every v1 response

Every response from `/v1` carries:

- `Deprecation: true`, or the deprecation date in HTTP-date form, per RFC 9745.
- `Sunset: <HTTP-date>`: the date the adapter itself is removed (6.9), per RFC 8594.
- `Link: <migration-guide-url>; rel="deprecation"`.
- `Meridian-Served-By: v1-adapter`, so customers and support can tell adapter traffic from legacy traffic.

The v1 response body stays unchanged.

### 6.7 Customer communication

| When | What | Channel |
|---|---|---|
| [T-90d] | Sunset announcement, migration guide, enforcement date | Email to account contacts and technical contacts, changelog, docs banner |
| [T-60d] | Per-customer usage report: which v1 endpoints they call and how often | Email + dashboard |
| [T-30d] | Reminder, with the non-translatable list (6.5) | Email |
| [T-7d] | Final notice | Email, and direct contact for the top accounts by v1 volume |
| Enforcement date | Adapter on; notice that integrations keep working | Email, status page |
| Adapter removal | Final notice 30 days before | Email, headers (6.6) |

Customers still on v1 at T-30d get a named contact at Meridian. Contractual v1 commitments are reviewed by Legal before enforcement.

### 6.8 Monitoring, incident response, and rollback

**Monitored per customer and per endpoint:**
- v1 request volume, by key.
- Adapter error rate, and rate of `v1_feature_unsupported` responses.
- Adapter versus legacy diff rate, where shadowing is still on.
- Client-side symptoms: abnormal 4xx rates, retry storms, and sudden drops in a customer's volume (which can mean silent breakage on their side).

**Alerts:**
- Any `v1_feature_unsupported` response pages support the same day.
- A customer's v1 volume falling more than [50]% day over day triggers a proactive check-in.
- Business-field diff above 0 on any shadow sample is a Sev-2.

**Rollback:** a single feature flag restores the legacy v1 path per customer or globally. The on-call engineer may flip it without further approval when a data-correctness issue is suspected. A correctness incident is always grounds for rollback, even if no customer has complained.

**Support runbook:** support can look up any customer's v1 endpoint usage, check whether they're hitting adapter or legacy paths via `Meridian-Served-By`, and escalate with a pre-filled template.

### 6.9 Adapter lifecycle

- The adapter has a **hard removal date**: [ENFORCEMENT DATE + 6 months]. This is the `Sunset` header value.
- At removal, `/v1/*` returns `410 Gone` with the v1 error format and `migration_url`.
- Extending that date requires written approval from the head of engineering and the head of support, with a reason and a new date. Extensions are limited to [2].
- Holding customers past removal needs a documented, per-customer exception (6.10).

### 6.10 Exceptions

- A customer may be granted a time-boxed exception only for a documented blocker (contract, certification freeze).
- Each exception records the customer, reason, end date, and approver, and is reviewed monthly.
- Exceptions are served by the legacy v1 path if it still exists, or by the adapter if it doesn't. They never extend the global dates.

### 6.11 Responsibilities

| Role | Owns |
|---|---|
| API team | Translators, fixtures, shadow diff, adapter operation |
| Catalog team | Fitment and pricing equivalence audit |
| SRE | Rollback, monitoring, alerts |
| Support | Runbook, customer outreach, escalations |
| Legal | Contractual v1 commitments |
| Head of engineering | Final go/no-go on enforcement and any date extension |

---

## Open items you need to resolve

1. **How different are v1 and v2 really?** I assumed they differ, since you called v2 "new logic." If the response contracts are already identical, the adapter shrinks to a thin router, but the 6.4 gates still apply.
2. **Exact dates:** the enforcement date, the key-freeze date, and the T-minus schedule. October is already underway.
3. **Does the head of support accept 6.5?** "Zero sunset errors" is only possible if the non-translatable list is empty. If it isn't, support needs to know which customers it affects before the date.
4. **Is a 6-month adapter window right?** Pick it with your top-volume customers' migration timelines in mind.
5. **Any customers with v1 written into a contract or SLA?** Legal must review them before enforcement.