# Public gRPC case studies and transcoding mechanics

Detail behind SKILL.md steps 1, 4, and 6. Sources: Google Cloud engineering blog ("Understanding gRPC, OpenAPI and REST"), Google Apigee blog ("From gRPC to RESTful APIs", 2024), Square engineering (2015), Dropbox engineering (Nginx→Envoy migration), Cloudflare blog and product docs, Temporal.io documentation, Buf announcements ("Connect: A better gRPC"; CNCF acceptance), Microsoft gRPC-vs-HTTP comparison, Google Cloud and AWS load-balancer documentation. Each entry keeps its precision caveat - do not cite beyond what the caveat allows.

## Case studies, with precision caveats

**Google Cloud - the archetype of gRPC-plus-transcoding.** External Google Cloud APIs are dual-published: a REST/JSON facade plus native gRPC, with SDKs shipping actual gRPC stubs where latency matters (Bigtable, Spanner, Pub/Sub, Firestore) and REST for the rest. Two distinct quotable arguments from Google itself:

- Reach (Apigee, 2024 - use when deciding _whether_ to transcode): "not all developers are equipped or experienced enough to consume gRPC services. API providers would therefore risk missing out on a potential audience by limiting themselves to exposing gRPC services only."
- Control loss (Google Cloud engineering blog - use when weighing the operational cost of gRPC at the edge): adopting gRPC in place of OpenAPI/REST gives "much more limited opportunity to augment or remediate the API's behaviors in proxies, especially API management tools."

**Square - dual-stack, stated with its caveat.** Square's 2015 engineering post recounts evaluating open-sourcing its internal Protobuf-based RPC library, then choosing to get involved with gRPC instead - establishing gRPC/Protobuf as Square's internal contract layer (payments-fraud, accounting, dispute-resolution flows). Separately, Square's public developer API is REST/JSON (HTTPS + JSON bodies, a `Square-Version` header, cursor pagination) - "because partner developers expect that."

**Caveat:** the crisp "gRPC inside, REST outside" framing combines two separate primary sources; no single Square sentence asserts both halves, and secondary claims circulating about Square (e.g. a "35% fraud-decision tail-latency improvement") could not be verified against any Square primary source - never repeat them as company-stated fact. Netflix and Lyft are also _reported_ to run the same split in the same source family, but only Square's product-surface detail was independently verifiable - name them only as "also reported", never with Square's level of detail.

**Dropbox - internal gRPC, public gRPC as a stated aspiration only.** Dropbox runs gRPC internally via an in-house framework named Courier. Its Nginx→Envoy migration writeup notes internal and private-external APIs "gradually migrating from REST to gRPC" and muses about eventually offering "public gRPC APIs… transcoding our existing REST-based APIs right on the Edge" - an aspiration, not a shipped state; the public surface remained REST-fronted as of that post.

**Cloudflare - both practitioner and vendor.** gRPC for internal Kubernetes pod-to-pod communication, while separately shipping gRPC proxying as a customer-facing product (WAF understanding of gRPC semantics, HTTP/2 to origin) so customers can run their own public gRPC APIs behind Cloudflare. Cite it as the named answer to "what actually terminates TLS and enforces policy in front of our raw gRPC edge".

**Temporal.io - the genuine public-gRPC counter-example.** Temporal's Cloud Ops API is "an open source, public HTTP API and gRPC API", with proto files published on GitHub and the Buf Schema Registry for client-library generation; the server frontend API is gRPC wrapped directly by official SDKs. It works because the consumer base is control-plane/infrastructure engineers already fluent in generated-SDK tooling - exactly SKILL.md's SDK-mediated trigger. Note that even Temporal dual-publishes an HTTP API alongside the gRPC one.

**Bottom line by audience** (near-verbatim from the 2026 source consensus):

- Broad third-party developer platforms (payments, SaaS partner APIs, anything browser-adjacent): REST/JSON, optionally Protobuf-defined and transcoded, remains the right default in 2026.
- Infrastructure/control-plane APIs whose users are engineers wiring up SDKs: native gRPC or Connect-RPC is defensible and increasingly the more attractive choice.

## Transcoding-option mechanics table

The menu SKILL.md step 6 ranks; this table carries the per-option mechanics. gRPC-Web appears here for completeness - Connect serves the gRPC-Web protocol itself, which is why it does not need its own rung in the menu.

| Option                     | What it is                                                        | Streaming                                                    | Browser path                      | Proxy needed?                                  | Operating burden                                                                                                                                |
| -------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Connect-RPC                | Buf's slim framework; one server speaks Connect + gRPC + gRPC-Web | Full, incl. bidi over HTTP/2; server-streaming over HTTP/1.1 | Native via connect-web - no proxy | No                                             | Lowest: "no custom HTTP implementation, no new name resolution or load balancing… any package that works with net/http also works with Connect" |
| Envoy gRPC-JSON transcoder | Envoy HTTP filter driven by proto descriptors; no codegen         | Server-streaming (array semantics)                           | Via REST/JSON (any client)        | Yes - Envoy, often already the mesh data plane | Config-heavy, no generated code; the most common approach in Kubernetes environments; descriptor set must be kept in sync                       |
| grpc-gateway               | Codegen'd Go reverse proxy from `google.api.http` annotations     | Server-streaming via chunked/SSE; limited                    | Via REST/JSON                     | Runs as a separate proxy/handler               | Regenerate on every proto change; double JSON↔protobuf parse per request; default error handler drops `details`                                 |
| gRPC-Web                   | Official browser answer; needs a translating proxy                | Server-streaming only; no client/bidi                        | Yes (generated JS/TS client)      | Yes (Envoy or equivalent)                      | Frontend regenerates stubs; historically poor TypeScript ergonomics                                                                             |
| Raw public gRPC            | Native gRPC exposed at the edge                                   | Full                                                         | None - browsers cannot connect    | gRPC-aware L7 edge (LB, WAF, TLS)              | Consumer-side Protobuf tooling mandatory; full exposure audit; API-management tooling coverage limited                                          |

**Performance honesty across the table:**

- grpc-gateway pays a double parse (JSON→protobuf→JSON) on every request.
- Envoy's transcoder similarly adds JSON parse/serialize overhead.
- gRPC-Web sends binary end-to-end and avoids gateway-side parsing.

No JSON-transcoding path is free - steer performance-critical consumers to native gRPC or Connect's binary mode.

**Connect-RPC adoption facts, dated:** Connect-RPC was accepted to the CNCF Sandbox on April 13, 2024 (Buf's announcement followed on June 4, 2024). Named production adopters per Buf: CrowdStrike, PlanetScale, RedPanda, Chick-fil-A, Bluesky, Dropbox. It is wire-compatible with gRPC, validated against Google's own interoperability test suite.

Buf's launch framing of plain grpc-go - "130 thousand lines of hand-written code… nearly a hundred configuration options, and bespoke name resolution and load balancing" - against Connect's premise that "conceptually, the gRPC protocol is HTTP with Protobuf-encoded bodies". Import-path footnote for any example code: the Go package moved from `github.com/bufbuild/connect-go` to `connectrpc.com/connect` at v1.0 (2023); the packages are identical apart from the import path.

## Load-balancer keepalive and idle-timeout numbers

The streaming/load-balancing rule in SKILL.md step 4, with the vendor numbers that make it actionable rather than "configure keepalive appropriately":

| Balancer                             | Idle/keepalive timeout                                                                                       |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| Google Cloud external Application LB | 600 s backend keepalive - Google states the backend value "is fixed" (client-side default 610 s, adjustable) |
| AWS Classic / Application LB         | 60 s idle timeout (default)                                                                                  |
| AWS Network LB (TCP flows)           | 350 s (default)                                                                                              |

**The actionable rule:** set the gRPC client's HTTP/2 keepalive PING interval _below_ whichever load balancer idle timeout applies on the path, or the balancer silently drops the connection before the client-side keepalive ever fires. These are vendor-documented defaults as of 2026 - reverify against current vendor documentation before quoting in a design doc, since defaults change.
