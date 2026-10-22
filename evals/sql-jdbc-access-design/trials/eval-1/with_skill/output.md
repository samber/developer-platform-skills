**Verdict: do not build as drawn.** One item leaks every customer's data, one is silently broken, and the QA plan can't see either problem.

Next action: delete the base table from the share plan. Then read the rest.

## 🔴 Block: fix before any build

1. **Base fact table in the share.**
   - A share grants the same objects to every consumer account.
   - Any customer can `SELECT * FROM` the fact table and read all 180 tenants' rows.
   - The "drill down" use case is a full breach.
   - Fix: never share base or mapping tables. Add a second secure view with more columns and the same predicate.

2. **`CURRENT_USER()` catch-all view.**
   - `CURRENT_USER()` and `CURRENT_ROLE()` return `NULL` inside a secure view once it crosses an account-to-account share.
   - The predicate matches nothing, or everything, depending on its shape. An `OR ... IS NULL` or a `NOT IN` can fail open.
   - Even without the NULL, a consumer's user name isn't your `customer_id`.
   - Fix: join a private entitlement table on `CURRENT_ACCOUNT()`. It is the only identity function that is safe across a share.

3. **180 per-customer views in one share.**
   - Every consumer account can query every view in the share, so `v_headcount_beta` is readable by acme.
   - Isolation then depends on 180 separate shares, each with exactly one view.
   - 180 hand-written literals (`'acme'` vs `'acmee'`) also mean 180 edits per new column.
   - Both view styles together double the attack surface for no gain. The catch-all view makes the per-customer views redundant.
   - Fix: one secure view, one share, one entitlement table. Add a row per customer.

4. **"Four years, no leaks."**
   - This evidence covers the API layer. A SQL share has no API layer, so the evidence doesn't transfer.
   - An app-layer `WHERE` is a named failure class here. One missed filter anywhere returns another tenant's rows.
   - "Never leaked" also means "never probed". It is not proof of a control.
   - Fix: put isolation in the engine (items 1 to 3).

5. **QA plan: query each view from your own account and eyeball `customer_id`.**
   - Your account is the provider. There `CURRENT_USER()` returns a real user, so the NULL trap in item 2 stays invisible.
   - Eyeballing 180 views is not a gate. It also can't tell "empty because fail-closed" from "empty because broken".
   - Fix: run an automated consumer-side probe. Spec below.

## 🟠 Fix before GA

6. **Do customers have Snowflake accounts?**
   - If not, you provision reader accounts. Their warehouses bill to you with unlimited credits by default.
   - A resource monitor on every reader account is mandatory before the first login.
   - For credentials: key-pair or OAuth only, no static passwords.

7. **Region and cloud.**
   - Shares only work inside one region and cloud.
   - Customers elsewhere need replication, which means a second copy of the data (PII included) and extra cost.

8. **Scan frequency.**
   - A zero-copy share is cheap only while scans are infrequent.
   - Rule of thumb: about 20 scans/day on a ~200 GB table makes a replica cheaper.
   - A finance dashboard refreshing every morning could cross that line.
   - Who pays compute? Full accounts pay their own. Reader accounts bill to you.

9. **Schema is now an API.**
   - Don't share views over the live operational tables. A rename breaks customer dashboards silently.
   - Serve a curated mart layer. Make changes additive-only.
   - Enforce this in CI with dbt model contracts, which fail the run on a breaking column change.
   - List explicit columns in the view, never `h.*`, so new internal columns don't leak out.

10. **No pricing or onboarding.**
    - Default to a flat add-on or tier gate. SQL access is expensive to over-serve, and a price is also a control.
    - Automate onboarding (mapping row plus add account to share) and offboarding (remove account from share and delete the mapping row).

## Replacement design

```sql
-- private schema, never in the share
CREATE TABLE priv.entitlement (
  snowflake_account STRING,  -- customer's CURRENT_ACCOUNT() locator
  customer_id       STRING
);

-- the only objects in the share
CREATE SECURE VIEW share_mart.v_headcount AS
SELECT h.customer_id, h.period, h.department, h.headcount  -- explicit columns
FROM priv.mart_headcount h
JOIN priv.entitlement e ON e.customer_id = h.customer_id
WHERE e.snowflake_account = CURRENT_ACCOUNT();
```

- Add `share_mart.v_headcount_detail` for the drill-down. Use the same predicate and more columns.
- Grant only the two secure views to the share.
- A customer with several accounts gets several mapping rows.

## Isolation gate (replaces the eyeball check)

Run this for every view, in CI, on every policy or schema change. It takes about half a day to build.

1. Set `SIMULATED_DATA_SHARING_CONSUMER` to a test consumer account, or use a real second account. Query as that consumer.
2. Assert own-tenant row count `> 0` (catches fail-closed empties).
3. Assert `COUNT(*) WHERE customer_id <> expected` equals `0`.
4. Assert an account absent from `priv.entitlement` returns `0` rows.
5. Run `SHOW GRANTS TO SHARE` and assert the base and entitlement tables are absent.

Also run a second probe as a different tenant. Zero foreign rows is a binary pass/fail.

## Questions I need answered

1. Do the 180 customers all have Snowflake accounts? If not, how many need reader accounts?
2. Which regions and clouds are your customers on?
3. What is the scan pattern: ad-hoc a few times a week, or a parked dashboard?
4. Is the "detail" columns request really row-level employee data? If yes, check PII and DPA scope before exposing it.
5. Flat add-on, tier gate, or free?

Next step: answer questions 1 and 2. Then I'll turn the design above into a build plan. That takes about an hour.