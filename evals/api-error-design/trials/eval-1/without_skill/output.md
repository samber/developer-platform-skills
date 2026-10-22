# Ledgerline error catalog: taxonomy v1

## 1. Drop the HTTP column

You have no REST gateway and none planned, so an HTTP status on each code would have no consumer. It would also lose information. FAILED_PRECONDITION, OUT_OF_RANGE and INVALID_ARGUMENT all collapse to 400, and the gRPC code is the better signal.

Use the gRPC status code as the Stripe-style "type" and a stable reason string as the Stripe-style "code". This is Google's own model (AIP-193, `google.rpc.Status` with `ErrorInfo`), so it fits your Google Cloud shop.

If a gateway ever appears, Google publishes a deterministic `google.rpc.Code` to HTTP mapping. Adding the column later costs nothing, so don't build it now.

## 2. Wire contract

Every error returns a `google.rpc.Status` with these details, carried in the `grpc-status-details-bin` trailer.

| Part | Rule |
|---|---|
| gRPC `code` | One of the 17 canonical codes. It drives client retry and control flow. Never `UNKNOWN` from application code. |
| `message` | English prose for humans. It is not a contract and may change at any time. No PII and no account numbers. |
| `ErrorInfo.reason` | The catalog code, `UPPER_SNAKE_CASE`, at most 63 characters. **Required on every error.** |
| `ErrorInfo.domain` | `api.ledgerline.com`. The reason is unique within the domain. |
| `ErrorInfo.metadata` | String to string map, keys in `lowerCamelCase`, values never contain PII. Keys per reason are listed below and are part of the contract. |
| `RequestInfo` | `request_id`, always set. Partners quote it to support. |
| Standard details | `BadRequest` (field violations), `RetryInfo` (when to retry), `QuotaFailure`, `PreconditionFailure`, `ResourceInfo`. Use them where noted. |

**Client contract:**
1. Switch on `reason`.
2. If the reason is unknown (added after the client was built), fall back to the gRPC code.
3. Never parse `message`.

**Catalog invariants:**
- A reason is never renamed, reused, or moved to a different gRPC code. That would break partners' retry logic.
- Adding a reason is non-breaking. Metadata keys can be added but not removed.
- Retiring a reason means marking it deprecated in the docs and keeping it in the catalog.

## 3. Choosing the gRPC code

Walk these questions in order.

1. Is the caller unidentified or the credential bad? → `UNAUTHENTICATED`.
2. Is the caller identified but not allowed? → `PERMISSION_DENIED`.
3. Does the resource belong to another partner? → `NOT_FOUND`, never `PERMISSION_DENIED`. This stops partners from probing each other's IDs.
4. Is the request wrong regardless of system state? → `INVALID_ARGUMENT`.
5. Is the request fine, but the system state forbids it? → `FAILED_PRECONDITION`. The caller must change something first.
6. Would waiting alone fix it (rate, quota, daily limit)? → `RESOURCE_EXHAUSTED`, with `RetryInfo`.
7. Did a concurrent writer win? → `ABORTED`. The caller re-reads and retries.
8. Is it the server's fault and transient? → `UNAVAILABLE`.
9. Is it the server's fault and a bug? → `INTERNAL`.

**Rule of thumb:** waiting fixes it → `RESOURCE_EXHAUSTED`. A person or a state change fixes it → `FAILED_PRECONDITION`.

## 4. The catalog

The "Retry" column means:
- **no**: don't retry as-is.
- **fix**: change the request or state, then retry.
- **backoff**: retry with exponential backoff and jitter.
- **reread**: re-fetch the resource, then retry.
- **reconcile**: the outcome is ambiguous, so check state or retry with the same idempotency key.

### Authentication (`UNAUTHENTICATED`)

| Reason | Retry | Meaning | Metadata |
|---|---|---|---|
| `CREDENTIALS_MISSING` | fix | No token or client certificate presented. | |
| `CREDENTIALS_INVALID` | fix | Malformed, unknown or bad signature. | |
| `CREDENTIALS_EXPIRED` | fix | Refresh and retry. | `expiredAt` |
| `CLIENT_CERTIFICATE_INVALID` | fix | mTLS identity not trusted or revoked. | |

### Authorization (`PERMISSION_DENIED`)

| Reason | Retry | Meaning | Metadata |
|---|---|---|---|
| `SCOPE_INSUFFICIENT` | fix | The credential lacks the scope for this method. | `requiredScope` |
| `SERVICE_NOT_ENABLED` | fix | The partner has not been provisioned for this service. | `service` |
| `PARTNER_SUSPENDED` | no | The partner account is suspended. Contact support. | |
| `IP_NOT_ALLOWLISTED` | fix | The source address is not on the partner's allowlist. | |
| `ENVIRONMENT_MISMATCH` | fix | Sandbox credential used in production, or the reverse. | `credentialEnvironment` |

### Validation (`INVALID_ARGUMENT`)

| Reason | Retry | Meaning | Metadata |
|---|---|---|---|
| `REQUEST_INVALID` | fix | Generic validation failure. `BadRequest` lists every offending field. | |
| `AMOUNT_INVALID` | fix | Zero, negative, or wrong precision for the currency. | `currency` |
| `AMOUNT_OUT_OF_BOUNDS` | fix | Outside the product's absolute minimum or maximum. | `min`, `max`, `currency` |
| `CURRENCY_UNSUPPORTED` | fix | Unknown or disabled currency code. | `currency` |
| `ACCOUNT_IDENTIFIER_INVALID` | fix | IBAN, routing number or account number fails format or checksum. | `identifierType` |
| `PAGE_TOKEN_INVALID` | fix | Malformed or tampered token. Restart pagination. | |
| `IDEMPOTENCY_KEY_INVALID` | fix | Missing on a mutating call, or malformed. | |
| `IDEMPOTENCY_KEY_PAYLOAD_MISMATCH` | fix | Same key, different request body. Use a new key. | |

`PAGE_TOKEN_INVALID` also covers expired tokens. Tokens are opaque, so the client can't tell the difference and shouldn't have to.

### Resources (`NOT_FOUND`, `ALREADY_EXISTS`)

| Reason | gRPC code | Retry | Meaning | Metadata |
|---|---|---|---|---|
| `RESOURCE_MISSING` | `NOT_FOUND` | no | The resource doesn't exist, or belongs to another partner. Never distinguish the two. | `resourceType` |
| `RESOURCE_ALREADY_EXISTS` | `ALREADY_EXISTS` | no | A natural-key collision, such as an external reference. | `resourceType` |

### State and business rules (`FAILED_PRECONDITION`)

| Reason | Retry | Meaning | Metadata |
|---|---|---|---|
| `RESOURCE_STATE_INVALID` | fix | Generic "wrong state for this operation". Prefer a specific reason below. | `resourceType`, `currentState` |
| `ACCOUNT_CLOSED` | no | Terminal state. | |
| `ACCOUNT_FROZEN` | no | Frozen by the partner or by Ledgerline. | |
| `ACCOUNT_VERIFICATION_REQUIRED` | fix | KYC or KYB is incomplete. | `verificationStatus` |
| `INSUFFICIENT_FUNDS` | fix | The available balance doesn't cover the debit. | `currency` |
| `CURRENCY_MISMATCH` | fix | Source and destination currencies differ and no FX was requested. | `sourceCurrency`, `destinationCurrency` |
| `TRANSACTION_LIMIT_EXCEEDED` | fix | The per-transaction cap is exceeded. A limit increase needs a human. | `limit`, `currency` |
| `TRANSFER_ALREADY_SETTLED` | no | Can't cancel after settlement. | |
| `TRANSFER_ALREADY_REVERSED` | no | A second reversal was attempted. | |
| `TRANSFER_NOT_REVERSIBLE` | no | Outside the reversal window, or the rail doesn't allow reversal. | `rail` |
| `COMPLIANCE_REJECTED` | no | Blocked by a compliance control. **Deliberately opaque.** | |

**Compliance rejections must not name the control.** Sanctions and AML tipping-off rules in many jurisdictions forbid revealing why a transaction was blocked. Use one reason, no metadata, and a fixed message. Confirm the exact wording with your compliance counsel before publishing.

### Concurrency (`ABORTED`)

| Reason | Retry | Meaning | Metadata |
|---|---|---|---|
| `CONCURRENT_MODIFICATION` | reread | An etag or version mismatch. | `resourceType` |
| `IDEMPOTENT_REQUEST_IN_PROGRESS` | backoff | The original request with this key is still running. | |
| `TRANSACTION_CONFLICT` | backoff | A serialization failure in the ledger. Safe to retry, because no state changed. | |

### Throttling (`RESOURCE_EXHAUSTED`)

All of these carry `RetryInfo`. Clients must honor `retry_delay`.

| Reason | Retry | Meaning | Metadata |
|---|---|---|---|
| `RATE_LIMIT_EXCEEDED` | backoff | Per-partner request rate. | `limitName` |
| `QUOTA_EXCEEDED` | backoff | A longer-window quota. `QuotaFailure` is attached. | `quotaName` |
| `DAILY_LIMIT_EXCEEDED` | backoff | A daily volume or velocity limit. Resets at a known time. | `limit`, `currency`, `resetAt` |
| `CONCURRENT_STREAMS_EXCEEDED` | backoff | Too many open streams. | `limit` |

### Range (`OUT_OF_RANGE`)

| Reason | Retry | Meaning | Metadata |
|---|---|---|---|
| `DATE_RANGE_OUT_OF_RETENTION` | fix | The query reaches past data retention. | `earliestAvailable` |

### Availability and server faults

| Reason | gRPC code | Retry | Meaning | Metadata |
|---|---|---|---|---|
| `SERVICE_UNAVAILABLE` | `UNAVAILABLE` | backoff | Transient. Safe to retry. | |
| `MAINTENANCE_IN_PROGRESS` | `UNAVAILABLE` | backoff | A scheduled window. `RetryInfo` is attached. | `endsAt` |
| `RAIL_UNAVAILABLE` | `UNAVAILABLE` | backoff | The downstream payment rail is down. No vendor names. | `rail` |
| `UPSTREAM_TIMEOUT` | `DEADLINE_EXCEEDED` | reconcile | A downstream call timed out and the **outcome is unknown**. | `rail` |
| `REQUEST_CANCELLED` | `CANCELLED` | reconcile | The client cancelled. State may have changed. | |
| `METHOD_NOT_IMPLEMENTED` | `UNIMPLEMENTED` | no | The method doesn't exist in this API version. | |
| `INTERNAL_ERROR` | `INTERNAL` | backoff | A bug on our side. Retry at most a few times. It is auto-reported with the `request_id`. | |
| `DATA_INTEGRITY_FAULT` | `DATA_LOSS` | no | A ledger invariant was violated. **Pages on-call.** Reserved. | |

The `UPSTREAM_TIMEOUT` and `REQUEST_CANCELLED` entries matter most for money movement.

- The client must never treat them as failure.
- Retry with the same idempotency key, or call `Get*`.
- Document this prominently on the docs site.

**Count:** 47 reasons across 11 gRPC codes. Codes I deliberately didn't use for application errors: `UNKNOWN` (banned), `OK`.

## 5. Single source of truth

Define the catalog once in protobuf and generate everything else from it.

```proto
// ledgerline/error/v1/reason.proto
extend google.protobuf.EnumValueOptions { ErrorSpec error_spec = 50001; }

message ErrorSpec {
  google.rpc.Code grpc_code = 1;
  Retry retry = 2;                 // NO, FIX, BACKOFF, REREAD, RECONCILE
  repeated string metadata_keys = 3;
  string summary = 4;              // feeds the docs site
  string client_action = 5;
}

enum ErrorReason {
  ERROR_REASON_UNSPECIFIED = 0;
  INSUFFICIENT_FUNDS = 12 [(error_spec) = {
    grpc_code: FAILED_PRECONDITION, retry: FIX, metadata_keys: ["currency"],
    summary: "Available balance does not cover the debit.",
    client_action: "Top up the account or reduce the amount."
  }];
}
```

- **On the wire:** `ErrorInfo.reason` carries the enum value's name as a string. Partners never need the proto, and unknown values can't break their decoding.
- **Server:** one unary and stream interceptor turns typed domain errors into `Status` plus details. Handlers never build a `Status` by hand.
- **Gates:** run these in CI.
  - A lint rejects any handler path that returns a bare `error` or `codes.Unknown`.
  - A test checks that each reason's `grpc_code` never changes between commits. Diff the generated catalog against `main`.
  - A metadata-key check fails when a handler omits a declared key.
- **Observability:** label error metrics by `reason` and gRPC code. Alert on any `UNKNOWN` in production, because it means a handler skipped the interceptor.
- **Docs site:** generate one page per reason from `ErrorSpec` (summary, gRPC code, retry, metadata, client action, example `Status` as text-proto). Add a summary table at the top, grouped by gRPC code. Grouping lives in docs only, not in the reason names.

## 6. Partner-side usage

```go
st, _ := status.FromError(err)
for _, d := range st.Details() {
    if info, ok := d.(*errdetails.ErrorInfo); ok && info.Domain == "api.ledgerline.com" {
        switch info.Reason {
        case "INSUFFICIENT_FUNDS": // ...
        default:                   // unknown reason: fall back to st.Code()
        }
    }
}
```

Publish this snippet in the docs for Go, Java and Python, since your partners will mostly use generated gRPC clients.

## 7. Rollout

1. Ship the proto, interceptor and lint with the 12 services mapped incrementally. Start with the three highest-traffic services.
2. Keep the old prose string during a deprecation window. Add a response header or docs note that the prose is going away.
3. Announce to the 40 partners with the docs site and a one-page migration note: "switch on `reason`, fall back to the code".
4. Flip the CI gate from warn to fail once every service is migrated.

## Decisions to confirm

- **Compliance wording:** does counsel approve a single opaque `COMPLIANCE_REJECTED`? Do some partners have a contractual right to a reason?
- **Idempotency:** do all 12 services honor an idempotency key today? If not, `IDEMPOTENCY_KEY_INVALID` can't be required yet. Make it required per service as each one adopts it.
- **Localized messages:** do partners need localized `message` text? If so, add `LocalizedMessage`. I'd skip it for v1.
- **Daily limits:** do you prefer `DAILY_LIMIT_EXCEEDED` as `RESOURCE_EXHAUSTED` (my pick, since waiting fixes it) or as `FAILED_PRECONDITION`? Either works, but pick one before publishing, because it can't change afterward.