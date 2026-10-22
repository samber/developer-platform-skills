# Export schema stability policy

## Exec-review summary

**Proposal:** the Parquet export is a versioned public contract, not a byproduct of internal schemas. A breaking change can't ship without a version bump, a deprecation window, and a passing automated gate. The gate fails the job closed.

**Why release notes alone fail:**
- **They're late.** Tuesday's rename would have been announced weeks afterward.
- **They're passive.** Nobody reads a monthly note and then audits their dbt models.
- **They enforce nothing.** The next rename ships the same way.
- **They wouldn't have caught the worst incident.** The fraud model scored on nulls for a day because nothing in the pipeline noticed a column going empty.

The root cause is that the export job passes the internal service schema straight to 300 customers. Every internal refactor is therefore a customer-facing API change.

## The policy

### 1. Separate the contract from the internals
- Keep a committed contract file (`export-contract/v1.yaml`) that lists each column's name, type, nullability, units, enum values, and meaning.
- The export job maps internal fields to the contract. When the backend renames `merchant_ref` to `merchant_reference`, the mapping layer keeps emitting `merchant_ref`. Customers see no change.
- Name one team as owner of the contract, with CODEOWNERS enforcement.

### 2. Classify every change

| Class | Examples | Rule |
|---|---|---|
| Non-breaking | New nullable column, new file partition | Ship anytime. Notify in the changelog. |
| Breaking | Rename, removal, type change, nullability change | Needs a new version and a deprecation window. |
| Semantic breaking | Units, timezone, enum values, null meaning, row grain, path or partitioning change | Treated as breaking, even though the schema looks identical. |

### 3. Handle breaking changes in four steps
1. **Renames:** publish both the old and new column, with identical values, for the whole window.
2. **Other breaking changes:** publish a parallel `v2` prefix beside `v1`.
3. **Notice:** give at least 90 days before removal. I'd propose 180 days for annual-contract customers, but that's your decision.
4. **Early access:** offer the new version to opt-in design-partner customers first, ideally 2 to 4 weeks ahead of the general announcement.

Customers pin a version and migrate on their own schedule until the sunset date.

### 4. Notify directly, in machine-readable form
- **Email** a named technical contact per customer. Collect these now, because you likely don't have them for all 300.
- **Changelog page** with an RSS feed, plus an in-product banner.
- **A `_manifest.json` in every bucket,** written with each delivery. It holds the schema version, a column fingerprint hash, row counts, and any deprecations. Customers can alert on a fingerprint change.
- **Release notes stay,** but only as a summary of the above.

### 5. Gate the change automatically
- **CI contract test:** diff the export's actual output schema against the contract file. A breaking diff fails the PR unless it carries an approved version bump. This would have blocked last Tuesday's rename.
- **Pre-publish validation:** before delivery, the job checks its output against the contract and writes a `_SUCCESS` marker only on a pass.
- **Fail closed:** on a mismatch, the job quarantines the output to a staging prefix, doesn't deliver it, and pages on-call. A visibly late file is recoverable. A wrong file that customers ingest silently is not.
- **Data-quality checks:** compare each column's null rate and the row count to a trailing 7-day baseline. A jump from 0% to 100% nulls halts the delivery. This is the check that catches the fraud-model failure, and a pure schema diff would miss a column that exists but is empty.

### 6. Respond when something escapes
- **Rollback or restore** the contract-conformant export within 4 hours.
- **Notify** affected customers within 4 hours, naming the columns and dates.
- **Backfill** corrected files.
- **Write a postmortem** that is shared with customers.

## What to measure
- Breaking changes shipped without a version bump. The target is 0.
- Changes caught in CI before merge.
- Time from a bad export to detection.
- Time from detection to customer notice.
- Export-related support tickets per quarter. Last week's baseline is 31.

## Rollout

| When | Action |
|---|---|
| This week | Revert the rename in the export (or emit both columns). Collect technical contacts. Send an incident note to the affected customers. |
| Days 1–30 | Write the contract file for the current schema, add the CI diff test, and name the contract owner. |
| Days 30–60 | Add pre-publish validation, null-rate checks, the `_SUCCESS` marker, and the manifest. |
| Days 60–90 | Publish the stability policy and changelog. Run the first deprecation under the new process. |

## Decisions for the exec review
1. Who owns the contract: a data platform team, or the backend team that owns the export job?
2. How long is the deprecation window, and does it differ by tier?
3. Is failing closed acceptable? That means a late file, and possibly a missed customer SLA, instead of a bad one.
4. Is dual-publish storage and egress acceptable for the length of each window?

## Caveats
- I haven't seen your export code. I'm assuming the job maps internal fields to Parquet columns with little or no translation layer, as your description suggests.
- Adding a column is safe only for customers who read Parquet by name. Customers who read by position break on an insert, so the policy should tell consumers to select columns explicitly.
- The 90/180-day windows and the 4-hour response targets are my proposals, not industry standards. Adjust them to your contracts and on-call capacity.