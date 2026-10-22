# Harbourline GraphQL launch readiness (8 weeks)

**Verdict:** all four items are launch blockers. Two of them are bigger than they look. The cost number can't just be reused for billing, and introspection is the right call only behind authentication.

**Start here:** pull one week of production query traffic and compute the real depth, cost and rows-per-request distribution. Every limit below should come from that data, not from the old proxy's preset.

## 1. Depth limit of 25

- The number is inherited, not derived. Depth is also a poor proxy for cost.
- A CRM graph is cyclic (Account → Contact → Account → Deals …). With 100 items per list, depth 4 already reaches about 10⁸ nodes.
- **Change:**
  - Set depth from the p99 of legitimate queries plus headroom. Expect roughly 8–12.
  - Add limits on aliases, root fields per request, query size in bytes, and total selected fields.
  - Require `first`/`limit` on every list, with a default (say 20) and a hard max (say 100).
  - Add a per-request execution timeout with context cancellation.
- Check what else the old "strict" proxy preset enforced besides depth: body size, timeouts, rate limits. Recreate those too, or they silently vanish.

## 2. Cost computed after the response

- Today it is a log line, not a control. Nothing stops an expensive query.
- **Change (enforcement):**
  - Compute cost statically before execution, from list-size arguments and field weights.
  - Reject queries over a per-query maximum.
  - Add a per-tenant and per-API-key budget, such as a cost-based token bucket. Don't limit by IP.
  - Reconcile with actual cost after execution, because the estimate over-counts short lists.
- Return the cost in `extensions.cost` (requested, actual, remaining budget) and in headers. Developers can't stay inside a budget they can't see.
- Use `429` for budget exhaustion and a typed `extensions.code` for per-query rejections. Error text must name the limit and its value.
- **Change (billing prerequisites):** don't commit to billing on this number until all of these hold.
  1. The formula is deterministic, versioned and documented. A weight change is a price change.
  2. Weights are calibrated to measured database load. Recalibrate after the N+1 fix (item 4), because actual cost shifts.
  3. You've decided whether you bill estimated or actual cost.
  4. Introspection and error responses cost zero.
  5. Customers get a usage view, and you run shadow invoices through the first months so there is no bill shock.
- Launch only needs enforcement and visibility. Billing can wait, but the formula must be frozen early enough that a year of data is comparable.

## 3. Introspection on for everybody

- Your DX lead is right that the playground is valuable. Keep it, but authenticated only.
- **Change:**
  - Disable introspection and the playground for unauthenticated requests.
  - Disable "Did you mean…" field suggestions in errors. They leak the schema even with introspection off.
  - Audit the schema before exposing it. Internal-only fields, admin types, unreleased features, and deprecated fields with names that reveal internals must be hidden or filtered per role and tenant.
  - Point the playground at a sandbox tenant by default, not production data.
  - Check that the standard introspection query passes your new depth limit. It nests about 7–13 levels, so a tight limit can break it. Exempt it from cost and cache it.
  - Publish the SDL as a docs artifact too. Introspection can't carry limits, rate budgets or a changelog.

## 4. N+1 on `Account.contacts`, `Contact.activities`, `Deal.notes`

- **Change:**
  - Batch each with a per-request DataLoader (`WHERE parent_id IN (...)`). Never share loader instances or caches across requests or tenants.
  - Keep tenant and authorization checks inside the batched query.
  - Paginate per parent. Use a window function or lateral join, because a plain `IN` with `LIMIT` caps the whole batch, not each parent.
  - Add a CI test that asserts the query count per GraphQL operation (for example, 3 queries for Account → Contact → Activity, independent of row count).
- Batching cuts round trips, not rows. The page-size caps and cost limits from items 1 and 2 are still required.
- Isolate the public API's database access with its own connection pool or a read replica, plus a statement timeout. One customer's heavy query shouldn't starve your first-party app.

## 5. Documentation

Nothing is documented today, so customers will find the limits by hitting them. Publish before launch:

- Every limit and its value: depth, aliases, page size, per-query cost, timeout, rate budget.
- How cost is calculated, with worked examples.
- Error codes and what to do about each.
- The response headers and `extensions.cost` fields.
- How to request higher limits.
- A policy for changing limits, such as notice period and changelog. This matters more once cost becomes a billing unit.

## 8-week sequence

1. **Weeks 1–2:** traffic analysis, set limits, decide the cost-model questions in item 2, schema audit.
2. **Weeks 3–4:** pre-execution cost, budgets, timeouts, introspection gating, DataLoaders and pagination.
3. **Week 5:** load test with a hostile query corpus (deep cycles, alias floods, huge `first`, introspection loops). Then run a mutation check: remove each limit and confirm a test fails.
4. **Week 6:** docs, error messages, usage view.
5. **Week 7:** beta with a few friendly customers, cost headers visible.
6. **Week 8:** launch, with alerts on rejections, budget exhaustion and query-count regressions.

## Decisions needed from you

1. **Estimated or actual cost for billing?** I recommend actual cost for billing and estimated cost for admission control, with both exposed.
2. **Same limits for first-party and public clients?** I recommend separate budgets, so your own app can't be throttled by customer traffic.
3. **Introspection for any valid API key, or only after signup verification?** I recommend any valid key, with rate limiting.