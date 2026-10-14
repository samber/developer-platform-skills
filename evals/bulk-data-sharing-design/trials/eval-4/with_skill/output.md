# Ferrolane bulk export: design review for Thursday

I read the `bulk-data-sharing-design` skill and its three references, then checked your design against it. The skill says to ask clarifying questions first. This task was one-shot, so I've listed the assumptions I made at the end. Your answers to those could change the ranking.

## Verdict

The design fails all four of the skill's launch gates, and two of the failures are serious.

| Gate | Status | Why |
|---|---|---|
| Contract completeness | ❌ | No written schema, layout, or freshness posture |
| Cost allocation named | ❌ | You pay egress and API compute for every byte, and nothing says so |
| Residency coverage | ❌ | One bucket, one region, no documented posture for EU or other regulated customers |
| Premium gating | ⚠️ | Unknown. Nothing says export sits behind a paid tier or add-on |

## Holes, ranked

### 🔴 1. Static emailed IAM keys

- **Shared secret in plaintext email.** Anyone with access to the mailbox, a forwarded thread, or a ticket system has the key.
- **No rotation or expiry.** Offboarding a customer's engineer rotates nothing. A leak means a manual rotate for that customer, and breaking their pipeline.
- **Isolation rests on policy correctness.** If a prefix-condition policy is wrong for one of 900 customers, they read the others' data. IAM size limits make hand-written per-user policies fragile at this count.
- **`list` on a shared bucket leaks metadata.** A slightly wrong policy exposes other tenants' prefix names, which are customer IDs or export IDs.
- **Two auth paths that can disagree.** You revoke a customer in the API, and their IAM key still works directly against the bucket. Revocation is only as strong as the weaker path.
- **Wrong for a third of your base.** Azure customers get AWS identity material they must wire into their own cloud's tooling.

**Fix.** Issue no static keys. The API mints short-lived scoped credentials on request:
- **AWS recipients:** STS `AssumeRole` with a session policy scoped to the tenant prefix, TTL 15–60 minutes. For customers who run their own AWS account, a cross-account role with an ExternalId is the stronger option.
- **Azure recipients:** a user-delegation SAS scoped to that tenant's container or directory. Verify that prefix-scoped SAS needs a hierarchical-namespace account. Without one, use a container per tenant.
- **Both:** one KMS grant per recipient, so revocation touches only that customer.

### 🔴 2. Streaming bytes through the API pods

The skill names this as the "proxied bytes" failure. You become the throughput ceiling and the egress payer at once.

- **Shared fleet.** Download load competes with the live freight-visibility API for CPU, memory, connections, and autoscaling. One customer's 50 GB pull can degrade tracking queries for everyone.
- **Long streams break on deploys.** Rolling restarts and idle timeouts cut downloads mid-stream. Check that you support `Range` requests and resume.
- **Attribution is lost.** In S3 logs every read comes from the pods' role, so you can't tell which customer read what without your own logging.
- **You pay twice.** Bucket-to-pod is cheap in-region, but pod-to-internet egress is yours on top of compute.

**Fix.** Make the endpoint authorize and sign, not stream. `GET /v1/exports/{id}` returns a manifest of short-lived signed URLs (S3 presigned or Azure SAS), and the customer's client reads from storage directly. Bind each signed URL to the caller's tenant prefix. This also replaces `list`: the manifest is the listing, so no customer needs list permission on the bucket.

### 🟠 3. Quarterly calendar access reviews

- **Review cadence is a separate process from credential lifetime.** With long-lived keys, a revoked or compromised key stays live for up to 90 days, until the next review.
- **It doesn't scale.** Reviewing 900 credentials by hand each quarter is a chore that will slip.
- **With short TTLs, the review mostly disappears.** Expiry becomes the enforcement point. The skill's rule is to pin the review cadence to the credential TTL.
- **What's left to review is entitlements,** meaning which customers have export enabled. Review that, ideally from billing state.
- **If keys survive for a transition period,** rotate them on a schedule and alert on unused or anomalous keys (IAM Access Analyzer, CloudTrail).

### 🟠 4. The Azure third and egress cost

- **Who pays egress is unstated.** S3 bills data-transfer-out to the bucket owner by default, which is you. For ~300 Azure customers every download is internet egress from AWS to Azure, on your invoice.
- **Requester Pays doesn't help here.** It needs the recipient to have an AWS account, which Azure-native customers lack.
- **Options, cheapest build first:**
  1. Keep one AWS bucket, sign S3 URLs for everyone, and absorb egress. Put the cost in the export add-on price.
  2. Replicate once into an Azure Blob export store, then vend SAS from there. This pays one inter-cloud transfer per object instead of per customer download.
  3. For customers who need locality, push to a customer-owned destination (their S3 or Blob, via a role or SAS they grant you). They pay storage.
- **Decide and write it down:** who pays storage, compute, and egress, including the cross-region and cross-cloud cases.

### 🟠 5. Residency: one bucket, one region

- If any customers are EU-based, a single non-EU bucket commits you to SCC plus a transfer impact assessment for all of them. That is the skill's "cross-border violation" failure.
- Remote access counts as a transfer. A US-based support engineer reading an EU customer's export is a transfer event.
- Freight data has personal data in it: driver names, phone numbers, and location traces.

**Fix.** Pin region per tenant from day one, with regionalized KMS keys. Document one row per delivery route: legal basis, data classes, and whether the data is pseudonymized. Decide for any localization-mandate country (India, China, Russia) whether the product is simply not offered there. Retrofitting residency later is what led Segment to kill its EU Data Lakes product.

### 🟠 6. No data contract

The skill rates silent schema drift as the costliest failure in this domain. Nothing in the design covers:
- **Layout:** what `exports/{id}` contains. One object per export, or Hive-partitioned Parquet (`year=/month=/day=`, 256–512 MB files)?
- **Format and catalog:** Parquet (not CSV or JSON), with a registered schema in Glue or an Iceberg REST catalog.
- **Evolution:** add-only nullable columns, no renames, a validation step before a delivery counts as successful, and a dated deprecation process for breaking changes.
- **Freshness posture:** fixed cadence, best-effort target, or contractual SLA. Pick one and say so in the docs.
- **Mutable data:** shipment status updates and deletes. A full-dump default avoids delete-tracking. Only promote to CDC when the dump's cost forces it, and then you need tombstones and periodic reconciliation.

### 🟡 7. Smaller items to raise in the room

- **No warehouse-share option.** If 30–40% or more of customers sit on one platform (Snowflake, Databricks), a native share beats file-drops for them. It has zero copies and no egress for you. Delta Sharing and Snowflake both work across AWS and Azure, so the Azure split doesn't block it. Question 1 below decides this.
- **Retention and erasure.** How long do export objects live? An S3 lifecycle policy is needed, and so is a GDPR erasure story for historical exports.
- **Object-level authorization.** Confirm the signing path checks that `{id}` belongs to the caller's tenant, so a guessed ID can't get a URL.
- **Build vs partner.** Prefer the warehouse's own sharing primitive and signed URLs over a custom pipeline.

## Recommended target design

1. **Signing, not streaming.** `GET /v1/exports` returns a manifest. Each entry carries a signed URL (S3 presigned or Azure SAS) with a 5–15 minute TTL. The customer reads storage directly.
2. **Per-tenant credentials for pipelines that need a listing.** Short-lived STS or SAS tokens from an API call, TTL 1 hour or less, scoped to that tenant's prefix. No emailed keys.
3. **Isolation ladder.** Move from prefix isolation on the shared bucket to per-recipient access points, then to broker-minted credentials as the tenant count and risk require.
4. **Region-pinned storage per tenant,** with regional KMS keys and per-recipient grants.
5. **Written data contract:** layout, Parquet, catalog, add-only evolution, and a named freshness posture.
6. **Cost model in writing,** and export as a paid add-on or enterprise-tier feature. Every vendor the skill studied gates this feature class.
7. **Reviews follow TTL.** Review entitlements quarterly from billing state, not credentials.

## Rollout

1. Ship signed-URL download and the manifest, and retire the proxy path. Add an audit log keyed by tenant. This removes hole 2 first.
2. Move pipeline access to short-lived credentials. Give existing key holders a deprecation window (for example 60 days), then rotate and disable the old keys. This closes hole 1.
3. Region-pin new tenants, then migrate existing ones.
4. Add the Azure path (Blob store plus SAS, or replication) and publish the cost allocation.
5. Add a native share (Snowflake or Delta Sharing) if question 1 shows concentration.
6. Add incremental or CDC delivery only when a customer's freshness demand or the full-dump bill forces it.

## Questions for Thursday

I assumed an answer for each, and they would change the plan if wrong.

1. **Warehouse landscape.** What share of customers run Snowflake, Databricks, or BigQuery, and does one dominate? *Assumed no strong concentration, so file-drop first.*
2. **Data shape.** Is the data append-only events or mutable records with deletes? *Assumed mutable shipment records.*
3. **Freshness.** What have paying customers actually asked for? *Assumed day-old data is acceptable.*
4. **Regions.** Which regions and compliance regimes apply, and are any customers in localization-mandate countries? *Assumed some EU customers and unknown others.*
5. **Pricing.** Is export an enterprise gate, a usage add-on, or bundled? *Assumed it is not yet decided.*
6. **Clouds.** Is the roughly 2/3 AWS and 1/3 Azure split of recipients correct, and is your own storage AWS-only? *Assumed yes to both.*
7. **Delivery ceiling.** What is the deadline, and is this a one-off deal-closer or a platform surface? *Assumed a platform surface.*