**Verdict: ❌ not ready to publish.** Three of the ten mappings are wrong, one is missing, and the table has no consumer caveats. The seven lines that are fine match the common gateway mapping (the de facto grpc-gateway convention, not a standard).

## Where the table goes wrong

| gRPC code | Their HTTP | Common gateway mapping | Verdict |
|---|---|---|---|
| `INVALID_ARGUMENT` | 400 | 400 | ✅ |
| `FAILED_PRECONDITION` | **412** | 400 | ❌ |
| `OUT_OF_RANGE` | **416** | 400 | ❌ |
| `NOT_FOUND` | 404 | 404 | ✅ |
| `ALREADY_EXISTS` | 409 | 409 | ✅ |
| `PERMISSION_DENIED` | 403 | 403 | ✅ |
| `UNAUTHENTICATED` | 401 | 401 | ✅ |
| `CANCELLED` | **408** | 499 | ❌ |
| `RESOURCE_EXHAUSTED` | 429 | 429 | ✅ |
| `DEADLINE_EXCEEDED` | 504 | 504 | ✅ |
| everything else | **500** | varies | ❌ |

1. **`FAILED_PRECONDITION` → 412 is wrong.** The skill calls this "the recurring point of confusion". Gateways use 400. HTTP 412 means a conditional request header (`If-Match`, `If-Unmodified-Since`) failed. Partners who see 412 will look for an ETag problem that doesn't exist.
2. **`OUT_OF_RANGE` → 416 is wrong.** 416 means a `Range` header can't be satisfied. Gateways use 400. A bad page offset or index is not a byte-range failure.
3. **`CANCELLED` → 408 is wrong.** 408 means the server timed out waiting for the client's request. `CANCELLED` means the caller abandoned the call. Gateways use 499 (non-standard "Client Closed Request", no formal IANA status). If you dislike 499 in public docs, pick a deliberate alternative and document it. Don't pick one with the opposite meaning.
4. **The catch-all to 500 is the worst defect.** It silently swallows four real codes:
   - `UNAVAILABLE` should be 503. It is the only code generally safe to auto-retry (AIP-194). At 500, partners' retry logic can't tell a transient outage from a bug.
   - `ABORTED` should be 409. It is a retryable concurrency conflict, and it ends up looking like a server fault.
   - `UNIMPLEMENTED` should be 501.
   - `DATA_LOSS` and `UNKNOWN` correctly land on 500, so those two are fine.

   Map all 17 codes explicitly. A fallthrough is fine only for codes added in the future.

## The deeper problem: wrong source, wrong direction

"They pulled it from the gRPC docs" is the root cause. The gRPC project's own text says servers must not use its HTTP↔gRPC table to pick an HTTP status. Its words: "the mappings are neither symmetric nor 1-to-1." That table exists for clients interpreting responses that arrived without a `grpc-status`.

An outbound gateway needs its own deliberate mapping. Confirm it against the transcoder you actually run, because grpc-gateway and Envoy tables can differ. Which gateway do you use: grpc-gateway, Envoy, or Connect-RPC?

## Corrected table

This assumes the grpc-gateway convention. Verify it against your actual gateway before publishing.

| gRPC code | HTTP |
|---|---|
| `INVALID_ARGUMENT`, `FAILED_PRECONDITION`, `OUT_OF_RANGE` | 400 |
| `UNAUTHENTICATED` | 401 |
| `PERMISSION_DENIED` | 403 |
| `NOT_FOUND` | 404 |
| `ALREADY_EXISTS`, `ABORTED` | 409 |
| `RESOURCE_EXHAUSTED` | 429 (pair with `RetryInfo`) |
| `CANCELLED` | 499 |
| `INTERNAL`, `UNKNOWN`, `DATA_LOSS` | 500 |
| `UNIMPLEMENTED` | 501 |
| `UNAVAILABLE` | 503 |
| `DEADLINE_EXCEEDED` | 504 |

## What the partner docs must also say

1. **The HTTP status is lossy.** Three codes share 400 and two share 409. State that the structured error body (`code`, `message`, `details`) is the source of truth.
2. **Retry guidance.** Only `UNAVAILABLE` (503) is safe to retry automatically. Everything else needs `RetryInfo` or the caller's judgment.
3. **Use the most specific code.** Return `OUT_OF_RANGE` over `FAILED_PRECONDITION` where both apply. Don't default to `UNKNOWN` or `INTERNAL`, which flattens your status dashboards into one bucket.

## Checks to run before publishing

- **Detail survival.** The doc promises a structured body, so check your gateway actually delivers it:
  - grpc-gateway's default handler drops `details` entirely. You need a custom error handler.
  - Envoy needs `convert_grpc_status: true`, and every detail type must be in the proto descriptor. Missing types drop silently.
  - Connect-RPC emits JSON errors natively.
- **No `DebugInfo` leaks.** Filter `DebugInfo` out of `details` before responses leave. Sanitizing `message` alone is not enough.
- **A contract test of the mapping.** Test all 17 codes through the real gateway, so the published table can't drift from behavior.

## Next step

Tell me which gateway you run. I can then confirm the exact mapping and write the partner-doc error section.