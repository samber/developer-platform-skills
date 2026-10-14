# Nimbus Ledger data export: cadence and customer commitments

**Next action today:** change "hourly data SLA" on the pricing page to "hourly data refresh" (copy below). Then settle the cadence question with data engineering.

## Decision

Ship **hourly incremental batch** at launch. Define the customer contract independently of the mechanism, and treat Debezium as a phase-2 swap behind that contract. Don't skip batch, and don't reject CDC.

## Why not CDC-first

- **Customers asked for hourly.** Marketing's promise is hourly, and nobody has asked for sub-minute data. CDC buys latency you aren't selling.
- **A replication slot can take down billing.** If the Debezium consumer stalls, Postgres retains WAL until the primary's disk fills. Your most critical database then depends on a new Kafka Connect deployment, and that is the wrong risk for a first release.
- **CDC doesn't ship an export product by itself.** You still need per-customer partitioning (4,200 tenants), file or share delivery, schema mapping that hides internal tables, backfill, and snapshot handling. CDC supplies the change feed, which is about a third of the work.
- **The deadline is next quarter.** Your lead has run Debezium for three years, and that experience is an asset. He should build it as an internal pipeline after launch, with the batch export as the reference to check it against.

**CDC's real advantage is hard deletes.** Plain `updated_at` batching can't see deleted rows. You can fix this without CDC:

1. Write every hard delete to a `deleted_records` table, via a trigger or in the dispute code path. It records entity, id, customer, and `deleted_at`.
2. Better still, make disputed deletes soft deletes, with a purge job after the retention window.

Either way the export emits **tombstones**.

## Batch design (the parts that bite)

1. **Read from a replica**, not the primary. Include replica lag in the freshness number you report.
2. **Don't trust `updated_at` or sequence watermarks alone.** Long transactions commit rows with older timestamps, so you would miss them. Re-read an overlap window (last 2 hours) and dedupe by primary key plus version.
3. **Append-only events:** same overlap logic, keyed on event id. Corrections arrive as new events and are never rewritten.
4. **Daily reconciliation:** compare per-customer row counts and checksums against the source, and run a full snapshot weekly. This catches missed deletes and drift, and it gives you the evidence for a later SLA.
5. **Every delivery carries a manifest** with `data_complete_through` (a timestamp), row counts, and a schema version.

## What to put in front of customers

**Pricing page (replaces the current claim):**

> **Hourly data refresh.** Your export updates every hour with new billing events and changes to invoices and subscriptions, including deletions. Each delivery shows exactly how current it is.

Mark it "available [launch date]" if the page is live before the product.

**Data contract page (docs, linked from pricing):**

| Topic | Commitment |
|---|---|
| Cadence | Hourly incremental, plus a weekly full snapshot |
| Freshness | Target: changes visible within 75 minutes of commit. Each delivery states `data_complete_through` |
| Delivery semantics | At-least-once. Upsert by primary key and version |
| Events | Append-only. Corrections arrive as new events |
| Updates | The latest version of each invoice or subscription replaces the previous one |
| Deletes | Hard-deleted records arrive as tombstones in the next delivery. Customers must remove them downstream |
| Schema changes | Additive changes are made without notice. Breaking changes get 90 days' notice |
| Status | Delivery status page and failed-run alerts |
| Credits and penalties | None at launch. Freshness is a target |

**SLA:** offer a formal SLA with credits only after about 90 days of measured delivery data. Add it to enterprise order forms first, using the percentile you actually hit, not hourly.

**Why 75 minutes:** with a run every 60 minutes, the oldest data in a delivery is about 60 minutes old plus runtime. Hourly refresh is not the same as data under one hour old. Check this number against real run times and replica lag before it goes on the page.

## The marketing issue

- "SLA" is the problem, not "hourly". An SLA implies a contractual guarantee with remedies, and you can't measure one yet. Keep the hourly claim and drop the word.
- **Check this week:** has any deal, RFP, or contract cited the SLA since it was published? Ask sales and legal. If so, you may need a written clarification for that customer.
- **Process fix:** any numeric performance, uptime, or freshness claim on a public page needs sign-off from the engineering owner. Frame it as protecting marketing from commitments they can't see, not as a reprimand.

## When to move to Debezium

Move when one of these happens:

- **Demand:** several customers or prospects, with named deals, need freshness under 15 minutes.
- **Load:** batch extraction measurably strains the replica or runs past its hourly window.
- **Deletes:** the reconciliation job keeps finding missed deletes the trigger approach can't fix.

The contract above stays the same through the swap. Only the freshness number improves.

## Assumptions to confirm

- Finance and legal confirm that a disputed deletion must also be propagated to customers' exported copies.
- Delivery is files or a warehouse share, not a streaming API. If customers expect a stream, the CDC case gets stronger.
- A replica exists or can be added before launch.