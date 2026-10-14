# Rondelet Public API: gRPC Design

## 0. Read this first: the browser constraint

You decided on gRPC for the public surface, and this design keeps that. One requirement in your brief needs a design response, though. **Browsers cannot speak native gRPC.** `fetch` and XHR give JS no control over HTTP/2 framing or trailers. Your React partners therefore can't call a plain gRPC listener directly.

So the public surface is **one proto contract served over three wire formats**:

| Wire | Who uses it | How it's served |
|---|---|---|
| Native gRPC (HTTP/2) | Go, Java, Kotlin, Python, C# server-side partners | Envoy passthrough |
| gRPC-Web (or Connect) | React dashboards, any browser | Envoy `grpc_web` filter |
| JSON over HTTP (`POST /v1/payments`) | PHP, Ruby, no-code, curl, anyone without a gRPC toolchain | Envoy `grpc_json_transcoder`, driven by `google.api.http` annotations |

- The protos stay the single source of truth.
- Native gRPC stays first-class.
- The JSON path costs one annotation per method and removes the biggest adoption risk with 200 mixed-stack engineers.
- The speed argument matters less for third parties than for your mesh. Their latency is dominated by the internet and by integration effort, not by payload encoding.
- gRPC-Web alone is the minimum to satisfy the React requirement. I recommend the JSON path as well.
- If you'd rather not run Envoy transcoding, use Connect (`connect-go`). One handler then serves gRPC, gRPC-Web, and Connect's JSON-over-POST.

Two more things the brief doesn't cover but a payments API needs regardless of wire format:
- **Webhooks.** Partners' servers sit behind firewalls and mixed stacks. Async events can't be gRPC server streams. See §8.
- **Browser credentials.** A merchant dashboard in React must never hold a secret key. See §7.

---

## 1. Core decisions

1. **Public protos are a separate contract from internal protos.** Never expose the 40 internal services through the edge. Build a thin **public facade** (`public-api`, a Go service) that implements the public services and calls internal gRPC. This lets internal protos change daily while the public API stays frozen.
2. **Version by package** (`rondelet.payment.v1`). Breaking changes go to `v2` alongside `v1`. Previews go in `v1beta1`.
3. **Unary only in v1.** No client or bidi streaming. Server streaming doesn't work through gRPC-Web in all cases, and webhooks cover async needs.
4. **A declined payment is not an RPC error.** `CreatePayment` returns OK with `status = FAILED` and a `decline_code`. gRPC errors are reserved for API faults: invalid argument, auth, rate limit, internal.
5. **Idempotency is mandatory on every mutating call.**
6. **Style follows Google AIP** (`Get`, `List`, `Create`, `Update` with field masks, custom verbs like `Capture`). It is well documented and `buf` lint understands it.

---

## 2. Edge architecture

```
Partner (gRPC / gRPC-Web / JSON)
        │ TLS 1.2+, HTTP/2 (+ HTTP/1.1 for grpc-web and JSON)
        ▼
 api.rondelet.com  ── Envoy (dedicated public edge, not the internal mesh)
   • CORS (allowlist per publishable key / registered origin)
   • authn: API key / JWT validation (ext_authz) → scopes, account id
   • rate limit (global ratelimit service; descriptor = key id + method class)
   • grpc_web filter
   • grpc_json_transcoder (proto descriptor set built from public module only)
   • request size caps, deadline cap (30s), header allowlist
        ▼
 public-api (facade, implements rondelet.*.v1 services)
        ▼
 internal mesh (internal protos, mTLS, existing Envoy)

 vault.rondelet.com  ── separate host/cluster, tokenization only (PCI scope isolation)
 sandbox.api.rondelet.com ── same stack, test-mode data, test keys
```

Rules:
- **Descriptor set for transcoding is built only from the public buf module.** Internal services must be unreachable by construction.
- **Disable gRPC server reflection in production.** Publish protos instead (§9). Enable reflection in sandbox only.
- **Cap client deadlines at the edge.** Honor `grpc-timeout`, but never above the cap.
- **Known transcoder gotcha:** proto3 JSON encodes `int64` as a **string**. `Money.amount_minor` therefore appears as `"1999"` in JSON. Document it, show it in every example, and keep `int64`: `int32` overflows for large JPY or similar-currency amounts.

---

## 3. Repo and package layout

Two buf modules in the monorepo. Public can't import internal.

```
proto/
  buf.work.yaml
  internal/                      # existing, untouched
    buf.yaml
    ...
  public/
    buf.yaml                     # name: buf.build/rondelet/api
    buf.gen.yaml
    rondelet/
      common/v1/
        money.proto              # Money
        pagination.proto         # (conventions only; fields are inline per AIP)
        errors.proto             # PaymentError, ErrorCode details
        types.proto              # Address, Metadata helpers, DateRange
      options/v1/
        access.proto             # custom method options: scopes, browser_allowed
      auth/v1/
        api_key_service.proto
        client_session_service.proto
      account/v1/
        account_service.proto
      customer/v1/
        customer_service.proto
      paymentmethod/v1/
        payment_method_service.proto
        payment_method.proto
      payment/v1/
        payment_service.proto
        payment.proto
        refund_service.proto
        refund.proto
      payout/v1/
        payout_service.proto
        balance_service.proto
      dispute/v1/
        dispute_service.proto
        dispute.proto
      ledger/v1/
        transaction_service.proto   # read-only
      webhook/v1/
        webhook_endpoint_service.proto
        event_service.proto
        event.proto                 # Event envelope + oneof of payloads
      vault/v1/
        tokenization_service.proto  # served only on vault.rondelet.com
    docs/                           # OpenAPI output, examples (generated)
```

Conventions for the layout:
- Directory = package = `rondelet.<domain>.v1`.
- One service per file, named `<resource>_service.proto`. Resource messages go in their own file.
- `go_package`, `java_package`, `csharp_namespace`, and similar options are set via buf managed mode, not by hand.

---

## 4. Conventions (apply to every method)

**Identifiers.** Opaque, prefixed strings: `pay_`, `ref_`, `cus_`, `acct_`, `pm_`, `po_`, `dp_`, `evt_`, `we_`. No integer IDs.

**Money.**
```proto
message Money {
  // Smallest currency unit (cents for USD, yen for JPY). JSON: string.
  int64 amount_minor = 1;
  // ISO 4217 alpha-3, uppercase.
  string currency = 2;
}
```

**Idempotency.** Header `Idempotency-Key` (gRPC metadata `idempotency-key`) on every mutating call. A header works identically across all three wires and doesn't pollute messages.
- Keys are retained 24h.
- Same key with the same payload returns the original response.
- Same key with a different payload returns `ABORTED` with `IDEMPOTENCY_KEY_REUSED` in `ErrorInfo`.

**Acting on behalf of a merchant.** Platform partners send `Rondelet-Account: acct_...` as metadata. It is never in the URL path, so paths stay stable.

**Pagination.** `page_size` (max 100, default 25) and opaque `page_token` in; `next_page_token` out. List filters are typed request fields, not a free-form string, in v1.

**Updates.** `PATCH` semantics with `google.protobuf.FieldMask update_mask`. Only explicitly listed mutable fields are allowed.

**Enums.** Every enum has `X_UNSPECIFIED = 0`. Clients must tolerate unknown values, and this is stated in the docs. New values are non-breaking.

**Field presence.** `optional` for scalars where "unset" differs from zero. Annotate with `google.api.field_behavior` (`REQUIRED`, `OUTPUT_ONLY`, `IMMUTABLE`).

**Field numbers.** Never reuse. Always `reserved` a removed field's number and name. This matters more here because JSON clients depend on names.

**Timestamps.** `google.protobuf.Timestamp` everywhere. No epoch ints.

**Metadata.** `map<string,string> metadata` on payments, customers, refunds (max 50 keys, 500 chars per value).

**Errors.** `google.rpc.Status` with these details:
- `ErrorInfo` (`reason` = stable machine code, `domain` = `rondelet.com`)
- `BadRequest` (field violations)
- `RetryInfo` (on rate limit and overload)
- `rondelet.common.v1.RequestInfo` (`request_id`, always also returned as response header `rondelet-request-id`)

| Situation | gRPC code | HTTP |
|---|---|---|
| Malformed or invalid field | `INVALID_ARGUMENT` | 400 |
| Missing or invalid credentials | `UNAUTHENTICATED` | 401 |
| Valid credentials, insufficient scope | `PERMISSION_DENIED` | 403 |
| Unknown resource | `NOT_FOUND` | 404 |
| Idempotency conflict, concurrent mutation | `ABORTED` | 409 |
| Illegal state (e.g. capture a voided payment) | `FAILED_PRECONDITION` | 412/422 |
| Rate limited | `RESOURCE_EXHAUSTED` + `RetryInfo` | 429 |
| Backend unavailable | `UNAVAILABLE` + `RetryInfo` | 503 |
| Deadline exceeded | `DEADLINE_EXCEEDED` | 504 |

Never use `UNKNOWN` for known conditions. Never leak internal error text.

---

## 5. Services

I assumed a standard payments-processor domain. **Correct this list if your product differs** (see §11).

| Package | Service | Methods (v1) | Browser OK? |
|---|---|---|---|
| `auth.v1` | `ApiKeyService` | Create, Get, List, Roll, Revoke | No |
| `auth.v1` | `ClientSessionService` | CreateClientSession (mint short-lived browser token) | No (server-side only) |
| `account.v1` | `AccountService` | Create, Get, Update, List (connected merchant accounts) | Get only |
| `customer.v1` | `CustomerService` | Create, Get, Update, Delete (soft), List | Read |
| `paymentmethod.v1` | `PaymentMethodService` | Get, List, Attach, Detach | Read |
| `vault.v1` | `TokenizationService` | CreateCardToken, CreateBankToken | Yes, publishable key only |
| `payment.v1` | `PaymentService` | Create, Get, List, Update (metadata), Confirm, Capture, Cancel | Read |
| `payment.v1` | `RefundService` | Create, Get, List | Read |
| `payout.v1` | `PayoutService` | Create, Get, List, Cancel | Read |
| `payout.v1` | `BalanceService` | GetBalance | Read |
| `dispute.v1` | `DisputeService` | Get, List, SubmitEvidence, Accept | Read |
| `ledger.v1` | `TransactionService` | Get, List (settled balance movements; reconciliation) | Read |
| `webhook.v1` | `WebhookEndpointService` | Create, Get, Update, Delete, List, RotateSecret | No |
| `webhook.v1` | `EventService` | Get, List, Resend | Read |

About 14 services and ~55 methods. That is enough for launch. **Cut anything not needed by day one**: you can add methods to `v1` later, but you can never remove them.

### Access control as a proto option

Every method declares its scopes and whether browsers may call it. The edge enforces this from the descriptor, so there is no per-service auth code.

```proto
// rondelet/options/v1/access.proto
syntax = "proto3";
package rondelet.options.v1;
import "google/protobuf/descriptor.proto";

message Access {
  repeated string scopes = 1;          // e.g. "payments:read"
  bool browser_allowed = 2;            // false = rejected if caller used a client-session token
  RateClass rate_class = 3;
  bool idempotent_required = 4;        // edge rejects calls missing Idempotency-Key
}
enum RateClass {
  RATE_CLASS_UNSPECIFIED = 0;
  RATE_CLASS_READ = 1;
  RATE_CLASS_WRITE = 2;
  RATE_CLASS_HEAVY = 3;                // list-with-big-range, exports
}
extend google.protobuf.MethodOptions { Access access = 50100; }
```

---

## 6. Proto sketches

### PaymentService

```proto
syntax = "proto3";
package rondelet.payment.v1;

import "google/api/annotations.proto";
import "google/api/field_behavior.proto";
import "google/protobuf/field_mask.proto";
import "google/protobuf/timestamp.proto";
import "rondelet/common/v1/money.proto";
import "rondelet/options/v1/access.proto";

service PaymentService {
  rpc CreatePayment(CreatePaymentRequest) returns (Payment) {
    option (google.api.http) = { post: "/v1/payments" body: "*" };
    option (rondelet.options.v1.access) = {
      scopes: ["payments:write"] rate_class: RATE_CLASS_WRITE idempotent_required: true
    };
  }
  rpc GetPayment(GetPaymentRequest) returns (Payment) {
    option (google.api.http) = { get: "/v1/payments/{payment_id}" };
    option (rondelet.options.v1.access) = {
      scopes: ["payments:read"] browser_allowed: true rate_class: RATE_CLASS_READ
    };
  }
  rpc ListPayments(ListPaymentsRequest) returns (ListPaymentsResponse) {
    option (google.api.http) = { get: "/v1/payments" };
    option (rondelet.options.v1.access) = {
      scopes: ["payments:read"] browser_allowed: true rate_class: RATE_CLASS_READ
    };
  }
  rpc UpdatePayment(UpdatePaymentRequest) returns (Payment) {
    option (google.api.http) = { patch: "/v1/payments/{payment_id}" body: "payment" };
    option (rondelet.options.v1.access) = { scopes: ["payments:write"] rate_class: RATE_CLASS_WRITE idempotent_required: true };
  }
  rpc ConfirmPayment(ConfirmPaymentRequest) returns (Payment) {
    option (google.api.http) = { post: "/v1/payments/{payment_id}:confirm" body: "*" };
    option (rondelet.options.v1.access) = { scopes: ["payments:write"] rate_class: RATE_CLASS_WRITE idempotent_required: true };
  }
  rpc CapturePayment(CapturePaymentRequest) returns (Payment) {
    option (google.api.http) = { post: "/v1/payments/{payment_id}:capture" body: "*" };
    option (rondelet.options.v1.access) = { scopes: ["payments:write"] rate_class: RATE_CLASS_WRITE idempotent_required: true };
  }
  rpc CancelPayment(CancelPaymentRequest) returns (Payment) {
    option (google.api.http) = { post: "/v1/payments/{payment_id}:cancel" body: "*" };
    option (rondelet.options.v1.access) = { scopes: ["payments:write"] rate_class: RATE_CLASS_WRITE idempotent_required: true };
  }
}

message Payment {
  string id = 1 [(google.api.field_behavior) = OUTPUT_ONLY];       // pay_...
  PaymentStatus status = 2 [(google.api.field_behavior) = OUTPUT_ONLY];
  rondelet.common.v1.Money amount = 3;
  rondelet.common.v1.Money amount_captured = 4 [(google.api.field_behavior) = OUTPUT_ONLY];
  rondelet.common.v1.Money amount_refunded = 5 [(google.api.field_behavior) = OUTPUT_ONLY];
  string customer_id = 6;                // nullable: empty = none
  string payment_method_id = 7;
  CaptureMethod capture_method = 8;
  string description = 9;
  map<string, string> metadata = 10;
  // Set when status == PAYMENT_STATUS_FAILED. A decline is a normal outcome, not an RPC error.
  Decline decline = 11 [(google.api.field_behavior) = OUTPUT_ONLY];
  // Set when status == PAYMENT_STATUS_REQUIRES_ACTION (e.g. 3-D Secure).
  NextAction next_action = 12 [(google.api.field_behavior) = OUTPUT_ONLY];
  google.protobuf.Timestamp create_time = 13 [(google.api.field_behavior) = OUTPUT_ONLY];
  google.protobuf.Timestamp update_time = 14 [(google.api.field_behavior) = OUTPUT_ONLY];
  reserved 15 to 29;                     // headroom for lifecycle fields
}

enum PaymentStatus {
  PAYMENT_STATUS_UNSPECIFIED = 0;
  PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD = 1;
  PAYMENT_STATUS_REQUIRES_CONFIRMATION = 2;
  PAYMENT_STATUS_REQUIRES_ACTION = 3;
  PAYMENT_STATUS_PROCESSING = 4;
  PAYMENT_STATUS_AUTHORIZED = 5;
  PAYMENT_STATUS_SUCCEEDED = 6;
  PAYMENT_STATUS_FAILED = 7;
  PAYMENT_STATUS_CANCELED = 8;
}

enum CaptureMethod {
  CAPTURE_METHOD_UNSPECIFIED = 0;   // server default: AUTOMATIC
  CAPTURE_METHOD_AUTOMATIC = 1;
  CAPTURE_METHOD_MANUAL = 2;
}

message Decline {
  // Stable, documented, additive enum. Not free text.
  DeclineCode code = 1;
  string message = 2;               // human-readable, not for branching
  bool retryable = 3;
}

message CreatePaymentRequest {
  rondelet.common.v1.Money amount = 1 [(google.api.field_behavior) = REQUIRED];
  string customer_id = 2;
  string payment_method_id = 3;
  CaptureMethod capture_method = 4;
  bool confirm = 5;                 // create + confirm in one call
  string description = 6;
  map<string, string> metadata = 7;
}

message GetPaymentRequest { string payment_id = 1 [(google.api.field_behavior) = REQUIRED]; }

message ListPaymentsRequest {
  int32 page_size = 1;
  string page_token = 2;
  string customer_id = 3;
  repeated PaymentStatus statuses = 4;
  google.protobuf.Timestamp created_after = 5;
  google.protobuf.Timestamp created_before = 6;
}
message ListPaymentsResponse {
  repeated Payment payments = 1;
  string next_page_token = 2;
}

message UpdatePaymentRequest {
  string payment_id = 1 [(google.api.field_behavior) = REQUIRED];
  Payment payment = 2;
  google.protobuf.FieldMask update_mask = 3;   // only description, metadata are mutable
}
message ConfirmPaymentRequest { string payment_id = 1; string payment_method_id = 2; string return_url = 3; }
message CapturePaymentRequest { string payment_id = 1; rondelet.common.v1.Money amount_to_capture = 2; } // unset = full
message CancelPaymentRequest  { string payment_id = 1; string reason = 2; }
```

(`DeclineCode` and `NextAction` live in `payment.proto`. They are omitted for length.)

### ClientSessionService (the answer to "React talks to us directly")

```proto
service ClientSessionService {
  // Called by the PARTNER'S BACKEND with a secret key.
  // Returns a short-lived bearer token safe to hand to a browser.
  rpc CreateClientSession(CreateClientSessionRequest) returns (ClientSession) {
    option (google.api.http) = { post: "/v1/client-sessions" body: "*" };
    option (rondelet.options.v1.access) = { scopes: ["client_sessions:write"] idempotent_required: false };
  }
}
message CreateClientSessionRequest {
  string account_id = 1 [(google.api.field_behavior) = REQUIRED];  // merchant the dashboard is for
  repeated string scopes = 2;               // must be subset of browser_allowed read scopes
  int32 ttl_seconds = 3;                    // max 900
  repeated string allowed_origins = 4;      // bound into token; edge checks Origin
  string customer_id = 5;                   // optional: restrict to one customer's data
}
message ClientSession {
  string token = 1;                         // opaque or JWT; Bearer
  google.protobuf.Timestamp expire_time = 2;
  repeated string scopes = 3;
}
```

---

## 7. Authentication and authorization

| Credential | Lives where | Can do |
|---|---|---|
| **Secret key** (`sk_live_…`, `sk_test_…`) | Partner servers only | Everything its scopes allow; calls `CreateClientSession` |
| **Publishable key** (`pk_live_…`, `pk_test_…`) | Browser / mobile, public | Only `vault.v1.TokenizationService`. Cannot read anything. Origin-restricted |
| **Client-session token** | Browser, minted per user session | Read-only scopes marked `browser_allowed`; bound to one account, ≤15 min, origin-bound |
| **OAuth2 client credentials** (phase 2) | Platform partners' servers | Acts for connected merchants via `Rondelet-Account` |
| **mTLS + key** (optional) | Large partners | Extra layer, not a replacement |

Rules:
- **Key format is a typed prefix + random** (`sk_live_`), so secret scanners catch leaks. Register the prefix with GitHub secret scanning.
- **Keys are stored hashed.** Rolling a key supports an overlap window.
- **Auth runs in Envoy `ext_authz`**, using the `access` option in the descriptor. A client-session token hitting a method without `browser_allowed` gets `PERMISSION_DENIED`.
- **CORS is enforced per key or session origin allowlist**, never `*`.
- **Raw card data never touches `api.rondelet.com`.** Card and bank entry goes to `vault.rondelet.com` (a separate cluster) with a publishable key. It returns a token that `PaymentService` accepts. This keeps your PCI scope narrow and gives partners a hosted-field-style path.
- **Rate limits** per key and rate class, with defaults in sandbox. Returned as `RESOURCE_EXHAUSTED` + `RetryInfo`, with `ratelimit-*` response headers.

---

## 8. Webhooks (mandatory, not optional)

```proto
message Event {
  string id = 1;                       // evt_...
  string account_id = 2;
  google.protobuf.Timestamp create_time = 3;
  string api_version = 4;              // "v1"
  oneof data {
    PaymentEvent payment = 10;         // payment.succeeded, payment.failed, payment.requires_action, ...
    RefundEvent refund = 11;
    PayoutEvent payout = 12;
    DisputeEvent dispute = 13;
  }
}
```

- **Delivery:** HTTPS POST of the proto-JSON `Event`.
- **Signature:** `Rondelet-Signature: t=<unix>,v1=<hmac_sha256(secret, t + "." + body)>`. Reject timestamps older than 5 minutes. SDKs ship the verifier.
- **Retries:** exponential backoff for 72h. Events are at-least-once and unordered, so receivers dedupe on `evt_` id.
- **Replay:** `EventService.List` and `Resend` let partners recover after downtime. Events are retained 30 days.
- **Thin vs. fat payloads:** start with the full object snapshot. Recommend partners re-`Get` for authoritative state.

Browsers that need live updates poll `GetPayment` in v1. No public streaming yet.

---

## 9. Governance, tooling, and lifecycle

**Buf configuration (public module):**
- `lint: STANDARD` plus `RPC_REQUEST_STANDARD_NAME` and `RPC_RESPONSE_STANDARD_NAME`.
- `breaking: use: [FILE]` on PRs against `main`. `FILE` is stricter than wire-compat on purpose, because generated SDK source compatibility is part of the contract. The floor is `WIRE_JSON`, since transcoded JSON clients depend on field names.
- Custom lint (ast-grep or buf plugin):
  - every method has an `access` option
  - every mutating method sets `idempotent_required`
  - every enum has `_UNSPECIFIED = 0`
  - no `int32` money fields
  - no `float` or `double` money fields

**Ownership.** CODEOWNERS on `proto/public/**` points to an API review group of 2–3 people. Every public proto change needs their approval. This is the one place where friction is the feature.

**Distribution.**
- Publish `buf.build/rondelet/api` (BSR) on release tags. Partners then get generated SDKs in any language without cloning your repo.
- Generate OpenAPI v2/v3 from the same protos and publish interactive docs. This is what the JSON-only partners will actually read.
- Official SDKs for TypeScript (`protobuf-es` + `connect-es`, which also does gRPC-Web), Go, Java, and Python. Each is a thin hand-written layer over generated stubs that adds auth, idempotency-key generation, retry and backoff on `UNAVAILABLE` only, and webhook verification. Others come later.

**Deprecation.**
- A `v1` major is supported at least 24 months after `v2` GA.
- Mark deprecated methods with `option deprecated = true`.
- Edge adds `Deprecation` and `Sunset` response headers.
- Per-key usage reporting by version, so you know who to chase.

**Sandbox.** Same facade, test-mode data, test cards for each `DeclineCode`, and a `sandbox`-only reflection endpoint. It is free to self-serve. Partners' first call should work in under 10 minutes.

---

## 10. Rollout

1. **Weeks 0–3: contract.** Finalize `common`, `payment`, `paymentmethod`, `vault`, `auth`, `webhook` protos. Stand up the edge Envoy with all three wires on sandbox. Run one React page and one curl script end to end.
2. **Weeks 3–6: facade and SDKs.** Implement `public-api` for those services. Publish the TS and Go SDKs and OpenAPI docs.
3. **Weeks 6–9: breadth.** Add refund, payout, balance, dispute, ledger, and customer. Run a closed beta with 10–15 of the 200 partners, deliberately including a React shop, a PHP or Ruby shop, and a Java shop.
4. **Weeks 9–12: GA prep.** Load test rate limits, run a pen test of the edge and `ClientSession` flow, and run the idempotency chaos test (retry storms). Then open to everyone.

---

## 11. Assumptions and open questions

Please confirm or correct these before I go deeper (full proto files, Envoy config, or `buf` setup):

1. **Domain scope.** I assumed card and bank acquiring, payouts, disputes, and a ledger. If you are infrastructure beneath PSPs (issuing, FX, BaaS accounts), the service list in §5 changes.
2. **Who calls from the browser?** I assumed the partner's end user is a merchant viewing their own data. If browsers also need to create payments, that is a separate, more constrained design.
3. **JSON transcoding.** I recommended it. If leadership wants gRPC-only, the minimum is gRPC-Web for React, and you should accept that PHP, Ruby, and no-code partners will struggle.
4. **Envoy transcoder or Connect?** Both work. Connect gives one binary for all three wires and cleaner JSON, but replaces your edge handler stack. Envoy keeps your current operations model.
5. **Multi-tenancy model.** Do partners act for many merchants (platform model, `Rondelet-Account`) or only their own account? This affects `AccountService` and OAuth in phase 2.
6. **Regulatory and PCI constraints.** SCA/3-D Secure, regional data residency, and PSD2 TPP obligations may force regional endpoints (`eu.api.rondelet.com`). Compliance needs to review the `vault` split.