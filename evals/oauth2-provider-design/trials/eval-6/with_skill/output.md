**No. Don't ship open `/register`.** Ship gated DCR (RFC 7591) instead. It keeps agent discovery and puts a human gate in front of data access.

## Why open DCR fails

1. **Metadata validation can't fix impersonation.** `client_name` and `logo_uri` are self-asserted. Any agent can register as "Claude" or "Verity Ops Official" with a real-looking logo. Your consent screen then shows a stranger's claim as if it were fact. An open endpoint is a phishing kit.
2. **Rate limiting stops volume, not one bad client.** An attacker needs a single registration, and the hard limit doesn't touch it.
3. **The data raises the stakes.** Incident data probably reaches other users' and org-wide data. That is the highest verification tier in the skill.
4. **The evidence is bad.**
   - A May 2026 preprint probed 119 OAuth-enabled remote MCP servers and found DCR flaws in 96.6%.
   - The skill reports the MCP spec moved DCR from SHOULD to MAY to deprecated across 2025-2026. Re-check the current spec revision before you cite it to your team.
   - No major B2B SaaS platform offers ungated public DCR (GitHub, Slack, Stripe, Salesforce).
5. **Your premise is half right.** MCP agents are the one population that can't pre-register, so DCR is justified for them. That justifies *gated* DCR, not *open* DCR.

## Design to ship

**Registration**
1. Require an **initial access token** at `/register`.
2. A human mints the token: an org admin in the Verity Ops dashboard, or your team for a named MCP host vendor.
3. Keep rate limits. Treat every metadata field as untrusted input.
4. Never fetch `logo_uri` server-side without SSRF protection. Proxy and re-encode it, or don't render it at all.
5. Redirect URIs: exact match only. Allow `https` and loopback, with the port as the only wildcard. No patterns.
6. Reject `client_name` values that collide with verified publishers.

**Protocol core (OAuth 2.1 profile)**
- `authorization_code` with PKCE S256, required for every client.
- `refresh_token` and `device_authorization`.
- No implicit or password grant.
- No bearer tokens in query strings.
- Authorization codes are single-use, max 10 minutes.
- Access tokens last about 1 hour.
- Refresh tokens rotate with family reuse detection and a 10-30 second grace window.
- Agent tokens are long-lived and widen the theft blast radius, so consider DPoP later (step 4 in the skill).

**Scopes and consent**
- Use `resource:action` scopes, read-only by default (e.g. `incidents:read`).
- Never add a catch-all `full_access` scope.
- Bind scopes to token type (user-delegated vs app identity) from day one.
- Write per-scope plain-language consent copy.
- Always diff granted scopes against requested scopes on the server.
- Support incremental consent that shows only the net-new scope.
- B2B means two gates. The end user consents, and an org admin can approve installs and review org-wide grants.

**Verification lane**
1. **Unverified (every DCR client by default).**
   - Show a visible warning screen. Display the client as "unverified" and show the redirect host.
   - Cap it at named users, using Google's model of a lifetime cap of 100 users. The cap must be enforced in code, not documented.
   - Test tokens expire after 7 days.
   - Scopes are limited to read-only on the requesting user's own data.
2. **Publisher verified.** Domain plus verified account, and no scopes beyond basic profile without it. List known MCP hosts here.
3. **Third-party assessed.** Required before any scope reaches other users' data or PII, and reassessed yearly.

Keep identity, attestation and audit as three distinct signals in the UI, not one checkmark.

**Runtime enforcement**
- Reject any scope request that isn't a subset of what was declared and approved at registration.
- Expire and clean up unused registrations.

## Gates before launch

- Test shows PKCE-less requests are rejected, with no implicit or password grant in discovery.
- Staging replay of a consumed refresh token revokes the family. A concurrent refresh doesn't log users out.
- Partial-grant integration test exercises the scope diff.
- Test shows a client with no initial access token gets 401 at `/register`.
- Test shows an unverified client past the user cap is blocked.

Track from launch: median review turnaround, share of apps requesting scopes they never use, and reuse-detection trip rate.

## What your MCP team gets

Agents still register at runtime, with no per-client ticket. The human step moves to token issuance and to the admin install gate. Known MCP hosts can go in the verified tier so users see no warning for them.

## Open questions

These change the tiers. I assumed the answers noted below.

1. Greenfield, or are there existing registered apps and grants?
2. Which clients: MCP hosts only, or SPAs, CLIs and server-side apps too?
3. Do agents act only as a signed-in user, or also with their own identity?
4. Can any scope reach other users' or bulk data? I assumed yes.
5. Who approves an install: end users only, or org admins too? I assumed both.
6. What are your substrate and deadline? Do you build the authorization server yourself, or sit on an identity product that ships rotation and DPoP?

**Next step:** answer 4 and 5 and I'll turn this into the scope list and tier table (about 20 minutes).