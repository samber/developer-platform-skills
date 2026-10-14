# Diagnosis and recommendation: missing field-level errors on the JSON endpoint

I haven't seen your code, so I'm giving you the most likely causes, a short test to tell them apart, and what I'd do. The test takes about 15 minutes.

## What's probably happening

Your services are fine. The detail is lost somewhere between the gRPC response and the JSON body. It is almost certainly a gateway, handler, or proxy problem, not a transport problem. Stock grpc-gateway v2 serializes the whole `google.rpc.Status`, details included, so a flat message string means something in your path changed that behavior.

Likely causes, most probable first:

1. **A custom error handler flattens the status.** Look for `runtime.WithErrorHandler` (v2) or `WithProtoErrorHandler` (v1) in the gateway setup. A handler that writes `{"error": st.Message()}` or `{"message": ...}` would produce exactly what partners report. Someone may have added it to keep `DebugInfo` from leaking and dropped everything else with it.
2. **The gateway binary can't resolve the detail types.** The default handler marshals `Status` with protojson, which has to unpack each `Any`. If the gateway never links `google.golang.org/genproto/googleapis/rpc/errdetails`, the marshal fails. grpc-gateway then falls back to `{"code":13,"message":"failed to marshal error message"}`, with no details. The fix is a blank import of `errdetails`, or any package that pulls it in.
3. **Something strips the details before the gateway sees them.** A server or client interceptor, or a mesh or proxy, may remove `grpc-status-details-bin` for "external" traffic. A `Status` built with `status.New(...).WithDetails(...)` also loses its details if a middleware rewraps it with `status.Error(code, msg)`.
4. **A layer in front of the gateway rewrites error bodies.** Check any API gateway, WAF, or CDN with custom error pages, and any HTTP middleware that wraps responses with status 400 or above.

## How to tell which one (about 15 minutes)

1. Call the same failing RPC directly over gRPC, bypassing the gateway: `grpcurl -v -d '{...}' host:port pkg.Service/Method`. Look for ErrorInfo and BadRequest in the output.
   - **Details missing:** the bug is on the service side (cause 3). Check interceptors.
   - **Details present:** the loss is in the gateway or in front of it. Go to step 2.
2. Call the gateway directly, bypassing the public edge: `curl -i` against the gateway's own port.
   - **Details present:** the edge is rewriting bodies (cause 4).
   - **Flat message:** go to step 3.
3. Grep the gateway for `WithErrorHandler`, `WithProtoErrorHandler`, `WithStreamErrorHandler`, and `WithRoutingErrorHandler`.
   - **Custom handler found:** that's cause 1.
   - **None, and you get `failed to marshal error message`:** that's cause 2.

## Do not move to Envoy's transcoder to fix this

- Envoy's `grpc_json_transcoder` only emits the `Status` as JSON when `convert_grpc_status` is enabled. It also needs the `errdetails` protos in the descriptor set, or it can't unpack the details. That is the same class of problem you have now, with a harder place to debug.
- Migrating adds rollout risk and changes URL, status-code, and body semantics for every partner.
- It moves error shaping into proxy config. You lose the Go hook where you can allowlist, redact, and add a request ID.

Move only if you have other reasons, such as fleet-wide proxy consolidation or removing a Go hop. Even then, fix the error body first so the migration doesn't change two things at once.

## What I'd do

1. **Find and fix the root cause** using the steps above.
2. **Write one explicit error handler** for the gateway and keep it in the repo. Pass it with `runtime.WithErrorHandler`, and also set `WithStreamErrorHandler` and `WithRoutingErrorHandler` so 404s, 405s, and streams are shaped the same way.
3. **Allowlist what leaves the building.**
   - Pass through: `ErrorInfo` (reason, domain, metadata), `BadRequest` field violations, and optionally `RetryInfo`, `QuotaFailure`, `Help`, and `LocalizedMessage`.
   - Always drop `DebugInfo` and any detail type you haven't listed.
   - Exposing a stack trace to partners is a security leak. If the current setup is hiding it, that part is correct, so keep the redaction when you restore the rest.
4. **Keep on-call correlation without shipping `DebugInfo`.**
   - Log `DebugInfo` server-side, keyed by trace ID or request ID.
   - Return that ID to partners in `ErrorInfo.metadata` and in a response header such as `X-Request-Id`.
   - Partners then paste an ID into the ticket, and your on-call resolves it to the stack.
5. **Define the public JSON contract and document it.** For example:
   ```json
   {
     "code": 3,
     "message": "invalid request",
     "details": [
       {"@type": "type.googleapis.com/google.rpc.ErrorInfo", "reason": "...", "domain": "...", "metadata": {"request_id": "..."}},
       {"@type": "type.googleapis.com/google.rpc.BadRequest", "fieldViolations": [{"field": "...", "description": "..."}]}
     ]
   }
   ```
   Pin it with golden tests so a future handler change can't silently flatten it again.
6. **Add tests.**
   - Run an end-to-end test through the gateway for each error class: validation, not found, permission denied, and internal.
   - Assert that `fieldViolations` survive and `DebugInfo` never appears.
   - Break the handler on purpose once to confirm the test fails.
7. **Tell partners.** The shape change is additive, but they should know `details[]` now exists. Also fix the support-ticket template to ask for `request_id`.

## Open question

If step 1 shows the details are already missing at the gRPC layer, tell me which interceptors or mesh sidecars sit on that path. That would be a different fix.