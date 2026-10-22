# Nimbus Ledger data export: cadence and customer commitments

I read the skill and its three references. I couldn't ask the skill's clarifying questions, so the open ones are listed at the end. Each says which way it would change the plan.

## Decision

1. **Ship batch first.** Scheduled snapshots, with a published cadence of **every 3 hours** as the starting default. Re-measure it before launch.
2. **Do not put "SLA" in front of customers yet.** Replace the pricing-page line this week. Hourly can come back later, once delivery history supports it.
3. **Don't skip batch for Debezium, and don't reject it.** Debezium is a later internal upgrade behind the same customer-facing contract. Your data engineering lead's experience moves that upgrade earlier. It doesn't remove the need for the contract.

## 1. The cadence we ship

The skill's default rung is a scheduled full dump: idempotent overwrite, no delete tracking, simplest to run. Stripe's reference is a full load every 3 hours. Your data splits into two shapes.

| Data | Shape | Cadence |
|---|---|---|
| Billing events | Append-only | New Parquet files per cycle, partitioned by date (`year=/month=/day=`). No delete problem, and incremental is nearly free. |
| Invoices, subscriptions | Updated, sometimes hard-deleted | Full snapshot each cycle that replaces the previous one. A hard-deleted dispute row simply isn't in the next snapshot, so no tombstone logic is needed. |

- **Why a full snapshot for mutable tables.** Hard deletes are the named CDC failure mode: a delete that never emits an event leaves a phantom row in every customer's copy. A snapshot cannot have that bug.
- **Publish the swap atomically.** Raw Parquet has no atomic multi-file commit. Write each snapshot to a new directory, then update a manifest file that points at it. The manifest carries an `as_of` timestamp, so customers can check freshness themselves.
- **Move to Iceberg or Delta only when needed.** Do it when you need time-travel or in-place schema evolution. The manifest approach is enough for now.
- **Set the exact interval after a load test.** 3 hours is the reference, not a measurement. As a rule of thumb of mine (not from the skill), promise an interval of at least 2–3× the p95 duration of your slowest full snapshot cycle. If that p95 is well under 20 minutes at your largest tenant, hourly becomes plausible.

## 2. The hourly SLA on the pricing page

The skill's freshness posture has three levels, and they carry different consequences:

| Posture | Example | Meaning |
|---|---|---|
| Fixed cadence | Stripe: a full load every 3 hours | A stated schedule |
| Best-effort target | Amplitude: "aims to export five million events per hour" | A goal, explicitly variable |
| Contractual SLA | Fivetran: 99.9% uptime, penalty-backed | Credits, escalation, legal exposure |

"Hourly data SLA" reads as the third. As things stand you have made a promise your engineering can't back with a measured track record.

**This week:**
1. **Tell marketing and legal the page now makes a commitment.** Get legal to check whether any customer contracts or sales emails already reference it. I'm not a lawyer, so that check is theirs.
2. **Change the copy** to the posture you can honestly state. The simplest option is "Data refreshed every 3 hours. Each delivery includes a timestamp so you can verify it." The alternative is "We aim to deliver hourly" with the word SLA removed. Choose that only if load testing shows hourly is achievable.
3. **Don't move to a contractual SLA yet.** Promote to one only after at least a quarter of tracked "share of deliveries meeting posture" numbers, plus a decision on penalties.
4. **Align on the process.** Pricing-page claims about data products need an engineering sign-off before they go up.

## 3. Debezium CDC

**For it.** The skill says a team that has run log-based CDC before buys that rung much cheaper than the generic ladder assumes. Three years of Debezium is a real input. CDC also wins at scale: operating cost falls and freshness improves.

**Against skipping batch.**
- **CDC doesn't replace the customer-facing layer.** Per-tenant partitions, compaction, a catalog, per-recipient credentials, the schema contract, and the delete semantics are all still required. A WAL stream is an internal table shape, and exposing it directly would turn your internal schema into the customer's contract.
- **CDC adds obligations.** Adopting it commits you to upsert-by-primary-key dedup, explicit delete tombstones, and a periodic full-scan reconciliation job. The skill treats reconciliation as mandatory even though Debezium does emit Postgres deletes.
- **Timing.** The deadline is next quarter and nobody has asked for sub-3-hour freshness (open question 3). Building the hardest rung first, with no demand signal, is the skill's "starved option" pattern.

**Proposal that respects both positions.**
1. **Quarter 1:** ship the batch design above.
2. **In parallel:** your data engineering lead builds Debezium as an internal feed that produces the same files under the same contract. Customers see no change.
3. **Promote CDC when either trigger fires:** the full-snapshot bandwidth and compute bill exceeds CDC's build cost, or a paying customer needs fresher than your published cadence. Keep the weekly full-scan reconciliation job as a safety net.
4. **Write the trigger numbers down** now, so this doesn't become a recurring debate.

## 4. What goes in front of customers

One page, the "data contract". The skill has four parts, and the contract names each:

1. **Schema.** Columns, types, and nullability for each table.
   - Add-only: new nullable columns go at the end. Nothing is renamed, removed, or retyped in place.
   - Breaking changes get an announced window, parallel old and new columns, and a dated removal.
2. **Freshness.** State the posture by name, e.g. "Fixed cadence: every 3 hours, with an `as_of` timestamp in each delivery."
3. **Quality and delete semantics.**
   - Say plainly that `invoices` and `subscriptions` are full snapshots. A row removed after a dispute disappears from the next snapshot, and customers who keep their own copies must handle that.
   - Events are append-only.
4. **Availability and layout.** Hive-style partitions, 256–512 MB target files, and a registered catalog schema. The paragraph on what customers do if a delivery is late or missing goes here.

Also put in writing:
- **Cost allocation.** In a file drop the customer pays for their bucket and compute. Say who pays cross-region egress, because that line item is the decisive one.
- **Credentials.** Per-recipient cross-account roles with an external ID, and KMS grants per recipient. No static keys, and bytes are never proxied through your API servers. With 4,200 customers, don't use a bucket per tenant. Start with a shared bucket plus prefix isolation or per-recipient access points.
- **Residency.** EU customers are pinned to EU buckets and keys from day one, so no cross-border transfer paperwork is needed. Anywhere with a localization law, say explicitly that it isn't offered.
- **Pricing.** Every vendor in the skill's research gates bulk export behind a paid tier or add-on. Keep yours gated, or record the decision to break that precedent.

## 5. Native share

If many of your accounts use one warehouse (the skill suggests roughly 30–40% on a single platform), ship a native share (Snowflake, Delta Sharing, BigQuery) first. It costs the consumer no egress or storage duplication. Otherwise the file drop is the only surface. Without any share-capable accounts, delete the share option from the roadmap rather than leaving it at the bottom.

## 6. Open questions

Answer these and I'll finalize the plan.

1. What share of target accounts runs Snowflake, Databricks, or BigQuery, and does one dominate?
2. How large are the datasets, and how long does a full snapshot take today at the largest tenant?
3. Did any paying customer actually ask for hourly or faster, or was "hourly" marketing's idea? If a deal depends on it, CDC moves up.
4. Which regions are your customers in, and is any EU personal data in scope?
5. Is the export a paid add-on, an enterprise-tier feature, or "free"? The page needs to match.
6. Which clouds are the recipients on?
7. Is there a hard launch date, and is this a one-off deal-closer or a surface you'll keep building on?
8. Are hard-deleted dispute rows legally required to be erased downstream? If so, that needs a separate policy, because customers already hold earlier exports.