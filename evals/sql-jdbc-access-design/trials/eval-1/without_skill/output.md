# Pre-build review: Trellisway Snowflake sharing plan

**Verdict:** don't build it as drawn. Two items would leak data (1 and 2). One makes your QA plan meaningless (5).

## 🔴 Blockers

**1. Sharing the base fact table gives every customer all 180 customers' rows.**
- A share grants access to the object. A `WHERE` clause on a different object doesn't restrict it.
- Customers who see the table can query it directly. The views don't matter.
- "Drill down when the view lacks detail" is the wrong fix. Make the secure view detailed enough, or add a second secure view with more columns.
- Never put the base table, or any table it joins to, in a share.

**2. `CURRENT_USER()` is the wrong identity function in a share.**
- In a shared view, it returns the consumer's own user name, which the consumer controls.
- Any admin can create a user named `acme`, or a user that collides with a name in your mapping. That bypasses the filter.
- Use `CURRENT_ACCOUNT()` instead. The consumer cannot fake it. Join it to an entitlement table you own:

  `entitlement(consumer_account, customer_id)`

  Add a unique constraint on `consumer_account`.
- The view filters with `customer_id IN (SELECT customer_id FROM entitlement WHERE consumer_account = CURRENT_ACCOUNT())`.
- An account with no match must return zero rows. Check that explicitly.
- Locators can be ambiguous across regions and clouds. Verify whether to key on org name plus account name, using `CURRENT_ORGANIZATION_NAME()` and `CURRENT_ACCOUNT_NAME()` if your edition has them. Don't key on the locator alone.

**3. Plain views can't be shared. They must be `CREATE SECURE VIEW`.**
- Secure views also hide the view definition from consumers. That matters because the definition would expose your entitlement logic.
- Expect some optimizer cost. Cluster the fact table on `customer_id` and benchmark at full size.

## 🟠 Design holes

**4. The 180 per-customer views are redundant.**
- Once you have the catch-all secure view with `CURRENT_ACCOUNT()`, the 180 views add nothing.
- They only give you 180 places to get a literal wrong.
- If you want per-customer physical isolation, use one share per customer. Still no base table.

**5. The entitlement table is now your security boundary.**
- One wrong row sends customer A's data to customer B.
- Make changes reviewed and audited, with no ad-hoc inserts.
- Don't expose the table in any share.
- Alert on rows that change.

**6. "Four years, no leaks in the API" says nothing about this path.**
- The API filter doesn't exist in the share path. This is a new tenant-isolation implementation with zero track record.
- Check for things the API may handle implicitly:
  - parent and child customer hierarchies
  - merged or acquired customers
  - case or whitespace variants of `customer_id`
  - soft-deleted rows
  - dimension or lookup tables that carry other tenants' values, such as cost center names, departments or manager names

**7. HR data is sensitive.**
- Check whether the fact table holds employee-level fields, such as salary, termination reasons or demographics.
- Once a customer has `IMPORTED PRIVILEGES`, their Snowflake admins decide who in their company sees it. That may include people who shouldn't see HR data.
- Check your DPA and customer contracts. Check GDPR and works-council implications, especially for EU employees.
- Consider a share that exposes only aggregates or pseudonymised rows. Add small-cell suppression if you do.
- Any benchmark or cross-customer derived columns must not be in the view.

**8. Sharing can't be undone.**
- Removing an account from the share stops future access immediately.
- Anything the customer copied with CTAS stays with them. Put retention and offboarding terms in the contract.

**9. Customers aren't all Snowflake accounts in your region.**
- Cross-region and cross-cloud sharing needs replication or listings auto-fulfillment, with egress and storage cost.
- Customers without Snowflake need reader accounts, which you create and pay compute for. You'd need to cap that spend with a resource monitor.
- `CURRENT_ACCOUNT()` works there too. Map the reader account to the customer.

**10. View schema is now an API.**
- Column changes break customers' finance joins.
- Version the views (`v1`, `v2`) and publish a deprecation policy.

## ❌ QA plan is invalid

Querying from your own account tests nothing:
- Your own account is probably in neither the entitlement table nor the intended consumer set, so the catch-all view returns nothing or your own rows.
- Eyeballing `customer_id` proves nothing across 180 views. Leaks can also be in other columns.
- Owner-account queries bypass the secure-view and share boundary.

Replace it with automated tests run **from consumer accounts**:

1. Create at least two test consumer accounts, or reader accounts, each mapped to a different synthetic customer with seeded data.
2. For each, assert:
   - `COUNT(*) WHERE customer_id <> expected = 0`
   - row count matches the expected count
3. Negative cases:
   - an unmapped account returns 0 rows
   - a user named like another customer changes nothing
   - the base table and entitlement table are not queryable
   - `GET_DDL` on the view is denied
4. Run `SHOW GRANTS TO SHARE` in CI and diff it against an allow-list. Fail the build on any extra object.
5. Run these on every deploy. A new column or table in the share must trip the allow-list.
6. Do a red-team pass before go-live. Try to exfiltrate through joins to any shared dimension.

## ✅ Recommended shape

1. One `SECURE VIEW` (plus a detail secure view if needed), filtered through the `CURRENT_ACCOUNT()` entitlement join.
2. Only secure views in the share. Never base tables.
3. One share, or one per region. Add consumer accounts by script from the entitlement table.
4. Automated consumer-side isolation tests plus a share-contents allow-list in CI.
5. Contract, DPA and sensitivity review before turning it on.

## Questions before you build

1. Does the fact table hold employee-level rows or only aggregates?
2. How many customers already have Snowflake, and in which regions and clouds?
3. Do your contracts and DPA allow sharing at this granularity?
4. Can you afford reader-account compute for customers without Snowflake?