# OAuth redesign: admin governance and workspace bots

The current design has one principal, the installing user, and the user's click is the only authorization. Both enterprise IT governance and bots break that assumption. The fix is to stop treating the grant as "a user's token" and model it as an installation owned by the workspace, with policy sitting above it.

## 1. Core change: three grant types

| Type | Who consents | Acts as | Token acquisition | Effective permission |
|---|---|---|---|---|
| **User grant** (today) | The user | The user | Authorization code + PKCE | app scopes ∩ admin ceiling ∩ the user's own access |
| **Admin-approved app** | A workspace admin, once | Each user who then connects | Authorization code, no per-user scope prompt beyond a light confirm | Same intersection |
| **Workspace bot** | A workspace admin | Itself (bot principal) | Client credentials | app scopes ∩ admin ceiling ∩ the bot's explicit content grants |

Today's model collapses all three into the first. The key rule is that a user token never exceeds what that user can do in the product.

## 2. Data model

- **`app_installation`** (new, owned by the workspace): `workspace_id`, `app_id`, `status` (`pending`, `approved`, `blocked`, `revoked`), `approved_scopes`, `approved_by`, `approved_at`, `created_at`, `deleted_at`.
- **`oauth_grant`**: add `installation_id` and `principal_type` (`user` or `bot`). The user grant is now a child of an installation, not a standalone record.
- **`bot_principal`** (new): `workspace_id`, `installation_id`, `name`, `role`, `owner_user_id` or `owner_team`, `created_at`, `deleted_at`. It has its own identity and appears in member lists and audit logs flagged as a bot.
- **`bot_content_grant`**: which spaces and collections the bot can read or write. The default is none.
- **`workspace_app_policy`**: `mode` (`allow_all`, `allowlist`, `admin_approval_required`, `block_all`), `scope_ceiling`, `allowed_app_ids`, `blocked_app_ids`.
- **`app_access_request`**: `user_id`, `app_id`, `requested_scopes`, `justification`, `status`, `decided_by`.

Per the SQL rules, no `ON DELETE CASCADE`. Revocation is explicit application logic with an audit entry, and rows are soft-deleted.

## 3. Admin controls (what IT asked about)

1. **Policy modes** per workspace, with the default flipped to `admin_approval_required` on the enterprise plan. SMB workspaces keep `allow_all`.
2. **Risk tiers for scopes:**
   - Low (read own content) can be user-consentable even under a permissive policy.
   - Write and read-all require admin approval.
   - Admin and bot scopes are always admin-only, regardless of policy.
3. **Request-access flow:**
   - When policy blocks a user, `/authorize` redirects to a "Request admin approval" screen instead of failing.
   - The admin gets a queue, notified by email, Slack and webhook.
   - The admin can approve for the whole workspace, approve with narrowed scopes, or deny with a reason.
4. **Admin consent URL:** `/oauth/admin/authorize?workspace=…` lets an app developer send an admin a direct link.
5. **Inventory and kill switch:**
   - A page lists every installation, its users, its scopes, and its last-used time.
   - Admins can revoke an installation, which cascades to all of its tokens.
   - Admins can also block an app workspace-wide.
6. **Audit and export:** log every consent, approval, denial, token issue, revocation, and bot action, with the actor and the acting app. Expose the log through API and SIEM export.
7. **Lifecycle via the IdP:** SCIM deprovisioning or SSO session termination revokes that user's grants. App tokens are not left alive behind a disabled employee.
8. **Public app API for admins:** list, approve, and revoke installations. Enterprise IT will want to script this.

## 4. Workspace bots

- **Auth:** client credentials grant with `private_key_jwt` (preferred) or a client secret. No human is in the loop and there are no refresh tokens. Access tokens are short-lived (≤ 1h).
- **Install:** admin-only, or a custom "manage apps" permission. Installation creates the bot principal and shows the exact content grants the admin must pick.
- **Token claims:** `sub = bot_id`, `workspace_id` as audience/tenant, `principal_type=bot`. Authorization is evaluated on every request against the bot's content grants, not just baked into the token.
- **Attribution:** posts and edits show "Bot name (app)", never a human name. Each bot has a named accountable owner for the audit trail.
- **Secrets:** support two active secrets or keys at once for zero-downtime rotation, and a per-bot revoke.
- **Limits:** a bot cannot approve apps, manage members, or read private user content unless explicitly granted. It gets its own rate limits so one runaway bot cannot starve users.
- **Ownership transfer:** if the owner leaves, the bot keeps running but flags "no owner" to admins. Do not tie its lifetime to the installer, because that is exactly the failure mode of today's design.
- **If any bot is LLM-driven:** it reads untrusted content, so prompt injection is a real path to unwanted writes. Default new bots to read-only, and require explicit write grants per space.

## 5. Enforcement points

- **Evaluate policy at request time**, not only at grant time. A block or ceiling change must take effect immediately, so the resource server checks installation status, the scope ceiling and the principal's access on each call. If tokens are JWTs, cache installation status with a short TTL (around 60s) or use introspection.
- Effective scope = `token scopes ∩ installation.approved_scopes ∩ policy.scope_ceiling`.
- Always scope tokens to one workspace. Never issue a cross-workspace token.

## 6. Threats this adds or closes

- 🔐 **Consent phishing** (a malicious app tricking users into broad grants): mitigated by risk tiers, `admin_approval_required` and a verified-app badge.
- 🔐 **Orphaned access** (the installer leaves): mitigated by workspace-owned installations.
- 🔐 **Confused deputy** (bot used to read what its caller cannot): require the bot's content grants to be explicit, and never let a bot act on behalf of a user without a user token.
- ⚠️ **Over-granting at admin approval:** show scopes in plain language, and allow narrowing before approval.

## 7. Migration

1. Backfill an `app_installation` for every existing grant, with `approved_by` set to the original installer. Mark these as `legacy`.
2. Ship the new tables and the intersection check in shadow mode: log would-be denials but don't enforce.
3. When an enterprise workspace turns on `admin_approval_required`, show a one-time review of existing installations, with bulk approve and revoke. Give a grace period (for example 14 days) before unapproved legacy grants stop working.
4. Tell app developers early. Apps must handle a new `admin_approval_required` outcome and send users or admins to the approval flow. Without that, existing integrations show an opaque failure.

## 8. Build order

1. Installation entity, backfill, policy table and request-time enforcement.
2. Admin console: policy modes, inventory, revoke, audit log.
3. Request-access queue and admin consent URL.
4. Bot principals with client credentials, content grants and attribution.
5. SCIM-driven revocation, SIEM export, admin API.

Steps 1–3 answer the three enterprise asks. Step 4 is independent once step 1 lands.

## 9. Decisions you need to make

1. **Bot billing:** does a bot count as a seat? Per-workspace pricing suggests no, but you need rate limits to compensate.
2. **Default policy for current paying customers:** do you flip the default to approval-required, or make it opt-in until they ask?
3. **Marketplace review:** do you build a verified-app program now, or rely on admin allowlists until the third-party app count justifies it?
4. **Bot user-impersonation:** do bots ever need to act on behalf of a user? I recommend no for v1, since it needs a separate delegated-token design.