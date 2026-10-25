# Router isolation for partner-hosted resolvers

Runtime controls between the platform router (or extension proxy) and any resolver a partner hosts: rungs 3-5 of the extension ladder. Load this when configuring the router, the proxy, or reviewing a partner integration before launch.

## Contents

- What leaves the perimeter
- Credentials
- Blast radius
- Routing URLs
- Caching
- Router CVEs that widen partner exposure
- Integration note: engine defaults

## What leaves the perimeter

Every call to a partner resolver carries data. List it per partner, field by field, before launch:

- Entity representation: `__typename` plus every field of the `@key`.
- Every field named in the partner's `@requires`, fetched from platform subgraphs and shipped even when the client never selected it.
- Arguments the client passed to partner fields.
- Headers the router propagates or inserts.
- Response `extensions` the router forwards (tracing can leak internal service names).

The data-clearance list per entity is the contract: what the partner may receive, under which consent. Anything outside it is a leak, however the field got there.

## Credentials

- Default to forwarding no client header to a partner. Some engines start empty and some ship a "forward all client headers" switch; check which one you run, then write an explicit allowlist.
- Never forward the end user's bearer token, session cookie or platform API key to a partner. Mint a per-partner credential instead: short-lived, audience-bound to that partner, scoped to the installing tenant and the consented scopes (OAuth 2.0 Token Exchange, RFC 8693, is the standard shape).
- Never add a catch-all propagation rule toward a partner. Rule order decides the outcome (a `remove` placed before a catch-all `propagate` has no effect), and an explicit per-header allowlist leaves nothing to order.
- Mint the per-partner token in code that runs per request: a router extension or coprocessor, or the egress proxy. Static header inserts carry only fixed values.
- Sign router-to-partner requests (mTLS or a request signature) so the partner can reject calls that did not come from the platform; partner endpoints are public URLs.
- Treat every value a partner returns as untrusted input: platform resolvers that `@requires` a partner field, or display it, validate it like user input.

## Blast radius

- Set a per-partner timeout well below the client latency SLA. Router defaults (30 s on one engine, 60 s on another) sit far above any client SLA.
- Add a per-partner circuit breaker that counts timeouts as failures, so a degraded partner is skipped instead of retried on every request.
- Size the partner timeout as client SLA minus the internal p95 up to the partner hop minus a margin; a `@requires` hop runs only after the platform fetches it depends on.
- Add a request-level deadline in front of engines that lack one: sequential entity fetches can take several multiples of one subgraph's timeout. Set it above the partner timeouts; a whole-request deadline that fires first fails the query instead of degrading to partial data.
- Where the router has no circuit breaker, route partner calls through an egress proxy with outlier detection.
- Rate-limit per partner subgraph and price partner fields in the query cost model, so one client cannot fan a query out into thousands of partner calls.
- Keep partner fields nullable (see the SDL policy) so a timeout yields partial data plus an error, never a blanked platform object.

## Routing URLs

A partner-submitted routing URL makes the router issue server-side requests to an address someone else chose. Validate on submission and on every DNS resolution:

- HTTPS only, public routable addresses only.
- Reject private, loopback, link-local and cloud metadata ranges, including after redirects and DNS rebinding.
- Pin the egress path: partner calls leave through a dedicated egress proxy with an allowlist of registered partner hosts.

## Caching

Shared response caches default to shared visibility on some engines. A partner response without a private cache scope is served to every user. Mark every partner field private-scoped, or exclude partner subgraphs from shared caching altogether, and include the tenant in any cache key that touches partner data.

Cross-request query deduplication is sharing too: identical in-flight subgraph requests from different callers collapse into one. Turn it off for partner subgraphs unless the engine documents that the deduplication key includes the forwarded credential.

## Router CVEs that widen partner exposure

No published CVE targets a malicious subgraph directly. These router bugs show how one subgraph's schema choices change the platform's exposure:

- CVE-2024-43414: query-planner infinite loop; Federation 2 graphs are affected only when `@shareable` fields are resolved by more than one subgraph. A partner co-resolving a shareable field opts the platform in. Fixed in Router 1.52.1 and query-planner 2.8.5.
- CVE-2024-32971 (CVSS 9.1): with distributed query-plan caching enabled, Router 1.44.0-1.45.0 could send the wrong operation to a subgraph. Fixed in 1.45.1. Unrelated to partner schemas: its lesson is that a partner graph multiplies who a router bug hits.
- CVE-2025-64173 (CVSS 7.5): access-control bypass when `@authenticated`/`@requiresScopes`/`@policy` sit on implementing object types but not on their interface; querying through the interface skips them. Fixed in 1.61.12 and 2.8.1. A partner that adds an implementing type or extends an interface can open this path, one more reason to reject `@interfaceObject`.
- CVE-2025-32034: deeply nested named fragments cause exponential planning cost. Fixed in 1.61.2 and 2.1.1.

Patch the router on a schedule the partner program depends on; a partner graph multiplies who is affected by a router bug.

## Integration note: engine defaults

| Engine | Header default | Per-subgraph timeout | Contracts | License |
| --- | --- | --- | --- | --- |
| Apollo Router | Empty until a `propagate` rule runs; rules under `headers.all` / `headers.subgraphs.<name>` | Subgraph default 30 s, per subgraph, returns a GraphQL error with HTTP 200; router (request) timeout also defaults to 30 s and returns 504, so lower partner timeouts below it; no native circuit breaker documented, use an egress proxy | Enterprise; one router instance per contract variant; exclude filters leak untagged fields | ELv2 (router, composition, query planner); subgraph libraries permissively licensed |
| WunderGraph Cosmo | "By default, no headers are forwarded" | `request_timeout` default 60 s per subgraph; per-subgraph circuit breakers; no request-level deadline | Include / exclude / feature-flag via `@tag` | Apache 2.0 |
| Hive Gateway | Explicit propagation rule from client to subgraphs | Upstream timeout configurable | Contracts via `@tag` in the Hive registry | MIT |
| Hasura remote schemas | `forward_client_headers` default false | `timeout_seconds` per remote schema | Role-based permissions | Apache 2.0 (v2 core) |

Use include-only contract filters for any partner-facing graph: an exclude filter publishes every field nobody remembered to tag.

Open standard: the GraphQL Composite Schemas specification (repository now titled "GraphQL Federation") sat at Stage 0, Preliminary, which "can change before reaching Draft stage". Re-check the stage before naming a dialect in a partner contract.
