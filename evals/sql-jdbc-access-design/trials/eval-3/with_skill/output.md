# Review: customer SQL access on a Postgres 16 read replica (Bellcurve Health)

**Verdict: don't ship this plan.** Four problems each leak cross-tenant data, or let a customer take down the replica, on day one. Schema-per-tenant fixes none of them and adds a worse problem at 900 orgs.

I used the `sql-jdbc-access-design` skill and its three references. This is problem (c) in its framing: customers get a live SQL endpoint to their own data. With no warehouse in your stack, zero-copy sharing isn't an option. The rung you picked, a replicated read endpoint, is the right one.

## 🔴 Blockers

**1. Tenant identity is a setting the customer controls.**
- `current_setting('app.tenant_id')` is an ordinary session variable.
- Once a customer holds a psql or Metabase connection, they can run `SET app.tenant_id = '<any uuid>'` and read another org's rows.
- Your API setting it protects only API connections. Direct customer connections have no API in front of them.
- The skill's rule is that identity must be injected server-side from a verified source. Never use anything the client can set.
- Fix: derive identity from the authenticated login role.
  - Give each customer credential its own login role, with an opaque name, as a member of a `customers` group role.
  - Keep a private mapping from role to tenant, and look it up in a `SECURITY DEFINER` function that uses `session_user`.
  - Don't use `current_user`, because `SET ROLE` changes it.
  - Scope the policy `TO customers`, so the API's GUC policy can never OR-combine with it.

```sql
-- side-effecting DDL: run on the primary; customer roles get no USAGE on schema access
CREATE SCHEMA access;
CREATE TABLE access.role_tenant (
  login_role name PRIMARY KEY,
  tenant_id  uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE FUNCTION access.tenant_ids() RETURNS SETOF uuid
  LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$ SELECT tenant_id FROM access.role_tenant WHERE login_role = session_user $$;
CREATE POLICY customer_read ON some_table FOR SELECT TO customers
  USING (tenant_id IN (SELECT access.tenant_ids()));  -- subquery = evaluated once per query
```

**2. The four views, exposed as-is, bypass RLS.**
- A view runs with its owner's privileges. The owner is the table owner, who skips RLS unless you force it, so every customer would see every row.
- Fix on PG16: create each view with `WITH (security_invoker = true)`.
- Catch: an invoker view needs `SELECT` on the base tables. That exposes the raw schema to `\dt`, which is the problem in the next point.
- The alternative is owner views with an explicit tenant filter and `security_barrier`, on tables the customer can't read.
- Pick one deliberately. Whichever you pick, probe it (see Gates).

**3. You'd be exposing your operational schema.**
- Views over 40 operational tables inherit every internal rename, retype and drop.
- That breaks customer Metabase dashboards with no warning.
- Publish a curated, versioned schema (`customer_api`, with `v1` views) that you own as a contract.
  - Additive-only changes, with expand/contract for anything else.
  - A CI check that diffs the schema against a committed snapshot and fails on any drop, rename or retype.
- The four reporting views were built for internal use. Check them for internal-only columns and cross-tenant aggregates before any of them goes out.

**4. RLS is enabled but not forced, and there are no resource caps.**
- Without `FORCE ROW LEVEL SECURITY`, the table owner skips every policy.
  - That includes your migrations, admin tooling and background jobs.
  - Make sure the API role is neither the owner, a superuser, nor `BYPASSRLS`.
  - Customer roles must be `NOSUPERUSER NOBYPASSRLS NOCREATEROLE`.
- **A customer can undo their own timeouts.** `statement_timeout` is user-settable, so `ALTER ROLE … SET statement_timeout` is only a default. A session can run `SET statement_timeout = 0`. The same goes for `idle_session_timeout` and `work_mem`.
- Enforce limits outside the session:
  - Put PgBouncer in front, with `query_timeout`, per-user pool size and `max_user_connections`.
  - Run a reaper job that calls `pg_terminate_backend` on customer-role sessions over a runtime ceiling.
  - Set `CONNECTION LIMIT` per role.
  - Revoke `EXECUTE` on `pg_sleep` and similar from PUBLIC, and keep dblink-style extensions out.
- This is the skill's cost gate. The replica is fixed cost, so the danger is capacity and replication health, not a bill.

**5. Clinical data means this probably isn't a normal SQL-access launch.**
- If the data is PHI, you need:
  - a BAA and your compliance team's sign-off
  - `pgaudit` on the replica, logging per role
  - column-level grants that leave out internal and sensitive fields
- Org-level RLS also bypasses any per-user permissions your app enforces inside an org. A clinic user limited to one site in the app would, as an analyst, see the whole org. Customers must accept that, in writing.

## 🟠 Serious

- **The `X-Org-Id` header is client-supplied.**
  - If the API copies it into `app.tenant_id` without checking it against the authenticated user's org membership, tenant isolation is already broken on the API, and RLS just enforces the forged value.
  - Derive the tenant from the verified token claims, and verify the header matches them.
  - With a pooler in transaction mode, set the value per transaction with `SET LOCAL` or `set_config(..., true)`. A session-level `SET` leaks the previous tenant onto the next borrower of that connection.
  - Use `current_setting('app.tenant_id', true)` so an unset value returns no rows instead of raising an error.
- **A physical replica carries all 900 tenants.**
  - RLS is the only thing separating them, so one policy mistake exposes everyone.
  - Run a dedicated customer replica. Don't reuse the failover or app-read replica.
  - Long analyst queries either get cancelled by replay conflicts or lag the replica.
  - Setting `hot_standby_feedback` on avoids the cancellations but bloats the primary. Pick `max_standby_streaming_delay` deliberately.
  - Publish a freshness SLA, because dashboards will show lag.
- **Roles and the mapping table must be created on the primary.** The replica can't hold its own objects.
- **Credentials.**
  - The skill's ladder is short-lived token, then managed secret, then static password.
  - PG16 has no native OAuth. Metabase also can't refresh tokens.
  - So issue role-per-credential logins from a self-service UI, each with `VALID UNTIL`, scoped to one tenant and revocable.
  - Require `hostssl` with SCRAM, and document `sslmode=verify-full`.
  - Offer IP allowlisting through `pg_hba`.
- **Catalog enumeration.** Any role can list `pg_roles`. If role names contain org names, you've leaked your customer list. Use opaque names.
- **Metabase's metadata sync and fingerprinting scans every table it can see.** One sync per customer, against a shared replica, is real load. Expose only the curated views.
- **Policy performance.**
  - Index `tenant_id` as the leading column.
  - Check that all 40 tables actually carry `tenant_id`. Denormalize it onto any child table that doesn't. A join inside a policy is slow.
  - Wrap any per-row function in `(SELECT …)`.

## 🟢 Checked and fine

- **`WITH CHECK`:** a `FOR ALL` policy with only `USING` reuses it as the write check, and the replica is read-only anyway. This matters only if you split policies by command later.
- **Recursion:** the policy as written is a plain column compare, so it can't recurse. That changes if you add helper functions that read other RLS tables.

## Schema-per-tenant

The team's instinct has one real merit. Isolation by privilege (`GRANT USAGE` on one schema) is harder to get wrong than a predicate. Everything else counts against it:

- 900 schemas × 40 tables is **36,000 tables**, and roughly 100k relations with indexes (my estimate, assuming ~3 indexes each).
  - Every migration becomes 900 DDL runs.
  - Catalog size, `pg_dump` time, per-backend cache memory and autovacuum work all grow with it.
  - The skill flags this as the pattern that collapses past a few hundred tenants. You're past that.
- It means migrating the primary's data model and rewriting every query, to ship a replica feature.
- It doesn't touch the real gaps: identity source, schema contract, caps, credentials, PHI.

You don't have to choose between schema-per-tenant and the current plan. Keep shared tables and serve one curated schema through per-customer roles. For your largest enterprise customers, use **logical replication with a row filter** (`WHERE tenant_id = …`, PG15+) into a dedicated instance.
- That is the skill's per-tenant compute rung, with physical isolation and no noisy neighbors.
- The row-filter column must be in the table's replica identity, or UPDATEs and DELETEs won't replicate. Check this per table.
- Promote a tenant when it regularly queues others. Never raise the shared caps for everyone.

## Gates before any customer connects

1. **Isolation probe.** Run these as a second tenant's role, against every view and table, and require zero foreign rows:
   - `SET app.tenant_id = '<other uuid>'`
   - `SET ROLE`
   - `SET row_security = off`
   - direct selects on base tables
   - views joined to each other
   - `pg_stat_activity`
   - Re-run on every policy or schema change.
2. **Schema gate.** The CI contract check blocks any breaking change to `customer_api`.
3. **Cost gate.** Each customer role has an enforced timeout, a connection cap, a parallelism and `work_mem` cap, and a reaper. Check this per role.

## Pricing

Gate it to the Enterprise tier or sell it as a flat add-on, which is the skill's default shape. Only move to metered pricing if your cost exposure becomes consumption-based.

## Open questions (each changes the design)

1. Is the data PHI, and in what jurisdiction? This decides the compliance work.
2. Do customers query tables, or only the views? This decides which of the two view options in point 2 you use.
3. How many customers will take this in year one, and how large is the biggest? A small, large-tenant set favors the logical-replication route.
4. Do any customers own several org IDs? The mapping table supports it, but the policy semantics change.
5. Are agents or embedded apps issuing queries, or only humans with psql and Metabase? Agents make the hard caps non-negotiable.
6. Does the API already validate `X-Org-Id` against the authenticated user?
7. Is PgBouncer already in the stack, and in which pool mode?