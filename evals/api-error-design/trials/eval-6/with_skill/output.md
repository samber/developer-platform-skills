# Fieldnest: fixing error documentation and measuring success

I followed `api-error-design`. Its clarifying questions are written below as assumptions, so correct any that are wrong.

**Do this first:** add `request_id` to the error body (not only the header) on every error response. Your tickets are screenshots, and a screenshot of a body shows the ID. A header never appears in one. This one change addresses "we can almost never trace the original request."

## Assumptions to confirm

- The API is REST-only. If gRPC is involved, the taxonomy choice changes to domain/reason.
- This is a retrofit, and the consumers are third-party integrators. That is the most demanding consumer type, so design for it.
- I don't know which codes or message strings integrators already branch on. Treat everything that has shipped as contract.
- There is no shared multi-service taxonomy and no hard ship date. The default rung, code/subcode, therefore fits.

## Diagnosis

- **~251 of 412 tickets (61%) are "what does this error mean."** That is 412 × 0.61.
- **Cause 1:** one shared "Error object" page can't say what a specific code means, what causes it, or how to fix it.
- **Cause 2:** there is no request ID in what integrators paste, so you can't trace the request.
- **Probable cause 3 (unconfirmed):** the messages themselves don't name the field, value, or constraint. Audit this in step 1 before trusting it.

## The fix, in order

### 1. Audit (about 1 week)

- Pull 5-10 real error responses per endpoint from production logs. Use the pasted screenshots from last month's tickets as extra samples.
- Build one table row per endpoint with these columns: endpoint, status returned, envelope shape, code present?, field-level detail?, retry signal?, documented?, findings.
- Grade each row against the skill's failure-mode checklist:
  - generic message
  - leaked internals in a 500
  - envelope shape that differs between endpoints
  - a code that appears in responses but not in docs
  - 200 with an error body
  - no request ID
  - a bare 500 with no retry signal
- Inventory every shipped code, field, and message string. Map each old identity to its new one, and never silently drop one.

### 2. Taxonomy

- Use the code/subcode catalog, with each code pinned to one HTTP status. Example: `VALIDATION_ERROR` (400) has the subcodes `REQUIRED`, `INVALID_FORMAT`, and `OUT_OF_RANGE`.
- Use a flat catalog instead if your surface is small and each category has essentially one reason.
- Publish it as one catalog. Nothing observable in a response may be missing from it.

### 3. Envelope

- Use RFC 9457 problem details with `Content-Type: application/problem+json` on every endpoint and status.
- Choose the correct HTTP status first. Settle 400 vs 422 and 401 vs 403 explicitly.
- Add these extension members:
  - `code`
  - `errors[]` for field-level detail
  - `retryable`
  - `documentation_url`
  - `request_id`
- Also send an `X-Request-ID` header.
- Reject a 200 with an error body.

Example:

```json
{
  "type": "https://api.fieldnest.example/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "One field failed validation.",
  "code": "VALIDATION_ERROR",
  "errors": [{
    "field": "...", "code": "OUT_OF_RANGE",
    "message": "<field> must be between <min> and <max>; received <value>.",
    "value_provided": "...", "constraints": {"min": "...", "max": "..."}
  }],
  "retryable": false,
  "documentation_url": "https://docs.fieldnest.example/errors#VALIDATION_ERROR",
  "request_id": "req_..."
}
```

The field names and values above are placeholders. Use your real ones.

### 4. Messages

- Name the field, the value received, and the constraint violated in one object.
- Use corrective, non-blaming wording: "Provide the date as `MM/DD/YYYY`", not "You entered an invalid date."
- When one paragraph can't carry the fix, link `documentation_url` instead of cramming it into the message.
- Say in the catalog which messages are safe to show end users.

### 5. Retry signals

- Send `Retry-After` on 429 and 503.
- Include `retryable: true|false` in the body of every error.
- Never return a bare 500. Add an explicit retry signal to it.

### 6. Documentation, which is your biggest gap

- **Per endpoint:** list every status the endpoint can return in its OpenAPI `responses` block. Give each distinct error code its own named example under that status. Don't use one `$ref` to a generic schema.
- **Catalog page:** publish one public page with a stable anchor per code, so `documentation_url` always has a target. For each code, state:
  - its HTTP status
  - what causes it
  - whether it is retryable
  - whether its message is safe to show end users
  - the fix path
- **Spec generation:** generate the catalog and the examples from the OpenAPI spec so they can't drift from the responses.
- **Support form:** require `request_id` as a field. Add a docs note: "Paste the `request_id`, not a screenshot."
- **Gatekeeper:** one owner or review step through which every new code passes. No code ships without a catalog entry.

### 7. Stability

- Codes are API contract. Evolve them by addition only. Never rename, repurpose, or delete a shipped code.
- Declare in the catalog that `code` is stable and `message` and `detail` text is not contractual.

## Measurement

### Where I disagree with the proposed target

I'd push back on "error-related tickets under 10% of volume within a quarter" as a commitment.

- **No evidence supports 10%.** The skill is explicit that no industry threshold exists. The sourced claim is only directional: echoing a request ID turns vague tickets into traceable ones.
- **It implies a very large cut.** 10% of 412 is about 41 tickets. If "error-related" is at least today's ~251 tickets, that is a reduction of roughly 84% or more.
- **Its denominator is unstable.** A share of total volume can fall when other ticket types rise, or rise when you fix other things. It can also be missed or hit for reasons unrelated to your work.
- **Your baseline is one month.** It may be noisy, and I don't know how "error-related" was labelled.
- **Better framing:** get leadership to commit to the work and the gates. Report the ticket numbers as a trend, not as a pass/fail commitment.

### Gates: binary and fully in your control

Ship is blocked until both pass.

1. **Envelope consistency:** one shape on 100% of endpoints and statuses. A single deviating endpoint fails.
2. **Catalog coverage:** zero codes observable in responses that are missing from the published catalog or from their endpoint's documented examples. Verify with a contract test against the spec plus a scan of production error responses.

### Trend metrics: watch these, don't gate on them

1. **Share of error-related tickets that arrive with a `request_id`.** This is the metric most directly tied to your 61% problem. Baseline it from the current month. It is probably near zero today, since no ID is exposed.
2. **Volume of "what does this error mean" tickets.** Set the baseline from your first full month after the new surface ships, then improve against it. Absolute counts are less noisy than a share of total volume.
3. **Traced-resolution rate.** Of the error tickets that carry a `request_id`, how many did support trace and close without a back-and-forth? Also track median time to first useful reply on those tickets. Both are leading indicators you can move fast.
4. **Docs engagement (optional).** Hits on `documentation_url` anchors per code. Codes with high ticket volume and low doc traffic point to messages or pages that need work.

### Setup before you start

- **Define "error-related" once.** Write the tagging rule and apply it retroactively to the last 2-3 months, so the baseline isn't one noisy month.
- **Add a ticket field** for `request_id` present: yes or no. Without it, metric 1 can't be measured.
- **Keep the 10% as a stretch goal, not a commitment.** Revisit it after one full month of data on the new surface.

## Rollout order

1. Request ID in the body and header, plus the support-form field. Ship this first, since it is the quickest win.
2. Audit, then catalog, then the envelope on the highest-ticket endpoints.
3. Per-endpoint OpenAPI examples and the generated catalog page.
4. Gates enforced in CI, then the baseline month.

## Open items I couldn't resolve

- I don't know which codes and messages existing integrators branch on. Confirm this before any rename.
- I haven't seen your real error responses, so the audit findings above are hypotheses.
- I don't know how your tickets are tagged "error-related."