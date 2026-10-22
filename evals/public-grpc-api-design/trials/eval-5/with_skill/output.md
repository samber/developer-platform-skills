# Verdict: reject "bidi streaming for every read"

Keep unary as the default. Make a streaming method a recorded exception, and prefer server-streaming over bidi. This follows `public-grpc-api-design` steps 1, 4 and 6.

## Why the architect's argument fails

**1. The connection-setup saving is not real for unary.**
- gRPC unary calls already multiplex over one long-lived HTTP/2 connection.
- Setup is paid once per channel, not once per call.
- The throughput gain he expects is mostly already there.
- Microsoft's gRPC guidance, quoted in step 4, says "replacing unary calls with bidirectional streaming for performance reasons is an advanced technique and is not appropriate in many situations".
- Treat any throughput claim as unmeasured until someone benchmarks it. The skill's rule is to benchmark the end-to-end operator, not the kernel.

**2. The HTTP/1.1 widget makes this a hard wall.**
- Browsers cannot do client or bidi streaming over HTTP/1.1. That is a protocol limit, not a tooling gap.
- The skill's own Connect-RPC mechanics table gives only server-streaming over HTTP/1.1 and full bidi only over HTTP/2.
- Even gRPC-Web is server-streaming only, with no client or bidi streaming.
- So under the architect's plan, the embedded widget cannot call any read method.
- Customers choose their own web apps, so you cannot force them onto HTTP/2.

**3. Bidi has no HTTP mapping.**
- AIP-127 requires a `google.api.http` mapping for every RPC except bidi.
- Every bidi read would be invisible to any transcoded JSON surface.
- Each one would need a documented non-streaming alternative. That means you'd build unary reads anyway, plus the bidi ones.

**4. It makes life harder for partner backends too.**
- A stream can fail mid-flight after partial data.
- Every partner SDK then needs restart and resume bookkeeping, which a unary retry never requires.
- Retries stop being managed transparently by the client library.
- A plain "get this resource" read has no streaming shape, so you'd be paying these costs for nothing.

**5. "gRPC gives us bidi for free" is the named anti-pattern.**
- Step 4 says streaming is never a free feature. Each streaming method needs its costs accepted and written down.

## Your ALB makes it worse

Streaming also stresses the load balancer.
- AWS ALB's default idle timeout is 60 s (vendor default as of 2026, so re-check it).
- Long-lived streams need client HTTP/2 keepalive PINGs set below that interval. Otherwise the ALB drops connections silently before keepalive fires.
- With streams pinned to one backend per connection, you also get uneven load unless balancing is L7 and HTTP/2-aware.
- From general AWS knowledge, not the skill: ALB supports gRPC only on an HTTPS listener with a gRPC-protocol target group. It does no JSON transcoding, so it does nothing for the widget. You'd still need Connect-RPC, the Envoy transcoder or grpc-gateway behind it.

## What I would do instead

**1. Run the when-gRPC gate first (step 1).**
- Partner backends are plausibly SDK-mediated, which is the legitimate trigger for public gRPC.
- The widget is a browser client, so raw public gRPC is ruled out as the only surface.
- Even Temporal dual-publishes an HTTP API next to its gRPC one.

**2. Use unary for all reads.**
- Use standard `Get` and `List` methods with pagination.
- Enable buf's `UNARY_RPC` lint category so a streaming method cannot slip in unnoticed.

**3. Add streaming only where a real need exists.**
- Candidates are tailing telemetry or push updates.
- Use server-streaming first. It maps to SSE through a gateway and works over HTTP/1.1 via Connect.
- Record the accepted tradeoff for each streaming method.

**4. Put Connect-RPC at the edge (step 6, the default rung).**
- One server speaks Connect, gRPC and gRPC-Web, with no proxy needed.
- The widget is served natively and errors come out as JSON.
- Choose the Envoy transcoder instead only if Envoy is already your mesh data plane.
- Connect-RPC is the lowest-effort and highest-value rung on the skill's ranking.

**5. Address the ALB.**
- Use an HTTPS listener with HTTP/2 to the targets, or the gRPC target-group protocol.
- Set client keepalive below the 60 s idle timeout.
- Raise the idle timeout if you do add streams.

## What to say to the architect

- "Unary already reuses one HTTP/2 connection, so the saving is small and unmeasured."
- "Our widget runs on HTTP/1.1, where bidi is impossible."
- "Bidi has no HTTP mapping and forces us to build unary alternatives anyway."
- "If he has benchmarks showing unary is a bottleneck for a specific read, bring them. The skill allows streaming for measured performance needs, as an exception."

## Questions that would change this

1. Is any read genuinely streaming-shaped, such as live telemetry tailing? If so, only that method gets server-streaming.
2. Does a public REST surface already exist that this must stay consistent with?
3. Was this service built internal-first? If so, run the step 7 exposure audit (disable reflection, check for admin and debug RPCs) before launch.
4. What is your ship date and effort ceiling? These could re-rank the edge choice toward whatever you already operate.

I did not read the other two references (proto governance, error mapping). They cover steps 2, 3 and 5 and don't bear on the streaming question.