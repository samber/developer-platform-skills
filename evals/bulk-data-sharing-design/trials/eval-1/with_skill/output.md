# Tilepath bulk export: design

**Shape: partitioned Parquet file-drops on S3, behind a paid add-on. No native warehouse share.**

I followed `bulk-data-sharing-design` (SKILL.md plus its three references). It says to ask seven questions before designing, so those come first. I've stated an assumption for each unanswered one and what would change the design.

## Inputs and assumptions

| # | Question | What I have | Assumption if not given | Flips if |
|---|---|---|---|---|
| 1 | Warehouse landscape | 0 of 120 top accounts on Snowflake, Databricks or BigQuery. They use Athena, DuckDB and Spark on EMR. | None needed. | See the re-promotion trigger in the next section. |
| 2 | Data shape | Three datasets (below). | Jobs and invoice lines are mutable, with updates and voids. Pings are append-only but arrive late from offline phones. | Pings turn out to be edited after the fact. |
| 3 | Freshness demand | Not sourced from buyers. | Day-old to 6-hour-old data is fine for analytics and churn models. | Buyers ask for under an hour. That promotes the cadence ladder (step 3). |
| 4 | Regions and compliance | Unknown. | US-centric base. Technician GPS is employee location data, so treat it as personal data everywhere. | Any EU or UK customer, or any localization-mandate country. |
| 5 | Pricing | Unknown. | Paid add-on or top-tier gate. | Only if you decide to break precedent (step 5). |
| 6 | Recipient clouds | Athena and EMR imply AWS. | AWS only. | A GCP or Azure buyer appears. |
| 7 | Delivery ceiling | Unknown. | Compounding platform surface, small team. | A hard deal-closing deadline. |

**Please confirm 3, 4 and 5. They change the numbers below.**

## 1. Camp: file-drop only, and delete the Snowflake line

- **Ship Parquet on object storage.** Athena, DuckDB and EMR Spark all read it natively, and this is the only shape your surveyed buyers can consume.
- **Delete "Snowflake sharing (later)" from the roadmap.** Don't demote it. A share needs a share-capable destination on the recipient's side, and zero of your top 120 accounts have one. An item left at the bottom is what keeps getting re-added in roadmap reviews.
- **Re-promotion trigger, written on the roadmap in place of the line:** roughly 30-40% or more of paying accounts concentrated on one shareable platform. That threshold is self-set, not a vendor figure. Re-ask the warehouse question in the annual customer survey, and revisit only if the trigger fires.
- **Survey caveat:** top accounts skew toward more sophisticated data stacks. The long tail of 1,780 smaller HVAC, plumbing and landscaping shops is less likely to run a warehouse than your top 120, not more.
- **Delta Sharing is not needed.** EMR Spark reads Parquet directly. It isn't Databricks.
- **Streaming push is starved.** Nothing in the survey asks for sub-minute delivery. Every roadmap review is a chance to ask whether anyone has asked for it.
  - If live technician tracking ever becomes a customer-side need, revisit it with Braze's replay warning in the contract.

## 2. Layout and partitioning contract

Bucket layout, one regional bucket per residency region:

```
s3://tilepath-export-<region>/v1/tenants/<tenant_id>/
  jobs/snapshot=<UTC-ts>/part-*.parquet
  invoice_line_items/snapshot=<UTC-ts>/part-*.parquet
  gps_pings/year=2026/month=10/day=08/part-*.parquet
  _manifest.json        # per dataset: last_completed_at, snapshot_id, schema_version, row_count
  _schema/v1.json       # the written contract
```

| Dataset | Nature | Layout | Why |
|---|---|---|---|
| `gps_pings` | Append-only, high volume, late-arriving | Hive `year/month/day` (2 levels under the tenant prefix) | Consumers filter by date. Never partition on technician ID (high cardinality). Sort by `technician_id, ts` inside files so row-group stats prune. |
| `jobs` | Mutable | Full snapshot per cycle, in a versioned `snapshot=` directory | Full snapshots carry deletes automatically, so there is no tombstone machinery. |
| `invoice_line_items` | Mutable (edits, voids) | Same as `jobs` | Same reason. |

Contract terms:

- **Atomic snapshot swap.** Write the snapshot directory first. Update `_manifest.json` last, and only after validation passes. Keep the last 3 snapshots. Never overwrite in place, because an in-place overwrite lets Athena read a half-written table.
- **Late pings.** Rewrite the trailing 3 day-partitions each cycle, idempotently. The 3-day window is my assumption; confirm it against how long phones actually stay offline. Say the window in the contract.
- **File size.** Target 256-512 MB files and 128-512 MB row groups.
  - Most tenants are far smaller than that (a plumbing franchise's jobs table may be tens of MB). **Do not pad.** One file per partition or snapshot is correct for them.
  - The small-files problem is about thousands of files per query. Run compaction on closed ping partitions when a partition holds more than 100 files that are each under 75% of target (the AWS Glue trigger).
- **Format and types.** Parquet only. UTC timestamps. Money as integer minor units plus a currency code. Stable string IDs.
- **Catalog.** Publish Glue table definitions and the DDL for Athena, with the schema registered per version. Don't make customers infer schema from files.
- **No table format yet.** The snapshot pointer covers atomicity. Graduate to Iceberg if you move jobs and invoices to incremental, or customers complain about the pointer pattern. Those are the atomic-commit and time-travel triggers.
- **Privacy deletions.** A removed technician or a data-subject request is purged from the trailing window on the next cycle. Older ping partitions are rewritten on demand. State this in the contract.

## 3. Cadence and freshness posture

- **Rung: scheduled full-dump** for jobs and invoice lines. Run a fixed cycle every **6 hours**. Pings are the exception: append-only day partitions, with the trailing 3 days rewritten each cycle.
  - Promote to a faster cycle or log-based CDC only when full-snapshot compute and bandwidth exceed CDC's build cost, or a buyer needs an interval the dump can't meet.
  - CDC would commit you to primary-key upserts, explicit delete tombstones and a periodic full-scan reconciliation. Missed deletes are the known CDC failure.
  - If someone on the team has already run Debezium, that rung is cheaper than this ladder assumes.
- **Posture: fixed cadence. State it as such.**
  - Wording for the docs: "data is refreshed every 6 hours; this is not an SLA." You are making the Stripe-style fixed-cadence promise, not Amplitude's best-effort one or Fivetran's penalty-backed 99.9%.
  - `_manifest.json.last_completed_at` lets customers detect staleness themselves.
  - Do not offer a contractual SLA until delivery-success telemetry shows you can meet one.

## 4. Security and credentials

- **Never proxy bytes.** Customers read S3 directly. Your service authorizes and mints credentials, nothing more.
- **Isolation rung:** shared bucket with `tenants/<tenant_id>/` prefix isolation. Move to one access point per recipient when the bucket policy grows unwieldy (AWS bucket policies have a size limit) or when add-on tenants pass roughly 100. The 100 is self-set.
- **Path A (default, Athena and EMR customers):** a cross-account IAM role with an ExternalId, scoped to that tenant's prefix. The customer assumes the role through STS. Never issue static keys.
- **Path B (conditional, DuckDB users with no AWS identity):** a small credential-vending endpoint. An API-key call returns STS credentials scoped by session policy to the tenant prefix, with a TTL of about 1 hour. Build it only if pilot customers actually lack an AWS principal.
- **Encryption.** SSE-KMS with a regional customer-managed key and one KMS grant per recipient, so revoking one customer never touches another. Rotation must not re-encrypt history.
- **Access review.** Tie it to credential TTL, since expiry is the enforcement point. Offboarding means revoking one role and one grant.

## 5. Cost allocation and pricing

| Layer | Who pays |
|---|---|
| Storage | Tilepath. Priced into the add-on. |
| Query and reprocessing compute | Customer (their Athena, EMR or laptop). |
| Egress, same region | Free. |
| Egress, cross-region | Customer. Enable Requester Pays on the bucket, or require same-region reads. |

- **Open item on Requester Pays.** I have not verified that DuckDB's S3 reader handles Requester Pays. Test it in the pilot. If it doesn't, pin DuckDB users to same-region reads or Path B.
- **Do not eat cross-region egress silently.** Unattributed egress is the "bill shock" failure mode.
- **Pricing: paid add-on or top-tier gate, from day one.** Every vendor studied gates this feature class, and there is no free-tier precedent.
  - GPS pings dominate storage and egress, so a volume tier or a pings sub-add-on is worth considering.
  - Giving it away free would be a margin giveaway that later repricing can't easily claw back.
  - If you want to break precedent, record an argued decision. The gate is binary on that.

## 6. Schema-evolution contract

- **Add-only.** Append new nullable columns at the end. Never rename, remove or retype in place. The correct move for a rename is add-new, deprecate-old.
- **Consistency.** Column order and types stay identical across every batch.
- **Validation gate.** Before `_manifest.json` flips, validate the written schema against `_schema/vN.json`. On failure, keep the previous snapshot live and alert internally. Drift becomes your alert, not a customer ticket.
- **Four-part data contract per dataset:**
  - Schema: columns, types, nullability.
  - Quality: completeness thresholds, such as row-count sanity versus the source.
  - Freshness: the fixed 6-hour cadence.
  - Availability: stated without an SLA.
- **Unavoidable breaks.** Use the API-deprecation process: announced window, parallel columns or paths (`v1/` to `v2/`), dated removal. That machinery belongs to `api-versioning-policy`.

## 7. Compliance and residency

- **Region-pin from day one.** One bucket per region, with a regionalized KMS key.
  - If you have EU or UK customers, give them an EU bucket. Don't use one global US bucket. That choice silently commits you to SCC and Transfer Impact Assessment paperwork for every EU customer.
  - Remote access counts as a transfer. A US support engineer reading an EU customer's export is a regulated event.
- **GPS pings need the most care.** They are employee location data. If you can, offer pseudonymization (tokenized `technician_id`) as a pre-export option.
- **Localization countries** (for example India or China) are hard blockers. "Not offered in region X" is a legitimate, precedented outcome (Stripe does this for India).
- **Deliverable for the compliance review:** a per-route table of legal basis, data classes and whether pseudonymization applies. I can't fill it in until I know customer countries.

## 8. Rollout

1. **Pilot with 5-10 design partners.** Pick from the EMR/Spark churn-model accounts plus a couple of Athena and DuckDB teams.
   - Ship `jobs` and `invoice_line_items` first.
   - Add `gps_pings` second, because privacy review and volume make it the riskiest dataset.
   - Region-pin, catalog and per-recipient credentials from the start. Don't bolt residency on later.
2. **GA** with pricing and the stated freshness posture.
3. **Cadence upgrades** only when full-dump cost or a buyer's freshness requirement forces them.
4. **Build vs partner:** build the file-drop in-house. There is no warehouse sharing primitive to partner with here, because the native-share route is struck.
   - Revisit if a vendor's usage pricing crosses roughly the fully-loaded cost of 1-2 data engineers (self-set).
   - Revisit also if the Snowflake trigger fires.

## Gates

| Gate | Status |
|---|---|
| Contract completeness | Pass once schema files and the fixed-cadence wording ship. |
| Cost allocation named | Pass, pending the Requester Pays and DuckDB check. |
| Residency coverage | **Open.** Needs your customer-country list. |
| Premium gating | Pass once you pick the add-on or tier. |

## Failure modes to watch

- Silent schema drift.
- Small-files decay on the large tenants.
- Static shared keys.
- Unattributed cross-region egress.
- A free-tier launch.

Track after launch:
- Share of deliveries meeting the 6-hour cadence.
- Schema-break incidents (target: zero).
- Egress cost per recipient per month.

## What I need from you

1. Do any customers sit in the EU, the UK, or a localization-mandate country? This sets the bucket regions.
2. What did buyers actually say about freshness? If they said "hourly," the cadence rung changes.
3. Add-on or top-tier gate? And is there a deal deadline?