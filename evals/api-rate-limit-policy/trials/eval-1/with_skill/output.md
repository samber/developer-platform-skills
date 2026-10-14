# Loamly public API: rate-limit policy (draft v0.1)

## Two changes to your brief

1. **"300 requests/min covering both surfaces" doesn't work.** A REST request and a GraphQL query have very different server cost. One GraphQL request can fetch one scalar or tens of thousands of nested nodes. Under one request counter, a partner could send "cheap" GraphQL requests that cost you 100× more than a REST call. The policy keeps one number, 300, as the ladder's base. The unit differs per surface: **requests** for REST and **cost points** for GraphQL. The docs stay simple because both budgets scale with the same plan multiplier.
2. **Plan multipliers are fine, with three conditions.**
   - Burst and sustained are two separate numbers.
   - Limits are enforced per organization, not only per key. Otherwise a customer can multiply their limit by creating keys.
   - Expensive endpoints get their own small budget, outside the general one.

The numbers below are proposals. Calibrate them against real per-endpoint cost before launch. Sections 5 and 8 list the open questions.

---

## What you will publish

### 1. Metering

| Surface | Unit | What the number means |
|---|---|---|
| REST | Requests | Each request costs 1. |
| GraphQL | Cost points | Each query is priced by the formula below. |

REST and GraphQL have **separate budgets**. Spending one does not reduce the other. They share only the concurrency cap in section 2.

**Algorithm: token bucket.** The sustained rate is the refill rate. The burst allowance is the bucket depth. Idle time banks capacity, up to the depth. Output is not smoothed.

**GraphQL cost formula**
- Scalar and enum fields cost 0.
- A query costs 1 for the root.
- Each connection field costs `ceil(first ÷ 100)`, minimum 1, for each parent object it runs under.
- A mutation costs 5, plus the cost of the fields it returns.
- Example: `warehouses(first: 10) { stockLevels(first: 50) }` costs 1 (root) + 1 (warehouses) + 10 (one stockLevels lookup per warehouse) = **12 points**.

**GraphQL accounting**
- The bucket must hold the query's estimated worst-case cost before it runs. Otherwise the request is rejected.
- After execution, the difference between estimated and actual cost is refunded.
- Every response reports `extensions.cost { requested, actual, remaining, restoreRate }`.
- `rateLimit { limit cost remaining resetAt }` is queryable at no cost.
- **A single query can never exceed 500 points, on any plan.** A query that works on Scale also works on Free.

### 2. Limits by plan

All limits are per **organization**. API keys in one organization share that organization's budget.

| | Free (1×) | Growth (5×, $49/mo) | Scale (20×, $299/mo) | Enterprise |
|---|---|---|---|---|
| REST sustained | 300/min (5/s) | 1,500/min (25/s) | 6,000/min (100/s) | By agreement |
| REST burst (bucket depth) | 600 | 3,000 | 12,000 | By agreement |
| GraphQL sustained | 300 pts/min | 1,500 pts/min | 6,000 pts/min | By agreement |
| GraphQL burst (bucket depth) | 600 pts | 3,000 pts | 12,000 pts | By agreement |
| Concurrent in-flight requests (REST + GraphQL combined) | 5 | 20 | 50 | By agreement |
| Bulk/export endpoint class | 10/min | 50/min | 200/min | By agreement |

- **Bulk/export class:** bulk import, bulk export, and report generation each get their own bucket. They don't spend the general REST budget, and the general budget can't spend them.
- **Per-key sub-limits:** an organization may cap individual keys inside its own allocation. This stops one integration from using the whole budget.
- **Scope:** limits are global per organization, not per region. *(Confirm this is how you enforce them. See open question 3.)*
- **Higher plan means higher limits** only as the table states. Enterprise limits are not automatic. They are activated in writing (section 6).
- **Load shedding:** under platform-wide stress we may shed traffic regardless of your own usage. Shedding order is test traffic, then reads, then writes. A well-behaved caller can therefore still see a 503 or 429 during an incident. *(Describe only what callers can observe.)*

### 3. Headers

Every API response carries the legacy trio:

```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 412
X-RateLimit-Reset: 1790000000
```

- `Limit` is the bucket depth for the surface you called.
- `Remaining` is the tokens left.
- `Reset` is a **UTC epoch timestamp in seconds** at which the bucket is full again. This definition will not change without a major announcement.
- On 429s we also send `Loamly-Rate-Limited-Reason`. Values are `rest_bucket`, `graphql_points`, `concurrency`, and `endpoint_class:<name>`, so you know which limit you hit.
- Headers are planning signals, not guarantees. "412 remaining" does not promise 412 successful calls.
- *Roadmap:* we may add the IETF `RateLimit` and `RateLimit-Policy` fields alongside the trio once the draft stabilizes. We will never remove the trio without notice under section 7.

### 4. When you are throttled

- **All throttles return HTTP 429 with a `Retry-After` header, on both REST and GraphQL.** This includes cost rejections on `/graphql`. A throttle is never returned inside an HTTP 200. Cost is checked before execution, so a rejected query returns no partial data.
- `Retry-After` is **delay-seconds** (for example `Retry-After: 12`). If it is present, it takes precedence over `X-RateLimit-Reset`.
- The 429 body uses our standard error envelope with code `rate_limit_exceeded`. GraphQL 429s use the same code in the GraphQL error `extensions`.
- Never cache a 429.
- **Client expectations:**
  1. Wait at least `Retry-After`.
  2. Back off exponentially with **jitter** on repeated 429s.
  3. Don't synchronize retries across workers.
  4. Parse `Retry-After` defensively and clamp it to ≥ 0.
- **Consequence:** an integration that keeps sending requests while throttled may have its key suspended.
- **Concurrency guard:** more than the plan's in-flight cap returns 429 with reason `concurrency`. Treat it like any other 429.

### 5. Increases, enterprise, and partners

- **Temporary increase** (a migration or a one-off backfill):
  - Open a support ticket at least **5 business days** ahead.
  - Name the organization, the key, the surface, the requested number, and the dates.
- **Permanent or large increase:** contact your account manager at least **6 weeks** ahead.
- **Enterprise:** custom limits are written into the order form. They are tied to your organization and API keys, never to a person.
- **Never overridden:** the 500-point single-query cap and the concurrency hard ceiling. Overrides raise budgets, not these guards.
- We may lower any override for platform stability.
- A published limit is an operational hint, **not an SLA**. A contract commitment must say so explicitly.

### 6. Change notice

- Limit changes are non-breaking and don't bump the API version.
- **Decreases to published plan limits:** at least **6 weeks'** notice by email to account owners, plus a changelog entry.
- **Increases:** announced in the changelog.
- **Emergency reductions** for platform stability may happen with less notice. We reserve this right.
- **Reset semantics or header definitions** never change silently. A change gets a major announcement of its own.
- New or tightened limits roll out in three phases: observe (log only), baseline (high ceiling), refine (tighten from real traffic). Affected callers are told before each tightening.

---

## Open questions

These feed the design. The numbers above assume the stated defaults.

1. **Free tier at 300/min:** is that deliberate? Free keys are the likeliest scraping target. Choosing a lower Free base would break the "300" headline, but would protect you. The alternative is a dedicated Free-tier abuse guard.
2. **Existing limits:** is anything enforced today? If so, send enforced versus documented numbers, because drift between them is the first thing to fix.
3. **Regions:** is the API served from more than one region? If limits run per region, the real ceiling is the limit times the number of regions, and the policy must say so.
4. **Abuse pressure:** is traffic mostly well-behaved partners, or scraped? Heavy abuse would justify a sliding window instead of the token bucket.
5. **Noisy neighbors:** has one customer ever degraded others? If yes, add per-user limits inside an organization's allocation and weighted sharing. If your engineering budget is tight, defer those until the first incident.
6. **Gateway capability:** can it count GraphQL cost points and emit the extra headers? Cost metering needs engine support.
7. **Pre-launch:** run the observe phase with logging only before enforcing. Measure real per-endpoint cost to decide the bulk class numbers and the 500-point cap.

## Acceptance gates

- 100% of throttle responses carry `Retry-After` and a documented machine-readable code.
- Zero drift between these published numbers and the enforced configuration. Secondary guards (concurrency, bulk class) must appear in both.
- From the first month, track the per-plan 429 rate, the share of retries that respect `Retry-After`, limit-related tickets, and override requests per quarter. If override requests stay high, the published tiers are set too low.