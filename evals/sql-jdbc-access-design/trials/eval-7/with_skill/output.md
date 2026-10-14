# Vantridge SQL/JDBC access: what you'd be signing up for

**Short answer:** don't sign the proposal as written. It has two of the skill's named failure modes in its first line, and the sprint-or-two estimate covers the smallest cost on the list. A 6-week date is reachable only for a different, narrower scope (below).

I used the `sql-jdbc-access-design` skill and its references. I haven't seen Vantridge's data volumes, scan patterns or code, so the assumptions are marked.

## 1. Which problem this is

It is problem (c): giving customers a queryable SQL endpoint to their own data. That is the skill's full scope, covering isolation, schema stability, BI connectivity, governance, credentials and pricing. Engineering has scoped only the driver.

## 2. Why the proposal fails

| Proposal element | Skill verdict |
|---|---|
| Point customers directly at the shared ClickHouse cluster | ❌ Named failure mode: customer SQL admitted onto the shared production cluster. |
| Our own VQL dialect | ❌ Named failure mode: a custom dialect where a standard wire protocol was available. |
| Own Type-4 JDBC driver, certified with both tools | ⚠️ Possible, but it is the most expensive connectivity option (ongoing, see §3). |
| "A sprint or two and then it's done" | ❌ A driver is a recurring cost, not a one-off build. |

**PostHog matches this setup almost exactly.** It has a shared multi-tenant ClickHouse cluster and its own query language (HogQL). In its 2026 post-mortem, PostHog called unbounded customer queries on that cluster "basically untenable". It also said it "could not expose direct connections to the Clickhouse cluster" and that its query language "is not a language that's already widely supported". It rebuilt on per-organization engine instances behind a Postgres wire-protocol endpoint.

**Isolation is the biggest unknown.** Once a customer holds a live SQL handle, no application layer is left to intercept the query. A tenant filter enforced only in the VQL-to-ClickHouse translation is an app-layer `WHERE`, which the skill names as a failure class. One missed filter returns another customer's rows. I don't know where Vantridge enforces tenant scoping today. That is question 1 in §7.

## 3. What the real scope contains

### A. Driver and BI certification (recurring)

- **Tableau.** Needs a pure-Java Type-4 JDBC 4.0+ driver with accurate SQLSTATEs. Returning a generic error instead of 28000 for bad credentials can break connector behavior.
  - The connector ships as a signed `.taco`. An expired signing certificate makes Tableau reject it outright.
  - You tune it with TDC XML whose vendor and driver names must match what the driver reports.
  - Tableau limits its own support and won't customize a connector for your driver, so connectivity tickets stay with you.
- **Power BI.** ⚠️ Likely the biggest gap in the plan. Certified connectors are built on the Power Query SDK, so a JDBC driver alone does not deliver Power BI. You need a second deliverable, which I'd treat as a separate connector project.
  - Certification requires a public, code-complete product and documented customer demand (a public ideas-forum thread). You submit by pull request to Microsoft's connector repository.
  - Microsoft distributes the connector but routes customer issues back to you. Self-signed custom connectors are the lighter path.
- **Review queues.** Tableau and Microsoft review times are outside your control, and the skill gives no turnaround figures. Don't promise customers a certified-by date for week 6.
- **Certification files are a second stability surface.** A schema change can break the customization file or a certified connector's expected typing even when the data contract holds.
- **Ongoing costs:** certificate renewals, per-tool packaging, first-line support, and tracking each tool's release changes.

### B. Tenant isolation in the engine (gate, before any customer connects)

- Enforce isolation in the engine, not in VQL translation. I believe ClickHouse offers row policies and per-user settings profiles for this. Engineering should verify that and show it holds under the VQL layer.
- Run probe queries as another tenant and require zero foreign rows. Re-run on every policy change.

### C. Governance and cost caps (gate, before any customer connects)

Each external compute handle needs all three:
- a statement timeout and a queue timeout;
- a per-tenant concurrency cap;
- a spend or resource budget.

BI dashboards re-scan on a schedule, so one customer's morning refresh can saturate a shared cluster. Raising the cap for everyone to suit one tenant is the stated anti-pattern. A tenant that keeps tripping the caps moves to isolated compute.

### D. Schema-stability contract (can stage, but must exist before dashboards depend on it)

- Customers' dashboards become clients of your schema. Never expose the live operational schema.
- Serve a curated mart layer and make changes additive-only (add freely, never rename, retype or drop in place). Enforce it in CI, for example with dbt model contracts.
- Publish four parts: schema, quality, freshness, availability.
- Engine drift is a documented risk. PostHog saw ClickHouse change results between releases, and your test suite can't cover every customer query shape.

### E. Credentials (can stage)

- Prefer short-lived tokens, then managed secrets, then static passwords.
- BI tools: OAuth where the client can refresh tokens, with a key-pair or PAT service account as the fallback. Verify each tool's refresh support.
- Enforce TLS, scope each credential to one tenant, and give customers self-service revocation.
- Publish a connection-setup page per tool. An undocumented connection string becomes a support ticket per customer.

### F. Pricing

- Package it as a tier gate or add-on, never free.
- With a hard ship date, the skill holds the flat add-on or tier gate, since it needs no billing engineering. Revisit consumption pricing once cost data exists.
- Sixty customers asking is demand evidence. Price accordingly rather than absorbing the compute.

## 4. Architecture recommendation

Vantridge runs a self-managed OLAP cluster with no cloud warehouse, so the zero-copy share rung is deleted, not demoted. The skill's ranking gives these rungs:

| Rung | Fit for Vantridge |
|---|---|
| Replicated copy or dedicated read endpoint | **Realistic for 6 weeks.** A separate read-only ClickHouse cluster or replica, never the shared production one. Data is stale to the last refresh. |
| Per-tenant compute isolation | **Target state.** Promotion conditions are met: arbitrary customer SQL at dashboard frequency across many tenants, on a shared cluster whose worst-case query threatens the product. A hard ship date keeps it off the 6-week path. |
| Zero-copy share | Not available. |

Assumptions to check: dashboards will park on this, and each tenant scans tables large enough to hurt. If customers only run a few ad-hoc queries a week, the shared-cluster risk shrinks but doesn't disappear.

## 5. What 6 weeks can honestly buy

**Scope: a limited-availability SQL endpoint on a separate replica, using standard drivers.**

- **Connectivity:** use a standard wire protocol instead of a custom driver. ClickHouse documents a PostgreSQL-compatible interface, which I recall but have not verified here. If it works, Tableau and Power BI use their existing PostgreSQL connectors, with no `.taco`, no certification cycle and no Power Query connector.
  - ⚠️ Run a spike on whether the BI tools' introspection queries work against it.
  - Customers write ClickHouse SQL over curated mart views, not VQL. If VQL carries semantics customers value (metric definitions, event abstractions), expose them as views.
- **Isolation:** engine-level row policies on mart views, with the cross-tenant probe suite as a release gate.
- **Governance:** the three caps in §3C on the replica. This is also a release gate.
- **Contract:** the mart layer, plus a CI contract check on it.
- **Credentials:** per-tenant database users with managed secrets and TLS. OAuth can follow.
- **Docs:** one connection page each for Tableau and Power BI.
- **Pricing:** flat add-on or tier gate.
- **Rollout:** a handful of the 60 customers first, not all at once.

**Deferred past week 6:**
- Own JDBC driver and Tableau `.taco` certification.
- Power Query connector and Microsoft certification.
- Per-tenant compute isolation.
- OAuth and consumption pricing.

**Risk:** the two gates (isolation, cost caps) cannot be skipped. If the spike or gate work slips, the fallback is a smaller cohort, not a launch without them.

## 6. If leadership insists on the custom driver

Treat it as a product line with an owner, not a project:
- standing headcount for driver, Tableau and Power BI maintenance;
- a certificate-renewal calendar;
- support routing for connectivity tickets;
- a budget line for the separate Power BI connector;
- a promise to sales of "GA when each vendor certifies" rather than a date.

I'd want to hear engineering's rebuttal on one point: what the driver gives customers that the PostgreSQL-compatible route doesn't, apart from VQL.

## 7. Questions to settle before committing

1. Where is the tenant filter enforced today: engine policy, or VQL translation?
2. How many dashboards, how often do they refresh, and how large are the scanned tables?
3. Do customers need VQL specifically, or do they just need Tableau and Power BI to connect?
4. Is there a replica or spare ClickHouse capacity today, or does this need new infrastructure?
5. Who owns the Tableau and Power BI vendor relationships and the ongoing maintenance?
6. Ship-date flexibility: is 6 weeks a hard date for the full certified driver, or for "customers can connect"?
7. Pricing intent: free, tier-gated or metered, and who pays compute?
8. Is the target cohort 60 customers at once, or a staged group?

## 8. Bottom line

- ❌ The proposal as written puts customer SQL on the shared cluster, in a custom dialect, with an unestimated certification program. Both are named failure modes, and PostHog has already documented the first.
- ⚠️ "Sprint or two" covers the driver only. The gates, schema contract, credentials, support and both certification tracks come on top.
- ✅ A 6-week limited launch is feasible if you change the scope (§5): a separate replica, a standard wire protocol, engine-level isolation and caps, and the certified driver deferred.
- Next step: the isolation answer (question 1) and the wire-protocol spike decide the plan. I'd get both before committing a date to Sales.