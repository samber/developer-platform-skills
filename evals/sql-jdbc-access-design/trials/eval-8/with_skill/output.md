**Start here:** book 30 minutes with the four people. Each writes one sentence: "who gets what data, and what do they do with it?" Do not debate. You will see four different projects.

## 1. The four asks are four problems

Skill step 1 splits "data sharing" into three problems. Your four asks map like this:

| # | Ask | Real problem | Skill fit |
|---|-----|--------------|-----------|
| A | Agencies see aggregate data across brands | Sharing with partner organizations, many-to-many entitlement | Reuses the isolation mechanics (step 3). The tenant model differs. |
| B | One monster report slows everyone | Internal compute isolation, no external handle | Touches the isolation menu (step 2) and the caps (step 6) only |
| C | 12 customers point Looker at their data | Customer SQL endpoint | Full scope: steps 2 to 8 |
| D | 2 customers want nightly Parquet in their S3 | Bulk file delivery, no live query | **Out of scope.** Hand to `samber/developer-platform-skills@bulk-data-sharing-design` |

Different consumers, isolation primitives, pricing and owners. Splitting them is the first deliverable.

## 2. Answer for Head of Product

Do not run one project. Run one program with four workstreams and three shared foundations. This keeps the single quarterly line item.

Shared foundations, built once:

1. **Curated mart layer.** Never expose the live operational schema. Feeds C, D and A.
2. **Tenant entitlement table.** Maps who may see which brand's rows. Feeds A and C.
3. **Schema-stability contract.** Additive-only, enforced in CI (dbt contracts). Feeds A, C and D. A Parquet file schema is also a contract.

## 3. Sequence

1. **B first.** It is a gate for C. Customer SQL on the shared cluster is the PostHog "basically untenable" failure. Opening Looker onto the cluster you are trying to protect multiplies the problem.
2. **D in parallel.** It is small, independent, and has 2 customers. Export from the curated mart or a replica. Never run a nightly job against the shared analytics DB, because that feeds B.
3. **C after B's caps exist.** Pilot with 2 to 3 of the 12 customers, then widen.
4. **A last, or in parallel if design capacity exists.** It needs consent and a privacy decision first (see section 4).

## 4. Per-workstream decisions

**B: noisy neighbor (engineering)**
- First, pull query logs and list the top 10 queries by runtime and the tenant behind each. No evidence, no design.
- Add a statement timeout, a queued-statement timeout, and a per-tenant concurrency cap.
- Add a spend cap that suspends the warehouse at budget. The timeout bounds a query. The cap bounds the month.
- Escalation rule: a tenant that regularly queues others moves to isolated or larger compute. Never raise the shared cap for everyone.
- Promote to per-tenant compute isolation only if arbitrary customer SQL runs at dashboard frequency across many tenants, or the worst-case query already threatens the product. Otherwise caps are enough.

**C: Looker for 12 customers**
- Architecture is gated on scan frequency. Scheduled Looker dashboards re-scan many times a day. That pushes you off zero-copy toward a **replicated copy or dedicated read endpoint**.
- The rule of thumb (one practitioner's, not a benchmark): about 20 scans a day on about 200 GB makes live re-scanning cost more than a replica.
- Isolation lives in the engine. On Postgres-family engines use RLS with `FORCE ROW LEVEL SECURITY` and tenant identity injected server-side. On warehouses use secure views with share-aware identity functions. `CURRENT_ROLE()` and `CURRENT_USER()` are NULL across a share.
- Probe from the consumer side: a second tenant's account must return zero foreign rows.
- Expose a Postgres wire-protocol endpoint if the engine allows it. Avoid a custom dialect.
- Verify Looker's supported dialect list yourself. My references cover only Tableau and Power BI certification, not Looker.
- Credentials: short-lived token over managed secret over static password. If Looker cannot refresh a token, fall back to a key-pair or PAT service account. Inline passwords never appear in docs.
- Pricing: default to a flat add-on or tier gate, with B's caps in place first. Revisit consumption pricing if usage varies by orders of magnitude.

**A: agencies, aggregate across brands**
- Entitlement is agency to brand, many-to-many. Isolation must be at engine level, with a mapping table rather than a single `tenant_id`.
- Serve pre-aggregated views only, never row-level data.
- Three agencies is a small set. A curated aggregate mart with an entitlement table may be enough. A SQL endpoint may not be needed.
- ⚠️ Do not build until the brands' consent and contracts are settled. Aggregates over a small brand count can re-identify a single brand. Decide a minimum-cohort rule.

**D: Parquet to S3**
- Hand off to the bulk-delivery skill. Do not design it here.

## 5. Questions to answer this week

Answer these and I will finish the design. The answers I assume in section 4 are marked.

1. Where does the analytics data live: Snowflake, Databricks, BigQuery, a Postgres, or a self-managed OLAP cluster? *(Assumed: unknown. This decides which rung is nearly free.)*
2. How often will the 12 Looker customers query? Do they park scheduled dashboards? How large are the tables? *(Assumed: dashboards, so a replica.)*
3. How many customer accounts are there, and is the store pooled or siloed per tenant?
4. Which SQL consumers do customers actually want beyond Looker? Notebooks, Tableau, agents?
5. Are the 12 customers asking for raw operational tables or a curated layer? *(Assumed: curated mart.)*
6. Is SQL access a free feature, a tier gate, or a paid add-on, and who pays the compute? *(Assumed: paid flat add-on.)*
7. Ship date, one-off versus compounding asset, and effort ceiling? A hard date favors the flat gate and a replica you already have.
8. Do the agencies' brands have contractual consent to cross-brand aggregates?

## 6. Gates before any customer connects

- **Isolation gate:** probe queries run as another tenant return zero foreign rows. Re-run on every policy change.
- **Schema gate:** CI contract check blocks any breaking column change.
- **Cost gate:** every external handle has a statement timeout, a concurrency cap and a spend cap. Pass or fail per handle.
- **Reader-account trap:** if you provision accounts whose compute bills to you, a resource monitor on each is mandatory.

## 7. Risks to flag to the Head of Product

- One project hides B as a prerequisite. Slip B and C slips with it.
- A is a consent and privacy problem more than a technical one. Engineering cannot unblock it.
- The Parquet export can worsen B if it runs against the shared DB. Source it from the mart or a replica.

## Next action

Send the 8 questions above to the Head of Product, and book the 30-minute alignment session. Ask engineering to pull the top-10 slow queries by tenant in parallel. That is about 1 hour of work and unblocks B.