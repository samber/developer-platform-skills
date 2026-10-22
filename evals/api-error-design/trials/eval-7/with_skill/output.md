# Validation error design for Bindery (`POST /v1/agreements` and `:bulkImport`)

I followed `api-error-design`. The skill says to ask its six clarifying questions first, but you asked for the full answer, so I stated my assumptions instead. Correct me if any are wrong, because several choices depend on them.

**Assumptions**
- The API is REST-only, so I used the default code/subcode catalog.
- Consumers are your mobile team plus possibly third-party integrators, so the design targets the more demanding audience.
- Clients may already branch on today's codes or messages. I add fields and codes only and never rename or drop anything shipped (see the stability contract).

## Verdict

| Your plan | Verdict | Fix |
|---|---|---|
| One error at a time on a 30-field POST | ❌ | Collect all failures and return them in one `errors[]` array. |
| Attach the 30-day rule to `renewal_date` as a field error | ❌ | It is a cross-field rule. Use `fields: [...]` and `values_provided`. A single-field shape for it is a named failure mode in the skill. |
| Bulk returns 200 with `{ok: false, reason: "..."}` | ⚠️ | A 200 is acceptable for bulk, but `reason` strings are not. Each failed item must carry the same error shape as a top-level error. |

## Settled up front

- **Status codes.** I pinned each code to one status:
  - `MALFORMED_REQUEST` returns 400 for unparseable JSON or a wrong top-level type.
  - `VALIDATION_ERROR` returns 422 for well-formed JSON that fails rules.
- **Envelope.** RFC 9457 `application/problem+json` on every endpoint and status.
- **Stable fields.** `code` and `errors[].code` are contract. `detail` and `message` text is not, and the catalog says so.

## Case 1: report every failure in one response

Validate the whole body and return all failures together, as `errors[]` inside one 422.

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json
X-Request-ID: req_41d2a9c7

{
  "type": "https://api.bindery.example/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "3 fields failed validation. Fix all of them and resubmit.",
  "instance": "/v1/agreements",
  "code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "counterparty.email",
      "code": "INVALID_FORMAT",
      "message": "counterparty.email must be a valid email address; received 'ops@@acme'.",
      "value_provided": "ops@@acme"
    },
    {
      "field": "currency",
      "code": "INVALID_ENUM",
      "message": "currency must be a 3-letter ISO 4217 code; received 'euro'. Did you mean 'EUR'?",
      "value_provided": "euro",
      "constraints": { "pattern": "^[A-Z]{3}$" }
    },
    {
      "fields": ["signature_date", "renewal_date"],
      "code": "RENEWAL_TOO_SOON",
      "message": "renewal_date must be at least 30 days after signature_date. Received a gap of 19 days; the earliest valid renewal_date is 2026-10-31.",
      "values_provided": { "signature_date": "2026-10-01", "renewal_date": "2026-10-20" },
      "constraints": { "min_gap_days": 30, "actual_gap_days": 19, "earliest_renewal_date": "2026-10-31" }
    }
  ],
  "retryable": false,
  "documentation_url": "https://docs.bindery.example/errors#VALIDATION_ERROR",
  "request_id": "req_41d2a9c7"
}
```

**Rules that make this work with 30+ fields**
1. **Two phases.**
   - Phase 1 is structural: JSON syntax and top-level type. A failure returns `MALFORMED_REQUEST` (400) immediately.
   - Phase 2 is field and cross-field rules. It never short-circuits on the first failure.
2. **Run cross-field rules only when their inputs are individually valid.** If `signature_date` is unparseable, report that and skip the 30-day check. Otherwise you emit a misleading second error.
3. **Use unambiguous field paths for nested and array fields.** For example, `counterparty.email` or `parties[2].email`. I added this convention. The skill's examples use flat names, so document it in the catalog.
4. **Set an error cap, for example 100, and signal truncation.** Add `"truncated": true` and the total count to the response. This is my addition, not from the skill. A mobile client should know that more errors may exist.
5. **Order deterministically**, by request-schema field order. Tests and UIs then stay stable.
6. **Put the missing-field class under `VALIDATION_ERROR`** with subcodes `REQUIRED`, `INVALID_FORMAT`, `OUT_OF_RANGE`, `INVALID_ENUM`, `TOO_FEW_ITEMS` and so on. Every item names the field, the value received and the constraint violated.

**For the mobile team**
- Publish the static constraints (`min`, `max`, `pattern`, required) in the OpenAPI spec so the app can pre-validate. The server stays the authority.
- Keep the 400 versus 422 split documented so clients can tell "bug in my serializer" from "user must fix a form".

## Case 2: the 30-day rule is cross-field

Do not attach it to `renewal_date` alone.

- **Why.** The failure belongs to the relationship between two fields. A fix may be either date, and the mobile UI should be able to highlight both. A single-field shape also has nowhere to put `signature_date`.
- **Shape.**
  - `fields` is an array: `["signature_date", "renewal_date"]`.
  - `values_provided` is a map with both values.
  - `constraints` carries `min_gap_days`, `actual_gap_days` and `earliest_renewal_date`, so the client can suggest a fix without parsing prose.
- **Code.** Use a dedicated subcode (`RENEWAL_TOO_SOON` above) instead of the generic `INVALID_RANGE` from the skill's example. Callers can then branch on the business rule, and it gets its own catalog entry and `documentation_url` anchor.
- **Rendering convention.** Document in the catalog which entry in `fields` the UI should attach the message to if it can show only one. I would pick `renewal_date`, as the last-edited field in the form flow. That is my suggestion and should be stated explicitly, because clients otherwise guess.
- **Message.** Corrective, not blaming: it states the rule, the received gap and the earliest valid date, as in the payload above.

## Case 3: `POST /v1/agreements:bulkImport`

**Partial-success 200 is allowed here.** The skill rejects mixed-outcome 200s in general and permits them for bulk operations. The condition is that per-item failures reuse the standard error shape. `{ok: false, reason: "..."}` breaks that condition. It is a second, ad hoc envelope with no `code`, no field detail, no retry signal and no doc link, so clients need bespoke parsing and cannot reuse their validation-error UI.

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: req_88b0c3de

{
  "summary": { "received": 500, "succeeded": 480, "failed": 20 },
  "results": [
    { "index": 0, "client_reference": "row-0001", "ok": true, "agreement_id": "agr_7Hq2" },
    {
      "index": 37,
      "client_reference": "row-0038",
      "ok": false,
      "error": {
        "status": 422,
        "code": "VALIDATION_ERROR",
        "title": "Validation Error",
        "detail": "2 fields failed validation.",
        "errors": [
          {
            "fields": ["signature_date", "renewal_date"],
            "code": "RENEWAL_TOO_SOON",
            "message": "renewal_date must be at least 30 days after signature_date. Received a gap of 19 days; the earliest valid renewal_date is 2026-10-31.",
            "values_provided": { "signature_date": "2026-10-01", "renewal_date": "2026-10-20" },
            "constraints": { "min_gap_days": 30, "actual_gap_days": 19, "earliest_renewal_date": "2026-10-31" }
          }
        ],
        "retryable": false,
        "documentation_url": "https://docs.bindery.example/errors#VALIDATION_ERROR"
      }
    },
    {
      "index": 212,
      "client_reference": "row-0213",
      "ok": false,
      "error": {
        "status": 503,
        "code": "SERVICE_UNAVAILABLE",
        "title": "Service Unavailable",
        "detail": "This item could not be stored. Resubmit it in a later request.",
        "retryable": true,
        "retry_after": 30,
        "documentation_url": "https://docs.bindery.example/errors#SERVICE_UNAVAILABLE"
      }
    }
  ],
  "request_id": "req_88b0c3de"
}
```

**Rules**
1. **Per-item `error` is the same object as a top-level problem body.** It has the same `code`, `errors[]` (including cross-field entries), `retryable` and `documentation_url`. One client parser and one catalog cover both. The `type`, `instance` and `request_id` members are omitted per item because the envelope carries them. Write that down.
2. **Identify items by `index` plus a caller-supplied `client_reference`.** A client can then retry just the failed rows. For safe resubmission, see `api-idempotency-retry`.
3. **Return the whole `results` array**, not only failures. Document that it is positionally complete.
4. **Whole-request failures keep real HTTP statuses and never ride in a 200.** These cover:
   - bad auth: 401 or 403
   - malformed JSON: 400
   - more than 500 items: 422 `VALIDATION_ERROR` with a `BATCH_TOO_LARGE` entry, stating the limit
   - rate limiting: 429 with `Retry-After`
5. **Document atomicity.** State plainly that each item is independent and the batch is not all-or-nothing, so the 480 successes are committed.
6. **All-items-failed case.** The skill allows 200 for bulk without covering this edge. I would keep 200 with `summary.succeeded: 0` so clients have one code path. If your monitoring needs a status signal, that is a decision for you.
7. **Collect all errors per item too.** Apply Case 1 here, so a failing row never needs a second import.

## Catalog additions

| Code | Status | Subcodes or entries | Retryable | Message safe for end users? |
|---|---|---|---|---|
| `MALFORMED_REQUEST` | 400 | `INVALID_JSON`, `WRONG_TYPE` | no | no |
| `VALIDATION_ERROR` | 422 | `REQUIRED`, `INVALID_FORMAT`, `OUT_OF_RANGE`, `INVALID_ENUM`, `TOO_FEW_ITEMS`, `RENEWAL_TOO_SOON`, `BATCH_TOO_LARGE` | no | decide per subcode and mark it |

- **Catalog contents.** Each entry needs its status, cause, retryability, end-user safety and fix path. Give each code a stable anchor for `documentation_url`.
- **Stability.** `code` and subcodes are contract: add only, never rename or repurpose. `message` and `detail` may change without notice, and the catalog states this.
- **Existing clients.** If today's responses have codes or strings, map each old identity to a new one and keep it. I have not seen your current responses, so I have not audited them. Send 5–10 real error payloads across endpoints if you want the audit table.
- **Gatekeeper.** No code ships without a catalog entry.

## OpenAPI and request IDs

- **Documented examples.** Document these on `POST /v1/agreements`:
  - 400 `MALFORMED_REQUEST`
  - 422 `VALIDATION_ERROR`, with named examples for a field error and for `RENEWAL_TOO_SOON`
  - 401, 403, 409, 429 and 5xx
- **Bulk example.** `:bulkImport` additionally gets a 200 example with mixed `results`.
- **Request IDs.** Return `X-Request-ID` on every response and echo it as `request_id` in the body. Bulk responses carry one at the top level.
- **Retry signal.** Every 5xx includes `retryable`, so no bare 500 reaches clients.

## Acceptance gates

- **Envelope consistency.** Every endpoint and status uses one envelope, and per-item bulk errors parse with the same code.
- **Catalog coverage.** No code observable in responses is missing from the catalog or from the endpoint's documented examples.
- **Tests worth adding.**
  - A body with 30 invalid fields returns 30 entries in one response.
  - A cross-field rule is suppressed when one of its inputs is invalid.
  - A 20-of-500 bulk run returns 20 item errors that match the top-level shape.
  - The 501-item request returns 422 and not 200.
- **Support signal.** Track the share of error tickets that carry a `request_id`, as a trend.

## Open questions that could change this

1. Do you have third-party integrators or only your mobile team? Third parties raise the bar on `documentation_url` and catalog completeness.
2. Is there existing error output that clients already depend on? That decides the old-to-new mapping.
3. Should the bulk all-failed case stay 200 (point 6 above)?