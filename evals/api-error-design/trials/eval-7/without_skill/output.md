# Bindery validation errors: design

## Verdicts

1. **Case 1:** Collect every violation and return them all in one response. One error at a time is the bug.
2. **Case 2:** Attaching the error to `renewal_date` is fine as the primary location. It is incomplete on its own, so add a link to `signature_date` and a computed fix.
3. **Case 3:** A 200 with a results array is right. The `reason` string is wrong. Reuse the exact error object from case 1 for each failed item.

## One error shape everywhere

Use RFC 9457 `application/problem+json` with an `errors` extension. Single create and bulk items share the same error object.

```json
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{
  "type": "https://api.bindery.example/problems/validation-failed",
  "title": "Validation failed",
  "status": 422,
  "detail": "3 fields are invalid.",
  "errors": [
    {
      "code": "required",
      "pointer": "/counterparty/legal_name",
      "message": "counterparty.legal_name is required."
    },
    {
      "code": "invalid_format",
      "pointer": "/parties/2/email",
      "message": "Must be a valid email address.",
      "params": { "format": "email" }
    },
    {
      "code": "renewal_too_soon",
      "pointer": "/renewal_date",
      "related_pointers": ["/signature_date"],
      "message": "renewal_date must be at least 30 days after signature_date.",
      "params": {
        "min_gap_days": 30,
        "earliest_allowed": "2027-01-14"
      }
    }
  ]
}
```

Field rules:

- **`code`:** Stable, machine-readable, documented. Clients branch and localise on it, never on `message`.
- **`pointer`:** A JSON Pointer (RFC 6901) into the request body. Array indexes make nested fields addressable (`/parties/2/email`), which matters with 30+ fields.
- **`params`:** The numbers behind the rule. Put `30` here so a rule change doesn't break client copy.
- **`message`:** English fallback for humans and logs only.

## Case 1: report all errors in one pass

1. **Run all independent checks.** Do not return on the first failure. Validate every field and accumulate.
2. **Order the passes.**
   - Pass A: JSON parse and per-field type, format, and required checks.
   - Pass B: cross-field rules, run only when all their inputs passed pass A.
   - Skip a dependent rule when an input is already invalid. If `signature_date` is unparseable, don't also emit `renewal_too_soon`. That would be noise and a false error.
3. **Put state-dependent checks in pass C.** Examples are uniqueness, referenced IDs existing, and permissions. These cost DB calls, so run them only if A and B are clean. Document that a clean 422 can still be followed by a 409 or 403. Otherwise mobile will think "all errors" was a lie.
4. **Bound the response.** Cap `errors` at about 100 and set `"truncated": true` if hit. Dedupe repeated array-item errors if needed.
5. **Add a dry-run mode** for the mobile team, so they can validate as the user fills the form instead of only on submit. Use `POST /v1/agreements?validate_only=true`. It runs passes A and B, writes nothing, and returns 200 `{"valid": true}` or the same 422 body. This follows the Google AIP-163 convention.

## Case 2: the `renewal_date` rule

Attaching to `renewal_date` is a reasonable default, since that is the field users usually adjust. Three gaps need closing:

- **Blame is ambiguous.** The user may have mistyped `signature_date`. A form that highlights only `renewal_date` hides half the problem. Return `related_pointers: ["/signature_date"]` so the client can mark or link both.
- **PATCH breaks the simple model.** If a PATCH changes only `signature_date` and violates the rule against the stored `renewal_date`, the error would point at a field the client didn't send. Keep the primary pointer on `renewal_date`, but always include `related_pointers` so the client can see which sent field caused it. Alternatively, point the primary at the field in the request. Pick one rule and document it.
- **The error should be actionable.** `params.earliest_allowed` gives the client the fix directly, so it can show "earliest: 14 Jan 2027" or pre-fill the date picker.

Pin down the semantics in the docs:

- Both fields are dates (`YYYY-MM-DD`), not datetimes, so there is no timezone ambiguity.
- "At least 30 days" is calendar days, and equal to signature + 30 is valid (inclusive).
- Missing or invalid inputs suppress this rule, per pass B above.

## Case 3: `POST /v1/agreements:bulkImport`

Keep the 200 with per-item results. The batch envelope was processed, and partial success is the point of the endpoint. Change the item shape:

```json
HTTP/1.1 200 OK

{
  "summary": { "total": 500, "succeeded": 480, "failed": 20 },
  "results": [
    {
      "index": 0,
      "client_reference": "crm-8841",
      "status": "created",
      "agreement": { "id": "agr_01J9X...", "...": "..." }
    },
    {
      "index": 1,
      "client_reference": "crm-8842",
      "status": "failed",
      "errors": [
        {
          "code": "renewal_too_soon",
          "pointer": "/renewal_date",
          "related_pointers": ["/signature_date"],
          "message": "renewal_date must be at least 30 days after signature_date.",
          "params": { "min_gap_days": 30, "earliest_allowed": "2027-01-14" }
        }
      ]
    }
  ]
}
```

What changed and why:

- **No `reason` string.** A free-text reason forces callers to regex-parse errors. It also gives the bulk path a different error contract from single create. Items carry the same `errors[]` array, with pointers relative to the item.
- **`status` enum instead of `ok: bool`.** Use `created | failed` now. It leaves room for `skipped` or `duplicate` later without a breaking change.
- **`index` plus `client_reference`.** Index is positional. The caller-supplied reference lets them reconcile after reordering or retries. Return the new `id` on success so they can map CRM records to agreements.
- **`summary` counts.** A caller can see "20 failed" without scanning 500 items.
- **All errors per item.** Apply case 1 inside each item, so one failed row is fixable in one resubmit.

Envelope-level problems are ordinary 4xx responses, with no results array:

- Malformed JSON
- More than 500 items
- Auth failure
- A missing required top-level field

If every item fails, still return 200. The batch ran, and the results say what happened. Document this explicitly, because many clients only check the status code.

Two more decisions to make for bulk:

1. **Retries:** Require `Idempotency-Key` on the request. The caller should retry only the failed items, but a blind whole-batch retry must not duplicate the 480 successes. Per-item `client_reference` uniqueness is a second guard.
2. **Atomic mode:** Offer `?atomic=true` for all-or-nothing imports. On any failure it returns 422 with errors pointed at `/agreements/17/renewal_date`. Many importers want this, and it costs little once the shared error shape exists.

If 500 items validate too slowly for a synchronous call, make it a long-running operation (202 plus a poll URL). Keep the same results shape in the finished job.

## Rollout order

1. Define the error object and the `code` catalog (30+ field codes plus the cross-field ones).
2. Refactor validation into accumulate-then-report, with passes A, B and C.
3. Ship `validate_only` for mobile, then publish the 422 example to the mobile team.
4. Move bulk onto the shared error object. Keep `reason` for one deprecation cycle if existing clients depend on it, and mark it deprecated.

## Open questions for you

1. Are there existing bulk clients that rely on `reason` or `ok`? That decides whether step 4 needs a version bump.
2. Is `PATCH /v1/agreements/{id}` in scope? That determines which pointer rule you pick for cross-field errors.
3. Do you need localised messages? If so, `code` plus `params` is the contract, and `message` stays English.