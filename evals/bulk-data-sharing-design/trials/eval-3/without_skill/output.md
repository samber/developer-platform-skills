**Don't greenlight "migrate to Iceberg" as the fix.** The layout causes the 40 seconds, and Iceberg on top of the same tiny JSON files would still be slow. Ship plain Parquet in daily partitions first. Offer Iceberg later as an opt-in.

## Why queries take 40+ seconds

1. **Too many files.** A large account writes about 500k files a month, so a one-week query opens about 115k objects. Athena pays a LIST and a GET round trip per file. At 0.2 MB each, that overhead is most of the runtime.
2. **Wrong partition order.** `session_id` sits above `hour`. A time filter can't prune by session, so Athena walks every session prefix. Session cardinality is huge, which also bloats Glue partition metadata.
3. **`customer_id=` is probably a dead partition.** Each customer gets their own bucket, so every query filters on a single value. Confirm this is true for all 700 accounts.
4. **JSON in gzip.** Athena can't split a gzip file. It reads every byte of every column and parses text. Parquet reads only the columns the query names and skips row groups using min/max statistics.

## Recommended export layout

```
s3://<customer-bucket>/quarrystone/v2/events/event_date=2026-10-07/part-<run_id>-0000.zstd.parquet
```

- **Format:** Parquet with zstd compression. Athena supports zstd.
- **Partition:** `event_date=YYYY-MM-DD` only, in UTC. Skip `hour`, `session_id` and `customer_id`.
- **Columns:** `session_id`, `user_id`, `event_name`, `event_ts` and the other core fields become typed columns, not path segments. Keep volatile custom properties in one JSON string column, or a `map<string,string>`. A stable schema keeps the Glue table simple.
- **File size:** Target 128–512 MB per file, with 128 MB row groups. A large account writes about 100 GB of JSON.gz a month, or about 3.3 GB a day. That compacts to roughly 5–20 Parquet files a day. Check the exact ratio in the benchmark.
- **Small accounts:** One small file per day is fine. Don't split further.
- **Sort order:** Sort within each file by `event_name`, then `event_ts`. Row-group statistics then prune well on the most common filters. Test whether adding `session_id` helps.
- **Table registration:** Ship DDL that uses Athena partition projection on `event_date`. Queries then skip Glue partition lookups entirely.
- **Hive-style path:** `key=value` in the path keeps the layout readable by Snowflake, Spark, DuckDB and BigQuery.

## Write path

You can't write 256 MB files in real time, so use two tiers:

1. **Staging.** Buffer per customer per hour and write Parquet to `quarrystone/v2/_staging/`, outside the table location. A large account produces about 50 MB an hour.
2. **Daily compaction.** After the day closes, merge the staging files into the `event_date=` partition. Write new files first, then delete the staging files. Never mutate a partition in place while customers may be querying it.

The catch is freshness. Customers see yesterday's data in the clean layout. If you promise sub-hour freshness, tell me. In that case you'd expose staging through a second table, or accept that "today" queries are slower.

## Expected result

For a large account over one week:
- Files drop from about 115k to about 70–140.
- Bytes scanned drop several-fold, because the query reads only the columns it needs.
- Athena time should land in the low seconds, not tens of seconds.
- The Athena bill falls with the bytes scanned ($5 per TB).

These are estimates, not measurements. Prove them before migrating anyone.

## Where Iceberg fits

**What it gives you:**
- Atomic commits.
- Managed compaction.
- Schema evolution.
- Hidden partitioning.
- Row-level deletes, which help with GDPR erasure.

**What it costs in your setup:**
- You write into 700 customer-owned accounts. Each Iceberg commit needs catalog access in their account (Glue or similar), and metadata files land in their bucket.
- Every customer's query engine must support Iceberg. Older Athena setups, Redshift Spectrum configurations and customer ETL tools vary in support.
- Snapshots keep old data files alive until expired, so you need a snapshot-expiry job on every customer table or their storage bill grows.
- You take on operational ownership of 700 tables.

**Recommendation:**
1. Ship Parquet with daily partitions now. It works with every engine.
2. Treat Iceberg as an opt-in tier for customers who ask for it, built on the same Parquet files. You can register existing Parquet files into an Iceberg table without rewriting them.
3. Parquet in the right layout is the prerequisite either way. Starting with Iceberg doesn't skip it.

## Migration

- Write to the new `v2/` prefix and leave the old layout untouched.
- Dual-write for a deprecation window (suggest 60–90 days) with a published sunset date.
- Backfill history with Athena CTAS or a Spark job, one customer at a time, starting with the largest accounts, which hurt most.
- Don't convert in place.

## Benchmark before you commit (about 2 hours)

1. Pick one large account and one week of data.
2. Run Athena CTAS to write Parquet with zstd, partitioned by `event_date`, then set the bucket count so files land at 128–256 MB.
3. Run the customer's slowest real query on both tables. Record runtime, bytes scanned and file count.
4. Test a second query that filters on `event_name` to check sort-order pruning.
5. If the speedup is under 5x, I'm wrong, and we revisit.

## Open questions for you

1. Does every customer have their own bucket? If any share one, `customer_id` needs to stay as the top-level prefix.
2. What freshness do you promise: hourly or next-day?
3. Which query engines do customers use? If it's mostly Athena, the Iceberg opt-in can wait. If it's a Snowflake/Databricks mix, it may come sooner.
4. How stable is the event schema? Heavy custom properties push toward the JSON-column approach.

**Next:** Pick the large account for the benchmark, and give me its bucket access path so I can write the CTAS.