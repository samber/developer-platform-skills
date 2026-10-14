**Verdict: do not sign.** Phases 1, 3 and 4 and both success criteria need to change. Phase 2 is right, but it is not enough for the file-only accounts.

## What breaks

1. **Phase 1 (own file transfer service) is the worst item.**
   - Nothing about owning the protocol helps a customer. Customers want the data to arrive.
   - Managed object storage, signed URLs and managed SFTP already do this.
   - A custom service gives you an auth and tenant-isolation surface to defend. Two DEs and a half-time SRE cannot carry it, and it would eat the whole quarter.
   - Cut it. Buy it.

2. **Phase 2 (Parquet) fits only the Databricks accounts.**
   - About 129 accounts (38% of 340) are on Databricks. Parquet works for them.
   - The other ~211 "just want files". Distributor staff open files in Excel, so ship CSV too, or Parquet will go unread.
   - The doc ignores Delta Sharing, which is the native Databricks path. Treat it as an option, not a day-one build.

3. **Phase 3 (log-based CDC) is premature.**
   - Customers asking for files want daily or hourly increments, not sub-minute streams.
   - CDC also publishes your internal OLTP schema as a contract. Every migration then breaks customers.
   - Replace it with incremental drops (by `updated_at`, plus tombstones from `deleted_at`).
   - Do CDC only when real demand shows up (see "Gated, not scheduled").

4. **Phase 4 is in the wrong place.**
   - EU pinning is a design parameter. Making region a per-tenant setting on day one is cheap. Retrofitting it after data lives in one region is expensive.
   - Pricing decides scope and what counts as adoption. Set a posture before building, not after.

5. **The doc leaves out the pieces that decide whether this works:**
   - A versioned export schema (data contract).
   - Per-tenant credentials and isolation.
   - Atomic publish, so customers never read half-written files.
   - Freshness monitoring and alerting.
   - Backfill and late-arriving data.
   - Deletes and PII handling.
   - Schema documentation.

6. **"Export NPS above 40" is a bad success criterion.**
   - Only adopters answer, so the sample is small and biased.
   - It lags usage and says nothing about whether data is consumed.

7. **"25% adopted by Q4" is not reachable.**
   - 25% of 340 is 85 accounts. Today is 2026-10-08, so you have about 12 weeks (assuming Q4 means calendar Q4).
   - "Adopted" is undefined.
   - With about 2.5 people, 85 onboardings in 12 weeks only works with full self-serve, and self-serve is not built.

## The plan I would run

Capacity: 2.5 FTE for 12 weeks is about 30 person-weeks. Reserve ~25% for support and on-call, which leaves ~22 for building.

**Weeks 0-2: validate and decide**
- Pick 8-10 design partners: 4 on Databricks, 5-6 file-only, and 1-2 EU accounts if you have any.
- Interview them. Find out who consumes the files (analyst, ERP admin, BI tool), the format they want, and the freshness they need.
- Decide pricing posture: included in the enterprise tier until end of Q2 2027, then revisit with usage data. This removes pricing as an adoption variable.
- Write export contract v1: core entities, stable IDs, `deleted_at` tombstones, schema version field.

**Weeks 2-6: MVP, file-only first**
- Nightly full snapshot plus incremental drops per tenant.
- Formats: Parquet and CSV, partitioned by date.
- Tenant-isolated prefix in a region-pinned bucket. Region is a tenant setting, and the EU bucket exists from the start.
- Delivery: two options, both on managed services.
  - Push into the customer's own bucket via a cross-account role.
  - Hosted bucket with signed URLs or managed SFTP, for customers with no cloud account.
- Each drop ships a manifest (row counts, checksums, schema version, watermark) and a success marker, published atomically.
- Freshness SLO, failure alerts, one runbook. The half-time SRE owns this and nothing custom.

**Weeks 6-10: Databricks path and design-partner feedback**
- Ship docs and a notebook template (Auto Loader or external table over the drops).
- Ask the 4 Databricks partners whether Unity Catalog and Delta Sharing would beat bucket access. Build it only if at least 3 say yes.
- Add hourly increments only for partners who ask.

**Weeks 10-12: general availability**
- In-app self-serve: create credentials, choose format and schedule, view delivery history.
- Enable enterprise accounts in waves of about 20-30, not all at once.
- Revisit the pricing posture with usage data.

**Gated, not scheduled (2027)**
- CDC: start only if at least 5 accounts name a use case that needs data fresher than 15 minutes.
- Delta Sharing: see the gate above.
- Warehouse-native sharing for other platforms (e.g. Snowflake): only on named demand.
- Write the kill or continue rule down now, so these do not creep back in.

## Success criteria to replace the old ones

- **Adopted** means: the customer fetched files from 2 consecutive scheduled deliveries and keeps pulling for 4 weeks. Delivery alone does not count.
- Weeks 0-12:
  - 10-15 accounts adopted by 2026-12-31 (about 3-4% of 340).
  - Time to first consumed file under 2 days.
  - Freshness SLO met on at least 99% of deliveries.
- By end of Q2 2027: 25% of enterprise accounts adopted, conditional on self-serve working. This is my estimate, so confirm it.
- Business outcome (track it, do not gate on it): deals unblocked or renewals tied to export, counted from CRM notes.
- Support load: tickets per adopted account. If it does not fall, self-serve is not working.
- Keep NPS as a survey, not a target.

## Open questions that change the plan

1. Do you have EU accounts, and are any of them blocked on residency today?
2. Is there evidence beyond the doc that file-only accounts want files, such as tickets or lost-deal notes?
3. Which cloud are the Databricks accounts on (AWS, Azure or GCP)?

**Next (2 minutes):** answer question 1. It decides whether EU pinning moves into the MVP.