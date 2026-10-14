# OAuth design changes for Hollowpine: org-level app control and workspace bots

## Summary

Today the design has one consent party, the installing user. You need two changes:

1. **Two-party consent for delegated apps.** The workspace admin sets policy and the user then consents inside it. This answers the question your last three enterprise deals asked.
2. **A second kind of principal for bots.** A bot is a workspace-owned service identity with its own permissions, authorized by an admin. It is not a user's token with the human removed.

Don't extend the user-grant model to cover bots. A bot has no person to click Allow, so it needs its own principal, grant path and lifecycle.

## 1. Delegated apps: add workspace policy above user consent

### Data model

| Entity | Purpose |
|---|---|
| `App` | Global client registry: publisher, verified flag, maximum scopes, redirect URIs. |
| `AppInstallation` | Workspace × App. Status is `pending`, `approved` or `blocked`. Holds a **scope ceiling**, `approved_by` and `approved_at`. |
| `UserGrant` | User × Installation. Holds the scopes the user accepted (a subset of the ceiling) and the refresh-token family. |
| `AccessRequest` | A user asks for an app. Holds the reason, the admin decision and who decided. |
| `WorkspacePolicy` | The consent mode, the always-admin scope list, and optional group/role restrictions. |

The grant is scoped to the workspace, not the user globally. You sell per workspace, and one person can belong to several workspaces with different policies.

### Workspace policy modes

- **Open:** users may consent to anything except high-risk scopes.
- **Verified only:** users may consent only to verified apps with low-risk scopes.
- **Admin-approved only:** users may connect only apps on the allowlist. This is the one enterprise buyers will pick.
- **Blocked:** no third-party apps at all.

High-risk scopes always need an admin in every mode except Blocked, where no apps connect at all. Examples are write on all content, export, member management and admin APIs.

### Authorization flow

1. The authorize request resolves the workspace context first.
2. The server evaluates policy before rendering consent.
3. If the app is allowed, it shows the normal Allow screen. That screen now names the workspace, the publisher, the verified status and the scopes.
4. If the app is not allowed, it shows "Request admin approval" instead of Allow. This creates an `AccessRequest` and notifies admins. Don't just return an error.
5. The effective scope is the intersection of the requested scopes, the installation ceiling, and the user's own permissions in that workspace. An app can never exceed what its user could do.

### Enforcement beyond the consent screen

- Check installation status on every token refresh and on every API call, or use access tokens with a TTL of 5–10 minutes plus revocation events. "Blocked" must take effect within minutes, not at token expiry.
- Revoke grants automatically on user removal, on SCIM deprovisioning, and when SSO sessions are terminated.
- Give admins a one-click "revoke all tokens for app X" action.

### Admin surface

- Installed apps list, with users per app and scopes granted.
- A pending-requests queue.
- Block, revoke and change-ceiling actions.
- An audit log of consents, requests, approvals, revocations and token issuance, with SIEM export. Enterprise IT will ask for this in the same breath as app control.

### Migration

Existing installs were made without org policy. Convert each one into an `AppInstallation` with status `legacy-unreviewed`. Show them to admins in a "discovered apps" queue and give them a grace period, for example 30 days, to approve or block. Don't silently approve them and don't silently break them.

### Protocol hygiene

- Require PKCE and exact-match redirect URIs.
- Treat dynamically registered or unverified clients as untrusted. They default to `pending` in every workspace.
- Surface policy denials with distinct errors such as `admin_approval_required`, so app developers can show a useful message.

## 2. Workspace bots: a separate principal

### Identity and grant path

- A `Bot` principal belongs to the workspace, not to a user. It has its own ID and appears in content as a bot, for example "Release Notes Bot, installed by Dana".
- An **admin consent flow** installs it. The admin approves the bot's scopes and its resource access once. No end user ever sees an Allow screen.
- It authenticates with the client-credentials grant, using `private_key_jwt` or a rotating secret. Access tokens are short-lived (1 hour or less) and have no refresh token.
- Only workspace admins with an install permission can install bots. Make "app-only" scopes a separate set from delegated scopes, so an app can't quietly request a bot-grade scope through a user.

### Permissions: least privilege by default

- A new bot can read nothing. An admin or the space owner explicitly grants each collection or space.
- "Reads and posts as itself" means its permissions are its own. They are not a union of the installer's permissions.
- A private space needs a grant from that space's owner, not just from a workspace admin.
- A bot can't take admin actions, approve other apps, or mint other bots.

### Ownership and lifecycle

- Every bot has a named human owner for accountability. When that person leaves, the bot must be reassigned. Alert admins about orphaned bots rather than letting the bot die with the installer's account.
- Support suspend, rotate (two secrets active during rotation), and delete.
- Add per-bot rate limits and quotas. If bots don't consume seats, quotas are what protect your costs. See the pricing question below.
- Optional IP allowlisting for enterprise.

### Attribution

Every bot write is audited as bot X, installed by Y, authorized by Z. The UI must make bot content visibly distinct, and bot content can't be edited as if a human wrote it.

### The confused-deputy risk

A bot answering questions for many users can expose content that a given asker couldn't see. Two rules:

- If a bot acts on a specific user's request, use a delegated, on-behalf-of token for that user.
- If it uses its own identity, its permissions are the ceiling for everything it serves. Tell admins this at grant time: whatever a bot can read can leave the workspace through that bot.

## 3. Suggested rollout

1. **Policy foundation:** `AppInstallation`, `WorkspacePolicy`, policy check at authorize and refresh, allowlist UI, audit log, and the legacy-install migration. This alone answers the enterprise deals.
2. **Request flow:** the access-request queue, scope ceilings, and group/role restrictions.
3. **Bots:** principal, client credentials, resource grants, ownership and rotation.
4. **Enterprise integrations:** SIEM export and SCIM-driven revocation.

## Decisions for you

1. **Default policy for new workspaces.** I recommend verified-only for self-serve and admin-approved-only for enterprise.
2. **Do bots take seats?** I recommend no seats, with per-bot quotas, since you price per workspace.
3. **Plan packaging.** Decide whether full app governance (SIEM export, group-based policy) sits in the enterprise tier. I recommend basic allow/block for all plans and the rest for enterprise.
4. **Legacy grace period length.** I suggest 30 days.

I didn't read your codebase, so this is a design-level answer. I can map it onto your current OAuth implementation if you want.