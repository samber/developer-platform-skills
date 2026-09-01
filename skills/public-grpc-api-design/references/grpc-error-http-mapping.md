# gRPC error model and HTTP mapping reference

Detail behind SKILL.md step 5. Sources: grpc/grpc `doc/http-grpc-status-mapping.md`, `google/rpc/error_details.proto`, grpc-go `codes.go`, Envoy transcoder documentation, grpc-gateway documentation, Connect-RPC documentation, AIP-194.

## The direction rule, quoted

The gRPC project's own documentation on its status-mapping table: **"servers must not use this table to determine an HTTP status code to use... the mappings are neither symmetric nor 1-to-1."** The canonical table exists for a client or intermediary interpreting a response that arrived _without_ a `grpc-status` field. A gateway translating gRPC errors outward for public HTTP exposure needs its own deliberate mapping - and the tables actually shipped by grpc-gateway and Envoy can differ, so confirm against the implementation in use rather than assuming a universal spec.

## The 17 canonical codes and the common gateway mapping

`OK=0` through `UNAUTHENTICATED=16` - 17 codes, verified against grpc-go's `codes.go` (`Unauthenticated Code = 16` immediately followed by `_maxCode = 17`). The gateway-side mapping below is the one grpc-gateway implements - a de facto convention, not a standard:

| gRPC code                            | HTTP    | Note                                                        |
| ------------------------------------ | ------- | ----------------------------------------------------------- |
| `INVALID_ARGUMENT`                   | 400     |                                                             |
| `FAILED_PRECONDITION`                | 400     | **not 412** - the recurring point of confusion              |
| `OUT_OF_RANGE`                       | 400     |                                                             |
| `UNAUTHENTICATED`                    | 401     |                                                             |
| `PERMISSION_DENIED`                  | 403     |                                                             |
| `NOT_FOUND`                          | 404     |                                                             |
| `ALREADY_EXISTS`                     | 409     |                                                             |
| `ABORTED`                            | 409     |                                                             |
| `RESOURCE_EXHAUSTED`                 | 429     | pair with `RetryInfo`                                       |
| `CANCELLED`                          | **499** | non-standard "Client Closed Request", no formal IANA status |
| `INTERNAL` / `UNKNOWN` / `DATA_LOSS` | 500     |                                                             |
| `UNIMPLEMENTED`                      | 501     |                                                             |
| `UNAVAILABLE`                        | 503     | the only code generally safe to auto-retry (AIP-194)        |
| `DEADLINE_EXCEEDED`                  | 504     |                                                             |

**The collapse points to document for consumers:** three distinct codes (`INVALID_ARGUMENT`, `FAILED_PRECONDITION`, `OUT_OF_RANGE`) all become 400, and two (`ALREADY_EXISTS`, `ABORTED`) become 409. A REST/JSON client reading only the status line loses the semantic distinction - state in the API docs that the structured envelope in the body is the source of truth, and the HTTP status is a lossy convenience.

## Code selection discipline

1. Return the most specific applicable code - `OUT_OF_RANGE` over `FAILED_PRECONDITION` when both technically apply.
2. Never default to `UNKNOWN` or `INTERNAL` as a defensive habit. It is the named overused anti-pattern in the wild, and it defeats observability: status dashboards aggregating by code lose all signal when everything routes through one bucket.
3. Sanitize `message` for production - developer-facing English, no internal implementation detail, never the channel for localized end-user text (use a `LocalizedMessage` detail or client-side localization).

## The error-details catalog

`google/rpc/error_details.proto` standardizes the typed payloads carried in `Status.details`:

| Type                                                      | Purpose                                                                                                                                                                                                                 |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ErrorInfo`                                               | machine-readable reason + domain + metadata - the general-purpose detail to reach for first                                                                                                                             |
| `RetryInfo`                                               | how long before a retry is safe - pair with `RESOURCE_EXHAUSTED` and `UNAVAILABLE`                                                                                                                                      |
| `BadRequest`                                              | field-level validation violations                                                                                                                                                                                       |
| `QuotaFailure`, `PreconditionFailure`                     | structured cause lists for their respective codes                                                                                                                                                                       |
| `RequestInfo`, `ResourceInfo`, `Help`, `LocalizedMessage` | request correlation, resource identity, doc links, localized text                                                                                                                                                       |
| `DebugInfo`                                               | **internal only - never expose to external clients.** Stack/trace detail; filter it from `details` before the response leaves the service. Sanitizing `message` is insufficient if `details` still carries `DebugInfo`. |

Only `UNAVAILABLE` is generally safe to auto-retry without additional signal; every other code needs an explicit `RetryInfo` or caller-side judgment before automatic retry. The taxonomy-level decisions - catalog shape, message writing, a `retryable` flag - are `samber/developer-platform-skills@api-error-design`'s territory; its AIP-193 `ErrorInfo` (domain/reason) shape is the one that spans REST and gRPC in a single taxonomy.

## Envelope survival per gateway

Whether `Status.details` reaches the JSON consumer depends entirely on the transcoding layer:

- **Envoy gRPC-JSON transcoder:** with `convert_grpc_status: true`, Envoy takes `google.rpc.Status` from the `grpc-status-details-bin` header and uses it as the JSON body - **but only if the error-detail types are present in the proto descriptor** the transcoder was built with. Omit a detail type from the descriptor set and it drops from the response silently. The resulting shape - `{"error":{"code":…,"status":"INVALID_ARGUMENT","details":[{"@type":"type.googleapis.com/google.rpc.BadRequest",…}]}}` - is what Google Cloud APIs and Dapr return, making it a de facto standard JSON error shape worth adopting even outside a pure-Envoy stack.
- **Connect-RPC:** serializes errors as JSON natively (a code, an optional message, an optional details array); its code mapping is a superset of gRPC's. No transcoding gap exists.
- **grpc-gateway:** the weakest by default - out of the box it maps codes to an HTTP status but flattens the message and **drops `details` entirely**. A custom error handler is required to preserve the structured envelope; budget for it, or prefer Connect/Envoy when structured error detail matters to external consumers.

## Why a team might not use google.rpc.Status at all

gRPC is a CNCF project, not a Google product, and `google.rpc.Status` can be impractical outside Google's context:

- Protobuf-encoded errors cause binary bloat on Android.
- gRPC carries status in HTTP/2 trailers, so any proxy or logging tool wanting the structured fields must unpack the proto instead of using standard HTTP-status tooling.

A lighter home-grown envelope is a legitimate choice - consistency _within_ one system matters more than universal standardization across systems. If taken, the mapping-direction rule and the collapse points above still apply unchanged.
