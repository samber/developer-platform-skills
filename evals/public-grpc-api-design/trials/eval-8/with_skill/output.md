# Edge architecture decision: Bellweather Analytics

## Decision

**Use Envoy's gRPC-JSON transcoder at the edge, not grpc-gateway.** Annotate the protos with `google.api.http`. Serve JSON to the dashboard and to partners at launch. Keep Connect-RPC as a planned upgrade for partners whose latency needs JSON can't meet.

**Next action:** confirm the five assumptions below by Friday. Then have the two Envoy engineers build the transcoder spike this week, not next.

## Assumptions to confirm

I haven't seen your protos or infrastructure. The skill says to ask these first. I'm assuming the following, and each one changes the answer if it's wrong.

1. ℹ️ The Go backends already speak gRPC inside the mesh. If they don't, there is nothing to transcode and this is a REST design question.
2. ℹ️ The dashboard calls the API directly from the browser. If a backend-for-frontend sits in between, that changes the browser constraint.
3. ℹ️ No public REST surface exists yet that this must stay consistent with.
4. ℹ️ Partners are unlikely to be SDK-mediated, because you describe them as backends that poll. They are raw HTTP or proto integrators.
5. ℹ️ "Poll hard" means high-QPS unary reads, not a need for push.

## Options

| | grpc-gateway | Envoy transcoder | Connect-RPC | Raw public gRPC |
|---|---|---|---|---|
| Browser | Yes, via JSON | Yes, via JSON | Yes, natively | ❌ Impossible |
| New runtime to operate | Yes, a Go proxy | **No**, you already run Envoy | No proxy needed, but every service's server layer changes | Gateway-aware L7 edge |
| Codegen per proto change | Yes | No, descriptor set only | Yes | Partners generate stubs |
| Error `details` reach consumers | ❌ Dropped by default; custom handler needed | Yes, if configured | Yes, JSON natively | Yes |
| Latency path | Extra hop plus double JSON↔protobuf parse | JSON parse in Envoy, no extra hop | Binary or JSON, no gateway | Binary, best |
| Fit for 6 weeks | Medium | **Best** | Risky: new framework on the critical path | Wrong audience |

## Why not grpc-gateway

- ⚠️ **You'd run a second proxy beside Envoy.** The path becomes Envoy → gateway → service. That adds a hop for partners who care about latency.
- ⚠️ **The default error handler flattens messages and drops `details`.** You'd need a custom handler, and with it extra code and tests, before external errors are usable. Envoy returns the structured `google.rpc.Status` JSON with `convert_grpc_status: true`.
- ⚠️ **It regenerates a Go proxy on every proto change.** Envoy needs only a refreshed descriptor set.
- ✅ It costs the same order of effort as Envoy in general, but "already run Envoy, two engineers know it" breaks that tie. The team's instinct is that it's the best known and everyone is Go. That is a reason for the backends, not for the edge.

## Why not Connect-RPC first

- Connect is the skill's default for new surfaces. It's the best long-term fit: one server speaks Connect, gRPC and gRPC-Web, the browser works natively, and errors are JSON.
- ⚠️ It means changing every service's server layer inside the six-week window. The mesh edge is already there. Save the migration for after launch.
- ✅ Connect handlers stay wire-compatible with gRPC, so Envoy keeps routing to them. Adopting Connect later does not undo this decision.

## Why not raw public gRPC

- ❌ Browsers can't speak gRPC framing, so it can't be the only surface.
- Partners are not confirmed SDK-mediated, so they would each carry the `protoc` and stub cost.
- It needs a full audit of internal RPCs before anything is public.

## Latency caveat for partners

- ⚠️ Every JSON-transcoding path pays a parse and serialize cost. Envoy's is no exception.
- ⚠️ The skill's 3-11x size and 8-12x speed figures for protobuf versus JSON are vendor benchmarks, directional only. Measure your own numbers.
- 🎯 **Gate in week 3:** load-test the transcoded path at expected partner poll rates. Record p50 and p99 against a direct gRPC call. If partners miss their latency target, move those partners to Connect's binary mode or native gRPC.
- ℹ️ Envoy's transcoder gives server-streaming only as array semantics, not SSE. If "poll hard" turns out to mean "wants push," the transcoder won't meet it. Treat that as a separate design and don't add it now. Keep the surface unary, and turn on buf's `UNARY_RPC` lint.

## What to build in six weeks

| Week | Work |
|---|---|
| 1 | Proto package `bellweather.analytics.v1`. Directory mirrors the package, version is not in the filename. One request and response message per RPC. Add `google.api.http` annotations. Run a transcoder spike. |
| 2 | Build the descriptor set from **public protos only**, and include `google/rpc/error_details.proto` or the details drop silently. Set `convert_grpc_status: true`. Add CORS for the dashboard origin. |
| 3 | Add `buf lint` (STANDARD) and `buf breaking` (FILE) as hard CI gates. Add the latency load-test gate. |
| 4 | Auth, TLS, rate limits at the edge (details below). |
| 5 | Dashboard integration, error-envelope docs, contract tests on transcoded routes. |
| 6 | Exposure audit, launch checklist, buffer. |

## Gates and traps

- ⚠️ **`buf breaking` doesn't inspect `google.api.http`.** A change to a URL, verb or body mapping can break partners while buf stays green. Snapshot the derived HTTP routes and diff them in CI, or add contract tests. This is a hard requirement.
- ⚠️ **Don't derive HTTP statuses from the client-side gRPC↔HTTP table.** The gRPC project forbids servers from doing that. Check what Envoy actually returns.
- ℹ️ Three codes collapse to 400 and two to 409. Document that the body envelope is the source of truth, not the status line.
- ⚠️ **Strip `DebugInfo` from error details before responses leave the edge.** Sanitizing `message` alone is not enough.

## Auth and exposure

1. 🔐 TLS at the edge, always.
2. 🔐 Use Client Credentials OAuth2 for partner backends and Authorization Code with PKCE for dashboard users. Validate JWTs in Envoy's `jwt_authn` filter.
3. 🔐 Enforce scopes per method, not just "is authenticated".
4. 🔐 Rate limit with `RESOURCE_EXHAUSTED` (429) plus a `RetryInfo` detail. Hard-polling partners need that backoff signal.
5. 🔐 API keys identify the consumer for quota. They are not authentication.
6. 🔐 Disable server reflection in production. Audit the full method surface for admin, debug and monitoring RPCs. Building the descriptor from public protos only gives you an allowlist for free.
7. mTLS stays inside the mesh. It does not go to partners.

## Revisit when

- Partner load tests miss the latency target. Then move those partners to Connect binary or native gRPC.
- Several products will share this contract for years. Then weight error fidelity and move toward Connect sooner.
- A partner cohort turns out to be SDK-mediated and proto-fluent. That is the one case that justifies public gRPC, and even then ship an HTTP surface alongside it.

## What I could not verify

I checked this against the skill and its references only. The numbers there are vendor figures and I did not re-verify them. Envoy transcoder behavior on your exact version, including streaming and detail-type handling, needs the week-1 spike to confirm. I haven't seen your Envoy config, your protos or your partner SLAs.