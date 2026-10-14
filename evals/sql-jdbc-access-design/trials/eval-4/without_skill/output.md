# Managing schema change on the Quarrystone Snowflake share

## The core problem

The share is a public API with no contract. It sits directly on production tables, so any change to production is a change to 30 customers' pipelines. Two-weeks-notice-in-a-changelog and a "share v2 next quarter" don't fix that. They're a notice policy bolted onto a missing mechanism.

Three things to settle before the two changes:

1. **Separate the contract from the tables.** Customers should depend on a published layer you control, not on production.
2. **Make most changes additive.** Add the new name next to the old one, then retire the old one on a schedule that customers can plan against.
3. **Reject the `order_total` string change.** It's the dangerous one.

## 1. Why the two changes are not equal

| Change | Failure mode for customers | Verdict |
|---|---|---|
| `cust_ord_dt` → `order_placed_at` | Loud. Queries, dbt models and BI fields error out. | Fine, if delivered as add-then-retire. |
| `order_total` NUMBER → string with currency code | Silent or semantic. | Do not ship as designed. |

The type change breaks in several ways:

- **Aggregates break.** `SUM(order_total)` over `'12.50 USD'` raises a cast error, or worse, gets "fixed" by a customer with a regex that drops the currency.
- **Cross-currency sums look valid.** Once multi-currency orders land in one column, a customer's existing revenue dashboard adds euros to dollars and gives a wrong number with no error.
- **Tableau reclassifies the field.** A NUMBER becomes a string, so the field flips from measure to dimension. Every workbook using it breaks, and no query fails.
- **Packing amount and currency into one string is an anti-pattern.** It forces every consumer to parse it, and it hides precision rules. JPY has 0 decimals and KWD has 3.

**Recommended shape.** Keep the amount numeric and add the currency as a separate column:

- `order_total`: keep the type and keep the current meaning. If it has been implicitly USD, it stays "USD-equivalent". Existing dashboards then stay correct.
- `order_currency_code`: new, `CHAR(3)`, ISO 4217.
- `order_total_original`: new, `NUMBER`, the amount in the order's own currency.

This assumes `order_total` is single-currency today. If it isn't, tell me and the design changes.

Both changes then become additive and non-breaking on day one.

## 2. Put a contract layer between production and customers

**Build a versioned schema of secure views over the production tables.** Snowflake shares require secure views for this anyway. For example, a `V1` schema in the share containing one secure view per exposed table.

- **The views are the contract.** Production can be renamed or retyped freely, and the view absorbs it:
  ```sql
  CREATE OR REPLACE SECURE VIEW share_db.v1.orders AS
  SELECT
    cust_ord_dt AS cust_ord_dt,       -- deprecated alias, removed no earlier than <date>
    cust_ord_dt AS order_placed_at,   -- new name
    order_total,
    order_currency_code,
    order_total_original
  FROM prod.orders;
  ```
- **Use an explicit column list in the view, never `SELECT *`.** That way a new production column doesn't leak into the share by accident.
- **Add views before you remove anything.** The migration for customers is then to switch column names on their own schedule.
- **Skip the "share v2 next quarter" plan for changes this size.** A rename and an additive column don't need a new share. Reserve a `V2` schema for batched removals or semantic breaks. Put it in the same share as a second schema, so the 30 customers change a schema name rather than re-onboarding to a new share. Run `V1` and `V2` side by side until `V1` retires.

If you aren't using listings, check whether moving to them would give you better usage visibility (see §4).

## 3. Change classes and the rule for each

Write this down as the contract. Publish it on the docs site and link it from the share's onboarding.

| Class | Examples | Rule |
|---|---|---|
| Additive | New view, new nullable column, new row range | No notice window. Announce in the changelog. Tell customers up front that this can happen, and to use explicit column lists, not `SELECT *`. |
| Breaking | Rename, removal, type or precision change, nullability change, new enum values | Add-then-retire, with a published removal date, and no removal until usage hits zero or stragglers are handled. |
| Semantic | Timezone of a timestamp, row filter, grain, currency basis, what "total" includes | Treat as breaking even though no schema diff shows it. Needs a changelog entry and direct customer notice. |

Also commit to a minimum deprecation window. Two weeks is too short for data pipelines that run on quarterly planning cycles and have their own change control. I'd use 90 days as the floor for renames. For anything that changes meaning, use 180 days. Pick numbers you can keep.

## 4. Make the process enforceable

1. **Snapshot the contract in the repo.** Commit a file listing every column, type and nullability in the `V1` schema.
2. **Add a CI gate.** Diff `INFORMATION_SCHEMA.COLUMNS` for the share schema against that snapshot. Additive diffs pass. Removals, renames and type changes fail unless the PR includes a deprecation entry. Treat the gate as a fixed rule and ask before changing it.
3. **Mark deprecations in the catalog.** `COMMENT ON COLUMN ... 'DEPRECATED: use order_placed_at; removal not before 2027-01-15'`. Customers see it in their own catalog tooling.
4. **Publish a machine-readable schema-change feed.** Add a small view, such as `v1._schema_changes`, listing each change, its class, effective dates and replacement. Customers can alert on it.
5. **Measure usage before you remove anything.** Check what your edition exposes. Provider-side visibility into consumers of a direct share is limited. Listings give you more, through `SNOWFLAKE.DATA_SHARING_USAGE`, and I haven't verified exactly which views cover your setup. If you can't see usage, the fallback is to ask each of the 30 customers to confirm migration in writing. Don't pull the old column on a guess.
6. **Run a brownout before removal.** For example, hide the deprecated column for 24 hours a few weeks before the real date. Customers who skipped the notices will notice, and you'll learn who they are.
7. **Keep an adoption list.** Per customer: notified, acknowledged, migrated. Work stragglers by name.

## 5. The Tableau connector

This is the highest-risk item on the list.

- **Contact its owner now, not in the changelog.** They're a customer, but their connector is a downstream product. Their end users are outside your 30, so your real blast radius is bigger than 30.
- **Ask what it hardcodes.** Column names, type mappings, and data-source definitions are the likely spots. The rename breaks any of them that reference `cust_ord_dt`.
- **Recertification may be slow.** Changes to a certified connector may need another review cycle with Tableau, and you don't control that clock. Ask the owner how long it takes, and set your removal date after it.
- **With add-then-retire, nothing breaks on day one.** The connector keeps working against `cust_ord_dt` while they update and recertify against `order_placed_at`.
- **Keep the `order_total` type frozen.** A measure-to-dimension flip would break every workbook downstream of that connector, which is another reason to reject the string change.

## 6. Proposed timeline

Today is 2026-10-10 and the changes land next sprint. This keeps the sprint date and removes the breakage:

1. **This sprint.** Build the `V1` secure-view layer. Ship `order_placed_at`, `order_currency_code` and `order_total_original` as additive columns. `cust_ord_dt` and `order_total` stay unchanged. Nothing breaks, so the changelog entry reads "added", not "breaking".
2. **Same week.** Email the Tableau connector owner directly. Send all 30 customers the contract, the deprecation of `cust_ord_dt`, and a detection query or search pattern for finding it in their code.
3. **Day 0 of deprecation.** Add the catalog comments, the schema-change feed entry and the CI gate.
4. **Day 60.** Reminder to customers who haven't migrated, plus usage data if you have it.
5. **Day 75 to 85.** Brownout.
6. **Day 90 or later.** Remove `cust_ord_dt` from `V1` only if usage is zero or the stragglers have a written plan. Otherwise extend, and say so publicly.

## 7. Draft changelog entry for the rename

> **Deprecated: `orders.cust_ord_dt`** (anchor: `#cust-ord-dt`)
> **Affected if** your queries, dbt models or BI fields reference `cust_ord_dt`. Search your repos for that string.
> **What changed.** `order_placed_at` is now available with identical values and type. `cust_ord_dt` remains until at least `<date>`. The old name was unclear, so we are retiring it.
> **Before** `SELECT cust_ord_dt FROM share_db.v1.orders`
> **After** `SELECT order_placed_at FROM share_db.v1.orders`
> **Escape hatch.** Both columns return the same data until the removal date. After that there is none.

Write the same kind of entry for `order_currency_code` and `order_total_original`, marked "added".

## Questions that would change this plan

1. Is `order_total` single-currency today, and what currency does it implicitly hold?
2. Are you on direct shares or listings? That decides what usage visibility you get.
3. How many end users does the Tableau connector reach, and how long does its recertification take?
4. Do any of the 30 customers have contractual notice terms for data changes? Those override my 90-day default.