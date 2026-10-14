# Corvid "connector strategy": sorted into four separate decisions

## Next actions

1. Change the board deck. "Connector strategy" is four different surfaces with different owners, risks and costs (see the table).
2. Build item 1 now, as a managed per-customer export.
3. Run item 3 as a two-partner pilot on a curated directory, not an open one.
4. Don't build item 2. Answer the prospect with item 1's output.
5. Don't build ETL-platform connectors (Fivetran, Airbyte and similar). No evidence supports them yet.

I followed `etl-connector-strategy`. It covers only being a source in a third-party ETL catalog, and none of your three items is that. The skill tells you to route mismatched demand to its sibling skills. I used the siblings' framing for the routing, but I did not run their full workflows.

## Where each item belongs

| # | Ask | What it really is | Skill that owns it | Verdict |
|---|---|---|---|---|
| 1 | Nightly Parquet into customers' S3 | Bulk data delivery | `bulk-data-sharing-design` | **Build** (small, managed) |
| 2 | Tableau live on our data | Customer-facing live SQL | `sql-jdbc-access-design` | **Don't build yet**; answer with item 1 |
| 3 | Partners building into our app directory | Inbound marketplace (third parties build into you) | `connector-marketplace-strategy` | **Pilot**, curated, 2 partners |
| – | Being a source in ETL platforms | Outbound presence in others' catalogs | `etl-connector-strategy` | **Parked** at the demand gate |

The ETL skill points in the opposite direction from item 3. Item 3 is third parties building into your directory. The ETL skill is you building into someone else's catalog.

## Item 1: Parquet drops to customer S3

You have two customers asking and no warehouse concentration data. That points to the file-drop camp. A native warehouse share (Snowflake, Delta Sharing) only makes sense if a share of your accounts concentrates on one platform, roughly 30–40% or more. That threshold is self-set in the skill, not a vendor figure. Ask the two customers which warehouse sits behind that bucket before ruling shares out.

**Scope:** build two managed export jobs, not a product surface.

- **Layout contract, written down.**
  - Use Hive-style date partitions (`year=/month=/day=`), with a tenant prefix. Keep 2–3 low-cardinality levels.
  - Use Parquet, not CSV.
  - Register the schema in a catalog, such as a Glue table, so customers don't infer it from files.
  - The skill's 256–512 MB file target is sized for large tenants. For nightly shipment deltas you will produce small files, so compact weekly rather than shipping many tiny ones.
- **Cadence.** Nightly incremental by `updated_at`, plus a periodic full reconcile. Say "daily snapshot, up to 24 h stale" in writing. Don't call it CDC.
- **Deletes.** Cancelled or purged shipments need an explicit tombstone or `deleted_at` column. Otherwise the customer's copy drifts silently.
- **Credentials.** Per-customer cross-account IAM role with an external ID. Grant `PutObject` on one prefix only. Never share a Corvid-owned secret across customers.
- **Schema evolution.** Additive-only columns. Renames and removals need a versioned path and a notice window.
- **Cost.** Egress and storage land on you when you write into their bucket. Price it as a premium or enterprise add-on, not a free feature. A free export is a documented failure mode in the skill.
- **Residency and PII.** Shipment data can include consignee names and addresses. Confirm the regions of both customers before the first drop. EU personal data in a bucket outside the EU needs a legal check.
- **Promotion trigger.** Turn the managed jobs into a self-serve product surface at about 5 requests in a quarter. That number is my suggestion, not a documented threshold.

## Item 2: Tableau live

One prospect's analyst asked a question. That is a signal, not demand.

**Answer to give the prospect now:** "Take the nightly Parquet drop into your own bucket, query it with Athena or your warehouse, and connect Tableau to that." It gives them real SQL on their own copy, and Corvid's infrastructure never gets a Tableau handle.

**Why not build a live endpoint yet.** An isolation bug on a live SQL endpoint returns another customer's rows. Your data is shipment visibility. Competing shippers and carriers are plausibly among your customers. A cross-tenant leak there is a trust-ending incident, not a bug. A runaway dashboard query also lands on your infrastructure bill.

**If you reopen it later,** two gates must pass before any customer gets a handle:
- Tenant isolation enforced in the engine (secure views or row-level security).
- Query governance (cost and time caps).

Also required first:
- A scan-frequency estimate. Few scans a week allows a zero-copy share. A dashboard that 40 people load each morning needs a replicated copy.
- A published schema-stability contract on a curated mart layer, not raw operational tables.
- A certified driver, if Tableau is the actual consumer.

**Reopen trigger:** two or more customers (not prospects) ask for live BI access, or a lost deal cites it. Log the prospect's request now with its date.

## Item 3: partners building into the app directory

First, a fact I don't have: does the app directory exist today, or is it a page of logos? The pilot differs in each case.

**Build, join or buy gate.** The skill says most SaaS companies should not build a full marketplace. It requires all four of these before building:
- Customer pull.
- Supply signal.
- Procurement friction.
- Staffing for the full partner lifecycle.

You have partial supply: two partners are asking. Demand is not shown. Do joint customers actually ask for these two connectors? Staffing is unknown. A real marketplace without both demand and supply is "an expensive partner directory."

**Recommendation: a curated pilot with these two anchor partners.**
- Treat it as partner onboarding and listing standards, not a marketplace launch.
- Require a public API, sandbox tenancy, a review before listing and a named Corvid partner contact.
- No take-rate, no open submissions, no public commitments.
- Promotion to a real marketplace needs all four triggers above, with evidence.
- Next skills to run: `partner-app-onboarding`, `app-marketplace-listing-standards`, `app-marketplace-review`.

**Dependency on items 1 and 2.** The connectors that partners build will extract data through your API. The readiness work below serves them too.

## ETL-platform presence: parked at the demand gate

The ETL skill requires named, verifiable evidence before any build. That means tickets that name a platform, lost-deal notes citing the data stack, or hand-rolled API scans from data-team accounts. You gave none. The two Parquet customers are evidence that these customers want files in their lake, not that they run Fivetran or Airbyte.

- **Decision:** no ETL connector build.
- **Reopen signals:** three tickets naming the same platform in a quarter, or one lost deal that cites the gap. Then run interview question 2 (which platforms customers run) before choosing a platform.
- **Not a revenue line.** No ETL platform pays a source vendor. Any future business case rests on support deflection and retention.
- **Maintenance cost if you do build later.** Budget 15–30% of build cost per year, with a named month-13 owner. These are vendor-published estimates, so treat them as an order of magnitude.
- **CDC wording.** Never write "CDC" on a data page. Write "incremental sync, up to N hours stale." State what it misses: intra-interval overwrites, and hard deletes where no deletion feed exists.

## The shared investment: extraction readiness

This is the one piece of engineering that pays off across items 1 and 3 and any later ETL work. Audit the Corvid API for these:
- A stable incremental cursor or reliable `updated_at`.
- A bulk or backfill path separate from UI-grade pagination.
- An explicit delete signal.
- 429 with `Retry-After`.
- Additive versioning with published sunset dates.

Do the audit before building item 1's export, because the nightly incremental job needs the cursor and the delete signal. A delete feed for item 1 also gives partner connectors a delete signal.

## Corrected board-deck wording

> **Data & integration surfaces**
> 1. **Data delivery** (now): nightly Parquet export to customer buckets, priced as an add-on.
> 2. **Live SQL/BI access** (gated): not on the roadmap until customers, not prospects, request it. Interim answer is item 1.
> 3. **Partner app directory** (pilot): 2 curated partners. Marketplace scale-up needs demand and staffing evidence.
> 4. **Third-party ETL catalogs** (parked): reopens on documented platform-specific demand.

## Open questions that would change this

1. What warehouse sits behind the two customers' S3 buckets? Is any platform dominant across your accounts?
2. Does the app directory exist today? Do joint customers ask for these two partners' connectors?
3. Who owns each surface in month 13, and what effort ceiling do you have for item 1 and the pilot?
4. Are there EU or other residency constraints on the two customers' data?
5. Does the API already expose a cursor and a delete signal?

I couldn't run the one-question-per-message interview in a single response, so all of the above rests on your message and the assumptions I flagged. I also did not read the ETL skill's economics and extraction-readiness references in full, because the ETL decision stopped at the demand gate. I read only the first 90 lines of each of the three sibling skills.