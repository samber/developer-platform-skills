# Verdict

Your instinct gets the answer partly right for the wrong reason. Don't split by what customers pay. Split by workload shape and by how bad a failure would be.

## Where the instinct breaks

1. **Price doesn't set infrastructure cost.** Six accounts at six figures each, against a few hundred dollars a month of BigQuery. Cost is not the deciding variable. Blast radius and SLA are.
2. **The enterprise load is the easy one.** It's the same fixed queries, run by 300 people, on a predictable weekday morning peak. Precompute, cache and serve that, and 300 GB per customer stops mattering.
3. **Mid-market is the riskier one.** Arbitrary SQL from 40 accounts is where a runaway scan or a cross-tenant leak happens. "Pooled" must mean pooled compute. It must never mean pooled raw data.
4. **"Dedicated" in BigQuery has no server to rent.** It means a project boundary, a slot reservation, or both. Dedicated slots for one customer would sit idle about 99% of the day.

## Numbers (assumptions in brackets, so check them)

On-demand is about $6.25/TiB in the US [verify current pricing].

| Case | Scan per day or month | Cost |
|---|---|---|
| Enterprise, naive: 50 users × 10 tiles × 30 GB, no cache | ~14.6 TiB/day per customer | ~$2,000/mo per customer, ~$12k/mo for all six |
| Enterprise, shared identity + result cache (10 distinct queries) | ~0.3 TiB/day | ~$40/mo per customer |
| Enterprise, aggregated serving tables | MBs per tile | ≈ $0 |
| Mid-market: 40 accounts × ~10 queries/week × 2 GB, full scans | ~3 TiB/mo | ~$20/mo total |
| Storage: per-tenant copies, 1.8 TB + 80 GB at ~$0.02/GB | n/a | ~$40/mo |

Two conclusions follow:
- Mid-market compute is nearly free. Buying reserved slots for it would cost more than the workload.
- Per-tenant physical copies cost almost nothing. That is cheaper and safer than clever row-level security on shared tables.

## What I'd build

**1. Data isolation, the same for everyone**
- Build a per-customer serving dataset, fed incrementally from core tables that are partitioned by date and clustered by `tenant_id`.
- Refresh with Dataform or scheduled queries. Enterprise data is ready by about 06:00 local.
- Customers never get raw core tables. Expose curated tables or authorized views only.

**2. Boundary, which is where the tiers differ**
- **Enterprise:** one GCP project per customer. You get a clean IAM boundary, per-customer cost attribution, per-project quotas, and a path to CMEK, residency or VPC-SC if a contract demands it. Offboarding is deleting a project.
- **Mid-market:** one shared project (or a few). One dataset per customer, one service account per customer, and IAM granted at dataset level.

**3. Compute**
- **Enterprise:** one shared autoscaling reservation (Enterprise edition, baseline small, max about 400 slots), assigned to the six projects. Worst-case cost is in the low hundreds of dollars a month. Peak is 30 minutes a day, so one pool covers all six. If one customer ever hurts the others, give it its own reservation. Project-per-customer makes that a config change.
- **Mid-market:** on-demand, in a separate project, so ad-hoc queries can never compete with the enterprise morning peak.

**4. Enterprise dashboard path**
- **Find out whether the BI tool uses a live connection or a scheduled extract.** An extract turns 50 users into one refresh job and is the cheapest fix.
- For a live connection, use one service account per customer. Identical query text then hits the 24-hour result cache.
- Point tiles at pre-aggregated tables, such as shipment performance by day and lane. Don't point them at the 300 GB base tables.
- Add BI Engine last, and only if p95 tile latency misses target after the above. It is the priciest component.

**5. Mid-market guardrails**
- Set custom quotas on bytes per user per day and per project per day. That is the server-side cap, because `maximum_bytes_billed` is only per job and the client sets it.
- Add a job timeout, and label every job with its customer for chargeback.
- Alert on `INFORMATION_SCHEMA.JOBS` for anyone above 10× their norm.

**6. Optional:** for customers already on GCP, offer Analytics Hub linked datasets. They query from their own project and pay their own compute.

## Rollout

1. Build the serving layer and one enterprise project as a pilot.
2. Run on-demand for 2–4 weeks and measure `total_slot_ms` and bytes billed per customer.
3. Size the reservation from the measured numbers, not my guesses.
4. Onboard mid-market in batches of 5–10.

## What would change my answer

- ❓ Are core tables already per-tenant, or shared with a `tenant_id` column? Shared means the serving layer is the first piece of work.
- ❓ Do the enterprise contracts already promise residency, CMEK or a latency SLA? If so, those drive the enterprise tier, not volume.
- ❓ How do customers authenticate: Google identities, or service-account keys into Power BI or Tableau? That determines the identity design.
- ❓ How fresh must the data be? Sub-hourly changes the refresh design and the cost.
- ❓ Do they truly need SQL, or do they need the dashboard? An embedded dashboard avoids the whole access surface.