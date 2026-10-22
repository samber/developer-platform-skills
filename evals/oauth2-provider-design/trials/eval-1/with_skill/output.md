I couldn't re-check the OAuth 2.1 status live, because the web fetch was denied. The last status I have is from the skill's reference file: `draft-ietf-oauth-v2-1-15`, March 2026, still a draft. Check the IETF datatracker before the doc is signed off. If it has since been published as an RFC, the number goes in the doc in place of the placeholder below.

## 1. What to write in the security review doc

**There is no "OAuth 2.1 RFC number" to give legal.** The consolidated OAuth 2.1 document is still an Internet-Draft, so it has no RFC number and shouldn't be cited as a published standard. Naming it as one would put a false statement in front of legal and auditors.

Name the specifications that are final:

- **RFC 6749** is the OAuth 2.0 core framework.
- **RFC 7636** is PKCE.
- **RFC 8628** is the device authorization grant, used by `tsq`.
- **RFC 6750** is bearer token usage. It governs the query-string question below.
- **RFC 9700 (BCP 240)** is the OAuth Security Best Current Practice, published January 2025. It is final and ratified, and it is the strongest normative document you can cite.
- **RFC 7009** (revocation), **RFC 7662** (introspection) and **RFC 8414** (discovery) cover the supporting endpoints.

Suggested wording:

> Tessaract's authorization server implements OAuth 2.0 (RFC 6749) hardened to the requirements of RFC 9700 (BCP 240, January 2025). It also follows the draft OAuth 2.1 profile (draft-ietf-oauth-v2-1, an IETF Internet-Draft that has not been published as an RFC). PKCE (RFC 7636, S256) is mandatory for every client. Headless clients use the device authorization grant (RFC 8628). The implicit and resource-owner password grants are not supported. Redirect URIs are matched by exact string comparison. Access tokens are accepted only in the `Authorization` header (RFC 6750 §2.1).

The doc should cite **RFC 9700 as the conformance anchor** and treat OAuth 2.1 as "aligned with", not "conforms to". Per the skill's guidance, build each RFC 9700 requirement as its own gate, in the style of Django OAuth Toolkit's `COMPLIANT_BCP_RFC9700_*` booleans. Then the doc can point to exactly which requirements are enforced.

## 2. Grant list

| Grant | Ship? | Used by |
|---|---|---|
| `authorization_code` + PKCE (S256) | ✅ | "Connect with Tessaract" third-party apps. PKCE is required for every client, confidential ones included. |
| `device_authorization` (RFC 8628) | ✅ | `tsq` on headless build servers. |
| `refresh_token` | ✅ | Both of the above. |
| `client_credentials` | ✅ only if you want app-identity tokens | Machine-to-machine access with the app's own identity, not a user's. Needs an admin-consent tier. |
| `implicit` | ❌ | Removed in OAuth 2.1. |
| Password grant | ❌ | Removed in OAuth 2.1. |

**The `tsq` CLI:**
- The device grant is the right fit for build servers with no browser. The user approves on any other device.
- Treat `tsq` as a public client, so rotation with reuse detection applies. Build servers often share a token cache, so set the grace window to around 10-30 seconds to avoid false-positive logouts.
- A pure CI pipeline with no human present is really a machine identity. Route it to `client_credentials` or to your API-key product, not to a device flow nobody can approve.

**Token policy defaults:**
- Access tokens last about 1 hour.
- Authorization codes are single-use and live at most 10 minutes.
- Refresh tokens use rotation with token-family reuse detection, and the family is tracked from the very first grant.
- DPoP is a later-stage option, not a day-one requirement.

**Scopes:** use `resource:action` naming with read-only defaults, for example `dashboards:read`. Bind each scope to a token type (user-delegated or app-identity) from day one. Don't ship a catch-all scope.

## 3. Redirect rules

1. **Exact string match only.** RFC 9700 says pattern matching has produced "several successful attacks... observed in the wild".
2. **Register each URI in full.** That includes scheme, host, port and path.
3. **HTTPS is required**, with one exception: native-app loopback redirects such as `http://127.0.0.1` may vary the port only.
4. **No wildcards.** This is the answer to the frontend team's request.
5. **Reject at registration time**, not only at runtime. Also reject at runtime any `redirect_uri` that isn't byte-identical to a registered one.

**On `https://*.preview.acme-partner.dev`: decline it.**

- A wildcard lets any subdomain receive authorization codes. A dangling DNS record or a subdomain takeover on that domain then turns into account takeover for every Tessaract customer who uses that partner's app.
- Preview hosts are the kind of subdomains that get abandoned, which makes this a realistic attack path.

Workarounds that keep their previews working:
- **Fixed callback host.** The partner registers one stable callback such as `https://auth.acme-partner.dev/callback`. It receives the code and then redirects to the right preview deployment.
- **Per-preview registration.** Each preview URL is registered through the developer portal. Automate this with a portal API if volume requires it, since manual registration with review is the default posture.
- **Separate sandbox client.** Give the partner a dev client, with test users and a capped user count, that is allowed to register extra exact URIs. Production keeps strict matching.

Do not use dynamic client registration to get around this. Open DCR is a phishing risk, and no major B2B platform offers it ungated.

## 4. Access token in the query string: no

- Bearer tokens must not be put in URI query strings. That is the rule in RFC 9700 and in the OAuth 2.1 draft.
- Query strings leak into server and proxy logs, browser history and `Referer` headers. For a log-analytics product, those leaks are especially embarrassing.
- Enforce it as a gate. The resource server should reject `?access_token=` outright. Don't accept it and merely warn.

The frontend problem is a fetch-wrapper annoyance, so fix it there:
- Set the header once in the wrapper with `headers: { Authorization: \`Bearer ${token}\` }`.
- Better, don't hold the token in the browser at all. Put a small backend-for-frontend in front of the SPA, keep tokens server-side, and have the SPA use a session cookie.
- Cap refresh-token lifetime hard for browser clients. Microsoft's 24-hour SPA limit is a reasonable reference.

## 5. Decisions to confirm before you build

- Do third-party apps act only for a signed-in user, or also with their own identity? This decides whether `client_credentials` ships.
- Can any scope reach other users' data or bulk data? If yes, apps need a third-party security assessment before they can request it.
- Does an org admin need to approve installs? In B2B this is almost certainly yes, so design the admin approval surface now rather than when the first enterprise customer asks.
- Will you build the authorization server yourselves, or on an identity product that already ships rotation and DPoP as configuration? That changes the effort ranking above.