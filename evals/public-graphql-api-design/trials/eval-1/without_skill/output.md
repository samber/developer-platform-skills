# Where to start on the Kettleworth GraphQL schema

**Start with the requirement, not the schema.** Your numbers make GraphQL the weaker fit for the public API, and a schema built before that is settled will probably be rework. I haven't seen your API or traffic data, so everything below rests on what you described.

## Step 0: Decide what the GraphQL API is for (about 1 week)

Four facts in your description matter here:

- **Flat, three-resource data.** GraphQL's main win is fetching nested graphs in one round trip. You have little nesting, so there is little to save.
- **70% of traffic is served by the CDN.** Standard GraphQL is a single `POST /graphql`, which the CDN can't cache. Without extra work, that 70% lands on origin.
- **About 40 partners poll.** Polling is a sync problem. It is better solved by an `updatedSince` filter or by webhooks than by a query language. Those fixes work in REST too.
- **One first-party client.** There is no mobile or web client team asking for flexible queries.

Run these checks before committing:

1. **Ask the CTO what outcome they want.** Examples are partner DX, fewer round trips, a modern-API story, or AI-agent friendliness. Each leads to a different design.
2. **Ask 5–8 partners** what hurts today. Don't ask whether they want GraphQL.
3. **Pull the data.** Get the top endpoints by origin traffic, the most common partner call chains, and any N+1 patterns, such as "list shipments, then fetch scan events for each".
4. **Model the origin load** if the CDN-cacheable share drops from 70% to X%. This is the number that will persuade people.

**My recommendation:** ship GraphQL as an additive second surface and keep REST. Don't replace it. The 40 integrators already work, and a forced migration would cost you partner goodwill for no measurable gain. Position GraphQL for partners who want to batch shipments with scan events. If step 0 shows no real demand, say so, and offer the CTO a smaller fix: add `include=scanEvents`, `updatedSince`, and webhooks to REST.

## Step 1: Design from partner jobs, not from tables

Write 5–10 concrete use cases first. For example:

- Track one shipment with its full scan history.
- Sync everything changed since my last poll.
- List a carrier's active shipments.
- Look up a shipment by tracking number.

Every Query field must trace back to one of these. Don't mirror REST endpoints one for one.

## Step 2: Schema skeleton (starting point, not final)

```graphql
scalar DateTime   # ISO 8601, always UTC

interface Node { id: ID! }   # opaque global ID

type Shipment implements Node {
  id: ID!
  trackingNumber: String!
  status: ShipmentStatus!
  carrier: Carrier!
  createdAt: DateTime!
  updatedAt: DateTime!
  scanEvents(first: Int = 20, after: String,
             orderBy: ScanEventOrder = OCCURRED_AT_DESC): ScanEventConnection!
}

type Carrier implements Node {
  id: ID!
  name: String!
  shipments(first: Int = 20, after: String,
            filter: ShipmentFilter): ShipmentConnection!
}

type ScanEvent implements Node {
  id: ID!
  type: ScanEventType!
  occurredAt: DateTime!
  location: String
  shipment: Shipment!
}

input ShipmentFilter {
  status: [ShipmentStatus!]
  carrierId: ID
  updatedSince: DateTime   # the polling-replacement field
}

type Query {
  node(id: ID!): Node
  shipment(id: ID!): Shipment
  shipmentByTrackingNumber(trackingNumber: String!): Shipment
  shipments(first: Int = 20, after: String,
            filter: ShipmentFilter): ShipmentConnection!
  carriers(first: Int = 20, after: String): CarrierConnection!
}
```

`*Connection` types follow the Relay shape: `edges { node cursor }`, `pageInfo`, and `totalCount` only if it is cheap.

## Step 3: Decisions to make explicitly

| Topic | Recommendation |
|---|---|
| **Pagination** | Cursor connections everywhere. Hard cap `first` at 100. Never offset pagination. |
| **Incremental sync** | `updatedSince` filter with a stable sort order. Consider webhooks or a subscription for scan events. |
| **Enums** | Treat `ShipmentStatus` and `ScanEventType` as open-ended. Adding values is non-breaking in the schema but breaks naive clients, so document it. |
| **Nullability** | Be deliberate. Non-null that later becomes null is a breaking change. Default optional for anything partner-sourced, such as `location`. |
| **Mutations** | You didn't say whether the API writes. If it does, use `input` objects and payload types with typed errors (a union or an `errors` field), not just top-level GraphQL errors. |
| **Versioning** | None. Evolve additively and mark old fields with `@deprecated(reason:)`. Track field usage so you know when removal is safe. |
| **Auth** | Authorize per object, not per endpoint. A partner must see only their own shipments, and this is easy to miss with a graph traversal. |
| **IDs** | Opaque global IDs, decoupled from database keys. |

## Step 4: Plan the non-schema work now

These items take more of the Q3 timeline than the SDL does:

1. **CDN caching.**
   - Use persisted queries sent as `GET` with a hash.
   - Set `Cache-Control` per response, using `@cacheControl` hints and the minimum `maxAge` across selected fields.
   - Confirm your CDN caches GET on a query string.
   - Without this, you give up the 70%.
2. **Abuse limits.** Set query depth and complexity limits and cost-based rate limiting. Consider an allowlist of persisted queries for the public API. This is the main new risk for a public endpoint.
3. **N+1 control.** Use DataLoader-style batching on `scanEvents`, `carrier`, and `shipment`.
4. **Observability.** Track per-operation latency, error rate, and cost, since the URL no longer tells you what was called. Name your operations.
5. **Docs and DX.** Publish the schema, an explorer, and example queries for the real partner jobs. Include a REST-to-GraphQL mapping table.
6. **Migration stance.** State publicly that REST stays supported, with no sunset date unless you choose one.

## Questions I'd want answered first

1. What does the CTO want GraphQL to achieve?
2. Does the public API accept writes, or is it read-only?
3. Which "Q3" is it, and is it a hard date or a target?
4. Can your CDN cache GraphQL GETs (persisted queries)?
5. Do partners' integrations have a real need for push updates?
6. Do you want the ops dashboard to move to GraphQL as the dogfooding client?

## Suggested sequence

1. **Weeks 1–2:** run the step 0 checks and write the use cases.
2. **Weeks 3–4:** draft the schema with 3–5 pilot partners and prototype persisted-query GET caching.
3. **Mid-quarter:** load-test the origin with the new cache hit rate.
4. **Late quarter:** ship as beta, additive to REST, with the ops dashboard as the first client.

If the step 0 data shows no partner demand, the strongest result for the CTO may be a smaller REST improvement plus webhooks, with GraphQL kept as a later option.