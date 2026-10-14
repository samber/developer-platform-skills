# Ardenway Labs public REST API: pre-launch review

**Scope:** this review is based only on your description. I haven't seen code, the Notion page, or live responses. Where a finding depends on something I can't see, I say so.

## Verdict

Don't launch as is. The three error shapes and the null-200 responses are cheap to fix now and expensive after external clients depend on them. Skipping the spec is defensible only in part. Full per-endpoint documentation can wait, but a handful of contract decisions can't.

## P0: fix before launch

### 1. Return one error shape everywhere

You have three behaviors today:

| Source | Behavior |
|---|---|
| `/v1/accounts` | `{"error": "..."}` |
| `/v1/transfers` | `{"errors": [{"code": 4012, "detail": "..."}]}` |
| a few endpoints | `200` with `null` |

- A client can't write one error handler against this. Every integrator ends up with per-endpoint special cases.
- The shapes also show that no shared error layer exists. Each handler formats its own errors, so each handler is a separate chance to leak something.
- Pick one envelope, enforce it in one middleware, and make handlers raise typed errors instead of building bodies. I recommend RFC 9457 `application/problem+json`, because it's a standard and your integrators' tooling already understands it.

```json
{
  "type": "https://docs.<your-domain>/errors/resource-not-found",
  "title": "Resource not found",
  "status": 404,
  "code": "resource_not_found",
  "request_id": "req_01J...",
  "errors": [{ "field": "account_id", "code": "invalid_format" }]
}
```

- Use **string codes** (`insufficient_funds`), not bare integers like `4012`. Integers need a lookup table to be readable, and the table drifts. If you want to keep `4012`, keep it as a secondary `legacy_code` field.
- Every error carries a `request_id`, which is also returned in a response header. Support and auditors can then correlate a client report to your logs without the body containing any internals.
- Treat the code list as a public enum. Adding codes is non-breaking, but renaming or removing one is breaking.

### 2. Replace `200 null` with `404`

- `200 null` can't be told apart from "exists but empty", "forbidden", or "handler bug swallowed an exception". Clients will treat it as success and fail later, somewhere harder to debug.
- Return `404` with the standard envelope. For resources the caller isn't entitled to see, also return `404`, not `403`. Use the **same body and similar timing** in both cases, so an attacker can't enumerate which account or transfer IDs exist.
- Find all such endpoints by grep or by crawling your own API, not from memory. "A couple" is exactly the kind of number that turns out to be seven.

### 3. Audit what error strings contain (ISO 27001 relevant)

- You said `/v1/accounts` "throws" an error. If `error` is built from `e.message`, it can contain SQL fragments, table or column names, file paths, class names, upstream vendor names, or internal hostnames. Check this first.
- **Rule:** the client-facing `title`, `detail`, and `code` come from a fixed catalog you wrote. Never pass exception text to the client. Full detail goes to server logs keyed by `request_id`.
- Add a **catch-all handler** that maps any unmapped exception to a generic `500` in the same envelope. Without it, the framework's default error page or stack trace is your real error format on the day something breaks.
- Check the surfaces around the app, not only handlers:
  - Router-level `404`/`405`, body-parse failures (malformed JSON), oversize payloads, and unsupported media types often bypass app middleware and return a different format.
  - `Server`, `X-Powered-By`, and framework version headers.
  - Debug flags or verbose modes left on in production.
- Auth responses must not distinguish "no such user" from "wrong credential". Validation errors may name the offending field, but should not echo submitted values, especially account numbers, tokens, or amounts.
- Make sure IDs are opaque and non-sequential for accounts and transfers. Sequential IDs combined with the `200 null` behavior make enumeration trivial.
- For the audit trail, map this to your Annex A controls. The relevant ones are likely 8.26 (application security requirements), 8.28 (secure coding), 8.15 (logging), and 8.32 (change management). Confirm the exact mapping against your Statement of Applicability.

### 4. Money movement needs explicit safeguards

You didn't mention these, so I can't tell whether they exist. Confirm each one:

- **Idempotency** on `POST /v1/transfers` (an `Idempotency-Key` header). Without it, a client retry after a timeout can double-send money.
- **Amount representation:** integer minor units or decimal strings plus a currency code. Never JSON floats.
- **Authorization on every object ID**, not only at the route level. Test that account A's token can't read or move account B's resources (a BOLA/IDOR test).
- **Rate limiting** with a standard `429` in the same envelope, plus `Retry-After`.

## P1: do before or at launch

### 5. The spec: what can wait and what can't

Writing it after things "settle" is the wrong order, for these reasons:

- **A public API never settles after launch, it freezes.** Once clients depend on a behavior, changing it is a breaking change. Cleanup becomes a versioning project, not an edit.
- **The Notion page is an uncontrolled document.** A PM updating it by hand will drift from the code. For an ISO 27001 audit, "the interface is described in a hand-edited wiki page" is a weak answer under change management.
- **You can't automate what isn't specified.** Without a schema you have no contract tests, no response-shape lint, and no automated checks. You need those to prove claims like "no endpoint returns a stack trace".

Writing all 40 endpoints by hand isn't the answer either. A cheaper path:

1. **Decide the cross-cutting contract now.** This is about a day of work, not a spec: error envelope and code catalog, auth scheme, ID format, pagination, money format, idempotency, rate-limit headers, versioning and deprecation policy. These are the decisions that are costly to change.
2. **Generate the spec from code or traffic** instead of writing it. Most frameworks can emit OpenAPI from route and type definitions, and tools can infer it from recorded requests. Tell me your framework and I can be more specific. Treat the output as a draft to correct, not as documentation.
3. **Make the spec a CI artifact.** Fail the build when generated output differs from the committed file without review. This replaces the manual Notion upkeep, and the diff history is your change-control evidence.
4. **Run a fuzzer against staging**, such as Schemathesis or ZAP, once any schema exists. It will find `500`s, leaked traces, and `null`-200s mechanically.
5. Polish the prose and examples after launch. Leaving that step for later is fine.

### 6. Versioning and deprecation policy

- You have `/v1` in the path, which is good. Write down what counts as a breaking change, and how long a deprecated behavior lives (for example `Deprecation` and `Sunset` headers, and a minimum notice period).
- State explicitly that new fields and new error codes are non-breaking, so clients are told to ignore unknown ones.

### 7. Logging that matches the error policy

- Log full error context server-side with `request_id`, but redact tokens, full account numbers, and personal data from logs. A leak through logs is still a leak in an audit.
- Set retention and access controls on those logs.

## P2: worth doing, not blocking

- Consistent status-code mapping (`400` malformed, `401` unauthenticated, `404` missing or not visible, `409` conflict or idempotency mismatch, `422` semantic validation, `429` rate limited), documented once.
- A consistent pagination shape, if list endpoints differ.
- A machine-readable error catalog page generated from the same enum the code uses.
- A security contact and `security.txt`, which auditors and researchers expect on a public financial API.

## Suggested order of work

1. Build the error middleware and catch-all, and write the code catalog. Roughly 1 to 2 days.
2. Migrate `/v1/accounts`, `/v1/transfers`, and the null-200 endpoints to it. Roughly 1 to 3 days, depending on handler count.
3. Run the leakage checks: force malformed JSON, bad routes, DB-down, and upstream-timeout conditions on staging, and read every response body and header.
4. Add the IDOR tests and the idempotency check on transfers.
5. Generate a draft OpenAPI from code, put it in CI, and fuzz staging.

## What I'd need to tighten this review

- Framework and language, to say how to centralize errors and generate the spec.
- Whether the API is already used by any external client. If yes, the error change needs a migration window. If not, change it now.
- The list of endpoints that return `null`.
- A sample of real `500` and malformed-input responses from staging. That is the fastest way to find actual leaks rather than potential ones.