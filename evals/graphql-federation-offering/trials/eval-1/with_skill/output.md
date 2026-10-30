**Don't onboard Quayside's subgraph into the supergraph. Ship a platform-owned `Order.shipments` field that all three partners write into through an API.**

Next action: confirm the three assumptions in section 1, then start on the ingest API (section 4).

## 1. Assumptions

You didn't answer the skill's interview, so I assumed the answers below. If one is wrong, the design changes where noted.

- **Partner count and terms:** 3 partners, all under contract, none self-serve.
- **Data flow:** updates flow from partner to you. Nobody needs to compute a tracking status live inside a client query. If a live ETA is required, see section 7.
- **Visibility:** buyers see tracking only on their own orders.
- **Data the partner needs:** the order ID and the shipping address already held by the fulfilment flow. No new personal data goes to the partner.
- **Stack and SLA:** Apollo Router with GraphOS, 6 internal subgraphs, client latency SLA unknown.
- **Deadline:** live before January peak, one-off integration with 3 partners.

## 2. Classification (workflow step 1)

| Partner ask | Shape | Rung |
| --- | --- | --- |
| Tracking number, carrier name | Stored data on `Order` | 1 or 2 |
| Status updates as the parcel moves | Events pushed into storage | 0 plus 2 |
| Live ETA computed by the partner | Live data | Not requested. Ask before assuming. |

"Put tracking on our Order type" is stored data plus events, which never needs a partner resolver. You already have a canonical type for it: a shipment. That puts it at **rung 2**, a platform-ingested connector into canonical types. Rung 0 webhooks tell partners when to ship.

Ranking for the rungs left standing (0, 1, 2):

- **Efficiency:** `app-owned extension data > webhooks plus callback > ingested connector`
- **Effort, highest first:** `ingested connector > app-owned extension data > webhooks plus callback`
- **Value (live partner data in one query):** `ingested connector == app-owned extension data > webhooks plus callback`
- **Compliance cost, highest first:** `ingested connector == app-owned extension data > webhooks plus callback`
- **Durability:** `webhooks plus callback == app-owned extension data > ingested connector`

Rung 2 beats rung 1 here because a canonical `Shipment` type exists, and three partners sync into it. The January date (interview answer 7) moves nothing. It only promotes rung 3 for live data, and this need is stored.

## 3. Why not Quayside's subgraph

You already run federation, but that tooling assumes every subgraph author is a trusted team inside your organisation. With a partner author, composition still validates the schema but no longer protects you.

- **Nothing stops a partner from claiming platform fields.** Composition accepts `@override(from:)` on `Order.total`, `@provides` on `Customer.email`, and `@shareable` on a platform type like `Money`. All compose cleanly and all ship.
- **Quayside's endpoint sits in the request path of every `Order` query.** A Quayside stall during peak degrades your core ordering API. Apollo Router's per-subgraph timeout defaults to 30 s and it has no native circuit breaker.
- **A non-null partner field blanks the whole `Order`.** One Quayside error nulls the order the buyer asked for.
- **Quayside's endpoint is a public URL.** Anyone can post `_entities` keys and enumerate order data unless it authenticates every call.
- **Header propagation can leak buyer credentials.** A catch-all propagation rule would send a buyer's `Authorization` or `Cookie` to Quayside.
- **Offboarding is a breaking change.** Removing the subgraph deletes public fields that clients query.
- **No precedent.** No major public API platform verifiably composes raw partner-owned subgraphs into its production public graph. Shopify, Atlassian, Hasura and Hygraph all keep schema ownership.

Composing partner subgraphs into your first-party production supergraph is not a rung on the extension ladder. Refuse it for all three partners.

## 4. Design: platform-owned `Shipment`

### Schema

This lives in whichever existing subgraph owns fulfilment. Partners never touch SDL.

```graphql
type Order @key(fields: "id") {
  id: ID!
  shipments: [Shipment!]!
}

type Shipment {
  id: ID!
  trackingNumber: String!
  carrierName: String!
  status: ShipmentStatus!
  events(first: Int, after: String): ShipmentEventConnection!
}

enum ShipmentStatus {
  LABEL_CREATED
  IN_TRANSIT
  OUT_FOR_DELIVERY
  DELIVERED
  EXCEPTION
}
```

You define the status enum, and each partner's codes map onto it. Adding an enum value is a breaking change for clients with exhaustive switches, so hand it to your versioning policy.

### Partner ingest API

Use a partner-facing REST API, not a mutation on the public buyer graph.

1. `POST /partner/v1/shipments` creates a shipment with order ID, tracking number and carrier name.
2. `POST /partner/v1/shipments/{id}/events` appends a status event with a partner event ID, timestamp, status code and optional location.
3. The partner event ID is the idempotency key. Handle out-of-order events by timestamp.
4. Map each partner code to your enum in a per-partner mapping table that you own.

### Credentials and authorisation

- **Per-partner machine credential:** OAuth client credentials with a `shipments:write` scope.
- **Orders assigned to that partner only:** write access is checked against the carrier assignment recorded at order allocation. Quayside cannot write to a Fernhill order assigned to another carrier.
- **Rate limit per partner.**

### Partner input is untrusted

Treat partner text like user input. Cap lengths, strip markup, and show buyers your mapped status, not raw partner strings. Don't pass partner error messages through to clients.

### Rung 0: webhooks to partners

Send a signed `order.shipment_requested` webhook so each partner knows when to ship and post tracking back.

## 5. Who sees what

- **Buyers:** `Order.shipments` follows the existing order authorisation. A buyer sees only their own orders. There is no "installed partner" concept because partners never appear in the graph.
- **Partners:** each sees only its own shipments, through the partner API.
- **Docs:** mark `Shipment` fields as data supplied by the carrier.

## 6. Lifecycle

1. **Publish:** there is no partner schema to publish. Partner onboarding is credentials, a sandbox, and a conformance run of fixture events through the status mapping. Go-live is gated on that run passing.
2. **Platform changes:** any breaking change to the partner API, or to the enum, follows your versioning policy with a notice window.
3. **Observe per partner:** event volume, rejection rate, event lag (partner timestamp to ingest), and a staleness alert for shipments with no event for N days.
4. **Offboard:** revoke the credential. Shipment data stays in your storage, and no graph field disappears.

## 7. If a partner needs live data

If a partner truly needs live data in the buyer's query, such as a live ETA that you can't store, reclassify it. Don't promote the rung.

1. **Rung 3 first.** Your platform maps Quayside's existing tracking API under a `Quayside_` namespace. You write the schema, mint a per-request token, set a timeout from the client SLA, add a circuit breaker through an egress proxy, and validate the routing URL against SSRF. Quayside needs no federation engineering.
2. **Rung 5 only if all three hold.** The need is live entity data a single mediated field can't shape, the partners are few and under contract (yours are), and you can staff partner schema review as a standing job. Even then, it goes in an isolated partner variant behind its own router, never the first-party supergraph. You would need a blocking policy check on every publish and no publish rights for partners. It would also need nullable-only fields, an allowlisted `Order` key, and a data-clearance list. This will not be ready before January.

## 8. Timeline

These are my estimates, not skill output. Check them against your team's capacity.

- **Now to about Nov 13:** `Shipment` schema, ingest API, partner credentials, status mapping, webhook.
- **Nov 16 to Nov 27:** Quayside in sandbox, fixture conformance run. Start the other two partners in parallel.
- **About Dec 1:** Quayside live on production, with 3 or more weeks of soak before peak.
- **Freeze:** pick a freeze date before peak and put it on the board.

## 9. Acceptance gates

Each gate is binary. Iterate the design until all pass.

- **Order isolation:** a Quayside credential posting an event for an order assigned to another carrier is rejected.
- **Credential isolation:** a call with no credential, or another partner's token, is rejected.
- **Buyer visibility:** a buyer querying another buyer's order gets no `shipments`.
- **Idempotency:** replaying the same partner event ID twice creates one event.
- **Outage drill:** with Quayside's ingest down, `Order` queries return full data within the SLA, because Quayside is not in the request path.
- **Offboard drill:** revoking the Quayside credential leaves existing shipment data readable.

## 10. Selling this to your platform lead

- **Lead's goal:** reuse the federation tooling for logistics partners.
- **What they keep:** the six-subgraph router, the registry and the contract tooling all stay as they are.
- **What changes:** one more platform-owned subgraph field, plus an API the partners write to.
- **What they avoid:** a partner outage during January peak degrading `Order` for every buyer.

Questions that would change the design:

1. Do any of the 3 partners need live computed values in the buyer's query? That is section 7.
2. Does a shipment or fulfilment entity already exist in one of the 6 subgraphs?
3. Can all three partners call a REST API, or does one only speak EDI or file drops?