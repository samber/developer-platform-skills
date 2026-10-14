# Tessellate GraphQL Admin API: rate limits to publish

I changed two of your three rules and tightened the third. The reasons are in section 1, and the numbers are in section 2.

## 1. Changes to the plan

| Your plan | Problem | What to publish instead |
|---|---|---|
| Measure cost only after execution, from response size | A client can run a huge query before you know its cost. Response size also misses the work done, since a filtered query that scans a million rows and returns 0 would cost 0. | **Estimate cost before execution** from the requested fields and `first`/`last` arguments. Reject the query if it is too big or the bucket is short. After execution, refund the difference between the estimate and the actual cost. |
| Premium gets a higher max cost per query | Large single queries are what hurt shared infrastructure, so you would be selling the riskiest behavior. | **One max cost per query for every plan.** Premium gets a bigger bucket, a faster refill and more concurrency, so it makes more queries, not heavier ones. |
| Mutations cost the same as queries | Mutations hit the primary database, take locks and trigger webhooks, emails and inventory events. | **Mutations cost more**: a base cost of 10, plus their input and payload. |

## 2. Numbers

These are starting values. I have no Tessellate traffic data, so validate them before publishing. Replay real REST or internal usage and check that your p99 legitimate query costs at most about 30% of the Standard bucket.

### Cost per field

| Item | Cost |
|---|---|
| Scalar or enum field | 0 |
| Single object (node) | 1 |
| Connection | 2 + (`first` or `last`) × cost of one node, including its nested fields |
| Interface or union | Cost of the most expensive branch |
| Mutation | 10 + payload selection (costed like a query) |
| Mutation with a list input | 10 + 1 per input item, with a maximum of 250 items |
| Expensive fields (aggregates, free-text search) | Surcharge, published in the schema with a `@cost` directive |

Every connection must have `first` or `last`, with a maximum of 250.

Worked example:

```graphql
products(first: 50) { nodes { id title variants(first: 10) { nodes { id sku } } } }
```

The cost is 2 + 50 × (1 + (2 + 10 × 1)) = **652 points**.

### Per-query ceilings, the same on every plan

| Limit | Value |
|---|---|
| Max cost per query | 1,000 points |
| Max page size | 250 |
| Max nodes per query | 10,000 |
| Max depth | 8 |
| Max aliases | 50 |
| Timeout | 10 s |
| Request size | 100 KB |

### Budget by plan

Each plan has a leaky bucket: it starts full, each query deducts its cost, and it refills continuously.

| | Standard | Premium ($800/mo) |
|---|---|---|
| Bucket size (burst) | 2,000 points | 10,000 points |
| Restore rate | 100 points/s | 500 points/s |
| Sustained throughput | 360k points/hour | 1.8M points/hour |
| Concurrent in-flight requests | 4 | 16 |

- **Scope:** the bucket applies per app and per account. One noisy app cannot starve another, and there is an account-level cap on top.
- **Mutation rate:** at the base cost, Standard sustains about 10 mutations per second and Premium about 50.
- **Premium's 5x** is a placeholder for the ratio you want to sell. The only hard rule is that every bucket stays larger than the 1,000-point query ceiling.

### Accounting rules

1. **Start check:** a query runs only if the bucket holds at least its estimated cost.
2. **Refund:** after execution, the cost drops to the actual cost based on nodes returned. The refund never takes the charge below 10% of the estimate. That floor covers scan work on queries that return little.
3. **Visible in every response:**
   ```json
   "extensions": { "cost": {
     "requestedQueryCost": 652, "actualQueryCost": 140,
     "throttleStatus": { "maximumAvailable": 2000, "currentlyAvailable": 1488, "restoreRate": 100 } } }
   ```

### Errors

| Case | Response |
|---|---|
| Bucket too low | HTTP 429, `Retry-After` header, error code `THROTTLED` |
| Query over 1,000 points, depth or node limits | HTTP 400, `MAX_COST_EXCEEDED`, with the cost breakdown. Do not retry. |
| Concurrency exceeded | HTTP 429, `TOO_MANY_CONCURRENT_REQUESTS` |

Prefer 429 over the GraphQL convention of HTTP 200 with an error body, because gateways and SDK retry logic understand it.

## 3. Rules to state in the docs

- **Bulk operations:** large exports go through an asynchronous bulk endpoint, outside the points budget, with 1 concurrent job per account. This is the answer to "my Premium customer needs bigger queries".
- **Efficiency:** request only the fields you need and use smaller `first` values. Estimated cost, not actual cost, determines whether a query can start.
- **Stability:** the cost table is versioned with the API. Cost changes ship only in a new version, with at least 90 days' notice.
- **No overage purchases:** points are a protection mechanism, not a billing unit. Customers who need more upgrade their plan or use bulk operations.

## 4. Before you publish

1. Replay real traffic against the cost model to validate bucket sizes.
2. Confirm any plans below Premium. I assumed a single "Standard" tier.
3. Decide whether the 5x Premium multiplier matches the pricing story.