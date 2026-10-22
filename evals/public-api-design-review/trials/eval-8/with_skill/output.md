**Next action:** pick one error envelope this week, before launch. Put it behind one shared error handler, and replace the `null`-with-200 responses with 404. The details are below.

# Public API design review: Ardenway Labs

## Scope

- **Surface:** public REST API, about 40 endpoints, `/v1`.
- **Material seen:** three behaviors you described (error bodies for `/v1/accounts` and `/v1/transfers`, and `null` with 200). No spec, no sampled responses, no endpoint list.
- **Audience and stage:** public, pre-launch. I treated this as a blocking review, so Must-change findings block launch.
- **Rule corpus:** you named none. Findings cite the checklist in the `public-api-design-review` skill by dimension and item.
- **Not done:** no linter run, because no spec exists. I could not ask the clarifying questions, so the assumptions are at the end.

## Dimension summary

| Dimension | Result |
|---|---|
| 1. Resource modeling and URIs | **Not assessed.** No endpoint list. |
| 2. HTTP method semantics | **Not assessed.** |
| 3. Status codes | **FAIL.** Finding 2. |
| 4. Field naming | **Not assessed.** Finding 1 shows one divergence (`error` vs `errors[].detail`). |
| 5. Pagination | **Not assessed.** |
| 6. Filter, sort, field selection | **Not assessed.** |
| 7. Error shape | **FAIL.** Finding 1. Leak check unverified (finding 3). |
| 8. Backward compatibility | **At risk.** Finding 4. |

"Not assessed" is not a pass. Consistency defects only show up across the whole surface, and I have seen three endpoints out of 40.

## Findings

| # | Finding | Dim | Bucket | Cited rule | Fix |
|---|---|---|---|---|---|
| 1 | Two error envelopes: `/v1/accounts` returns `{"error": "..."}` and `/v1/transfers` returns `{"errors":[{"code":4012,"detail":"..."}]}`. | 7 | **Must-change** | "One error envelope on every endpoint and every status… don't mix patterns" | Adopt one envelope everywhere (details below). |
| 2 | Some endpoints return `null` with 200 when the resource is missing. | 3, 7 | **Must-change** | "Same failure condition maps to the same status code on every endpoint"; 404 = not found; "don't mix patterns" (`null`, `{error}` and `{errors}` for the same failure class) | Return 404 with the standard envelope. |
| 3 | Internals leakage is unverified. | 7, 8 | **Unverified, blocks launch until checked** | "No 500 body leaks a stack trace, database error text, internal path, or config"; "Responses leak no implementation details" | Run the leak test below. Any hit becomes a Must-change. |
| 4 | No machine-readable spec. The Notion page is hand-maintained. | 8 | **Improvement** | Step 2 rule: a missing spec is logged as an Improvement. The "spec-first" item in dimension 8 also fails. | Write a minimal spec before launch. |

On the buckets: I cannot call finding 3 a Must-change without evidence. I also cannot call it a pass for an ISO 27001 shop. Finding 4 stays an Improvement by the skill's explicit rule, but I recommend treating it as pre-launch work (see below).

### Finding 1: one envelope

Recommended shape is RFC 9457 problem details, served as `application/problem+json`:

```json
{
  "type": "https://<your-docs-domain>/problems/<slug>",
  "title": "<fixed text per error type>",
  "status": 422,
  "detail": "<fixed or templated text, never raw exception text>",
  "code": 4012,
  "request_id": "<opaque id>"
}
```

- Keep the numeric `code` as an extension member, so `/v1/transfers` clients keep working.
- Add `request_id` so support can correlate a failure with internal logs without exposing anything.
- The `title` and `detail` text must come from a fixed table. Never interpolate exception messages, SQL, hostnames, or internal identifiers.
- Code taxonomy, message wording and retry signals belong to `api-error-design`. That is the next review if you want depth there.
- Enforce with one shared error handler as the only path out of the service. Add one contract test that sends a bad request to every endpoint and asserts the envelope. No spec is needed for this.

### Finding 2: `null` with 200

- A missing resource must return 404 with the envelope.
- A client cannot tell `null` from "empty", and a JSON body of `null` breaks typed clients.
- Name the endpoints that do this. I could not see which.

**Retrofit caution:** if any client already calls the API (design partners, a mobile app), changing the shape breaks it. Pre-launch, fix in place now. If clients exist, route it through `api-versioning-policy`, not a silent swap.

### Finding 3: leak test for ISO 27001

The `error` and `detail` strings are free text, and that is the usual leak route. Send these to every endpoint and read the bodies and headers:

1. Malformed JSON, wrong types, oversized body, wrong `Content-Type`.
2. Unknown route, wrong method (405), missing and invalid auth (401).
3. Inputs that force a 500, such as huge numbers, null bytes and unicode edge cases.
4. Gateway-generated errors (404, 413, 429, 502), which are often HTML pages or carry a framework default.
5. Response headers: `Server`, `X-Powered-By`, framework or version strings.

Also check one thing I suspect but cannot confirm. If another tenant's resource returns 403 or an object while a missing one returns `null`, a caller can tell whether an ID exists. Return the same 404 for "not yours" and "not found".

### Finding 4: no spec until after launch

"We'll write the spec after launch" is a rationalization the checklist rejects. The reason is Hyrum's Law. After launch, three error shapes and `null` responses become behavior clients depend on, and the spec would document them instead of fixing them. The cheapest moment to fix them is now.

A skeleton OpenAPI file is enough: paths, methods, and one shared error component referenced by every response. Then run Spectral on it. This also gives your auditors one source of truth instead of a Notion page that drifts.

## Five adjacent checks (existence only)

- **Versioning:** `/v1` prefix exists. No policy seen. See `api-versioning-policy`.
- **Idempotency:** unknown. `/v1/transfers` moves money, so check for idempotency keys. See `api-idempotency-retry`.
- **Auth:** unknown. See `api-auth-key-management`.
- **Rate limits:** unknown. Check for 429 with `Retry-After`. See `api-rate-limit-policy`.
- **Docs:** one hand-edited Notion page. Drift risk, with no way to verify coverage. See `api-reference-quality`.

## Ship gate

- **Blocks launch:** findings 1 and 2, plus the finding 3 leak test.
- **May ship open:** finding 4, though I advise against it.
- **Accepted deviations:** none recorded.

## Rough effort

These are my estimates for a typical backend, not measured:

- Shared error handler plus envelope: 1 to 2 days.
- `null` to 404 on the affected endpoints: under 1 day.
- Contract test over all endpoints: about half a day.
- Leak test: about half a day.
- Skeleton OpenAPI plus Spectral: 1 to 2 days.

## Assumptions

- The API is not yet public and has no clients you cannot contact.
- You follow no external guideline.
- 37 endpoints are unseen. The review is incomplete until I see them.

## Next steps

1. List the endpoints that return `null` with 200.
2. Paste 5 to 10 real responses across different endpoints, including one collection and one 500. That lets me assess dimensions 1, 2, 4, 5 and 6.
3. Answer one question: does any external client already call the API?