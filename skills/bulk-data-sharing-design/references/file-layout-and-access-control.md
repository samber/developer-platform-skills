# File layout, partitioning, and access-control mechanics

## Partitioning contract

- **Choose partition keys by consumer query pattern**, never by internal schema: time keys (year/month/day) for event data, business keys (tenant, region) for domain-scoped exports. The first design question is "what will the consumer filter on," not "what columns exist."
- **Hive-style paths are the convention every engine expects**: `year=2026/month=08/day=30/...` - this is what lets Athena, Spark, and Presto prune whole partitions instead of scanning every file. Name it in the contract so consumers know pruning works.
- **Cap at 2-3 partition levels using low-cardinality keys** (date, region, event type - never user ID). Beyond that, S3 LIST-call overhead inflates independently of file size (the "partition trap"), and metadata overhead slows query planning.
- **Both over- and under-partitioning are real failure modes**: too many small partitions inflate planning time; too few large ones kill parallelism. State an intended partition-file-count range in the contract, not just the key names.
- **Row groups: target 128-512 MB**; files: target 256-512 MB (Amplitude's own recommendation is ~500 MB within a 1 MB-5 GB observed range). Large enough to amortize I/O, small enough not to blow distributed-engine memory.
- **Keep column ordering and types consistent across batches.** Partition pruning (across files) and predicate pushdown via Parquet column statistics (within files) compound - inconsistent batches break the second mechanism silently.

## Compaction

- Small files are a measured penalty, not folklore: an AWS benchmark saw an Athena query over 582,000 small files (0.14 MB each) take 40 seconds, dropping to 9.7 seconds after compaction to 336 files of 247 MB - roughly a 4x improvement from compaction alone.
- A concrete trigger to copy (AWS Glue's managed Iceberg compaction): compact when a table or partition exceeds 100 files that are each smaller than 75% of the target file size.

## Format and table-format graduation

- **Parquet over CSV/JSON by default**, with AWS's own numbers: Parquet unloads up to 2x faster and up to 6x smaller on S3 than the same data as text.
- **Register the schema in a catalog** (Glue, Hive Metastore, Iceberg REST, Nessie) rather than relying on file-embedded metadata - this is also where schema versions live for the evolution contract.
- **Graduate raw Parquet to a table format (Iceberg, Delta Lake, Hudi) only when the export needs**: atomic multi-file commits, time-travel/rollback, or in-place schema evolution across batches. Delta's `_delta_log/` and Iceberg's `metadata.json` give these by construction. Below that bar, raw partitioned Parquet is cheaper to operate.
- Consuming warehouses can absorb additive changes without breaking loads - BigQuery's `ALLOW_FIELD_ADDITION` on Parquet appends, ClickHouse matching Parquet columns by name with automatic compatible-type casting - which is exactly why the evolution contract's add-only posture works: additions degrade gracefully, renames do not.
- The Avro alternative: schema-registry-based evolution instead of file-embedded schemas - the reason Braze Currents' streaming adopters chose it. Relevant only on the streaming rung.

## Multi-tenant isolation ladder (AWS's four patterns, in maturity order)

1. **Dedicated bucket per tenant** - simplest to reason about; stops scaling at modest tenant counts (bucket service limits, per-bucket operational load).
2. **Shared bucket with prefix isolation** - cheaper to operate; isolation now rides entirely on correct IAM prefix-condition policies.
3. **One access point per recipient** - decouples each partner's access path from a single ever-growing bucket policy; the answer to "share one bucket with many externals without their permissions colliding."
4. **Session broker + short-term credentials** - STS credentials minted per request by a broker evaluating caller context; the advanced rung.

Move up only as tenant count forces it. Cross-account multi-region access points extend pattern 3 when a recipient needs regional locality.

Adopt the provider/subscriber vocabulary (AWS's data-mesh framing) in design docs - it maps one-to-one onto Delta Sharing's provider/recipient terms, so one document describes either mechanism.

## Credentials and encryption, per cloud

The pattern is identical everywhere - time-boxed signed access, per-recipient key-based decryption, rotation without re-encryption - so specify it once and map it per recipient cloud:

- **Cross-account IAM roles with an ExternalId (AWS)** - the recipient assumes a role via STS instead of receiving key material; AWS frames this explicitly as the answer to key distribution, and it is how Segment operated compute inside customer accounts. Never distribute static keys.
- **Pre-signed URLs (AWS) / SAS tokens (Azure)** - time-boxed GET/PUT links; real configurations run as short as 300-second expiry. Delta Sharing, BigQuery, and Snowflake all use signed URLs or short-lived tokens as the underlying recipient-read mechanism.
- **Per-recipient KMS grants** - AWS Data Exchange creates one KMS grant per subscriber, so each recipient decrypts only their entitled data and revoking one never touches another. This is the per-recipient credential principle at the encryption layer.
- **CMEK/SSE-KMS with audit trail** - customer-managed keys give a CloudTrail record of every decrypt and support cross-account decryption via key policy. Rotation (AWS KMS, GCP Cloud KMS) applies the new key version going forward while prior versions keep historical data readable - rotation never forces re-encrypting the archive.
- **Snowflake Tri-Secret Secure** - the CMEK equivalent layered into Snowflake's own sharing.
- **Per-file Parquet encryption** - a unique key per file, underneath bucket/transport encryption; the finer-grained option when one shared bucket serves recipients with genuinely different trust levels.

Access-review cadence: expiration is the enforcement point in every one of these mechanisms (Delta Sharing tokens, presigned URLs, STS sessions), so pin the review/renewal cycle to the credential TTL rather than running it as an unrelated calendar process.
