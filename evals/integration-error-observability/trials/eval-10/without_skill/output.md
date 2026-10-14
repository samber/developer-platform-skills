# Shippable design: PHI-free failure diagnostics for synchronous POSTs

## Principle

Bodies never leave the tenancy boundary, so the viewer must be PHI-free by construction. We stop capturing less and start capturing differently. We record what happened to the request (stage, rule, field path, timing), never what the request contained.

Every field is added to an allowlist at the type level. Nothing is redacted after the fact.

## What the viewer shows (new columns)

Today it shows timestamp, method, path and status.

| Field | Why it answers "why did it fail" | PHI risk and handling |
|---|---|---|
| `request_id` | Also returned in the `X-Request-Id` response header. It is the support handle. | None. |
| `route` | Template such as `/v2/claims/{claim_id}/adjudicate`. **Replaces the raw path.** | Raw paths and query strings carry claim and member IDs. Log the template only. |
| `error_code` | Stable enum such as `VALIDATION_FAILED`, `AUTH_SCOPE_MISSING`, `PAYER_TIMEOUT`, `DUPLICATE_IDEMPOTENCY_KEY`, `RATE_LIMITED`, `PAYLOAD_TOO_LARGE`, `UNSUPPORTED_MEDIA_TYPE`. | None. Fixed enum. |
| `failed_stage` | `edge`, `auth`, `parse`, `schema`, `business_rule`, `downstream:<service>`, `serialize`. | None. |
| `rule_id` | The business rule or schema rule that fired, for example `R-204`. It links to docs. | None. |
| `field_paths[]` | Schema-defined paths only, for example `claim.lines[2].procedure_code`, with the reason `missing`, `wrong_type`, `format`, `enum` or `too_long`. | Low, handled below. |
| `duration_ms` and `stage_timings` | Separates slow client, our slowness, and downstream slowness. | None. |
| `downstream` | Which dependency failed, its status class, and whether it timed out. | None. Never log its body. |
| `req_bytes`, `content_type`, `content_encoding` | Catches truncated bodies, wrong content type, and oversized payloads. | None. |
| `api_version`, `client_id`, `sdk_version`, `idempotency_key_seen`, `retry_of` | Catches version skew, retries, and replays. | `idempotency_key` may be client-chosen, so log only seen, new, or replayed. |
| `tenant_id` | Scoping. | Internal ID. |

## Hard rules for PHI safety

1. **Allowlist logging.** The log event is a typed struct. The logger accepts only that struct, with no `map[string]any` and no free-text `extra` field. A new field needs a code-review sign-off from privacy.
2. **No interpolated error strings.** Error messages come from templates with no values. "Invalid value 'J. Smith'" is forbidden. "Field `patient.name` failed rule R-112 (format)" is allowed.
3. **Field paths come from the schema, never from the payload.**
   - Dynamic keys, for example a free-form map where the key is user-provided, are collapsed to `[*]` or `{key}`.
   - Array indices are kept because they are positions, not data.
   - Unknown fields in the payload are reported as `unknown_field_count: N`, never by name, because attacker or client key names can contain PHI.
4. **No body-derived hashes, prefixes, lengths per field, or samples.** Hashes of low-entropy fields such as member IDs, DOBs and codes are reversible by brute force. Only total `req_bytes` is allowed.
5. **Header allowlist.** Log only `Content-Type`, `Content-Encoding`, `Content-Length`, `User-Agent` (sanitized), `Idempotency-Key` presence, and version headers. Never log `Authorization`, cookies, or custom headers.
6. **Downstream errors are mapped, not passed through.** Map upstream error bodies to our own enum at the boundary. Raw upstream messages often echo PHI.
7. **Same rules for traces, metrics, and exception reporters.** The viewer is only one sink. Stack traces and panic handlers must go through the same sanitizer, and the third-party error tracker gets the same event type only.

## Caller-facing side (cuts the ticket pile directly)

The caller already holds their own request, so this is not a disclosure.

- Every error response returns a structured body, which is not PHI because it is built from the same allowlist:
  `{ "request_id", "error_code", "failed_stage", "rule_id", "field_paths": [...], "retryable": bool, "docs_url" }`
- Always set `X-Request-Id`, even on 5xx and edge failures such as gateway timeouts.
- `retryable` and `Retry-After` handle the "should I retry?" question.
- A docs page per `error_code` and `rule_id` states the cause and fix. This probably deflects a large part of the 70%.

## Viewer behavior

- Filter by `error_code`, `failed_stage`, `rule_id`, `client_id`, `route`, and time.
- Search by `request_id` (what customers paste into tickets).
- Group by "top failing rule this week" per client. This turns support from reactive to proactive.
- Support staff can view it anywhere because it holds no PHI. They still use the existing access controls and audit trail.

## What we are not shipping (and why)

- **Body capture, even encrypted, even short-lived.** Legal's no is absolute, and "in the tenancy boundary" storage that is queryable from outside the boundary breaks it.
- **Customer-side "replay" tooling.** It is a possible phase 3 that runs inside the customer's own tenancy. It needs a separate legal review, so it is not in this plan.
- **Masked bodies.** Masking is a pattern-matching bet on PHI shapes, so it is the wrong risk posture here.

## Rollout (smallest useful slice first)

1. **Request ID and error taxonomy.** Add `X-Request-Id` everywhere. Define the `error_code` enum and map existing failures to it. Add a catch-all `UNCLASSIFIED` and track its share, which becomes the backlog.
2. **Typed log event and sanitizer.** Add the struct, route templating, and stage timings. Deploy it dark, writing alongside the old logs.
3. **Schema and rule failure details.** Add `field_paths` and `rule_id`. This is the biggest win for "my call failed", because most failures on synchronous POSTs are probably validation or business rules. Check that against the real distribution in step 2's data.
4. **Viewer columns, filters, and the caller error body.**
5. **Docs per code.** Write them in order of ticket volume.

Measure after steps 1 and 2: tickets that arrive with a `request_id`, share of `UNCLASSIFIED`, and tickets resolved without engineering escalation.

## Verification before launch (the part Legal will ask about)

- **Canary-PHI test in CI.** Send requests containing unique sentinel strings (fake names, member IDs, DOBs) in every position: body values, keys, query, path, headers. Force every error class. Then grep all sinks (logs, traces, metrics, error tracker, viewer API responses) and fail the build if any sentinel appears.
- **Fuzz error paths** for interpolation bugs, for example malformed JSON, whose parser errors often quote the offending text.
- **Review third-party libraries** (JSON parser, validator, HTTP client, ORM) for messages that echo input. Wrap or replace them at the boundary.
- **Privacy sign-off** on the struct definition. The struct is the contract.

## Open questions for you

1. Is the viewer customer-facing, support-facing, or both? The design works for both, but customer-facing makes `tenant_id` scoping a hard requirement.
2. Do any route templates or `client_id` values embed PHI today? Check that before trusting step 2.
3. Which downstream services are involved? Each needs an error mapping.
4. Is a per-field "reason" such as `format` or `enum` acceptable to Legal? It reveals the kind of failure but not the value, and I expect it passes, but confirm it explicitly.