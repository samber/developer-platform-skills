**Do not sign off yet.** First action: send the 7 questions in section 6 to 5 enterprise accounts and your sales lead. That takes about 30 minutes. Three answers could flip the plan: where your data lives, how customers want to fetch files, and which regions they sit in.

I read the skill and all 3 references. Plan below assumes the doc is silent on anything I don't mention. Assumptions are in section 6.

## 1. Verdict

The doc fails all 4 binary gates from the skill:

- ❌ **Contract completeness**: no schema contract, no stated freshness posture.
- ❌ **Cost allocation**: nobody named as payer of egress.
- ❌ **Residency**: EU pinning is phase 4.
- ❌ **Premium gating**: pricing is "decide later" in phase 4.

Phase order follows what engineers enjoy building, not what customers need first. Targets are not achievable by 2.5 people in Q4.

## 2. Teardown

**Phase 1: in-house file transfer service. Cut.**
- "Own the protocol" buys nothing. Customers want data, not your protocol.
- Every production sharing system lets storage serve bytes. Server only authorizes and signs URLs. Proxied bytes make your fleet the throughput ceiling and the egress payer.
- Build vs partner: buy or use native primitives for standard paths. Fivetran bought Census instead of building. You have 2.5 people.
- Replace with: object storage, short-lived scoped credentials, a thin credential broker. About 1 week, not a phase.

**Phase 2: partitioned Parquet drops. Keep. Move first.**
- 62% of accounts (~211 of 340) have no warehouse. Files are the only shape they can use.
- Files also work for the 38% on Databricks (~129).
- Doc says "partitioned" but gives no contract. Section 3 fixes that.

**Phase 3: log-based CDC. Defer, with explicit triggers.**
- Default rung is scheduled full-dump: idempotent overwrite, deletes handled for free.
- CDC commits you to upsert-by-key, delete tombstones, and a periodic full-scan reconciliation. Missed deletes become phantom rows in every customer copy.
- It also loads the prod DB and your half-time SRE.
- Promote only when (a) full-dump bandwidth/compute bill exceeds CDC build cost, or (b) a named customer needs fresher data than the dump interval. Exception: if one of your engineers has run Debezium before, cost drops. Ask.
- Middle rung is incremental by `updated_at`. Check first that tables have reliable `updated_at` and soft deletes.

**Phase 4: EU pinning plus pricing. Wrong place, wrong time.**
- Region pinning is cross-cutting. Retrofitting it killed Segment's EU Data Lakes product. Put it in week 1.
- A global bucket silently commits you to SCC and Transfer Impact Assessment paperwork for every EU customer, forever.
- Every vendor studied gates bulk export behind a paid tier or add-on. No free precedent. Decide pricing before the first customer gets access, not after launch.

**Missing from the doc entirely**
- Native Delta Sharing for the Databricks cohort. Rationale in section 3.
- Credential model, cost allocation, schema-evolution rules, atomic publish of a dump.
- Definition of "adopted".

**Success criteria**
- "Export NPS above 40": you will have under 15 respondents. One answer swings the score by many points. Not a gate. Drop it.
- "25% of enterprise accounts adopted by Q4": 25% of 340 is 85 accounts. Today is 2026-10-08. Q4 ends in about 12 weeks, so that is about 7 onboardings per week. Customer-side setup alone breaks that. "Adopted" is also undefined. And "target accounts" may be prospects, not customers. Replacement in section 5.

## 3. Plan I'd run

**Camp: both, file-drop first.**
- The skill's default is native share first once 30-40%+ sit on one platform. You are at 38%, right at the self-set threshold.
- I re-rank on purpose. File-drop reaches all 340 accounts. Share reaches 129.
- Share effort assumes data already sits in Delta. Yours probably sits in an operational DB. Getting it there is the real cost.
- Delta Sharing ships second, backed by the same data. Interim for Databricks accounts: they can often read the bucket directly. Verify with 2 design partners.

**File layout contract (write it down)**
- Hive-style paths, max 2-3 low-cardinality levels. Tenant scoping via per-recipient prefix.
- CRM records are mutable. Partition mutable tables by `snapshot_date`. Partition activity/event tables by event date. Date-partitioning mutable entities misleads consumers.
- Files 256-512 MB. Compact when a partition has more than 100 files under 75% of target.
- Register schema in a catalog (Glue or Iceberg REST).
- **Atomic publish**: write the snapshot, then write a manifest or `_SUCCESS` marker last. Consumers read only marked snapshots. Otherwise a consumer reading mid-dump sees half a dataset.
- Stay on raw Parquet. Graduate to Delta only for the share path, where atomic multi-file commits are needed.
- Format risk: "just want files" may mean CSV or Excel users, not Spark users. Ask. If so, offer CSV as a second format, not the default.

**Cadence and freshness**
- Rung: scheduled full-dump. Stripe's fixed 3-hour cadence is the reference.
- Posture: **fixed cadence**, published. Start at one dump per 6 or 24 hours, whichever customers say is fine. No SLA, no penalty.
- Retain only the last N snapshots. This makes deleted records vanish from old files within a bounded window, which matters for GDPR erasure.

**Security and credentials**
- Shared bucket with prefix isolation. Move to per-recipient access points only if tenant count forces it.
- Per-recipient credentials, never static keys.
  - AWS recipients: cross-account role with ExternalId.
  - Customers with no cloud account, probably many of your 211: the broker mints presigned URLs or short-lived tokens. Customers fetch with `aws cli`, `rclone`, or a script.
- Per-recipient KMS key or grant, region-local.
- Tie access review to credential TTL.
- If customers demand SFTP, use a managed service. Do not build it.

**Cost allocation (write it before launch)**
- You host the bucket, so you pay storage and egress on every pull. Your doc assumes none of this.
- Fix: price the add-on to cover egress, with a fair-use volume cap. If a recipient has their own AWS account, requester-pays is an option.
- Cross-region reads cost more. EU bucket pulled by US users is egress.
- Delta Sharing to a remote-region consumer can leave you paying egress that scales with their query volume.
- Customer pays their own compute.

**Schema contract**
- Add-only: new nullable columns at the end. Never rename, drop, or retype in place.
- Same column order and types in every batch.
- Validate each written batch against the documented schema before the delivery counts as successful. Drift alerts you, not the customer.
- Breaking change: announced window, old and new columns in parallel, dated removal.

**Residency**
- One bucket and one key per region (EU, US to start). Customer's data home region decides placement.
- Support-engineer access to EU exports counts as a transfer. Gate it.
- Localization countries (India, China, Russia): "not offered" is a legitimate, precedented outcome. Write the list down.

**Pricing**
- Gate as enterprise-tier feature or paid add-on. Decide in week 1.
- Design partners get a free preview with a dated end, in writing.
- Flat per-account fee plus volume cap is simplest. Do not meter raw calls.

## 4. Timeline (my estimates, unvalidated against your stack)

Capacity: 2 DEs plus 0.5 SRE, about 2.5 FTE.

1. **Week 0-1 (Oct 8-16)**: answer section 6. Write data contract, region matrix, posture, pricing. Pick 8-10 design partners (5-6 file, 2-3 Databricks).
2. **Weeks 1-5 (to ~Nov 20)**: file-drop v1. Region-pinned buckets, broker, catalog, validation, atomic publish, full-dump job. 3 design partners reading by week 5.
3. **Weeks 6-9 (to ~Dec 18)**: Delta tables for the shared datasets, Delta Sharing to 2-3 Databricks partners. Compaction job. Remaining file partners.
4. **Weeks 10-12**: harden. Publish posture. Turn on pricing. Freeze before the holiday gap.
5. **Q1 2027**: CDC decision, only if a trigger fires.

Slip risk: Delta conversion. If data is not already in a lakehouse, expect weeks 6-9 to stretch.

## 5. Success criteria replacement

**Launch gates (binary, from the skill)**
1. Written data contract for every surface, with named freshness posture.
2. Who pays storage, compute, egress, written down, including cross-region.
3. Every regulated region present in the customer base has a posture: pinned, mechanism documented, or not offered.
4. Export sits behind a paid tier or add-on.

**Adoption (define it)**
- "Adopted" = account with at least 1 successful read in each of the last 4 weeks.
- Q4 target (self-set, my proposal): 8-10 design-partner accounts adopted, 0 schema-break incidents.
- 25% (85 accounts) is a plausible stretch for mid-2027, once self-serve onboarding exists. Confirm against sales cycle.

**Trends, not thresholds**
- Share of deliveries meeting stated posture.
- Time from credential issue to first successful read.
- Egress cost per recipient per month.
- Add-on attach rate once pricing is on.
- Replace NPS with 5-8 design-partner interviews.

## 6. Open questions

Each has my assumption and what flips the plan.

1. **Where does the source data live, and does a lakehouse exist?** Assumed: operational DB, no lakehouse. If already in Delta, move Delta Sharing to week 1-5.
2. **Are the 340 customers or prospects?** Assumed: mix. Changes who gets design-partner access and the adoption denominator.
3. **Do file-only accounts read Parquet?** Assumed: yes, some via Spark/DuckDB/Python. If Excel/BI users, add CSV.
4. **Freshness demand from actual buyers?** Assumed: daily is fine. If hours, dump interval shrinks; if minutes, CDC trigger fires.
5. **Regions and EU share of the 340?** Assumed: some EU. If none, residency drops to a documented stub. If India/China, mark not offered.
6. **Your cloud, and recipients' clouds?** Assumed: one primary cloud for hosting. Mixed recipient clouds raise egress.
7. **Pricing intent and any CDC experience on the team?** Assumed: add-on, no prior Debezium. Prior CDC experience moves phase 3 earlier.

Next action: forward section 6 to your sales lead and book 3 customer calls this week.