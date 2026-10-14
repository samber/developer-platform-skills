# Quarrystone export layout: recommendation

**Don't greenlight "migrate to Iceberg" as the fix.** The 40-second queries come from the file layout, and Iceberg doesn't change that layout. Fix the layout first, and keep Iceberg as a later option with defined triggers.

I followed `bulk-data-sharing-design`. I didn't ask its clarifying questions, so the assumptions are listed at the end.

## Why queries are slow

Your layout is `customer_id=/session_id=/hour=/part-*.json.gz`. It has four problems:

1. **Files are far too small.** At 0.2 MB each, a large account writes about 115k files a week. AWS measured this case: 582,000 files of 0.14 MB took 40 s in Athena. After compaction to 336 files of 247 MB, the same query took 9.7 s. Your numbers sit on that benchmark. The target is 256–512 MB files.
2. **`session_id` is a partition key.** It is high-cardinality, which the skill forbids. It creates one directory per session, so most partitions hold a single tiny file. Athena spends its time on S3 LIST and GET calls and planning.
3. **The format is gzip JSON.** Gzip is not splittable. JSON has no column pruning or predicate pushdown, and the data is up to 6× larger than Parquet.
4. **`customer_id=` is probably redundant.** If each customer has their own bucket, every path carries a constant prefix. Drop it. If you use a shared bucket, see the assumptions below.

## Recommended layout

```
s3://<customer-bucket>/quarrystone/events/dt=2026-10-08/part-<batch_ts>-<n>.parquet
```

| Item | Contract |
|---|---|
| Partition | One level: `dt=YYYY-MM-DD` (UTC event date). Hive-style, so Athena, Spark and DuckDB can prune partitions. |
| Dropped keys | `session_id` and `hour` become columns. `customer_id` becomes a column only in a shared bucket. |
| Format | Parquet with zstd or snappy compression. Typed core columns: `event_id`, `event_time`, `session_id`, `user_id`, `event_name`, and so on. |
| Custom properties | Store arbitrary event properties as one JSON-string column, so customer-defined properties don't change the schema. |
| Within-file sort | Sort by `event_time`, then `session_id`. Parquet column statistics then let queries skip row groups by time or session. |
| File sizing | Row groups of 128 MB or more. Files up to 512 MB where volume allows (see below). |
| Catalog | Register the table in Glue with partition projection on `dt`. Customers get a ready-made Athena table instead of inferring schema from files. |
| Docs | Publish the layout, the schema, and a copy-paste `CREATE EXTERNAL TABLE`. |

## File count: cap the number, not the size

Your large account writes about 100 GB of gzip JSON a month, roughly 3 GB a day. As Parquet that is about 1–1.5 GB a day. That means:

- **Largest accounts:** one batch every 3 hours gives 8 files a day, about 150 MB each. That is 240 files a month, down from 500,000.
- **Most of your 700 accounts:** they will never fill a 256 MB file. Don't wait for size. Write one file per customer per batch interval. At most 24 files a day, and tiny files are harmless at that count. A week of data is under 170 files.
- **The rule to publish:** at most N files per `dt` partition per customer, with N derived from the batch cadence. Customers query by date, so a stable file count matters more than file size.

Write finished files at the source. Buffer per customer, convert to Parquet, and flush at each batch boundary. Don't write small files and compact them afterwards.

## Cadence and freshness

- **Start at the skill's default rung:** a batch every 3 hours (Stripe's reference cadence). Pick the interval from what your buying customers need, which I haven't confirmed.
- **Publish the posture explicitly.** Choose fixed cadence, best-effort or contractual SLA, and say which. I recommend best-effort ("delivered within 3 hours"), because a penalty-backed SLA is a legal commitment.
- **Append-only batches.** Each batch adds new part files, and late events go into the partition for their event date. Never rewrite published files in raw Parquet, because a reader mid-query would see duplicate or missing data.

## Where Iceberg fits

The skill says to graduate to a table format only for atomic multi-file commits, time-travel, or in-place schema evolution. Revisit Iceberg if one of these happens:

1. **You need deletes.** Product analytics usually has GDPR erasure requests. If you must delete events from files already delivered, rewriting raw Parquet is unsafe. Iceberg's row-level deletes and atomic commits solve this. I think this is the most likely trigger.
2. **You want to compact after delivery.** Sub-hour freshness would bring back small files. An Iceberg table can swap in compacted files atomically. Raw Parquet can't.
3. **Customers ask for time-travel or snapshots.**

Iceberg has costs. You would need a catalog in every customer account, and your writers would need to commit to it. Customers on engines without good Iceberg support would also be worse off. None of this fixes your current problem.

## Other contracts

- **Schema:** add-only. New columns are nullable and go at the end. Never rename, remove or retype a column in place. Validate each batch's written schema against the documented contract before counting it as delivered, so drift raises an alert instead of a customer ticket. A breaking change needs an announced window and parallel old and new columns.
- **Credentials:** write into the customer's bucket through a cross-account role with an ExternalId, scoped to the `quarrystone/` prefix. No static keys.
- **Encryption:** support the customer's SSE-KMS key, with a per-customer KMS grant.
- **Cost:** the customer pays for storage and for their own Athena queries. You pay egress if your writers are in a different region from the customer's bucket. Write from the same region where you can.
- **Residency:** the data stays in the customer's chosen bucket region, so region-pinning comes with the layout. Document that posture per customer region.
- **Pricing:** export sits behind a paid tier or add-on. No vendor the skill studied gives it away free.

## Migration plan

1. **Prove it before committing.** Take one large account and write one week into the new layout in a test bucket. Run the customer's real Athena query on both layouts. The AWS benchmark suggests about 4× or better, but that is a hypothesis for your data until you measure it. This is the gate before any other work.
2. **Dual-write.** Ship the new layout under a new prefix (`quarrystone/events/`) next to the old one. Announce the old layout's deprecation with a dated removal window.
3. **Backfill.** Rewrite history into daily Parquet for customers who ask. Do this as a one-off job, not a live compaction.
4. **Retire the old layout** after the window.
5. **Only then** decide on Iceberg, using the triggers above.

## Assumptions to confirm

I haven't asked you any of these, and each could change the design:

1. **Do customers have their own buckets, or is it a shared bucket?** If shared, `customer_id=` stays as a leading prefix with per-recipient access points or isolation.
2. **Do customers already use Snowflake, Databricks or BigQuery?** The skill makes native sharing the default when 30–40% or more of accounts sit on one platform. I assumed none do, because you already ship to S3.
3. **What freshness do buying customers need?** I assumed 3 hours is fine. Hourly or faster changes the compaction story above.
4. **Do you handle deletion or erasure requests on delivered events?** If yes, Iceberg moves up the list.
5. **Which regions are your customers in?** Any China or India customers could mean a localization block.
6. **Is export gated today, and what are the delivery deadline and engineering budget?** A tight deadline favors the layout fix alone.