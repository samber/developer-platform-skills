# Recommendation: use RFC 9457 Problem Details, not a custom `{ok, errorCode, errorText}`

## Short version

1. Adopt **RFC 9457** (`application/problem+json`) as the envelope. It is a standard, and integrators' HTTP clients and tooling already understand it.
2. Drop the `ok` boolean. The HTTP status is the success signal.
3. Add a stable machine-readable `code` and a per-field `errors[]` list.
4. Return **422** for well-formed JSON that fails business validation. Keep **400** for requests that cannot be parsed.
5. Ship it under a new API version or opt-in. Do not change `/v1/*` in place.

## Why not `{ok, errorCode, errorText}`

- **`ok` duplicates the HTTP status.** The two can disagree, and that is exactly today's `/v1/labels` bug (`success:false` with HTTP 200). A boolean in the body keeps that bug possible.
- **Success responses would need the field too.** Otherwise `ok` only exists on failures and is useless.
- **There is no room for several errors.** Address validation routinely fails on more than one field, and a single `errorText` can't express that.
- **There are no field pointers.** Integrators would have to parse prose to find which field is wrong.
- **No `request_id`.** Support can't trace a failure without one.
- **It is a one-off format.** Each of 900 integrators writes a bespoke parser, and you maintain the docs forever.

## The envelope

Status and `Content-Type: application/problem+json` are on the HTTP response.

```json
{
  "type": "https://docs.parcelbyte.com/errors/address-validation-failed",
  "title": "Address validation failed",
  "status": 422,
  "detail": "The destination address could not be validated.",
  "instance": "/v2/labels",
  "code": "ADDRESS_VALIDATION_FAILED",
  "request_id": "req_01J9ZK3Q8M",
  "errors": [
    {
      "pointer": "/to_address/postal_code",
      "code": "POSTAL_CODE_MISMATCH",
      "detail": "Postal code 75001 does not match city 'Lyon'."
    },
    {
      "pointer": "/to_address/street1",
      "code": "FIELD_REQUIRED",
      "detail": "street1 is required."
    }
  ]
}
```

| Field | Rule |
|---|---|
| `type` | Stable URI that resolves to a docs page. It is the primary identity of the error class. |
| `title` | Short, human-readable, same for every occurrence of that `type`. |
| `status` | Mirrors the HTTP status. |
| `detail` | Human-readable, specific to this occurrence. **Documented as not machine-parseable.** |
| `code` | Stable UPPER_SNAKE string integrators can `switch` on. Enumerated in the OpenAPI spec. |
| `request_id` | Also sent as a response header. Support's first question is always this. |
| `errors[]` | Optional. Each entry has `pointer` (RFC 6901 JSON Pointer into the request body), `code`, and `detail`. Query and header problems use `parameter` or `header` instead of `pointer`. |
| `retry_after` | Only on 429 and 503. Also sent as a `Retry-After` header. |

### Rules to put in writing before building

- **Codes are append-only.** Never rename or reuse one. Tell integrators to handle unknown codes by falling back on `status`. That keeps new codes non-breaking.
- **`code` is one flat namespace.** Field-level codes (`FIELD_REQUIRED`) and request-level codes (`ADDRESS_VALIDATION_FAILED`) come from the same published list.
- **Never leak internals.** No stack traces, SQL, or carrier credentials in `detail`.
- **Same shape for every error.** Auth, validation, rate limit, and 5xx all use the envelope, including errors from the gateway or WAF. Check that your edge doesn't return HTML.
- **Success responses are unchanged.** They are plain resources, with no wrapper.

## Status code mapping

| Situation | Status |
|---|---|
| Unparseable JSON, wrong content type, wrong field types, missing required fields | 400 |
| Missing or invalid credentials | 401 |
| Valid credentials, not allowed | 403 |
| Unknown resource | 404 |
| State conflict (label already voided, duplicate idempotency key with a different body) | 409 |
| Well-formed JSON that fails business rules (undeliverable address, postal code and city mismatch, unsupported service for route) | **422** |
| Rate limit | 429 with `Retry-After` |
| Carrier or upstream failure | 502 or 503 |
| Our bug | 500 |

## The 400 vs 422 question

Use **422 Unprocessable Content** (RFC 9110) for your case: valid JSON, understood structure, and the content is rejected by business rules. 400 then means "I couldn't interpret this request", and 422 means "I understood it and it's not acceptable". Integrators get a useful split. A 400 means fix your client code, and a 422 means fix the data you sent.

Two caveats:

- **Draw the line deliberately.** Missing required field or wrong type: 400, because it violates the schema. Valid shape but a bad value (a postal code that doesn't exist for that country): 422. Pick that rule, write it down, and apply it everywhere. Some APIs use 422 for both, which is also defensible if applied consistently.
- **This is a breaking change for anyone who branches on 400 today.** Moving to 422 is safe only inside the new version. Treat that as part of the envelope migration, not a separate quiet change.

Neither status is retryable. Say so in the docs: 4xx except 429 means "don't retry unchanged".

## Migration with about 900 integrators

You can't fix this in place, and the three legacy endpoints need different treatment:

1. **`/v1/labels` (HTTP 200 with `success:false`).** Changing it to 4xx breaks every integrator who checks `success` and ignores the status. **Freeze it.** Fix it in v2 only. Before you deprecate, log which API keys actually hit the error path, so you can contact them directly.
2. **`/v1/rates` (`{message, status}` with 4xx).** Close to the target already. You can additively return `type`, `title`, `detail`, `code`, and `request_id` next to the existing `message` and `status`. Nobody breaks, and this is the cheapest win.
3. **Newer `{"errors":[...]}` endpoints.** Fewer integrators depend on them. Migrate them to the new envelope with an announced date.
4. **Versioning mechanism.** Use whatever versioning you already use (path `/v2/` or a version header). Do not make the envelope depend on a one-off flag.
5. **Ship in this order.**
   1. Publish the spec and the error-code catalog.
   2. Build a shared error library or middleware, so no handler hand-writes error JSON.
   3. Add a contract test that fails CI on any non-envelope error.
   4. Release v2.
   5. Announce the v1 sunset with a long window, because these are external integrators.
6. **Labels need extra care.** A label purchase moves money. On a 5xx or timeout, the response must let integrators find out whether a label was created. Pair the envelope with an `Idempotency-Key` on `POST /labels`, and document the recovery path. That matters more than the envelope shape.

## Questions to settle before building

- **Do you want localized `detail`?** If yes, key it off `Accept-Language`. `code` and `type` never change.
- **Which versioning mechanism does the rest of the API use?** The migration path depends on it.
- **Does the new backend lead have a reason to avoid RFC 9457?** If their reason is "we need `ok`", the answer is that clients can check `response.ok` or the status code. If it is "we want a smaller shape", the RFC's required fields are all optional, so you can send only `type`, `title`, `status`, and `code`.