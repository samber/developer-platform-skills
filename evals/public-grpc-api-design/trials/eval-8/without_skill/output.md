**Decision: use Envoy as the single edge, with its gRPC-JSON transcoder. Skip grpc-gateway as a separate service.** Fallback: if the week-1 spike fails, embed grpc-gateway inside each Go service. Do not run it as an extra hop.

This assumes your Go backends already speak gRPC with protos. If they are plain `net/http` JSON, you need no gateway at all. Envoy alone covers it. Confirm this first.

## Why

- Envoy already runs as your data plane, so you add no new component to deploy, scale, or page on.
- Partners care about latency. Transcoding inside Envoy adds no hop. A standalone grpc-gateway adds one (client, Envoy, gateway, service), and you still need Envoy for TLS, authn, and rate limits.
- Two engineers know Envoy config. Nobody needs to learn a new proxy.
- One place handles authn, rate limits, CORS, and metrics. Partner and dashboard traffic share it.
- Six weeks is tight. Fewer moving parts wins.

## Options

1. **Envoy-only (recommended).**
   - Filters: `grpc_json_transcoder`, `jwt_authn` or `ext_authz`, rate limit, CORS, and optionally `grpc_web` for the browser.
   - Pro: lowest latency, no new service, one control point.
   - Con: transcoding logic lives in Envoy config. You cannot add custom Go logic to responses. Debugging means reading Envoy logs and descriptors. Only two people know it.
2. **grpc-gateway as a separate service behind Envoy.**
   - Pro: best-known tool. Plain Go, easy to unit test, generates OpenAPI.
   - Con: extra hop and extra service. You run two proxies. This is the team's instinct, but it costs you most where partners care most.
3. **grpc-gateway embedded in each service (fallback).**
   - The REST mux and the gRPC server share one process. Envoy only routes by path.
   - Pro: no extra hop, full Go control, familiar.
   - Con: every service carries the gateway code and a second listener. Handler behavior is spread across services.
4. **Connect-RPC (connect-go).**
   - One handler serves gRPC, gRPC-web, and JSON over HTTP. The browser needs no proxy filter.
   - Con: JSON is POST/RPC style, not REST. Partners lose GET caching and ETag semantics. It also means migrating handlers. Pick it only if you do not need REST resources.
5. **Dedicated API gateway (Kong, Apigee, and similar).** Too much to adopt in six weeks. Skip.

## Partner polling

- Rate limit per partner key at Envoy.
- Have services return `ETag` and honor `If-None-Match` so repeated polls get cheap 304s.
- Load test before week 6 with realistic poll rates.

## Plan

1. **Week 1:** Spike the transcoder against 2 real services. Time-box to 3 days.
2. **Weeks 2-3:** Build the routes, authn, rate limits, and CORS.
3. **Week 4:** Integrate the dashboard.
4. **Week 5:** Run the partner load test and tune.
5. **Week 6:** Harden, write the runbook, and hold a go/no-go.

## Week-1 spike pass criteria

- Descriptor set builds with `--include_imports --include_source_info` and ships via your xDS or ConfigMap path.
- `google.api.http` annotations cover your routes.
- gRPC status maps to the right HTTP codes, and error bodies are usable by partners.
- `int64` as JSON strings, enums, and field masks behave acceptably.
- Added p99 latency is acceptable under load.
- If any of these fails and has no quick fix, switch to option 3.

## Risks

- **Bus factor of 2 on Envoy config.**
  - Keep config in repo and generate it from templates.
  - Validate in CI with `envoy --mode validate`.
  - Pair a third engineer in week 2.
- **Descriptor and service version drift.** Build and deploy the descriptor in the same pipeline as the proto change.
- **Streaming.** Transcoded server streams return JSON arrays. Do not use them for long polling.

**Next (2 minutes):** confirm whether the backends already expose gRPC with protos. If yes, approve option 1 with option 3 as the fallback. If no, drop the gateway question and use Envoy-only.