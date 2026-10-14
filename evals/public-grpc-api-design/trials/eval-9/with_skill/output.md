# Partner complaint at Corvid Payments: field-level errors missing from the JSON API

I read the skill and its error-mapping and case-study references. I haven't seen your code, so the diagnosis below is the most likely cause, with a way to confirm it.

## What's happening

Your services are fine. The loss happens at the JSON edge.

- `Status.details` (`ErrorInfo`, `BadRequest`) travels in the `grpc-status-details-bin` trailer. Whether it reaches a JSON body depends on the gateway layer.
- The skill's reference says grpc-gateway's default error handler maps the code to an HTTP status but flattens the message and drops `details`.
- Partners see `{"code":3,"message":"invalid request"}` and nothing else.
- I'm not certain the default handler is the culprit. As I recall, grpc-gateway v2's default handler marshals the whole `Status` proto, `details` included. That differs from the skill's reference, so check your version.
- A flat message with v2 usually means one of these:
  - a custom `WithErrorHandler` that flattens the error;
  - an interceptor or wrapper that rebuilds the error from `err.Error()` and loses the status;
  - detail types missing from the Go proto registry, so `Any` marshaling fails.
- The check takes five minutes. Call the same failing request with `grpcurl` directly against the service, then through the gateway. If `grpcurl` shows `ErrorInfo` and `BadRequest` and the gateway doesn't, the loss is at the edge.

## Don't migrate to Envoy just for this

- The skill's ranking puts Connect-RPC first, then the Envoy transcoder, then grpc-gateway. That ranking is a default, not a law.
- The promotion condition for Envoy is "Envoy is already your mesh data plane and a second runtime is the real cost". If that doesn't describe you, a migration swaps one operational burden for another to fix an error-shape bug.
- Envoy also has its own silent-failure mode:
  - it needs `convert_grpc_status: true`;
  - every detail type must be in the proto descriptor, or the missing types drop with no error.
- A migration changes your whole JSON surface, including paths, error shape and descriptor sync. Partners absorb that change, and fixing this bug doesn't need it.

## A safety issue to fix first: `DebugInfo`

- You attach `DebugInfo` with stack detail to every error.
- It is documented as internal-only. Sanitizing `message` alone is not enough.
- Today the gateway's flattening may be hiding it from partners by accident.
- Once you pass `details` through, whether by fixing grpc-gateway or by moving to Envoy, partners get your stack traces. Do the filtering before you ship the fix.

## What to do

1. **Confirm the diagnosis.** Run the `grpcurl` versus gateway comparison above and check your grpc-gateway version and any custom error handler.
2. **Filter at the edge by allowlist, not denylist.** Pass `ErrorInfo`, `BadRequest`, `RetryInfo`, `QuotaFailure`, `PreconditionFailure`, `Help` and `RequestInfo`. Drop everything else, `DebugInfo` included. A denylist leaks the next internal type someone adds.
3. **Install a custom error handler on grpc-gateway.** Use `runtime.WithErrorHandler`.
   - Emit the Google-style envelope: `{"error":{"code":400,"status":"INVALID_ARGUMENT","message":"…","details":[{"@type":"type.googleapis.com/google.rpc.BadRequest",…}]}}`.
   - Google Cloud APIs and Dapr use this shape, so it is a familiar contract for partners.
   - Make sure the detail types are imported so `Any` can resolve them. Otherwise marshaling fails.
4. **Keep on-call correlation without exposing stacks.** Log `DebugInfo` server-side, keyed by a request ID. Return the ID to partners in `RequestInfo`. Partners can quote it in a ticket and on-call can look it up.
5. **Fix the status-line expectation in your docs.** `INVALID_ARGUMENT`, `FAILED_PRECONDITION` and `OUT_OF_RANGE` all map to 400. `ALREADY_EXISTS` and `ABORTED` both map to 409. Tell partners that the body, `ErrorInfo.reason` plus `BadRequest.field_violations`, is the source of truth. The HTTP status is a lossy convenience.
6. **Check your own status mapping.** The gRPC project says servers must not use its client-side gRPC-to-HTTP table to pick HTTP status codes. Confirm your gateway's mapping is deliberate.
7. **Add a regression gate.** Add a contract test that triggers a validation failure through the JSON endpoint and asserts that:
   - `ErrorInfo.reason` is present;
   - `BadRequest` field violations are present;
   - `DebugInfo` is absent.
   - `buf breaking` won't catch any of this. It doesn't see gateway behavior.

## When Envoy or Connect is the right move

- **Envoy:** you already run it as your mesh or edge data plane, and you'd drop the Go proxy and its codegen. Set `convert_grpc_status: true`, include `google/rpc/error_details.proto` in the descriptor set, and keep the allowlist from step 2.
- **Connect-RPC:** you want a contract several products share for years, or you have browser clients. Errors are JSON natively and no proxy is needed. It's a larger migration for consumers, so schedule it deliberately.

## Questions that would change this advice

- Do you already run Envoy in front of everything?
- Do browser clients call the JSON endpoint?
- Is the JSON surface a contract several products will share for years, or just the partner API?
- Is anything else in the path, such as an API management layer or WAF, rewriting error bodies?

## Result

Partners start getting field-level errors after a small, reversible change. It means a custom error handler plus an allowlist, with no migration. Your stack traces stay internal.