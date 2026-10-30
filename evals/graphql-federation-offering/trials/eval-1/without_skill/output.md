# Onboarding Quayside's subgraph into the Fernhill supergraph

## Recommendation

**Don't let Quayside's subgraph sit in the live query path for Order tracking before January.** Do this instead:

1. Fernhill defines the shipment contract (schema below) and owns a `shipping` subgraph.
2. Quayside pushes tracking data into it (webhook or API) and never hosts GraphQL.
3. Add a partner-hosted subgraph later, per partner, once the contract has survived a peak.

**Why.** A partner subgraph is a runtime dependency of your public API, not just a schema contribution.

- Every query touching `Order.shipments` fans out to Quayside's servers. Their p99, deploys and outages become yours.
- Their subgraph receives your customers' order IDs, auth context and query shapes. That is a trust boundary you'd be opening under peak load.
- A bad publish from them can fail composition for the whole supergraph. This is safe only if you own the publish pipeline.
- Three partners means three SLAs and three on-call rotations. That is a lot of coordination for a 6-week window.

The webhook path is a standard integration. It also gives you tracking data when Quayside is down, because you hold the last known state.

If the platform lead still wants Quayside hosting a subgraph, the sections below make it safe. Both options share the same schema contract, so you can start with option A and move to B without a client-facing change.

## 1. The contract (Fernhill-owned, partner-agnostic)

Define one carrier-neutral shape. Partners map to it and never extend `Order` directly. If all three partners add fields to `Order`, you get composition conflicts and three diverging vocabularies.

```graphql
# shipping subgraph (Fernhill-owned)
type Order @key(fields: "id") {
  id: ID!
  shipments: [Shipment!]!          # nullable fields inside; list itself never errors the order
}

type Shipment @key(fields: "id") {
  id: ID!
  carrier: Carrier!                # enum or small type: QUAYSIDE_FREIGHT, ...
  trackingNumber: String
  status: ShipmentStatus           # nullable on purpose: see "Failure behavior"
  events(first: Int = 20, after: String): ShipmentEventConnection
  lastUpdatedAt: DateTime
}

enum ShipmentStatus {
  LABEL_CREATED IN_TRANSIT OUT_FOR_DELIVERY DELIVERED EXCEPTION RETURNED
}
```

Rules:

- **Fernhill owns the status enum.** Partners map their codes to it, and unknown codes map to `EXCEPTION` plus a raw code in event metadata.
- **`Order.shipments` returns a list.** Orders split into several parcels, and B2B orders usually do.
- **Tracking fields are nullable.** A partner failure then yields `null` plus an error entry instead of nulling the whole `Order`.
- **Status updates are a paginated `events` field, not a subscription.** Federated subscriptions need extra router and infrastructure setup you shouldn't take on before peak. Clients can poll `status` and `lastUpdatedAt`.

## 2. Option A: Fernhill-owned subgraph with partner ingestion (recommended)

1. **Ingestion API.** `POST /partners/{carrier}/tracking-events`, authenticated per partner (mTLS or signed requests, per-partner credentials).
2. **Payload.** Carrier shipment ref, your order ID or PO number, tracking number, carrier status code, event timestamp, event ID for idempotency.
3. **Processing.** Dedupe by event ID and ignore out-of-order events (keep the highest timestamp). Map the status code and store it.
4. **Resolvers.** `Order.shipments` reads your own store, so there is no partner call at query time.
5. **Authorization.** A shipment is visible only to the customer account that owns the order. Enforce this in your resolver. Partners never see customer queries.

This matches how most carrier integrations work. Whether Quayside can push webhooks is the open question (see the end).

## 3. Option B: Quayside hosts a subgraph

Use this only if Quayside can't push events or the platform lead requires it.

### Schema ownership

- Quayside's subgraph defines only the `Shipment` entity (`@key(fields: "id")`). It adds **no fields to `Order`**.
- Your `shipping` subgraph owns `Order.shipments` and returns stub `Shipment { id carrier }` objects.
- The router calls Quayside only when a client asks for `trackingNumber`, `status` or `events` on a Quayside shipment.
- Use `@tag` or an `@inaccessible` convention so internal helper fields in their subgraph never appear in the public schema.

### Fernhill controls the pipeline, not Quayside

- Quayside commits SDL to a repo you own (or a PR-gated directory). **They don't run `rover subgraph publish` against your graph.**
- CI runs `rover subgraph check` against production traffic for every change. Fernhill's pipeline publishes.
- Set a rule: no `@override`, no `@shareable` on shared types, no field removals without a deprecation period.
- Give Quayside a staging graph variant with a pinned copy of your supergraph so they can test composition without touching production.

### Router configuration (Apollo Router)

- **Per-subgraph traffic shaping for `quayside`.** Short timeout (suggest 1-2 s, tuned from load test), limited retries, and a concurrency cap.
- **Circuit-breaker or fallback behavior.** If Quayside is down, `status` returns `null` plus an error, and the rest of the order still loads.
- **Entity caching** (if you're on a router tier that supports it) for `Shipment` with a short TTL. This protects Quayside from your peak read traffic and protects you from their latency.
- **Header propagation allowlist.** Forward only a signed service token and a request ID. Don't forward customer JWTs.
- **Query cost and depth limits on `shipments` and `events`.** A client shouldn't be able to ask for a deep events list on 500 orders in one query.

### Security requirements before go-live

- mTLS or equivalent between router and Quayside's endpoint, with an IP allowlist.
- Quayside's subgraph receives only shipment IDs, never customer identifiers or order contents.
- Introspection disabled on their endpoint. Their subgraph must reject direct client traffic.
- Their data-processing terms cover being in your request path. Check with legal.

### Operational requirements

- A written SLA: availability, p99 latency, and incident contact.
- Fernhill dashboards for per-subgraph latency, error rate and timeout rate, with alerts.
- A kill switch: the ability to remove or stub their subgraph from composition within minutes. Rehearse this once.
- Load test at roughly 2x your expected January peak with their endpoint in the path.

## 4. Timeline to January

Today is Fri 30 Oct. I'm assuming a change freeze around mid-December. Confirm your actual date, because it sets everything below.

| When | Milestone |
|---|---|
| By Fri 6 Nov | **Decision gate.** Choose option A or B for Quayside. Confirm whether the other two partners follow the same path. |
| Week of 9 Nov | Contract schema reviewed and frozen (v1). Quayside's data mapping agreed (their status codes to your enum). |
| Weeks of 16 and 23 Nov | A: ingestion API and `shipping` subgraph built. B: Quayside builds their subgraph against staging, and CI checks wired. |
| Week of 30 Nov | Staging integration with real Quayside data. Load test. Security review. |
| Week of 7 Dec | Production rollout behind a feature flag or schema-level flag, enabled for a small customer cohort. Kill-switch rehearsal. |
| By ~14 Dec | General availability, then change freeze. Watch the dashboards. |

Option B adds work in the middle: SLA negotiation, security review and pipeline setup. If your freeze is any earlier than mid-December, option B for Quayside is unlikely to fit.

## 5. Rollout order for the three partners

1. Quayside first (biggest volume, most pressure).
2. The other two partners onboard against the same contract after Quayside has run in production for at least a week. Don't onboard all three in the peak window.
3. Anything the partners disagree on goes into a v2 contract after January.

## Open questions

These change the plan, so I'd resolve them first:

1. **Can Quayside push webhooks or call a REST API today?** If yes, option A is clearly faster.
2. **When is your actual change freeze?**
3. **Which Apollo plan are you on?** GraphOS Enterprise or Free affects entity caching, contracts and operational limits.
4. **How is `Order` keyed?** Is `id` stable and known to Quayside, or do they only know a PO number?
5. **What are the partner SLAs and contract terms today?** Is a subgraph in the request path covered?
6. **What are the platform lead's reasons for option B?** If the motivation is to avoid building an ingestion API, option A's cost may be smaller than expected.