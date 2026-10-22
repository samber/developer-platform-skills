# Harbourline public GraphQL: what must change before launch

Eight weeks is enough if you start now. Four of your five items are blockers. The fifth, introspection, is a smaller change than your DX lead fears.

I haven't seen your SDL or any production queries. Numbers below are starting values. Items marked *(verify)* depend on answers I don't have. See "Open questions" at the end.

## Blockers

### 1. Cost scoring runs after the response. Move it before execution.

- A cost number logged after the response does no admission control. A hostile or careless query has already run.
- Run the cost analysis statically, after parse and validation and before any resolver runs. Reject over-budget queries with no work done. Shopify does this.
- Price lists by `first` (or `last`) times the child cost. The page-size cap is the multiplier.
- Weight mutations far above reads. Shopify uses 10x.
- Return the computed cost to the caller, for example in response `extensions`. Integrators then self-regulate instead of finding the ceiling through rejections.
- Cost-scoring mechanics (formula, budget per window, headers) belong to `api-rate-limit-policy`. You own the ceiling and the fact that it is checked before execution.

### 2. Billing on the cost number next year: fix the contract this year.

- A bill needs a number the customer can predict and reproduce. A number computed after the fact and invisible to them gets disputed.
- Publish the formula in the docs at launch, and return the cost in every response.
- Treat the formula as part of the API contract. Changing it later changes what customers pay, and Hyrum's Law applies. Version it or give notice periods. `api-versioning-policy` owns that.
- Run launch as observe-then-bill. Collect a year of real cost distributions while the pre-execution cap enforces limits. Set prices from that data.
- Do not bill on a number you have only ever logged. It has never been used to reject anything, so you don't know it is accurate.
- Check that the model prices what actually hurts. N+1 resolvers (item 4) make real DB cost diverge from the cost score. Fix the divergence first, or customers pay for queries that are cheap in practice.

### 3. Depth limit 25 comes from an old proxy preset, not from your schema.

- The skill's starting ranges are 5-7 levels for a simple API and 7-10 for a complex one. A public surface sits at the low end and raises only with a written justification per raise. 25 is far outside that.
- Proposal: set the default at **7**. Replay 5-10 real production queries and your first-party app operations. If a legitimate query needs more, raise to **10** with a written reason. Do not exceed 10 at launch.
- Enforce at parse time, before any resolver runs. Depth alone doesn't stop a wide, shallow query, so add:
  - A page-size cap: clamp `first` to a documented maximum (start at 100).
  - A cap on aliases per operation.
  - A cap on root fields per operation.
  - A cap on batched operations per request.
- Starting values for the alias, root-field and batch caps need real queries to tune. The skill gives no numbers for them.
- A relational CRM has deep natural paths (`Account → Contact → Activity → …`). That is a reason to check each raise, not to default to 25. Two or three deep paths can get a documented exception only if a real customer query needs them.

### 4. N+1 on `Account.contacts`, `Contact.activities`, `Deal.notes`

- One lookup per parent object is a must-fix finding. It has the same severity as a missing pagination cap.
- Fix with a per-request batching loader (DataLoader pattern) on each of the three fields.
- These are list fields, so a loader alone is not enough. Check three things:
  - Each field must be a Relay cursor connection (`first`/`after`, `pageInfo`, documented cap). A bare list field cannot be paginated later without a breaking change.
  - Batching a paginated child list needs a per-parent limit. Use a window function (`ROW_NUMBER() OVER (PARTITION BY parent_id …)`) or an equivalent query. A single `WHERE parent_id IN (…) LIMIT n` is wrong.
  - Cursors need an indexed sort key such as `(account_id, created_at)`. Without the index, the cursor query degrades to a full scan.
- Chained, the three fields multiply: `Account.contacts` × `Contact.activities` × 100 items each. Depth and cost limits bound the multiplication. Batching removes the per-parent round trips. You need both.
- Grep every other relationship field for the same pattern. Three found by hand is rarely the full set. Add a test that counts DB queries per request and fails when the count scales with parent count.

### 5. No limit is documented anywhere

- A ceiling that exists but is undocumented is discovered through production failures. For a third-party developer that is the worst onboarding experience you can ship.
- Document at launch:
  - Depth ceiling.
  - Page-size cap.
  - Alias, root-field and batch caps.
  - Cost formula and per-request cost cap.
  - The exact error a violating query receives, for each ceiling.
  - How the returned cost value is read.
- Do the reverse check too: a ceiling documented but not enforced fails the same gate.

## Smaller change: introspection

- Your DX lead is right that the playground is your best documentation. The skill's rule is: introspection off for anonymous production callers, on for development and authenticated tooling.
- Your customers' developers hold credentials, so the playground can stay on for them. Only anonymous callers lose introspection.
- Treat the schema as documentation you publish on purpose:
  - Audit every `"""docstring"""` for internal system names, table names or team names. Every schema reader sees them.
  - Publish a generated SDL and field reference on the docs site, so introspection is not the only copy.
  - *(verify)* If anonymous callers can reach the endpoint today, add authentication or shut introspection for them before launch.
- Add a check that an unauthorized field behaves the same whether or not the underlying resource exists. If it nulls in one case and errors in the other, the response shape tells an attacker which records exist. In a CRM, that exposes whether a given contact exists.

## Not in your list, but they gate launch too

- **GraphQL-or-not gate:** the default for a public API is REST. Confirm a trigger holds: multiple client types needing different shapes of the same data, or nested variable data with many round trips. A CRM with `Account → Contact → Activity` nesting plausibly qualifies. Name the trigger in the design record. If a public REST API exists, share one global ID across both, as GitHub does with `node_id`.
- **Persisted queries:** no allowlist for third-party traffic. Their queries are unknown in advance, and a blanket allowlist would reject every legitimate query on day one. An allowlist is fine for your own first-party apps. Third parties rely on the ceilings above.
- **Error surface:** use the hybrid split. Top-level `errors` for server faults and auth. Union result types for expected mutation outcomes, such as `CreateDealResult = CreateDealSuccess | ValidationError | …`. Adding a union to a shipped field is a breaking change, so do this before launch.
- **Nullability and shape:**
  - `[Type!]!` for lists.
  - Object references, not `contactId`.
  - A `Node` interface on every entity.
  - A dedicated `input` and payload type per mutation, with nullable payload fields.
  - Business-action mutation names, not a monolithic `updateDeal`.
  - Pick verb-first or noun-first and enforce one.
- **Federation (if used):** only the router is public. A reachable subgraph leaks its schema through `_service { sdl }` and bypasses access checks through `_entities`. Probe every subgraph from outside the private network and expect connection failure.
- **Evolution:** record the deprecation stance (`@deprecated` on one live schema, or date versions as Shopify does) before launch, because integrators rely on it. `api-versioning-policy` owns the policy.

## Launch gates (all must pass)

1. Depth ceiling documented, enforced at parse time, with a test for the documented error.
2. Page-size cap documented and enforced on every list field. Every list that can grow is a cursor connection.
3. Cost analysis runs before execution, rejects over-budget queries, and returns the cost to the caller.
4. Query-count test: `Account.contacts`, `Contact.activities`, `Deal.notes` and all other relationship fields issue a constant number of DB queries regardless of parent count.
5. Every ceiling and the cost formula appear in the public docs with the exact rejection error.
6. Anonymous introspection off. Docstrings contain no internal names.
7. Every mutation returns a payload or result type that can carry expected business failures.
8. One casing scheme and one mutation-naming order across the schema.
9. Federation only: every subgraph unreachable from outside, verified by probe.

## Suggested order for the eight weeks

1. **Weeks 1-2:** fix the N+1 resolvers and paginate those three fields. Write the query-count test. Replay real queries to size depth and caps.
2. **Weeks 2-4:** build pre-execution cost admission control and set depth, alias and page-size ceilings. Lock the cost formula's published form.
3. **Weeks 4-6:** error unions, nullability and ID fixes, introspection policy, docstring audit.
4. **Weeks 6-8:** publish the ceilings and formula in the docs. Run the gate checklist. Add rejection-rate monitoring for the first weeks after launch.

Doing the schema-shape changes (pagination, error unions) early matters most, because they are breaking changes after launch.

## Open questions

These change the numbers above, not the direction.

1. Is this retrofit or greenfield? Can you share the current SDL and 5-10 real production queries?
2. Are the consumers third-party only, or first-party and third-party on one endpoint?
3. Does a public REST surface exist, and must objects be addressable from both?
4. Is federation in use, or is the schema owned by one team?
5. Which fields, type names and error shapes do early customers already query? Anything observable is contract.
6. Is eight weeks a hard date? Is this the platform's primary API for years, or a first release?
7. Can anonymous callers reach the endpoint today?