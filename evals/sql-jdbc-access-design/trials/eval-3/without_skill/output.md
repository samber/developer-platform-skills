**Do not ship this plan.** Next action, about 5 minutes: connect to a scratch DB as a non-owner role with RLS on, run `SET app.tenant_id = '<another org uuid>'; SELECT count(*) FROM <tenant table>;`, and watch it return that org's rows. That is the main flaw.

## Blockers (each one leaks data across tenants)

1. **The policy trusts a setting the customer controls.**
   - `app.tenant_id` is a custom GUC, and any connected role can `SET` it.
   - RLS keyed on a session setting only works when a trusted app sets it. Here the user holds the connection, so they can read any org.
   - Fix: one Postgres role per customer, with the tenant derived from `current_user` and never from a setting. For example: `tenant_id = (SELECT tenant_id FROM reporting.role_tenant WHERE role_name = current_user)`. Cache that lookup in a `STABLE` function.
   - Role-per-customer is not a schema-per-customer. 900 roles is cheap.

2. **The four views leak as-is.**
   - Views run with the view owner's privileges by default (`security_invoker` off).
   - The owner is usually a table owner or superuser, and owners bypass RLS unless the table has `FORCE ROW LEVEL SECURITY`. Every customer would see all tenants through the views.
   - Fix A: `ALTER VIEW ... SET (security_invoker = true)`. This works on PG16. But the customer then needs `SELECT` on the base tables, so you cannot hide them.
   - Fix B, which I recommend: a dedicated `reporting` schema. The views carry an explicit `WHERE tenant_id = reporting.current_tenant()`, and customers get `SELECT` on those views only, with no base-table grants. Keep RLS on the base tables as defense in depth for the app.
   - Also check whether any of the four views aggregates across tenants (benchmarks, rankings) or joins a table that has no `tenant_id`.

3. **Owner and bypass roles skip RLS.**
   - If the API connects as the table owner, RLS does nothing for it. Superusers and `BYPASSRLS` roles skip it too.
   - Add `FORCE ROW LEVEL SECURITY`, and make the API role a non-owner.
   - Customer roles must be `NOSUPERUSER NOBYPASSRLS NOCREATEROLE`.

4. **The API side is weak too.**
   - `X-Org-Id` is a client-supplied header. If the API doesn't check it against the authenticated user's org membership, any logged-in user can pass another org's id.
   - Derive the org from the token and use the header only to pick among orgs the user belongs to.
   - "Set when it opens the connection" is unsafe with pooling. In PgBouncer transaction mode a session-level `SET` leaks to the next client. Use `set_config('app.tenant_id', $1, true)` (equivalent to `SET LOCAL`) inside each transaction.

5. **Forgotten tables stay open.**
   - A table without RLS enabled is fully readable by anyone with a grant.
   - Tables with no `tenant_id` (join tables, lookups, audit logs, users, files) and any new table added later are the usual leaks.
   - Fix: add a CI check that every table in the exposed schemas either has RLS plus a policy or is on an explicit allowlist.
   - Also revoke `PUBLIC` privileges and `CONNECT` on the database, and grant to each customer role explicitly.

## Replica traps

6. **A physical replica is a byte copy.**
   - Roles, grants, views, and RLS policies all live on the primary. You cannot add a `reporting` schema, extra indexes, or customer roles only on the replica.
   - Your customer roles and logins will exist on the primary's catalog too.
   - Analytic queries get only the indexes your OLTP workload already has. Every policy needs a `tenant_id`-leading index on all ~40 tables, or customer scans will be slow.

7. **Arbitrary SQL from 900 orgs on shared hardware causes noisy neighbors and replication conflicts.**
   - Long queries on a hot standby either get cancelled, or delay WAL replay (`max_standby_streaming_delay`), or bloat the primary (`hot_standby_feedback`). You pick the failure.
   - Set per-role `statement_timeout`, `idle_in_transaction_session_timeout`, `work_mem`, and `CONNECTION LIMIT`. Put PgBouncer in front.
   - Customers will see replication lag as stale dashboards. Document the lag.

8. **The exposure surface is bigger than the tables.**
   - Enforce `hostssl` in `pg_hba.conf`, with IP allowlists or PrivateLink. Don't put raw Postgres on the open internet.
   - Catalogs show every table and column name. Check what `pg_stat_activity`, `pg_stats`, and `EXPLAIN` row estimates reveal, and keep customers off `pg_read_all_stats`.
   - Log queries with `pgaudit`.

## Product and compliance

9. **This is PHI in a clinical product.**
   - Check HIPAA minimum-necessary and your BAAs with customers.
   - Check whether raw tables hold internal columns that were never customer-facing: staff notes, billing, feature flags, soft-deleted rows.
   - Customer analysts also bypass the in-org permissions your app enforces. A clinician who can only see their own patients in the UI would see the whole org in SQL.
   - Treat the exposed objects as a versioned public API. If you expose raw tables, every migration breaks customer dashboards. Expose only `reporting.*`, with a stable contract.

## Schema-per-customer

- **It doesn't scale well here.**
  - 900 schemas × 40 tables is about 36,000 tables, plus indexes. That bloats the catalog and relcache and slows `pg_dump`, autovacuum, and planning.
  - Every migration runs 900 times. Pooling needs `search_path` handling.
- **It doesn't remove the access work.** You still need a role and grants per customer.
- **Its one real advantage:** a hard boundary with no GUC to forge. The role-per-customer and `reporting`-schema fix above gets most of that benefit without the table explosion.

## Better options

- **Ask how many customers really want direct access.** "Enterprise" is probably tens, not 900.
- **If it's tens, use logical replication.**
  - PG15+ publications support column lists and row filters: `CREATE PUBLICATION ... FOR TABLE t (cols) WHERE (tenant_id = '...')`.
  - Each customer gets their own small subscriber database, holding only their rows in the reporting schema. They can query it freely, with no shared RLS and no impact on the primary.
  - Row filters need the filtered column in the replica identity for `UPDATE` and `DELETE`.
- **If demand grows, add a warehouse or export path.** Your "no warehouse anywhere" is the root cause. An export to the customer's own bucket or Snowflake/BigQuery share, or a tenant-partitioned analytics store, is the standard answer.
- **If you stay on a shared replica,** the minimum is: role per customer, tenant from `current_user`, a `reporting` schema, resource limits, and an adversarial test suite.

## Tests to write

1. As a customer role, run `SET app.tenant_id = <other>` and `SELECT` from every exposed object. Expect zero foreign rows.
2. Attempt `SET ROLE` and a `RESET ROLE`, plus a `pg_stats` read.
3. Run a CI catalog scan for tables missing RLS.
4. As the API role, confirm RLS applies (non-owner or `FORCE`).
5. Run a long query on the replica and confirm it doesn't stall replay.

Next: run the 5-minute probe above on a scratch DB and send me the result.