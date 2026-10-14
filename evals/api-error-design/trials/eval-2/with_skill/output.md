# Parcelbyte error envelope: recommendation

I followed `api-error-design`. Its clarifying questions come first, but you asked for the full answer now, so I've stated my assumptions and listed what would change them at the end.

## Verdict

**Don't build `{ok, errorCode, errorText}`.** It would be a fourth error shape, and it would be a non-standard one.

Use **RFC 9457 problem details** (`application/problem+json`) with extension members. The same body shape goes on every endpoint and status. The skill is explicit about this: never invent a parallel non-standard envelope when the standard one accepts extensions.

Problems with `{ok, errorCode, errorText}`:
- **`ok` is redundant.** The HTTP status already says it, and `ok: false` invites the `/v1/labels` bug of returning 200 with a failure body.
- **There is no field-level detail.** An address failure needs to say which field, which value and which rule. `errorText` as prose can't do that.
- **There is no retry signal and no request ID.** Machine callers can't tell what to do next, and support tickets can't be traced.
- **The mixed-case names are your own invention.** Integrators' generic HTTP and problem-details tooling won't recognize them.

## The envelope

Assumptions: REST-only, third-party integrators, and an aim to ship in days to weeks rather than a quarter. That puts you on the **code/subcode catalog**, the skill's default rung. Each top-level `code` is pinned to exactly one HTTP status, and `errors[].code` carries the specific reason.

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json
X-Request-ID: req_9f8e7d6c

{
  "type": "https://docs.parcelbyte.example/errors#VALIDATION_ERROR",
  "title": "Validation Error",
  "status": 422,
  "detail": "The shipping address failed validation.",
  "instance": "/v1/labels",
  "code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "to_address.postal_code",
      "code": "INVALID_POSTAL_CODE",
      "message": "to_address.postal_code must match the postal format for country 'DE' (5 digits); received '1234'.",
      "value_provided": "1234",
      "constraints": { "country": "DE", "pattern": "^[0-9]{5}$" }
    }
  ],
  "retryable": false,
  "documentation_url": "https://docs.parcelbyte.example/errors#INVALID_POSTAL_CODE",
  "request_id": "req_9f8e7d6c"
}
```

(The domain and the code names are illustrative.)

| Member | Role |
|---|---|
| `type`, `title`, `status`, `detail`, `instance` | Standard 9457 members. Keep them generic and human-readable. |
| `code` | Stable top-level category, pinned to one status. Integrators branch on this. |
| `errors[]` | Field-level detail with field, subcode, message, value received and constraint. Cross-field rules use a `fields` array and a `values_provided` map. Don't force a cross-field rule into the single-field shape. |
| `retryable` | A boolean on every error. It's the one field a generic handler can branch on without a status lookup table. |
| `documentation_url` | Stable anchor into the published catalog, one per code. |
| `request_id` | Echoes the `X-Request-ID` header, which goes on every response. |

Rules that go with it:
- **`Retry-After`:** send it on 429 and 503. On a bare 500, emit an explicit `retry` object (`retryable`, `retry_after`) instead of leaving callers to guess.
- **Catalog:** publish it as one page with an anchor per code. Every code a client can see must be in it before it ships. It also needs a named owner or review step, so no code reaches production without an entry.
- **Starter catalog:** `VALIDATION_ERROR` (422, plus 400 for malformed requests, see below), `AUTHENTICATION_ERROR` (401), `AUTHORIZATION_ERROR` (403), `NOT_FOUND` (404), `CONFLICT_ERROR` (409), `RATE_LIMITED` (429), `INTERNAL_ERROR` (500), `SERVICE_UNAVAILABLE` (503), each with subcodes where needed.
- **Stability contract:** state in the catalog that `code` and subcodes are stable and safe to branch on, and that `message` and `detail` text is not contractual. Change codes by addition only. Never rename or repurpose a shipped code, and never translate it. Honor `Accept-Language` for prose only.
- **Per-endpoint docs:** put a named example per error code in each endpoint's OpenAPI `responses` block, and generate the catalog page from the spec where you can.

## Your 400-on-business-validation question

Under the skill's own distinction, **valid JSON that fails business rules is 422, not 400**:
- **400** means the request is malformed: bad JSON, wrong types, a missing required field.
- **422** means the request is syntactically valid but semantically invalid. Your address payload, which is well-formed but fails your business rules, is exactly that case.

Your current 400 is therefore the wrong status by this rule. But **changing it is a breaking change**. Some of your ~900 integrators almost certainly branch on 400 for address failures (Hyrum's Law), and the skill says an error code or status disappears on a version boundary, never silently. Settle it explicitly in the catalog:
- `VALIDATION_ERROR` on malformed input gets 400.
- `VALIDATION_ERROR` on well-formed but rule-violating input gets 422.
- Whichever you choose, pin it once. Don't let one code ride on two statuses without writing that down.

Ship 422 only with the new envelope, never as a silent tweak to the old one.

## Migration: it's a retrofit, so it's breaking in three places

Your three current shapes each map differently, and the skill requires mapping every old identity to a new one rather than dropping it:

| Today | Problem | Target |
|---|---|---|
| `/v1/labels`: `{"success": false, "error": "..."}` with **HTTP 200** | Wrong status. This is the skill's named anti-pattern, and proxies, monitors and generic clients all see success. | Proper 4xx/5xx with the 9457 body. **This is the most breaking change.** Clients that check `success` on a 200 will stop seeing errors in the place they look. |
| `/v1/rates`: `{"message", "status"}` with 4xx | Status is right, shape is non-standard. | Same statuses. `message` becomes `detail`. |
| Newer endpoints: `{"errors": [...]}` | Closest to the target shape. | Add the standard members and `code`, and keep `errors[]`. |

Recommended path:
1. **Audit first.** Pull 5–10 real error responses per endpoint into the skill's audit table (endpoint, status, envelope shape, code present, field detail, retry signal, documented, findings). Mine your logs for what clients observe, especially on `/v1/labels`.
2. **Ship the new envelope as opt-in or on a new version.** Use `Accept: application/problem+json` or `/v2`, and freeze the old shapes on v1 with a published sunset date, run through your deprecation policy. The 200-to-4xx change on labels should land only at that boundary.
3. **Where it's additive, do it now.** Add the new members (`code`, `request_id`, `retryable`) alongside the legacy keys without removing anything. Put `X-Request-ID` on every response from day one.
4. **Gate on two things:**
   - Envelope consistency: one shape on 100% of endpoints and statuses. A single deviating endpoint fails the audit.
   - Catalog coverage: zero codes appear in responses that aren't in the catalog and in that endpoint's documented examples.
5. **Track support tickets as a trend, not a gate.** Measure the share that arrive with a request ID and the volume asking what an error means. Baseline both in the first month.

## What would change this

If any of these differs, the recommendation moves:
1. **Paradigm.** If you also run or plan gRPC, or several services must share one taxonomy for years, promote to Google-style `domain`/`reason`. If you need something live in days, a flat catalog is enough.
2. **Which codes, fields or strings clients already branch on.** This decides how much of the legacy shape you must keep during the migration.
3. **Layered failure causes.** If you have carrier rejections or customs and compliance failures where one code under-informs, consider a Stripe-style `type` + `code` + a detail code layer.
4. **Your migration ceiling.** How soon it must ship, and how much client-visible change you can spend.
5. **GraphQL.** If any endpoint is GraphQL, this envelope doesn't apply there. It has its own error shape.