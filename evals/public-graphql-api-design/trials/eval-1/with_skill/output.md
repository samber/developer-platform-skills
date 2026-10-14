# Where to start on the schema: don't, yet

Start with the step 1 gate, not a schema. I read the skill and all four reference files. On the facts you gave me, the gate says to stop before schema work.

## 1. Gate verdict: no trigger fires, so stay on REST

The skill's default for a public API is REST. GraphQL has to earn its place against three triggers:

| Trigger | Your situation | Fires? |
|---|---|---|
| Multiple client types need different shapes of the same data | One first-party client (ops dashboard), plus about 40 partners polling the same flat resources | No |
| Nested, highly variable data that forces many round trips | Three flat resources, "no deep nesting anywhere" | No |
| Mobile or high-latency consumers where round trips dominate | Server-side polling integrators and an internal dashboard | No |

The skill gives Lee Byron's test for GraphQL: a "square-peg, round-hole problem" between server and clients. You don't have it.

The argument against switching is also stronger for you than for most teams. Your 70% CDN hit rate is the first reason the skill gives for REST winning. URL-keyed GETs cache at the CDN for free. On GraphQL's single POST endpoint you would have to rebuild that caching. Moving would trade away your main operational win and gain nothing in return.

Per the skill, the gate is a binary check against the trigger list. It doesn't rank GraphQL and REST by value or effort. The skill's exit for this case is to stop and hand the work to the REST-side skills. I therefore haven't produced SDL, pagination, error unions or ceilings. Any of that would be a design for an API the gate says you shouldn't build.

## 2. What to tell the CTO

Frame it as the gate's result, not a refusal.

- **The test is a consumer-mix question, not a preference.** GraphQL pays off when different clients need different shapes. You have one first-party client and 40 partners all polling flat data.
- **You would lose the 70% CDN offload.** To recover it you would need persisted queries (hash-identified GETs), which the skill treats as partial recovery of the gap, not parity.
- **You would take on a new public attack surface.** That means depth, breadth and cost ceilings, introspection policy, resolver batching, and a typed error surface. REST gives you most of this already.
- **Hybrid is a legitimate outcome.** The skill says offering both is a valid result of the gate. Keep REST as the stable cacheable surface and add GraphQL only where a trigger holds.
- **Persisted queries only work for your own clients.** The skill's persisted-query policy allowlists first-party traffic only. A closed allowlist can't work for third parties, because their operations aren't known in advance. So a public GraphQL launch would give your 40 partners the less protected path.

## 3. A cheap way to test the CTO's hypothesis

If the CTO believes a trigger exists that I can't see, find it with evidence before the Q3 launch.

1. **Check the partners.** Ask 5 to 8 of the 40 where REST hurts today. Look for N+1 call chains, over-fetching, or missing endpoints. Those are the signals that would fire trigger 1 or 2.
2. **Check the dashboard.** List its real call patterns. If it chains calls such as shipment, then carrier, then scan events, a GraphQL layer for that one first-party client is cheaper than a public API. It also gets the strict persisted-query allowlist, because you control the client. A dashboard BFF is out of this skill's scope; the surface-strategy sibling covers it.
3. **Write down the fired trigger.** If steps 1 and 2 find a real trigger, the gate flips and you design the schema. If they don't, you have your answer for the CTO in writing.

## 4. If the gate flips: the questions the skill requires first

I can't ask these interactively here. The answers decide the design, so settle them before any SDL.

1. Greenfield, or a retrofit with real production queries?
2. First-party only, third-party only, or both on one endpoint? Design for the third party if both are present.
3. Must objects be addressable from both REST and GraphQL? If yes, use one shared ID, as GitHub does with its REST `node_id`.
4. Is federation in play? With three resources and one team, almost certainly not. Keep a single schema, which avoids the subgraph exposure problem entirely.
5. What do partners already depend on in the REST shapes? Anything observable is contract, so the redesign maps old identities forward.
6. Is this a one-off surface or the primary API for years? That re-ranks the pagination and error-pattern choices.

## 5. Starting decisions if you proceed

If the gate flips, these are the schema defaults the skill would apply. They are not a design for you yet.

- **Types:** `Shipment`, `Carrier` and `ScanEvent`, all implementing `Node`. Use object references, not foreign keys, so `Shipment.carrier: Carrier!` rather than `carrierId`.
- **Pagination:** Relay cursor connections on every growing list, with a server-clamped `first` and a documented maximum. `Shipment.scanEvents` is the obvious growth field. Make `totalCount` nullable.
- **Casing and mutations:** PascalCase types, camelCase fields, SCREAMING_SNAKE_CASE enum values. Settle the mutation-naming fork (verb-first or noun-first) with the team and enforce it everywhere.
- **Errors:** union result types on every mutation, plus a shared `ErrorCode` enum.
- **Guardrails:** a documented depth ceiling at the low end of the skill's 5 to 7 range for public APIs. Add caps on page size, aliases and root fields, plus a pre-execution admission check. Introspection stays off for anonymous production callers.
- **Persisted queries:** a closed allowlist for the ops dashboard only. Partners get the guardrails, with optional persisted queries as a performance feature.

## Open question

If the partner check turns up a fired trigger, send it to me and I'll continue from step 2. Without one, the answer for the CTO is to stay on REST and keep the CDN offload.

One thing sits outside this skill. The skill covers GraphQL design only, so I haven't assessed whether polling is the right pattern for those 40 partners or whether webhooks would serve them better. The surface-strategy sibling skill (`api-integration-surface-strategy`) covers that.