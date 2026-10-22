# Hollowpine OAuth redesign: admin governance and workspace bots

**Next action:** add a second consent surface (the workspace admin) and a second token type (bot/app identity). The protocol core stays as it is. Everything below hangs off those two changes.

I couldn't ask the skill's clarifying questions first, so I assumed three things. Correct me and I'll re-rank:
- **Retrofit:** you have live apps and live user-delegated tokens.
- **Bots:** third-party apps may hold bot tokens, not just Hollowpine's own first-party bots.
- **Data:** no regulated financial or health data, so DPoP and PAR stay out (Stage 4).

## What stays unchanged

- **Grants and PKCE:** authorization_code with PKCE S256 for every client, plus `client_credentials`, `refresh_token` and `device_authorization`. No implicit or password grant, and exact redirect matching.
- **User-token lifecycle:** access tokens last about 1 hour. Refresh tokens rotate with family reuse detection and a 10-30 second grace window.
- **Registration:** manual portal registration with review. Open dynamic registration (DCR) stays deleted.
- **Why the core holds:** none of these assumed one consenter. The assumption lives in the consent topology, the scope-to-token-type binding, and the verification gate.

## Change 1: IT control over which apps employees connect

The skill's B2B split applies directly: the end user's "yes" is no longer sufficient. Build the admin surface as a first-class part of consent and scopes, not a patch.

1. **Per-workspace app policy.** The workspace owns one setting with these modes:
   - Open: users may consent to any app, subject to the scope tiers below.
   - Verified-only: users may consent only to apps at or above a chosen verification tier.
   - Allowlist: only admin-approved apps.
   - Admin-approval-required: every install needs an admin.
2. **Request-an-install flow.** When policy blocks a user, they get a "request admin approval" path, not a dead-end error. The admin sees a queue showing app, requester, scopes and verification signals.
3. **Scope tiers by consenter.**
   - *User-level scopes* touch the user's own data and can be consented by the user.
   - *Workspace-level scopes* reach other people's content or org-wide data and need an admin.
   - The same admin-only split is why Microsoft restricts application permissions to admins.
4. **Org-wide grant review.** Give admins:
   - an inventory of every app, user and scope in the workspace;
   - per-app "revoke for everyone";
   - an audit log of installs, approvals, denials and revocations.
5. **Enforce policy at use time, not only at consent.**
   - Evaluate policy on every authorization, refresh and introspection.
   - A newly blocked app then dies within the access-token TTL (about 1 hour), and its refresh families are revoked.
   - This is the main thing enterprise IT will test.
6. **Grant identity is (user, app, workspace).** Your product is sold per workspace, so consent must be workspace-scoped. A person in two workspaces consents separately in each.
7. **Offboarding.** Deprovisioning a user (SSO/SCIM) revokes their user-delegated grants. Verify this with a test.

**Verification feeds policy.** This is the gate that makes "verified-only" mean something.
- **Tiers:** publisher identity verification for every listed app, self-attestation as the middle rung, third-party security assessment as the top rung. Show them as three distinct signals. One undifferentiated checkmark misleads admins.
- **Bright line:** any scope reaching other users' data or PII requires the third-party assessment before public listing. Workspace-level scopes and bot scopes fall under it.
- **Unverified apps:** keep the Google-style testing lane with enforced ceilings (named test users, warning screen, hard user cap, short token expiry).
- **Runtime enforcement:** reject any scope request that isn't a subset of what was approved at registration.
- **Custom apps:** a customer's IT team will also want internal apps, registered in and usable only inside their own workspace. They skip public listing review but still pass the admin approval gate. This is my design suggestion, not from the skill.

**Consent copy for admins:**
- **Per-scope sentence:** use a plain-language sentence for each scope. Never use grouped buckets or raw scope strings.
- **Partial grants:** support them and diff granted against requested server-side, always.
- **Re-consent:** show only the net-new scope.
- **Acting identity:** state whether the app acts as the user or as itself.
- **Batch additions:** a new scope forces re-consent, and for workspace-level scopes it forces re-approval by an admin.

## Change 2: workspace bots (no human behind them)

This is the bot-versus-user token-type split. The skill names it a failure mode when deferred: Slack's migration "requires reauthorization from every user".

1. **Bind every scope to a token type now.**
   - Add a token-type field to each scope: `user` (delegated) or `bot` (app identity).
   - Declare all existing scopes `user`-bound. That matches how they behave today, so nothing breaks.
   - Scopes are additive-only. Never repurpose an existing scope's meaning for bots.
   - Bot scopes can reuse the `resource:action` names, as Slack does, but only with the binding explicit in the taxonomy and the consent copy.
2. **Bot installs are admin-only.** A bot has no human whose permissions bound it, so an admin must approve the install.
3. **The grant belongs to the workspace, not the installer.** The bot must survive the installing admin leaving. Record the installer for audit only.
4. **Bots are confidential clients only.** No public-client bots.
5. **Token mechanics.**
   - Mint short-lived (about 1 hour) installation-scoped tokens via `client_credentials`, bound to the workspace installation, in the GitHub installation-token style.
   - No refresh tokens: a bot re-mints.
   - Opaque tokens revoke instantly. If you use JWTs, the short TTL is your revocation story.
6. **Bots get their own permission set.**
   - The bot's reach is whatever the admin granted it, never an implicit "everything the installer could see".
   - A knowledge base has sensitive spaces. Add per-collection or per-space restriction on the bot installation so it sees only what it was explicitly given.
   - This is the first step of the skill's "fine-grained per-resource permissions" rung. It is justified here because org admins now demand approval policies and bot scopes reach org-wide data.
   - Do not build a full 50-permission taxonomy now (the skill calls that a quarters-long project). Keep `resource:action` as the default and keep the coarse tier alive during migration.
7. **Attribution and audit.**
   - Every write by a bot shows the bot as the actor, never a human.
   - The audit log records actor type (user, app-on-behalf-of-user, bot) and which installation.
   - "Read and post as themselves" depends on this.

## Verification updates for bots

Every bot scope that reads workspace content reaches other users' data. That triggers the top verification tier before public listing.

## Failure modes to avoid

- Putting admin policy only at consent time, so a blocked app keeps working on live tokens.
- A bot grant tied to the installing user.
- Reusing user-scope semantics for bots without an explicit token-type binding.
- An org-wide bot with no per-collection restriction.
- One trust badge for identity, attestation and audit.
- A dead-end block message with no request-approval path.
- Assuming granted scopes equal requested scopes.
- Citing a consent conversion percentage as fact.

## Gates before shipping

- **Policy enforcement:** an app blocked mid-session fails on its next refresh or introspection, and its refresh families are revoked.
- **Offboarding:** deprovisioning a user revokes their grants.
- **Admin-only scopes:** a non-admin cannot consent to a workspace-level or bot scope.
- **Bot survival:** a bot keeps working after its installer is removed.
- **Actor attribution:** a bot write is attributed to the bot, not a human.
- **Partial grants:** the integration test exercises the server-side diff.
- **Re-consent:** the screen shows only the net-new scope.
- **Verification:** every scope has a named tier, runtime subset-of-approved enforcement is live, and the unverified-lane cap is enforced.
- **Existing gates:** the protocol conformance and refresh-reuse tests still pass.

Baseline these from launch (the skill says no industry thresholds exist):
- admin approval turnaround;
- share of apps requesting scopes their traffic never uses;
- reuse-detection trip rate.

## Sequencing (my recommendation)

1. Token-type binding in the scope taxonomy, plus the (user, app, workspace) grant model. This is hard to retrofit, so do it first.
2. Admin policy engine, request-approval queue, org-wide revoke and audit log. This is what the three enterprise deals asked for.
3. Bot installation, `client_credentials` installation tokens and per-collection restriction.
4. Verification tier wiring: policy by tier, and the third-party assessment gate for bot and workspace-level scopes.

## Open questions

These change the answer:
1. Are workspace bots first-party only, or can third-party apps hold bot tokens? That decides how much of step 4 you need now.
2. What is the retrofit size: live apps, current scope list, and whether refresh rotation is already on?
3. Do you already have SSO/SCIM in the product? Offboarding revocation depends on it.
4. Do any customers need bots to reach regulated data? If yes, promote DPoP or mTLS (sender-constraining) to this release.
5. Is this an enterprise-deal unblock or the foundation of an app ecosystem? It sets how far to take verification and review.