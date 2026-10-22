**Verdict: no, not as stated.** Keep DCR, but don't make open `/register` plus metadata validation plus rate limiting your whole trust model.

## Two premises to fix

1. **Open registration isn't how agents discover you.** Discovery runs through RFC 9728 (protected resource metadata, pointed to by the `WWW-Authenticate` header) and RFC 8414 (authorization server metadata). Registration comes after discovery and is a separate choice.
2. **The MCP spec doesn't require open DCR.** I haven't re-checked the current revision, so verify this. The 2025-06-18 revision said servers SHOULD support DCR. The 2025-11-25 revision, as I recall it, added Client ID Metadata Documents (CIMD) as the preferred path and kept DCR as a fallback. Check which revision your MCP team read.

## What actually breaks

Registering without a human is fine. The danger is what a registered client can then reach, because incident data is sensitive.

1. **Consent phishing is the main risk.** An attacker self-registers "Verity Ops Security Scanner" with their own `redirect_uri` and sends a victim the authorize link. The victim approves and the attacker gets a token for incident data. Validating metadata and rate limiting don't stop this, because the attacker's metadata is valid.
2. **`client_name` and `logo_uri` are attacker-controlled text and images on your consent screen.** They enable impersonation, so you can't treat them as identity.
3. **`logo_uri`, `client_uri`, `tos_uri` and `policy_uri` are SSRF bait if you fetch them.** They are also a tracking and content risk if the browser loads them from the consent page.
4. **Rate limiting `/register` by IP is weak.** Botnets get around it, while legitimate agents behind shared cloud egress get throttled. Unbounded stored clients are a slow resource-exhaustion risk.
5. **If any of these agents run machine-to-machine (`client_credentials`), no human ever consents.** Self-registration there means self-granted access. That case needs admin-issued credentials.

## Design I'd ship

1. **Support CIMD first.** The `client_id` is an HTTPS URL, and you fetch its metadata at authorization time.
   - The domain becomes the identity you show on the consent screen.
   - You store no registration state.
   - Harden the fetch: block private and link-local ranges, cap size, set a short timeout, don't follow redirects blindly.
2. **Keep DCR as an "unverified" tier.**
   - Allow public clients only (`token_endpoint_auth_method: none`) and require PKCE S256.
   - Match `redirect_uri` exactly with no wildcards or fragments. Allow `https`, or `http` on loopback only. Reject `javascript:` and `data:`. Restrict custom schemes.
   - Never fetch or render `logo_uri` for unverified clients. Show the redirect host prominently instead of the client-supplied name.
   - Show an "unverified application" warning on the consent screen.
   - Cap scopes at a read-only subset, with short-lived access tokens and rotating refresh tokens.
3. **Add a verified tier.** Pre-registered vendors, or a software statement or initial access token (both are in RFC 7591). Only this tier gets full scopes and a logo.
4. **Add tenant-admin policy.** Admins can allowlist, deny or require approval for unverified clients. This is the control enterprise buyers will ask for.
5. **Add hygiene.**
   - Garbage-collect clients that have never completed an authorization within about 7 days (the number is a placeholder to tune).
   - Apply a global cap on unauthorized clients plus a per-IP limit.
   - Keep audit logs of registrations and grants, and make revocation easy for users and admins.

## One question that changes the design

Do these agents act on behalf of a logged-in human user (authorization code flow), or run unattended (client credentials)? The design above assumes the first. For the second, drop self-registration and use admin-issued credentials.

**Next:** answer that question. Then I can draft the scope split between the unverified and verified tiers, which is the first thing to settle.