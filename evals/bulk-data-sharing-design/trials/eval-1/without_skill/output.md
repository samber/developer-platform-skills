**Ship one thing: a scheduled, incremental Parquet export, delivered as files to the customer's own S3 bucket.** Add a pull fallback for customers without S3. Delete "Snowflake sharing (later)" from the roadmap.

## Shape

Name: **Tilepath Data Export**. It's one export format with two delivery modes.

| | A. Push to customer S3 (headline) | B. Pull from Tilepath bucket (fallback) |
|---|---|---|
| Who | Athena and EMR users, AWS data teams | DuckDB on a laptop, non-AWS users |
| Setup | Customer creates a cross-account IAM role with external ID. Tilepath assumes it and writes. | Customer clicks "Enable". API returns short-lived presigned URLs or scoped read-only creds. |
| Format | Identical in both modes | Identical in both modes |

- Both modes use one writer job and one layout.
- Mode B costs little extra, and it lets you ship before every customer finishes IAM setup.
- Add GCS or Azure Blob targets only if a real account asks.

## Layout

```
s3://<bucket>/<prefix>/v1/<table>/dt=YYYY-MM-DD/part-0001.parquet
s3://<bucket>/<prefix>/v1/_manifest/run=<timestamp>.json
```

- **Format:** Parquet with zstd compression. Hive-style `dt=` partitions work in Athena, DuckDB and Spark with no extra tooling.
- **Manifest per run:** lists files, row counts, schema version, and high-water-mark timestamp per table. Consumers read it to learn what's complete.
- **No Iceberg or Delta in v1.** Plain Parquet covers all three engines your customers use. Revisit if 5 or more accounts ask.
- **Tenant isolation:** one prefix per account. Mode B uses per-tenant KMS keys and a bucket policy scoped to that prefix.

## Tables

1. `jobs`
2. `job_status_history`
3. `customers_sites`
4. `technicians`
5. `invoices`
6. `invoice_line_items`
7. `gps_pings`

**Rules for every table**
- Each table has a stable primary key and `updated_at` in UTC.
- Money is `decimal(18,4)` plus a `currency` column.
- IDs are strings.
- Schema changes are additive only. A breaking change means a new `v2/` path, with `v1` kept for 12 months.

**Change tracking**
- Every table gets an append-only `_changes` feed: row, `op` (`upsert` or `delete`), `updated_at`. The feed is hourly.
- Deletes are tombstones, because user-owned rows are soft-deleted.
- Small dimension tables (customers, technicians) also get a daily full snapshot. Analysts then don't need to dedupe a change feed to get current state.
- Ship an Athena view and a DuckDB query for "latest row per key". Most churn models want exactly that.

**GPS pings are the hard one**
- Volume dominates everything else, so partition by `dt` plus hour.
- Write small hourly files, then compact daily. Compaction avoids the small-files problem that slows Athena.
- Sensitive location data of employees: gate it behind an admin-only toggle, log every enable and disable, and allow a retention setting.
- Offer an option to pseudonymize `technician_id`.
- Have legal check GDPR and CCPA before GA. The customer is the controller, but you still need a clear data-processing story.

## Docs and DX (this decides adoption)

- Athena: ready-made `CREATE EXTERNAL TABLE` DDL or Glue crawler config for every table, using partition projection.
- DuckDB: one-line `read_parquet('s3://…/dt=*/*.parquet', hive_partitioning=true)`.
- PySpark: a three-line example.
- A schema reference page with column types and an ERD.
- A "migrate off your scraper" guide that maps REST endpoints to export tables.
- A dedicated docs page per engine, so each data person finds their path.

## Why not Snowflake sharing

- 0 of 120 surveyed top accounts use Snowflake, Databricks or BigQuery.
- Native sharing needs a provider account, region replication and ongoing ops cost, all for zero demand.
- If a Snowflake customer ever appears, they can already read your Parquet from S3 through an external stage. The export covers them at no extra build cost.
- **Replace the roadmap line with a trigger rule.** For example: "Revisit warehouse-native sharing when 10 or more paying accounts, or one deal over $X ARR, require it." Put the rule in the roadmap doc so the line stops being re-added.

## Phases

1. **Weeks 1–6: MVP**
   - Mode A, all tables except GPS.
   - Hourly changes, daily snapshots, manifests.
   - Athena, DuckDB and Spark docs.
   - 5–10 design-partner accounts from the top 120, including one Athena user and one EMR user.
2. **Weeks 7–10: GPS and Mode B**
   - GPS table with compaction and the privacy controls.
   - Pull mode with presigned URLs.
   - Backfill: a one-time historical export on enable, for example 24 months.
3. **Weeks 11–14: GA**
   - Packaging decision.
   - Self-serve setup UI with a connection test.
   - Run-failure alerts and an export health page.
   - Rate-limit or deprecate heavy REST scraping, with a migration notice.

These estimates assume your pipeline can already read changes by `updated_at`. If not, add several weeks for change capture.

## Success measures

- Top-120 accounts that enable the export within 90 days.
- REST API request volume from known scraper clients, which should drop.
- Support tickets about data access.
- Export freshness: the share of runs finished within the hourly window.

## Decisions for you

1. **Packaging:** include it in the top tier, or sell it as an add-on? I recommend the top tier plus the highest-volume tier of GPS retention. This is your call, and it affects costs below.
2. **Regions:** same-region S3 writes are cheap. Cross-region egress is not. Decide whether to write only in the customer's chosen region.
3. **Long tail:** the survey covered only the top 120 of about 1,900 accounts. Smaller accounts probably want CSV or Excel from the UI, not Parquet. Keep that as a separate, small item. Don't let it bloat this project.

**Next action (under 2 minutes):** pick the 5–10 design-partner accounts from the survey and ask your data owners about their AWS region and IAM comfort.