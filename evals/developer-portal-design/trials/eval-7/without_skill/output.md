# Sable Grid account model

## Summary

1. The **Organization** owns billing, SSO, and keys. A **User** is a person who can belong to several organizations through a **Membership**. A membership carries one role.
2. Every organization has two **Environments**, `test` and `live`. API keys belong to an organization and an environment, never to a user. Test keys can't read live data, and test usage is never billed.
3. Roles become a fixed set built from permissions. A new `billing` role sees spend and invoices but has no key permissions at all.
4. Partners are organizations with `kind = partner`. They must use SSO, and `live` stays locked until Sable Grid staff approve them. Self-serve organizations activate `live` themselves.

## 1. Entities

| Entity | Purpose | Key fields |
|---|---|---|
| **Organization** | Contract, billing, and tenancy boundary | `id`, `name`, `kind` (`self_serve` \| `partner`), `status`, `billing_contact`, `created_at`, `deleted_at` |
| **User** | One human identity, global | `id`, `email` (verified), `auth_methods`, `created_at`, `deleted_at` |
| **Membership** | Links a user to an organization with a role | `org_id`, `user_id`, `role`, `source` (`invite` \| `sso_jit` \| `scim`), `created_at`, `deleted_at` |
| **Environment** | `test` or `live` slice of an organization | `org_id`, `type`, `status` (`active` \| `locked`), `approved_by`, `approved_at` |
| **ApiKey** | Credential for one organization and environment | `id`, `org_id`, `env`, `name`, `prefix`, `secret_hash`, `scope`, `created_by`, `expires_at`, `last_used_at`, `revoked_at`, `created_at` |
| **SsoConnection** | SAML or OIDC config for one organization | `org_id`, `protocol`, `idp_metadata`, `verified_domains[]`, `enforced`, `group_role_map` |
| **AccessRequest** | Approval record for a partner's `live` environment | `org_id`, `requested_by`, `status`, `reviewed_by`, `reviewed_at`, `contract_ref`, `note` |
| **AuditEvent** | Append-only log | `org_id`, `actor`, `action`, `target`, `ip`, `at` |

Conventions that follow your rules:
- Soft delete everywhere, with `deleted_at TIMESTAMPTZ`.
- No `ON DELETE CASCADE`.
- Every table has `created_at`.
- Key secrets are hashed, shown once at creation, and never retrievable afterward.
- Key prefixes encode the environment (`sg_test_…`, `sg_live_…`), so a leaked key is identifiable at a glance.

## 2. Test and live environments

- **Environment is a column on every tenant-owned row**: keys, usage, meters, webhooks, and rate limits. It is not a separate organization. A second account per customer would duplicate billing, SSO, and membership.
- **Isolation is enforced at the gateway.** The key's `env` decides which data partition the request can reach. A `test` key sent to a `live` resource gets 403.
- **Test behaves like a sandbox.**
  - It returns deterministic synthetic meter data.
  - It never produces billable usage.
  - It has its own, lower rate limits.
  - It has its own webhook endpoints and signing secrets.
- **Availability differs by kind.**
  - A self-serve organization gets `test` at signup and `live` after email verification and a payment method.
  - A partner organization gets `test` as soon as its SSO connection is verified. `live` stays `locked` until approval (section 5).
- **Each environment has a key cap**, for example 10, so a leak is bounded and a key listing stays readable.

## 3. API keys

- **Multiple keys per environment.** Each has a required `name`, such as "billing-sync-prod", and that name is what finance sees.
- **Created by a user, owned by the organization.** When someone leaves, their keys keep working unless revoked. Offboarding triggers a prompt to review keys they created, and the audit log records `created_by`.
- **Rotation without downtime.** Creating a second key, switching clients, and then revoking the old one all work because multiple keys are allowed. Optional `expires_at` supports scheduled rotation.
- **Scopes start coarse**: `read` or `read_write`. Finer per-resource scopes can follow later without a schema change.
- **Partner option: IP allowlist per key**, since partners' security reviews usually ask for it.
- **Keys are not tied to SSO.** SSO governs human login only. Machine credentials stay independent, and disabling a user in the IdP never silently breaks production.
- **Existing keys migrate to a `live` key named `default`.** No customer integration breaks.

## 4. Roles and permissions

Roles are fixed bundles of permissions. Custom roles are out of scope for now.

| Permission | Owner | Admin | Developer | Billing | Viewer |
|---|:-:|:-:|:-:|:-:|:-:|
| View usage and data (own environment access) | ✅ | ✅ | ✅ | ❌ | ✅ |
| View key list and metadata | ✅ | ✅ | ✅ | ❌ | ❌ |
| Create or revoke **test** keys | ✅ | ✅ | ✅ | ❌ | ❌ |
| Create or revoke **live** keys | ✅ | ✅ | ❌ | ❌ | ❌ |
| View spend, invoices, plan | ✅ | ✅ | ❌ | ✅ | ❌ |
| Edit payment method and plan | ✅ | ❌ | ❌ | ✅ | ❌ |
| Invite and manage members | ✅ | ✅ | ❌ | ❌ | ❌ |
| Configure SSO and role mapping | ✅ | ✅ | ❌ | ❌ | ❌ |
| Delete organization, transfer ownership | ✅ | ❌ | ❌ | ❌ | ❌ |

Details:
- **Billing is the finance request.** It holds `billing.read` and `billing.write` and no `keys.*` permission. Spend appears grouped by environment and by key name, which is a label, never a secret or a key-list page. Billing members can't open the keys page, the key prefix, or the key IDs. If you'd rather finance see no per-key breakdown at all, drop the grouping. That's a one-line change.
- **Test is more open than live.** Developers can create test keys freely and can't touch live keys. That gives customers the separate test credentials they ask for with little risk.
- **At least one owner per organization.** The last owner can't be removed or demoted.
- **Role enforcement happens in the API, not the UI.** The dashboard hides what a role can't do, and the backend rejects it anyway.

Migration mapping for current roles:

| Old role | New role |
|---|---|
| `admin` | `admin` |
| `member` | `developer` |

The earliest admin in each organization becomes `owner`. No one loses access they have today.

## 5. Partner organizations

**Lifecycle** (`Organization.status`):

1. `invited`: Sable Grid creates the organization from the signed contract. Contract reference is stored.
2. `sso_pending`: the partner's first owner signs in with a one-time link and configures SSO. Domain verification via DNS TXT is required.
3. `pending_approval`: SSO verified and `test` active. The partner (or Sable Grid on their behalf) files an `AccessRequest` for `live`.
4. `active`: staff approved, and `live` is unlocked.
5. `suspended`: `live` is locked and keys are rejected. Data is retained.

**Rules:**
- **SSO is enforced.** Human login is SSO-only once the connection is verified. Passwords and social login are disabled for that organization's members. A user whose email domain isn't verified for the organization can't join it.
- **Provisioning.**
  - Just-in-time on first SSO login, with the role taken from IdP groups through `group_role_map`. The default is `viewer`.
  - SCIM is a later phase for the partners who require automated deprovisioning.
  - Until then, removal in the IdP blocks login but leaves the membership row. A nightly job reconciles stale memberships.
- **Approval is org-level.** Staff review the contract and the SSO setup, then approve `live`. The decision is recorded in `AccessRequest` and `AuditEvent` with reviewer and time.
- **Approving individual users is not modeled.** The organization's owner controls who gets which role inside it. The partner's legal team, not Sable Grid, vets individual employees. If your contracts actually require per-user approval, I'd add a `pending` membership state, but that needs your confirmation.
- **Break-glass.** Each partner has two named owners. A Sable Grid staff recovery path exists, logged and requiring two staff members, for a lost IdP.
- **Staff tooling is separate.** Sable Grid staff use an internal admin system with its own identities. They are not members of customer organizations, and every impersonation or approval writes an `AuditEvent`.

## 6. Self-serve organizations

- Public signup creates a User, an Organization (`kind = self_serve`), and an owner Membership in one step.
- Email verification is required before any key is issued.
- `test` is available immediately. `live` unlocks once a payment method is on file. Staff don't review it.
- The same role set applies. The Billing role is available to a self-serve team that adds a finance colleague.
- SSO is not offered to self-serve in v1. A self-serve organization that needs SSO converts to a contracted partner.

## 7. Cross-cutting

- **A user in several organizations** switches organizations in the dashboard. Each organization's SSO policy applies when switching into it, so a partner session must come through SSO.
- **Audit log** covers key creation, revocation, and last-use anomalies, role changes, SSO changes, approvals, and logins. Organization owners and admins can read their own log. Retention is at least 12 months.
- **Rate limits and quotas** attach to `(org, env)`. `test` has its own, lower ceiling.
- **Billing** attaches to the organization's `live` environment only.

## 8. Rollout

1. **Schema and backfill.**
   - Create Organization, Membership, Environment, and the new ApiKey shape.
   - Map each existing account to an organization with one `live` environment and move its key.
   - Set `kind = partner` for the 35 contracted accounts.
   - Existing partners start `active`, so nothing locks them out.
2. **Test environment and multiple keys.** This delivers the most-requested feature. It can ship without the role changes.
3. **New roles, including Billing, with the spend views.** Roles are renamed through the mapping in section 4.
4. **SSO for partners.** Enforcement is switched on per partner, scheduled with each one.
5. **Approval workflow** and the staff tooling for new partners.
6. **SCIM**, only for partners who require it.

Phases 2 and 3 each ship independently of the others.

## 9. Assumptions to confirm

1. The 35 existing partners may be backfilled straight to `active`, with SSO enforcement scheduled afterward.
2. Partners get `test` before `live` approval. If legal says no access at all before approval, keep `test` locked too. It's one flag.
3. Approval is per organization, not per user.
4. Finance may see spend grouped by key name.
5. No custom roles are needed yet.