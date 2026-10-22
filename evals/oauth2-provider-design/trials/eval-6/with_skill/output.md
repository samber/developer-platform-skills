# Verdict: no, not as proposed

Don't ship wide-open RFC 7591 at `/register`. Keep dynamic registration, but gate it and limit what an unvetted client can do. Agents can still discover you at runtime, and your MCP team gets most of what they want.

I answered without your replies to the skill's clarifying questions, so I've listed my assumptions at the end. Please correct them.

## Why open DCR fails

1. **Validation can't fix self-asserted metadata.**
   - Anyone can register `client_name: "Verity Ops Official"` with a lookalike logo.
   - Format checks on name, logo URI, and redirect URIs prove the strings are well-formed, not that they're true.
   - The consent screen then shows an attacker's claim next to your brand. That makes the open endpoint a phishing kit, unless the metadata is cryptographically attested.
2. **Rate limiting doesn't help.** One registration is enough for a phishing campaign. Rate limits only stop table-flooding.
3. **Peer evidence:**
   - No major B2B SaaS platform (GitHub, Slack, Stripe, Salesforce) offers ungated public DCR.
   - A May 2026 preprint probed 119 OAuth-enabled remote MCP servers and found DCR flaws in 96.6% of them.
   - The MCP spec itself moved DCR from SHOULD to MAY to deprecated across 2025-2026.
   - "The spec pointed at it when we started" is therefore stale. Check the current MCP authorization spec revision before relying on it.
4. **Your data raises the stakes.** Incident data likely includes other users' data and operational detail. That is the sensitivity tier where every review program studied requires stronger vetting.
5. **"No human in the loop" is partly false.** The end user still consents, and in B2B an org admin may too. The consent screen is therefore the main place to defend. An open `/register` lets an attacker choose what that screen says.
6. **Discovery isn't registration.** Publishing RFC 8414 metadata lets agents find you at runtime. It doesn't require that anyone may register without a gate.

## Recommended design

Use **gated DCR**. The skill allows it for exactly your case, an MCP/agent ecosystem that can't pre-register everywhere.

**1. Gate `/register`**
- Require an **initial access token** (RFC 7591), or a signed **software statement** that attests the metadata.
- Issue tokens through a self-serve developer portal, with domain verification of the publisher.
- Publish `/.well-known/oauth-authorization-server` (RFC 8414) with the `registration_endpoint`.
- Keep the rate limit as defense in depth.
- Treat every metadata field as untrusted input:
  - Fetch no URLs server-side without SSRF protection.
  - Reject non-HTTPS redirect URIs, with the localhost-port exception only.
  - Match redirect URIs exactly, with no patterns.
  - Never render raw HTML or SVG.

**2. Treat dynamically registered clients as unverified, with these limits**
- **Consent screen:**
  - Show the verified redirect-URI domain and an "unverified app" warning.
  - Don't display self-asserted logos or names as trusted text.
- **Grants:**
  - Public clients only.
  - `authorization_code` with PKCE S256.
  - `refresh_token`, and `device_authorization` if you need it.
  - No `client_credentials`.
- **Scopes:**
  - Read-only scopes, in `resource:action` form.
  - Nothing that reaches other users' or bulk incident data.
  - Reject any runtime scope request that isn't a subset of what was approved at registration.
- **Testing-lane ceiling:**
  - A hard cap on users per unverified client, enforced rather than documented.
  - Short-lived refresh tokens, for example 7 days like Google's testing lane.
- **B2B:** let org admins block or approve unverified apps before an end user can consent.

**3. Add a path up for clients that need more**
- Run publisher identity verification (domain and verified account), Microsoft-style. It proves who the publisher is, not that the app is good.
- Make the unverified tier a real consent gate, not a badge.
- Give well-known MCP hosts manual, reviewed registration with a verified name and logo.
- Require a third-party security assessment before any scope that touches other users' data.
- Keep identity, attestation, and audit visually distinct as three signals.

**4. Keep the protocol baseline** (this applies whichever registration route you pick)
- PKCE for every client.
- No implicit or password grants.
- Access tokens of about 1 hour.
- Refresh-token rotation with family reuse detection and a 10-30 second grace window.
- Hold DPoP back unless these tokens guard regulated data or agent tokens live long.

## Tell your MCP team

- **Still true:** agents can discover your server and register at runtime.
- **What changes:** registration needs an initial access token or a software statement. Unvetted clients get a low-privilege tier. Full trust requires verification.
- **If they push back,** ask for the concrete client population. Named hosts such as Claude, Cursor, and your own agents can be pre-registered or verified. A truly unknown long tail only ever needs the restricted tier.
- **Unverified:** I haven't checked whether newer MCP-spec mechanisms such as client ID metadata documents suit your case better than DCR. Look at them before building.

## Gates before launch

- A conformance test shows no implicit or password grant, PKCE rejected if absent, and exact redirect matching.
- `/register` without a valid token returns 401, and the test proves it.
- A malicious-metadata test suite passes. Include a lookalike name, a `javascript:` or SSRF logo URI, a wildcard redirect, and an oversized payload.
- A concurrent-refresh test passes with no false logout, and a replayed refresh token revokes its family.
- Every scope has a named tier. Runtime subset-of-approved enforcement is live. The unverified user cap is enforced.
- From launch, baseline: registrations per day, share of unverified clients, scope-denial rate, and reuse-detection trip rate.

## Assumptions to confirm

1. Greenfield server, no live clients.
2. Clients are MCP hosts and AI agents, plus possibly browser or native apps.
3. Users act on their own behalf. Do any apps need org-wide or app-identity access?
4. Incident data includes other users' or customers' data.
5. Do org admins gate installs?
6. Which substrate and deadline? A one-off unblock favors the minimal gated version above. A foundation for an app ecosystem favors adding verification tiers early.

If any of these differ, the scope limits and verification bar change.