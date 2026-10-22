# Verdict: don't do it. Use unary as the default, and add streaming only where the data is a stream.

## The widget kills the "everywhere" rule

- Browsers can't speak native gRPC. JavaScript has no access to HTTP/2 framing or trailers.
- gRPC-Web supports unary and server streaming only. It has no client streaming and no bidi, so the widget can't call a bidi read method at all.
- Native gRPC needs HTTP/2 end to end, so HTTP/1.1 clients are out. gRPC-Web and the Connect protocol do work over HTTP/1.1, but only for unary and server-streaming calls.
- Making the widget work means shipping a second, non-bidi surface anyway. Then "uniform bidi" no longer exists.

## The throughput argument is weak

- Unary calls on one long-lived HTTP/2 channel already share a connection. Setup cost is paid once, not per call.
- Bidi only saves per-stream headers and a stream open. That's tiny next to payload and server time.
- Concurrent unary calls get you the same pipelining.
- Treat the gain as unproven until you benchmark it (`ghz` against both shapes, with real payloads).
- "Free" is wrong. Bidi adds stream lifecycle, backpressure, and half-close handling to every partner client.

## What bidi costs on your platform

- **Load balancing:** ALB balances per request, and a stream is one request. Long-lived streams pin to one target, so load skews and deploys need careful draining.
- **ALB timeouts:** The idle timeout (default 60s, configurable) applies to streams. Test whether HTTP/2 keepalive pings reset it. I'm not certain they do.
- **ALB requirements:** gRPC target groups need an HTTPS listener and HTTP/2 to targets. Partners must speak HTTP/2 to the ALB.
- **Errors:** A fatal error kills the whole stream. Per-message errors have to be carried in-band.
- **Retries:** The gRPC retry policy doesn't help once a stream has started.
- **Quotas:** Quota, rate limiting, auth refresh, and billing become per-message instead of per-call.
- **Observability:** Per-call metrics, logs, and traces become per-stream, which is far less useful.
- **Debugging:** `grpcurl`, curl, and support debugging all get harder for partners.

## Recommended shape

| Read type | RPC shape |
|---|---|
| Point lookups, bounded lists | Unary, with pagination |
| Large exports, live tail, watch | Server streaming |
| Interactive sessions where the client changes the subscription mid-stream | Bidi (justify case by case) |

- **Widget:** Add a REST/JSON transcoding layer (grpc-gateway, Connect, or Envoy). Use server streaming or SSE for live data.
- **Partner backends:** Offer native gRPC unary and server streaming. The transcoded REST surface also covers partners who prefer REST.

## What to say to the architect

- His instinct is right in one case: high-rate, long-lived, interactive reads. Keep bidi for those.
- Ask him for a benchmark showing bidi beating pipelined unary on your real workload. Without one, the throughput claim is a guess.
- Ask which of your read methods are actually streams. I'd bet most are point reads.

I haven't seen your service definitions or traffic profile. The ALB details come from my knowledge of its gRPC support, so check them against current AWS docs and test them in staging before committing.

If you send me the list of read methods, I can sort each one into unary, server-streaming, or bidi.