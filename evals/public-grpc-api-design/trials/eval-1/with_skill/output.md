# Rondelet public API design

I read the skill and its three references. I couldn't ask its clarifying questions, so Assumptions below states what I assumed. Section 1 comes before any proto layout because it changes the design.

## 0. Assumptions

Flip a design decision if one of these is wrong:

| # | Assumption | If wrong |
|---|---|---|
| A1 | The 40 internal protos hold admin, debug, ops, risk and ledger RPCs that were never meant for outsiders. | If audited clean, the facade in §3 can shrink to a thin proxy. |
| A2 | Partners are mixed: some use your SDKs, some generate their own stubs, and the React dashboards are browser clients. | If they were all SDK-mediated, raw gRPC would be viable. |
| A3 | No public REST API exists today, so there is nothing to stay consistent with. | If one exists, mirror its resources and versioning. |
| A4 | Nothing at launch is genuinely streaming-shaped. Event push is covered by webhooks. | See §6. |
| A5 | You ship next quarter and Envoy is your mesh data plane. | This is what promotes the Envoy transcoder over Connect in §4. |

## 1. Gate verdict: gRPC inside, JSON outside

**Raw public gRPC is ruled out.** Browsers can't speak gRPC's HTTP/2 framing, and your merchant dashboards call you directly. Under the skill's own rule this deletes raw gRPC as the only surface.

The other two stated reasons don't change that:

- **"It's faster than REST."** The skill treats performance as a trigger only when it is the *measured* bottleneck and consumers can absorb the tooling cost. Partner payment calls are dominated by network and issuer latency, not serialization. Serialization benchmarks (3–11x smaller, 8–12x faster) are directional vendor numbers.
- **"We run gRPC already."** That is a fact about your inside. Your 200 outside engineers have never met your protos.

Square, Dropbox and Cloudflare keep gRPC internal and put a JSON-facing surface at the public edge. Temporal's public gRPC works because its audience is control-plane engineers who already use generated SDKs, and it dual-publishes HTTP anyway. A broad partner platform for payments is the opposite audience.

**What you keep:** the protobuf contract. Protos stay the single source of truth, and JSON is generated from them through `google.api.http` annotations. Performance-sensitive server partners can get Connect's binary mode later (§4, promotion condition).

## 2. Package layout and versioning

Publish a separate, curated public proto module. Do **not** publish your internal protos, and do not annotate them in place.

```
proto/
  buf.yaml                         # workspace, two modules
  internal/                        # existing 40 services, untouched, never published
  public/
    buf.yaml                       # module: buf.build/rondelet/api
    buf.lock
    rondelet/
      type/                        # shared value types (see note)
        money.proto                # package rondelet.type
        address.proto
      payments/v1/
        payment_intents.proto      # package rondelet.payments.v1
        refunds.proto
      merchants/v1/merchants.proto
      payouts/v1/payouts.proto
      balance/v1/balance.proto
      disputes/v1/disputes.proto
      webhooks/v1/webhook_endpoints.proto
      events/v1/events.proto
    # new products start in rondelet/<api>/v1beta1/
```

Rules from AIP-191/215/185, all enforced by buf lint (§5):

- One package per API, ending in a major version. The directory mirrors the package exactly.
- No version in filenames. Major version only: `v1`, never `v1.2`.
- `v1` means stable. New products ship as `v1beta1` and graduate to `v1`. Beta features never go inside a `v1` package.
- A `v2` must not import `v1`. Stable resources keep identical resource names across majors.
- Set `java_package`, `go_package` and the other per-language options on every file.
- Every RPC gets its own `<Method>Request` and `<Method>Response`. Never use a bare scalar or a shared message.
- Never reuse or renumber a tag. `reserved` every removed field. Every enum zero value is `_UNSPECIFIED`.

**Note on `rondelet.type`:** unversioned shared types are my addition. It follows the `google.type` pattern, and the skill doesn't cover it. Keep the package tiny (Money, Address, DateTime) and add-only. The FILE-level `buf breaking` gate protects it. Never put resource messages there.

## 3. Services to expose

The services are resource-oriented under `merchants/{merchant}`. Standard methods are preferred. Custom `:verb` methods are used only where a standard verb fails: state transitions on a payment.

| Package | Service | RPCs | HTTP (via annotations) |
|---|---|---|---|
| `payments.v1` | `PaymentIntentService` | Create, Get, List, Update (metadata only, `FieldMask`), `Confirm`, `Capture`, `Cancel` | `POST /v1/{parent=merchants/*}/paymentIntents`, `…/{name}:confirm`, etc. |
| `payments.v1` | `RefundService` | Create, Get, List | `/v1/{parent=merchants/*}/refunds` |
| `merchants.v1` | `MerchantService` | Get, List (connected merchants), Update | `/v1/{name=merchants/*}` |
| `payouts.v1` | `PayoutService` | Get, List | `/v1/{parent=merchants/*}/payouts` |
| `balance.v1` | `BalanceService` | `GetBalance` (singleton), `ListBalanceTransactions` | `/v1/{name=merchants/*/balance}` |
| `disputes.v1` | `DisputeService` | Get, List, `SubmitEvidence`, `Accept` | `…/disputes/*:submitEvidence` |
| `webhooks.v1` | `WebhookEndpointService` | Create, Get, List, Update, Delete, `RotateSecret` | `/v1/{parent=merchants/*}/webhookEndpoints` |
| `events.v1` | `EventService` | Get, List (replay and reconciliation) | `/v1/{parent=merchants/*}/events` |

Design calls (my judgment, not skill requirements):

- **No `Delete` on money resources.** Payments, refunds, payouts and disputes only change state.
- **A card decline is a resource outcome, not an RPC error.** `ConfirmPaymentIntent` returns a `PaymentIntent` with `state = FAILED` or `REQUIRES_ACTION` and a typed `last_error`. RPC errors are for request-level failures. This also sidesteps the HTTP-status collapse in §7.
- **Cross-resource links are resource names.** A refund's `payment_intent` field is `"merchants/m_1/paymentIntents/pi_9"`, never an embedded message (AIP-122).
- **Every mutating RPC carries `request_id`** (AIP-155 style) so retries are safe. Semantics, retention window and key-reuse behaviour belong to `api-idempotency-retry`, not this design.
- **Money is `rondelet.type.Money`:** `currency_code` plus `int64 units_minor`. Never a float.
- **Card data never crosses this API.** Only tokens do. Collection stays in your existing PCI-scoped vault or hosted fields.
- **Partner onboarding (`CreateMerchant`) is not in v1.** It needs a KYC and compliance review first. Put it in `v1beta1` when it is ready.
- **Add a thin facade.** The 8 public services above are implemented by a **public API facade** that calls internal gRPC. Envoy does not transcode straight onto internal services. The facade gives you a versioning decoupling layer and a per-merchant authorization choke point. The cost is one extra hop and code to write. It rests on A1, since I haven't read your protos.
- **Never exposed:** ledger internals, routing, risk and fraud scoring, reconciliation, ops, admin, debug, anything on the vault.

Sketch of one file (abridged):

```proto
syntax = "proto3";

package rondelet.payments.v1;

import "google/api/annotations.proto";
import "google/api/field_behavior.proto";
import "google/api/resource.proto";
import "google/protobuf/field_mask.proto";
import "google/protobuf/timestamp.proto";
import "rondelet/type/money.proto";

option go_package = "github.com/rondelet/api/gen/go/rondelet/payments/v1;paymentsv1";
option java_package = "com.rondelet.payments.v1";

service PaymentIntentService {
  rpc CreatePaymentIntent(CreatePaymentIntentRequest) returns (CreatePaymentIntentResponse) {
    option (google.api.http) = {
      post: "/v1/{parent=merchants/*}/paymentIntents"
      body: "payment_intent"
    };
  }
  rpc ConfirmPaymentIntent(ConfirmPaymentIntentRequest) returns (ConfirmPaymentIntentResponse) {
    option (google.api.http) = {
      post: "/v1/{name=merchants/*/paymentIntents/*}:confirm"
      body: "*"
    };
  }
  // GetPaymentIntent, ListPaymentIntents, UpdatePaymentIntent, Capture, Cancel ...
}

message PaymentIntent {
  option (google.api.resource) = {
    type: "api.rondelet.com/PaymentIntent"
    pattern: "merchants/{merchant}/paymentIntents/{payment_intent}"
  };
  string name = 1 [(google.api.field_behavior) = IMMUTABLE];
  rondelet.type.Money amount = 2 [(google.api.field_behavior) = REQUIRED];
  State state = 3 [(google.api.field_behavior) = OUTPUT_ONLY];
  map<string, string> metadata = 4;
  google.protobuf.Timestamp create_time = 5 [(google.api.field_behavior) = OUTPUT_ONLY];

  enum State {
    STATE_UNSPECIFIED = 0;
    REQUIRES_PAYMENT_METHOD = 1;
    REQUIRES_ACTION = 2;
    REQUIRES_CAPTURE = 3;
    SUCCEEDED = 4;
    FAILED = 5;
    CANCELED = 6;
  }
}

message CreatePaymentIntentRequest {
  string parent = 1 [(google.api.field_behavior) = REQUIRED];
  PaymentIntent payment_intent = 2 [(google.api.field_behavior) = REQUIRED];
  string request_id = 3 [(google.api.field_behavior) = REQUIRED];
}
message CreatePaymentIntentResponse { PaymentIntent payment_intent = 1; }
```

## 4. Edge architecture (the transcoding choice)

```
React / partner server ──HTTPS (TLS 1.2+)──► Envoy public listener
                                              ├─ JWT validation, per-method scopes, rate limit
                                              ├─ grpc_json_transcoder (descriptor = public module only)
                                              └─► Public API facade (gRPC)
                                                        └─ internal mesh, mTLS ─► ~40 services
```

**Pick: Envoy gRPC-JSON transcoder at launch.** The skill's default rung is Connect-RPC. I'm overriding it for these reasons:

- You already run Envoy as the mesh, which is the skill's explicit promotion condition ("you already operate this").
- You ship next quarter, and it adds no new runtime.
- It is descriptor-driven, with no generated glue code.
- React clients get plain REST/JSON they can call with `fetch`.

The override has one real cost: the contract will be shared for years, and the skill says that weighs error fidelity over this quarter's effort. Envoy only meets that bar if you configure it exactly as below.

Required Envoy settings (without them the error envelope breaks):

- `convert_grpc_status: true`.
- The descriptor set is built from the public module only: `buf build public -o public.binpb`.
- That descriptor must include `google/rpc/error_details.proto` and every detail type you emit. Missing detail types are dropped **silently**.
- CORS is configured for the dashboard origins. This is my addition and the skill doesn't cover it.
- Reflection is off on every public-facing listener.

**Flip to Connect-RPC when any of these happens:**

- You need live push to dashboards, because Connect gives native server streaming without a proxy.
- Partners ask for typed TypeScript clients without a REST generator.
- The Envoy descriptor sync becomes a recurring failure.

Because the protos are annotation-clean and AIP-shaped, the switch changes the edge, not the contract.

**Performance partners:** steer high-volume server integrators to a native gRPC or Connect binary endpoint later, as an opt-in beta. Don't open it at launch.

## 5. CI gates

```yaml
# public/buf.yaml
version: v2
modules:
  - path: .
    name: buf.build/rondelet/api
lint:
  use: [STANDARD, UNARY_RPC]   # STANDARD enforces PACKAGE_VERSION_SUFFIX, SERVICE_SUFFIX,
                               # RPC_REQUEST_STANDARD_NAME, RPC_REQUEST_RESPONSE_UNIQUE,
                               # ENUM_ZERO_VALUE_SUFFIX
breaking:
  use: [FILE]                  # strictest category, right for a public surface
```

Run these on every PR as hard gates:

1. `buf lint public`
2. `buf breaking public --against '.git#branch=main,subdir=public'`
3. **HTTP mapping diff.** `buf breaking` does not inspect `google.api.http`, so a URL, verb or body change can pass every proto gate. Generate an OpenAPI document from the annotations (`protoc-gen-openapiv2`, committed in the repo) and diff it with `oasdiff`, failing on breaking changes. Back that with a small contract test suite hitting the real Envoy route table.
4. **Cross-version tests.** Run old client against new server and new client against old server.
5. Move to Buf Schema Registry review once the surface grows. A breaking push then goes into an approve/reject queue with a paper trail.

Deprecation: `deprecated = true` plus an AIP-192 comment saying why and what replaces it. Alpha can vanish. Beta gets at least 180 days of deprecation. An in-place breaking change to stable is for security or regulatory necessity only. Notice windows are for `api-versioning-policy` to define.

## 6. Streaming: unary only at launch

- `UNARY_RPC` lint is on, so nobody adds a streaming method by accident.
- Event delivery for partners uses **webhooks** (`WebhookEndpointService`). `EventService.ListEvents` is the polling and replay fallback.
- Webhook deliveries need signed payloads (HMAC with the rotatable secret). They sit outside the gRPC contract but inside the product.
- If a streaming need appears later, add server-streaming only, through Connect. Record the decision, and do not add client or bidi streaming. Bidi has no HTTP mapping, so it would be invisible to the transcoded surface.
- Any streaming path needs L7 HTTP/2-aware balancing and keepalive pings below the balancer's idle timeout (60 s on AWS ALB, 350 s on NLB).

## 7. Error model

Use `google.rpc.Status`:

- **`code`:** the most specific canonical code. Never default to `UNKNOWN` or `INTERNAL`.
- **`message`:** developer-facing English only.
- **`details`:** `ErrorInfo` always, with `domain = "api.rondelet.com"` and a stable machine `reason` such as `AMOUNT_TOO_SMALL`. Add `BadRequest` for field violations. Add `RetryInfo` with `RESOURCE_EXHAUSTED` and `UNAVAILABLE`.

Proposals for your two payment-specific cases:

- A reused `request_id` with a different payload returns `INVALID_ARGUMENT` with reason `IDEMPOTENCY_KEY_REUSED`.
- A request already in flight with the same `request_id` returns `ABORTED`.

Rules for the edge:

- **`DebugInfo` must never leave.** Strip it from `details` in the facade or a response filter. Sanitizing `message` alone is not enough.
- **Don't derive HTTP statuses from the gRPC project's client-side table.** gRPC says servers must not use it. Use the Envoy mapping and test it.
- **Document that the HTTP status is lossy.** `INVALID_ARGUMENT`, `FAILED_PRECONDITION` and `OUT_OF_RANGE` all become 400, and `CANCELLED` becomes 499. The body envelope is the source of truth.

The JSON error shape, matching Google Cloud and Dapr, is `{"error":{"code":…,"status":"INVALID_ARGUMENT","details":[{"@type":"type.googleapis.com/google.rpc.ErrorInfo",…}]}}`.

The error taxonomy is for `api-error-design` to define. This design only fixes the gRPC mechanics.

## 8. External auth, TLS and exposure audit

1. **TLS everywhere on the public listener:** 1.2 minimum, 1.3 preferred. mTLS stays inside the mesh, because issuing client certificates to 200 outside shops is impractical.
2. **OAuth2 by caller type:**
   - Partner servers use Client Credentials.
   - Merchant users on dashboards use Authorization Code + PKCE. The React app never holds a client secret.
3. **Tokens:** signed JWT (RS256) with expiry, sent as `authorization: Bearer`, validated at Envoy. Use introspection with caching for revocation. Use an established identity provider rather than a hand-rolled issuer.
4. **Per-method scopes**, for example `payments.write`, `payments.read`, `payouts.read`, `webhooks.write`, `disputes.write`. A valid token is not enough. The token must be scoped for that RPC.
5. **Merchant-level authorization in the facade.** Every `merchants/{id}` in a request path must belong to the token's grant. This closes cross-merchant access (IDOR), the most likely serious bug on this surface.
6. **API keys** only identify the project for quota attribution and coarse gating. They never replace OAuth.
7. **Rate limits** return `RESOURCE_EXHAUSTED` (429) with `RetryInfo`.
8. **Exposure audit before launch:**
   - Reflection is off in production.
   - Enumerate every method reachable from the public listener and diff it against the 8-service allow-list in §3.
   - The Envoy route table is deny-by-default.
   - The public descriptor contains only `public/` protos.

## 9. Launch pass criteria

All four are binary. Iterate until each one passes:

- ✅ `buf breaking` (FILE) green on 100% of merges to `main`.
- ✅ 100% of RPCs with `google.api.http` annotations covered by the OpenAPI diff or contract test.
- ✅ `UNARY_RPC` lint on, and zero streaming methods.
- ✅ Reflection off in production, and the exposure audit signed off.

After launch, watch as trends: support tickets caused by error-envelope confusion, and cross-version test results per release.

## 10. Open decisions for you

1. **Audit result (A1).** If the internal protos turn out clean, say so and I'll cut the facade down to a thin proxy.
2. **Implementation language of the facade.** This changes whether Connect is cheaper to promote later.
3. **Partner onboarding and KYC.** Decide whether `CreateMerchant` exists for platform partners in v1 or only in `v1beta1`.
4. **Native gRPC for performance partners.** Decide whether a beta binary endpoint is on the roadmap or deliberately absent.
5. **Handoffs to sibling skills.** Notice windows go to `api-versioning-policy`, the error catalog to `api-error-design`, and idempotency and retry semantics to `api-idempotency-retry`.