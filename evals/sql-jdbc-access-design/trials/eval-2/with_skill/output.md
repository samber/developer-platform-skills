# Customer SQL access for Paceline Metrics on BigQuery

## Verdict

Your instinct lands in roughly the right place, but the reasoning behind it doesn't hold up.

- **Revenue shouldn't pick the architecture.** Scan frequency times table size should. Six-figure contracts buy a higher service level: refresh SLA, named support, a bigger cap envelope. They don't buy a different engine.
- **Enterprises need a replicated mart, not dedicated compute.** Fifty people loading a dashboard over 300 GB each morning is well past the point where live re-scanning costs more than a copy. The fix is a pre-aggregated copy per tenant, which is a lighter rung than a dedicated engine. Dedicated per-tenant compute is promoted only for arbitrary customer-written SQL at dashboard or agent frequency across many tenants. Six fixed-shape dashboards don't meet that bar.
- **Mid-market on a pooled setup is right, but only if the pool has engine-level isolation.** At about 2 GB each and a handful of queries a week, cost isn't the issue. The risks are a leaked row and a runaway query.
- **Neither tier should query the project your product runs on.** This is the PostHog lesson: customer SQL must never share quota or slots with your own pipelines.

## Assumptions

I couldn't ask questions, so I assumed the following. Any of these could change the design.

- This is problem (c): customers get a SQL endpoint to their own data. They are not partner orgs, and this isn't about internal tenant compute.
- The 50 viewers per enterprise are BI-tool viewers, not 50 people each holding a database login.
- The BI tools are Tableau, Power BI or Looker, in live mode. I design for live mode as the worst case because you can't control a customer's import or extract settings.
- Enterprise dashboards have a fixed query shape. Some enterprise analysts may also want ad-hoc SQL.
- Most customers have no GCP project of their own, so compute bills to you. That makes caps mandatory, the BigQuery version of the reader-account trap.
- Pricing figures are BigQuery list prices from memory: $6.25/TiB on-demand scan, $0.02/GB-month active storage, about $0.04/slot-hour for a Standard edition slot. **Verify them before quoting anyone.**

Answers that would flip the design:

| Question | If the answer is… | Then… |
|---|---|---|
| Do enterprises have their own GCP projects? | Yes | Offer an Analytics Hub share as an option. Their queries run in their project and bill to them. |
| Do enterprise analysts want free-form SQL on the 300 GB detail? | Yes | Add a partitioned detail table with a mandatory partition filter (see Enterprise below). Per-tenant slot reservation is the escalation if they trip the caps. |
| Is the schema exposed raw or as curated marts? | Raw | Build the mart layer first. Nothing else ships until then. |
| Is there a ship date? | Hard date | Ship the mid-market pooled tier and the flat price first. |

## 1. Scan economics

**Enterprise, live zero-copy, worst case:** every dashboard load scans the full 300 GB.

- 50 loads × 300 GB ≈ 14.6 TiB/day ≈ **$92/day**
- × 22 weekdays ≈ **$2.0k/month ≈ $24k/year per customer**
- × 6 customers ≈ **$145k/year**

Partition pruning and the BI tool's cache would cut that, and one dashboard load usually runs several queries, so the real number could go either way.

For comparison, the skill's rule of thumb is that about 20 scans/day on a 200 GB table tips live access over a copy. You're at about 50 scans/day on 300 GB, which is 2.5× the scans on 1.5× the size.

**Enterprise, mart rung:** the dashboard reads pre-aggregated tables.

- Assume ≤ 1 GB scanned per load, so 50 GB/day, about 1.1 TB/month, or **~$7/month**.
- A full nightly rebuild of 300 GB costs about $1.8 per run, **≤ $60/month**. Incremental refresh costs far less.
- Storage for the copy is **~$6/month**.
- The cost you take on is staleness to the last refresh, plus a second copy of the data to govern.

**"Dedicated infrastructure" priced honestly:** 100 always-on baseline slots per enterprise is about **$2.9k/month**, or $35k/year each. For six that is about $210k/year, more than the worst-case live-scan bill. The dashboard is bursty and idle for roughly 23 hours a day, so a dedicated engine would mostly sit unused.

**Mid-market:**

- 40 tenants × 5 queries/week × 2 GB = 400 GB/week, **about $2.50/week** in total.
- If the pooled table is clustered badly and each query scans all 80 GB, that becomes about 16 TB/week, or **~$425/month**. Still small, but it shows the pool needs clustering and a per-query byte cap.

## 2. Architecture by tier

```
product pipelines (your project, untouched by customers)
        │  curated mart, dbt, additive-only contract
        ▼
┌──────────────────────── customer-facing projects ────────────────────────┐
│ ENTERPRISE (6): one project + one dataset per tenant                     │
│   mart_agg  – pre-aggregated shipment-performance tables (dashboard)     │
│   mart_detail – partitioned/clustered, require_partition_filter = true   │
│   one dashboard service account + named analyst identities               │
│                                                                          │
│ MID-MARKET (40): one shared project, one pooled dataset                  │
│   tables clustered by tenant_id, row access policy per tenant principal  │
│   per-user quota, per-query byte cap                                     │
└──────────────────────────────────────────────────────────────────────────┘
```

Enterprise:

- **One dataset per tenant.** Isolation comes from the IAM boundary, which is cheap at six tenants. It also gives clean per-tenant cost attribution.
- **Two table sets.**
  - `mart_agg` is shaped to the dashboard, with stable column names. The dashboard reads only this.
  - `mart_detail` is for ad-hoc queries, partitioned by ship date with `require_partition_filter = true`. A full scan of the 300 GB detail then fails by construction.
- **Refresh target:** ready before the morning peak in the customer's local time. This is a placeholder, so confirm each customer's time zone and the SLA.
- **BI Engine** (in-memory acceleration) is an optional later lever. Check its size limits first.
- **Per-tenant slot reservation** is the escalation path, not the starting point (see section 7).

Mid-market:

- **One shared dataset, with a private base table.** Cluster by `tenant_id` and verify the bytes scanned with dry runs. Don't assume a row access policy reduces billed bytes.
- **Not on your production project.** The customer-facing surface gets its own project, so a mid-market runaway query can't touch your product's quota.
- **Zero-copy or consumer-pays only where it fits.** If a mid-market customer has GCP and wants it, an Analytics Hub listing works. Otherwise they query your project.

## 3. Tenant isolation

Enforce it in the engine, never with an app-layer `WHERE`.

- **Mid-market:** use a row access policy per tenant, granted to that tenant's principal, filtering on `tenant_id`. A principal not covered by any policy sees zero rows, so a query that forgets the filter returns nothing. At 40 tenants you're well inside per-table policy limits. **Verify the current limit.**
- **Enterprise:** dataset-level IAM per tenant, with the base tables in a private dataset that never enters any grant.
- **Identity trap:** don't write policies against session-identity functions without testing them as a real consumer. The Snowflake NULL-context problem has no confirmed BigQuery equivalent, but cross-share identity behavior is exactly where it hides. Test through the same path customers will use.
- **Isolation gate, run before GA and after every policy or schema change:**
  1. Run probe queries as tenant B's principal against every view, table and policy that serves tenant A.
  2. Require zero foreign rows and zero readable base tables.
  3. Run it in CI.

## 4. Schema-stability contract

- **Mart only.** Never expose operational tables.
- **Additive-only.** Add columns and tables freely. Never rename, retype or drop in place; use expand/contract instead.
- **CI-enforced.** dbt model contracts fail the run on a breaking change. The `datacontract` CLI checks the PR.
- **Four-part contract per tenant:**
  - Schema: columns, types, nullability.
  - Quality: completeness thresholds.
  - Freshness: refresh SLA.
  - Availability: uptime and latency.
- **Higher bar for enterprise.** The `mart_agg` columns are the dashboard's API. A rename silently breaks six customers' reports, and a customer's BI connector may bind to column typing as well.

## 5. BI connectivity

Don't build a driver or a Postgres wire-protocol shim.

- Tableau, Power BI and Looker ship native BigQuery connectors, so there is no certification tax for you.
- Publish one connection-setup page per tool: project, dataset, auth method, TLS, and a recommended import or extract mode on a schedule. That is the cheapest way to cut scan frequency, and it works even though you designed for live mode.
- **Fifty viewers don't need 50 BigQuery identities.** Publish the dashboard under one dashboard service account per tenant. Viewers authenticate to the BI tool, not to BigQuery.
- **Verify each tool's auth options.** Check which of OAuth and service-account login each supported client actually handles, before promising either.

## 6. Governance and cost caps

Every handle needs all of these before the first customer connects. Several are not on by default.

| Control | Enterprise | Mid-market | Notes |
|---|---|---|---|
| Per-query timeout | Set | Set | Project-level default job timeout exists. **Verify the setting name.** |
| Per-query byte cap | Client-set `maximum_bytes_billed` plus the partition-filter requirement | Same | A project-wide per-query cap isn't something I can confirm. Don't count on one. |
| Daily bytes quota | Custom quota per project | Custom quota per user and per project | This is what actually stops spend. |
| Concurrency and burst | Slot reservation with a max-slots cap | Smaller pool reservation | Isolates tiers from each other. |
| Spend alarm | Billing budget alert | Same | **Budgets alert, they don't stop.** Alert-only is not a cap. |

- **Provider-pays trap:** compute bills to you with no default ceiling. Quotas and reservation caps are the single most important control on this surface.
- **Escalation signal:** a tenant that regularly queues others or trips its quota gets isolated or larger compute. Never raise the shared cap for everyone to accommodate one tenant.

## 7. When an enterprise gets dedicated compute

Promote a single tenant to its own slot reservation only when one of these holds:

- It runs arbitrary SQL at dashboard or agent frequency.
- It repeatedly trips quotas or queues other tenants.
- Its worst-case query already threatens the shared enterprise reservation.

Until then, all six share one enterprise reservation, kept separate from the mid-market one.

## 8. Credentials

Preference order: short-lived token, then managed secret, then static key.

- **Dashboard service account:** use workload identity federation or impersonation where the customer's tool supports it. Otherwise a rotated service-account key with overlap rotation, never a key in a connection string.
- **Named analysts:** OAuth through the customer's identity provider.
- **Scope and revocation:** scope every credential to one tenant. Give customers self-service revocation.
- **Degradation:** where a BI tool can't refresh tokens, fall back to a rotated service-account key, never a shared password.

## 9. Pricing

Charge for this. SQL access is never a free feature.

- **Start with two flat add-ons, not metering.**
  - Enterprise add-on: dedicated mart, refresh SLA, cap envelope, named support.
  - Mid-market tier gate: pooled access with the caps above.
  - A flat price has no billing engineering and is acceptable only because the section 6 caps bound the downside.
- **Your costs are consumption-based and tenant sizes span about 150× (2 GB to 300 GB).** That is the condition for promoting to consumption pricing. Decide after the first billing month, not before.
- **If you meter, meter a business unit the buyer understands,** such as shipments per month. Never meter BigQuery bytes or slots. Stripe Sigma shows pricing can be revised after launch.
- **From day one:** label jobs per tenant and query `INFORMATION_SCHEMA.JOBS` by project, so cost per tenant against price paid is measurable.

## 10. Go-live gates

1. **Isolation gate:** cross-tenant probes return zero rows (section 3).
2. **Schema gate:** zero breaking changes pass CI.
3. **Cost gate:** each handle has a timeout, quota, concurrency cap and spend control (section 6).

Baseline from the first month:

- Connectivity tickets per new connection.
- Per-tenant cost against price paid.
- Freshness-SLA adherence.

## 11. Build order

1. Confirm the four open questions above.
2. Build the curated mart and the dbt contract in CI.
3. Stand up the customer-facing projects with quotas and caps.
4. Pilot mid-market: 3 to 5 tenants, pooled table, row policies, probe tests.
5. Roll out enterprise one tenant at a time: dataset, `mart_agg`, dashboard service account, then the probe.
6. Review per-tenant cost after the first billing month. Then decide on metering and on any tenant's promotion.

I didn't save the settled decisions to a context file. Say if you want them written to `developer-platform-context.md`.