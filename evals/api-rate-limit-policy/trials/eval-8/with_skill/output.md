# Tessellate GraphQL Admin API: rate-limit policy to publish

The plan has three rules that would break in production. The first two fix the plan's headline mechanics, and the third is a smaller fix.

| Your plan | Problem | Published rule |
|---|---|---|
| Measure cost after execution from response size | The server can't refuse an expensive query before it runs, and the integrator can't price a query before sending it. | **Pre-charge** a static estimate, run the query, then **refund** the difference to the actual cost. Reject before execution if the bucket can't cover the estimate. |
| Max cost per query scales with plan | A query written against a Premium store fails on a Standard store. Shopify avoids this with one cap for all plans. | **One per-query cap for every plan**, checked on the estimated cost. Plans scale the bucket, not the cap. |
| Mutations cost the same as queries | Writes cost the server far more than reads of the same shape, and the same price invites bulk-write loops. | Mutations carry a **fixed base cost of 10** plus the cost of their returned selection. |

Everything below is the publishable policy. The numbers are my proposals, since no industry threshold exists for them. Calibrate them in the observe phase (section 8).

## 1. Metering model

- The GraphQL Admin API is metered in **cost points**, never in request counts. If you ship a REST surface later, it gets a separate request counter and a separate budget. The two models never blend.
- The limiter keeps one bucket per **app installation × merchant account**.
  - One app can't drain another app's budget.
  - One merchant's traffic can't drain another merchant's budget.
- Idle time banks capacity up to the bucket depth. Describe the behavior in the docs, not just the name. Under this model, the bucket depth is the burst allowance and the restore rate is the sustained rate.
- The published limit applies **globally per bucket**, not per region. If the limiter enforces per region, real throughput becomes the limit times the number of regions. Confirm this with engineering before publishing (see open questions).

## 2. Cost formula

| Field type | Cost |
|---|---|
| Scalar, enum | 0 |
| Object | 1 |
| Connection (`first`/`last` = N) | 2 + N × (cost of one node's selection) |
| Interface or union | the most expensive possible selection |
| Mutation | **10** + cost of the returned selection |

- `first`/`last` is required on every connection, in the range 1–100.
- Tessellate reserves the right to set manual per-field weights, and publishes any such weight in the schema docs.
- Structural guards (depth ceiling, total-node ceiling, persisted queries) are schema design, covered by `public-graphql-api-design`. This policy only prices and meters.

**Worked example: a query**

```graphql
products(first: 50) { nodes { id title variants(first: 10) { nodes { id price } } } }
```

- `variants` costs 2 + 10 × 1 = 12.
- Each product node costs 1 + 12 = 13.
- `products` costs 2 + 50 × 13 = **652** estimated.
- If the query returns 3 products with 2 variants each, the actual cost is 2 + 3 × (1 + (2 + 2)) = **17**. The refund is 635.

**Worked example: a mutation.** `productUpdate { product { id } }` costs 10 + 1 = **11**. The base 10 is not refunded once execution starts.

## 3. Accounting: pre-charge, then refund

1. **Estimate.** Compute the static worst-case cost from the arguments (`requestedQueryCost`).
2. **Admit or reject.** Reject before execution if the estimate exceeds the per-query cap (section 4) or the bucket's available points. Nothing runs and nothing is charged.
3. **Execute.** Deduct the estimate before running.
4. **Settle.** Compute `actualQueryCost` from what was returned, then refund the difference. Actual cost never exceeds the estimate.

Return the accounting in every response, in `extensions.cost`:

```json
{
  "requestedQueryCost": 652,
  "actualQueryCost": 17,
  "throttleStatus": { "maximumAvailable": 2000, "currentlyAvailable": 1983, "restoreRate": 100 }
}
```

- Offer a debug flag (for example `Tessellate-GraphQL-Cost-Debug: 1`) that returns a per-field cost breakdown.
- Offer a zero-cost introspection field for the live budget. GitHub's `rateLimit { limit cost remaining resetAt }` is the model.

## 4. Tier table

| | Standard | Premium ($800/mo) | Enterprise / partner |
|---|---|---|---|
| Burst (bucket depth) | 1,000 points | **2,000 points** | by process (section 7) |
| Sustained (restore rate) | 50 points/s (180,000/hr) | **100 points/s (360,000/hr)** | by process |
| **Max estimated cost per query** | **1,000** | **1,000 (same)** | **1,000 (same)** |
| Mutation base cost | 10 | 10 | 10 |
| Concurrent in-flight requests | 10 | 20 | by process |
| Keyed on | app × account | app × account | app × account |

- Burst and sustained are two separate numbers. A single blended figure breaks scheduled reports and webhook fan-out.
- The plan changes the bucket depth, the restore rate and the concurrency allowance. It never changes the per-query cap.
- Premium buys throughput. A Premium merchant who needs a large read paginates or uses a bulk path. Consider a separate bulk-operation endpoint class with its own allowance for expensive reads, so they don't compete with the general bucket.
- Say plainly that the numbers are operational hints, not an SLA.
- State whether a higher plan implies higher limits. Here it does, automatically, for the bucket and restore rate. It does not for the per-query cap.

## 5. Fairness and the secondary guard

- Layers, outermost first:
  1. The tenant ceiling is the bucket above.
  2. If a merchant has several apps, each app has its own bucket.
  3. The concurrency cap in the table is a secondary guard.
- **Document the concurrency guard.** Publish what triggers it and how it signals, so no caller finds it by tripping it. When it trips, return HTTP 429 with `extensions.code: CONCURRENCY_LIMITED` and a `Retry-After`.
- Say in the policy that load shedding exists. Under platform-wide stress, a well-behaved caller can be shed even with budget remaining.
- Internal fairness machinery (queues, weighting) is not published. Publish only what a caller can observe.

## 6. Throttle response and headers

| Situation | Response |
|---|---|
| Estimate ≤ cap, estimate > available points | **HTTP 429**, `Retry-After: <delay-seconds>`, error code `RATE_LIMITED`, `extensions.cost` with `requestedQueryCost` and `throttleStatus`. |
| Estimate > per-query cap | **HTTP 400**, error code `MAX_QUERY_COST_EXCEEDED`, `requestedQueryCost` and the cap in `extensions`. Not retriable, because waiting never helps. |
| Concurrency cap hit | **HTTP 429**, `Retry-After`, error code `CONCURRENCY_LIMITED`. |

- `Retry-After` = ceil((requestedQueryCost − currentlyAvailable) ÷ restoreRate), in delay-seconds. It tells the caller when the bucket can cover the query, so it is accurate.
- ⚠️ **Never return a throttle inside HTTP 200**, as Shopify's `THROTTLED` and GitHub's primary GraphQL limit do. A client that only checks status codes would read it as success. Pre-charging makes this possible, because the request is rejected before any partial result exists.
- The 429 body uses the API's standard error envelope (see `api-error-design`). Don't invent a rate-limit-specific format.
- Headers: ship the legacy trio by default, on every response.
  - `X-RateLimit-Limit` is the bucket depth.
  - `X-RateLimit-Remaining` is the current points.
  - `X-RateLimit-Reset` is **seconds until the bucket is full**. Document this semantics explicitly and never change it silently.
  - Add the IETF `RateLimit` and `RateLimit-Policy` fields later only if your edge emits them cheaply. Never ship them alone.
- Headers are advisory. "500 remaining" does not promise that 500 points of queries will succeed.
- Client guidance to publish:
  - Honor `Retry-After`. Detect both delay-seconds and HTTP-date forms and clamp to ≥ 0.
  - Back off exponentially with jitter.
  - Hammering while throttled may lead to suspension of the integration.
  - Retry and idempotency mechanics belong to `api-idempotency-retry`.

## 7. Override path

- Standard to Premium is plan-gated and automatic. Above Premium, the limit is set by process, not by a published number.
- Overrides go through support or the account manager and are keyed to the app installation and account, never a person.
  - **Temporary increase:** request at least 24 hours ahead, naming the app, the account, the target points/s and the dates.
  - **Permanent or large increase:** at least 6 weeks of lead time.
- **No override raises the per-query cap of 1,000.** Say so in writing, so integrators never write queries that only work on overridden accounts.
- Tessellate may lower any override for platform stability.

## 8. Change-notice policy

- Limit changes don't bump the API version. A written notice policy is therefore the only thing that forces communication.
- Treat changes to field weights, mutation base cost and the cost formula as limit changes. They move effective limits as much as budget changes do.
- **Rollout of the first limits:** observe (log real cost, no enforcement), then baseline (enforce at a high ceiling), then refine (tighten from observed data). Announce before each tightening.
- Notice for reductions: at least 6 weeks, matching the lead time for large increases. Emergency reductions for stability are reserved in writing.
- Never change reset semantics silently. That change alone warrants a major announcement.
- Version the policy document alongside the API.

## Check before you publish

- ✅ **Machine-readability:** 100% of throttles carry a documented signal (429 with `Retry-After`, or a documented error code). No throttle path returns 200.
- ✅ **Docs match enforcement:** every number above equals the enforced configuration, in both directions. The concurrency guard is documented.
- Baseline these in your first month:
  - the 429 rate per tier
  - the share of 429s retried inside the `Retry-After` window
  - the number of limit-related support tickets
  - the number of override requests per quarter. Persistent volume means the tiers are too low.

## Assumptions and open questions

I couldn't ask these, so I assumed the answers. Each one changes a number above.

1. **Tiers:** I assumed only Standard and Premium exist, plus an Enterprise process. If there is a free tier, it needs the tightest bucket and its own key.
2. **Regions:** I assumed one global bucket per key. If you enforce per region, publish the scope or fix the limiter.
3. **Abuse pressure:** I assumed mostly well-behaved integrations. Adversarial traffic would promote a sliding-window secondary guard.
4. **Noisy neighbors:** I haven't seen one customer degrade others. If that has happened, the fairness layers in section 5 become a priority.
5. **Gateway capability:** I assumed it can compute the static estimate before execution. If it can't, the pre-charge model needs engineering work first. Settle that before you publish.
6. **Deadline and effort:** I assumed a durable policy, not a one-off fix.