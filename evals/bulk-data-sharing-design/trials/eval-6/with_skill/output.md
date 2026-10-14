# Export schema policy for Kestrelbridge

## Recommendation

The nightly export schema becomes a versioned, published contract. A gate checks every batch against it before customers can see the batch. Release notes become a record of contract changes, not the control that prevents breakage.

## Why monthly release notes fail

- **They announce changes after the fact.** The rename shipped Tuesday and customers broke Wednesday. A note that lists it later can't un-break anything.
- **They run slower than the deploys.** Any backend team can ship a rename on any day. A monthly note can't cover every change in between.
- **They don't help the silent failure.** The fraud-model customer saw no error, only nulls. No one reads a note in time to catch that. Only a check on the data itself would have.
- **They leave the root cause in place.** The export job is a pass-through of the core service's internal schema. Any internal refactor reaches 300 customer buckets unreviewed.

## The policy

### 1. Decouple the export schema from the internal schema

- Put an explicit projection layer between the core service and the export job. It is a mapping, for example `merchant_reference AS merchant_ref`.
- The export team owns that layer. A backend team can rename internally and only touches the mapping.
- Define the contract as four parts, because a dashboard, a dbt job and an ML model each depend on a different one:
  - **Schema:** columns, types, nullability.
  - **Quality:** completeness thresholds, such as a maximum null rate per column.
  - **Freshness:** the cadence you commit to.
  - **Availability.**
- Register every schema version in a catalog (Glue, Iceberg REST or Hive Metastore). Customers read the schema from there, not from file contents.
- Keep the freshness posture explicit. I'm assuming the nightly drop is a fixed cadence, not a best-effort target or an SLA. Say which one it is in writing. Confirm this assumption.

### 2. Make the rules add-only

**Allowed without notice** (announced in the changelog only):
- Append a new nullable column at the end.

**Breaking** (needs the deprecation process in section 4):
- Rename a column.
- Remove a column.
- Retype a column, including changes to precision or units.
- Make a nullable column non-null, or the reverse.
- Change what a value means, such as an enum meaning or a currency unit.
- Reorder columns or change partition keys or file paths.

A rename is therefore never done in place. It is "add the new column, deprecate the old one."

### 3. Enforce it with two gates

1. **Producer gate, in CI.** A contract test in the core service's pipeline diffs the export projection against the registered contract. A breaking diff fails the build. Because the projection layer absorbs internal renames, this test would have passed Tuesday's change and Wednesday would have been quiet.
2. **Delivery gate, at export time.** Before a batch counts as delivered, validate the written Parquet schema and the quality checks against the contract.
   - Check column names, types and order.
   - Compare each column's null rate with its trailing baseline. A large jump is the signature of the fraud-model incident.
   - On failure, hold the batch back, keep the previous good batch visible, and page the export on-call. Customers read the previous data instead of broken data.
   - To make "hold back" enforceable, write a per-batch completion marker or manifest and tell customers to read only marked batches. The skill doesn't prescribe this mechanism. It is my suggestion for implementing the hold.

Both gates mean drift raises an alert for you instead of a ticket from a customer.

### 4. Run unavoidable breaking changes like an API deprecation

1. Announce the change directly to each customer's named data contact. A monthly newsletter doesn't count.
2. Run the old and new columns in parallel for the whole window. For a rename, both columns are populated until the sunset date.
3. Mark the old column deprecated in the catalog with its removal date.
4. Remove it on the announced date and not before.
5. For changes that can't be done as parallel columns, publish a new versioned path (`v2/`) next to `v1/`.

I propose a minimum window of 90 days. This is my number, not a vendor-published figure. Set it with Support and your largest customers. The sibling skill `samber/developer-platform-skills@api-versioning-policy` has the notice-period mechanics. This policy defines what counts as breaking for files.

### 5. Ownership and customer communication

- **Contract owner:** one named team, probably data platform. Changing the contract needs their sign-off, and a breaking change needs a documented exception.
- **Customer contacts:** collect a data contact for each of the 300 buckets. Today you may only have a support contact.
- **Changelog:** every contract change, additive ones included, goes into a machine-readable and human-readable changelog. Your VP's release-notes idea fits here, as a record of what the gates already enforce.

## Fix the current incident first

1. Re-add `merchant_ref`, populated, alongside `merchant_reference`. This stops the two failing dbt runs and the broken Looker dashboards immediately. It is also the parallel-column pattern from section 4.
2. Decide whether to rewrite Tuesday and Wednesday's partitions so the column is consistent across batches. Mixed names inside one table are their own hazard.
3. Contact the fraud-model customer directly. They need to know the exact window, since their model scored on nulls for about a day, and they may need to re-score.
4. Write the post-incident entry to match the contract. This is the first change to be announced under the new policy.

## How to measure it

Pass or fail, all must pass:
- **Contract completeness:** every export dataset has a written schema, quality thresholds and a named freshness posture.
- **Gate coverage:** both gates are live on every dataset that goes to customers.

Trends to watch:
- **Customer-reported schema-break incidents.** The target is zero.
- **Batches held by the delivery gate.** Each one is a ticket avoided. A rising number means the CI gate isn't catching enough upstream.
- **Share of deliveries meeting the stated freshness posture.**

## Rollout order for the exec review

1. Immediate: restore `merchant_ref` and contact the affected customers.
2. Write the contract for each dataset and register it in the catalog.
3. Build the delivery gate. It protects customers soonest, because it covers any cause of drift, including changes you didn't predict.
4. Build the CI gate and the projection layer.
5. Collect data contacts, publish the deprecation policy and the changelog.

I haven't estimated durations. They depend on how many datasets you export and how the job is built today.

## What I assumed

Please confirm or correct these:
- The export is the full set of Parquet file-drops, with no warehouse share today.
- Customers read the Parquet by column name, which is why a rename broke them.
- The nightly cadence is a fixed commitment, not best-effort.
- No contract or catalog registration exists today.

If you also want to cover warehouse sharing, cadence, egress or EU data residency, that needs a separate pass through the rest of the skill. I kept this answer to the schema question you asked.