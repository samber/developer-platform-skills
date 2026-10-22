# Hollowpine OAuth provider: changes for enterprise admin control and workspace bots

I read `SKILL.md` and its four references. The skill says to ask clarifying questions first. You asked for the full answer, so I've stated my assumptions below and listed what would change them at the end.

## Verdict

Your current design has one consent surface and one token type. You need two of each:

- **Consent:** the end user, plus a workspace admin who can gate installs.
- **Token:** user-delegated, plus app-identity (the bot).

Neither change touches the protocol core: PKCE on every client, exact redirect matching, no implicit or password grant, and refresh rotation with family reuse detection and a 10–30s grace window all stay as they are. The changes land in steps 2 and 3 of the skill (scope taxonomy and consent, then registration and verification), plus a new admin surface. The skill says to build that surface up front, "not bolt it on when the first enterprise customer asks". Your three enterprise deals are that moment.

## Assumptions

- Question 3 (do apps also act with their own identity?) is now answered: yes, via workspace bots.
- Question 5 (who approves an install?) is now answered: users and admins.
- Question 4 (can any scope reach other users' data or bulk data?) is also answered: a bot that reads a knowledge base reaches content belonging to many people. This sets the verification tier (see change 4).
- I assume this is a retrofit with live integrations, not a greenfield build.
- I assume the client mix is mostly server-side confidential apps.

## Change 1: Add a workspace admin consent surface

**Policy.** Each workspace gets an app-install policy with four modes:

- Users may install any verified app.
- Users may install allow-listed apps only.
- Every install needs admin approval.
- Installs are blocked.

Enterprise plans should default to "needs admin approval".

**Effective grant.** `requested ∩ user-consented ∩ admin ceiling`. Admins can approve a subset of the scopes an app requests. Run the same server-side granted-vs-requested diff you run for end users, because admin partial approval has the same silent-mismatch trap.

**End-user screen under an approval policy.**
- It becomes "Request approval", with an optional reason field.
- It keeps the per-scope plain-language sentences.
- The request lands in an admin queue.

**Admin queue shows:**
- Requested scopes, each tagged with its token type.
- The three trust signals, kept visually distinct: publisher identity, self-attestation, third-party audit. One merged checkmark misleads buyers.
- Who requested the install, and the data classes the app can reach.

**Admin tools:**
- List and revoke an app workspace-wide.
- List per-user grants.
- Re-approve when an app adds scopes. The screen shows only the net-new scope, not everything already granted.

**Enforcement at runtime.**
- Re-check policy at every token issuance and every refresh. Otherwise a revoked or de-listed app keeps working until its refresh token expires.
- Keep access tokens at about 1 hour, so an admin block takes effect quickly even on JWTs, which can't be revoked mid-life.
- Bind every grant to a workspace. Your product is sold per workspace, so a person's consent in workspace A must not carry into workspace B.

**Verification as a policy lever.** Unverified publishers can't get consent beyond basic profile in workspaces with approval policies. This is Microsoft's real enforcement lever, per the skill. An admin may override it per app, as an explicit exception.

**Operational consequences (my judgment, not from the skill):**
- Emit audit events per workspace: install requested, approved, denied, token issued, revoked, reuse detected. Enterprise IT will ask for these next.
- Cascade user deprovisioning to that user's delegated tokens.

## Change 2: Split every scope by token type now

**Do this before the bots ship.** Slack's documented price for deferring it is "reauthorization from every user".

- Add a binding field to scope metadata: `delegated` or `app`. Keep the `resource:action` names with the read/write split.
- Treat all existing scopes as `delegated`. Do not change their meaning (scopes are additive-only).
- Write separate consent and admin-queue copy per type.
  - Delegated: "Read pages you can see."
  - App: "Read all pages in the spaces you select."
  - These are not the same grant. Delegated access can never exceed the user's own permissions. App access is independent of any user.
- Add an admin-only tier for org-wide scopes: member lists, audit data, admin APIs. These need admin consent even when delegated.

**Do not add a catch-all scope**, such as a `bot:full_access`. The skill deletes that pattern.

## Change 3: Design workspace bots as a separate principal

**Identity and ownership**
- Create the bot as its own principal in the workspace.
- It reads and posts under its own name, so page history and audit logs never show the installer.
- The workspace owns it, not the installer. If the installer leaves, the bot survives and an admin reassigns ownership.
- Keep at least one named admin owner per bot.

**Consent**
- App-type scopes are admin-consent-only. A non-admin who clicks Allow can only file a request.
- Microsoft enforces the same rule for application permissions.

**Token mechanics**
- Bots are confidential clients.
- Use `client_credentials` scoped to the installation. Use short-lived (~1h) access tokens, minted on demand.
- Do not copy Slack's default of non-expiring bot tokens with rotation as an opt-in.
- Tokens die on uninstall, admin revoke, or app suspension.
- If you issue refresh tokens to bots, use rotation with reuse detection.
- My recommendation, not in the skill: prefer asymmetric client authentication (`private_key_jwt`) over a shared secret for bots.

**Blast radius**
- A bot with org-wide read plus no human attached is the long-lived, high-radius token the skill flags as a reason to promote sender-constraining (DPoP or mTLS) from step 4.
- Whether to promote it depends on your build substrate (question 6). If your identity product ships DPoP as configuration, turn it on for bot tokens.
- Otherwise start with short TTLs and scoped resources, and revisit.

**Resource scoping at install (decision for you)**
- A bot with "read the knowledge base" is org-wide data access.
- The skill says to promote fine-grained, GitHub-style per-resource permissions when admins demand approval policies or scopes reach org-wide data. Both are now true for the app tier.
- I recommend a hybrid: keep `resource:action` scopes, and add an admin-chosen allow-list of spaces or collections at install, like GitHub's per-repository restriction.
- This avoids a full permission-taxonomy rewrite, which the skill calls a quarters-long project.
- Keep the coarse tier alive for delegated scopes while this matures.

**Custom internal bots**
- Let a workspace create a private app that can be installed only in that workspace.
- It skips marketplace verification, but still goes through the admin policy and the allow-listed resource scoping.

## Change 4: Raise the verification bar for app-type scopes

- **Default:** manual developer-portal registration with a review step. Open dynamic registration stays deleted. Use gated DCR only if you serve an MCP or AI-agent ecosystem.
- **Publisher identity verification** is required for every listed app. It is cheap and proves identity, not quality.
- **Bright line:** the skill requires third-party security assessment once a scope reaches other users' data or PII. App-type content-read scopes cross it. Delegated scopes bounded by the installing user's own access mostly don't.
  - Consequence: marketplace bots with org-wide read or write need an independent assessment, with annual recurrence.
  - The developer pays the assessor, not you, and it takes months. Flag this to partners early.
  - It's a slower path for bot partners, but it's the answer to what enterprise IT will ask.
- **Unverified testing lane:** bounded to named test users or a developer's own test workspace, with a visible warning and a real enforced user cap. Test-token lifetime should be short (Google uses 7 days).
- **Runtime check:** reject any scope request that isn't a subset of what was declared and approved at registration.
- **Ongoing review:** `samber/developer-platform-skills@app-marketplace-review` owns that process. Step 3 here only designs the gate.

## Related skills (outside this one's scope)

- `api-auth-key-management` decides whether a first-party or internal bot should be an API key instead of OAuth. Third-party distributed bots belong on OAuth.
- `mcp-server-offering` applies if agents or MCP hosts will consume this authorization server.

## Build order

Sequenced against your enterprise deals:

1. **Scope token-type binding.** Mark all existing scopes `delegated`. Do this before anything else, because it can't be retrofitted cheaply.
2. **Workspace policy engine, approval queue, revoke and list tools, audit events.** This is the answer to the IT question the three deals asked, and it ships without bots.
3. **Bots:** app-type scopes, admin-only consent, installation-scoped `client_credentials`, resource allow-list, owner reassignment.
4. **Assessment tier** for app-type content scopes, then DPoP or mTLS for bot tokens if justified.

## Gates (test before calling this done)

- A non-admin cannot obtain an app-type token.
- Blocking an app or changing workspace policy denies the next refresh and the next issuance.
- A delegated token for a permission-reduced user cannot read what that user can't.
- A bot sees only its allow-listed spaces.
- A bot survives its installer's offboarding.
- A bot stops working immediately after uninstall.
- Admin partial approval produces the correct granted set, and the diff is exercised in an integration test.
- A scope-addition re-approval screen shows only the delta.
- The replay test still revokes the token family, with no false logouts under concurrent refresh.

**Metrics to baseline from launch.** The skill says no industry thresholds exist:
- Approval-request turnaround time.
- Denial rate.
- Share of approved apps requesting scopes their traffic never uses.
- Number of bots with org-wide read.
- Reuse-detection trip rate.

Do not cite any consent drop-off percentage as fact. No rigorous study exists.

## Open questions

Answers that would change the above:

1. Is this a retrofit, and how many live apps and tokens do you have today? A large number makes the scope binding migration the critical path.
2. Does the knowledge base have restricted spaces or per-page permissions? This decides whether the allow-list is optional or mandatory.
3. Are your three enterprise deals gated on a date? If so, step 2 of the build order alone may unblock them.
4. Are you building on your own authorization server or on an identity product? This decides whether DPoP is cheap.
5. Will AI agents or MCP hosts be clients, and does an agent act as a user, as a bot, or both?

I did not write `developer-platform-context.md`. I can save these decisions there if you want.