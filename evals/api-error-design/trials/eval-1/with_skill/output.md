# Ledgerline error taxonomy: domain/reason on `google.rpc.Status`

## ⚠️ One change to your brief: no HTTP status column

You asked for a flat list of codes, each mapped to an HTTP status, as Stripe does. For a gRPC-only surface, the `api-error-design` skill rules that shape out. It doesn't just rank it lower. Flat and code/subcode catalogs define a code's identity by pinning it to one HTTP status, and you have no HTTP surface to pin to. What's left is **domain/reason** (Google AIP-193 `ErrorInfo`), which fits your team:

- **You live in Google Cloud conventions.** `google.rpc.Status` and `ErrorInfo` are what your tooling and the partners' gRPC clients already understand. It's the effort-heavy rung for most teams, but nearly free for yours.
- **One taxonomy across 12 services, for years.** The skill's rule for a shared long-lived taxonomy is domain/reason. A flat list drifts into 12 dialects.
- **Publishing an HTTP column would misinform partners.** The gRPC project says servers must not derive HTTP status from its mapping table, because the mapping is lossy. Three codes collapse to 400, and `CANCELLED` becomes a non-standard 499. A column nobody can observe is documentation of behavior that doesn't exist.
- **"We'll map statuses later" comes back as scope.** The re-promotion trigger is: a REST surface joins the family. If that happens, design a deliberate outward mapping then. Don't use the canonical table.

The docs site keeps Stripe's strengths, and the closest analog of "code → status" is **reason → gRPC code**. The catalog is flat and enumerable, every reason has an anchor, and every entry says what to do.

## Assumptions

- **Consumers:** about 40 third-party fintech partners, plus machine callers. That is the most demanding consumer type, so I'm designing for them.
- **Layered failures:** yes. Payments, ledger and compliance causes need more than one code per error.
- **Retrofit:** today's `UNKNOWN` plus prose is the legacy surface. I haven't seen real responses, and I don't know which strings partners match on. See the migration section.
- **Go and buf:** I'm assuming protobuf with `buf`. The tooling parts are language-agnostic.

## 1. The model: four layers

| Layer | Carrier | Open or closed | Stable? |
|---|---|---|---|
| 1. Class | gRPC `code` (the 17 canonical codes) | Closed | Yes |
| 2. Identity | `ErrorInfo.reason` and `ErrorInfo.domain` | Open catalog, additions only | Yes. This is what callers branch on. |
| 3. Context | `ErrorInfo.metadata` and typed details | Keys added over time | Keys only added |
| 4. Prose | `Status.message` | n/a | **No.** Not contractual. |

- **Domain:** one domain for all 12 services, for example `api.ledgerline.com`. Pick it once, because it can never change. The emitting service goes in `metadata["service"]`, not in the domain. Reasons are unique platform-wide.
- **Reason:** `UPPER_SNAKE_CASE`, at most 63 characters, and **each reason maps to exactly one gRPC code, forever**.
- **gRPC code:** choose the most specific applicable code (`OUT_OF_RANGE` over `FAILED_PRECONDITION`). The server never emits `UNKNOWN`. It is reserved for client libraries that can't classify a failure.

### Rules for every error

1. `Status.details` always contains one `ErrorInfo`.
2. It always has one `RequestInfo` with `request_id`. The same ID is also returned as an `x-request-id` header or trailer on **every** response, success or failure. Tell partners to quote it in tickets.
3. It always has one `Help` link to `https://docs.ledgerline.com/errors#<REASON>`. This is Stripe's `doc_url`. The anchor exists before the reason ships.
4. `metadata["retryable"]` is `"true"` or `"false"`. `google.rpc` has no retry boolean. This is the one field a generic handler branches on without a lookup table. `RetryInfo.retry_delay` is added when a delay is known.
5. **`DebugInfo` never leaves the service.** An outbound interceptor strips it from `details` and replaces unknown internal errors with `INTERNAL_ERROR`. Sanitizing `message` alone isn't enough. No stack traces, SQL text, hostnames or paths in any response.
6. **Cross-partner access returns `RESOURCE_NOT_FOUND`**, not a permission error, so you never confirm that another partner's resource exists.

### Example: validation failure

```
code: INVALID_ARGUMENT
message: "Request validation failed: 2 fields invalid. See BadRequest for details."
details:
  - ErrorInfo
      domain: "api.ledgerline.com"
      reason: "REQUEST_VALIDATION_FAILED"
      metadata: { service: "transfers", retryable: "false" }
  - BadRequest
      field_violations:
        - field: "amount.units"
          reason: "OUT_OF_RANGE"
          description: "amount.units must be between 1 and 10000000; received -5."
        - field: "currency_code"
          reason: "UNSUPPORTED_CURRENCY"
          description: "currency_code must be an ISO 4217 code we support; received 'XBT'."
  - RequestInfo { request_id: "req_7c8d9e0f" }
  - Help { links: [{ description: "REQUEST_VALIDATION_FAILED", url: "https://docs.ledgerline.com/errors#REQUEST_VALIDATION_FAILED" }] }
```

### Example: layered payments failure

Stripe's `decline_code` layer maps onto metadata:

```
code: FAILED_PRECONDITION
message: "The payment was declined by the issuing bank."
details:
  - ErrorInfo
      domain: "api.ledgerline.com"
      reason: "PAYMENT_DECLINED"
      metadata: { service: "payments", retryable: "false", decline_code: "do_not_honor" }
  - RequestInfo { request_id: "req_a1b2c3d4" }
  - Help { ... #PAYMENT_DECLINED }
```

- `reason` is the stable identity Ledgerline controls.
- `decline_code` is an open vocabulary that comes from the card network or bank, not from Ledgerline. Document it in a second table on the same page, and don't try to enumerate it as reasons.
- If a decline is a normal business outcome of the RPC, return it in the response message and not as an error. Decide that per RPC.

## 2. Catalog (draft v1)

I haven't seen your 12 services, so this is a starter set of 33 reasons. Walk each service's failure conditions against it. Anything uncovered becomes a new reason before it ships.

- **Retry?** `yes` means a retry may succeed without changing the request. `after fix` means the caller must change something first. `no` means a retry fails identically.
- **User-safe?** means `message` can be shown to an end user verbatim. Decide this per reason, and say it in the docs, as Stripe does for card errors.
- Retry on `UNAVAILABLE` only with the same idempotency key. Backoff and jitter are owned by `api-idempotency-retry`.

### Request

| Reason | gRPC code | Retry? | User-safe? | Cause → fix |
|---|---|---|---|---|
| `REQUEST_VALIDATION_FAILED` | `INVALID_ARGUMENT` | after fix | no | One or more fields invalid → read `BadRequest`, fix each field |
| `FIELD_MASK_INVALID` | `INVALID_ARGUMENT` | after fix | no | Unknown path in `update_mask` |
| `PAGE_TOKEN_INVALID` | `INVALID_ARGUMENT` | after fix | no | Token malformed or from another query → restart listing |
| `PAGE_OUT_OF_RANGE` | `OUT_OF_RANGE` | no | no | Token points past the end of the data |
| `IDEMPOTENCY_KEY_MISSING` | `INVALID_ARGUMENT` | after fix | no | Mutating RPC called without a key |
| `IDEMPOTENCY_KEY_REUSED` | `INVALID_ARGUMENT` | after fix | no | Same key sent with a different payload → use a new key |
| `IDEMPOTENCY_REQUEST_IN_PROGRESS` | `ABORTED` | yes | no | Original request with this key still running → retry same key shortly |

### Authentication and authorization

| Reason | gRPC code | Retry? | User-safe? | Cause → fix |
|---|---|---|---|---|
| `CREDENTIALS_MISSING` | `UNAUTHENTICATED` | after fix | no | No token in metadata |
| `CREDENTIALS_INVALID` | `UNAUTHENTICATED` | after fix | no | Bad signature or unknown client |
| `TOKEN_EXPIRED` | `UNAUTHENTICATED` | after fix | no | Refresh the token, then retry |
| `SCOPE_INSUFFICIENT` | `PERMISSION_DENIED` | after fix | no | Token lacks the scope for this RPC. `metadata["required_scope"]` names it. |
| `PARTNER_SUSPENDED` | `PERMISSION_DENIED` | no | no | Account suspended → contact support with `request_id` |
| `SOURCE_IP_NOT_ALLOWED` | `PERMISSION_DENIED` | after fix | no | Caller IP is not on the partner allowlist |
| `FEATURE_NOT_ENABLED` | `PERMISSION_DENIED` | after fix | no | Product not enabled for this partner |

### Resources and concurrency

| Reason | gRPC code | Retry? | User-safe? | Cause → fix |
|---|---|---|---|---|
| `RESOURCE_NOT_FOUND` | `NOT_FOUND` | no | no | `metadata["resource_type"]` names the type. Also returned for cross-partner access. |
| `RESOURCE_ALREADY_EXISTS` | `ALREADY_EXISTS` | no | no | Create with a client-supplied ID that exists |
| `CONCURRENT_MODIFICATION` | `ABORTED` | yes | no | Etag mismatch → re-read, reapply, resend |

### Business state (ledger and payments)

| Reason | gRPC code | Retry? | User-safe? | Cause → fix |
|---|---|---|---|---|
| `ACCOUNT_CLOSED` | `FAILED_PRECONDITION` | no | yes | Operation on a closed account |
| `ACCOUNT_FROZEN` | `FAILED_PRECONDITION` | no | yes | Account frozen → contact support |
| `INSUFFICIENT_FUNDS` | `FAILED_PRECONDITION` | after fix | yes | Balance below amount → fund the account |
| `CURRENCY_MISMATCH` | `FAILED_PRECONDITION` | after fix | no | Source and destination currencies differ |
| `TRANSFER_LIMIT_EXCEEDED` | `FAILED_PRECONDITION` | after fix | yes | Per-transaction or daily business limit. `metadata["limit"]` and `["period"]` say which. |
| `TRANSFER_ALREADY_SETTLED` | `FAILED_PRECONDITION` | no | no | Cannot cancel or modify a settled transfer |
| `TRANSFER_NOT_CANCELLABLE` | `FAILED_PRECONDITION` | no | no | State does not allow cancel |
| `PAYMENT_DECLINED` | `FAILED_PRECONDITION` | no | yes | Issuer or network declined. See `decline_code`. |
| `COMPLIANCE_HOLD` | `FAILED_PRECONDITION` | no | no | Held for review → contact support. ⚠️ **The message must never state the screening reason.** Disclosing it can be an AML tipping-off problem. Confirm with compliance. |

### Throttling and quota

| Reason | gRPC code | Retry? | User-safe? | Cause → fix |
|---|---|---|---|---|
| `RATE_LIMIT_EXCEEDED` | `RESOURCE_EXHAUSTED` | yes | no | Always with `RetryInfo`. `metadata["limit_name"]` says which limit. |
| `QUOTA_EXCEEDED` | `RESOURCE_EXHAUSTED` | no, until reset | no | Periodic quota used up. `QuotaFailure` says which. `metadata["reset_at"]` gives the reset time. |

### Platform

| Reason | gRPC code | Retry? | User-safe? | Cause → fix |
|---|---|---|---|---|
| `SERVICE_UNAVAILABLE` | `UNAVAILABLE` | yes | no | Transient. Always `RetryInfo`. |
| `UPSTREAM_RAIL_UNAVAILABLE` | `UNAVAILABLE` | yes | no | Bank or payment-rail dependency down. Mutations may be in an unknown state → retry with the same idempotency key. |
| `OPERATION_TIMED_OUT` | `DEADLINE_EXCEEDED` | yes | no | Server-side deadline hit. **For mutations the outcome is unknown.** Retry with the same key, or look the resource up. |
| `INTERNAL_ERROR` | `INTERNAL` | `metadata["retryable"]` set explicitly per case | no | Our bug. Quote `request_id`. A bare `INTERNAL` with no retry signal is a defect. |
| `METHOD_NOT_IMPLEMENTED` | `UNIMPLEMENTED` | no | no | RPC exists in the proto but isn't served |

`CANCELLED` is client-originated and carries no reason in this catalog.

### Field-level reasons (`BadRequest.FieldViolation.reason`)

A second, smaller closed enum:

- `REQUIRED`
- `INVALID_FORMAT`
- `OUT_OF_RANGE`
- `INVALID_ENUM`
- `TOO_LONG`
- `TOO_SHORT`
- `UNSUPPORTED_CURRENCY`
- `INVALID_RANGE`

Every violation names the field, the value received and the constraint, in `description`. For a cross-field rule such as `end_date` before `start_date`, emit one violation per involved field with the same reason (`INVALID_RANGE`). Each description names both fields and both values. `FieldViolation` has no multi-field form, so this is a documented compromise.

## 3. Make the catalog enforceable

The catalog is a protobuf enum. That gives you a gate for free. `buf breaking` (FILE) catches renamed, renumbered or deleted values, and `reserved` retires them.

```proto
// ledgerline/errors/v1/reasons.proto
enum Reason {
  REASON_UNSPECIFIED = 0;

  // Funds are below the requested amount.
  INSUFFICIENT_FUNDS = 1 [(ledgerline.errors.v1.spec) = {
    grpc_code: FAILED_PRECONDITION, retryable: RETRY_AFTER_FIX, end_user_safe: true
  }];
  // ...
}
```

- **One constructor.** Services call `errs.New(Reason, ...)`. It reads the gRPC code, the retryable flag and the doc link from the enum option. A call site cannot pick a mismatched code, and the envelope is identical on all 12 services.
- **No ad hoc errors.** Add a lint rule (ast-grep or a custom linter) that forbids raw `status.Error(...)` and `codes.*` outside the errors package. Per your gate rules, this is a suggestion for you to approve. I haven't added it.
- **Server interceptor.** It strips `DebugInfo`, converts any non-catalog error to `INTERNAL_ERROR`, and attaches `RequestInfo`. It also increments a counter labelled by gRPC code and reason, which has bounded cardinality and gives you dashboards that don't flatten into one `UNKNOWN` bucket.
- **Docs are generated.** The catalog page is generated from the enum options: one anchor per reason, with the gRPC code, retryable flag, user-safe flag, cause and fix. Add a worked example per reason.
- **Per-RPC errors.** Add a repeated method option listing the reasons each RPC can return, and render it in the reference docs. A CI test asserts that observed errors are a subset of the declared ones.

## 4. Stability contract (publish this on the docs page)

- `(domain, reason)` and the gRPC code are stable and safe to branch on.
- `message` and `description` text is **not contractual** and may change without notice.
- Evolve by addition only: new reasons, new optional metadata keys. Never repurpose, rename or delete a shipped reason.
- Retiring a reason goes through your deprecation process, on a version boundary (see `api-versioning-policy`).
- Gatekeeper: every new reason passes one named owner or review step. The invariant is that no reason reaches production without a catalog entry and a docs anchor.

## 5. Migrating off `UNKNOWN` + prose

Changing a status from `UNKNOWN` to `FAILED_PRECONDITION` is a visible change, and with 40 partners someone may branch on today's prose (Hyrum's Law).

1. **Inventory.** Mine production logs for every distinct `UNKNOWN` message string per RPC, and ask partners' integration contacts which they match on. I'd like 5–10 real responses from different services to audit.
2. **Map** each old identity to a `(code, reason)` pair in a published table.
3. **Announce** a window, then flip service by service. Where practical, keep the old message text for the same condition during the window, since `message` is now non-contractual.
4. If you can't prove no partner depends on `UNKNOWN`, treat the flip as a breaking change and ship it behind a new API version boundary.

## 6. Measurement

Gates, which are binary:

- Envelope consistency: 100% of error responses on all 12 services carry `ErrorInfo`, `RequestInfo` and `Help`.
- Catalog coverage: zero reasons observed in production, or in any RPC's declared list, that are missing from the published catalog.

Trends to watch afterwards, with no pass threshold:

- the share of error tickets that arrive with a `request_id`
- tickets asking what an error means

Set the baseline from the first month.

## Open questions for you

1. **Domain.** Do you own `api.ledgerline.com` (or another domain) as the permanent `ErrorInfo.domain`?
2. **Partner reliance on current errors.** Do partners match on `UNKNOWN` prose today? That decides whether the migration needs a version boundary.
3. **Declines.** Are card or bank declines a normal RPC outcome (response field) or an error?
4. **Compliance.** Can compliance confirm that `COMPLIANCE_HOLD` must not carry a reason, and whether other reasons have disclosure limits?
5. **Service list.** Send me the 12 service names and I'll walk each one's failure conditions against the catalog to find the gaps.