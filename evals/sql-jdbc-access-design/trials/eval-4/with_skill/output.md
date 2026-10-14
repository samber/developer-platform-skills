# Managing schema change on the Quarrystone Snowflake share

Neither change should ship as written. The share has no mart layer, so both are in-place breaking changes to a live customer API. Announcing them in a changelog two weeks ahead is not a deprecation process. I read your skill (`sql-jdbc-access-design`) in full, plus its BI-connectivity reference. I haven't seen your share definition, so the assumptions are flagged at the end.

## Verdict on the plan

- **The rename** (`cust_ord_dt` to `order_placed_at`) breaks every dashboard, dbt model and saved query that names the column. This holds even if a customer reads the changelog.
- **The retype** (`order_total` from NUMBER to string with currency code) is worse. `SUM`, `AVG`, sorting and numeric filters stop working or silently change meaning. BI tools infer types from the column, so Tableau extracts and calculated fields break too.
- **The Tableau connector is a second stability surface.** The skill's reference says a schema change can break a certified connector's column typing or customization file even when the data contract is honored. That connector belongs to the customer, with their own signing and release cycle. Two weeks' notice is not enough for them.
- **"Share v2 next quarter" is the right instinct applied to the wrong thing.** It treats versions as a place to park bigger changes. The real defect is that the share sits on production tables, so every internal refactor becomes a customer-breaking change. The v2 should be the fix for that, not a bucket for large renames.

## The contract to adopt

1. **Additive-only.** Add columns and tables freely. Never rename, retype or drop in place. Evolve by expand/contract: add the new column, deprecate the old one in the docs, migrate consumers, and remove it only when nothing depends on it.
2. **Define "breaking" explicitly.** I'd list these:
   - rename, drop, or retype
   - tightening nullability
   - changing units or currency semantics (see below)
   - narrowing the value set of a column
   - changing a column's position if connectors depend on it
3. **Enforce it in CI.** Use dbt model contracts (1.5+) or the `datacontract` CLI so a breaking diff fails the PR. A contract that only lives in a doc won't survive the next readability refactor.
4. **Write it in four parts:**
   - schema
   - quality
   - freshness SLA
   - availability
5. **Set a removal window.** I recommend at least 90 days from deprecation notice to removal. That is a judgment call, not a number from the skill: I chose it to span one quarterly reporting cycle and a customer connector re-release. The sibling `api-versioning-policy` skill owns the notice mechanics.

## What to do with these two changes

### Rename: `cust_ord_dt` to `order_placed_at`

- Add `order_placed_at` alongside the old column, and populate both. If the share goes through views, the old name becomes a one-line alias.
- Mark `cust_ord_dt` deprecated in the docs and the changelog, with a removal date at least 90 days out.
- Remove it only when usage shows nothing reads it, or after the window ends and direct notices have gone out.
- Check what Snowflake's usage views can show you about consumer-side column access on shares. I haven't verified that for your setup, so confirm before relying on it for removal decisions.

### Retype: `order_total` to a string with currency

Don't do this. A currency code embedded in a string is a poor type design on top of the break.

- **Keep `order_total` as NUMBER** and add `order_currency` (ISO 4217, three characters).
- **Backfill history** with the single legacy currency. Confirm it is single.
- **Watch the semantic break.** Once orders arrive in several currencies, every existing `SUM(order_total)` silently mixes currencies. The type never changed, but the meaning did. By the contract's own definition, that is breaking.
- **My recommendation:** keep `order_total` meaning "amount in the account's reporting currency, converted at order time". Add `order_total_original` and `order_currency` for the transaction currency. Existing dashboards stay correct and new ones can opt in.
- **Decide the FX policy first.** That means the rate source, the conversion timestamp, and whether you store the rate on the row. It is a product decision, and the schema depends on it.

## Fixing the root cause: a mart layer

The skill says never expose the live operational schema. Serve a curated mart layer so internal churn stops at the boundary.

1. Build a curated schema of secure views over the production tables, with contract-grade names and types. Internal renames then happen in the view definition, and customers never see them.
2. Publish it as a new object set alongside the current one. Moving customers onto new object names is itself a breaking change, so do it once and deliberately.
3. Migrate the 30 customers to the new set, and sunset the raw-table objects on the standard window. **This is your "share v2"**, and it can start now rather than next quarter.
4. After that, additive changes keep flowing through the same schema. Reserve a new version for changes that cannot be made additively.

While you build this, treat production tables as frozen from the share's point of view. Internal column renames on shared tables wait for the mart layer.

## The Tableau connector customer

- Contact them this week, directly, not through the changelog.
- Get their column dependency list and their connector's release and recertification lead time.
- Give them early access to a staging share with the new columns so they can test before anything changes.
- Tell them which columns are stable and which are deprecated.
- Because they are the one customer with a certified artifact against you, ask them to flag any type assumptions in their customization file. Their signing and certification cycle is the real constraint on your removal date.

## Notice channels

A changelog is not enough for a data surface. The readers are analysts and BI owners who don't follow product changelogs.

- Send direct notices to the named technical contact at each of the 30 customers.
- Link the changelog entry and the contract page from each notice.
- Say what is changing, the exact dates, and the migration path with a before and after query.

## Plan for next sprint

1. **Ship only additive changes:** `order_placed_at`, `order_currency`, and `order_total_original` if you adopt my semantics. Dual-populate the old and new date columns.
2. **Do not retype `order_total` and do not drop `cust_ord_dt`.**
3. **Decide the FX policy** before the multi-currency launch.
4. **Add the CI contract check** over the shared objects, and make it fail on any breaking diff.
5. **Send direct notices** and contact the Tableau connector customer.
6. **Start the mart layer** and set the dual-publish and sunset dates.
7. **Draft the removal timeline** with dates, for the deprecated columns and for the raw-table objects.

## Gates before you call it done

- **Schema gate:** zero breaking changes reach the customer-facing schema past the CI check. A breaking change that ships counts as a failure even if nobody noticed.
- **Isolation gate:** because you are touching what is exposed, probe the share as another tenant. Require zero foreign rows on every view. I haven't seen how you isolate tenants today. A share on raw tables needs secure views filtered on `current_account()`, not `CURRENT_ROLE()` or `CURRENT_USER()`, which are NULL across a share.
- **Cost gate:** every external compute handle needs a statement timeout, a concurrency cap and a resource monitor. This matters most if any reader accounts bill compute to you.

## Open questions

These would change the design:

- How is tenant isolation done today, and has it been probed from a consumer account?
- Do any customers use reader accounts that you pay for?
- Is the legacy currency really one currency across all existing orders?
- How many of the 30 customers have dashboards parked on the share, versus ad-hoc use? That affects whether the share stays zero-copy or needs a replicated copy.
- Does the Tableau customer's connector go through Snowflake's driver or something of their own? That decides what their certification constraints are.