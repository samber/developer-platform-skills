# Vantablue bulk export: what must change before you scale

**Verdict:** the single global us-east-1 bucket is the problem. Three of your four facts are residency failures, not three separate issues. Fix the architecture, and the SCC paperwork, the Manila access and the India answer mostly resolve together.

I applied `bulk-data-sharing-design` and its compliance and access-control references. I did not read `vendor-case-studies.md`, so none of the vendor precedents below rely on it. I'm not a lawyer. Points marked ⚠️ need counsel to confirm.

## Gate scorecard (from the skill)

| Gate | Status | Why |
|---|---|---|
| Residency coverage | ❌ Fail | EU customers sit on an unpinned global bucket. The SCC/TIA documentation is unverified. |
| Cost allocation named | ❌ Fail (likely) | It's your bucket, so you pay storage and egress by default. See change 5. |
| Contract completeness | ❓ Unknown | I haven't seen a written schema or freshness posture. Check this. |
| Premium gating | ❓ Unknown | "Everything exports" suggests it's bundled free. Check this. |

## 1. "SCCs signed with every EU customer, so we're covered" is not sufficient

- **SCCs are only step 2 of the transfer analysis.** Since Schrems II, SCCs need a documented Transfer Impact Assessment on top. Ask counsel for the TIA, not only the signed clauses.
- **Remote access is a transfer.** Manila support staff querying EU names, national IDs and salaries through Athena is the same regulated event as copying the files out.
- **That is a second transfer, separate from the one to the US.** The skill's reference doesn't cover the Philippines' adequacy status. I'd assume no EU adequacy decision for it, so counsel should confirm.
- **Your customer SCCs probably don't cover Manila.** ⚠️ Counsel must confirm that all of these hold:
  - Manila is disclosed as a sub-processor or affiliate processing location.
  - The onward-transfer terms are flowed down.
  - A TIA exists for the Philippines specifically.
  - Customers were given sub-processor notice.
- **The US leg has its own question.** ⚠️ Is a transfer mechanism documented for us-east-1 itself? Counsel should answer that separately.
- **Meta's €1.2B fine (2023) was for transfer failures.** That is the downside the skill cites. A payroll SaaS holding national IDs and salaries is a worse data class than most.

**Fastest check:** ask counsel one question: "Does our TIA cover (a) storage in the US and (b) remote access from the Philippines to national-ID and salary data?" If either answer is no, you have a live gap today. Whether any past access needs further assessment is also a counsel decision. CloudTrail and Athena query history will show what Manila has read.

## 2. Region-pin the data (the architectural fix)

Do this before more EU customers land in us-east-1.

1. **Add a `data_residency` attribute per tenant** (EU, US, and later IN). The export job routes on it. There is no global default.
2. **Create an EU bucket** (for example eu-central-1 or eu-west-1) for the roughly 1,070 EU customers (41% of 2,600).
3. **Create a regional KMS key per region**, with key policy blocking use outside it. A key that stays in the EU closes the "it's encrypted, so it doesn't count" loophole, which regulators reject.
4. **Migrate existing EU data**, then delete the originals from us-east-1. Include the places people forget:
   - object versions and replicas
   - the Athena query-results bucket, which holds PII copies
   - logs and any backups
5. **Segment is the cautionary precedent.** It killed its EU Data Lakes product rather than retrofit compliance onto a US-region design. Retrofitting gets harder with every added customer, so do it now.

## 3. Manila's direct Athena access must stop

**Debugging failed exports rarely needs the payload.** Give support what they actually need, in order of preference:

1. **Metadata-first tooling.** Show export job status, row counts, file sizes, schema-validation results, partition listings and error logs. No PII fields. This likely covers most of the "several times a week" cases.
2. **A pseudonymized replica for debugging.** Tokenize or strip names, national IDs and salary before anything crosses a region. After that it is no longer personal data in the GDPR sense, which is the skill's pattern 3.
3. **Break-glass payload access, only when needed:**
   - Access is granted by an EU-region session broker minting short-lived STS credentials.
   - It is scoped to one tenant and one export, and time-boxed.
   - Every decrypt is auditable through CloudTrail on the regional KMS key.
   - Access is ideally performed by EU-located staff. Manila access to EU payload data needs the legal basis from section 1 first.
4. **Delete the standing access.** Athena should not hit the production bucket from a team-wide role. Static or shared credentials mean one leak or one offboarding affects everyone.

## 4. Per-recipient access instead of one shared bucket

- Check how customers read the data today. If they use shared or static keys, replace them.
- **Dedicated buckets for 2,600 tenants don't scale.** The skill's ladder is dedicated bucket, then shared bucket with prefix isolation, then per-recipient access points, then broker-minted credentials. Move to **access points per recipient** (or a broker) as the next rung.
- **Credentials:** cross-account IAM roles with an ExternalId for AWS recipients, SAS tokens for Azure, and a KMS grant per recipient so revoking one never touches another.
- **Never proxy bytes through your API servers.** Clients should read storage directly via signed access.
- **Align access reviews with credential TTL**, because expiry is the enforcement point.

## 5. Write down who pays what

- **The skill's file-drop model assumes the customer owns the bucket** (Segment's pattern). Yours is Vantablue's bucket, so Vantablue pays storage and egress by default.
- Pick one, in writing:
  - **Deliver into the customer's own bucket** by cross-account replication. They pay storage and compute.
  - **Keep your bucket with Requester Pays**, or charge for the export.
- **Egress is the decisive line item.** Cross-region transfer can reach up to 70% of data-transfer cost, per Snowflake's own figure, which is a vendor number. Region-pinning keeps same-region reads free in the common case.
- **Pricing:** every vendor studied gates bulk export behind an enterprise tier or usage-priced add-on, and none offers it free. If yours is bundled today, record an explicit decision to keep it that way or reprice.

## 6. Answering the Indian conglomerate's procurement team

- **Don't answer "us-east-1" and hope.** Their repeated question is a signal that data location matters to them. Say what you'll do, not what you do today.
- **Options, in the skill's order:**
  1. A region-pinned India deployment (for example ap-south-1 Mumbai).
  2. A documented legal basis for cross-border processing.
  3. "Not offered in India", which is a legitimate outcome. Stripe does this for Data Pipeline, citing data localization.
- **Don't promise India residency until you know the legal requirement.** ⚠️ I haven't verified India's current law (DPDP Act and sector rules for payroll and financial data). Counsel must confirm whether localization is mandatory or only contractual. Procurement may be asking for contractual comfort, not law.
- **Building a third region for one prospect is a business decision.** The region-routing from section 2 makes it cheap to add later, so don't build it speculatively.

## 7. Contract and schema hygiene (check, don't assume)

I haven't seen these, but they decide whether scaling breaks customers:

- **Write a data contract:** schema (columns, types, nullability), quality thresholds, freshness and availability.
- **State your freshness posture explicitly.** Choose fixed cadence (Stripe: every 3 hours), best-effort target (Amplitude), or contractual SLA (Fivetran). Unstated means customers assume the strongest version.
- **Schema evolution is add-only:**
  - Append nullable columns at the end.
  - Never rename, remove or retype in place.
  - Validate each batch against the registered schema before it counts as delivered.
  - Silent schema drift is the skill's costliest failure mode.
- **Layout:** Hive-style partitions (`year=/month=/day=`, at most 2-3 low-cardinality levels, tenant-scoped), Parquet files of roughly 256-512 MB, compaction, and a schema catalog (such as Glue).
- **Cadence default is scheduled full-dump.** Move to incremental or CDC only when bandwidth cost or a customer freshness demand forces it. CDC requires delete tombstones and reconciliation.

## 8. Rollout order

1. **Now (this week):** Ask counsel the TIA question in section 1. Freeze new Manila access to production payloads. Write down who pays what.
2. **Next:** Add `data_residency` routing, the EU bucket and regional KMS. Migrate EU data and delete the originals, including Athena results.
3. **In parallel:** Build metadata-first support tooling and the pseudonymized debug replica. Add break-glass access via the broker.
4. **Then:** Move customers to per-recipient credentials (access points). Publish the data contract and freshness posture.
5. **After:** Decide India (region, legal basis, or not offered). Decide on a native warehouse share only if a platform shows 30-40%+ concentration among target accounts. That threshold is self-set in the skill.
6. **Later:** Cadence upgrades and premium gating, driven by cost or customer demand.

Region pinning (step 2) is cross-cutting. Don't leave it for the pricing stage.

## Open questions

These change specifics, not the verdict:

1. Is the Manila team Vantablue employees, an affiliate, or an outsourced vendor?
2. What share of customers already run Snowflake, Databricks or BigQuery? A dominant platform would make a native share the default camp.
3. How fresh must data be, according to buying customers?
4. Is export bundled free today?
5. Does the current schema have a written contract, and is there batch validation?