# Ferncroft Labs: Delta Sharing review (isolation and credentials)

I read the skill and its references. I haven't seen your workspace, so the Databricks-specific mechanics below are marked where you need to verify them.

## Verdict

| Area | Status |
|---|---|
| Isolation (recipient property plus partition filtering) | ❌ Fails the isolation gate. It's an optimization, not access control. |
| Customer credentials (username/password, yearly rotation by email) | ❌ Bottom of the credential ladder. |
| Airflow service account (inline password) | ❌ "Fine internally" doesn't hold. Same anti-pattern. |
| Governance and cost caps | ⚠️ Not in the plan. Required before any customer connects. |
| Schema contract | ⚠️ Not in the plan. |

Per the skill, isolation (step 3) and cost caps (step 6) must both pass before any customer gets a handle.

## 1. Isolation

### Why the current plan fails

- **Partition filtering isn't access control.** Delta Sharing documents recipient-property partition filtering as best-effort. The skill says to treat it as a performance optimization only.
- **"Physically only reads their own partitions" is a claim, not a guarantee.** You'd be betting 40 customers' data on it. This is the named failure class for this surface: one miss returns another customer's rows. It can happen through:
  - a table whose partitioning drifts
  - a new table added to the share without `tenant_id` partitioning
  - a property typo or a missing property
  - a recipient with an empty or wrong property
- **The failure mode is silent.** No error, just foreign rows.

### Fix

1. Don't share base tables. Share only dynamic or secure views.
2. Keep the private base table and a private entitlement table (`recipient → tenant_id`) out of the share.
3. Write each view's predicate on the share-aware identity, `current_recipient()`, joined to the entitlement table.
4. Never use `current_user()` or `is_member()` in a shared view. They return `NULL` across a share boundary, so the predicate matches nothing, or everything, depending on its shape.
5. Keep your partition filtering as a performance layer on top. Isolation comes from the view predicate alone.

### Verify these before building

I'm working from general Databricks knowledge here, not from the skill.

- **Open-sharing recipients may not be able to receive dynamic views.** Dynamic-view sharing is, as I recall, limited to Databricks-to-Databricks recipients.
  - Tableau and Power BI customers using bearer-token (open) sharing may not qualify.
  - If so, the fallback with hard isolation by construction is **one share per customer**, containing only that customer's data. That means per-tenant tables or a replicated copy, which moves you to the "replicated copy" rung in step 2.
  - Check the current Databricks docs for your recipient types.
- **40 customers on shared compute:** confirm whether any customer will park dashboards on it. Scan frequency decides zero-copy versus replica (see section 3).

### Isolation gate (binary, before GA and after every change)

- Run probe queries as another tenant, using a second test recipient.
- Cover every shared view or table.
- Require zero foreign rows.
- Test the cases that break the partition-filter story:
  - a recipient with no property set
  - a recipient with a wrong property
  - a new table added without partitioning
- Re-run on every policy or schema change.

## 2. Credentials

### Customer credentials

Preference order: **short-lived token > managed secret > static password**.

| Your plan | Problem |
|---|---|
| One DB username/password per customer | Static password at the bottom of the ladder. The industry is retiring these. |
| Pasted into Tableau or Power BI | The tool stores a long-lived secret on analyst laptops and shared workbooks. |
| Rotated yearly | A leaked credential has a one-year replay window. |
| Rotated over email | Secrets travel in a mailbox, cached and forwarded. |

Replace with:

1. **BI tools:** OIDC federation or OAuth, using authorization-code with PKCE for desktop tools. The tool then never stores a database password. Delta Sharing supports OIDC federation, so there's no shared secret at all.
2. **Clients that can't refresh tokens:** degrade to a service account with key-pair auth or a PAT with a policy-bound maximum expiry. Never fall back to a static password. Check each BI client's refresh capability before promising OAuth-only.
3. **Bearer tokens where unavoidable:** short expiry, scoped to one tenant's entitlement, with no email delivery.
   - Issue through the product UI, shown once.
   - Give customers self-service issuance and revocation.
   - Rotate with dual-credential overlap (old and new valid together), so rotation doesn't break dashboards. Follow the discipline in the API key sibling skill.
4. **TLS** is a stated, named requirement. Don't leave it to client defaults.
5. **Connection-setup page** for each supported client (Tableau, Power BI):
   - URL template
   - driver or connector download
   - TLS requirement
   - auth method and where the credential comes from

### Your Airflow service account

"Fine internally" isn't a reason in this skill. Inline credentials in a connection string are "the anti-pattern no documented path should show."

- A password in the connection string leaks through Airflow's UI, logs, DAG exports, backups, and git.
- Move to key-pair auth or workload identity: short-lived signed tokens, no password on the network.
- Mark the identity service-type so the engine refuses password auth for it.
- Use Airflow's secrets backend for any remaining secret material. Keep it out of the connection URI.
- Scope the account to what the data team needs, and don't reuse the credential across environments.

## 3. Gaps the plan doesn't mention

1. **Cost caps (step 6, a gate).** Delta Sharing's provider pays cross-region egress, which grows with each customer's query volume. No cost control is on by default.
   - Set a statement timeout and a queued-statement timeout.
   - Set a per-tenant concurrency cap.
   - Set a spend cap or budget alarm, separate from the timeouts.
   - Back the share with an egress-free object store if possible.
   - Don't raise the shared cap for everyone to accommodate one tenant. Move that tenant to larger or isolated compute.
2. **Scan economics (step 2).** Zero-copy is the right default for infrequent scans.
   - One practitioner's heuristic: about 20 scans per day on a roughly 200 GB table makes live scanning cost more per month than a replica costs per year. Treat it as a rule of thumb, not a benchmark.
   - A 40-viewer morning dashboard is past the line. Measure before committing.
3. **Schema stability (step 4).**
   - Share a curated mart layer. Never share the live operational telemetry schema.
   - Make changes additive-only, using expand/contract.
   - Enforce the contract in CI (dbt model contracts or the `datacontract` CLI), not in a doc.
   - Cover schema, quality, freshness, and availability.
4. **Pricing (step 8).** Package this as a paid add-on or tier gate, not a free feature. The price is also a governance control.

## 4. Questions for you

1. Are the 40 customers open-sharing recipients (token, non-Databricks) or Databricks-to-Databricks? This decides whether dynamic views are available.
2. How often will customers scan, and how big are the tables? Do dashboards get parked on it?
3. Which consumers matter most: Tableau, Power BI, notebooks, or agents?
4. Do you share raw operational tables or a curated mart today?
5. Is this a free feature, a tier gate, or a metered add-on? And who pays query compute and egress?
6. What are your ship date and effort ceiling?

## 5. Order of work

1. Answer question 1. It decides the isolation mechanism.
2. Build the entitlement table and secure views, or per-customer shares as the fallback.
3. Run the other-tenant probe gate until it returns zero foreign rows.
4. Set cost caps on every compute handle.
5. Move customer auth to OIDC or OAuth, with the degradation path.
6. Move the Airflow account to key-pair or workload identity.
7. Publish the schema contract and enforce it in CI.
8. Publish the connection-setup pages.