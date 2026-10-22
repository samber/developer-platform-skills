# Kestrel HR: DPoP on everything, or something else?

**Verdict: no. Don't make DPoP mandatory for the partner directory launch.** Ship an OAuth 2.1 profile with refresh rotation and reuse detection, per-scope consent, an admin approval gate, and a tiered verification program. Keep DPoP as an opt-in later step with explicit promotion triggers.

The skill asks clarifying questions before designing, but you asked for a single deliverable. So I've stated my assumptions below. Correct me if one is wrong, since several change the answer.

## Assumptions

- **Greenfield for third parties.** Partners don't integrate yet, so nothing needs a retrofit.
- **Mostly confidential clients.** ATS and payroll vendors are server-side apps, not SPAs or native apps.
- **Two ways in.** Some apps act for a signed-in user. Most payroll and ATS syncs will want org-wide, app-identity access.
- **Org admins approve installs.** An employee should not be able to approve sharing company-wide HR data.
- **Authorization server in Node.** You wrote it yourself and are not moving to an identity product in 8 weeks.

## Why not DPoP-everywhere

1. **Your data doesn't meet the skill's promotion trigger.** It promotes DPoP when tokens guard financial or health data, or when long-lived AI-agent tokens widen the theft blast radius. You hold employee directory and time-off data, with no payments and no health records. Neither trigger is met today.
2. **Your clients can't do it.** The skill's ranking puts DPoP last on client-library compatibility.
   - The skill cites an issuer survey where 0 of 18 mainstream issuers with a working discovery document advertised DPoP.
   - Small ATS and payroll vendors on off-the-shelf OAuth libraries would have to generate keys, sign a proof on every request and handle nonces.
   - Mandatory DPoP means a partner who can't do it can't integrate. That hits the exact partners you're recruiting.
   - Making it optional leaves a bearer fallback, so you get no guarantee.
3. **It's the highest-effort option, and you have 8 weeks.** DPoP ranks last on effort.
   - You'd write proof validation (`htm`, `htu`, `jti` replay cache, nonce handling, key-bound refresh tokens) in a self-built Node server.
   - Every resource-server endpoint, not just the authorization server, would also have to validate proofs.
   - That work would compete with the protocol core, scopes, consent and verification program, all of which have to ship by launch.
4. **It's the wrong first dollar of security spend.** DPoP is real protection against stolen tokens being replayed. But the Salesloft Drift campaign (700+ organizations, Aug 2025) and Salesforce's forced retrofit show where the failures were:
   - missing rotation and PKCE controls
   - over-broad connected apps
   - weak vetting of what was listed

   Those are the first things to fix.
5. **Confidential clients are already partly sender-constrained.** RFC 9449 carves them out because client authentication constrains redemption. OAuth 2.1 only demands "sender-constrained or rotated" for public clients. Most of your partners fall under that carve-out.

## What the CISO is right about

Token theft is not "solved". The Drift campaign was stolen OAuth tokens. A fair reply to "ahead of the curve" is that the curve is currently rotation, PKCE everywhere and app vetting. Salesforce was forced into those on a deadline, with de-listing as the penalty. Building them in on day one is ahead of the curve. DPoP is differentiation: the survey found no mainstream issuer advertising it.

## What to ship instead

### 1. Protocol core (weeks 1–3)

- **Grants:**
  - `authorization_code` with PKCE S256, required for every client, confidential ones included.
  - `client_credentials` and `refresh_token`.
  - Skip `device_authorization` unless a partner needs a CLI.
  - No implicit or password grant.
- **Redirect URIs:** exact string match, with no patterns. The only exception is the port on native `localhost` redirects.
- **Bearer tokens:** accepted only in the `Authorization` header, never in query strings.
- **Authorization codes:** single-use, 10 minutes at most.
- **Access tokens:** about 1 hour. If you issue JWTs, the short lifetime is your revocation story. Opaque tokens can be revoked instantly through the database.
- **Refresh tokens:** rotation with token-family reuse detection.
  - Each refresh token belongs to a family tied to the original grant. Presenting a consumed token again revokes the whole family.
  - Add a 10–30 second reuse grace window from day one, or retries and multi-tab clients will read as attacks.
  - Hash tokens at rest, but keep the predecessor's hash with a validity timestamp so the grace window can recognize it.
- **Discovery and endpoints:** publish the RFC 8414 discovery document now, with `/revoke` and `/introspect`. It's where DPoP gets advertised later.
- **Compliance gates:** model each requirement as its own toggle (PKCE, redirect matching, rotation), not one "2.1 mode" flag. That lets you audit exactly what's enforced.

Because this is self-written, treat a conformance test pass as a launch gate. See Gates below.

### 2. Scopes and consent (weeks 3–5)

- **Naming:** `resource:action` with a read/write split and read-only defaults. Use the same nouns as your API.
- **No catch-all scope.** Don't ship a `full_access` scope.
- **Token-type binding:** decide now, per scope, whether it belongs to a user-delegated token or an app-identity token. Deferring this is the mistake that forced Slack into reauthorizing every user.
- **Time-off needs care.** Leave type (sick or medical leave) can reveal health information, even though you store no health records. Put it behind its own scope instead of bundling it with basic time-off.
- **Split directory scopes by sensitivity.** Keep basic fields (name, work email, title) apart from personal contact details and birthdate.
- **Rules for scopes:**
  - Scopes are additive-only. Never change what an existing scope means.
  - Write one plain-language consent sentence per scope, never grouped.
  - Diff granted scopes against requested scopes server-side every time.
  - Make the re-consent screen show only the new scope.
- **Admin gate:** build the admin approval queue and the org-wide grant review now. Don't wait for the first enterprise customer to ask. Over-scoping fails at that gate, and the end user can't approve past it.

### 3. Registration and verification (weeks 5–8)

- **Registration:** manual portal registration with a review step. Don't build open dynamic client registration.
- **Verification tiers:**
  1. **Every listed app:** publisher identity verification (domain plus a verified business). It proves continuity, not quality.
  2. **Any app with employee-data scopes:** self-attestation on top of identity verification.
  3. **Third-party security assessment:** this is the tier that needs your call. The skill's bright line is any scope that reaches other users' data or PII. A directory scope reads employees other than the consenting person, in bulk, so by that rule it qualifies. Assessment takes months and the partner pays for it, so it cannot gate an 8-week launch.
- **Recommendation for tier 3:**
  - Launch with tiers 1–2.
  - Gate the high-sensitivity scopes (personal contact data, leave type, bulk export) behind assessment as a second wave.
  - Show identity, attestation and audit as three separate badges, not one checkmark.
- **Unverified test lane:** bounded named test users, a visible warning screen and a hard user cap, enforced in code. Add short test-token expiry too.
- **Runtime enforcement:** reject any scope request that isn't a subset of what was declared and approved at registration.

### 4. DPoP and PAR: later, with explicit triggers

Publish the promotion criteria so the CISO has a roadmap, not a rejection:

- **A regulated scope appears.** Payroll or bank data, or real health data.
- **Long-lived agent tokens.** AI agents or MCP hosts begin holding long-lived tokens.
- **Partners can support it.** Your top partners' libraries support DPoP, or a partner asks for it.

Start it as opt-in per client, and let high-sensitivity scopes require it first. Skip PAR and Rich Authorization Requests. They are for transaction-level consent and add nothing to an HRIS.

## 8-week plan

| Weeks | Deliverable |
|---|---|
| 1–3 | Protocol core, rotation with reuse detection, discovery document, conformance tests |
| 3–5 | Scope taxonomy, per-scope consent copy, partial-grant diff, admin approval queue |
| 5–8 | Portal registration and review, verification tiers, test lane with enforced cap, runtime scope enforcement |
| Post-launch | Assessment gate for high-sensitivity scopes, DPoP opt-in design |

If the schedule slips, cut in this order: the assessment wave, then the badges, then fine-grained sensitivity splits. Never cut rotation or the PKCE and redirect rules.

## Gates (the skill's checks, adapted)

- **Protocol:** a conformance pass and discovery document show no implicit or password grant. PKCE is rejected-if-absent for every client. Redirect matching is exact.
- **Token lifecycle:** in staging, replaying a refresh token revokes the family, and a concurrent-refresh test passes without a false-positive logout.
- **Consent:** every scope has plain-language copy, and a partial-grant test exercises the server-side diff.
- **Verification:** every scope is assigned a tier, runtime subset enforcement is live, and the unverified-lane cap is enforced, not just documented.

After launch, baseline median review turnaround, the share of apps requesting scopes they never use, and the reuse-detection trip rate. No industry thresholds exist for these. A high trip rate can mean attacks or a grace window that is too tight.

## One thing to say to the CISO

"We're shipping the controls Salesforce had to retrofit under a deadline: PKCE everywhere, rotation with reuse detection, scoped consent, admin approval and vetted publishers. DPoP is next, with defined triggers. Requiring it today would block the small vendors we're trying to attract and starve the work that matters most before launch."

## Open questions that could change this

1. Will any partner use app-identity (org-wide) tokens? I assumed yes, which makes the token-type binding and admin consent essential.
2. Does the directory include personal contact data or birthdate? If so, that scope triggers the assessment gate.
3. Is there any chance of moving the authorization server onto an identity product that ships DPoP as configuration? That would lower DPoP's effort cost, but not within 8 weeks.