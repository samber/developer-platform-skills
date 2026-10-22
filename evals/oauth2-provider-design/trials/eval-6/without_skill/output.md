**Verdict: not as stated.** Keep `/register` for compatibility, but don't treat registration as trust. Registration can stay open. Privilege cannot.

First next action: read the current MCP authorization spec revision. I couldn't check it in this session. As I recall, the 2025-11-25 revision made Client ID Metadata Documents (CIMD) the preferred path and demoted DCR to a compatibility fallback. Verify that before the team cites "the spec pointed at DCR".

## Two premises to fix

1. **"Only way agents discover us at runtime" is wrong.**
   - Discovery uses RFC 9728 (protected resource metadata) and RFC 8414 (AS metadata). Registration is a separate step after discovery.
   - CIMD also gives runtime onboarding with no pre-registration. The `client_id` is an HTTPS URL that hosts the client's metadata.
2. **"No human in the loop" is fine for registration and wrong for authorization.**
   - Your data is incident data: security events and customer impact. A human must still see a consent screen and approve each grant.
   - Open DCR makes that screen the only control. Attackers fully control what it displays.

## Why open DCR hurts here

1. **Consent phishing.**
   - An attacker registers "Verity Ops Official" with a convincing logo and a redirect to their own host.
   - Your employee clicks Allow. The attacker holds a token for incident data.
   - Metadata validation checks format, not truth. It cannot stop this.
2. **`logo_uri`, `client_uri`, `tos_uri`, `policy_uri` are attack surface.**
   - Fetching them server-side is SSRF.
   - Rendering them on the consent page leaks the user's IP to the attacker and allows hostile image content.
3. **Redirect URIs.**
   - Wildcards or loose matching give open redirects and code theft.
   - Custom schemes and `javascript:`/`data:` need rejecting.
4. **Hard rate limits fail in both directions.**
   - IP limits don't stop botnets.
   - They do lock out legitimate agents behind shared cloud egress IPs.
   - Agents that re-register on every start also bloat your client table.
5. **Registered clients accumulate with no owner.** You get no inventory, no cleanup, and a weak audit trail for SOC 2-style questions.

## Recommended design: trust tiers

**Tier 0: DCR at `/register`, anonymous.** Mandatory limits:
- Public clients only: `token_endpoint_auth_method: none`.
- Grants limited to `authorization_code` and `refresh_token`. Never `client_credentials`.
- PKCE S256 required.
- Read-only minimum scopes.
- Short refresh-token lifetime.
- Garbage-collect clients that never completed a grant within about 24h.
- Consent screen says "Unverified app" and shows the redirect host in plain text.
- Per-consent approval. Never remember approval by `client_name`.

**Tier 1: CIMD.**
- Fetch the metadata document through an SSRF-hardened fetcher: block private ranges, cap size and redirects, set timeouts, cache.
- The domain is the identity, and the consent screen shows it as TLS-verified.
- Redirect URIs must appear in the document.
- Scopes can be somewhat broader.

**Tier 2: allowlisted or pre-registered clients.**
- Known vendors get a verified badge and the broadest scopes.
- Org admins can allow or block clients per tenant, which is essential for enterprise.
- Headless service-to-service use goes here, with provisioned credentials. It does not go through open DCR.

## Metadata validation rules

- **Allowlist fields.** Ignore everything else.
- **Redirect URIs:**
  - Exact match only.
  - HTTPS, or loopback per RFC 8252.
  - No wildcards.
  - No fragments.
- **`client_name`:**
  - Cap the length.
  - Strip control and bidi characters.
  - Reject Unicode lookalikes of your brand and of known vendors.
- **Logos:**
  - Never hotlink them.
  - For Tier 0, skip them entirely.
  - Otherwise fetch once, check content type, re-encode, and serve from your own domain.
- **Management endpoint (RFC 7592):** offer none, or require the `registration_access_token`.

## Rate limiting

- Limit per IP, per IPv6 /64, and globally.
- Starting point: 10 registrations per hour per IP and a global ceiling. These numbers are guesses. Tune them on real traffic.
- Deduplicate: return the existing client when the metadata is identical. This reduces re-registration churn.

## Operational controls to ship with it

- Kill switch per `client_id` and per redirect host.
- Audit log of `client_id`, user, scopes, and each query.
- Short access-token lifetimes and revocation.
- Alert on a sudden burst of new clients.

## Decisions for you

1. Does consent show the user's tenant, and can an admin restrict which clients users may approve? If not, that is the first gap to close.
2. Will any agents run headless with no user? Those need Tier 2 credentials, not DCR.
3. Is CIMD support on your roadmap? Tier 0 DCR plus CIMD covers most MCP clients.

**Next:** answer decision 1. Everything else in the design follows from it.