**Verdict: not right as written. Don't publish it yet.** Three mappings are wrong, and six status codes are missing. The wrong ones aren't in the gRPC docs. The table looks like it was assembled from the HTTP status names, not from the canonical mapping.

## Wrong (fix before publishing)

| gRPC code | Their table | Canonical | Why |
|---|---|---|---|
| FAILED_PRECONDITION | 412 | **400** | HTTP 412 means a conditional header failed (`If-Match`, `If-Unmodified-Since`). Partners' HTTP clients and caches may treat it that way. |
| OUT_OF_RANGE | 416 | **400** | HTTP 416 is only for an unsatisfiable `Range` header. gRPC's OUT_OF_RANGE means something like a bad page offset or index. |
| CANCELLED | 408 | **499** | HTTP 408 means the server timed out waiting for the client's request. CANCELLED means the client gave up. The canonical value is 499 (Client Closed Request). |

The canonical mapping is in `google/rpc/code.proto` and also used by grpc-gateway and Google's AIP-193.

If you want 412 for real `If-Match` / ETag conflicts, that's a legitimate separate case. Make it an explicit HTTP-level rule, not the mapping for FAILED_PRECONDITION.

On 499: it's nonstandard, but it's the canonical value. The client has usually disconnected, so partners rarely see it. If you'd rather stay inside the IANA registry, document a deliberate deviation, but don't use 408.

## Correct as listed

- INVALID_ARGUMENT → 400
- NOT_FOUND → 404
- ALREADY_EXISTS → 409
- PERMISSION_DENIED → 403
- UNAUTHENTICATED → 401
- RESOURCE_EXHAUSTED → 429
- DEADLINE_EXCEEDED → 504

## Missing (the fallthrough gives wrong answers)

The "unclassified → INTERNAL → 500" rule silently misreports these:

| gRPC code | HTTP | What the fallthrough does |
|---|---|---|
| ABORTED | **409** | Returns 500 for a retryable concurrency conflict. |
| UNIMPLEMENTED | **501** | Returns 500, so partners can't tell "not supported" from "broken". |
| UNAVAILABLE | **503** | Returns 500, which breaks retry logic. This is the worst one: 503 is the code clients and load balancers retry on. |
| UNKNOWN | 500 | Fine, but list it explicitly. |
| DATA_LOSS | 500 | Fine, but list it explicitly. |
| OK | 200 | List it for completeness. |

Keep the 500 default for genuinely unrecognized codes. Don't let it stand in for known ones.

## Worth adding for a public partner doc

- **Headers:**
  - 429 and 503 should carry `Retry-After`.
  - 401 needs `WWW-Authenticate`.
- **Retry guidance per code:**
  - Safe to retry: 503, 504 (idempotent calls only), 429 after the delay, and 409 from ABORTED after re-reading state.
  - Do not retry: 400, 401, 403, 404.
- **Existence leaks:** decide whether cross-tenant resources return 404 or 403. For B2B logistics, 404 is usually safer.
- **Error body:** document the shape, and keep INTERNAL and UNKNOWN messages generic so no internals leak.
- **Two 409 sources:** ALREADY_EXISTS and ABORTED both map to 409. Say that partners must read the error body's `status` or `code` field to tell them apart.

## Corrected table

| gRPC | HTTP |
|---|---|
| OK | 200 |
| CANCELLED | 499 |
| UNKNOWN | 500 |
| INVALID_ARGUMENT | 400 |
| DEADLINE_EXCEEDED | 504 |
| NOT_FOUND | 404 |
| ALREADY_EXISTS | 409 |
| PERMISSION_DENIED | 403 |
| RESOURCE_EXHAUSTED | 429 |
| FAILED_PRECONDITION | 400 |
| ABORTED | 409 |
| OUT_OF_RANGE | 400 |
| UNIMPLEMENTED | 501 |
| INTERNAL | 500 |
| UNAVAILABLE | 503 |
| DATA_LOSS | 500 |
| UNAUTHENTICATED | 401 |
| *(unrecognized)* | 500 |

I wrote this from memory of `code.proto` and didn't re-fetch it. Diff it against the current file in googleapis before you publish.