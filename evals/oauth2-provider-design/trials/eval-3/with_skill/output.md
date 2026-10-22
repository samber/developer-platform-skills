# Kestrel HR: DPoP before launch, or something else?

**No to DPoP on everything before launch. Ship an OAuth 2.1 profile with PKCE, refresh-token rotation with reuse detection, and tiered app verification. Design DPoP in as an opt-in later.**

I followed `oauth2-provider-design` and its four references. The skill says to ask clarifying questions first. I couldn't, so the assumptions I used are listed at the end. Where I go beyond the skill, I mark it as my judgment.

## Why not DPoP now

1. **Your partners can't use it yet.**
   - They are small ATS and payroll vendors on off-the-shelf OAuth client libraries.
   - The skill ranks DPoP last for client-library compatibility. 0 of 18 mainstream issuers with a working discovery document advertise DPoP (MojoAuth issuer survey).
   - "On everything" means a partner whose library can't produce DPoP proofs can't integrate. Your directory launches nearly empty.
2. **It costs the most to build on your stack.**
   - The skill ranks DPoP highest on effort. You wrote your own Node authorization server, so you'd write and test proof validation, nonce handling, `cnf` binding and replay protection yourself.
   - Keycloak 26.4 ships DPoP as configuration, which flips that cost. You don't run it.
   - Eight weeks is not enough for that work plus the baseline below.
3. **Your data doesn't meet the skill's trigger.**
   - The skill promotes DPoP for financial or health data, or for long-lived AI-agent tokens.
   - You store employee directory and time-off data only. You have no payments, no health records and no agent ecosystem. The runtime cost (~2-10 ms per request) isn't the issue. Missing library support is.
4. **The baseline is the larger risk reduction.**
   - Salesforce's May 2026 mandate is PKCE plus refresh rotation on all connected apps, with de-listing as the penalty. That is what a forced retrofit looks like, and it is the posture to match.
   - Mandatory DPoP is not part of that mandate.
5. **Most of your partners are confidential clients.**
   - Server-side ATS and payroll vendors authenticate to the token endpoint. RFC 9449 itself carves them out: client authentication already constrains redemption of their refresh tokens.
   - The sender-constraining DPoP adds matters most for public clients. OAuth 2.1 requires "sender-constrained or rotated" only for those.

**What to tell the CISO (my framing, not the skill's):**
- He is right that DPoP is the strongest posture. The skill ranks it first on security.
- Mandating it before launch trades away partner adoption for protection against a threat he can already contain with rotation and verification.
- Offer a dated trigger instead of "never". Promote DPoP if you add a scope for sensitive HR data, if a partner population emerges that can support it, or if a token-theft incident shows rotation isn't enough.

## What to ship in 8 weeks

### 1. Protocol core (weeks 1-3)

- **Grants:**
  - `authorization_code` with PKCE S256, required for every client, confidential ones included.
  - `client_credentials` for app-identity access.
  - `refresh_token`.
  - `device_authorization` (RFC 8628) only if a CLI partner exists.
  - No `implicit` and no password grant.
- **Redirect URIs:** exact string match. The only exception is the port on native `localhost` redirects.
- **Token transport:** no bearer tokens in query strings.
- **Authorization codes:** single-use, 10 minutes at most.
- **Access tokens:** ~1 hour. If you issue JWTs, the short TTL is your revocation story. Opaque tokens revoke instantly.
- **Refresh tokens:**
  - Rotation with token-family reuse detection. Replaying a consumed token revokes the whole family.
  - Reuse grace window of 10-30 seconds from day one, so retries and concurrent refreshes don't log users out.
  - Store tokens hashed (SHA-256). Keep the predecessor's hash with a validity timestamp so the grace window still works.
  - Cap SPA refresh tokens at 24 hours, if you have SPA partners.
- **Endpoints:**
  - `/authorize`, `/token`, `/revoke` (RFC 7009), `/introspect` (RFC 7662).
  - `/.well-known/oauth-authorization-server` (RFC 8414), published at launch. Advertising capabilities later, DPoP included, happens there.
- **Compliance gates:** copy Django OAuth Toolkit's shape of one boolean per RFC 9700 requirement. A partial rollout or audit can then say exactly what is enforced.
- **Rotation friction (my note):** some partner libraries mishandle a new refresh token returned on refresh. Document it in the partner guide and test against 2-3 popular libraries before launch. If a strong partner can't comply, the skill permits non-rotating refresh tokens for confidential clients only.

### 2. Scopes and consent (weeks 3-5)

- **Naming and defaults:** `resource:action` scopes with a read/write split and read-only defaults, using the nouns your API uses. Examples: `employees:read`, `timeoff:read`, `timeoff:write`.
- **No catch-all scope.** Do not create `full_access`.
- **Additive-only, forever.** Never repurpose a scope's meaning.
- **Token-type binding:**
  - Decide per scope from the first scope shipped whether it applies to a user-delegated token or an app-identity token.
  - Slack's late change forced reauthorization from every user.
- **Two consent surfaces.** Your buyer is the HR admin.
  - Build an admin approval queue and an org-wide grant review.
  - Directory-wide and app-identity scopes need admin consent.
  - Over-scoping fails at the admin gate, whatever the end user clicks.
- **Consent screen:**
  - One plain-language sentence per scope. No grouped buckets, no raw scope strings.
  - Support partial grants and diff granted against requested scopes on the server.
  - Incremental authorization shows only the net-new scope.
  - Do not cite consent drop-off percentages. No rigorous study exists.
- **Time-off needs care (my judgment, not the skill's).** Leave type or reason can imply a health condition.
  - Split a coarse `timeoff:read` (dates and balances) from anything revealing leave type or reason.
  - Gate the sensitive part more tightly, or don't expose it at launch.

### 3. Registration and verification (weeks 4-7)

- **Registration:** manual developer-portal registration with a review step. No dynamic client registration. An open endpoint lets anyone impersonate a legitimate app's name and logo.
- **Verification tiers** (scale review depth to data sensitivity):
  - **Every listed app:** publisher identity verification covering domain and a verified company.
  - **Every listed app:** self-attestation, shown as a separate signal from identity. Do not use one undifferentiated badge.
  - **Apps reaching other employees' PII in bulk:** these scopes cross the skill's bright line, because directory data is other people's PII.
- **The honest conflict:**
  - Mandatory third-party assessment takes months and the partner pays the assessor. That doesn't fit eight weeks for small vendors.
  - A pragmatic option (my judgment): launch with identity plus attestation plus your own manual review, limited to a vetted launch cohort.
  - Require an independent assessment on a dated schedule, within 6-12 months for directory-wide PII scopes, then annually.
  - The bridge is a temporary exception. Decide it with the CISO and legal.
- **Unverified testing lane:**
  - Named test users, a visible warning screen, a hard lifetime user cap, and 7-day test-token expiry.
  - Enforce the cap in code. A documented cap is not a cap.
- **Runtime enforcement:** reject any scope request that isn't a subset of what was declared and approved at registration.
- **Related skill:** `app-marketplace-review` owns the standing review operation after launch.

### 4. DPoP as an opt-in (weeks 7-8 groundwork, build later)

Keep these cheap now so DPoP becomes a switch rather than a rewrite:
- Keep the discovery document extensible.
- Add a nullable key-binding column to the token and refresh-family tables.
- Add a `token_type` field to token responses.
- Build DPoP validation as a separate module that can be switched on per client.
- Later, offer opt-in DPoP to partners who can support it. Promote it to default only when partner library support exists.

## Gates before launch

- **Protocol:**
  - The discovery document shows no implicit or password grant.
  - A request without PKCE is rejected for every client.
  - Exact redirect matching is verified by a test, not asserted.
- **Tokens:**
  - In staging, a replayed refresh token revokes the family.
  - A concurrent-refresh test passes without a false-positive logout.
- **Consent:**
  - Every scope has plain-language copy.
  - A partial-grant test exercises the granted-versus-requested diff.
- **Verification:**
  - Every scope is classified into a tier with a named review requirement.
  - Runtime subset enforcement is live.
  - The unverified-lane cap is enforced.
- **Baseline from launch (no industry thresholds exist):**
  - Median app-review turnaround.
  - Share of apps requesting scopes their traffic never uses.
  - Reuse-detection trip rate, which signals either attacks or a grace window that is too tight.

## Assumptions to confirm

I assumed:
1. Greenfield, no existing apps or tokens.
2. Mostly server-side confidential partners.
3. A mix of user-delegated and app-identity access.
4. Directory scopes reach other employees' PII.
5. Admins approve installs.
6. A custom Node authorization server with an eight-week ceiling.

Questions 1, 4 and 6 move the plan most. If any of them is wrong, the plan changes.