# Review: Delta Sharing isolation and credentials for 40 customers

## Verdict

| Area | Verdict |
|---|---|
| Isolation (recipient property + `tenant_id` partition filter) | 🟢 Right mechanism, ⚠️ with gaps you must close |
| Customer credentials (username/password, yearly, via email) | ❌ Reject. It doesn't match how Delta Sharing authenticates, and the rotation plan is weak |
| Airflow service account with inline password | 🔴 Not fine. It is your highest-value secret |

I wrote the SQL from memory, so check the syntax against current Databricks docs before use.

## 1. Isolation

### What is right

- Databricks supports partition-scoped shares driven by a recipient property:
  ```sql
  CREATE RECIPIENT acme PROPERTIES ('tenant_id' = 'acme-001');
  ALTER SHARE telemetry ADD TABLE prod.readings
    PARTITION (tenant_id = CURRENT_RECIPIENT('tenant_id'));
  ```
- The sharing server filters the file list server-side. A recipient only receives pre-signed URLs for files in matching partitions.
- Files do not mix tenants, because Hive-style partition directories hold one tenant each. So "can't read other partitions" is a protocol-level guarantee, not a convention. Your instinct is sound.

### Gaps to close

1. **"Every table is partitioned" is a claim to verify, not assume.**
   - Liquid-clustered tables have no partitions, so the filter can't apply.
   - Check views, materialized views, and streaming tables too.
   - Check any future table someone adds to the share.
   - Add a CI check: every table in a share must be partitioned by `tenant_id` or be explicitly allow-listed as non-tenant data.
2. **The property is the whole security boundary.** A typo, a copy-paste between recipients, or a duplicate `tenant_id` means customer A sees customer B's data.
   - Manage recipients in IaC (e.g. Terraform `databricks_recipient`) with PR review.
   - Enforce one property value per recipient, unique across all 40.
   - Restrict who can run `ALTER RECIPIENT` to a small group.
   - Alert on property changes in the audit logs.
3. **Missing property.** Check what happens when the property is absent or doesn't match. Test it. It should fail closed (empty result), not open.
4. **Non-tenant tables leak by omission.** Look for shared dimension, reference, calibration, or fleet-wide aggregate tables. Also look for columns that embed other tenants' info, such as shared instrument IDs, lab names, or model benchmarks. Partition filtering only protects partitioned rows.
5. **Table-level extras.** Check history sharing, change data feed, and schema visibility against partition filtering for your table features. Confirm they respect the filter. Test, don't assume.
6. **Negative tests, not just a positive one.**
   - For each recipient, use its real credential to query for other tenants' rows. It must return zero rows.
   - Try listing files and reading the raw table directly.
   - Run this in CI after any share or recipient change.
7. **Monitoring.** Review Delta Sharing events in `system.access.audit` per recipient. Alert on unusual volume. Open sharing costs you cloud egress, so a runaway BI refresh is a bill and a signal.

## 2. Customer credentials

### Problem A: the mechanism doesn't exist

- Delta Sharing has no database username and password.
- Open sharing uses a **bearer token** in a credential file. Databricks-to-Databricks sharing uses no secret at all.
- If "username and password" means real warehouse or database logins, stop. That gives customers query access to a compute endpoint. It bypasses the partition-filter guarantee and needs a much larger access model. Don't do it.
- Use Delta Sharing and its connectors. Power BI has a Delta Sharing connector that takes a URL and token. Verify the current Tableau connector path before promising it to customers.

### Problem B: the lifecycle

- **Email is plaintext and forwardable.** A bearer token is a password with no second factor. Anyone holding it can read that customer's data.
- **Yearly rotation is too long.** An exposure goes unnoticed for up to 12 months.
- **Manual rotation across 40 customers will fail.** It happens once a year, so nobody remembers the runbook. Customers will break dashboards on cutover day.
- **Token pasted into Tableau or Power BI** gets stored in workbooks and server data sources, often under a shared analyst's account. Treat it as widely copied.

### Fix

1. **Prefer federation.** If your customers' IdPs allow it, use OIDC federation for open sharing so there is no long-lived secret to leak. Check what's available in your Databricks release.
2. **If tokens are unavoidable:**
   - Set a token lifetime of 90 days or less.
   - Deliver through Databricks' one-time activation link, sent to a named customer security contact, never as the token in an email body.
   - Rotate with an overlap window, using the existing-token expiry grace option. The old token keeps working for a few days so customers can swap without downtime.
   - Script rotation through the API, with alerts at 30 and 7 days before expiry.
3. **Add network controls.** Set an IP access list on each recipient where the customer has stable egress.
4. **One recipient per customer environment** (prod versus test BI), so revoking one doesn't cut everything.
5. **Write a revocation and offboarding runbook.** Drop the recipient, then check the audit log for the last access.

## 3. Airflow service account

"Fine internally" doesn't hold here.

- **Inline passwords leak.** They show up in Airflow's connections UI and exports, the metadata DB, task logs, stack traces, and git history.
- **Blast radius is everything.** A data-team account that reads all tenants means one leak exposes all 40 customers, which defeats the isolation design in section 1. If it can also modify shares or recipients, it can undo the boundary itself.
- **Fix:**
  1. Use a Databricks service principal with OAuth M2M (short-lived tokens), or workload identity federation if Airflow runs somewhere that supports it.
  2. Store any remaining secret in a secrets backend (Vault, AWS Secrets Manager, Azure Key Vault, etc.) via the Airflow secrets backend. Never put it in the connection string.
  3. Separate duties:
     - The **pipeline principal** reads and writes tables, with no sharing privileges.
     - The **sharing-admin identity** manages recipients and shares, with human review and IaC.
  4. Treat the current password as **already exposed**. Rotate it now, then grep git history, Airflow logs, and exported connections for it.

## 4. Priority order

1. ⏳ Rotate the Airflow password and move it to a secrets backend (today).
2. ⏳ Verify every shared table is partitioned by `tenant_id`, and list any non-tenant tables (this week).
3. ⏳ Put recipients and shares in IaC, with a uniqueness check and the per-recipient negative-access test in CI (before onboarding any customer).
4. ⏳ Replace the username/password plan with federation, or with 90-day tokens delivered via activation link and rotated with overlap (before onboarding).
5. ⏳ Add audit-log alerts and the revocation runbook (before go-live).

## Open questions for you

- Do any of the 40 customers' IdPs support OIDC federation?
- Are any shared tables liquid-clustered, or views?
- Does the Airflow account hold sharing-admin privileges today?