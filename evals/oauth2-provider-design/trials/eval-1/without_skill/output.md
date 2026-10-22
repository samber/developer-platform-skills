# Connect with Tessaract: OAuth grants, redirect rules, and security-review wording

## 1. What to name in the doc (for legal)

**Don't cite "OAuth 2.1" with an RFC number.** As of my knowledge (cutoff June 2026), OAuth 2.1 (`draft-ietf-oauth-v2-1`) is an IETF Internet-Draft, not an RFC. I can't check its status today, so confirm at datatracker.ietf.org before signing. If it has since been published, use the number from there. Don't take one from me or from a blog post.

Name the published RFCs instead, which are stable and citable:

| Role | Spec |
|---|---|
| Core framework | RFC 6749, OAuth 2.0 Authorization Framework |
| Bearer token usage | RFC 6750 |
| Security hardening | RFC 9700 (BCP 240), OAuth 2.0 Security Best Current Practice |
| PKCE | RFC 7636 |
| Headless CLI | RFC 8628, Device Authorization Grant |
| Issuer mix-up defence | RFC 9207, `iss` response parameter |
| Discovery | RFC 8414, Authorization Server Metadata |
| Revocation | RFC 7009 |

Optional, if adopted: RFC 9449 (DPoP), RFC 9126 (PAR), RFC 8707 (resource indicators), RFC 9068 (JWT access tokens), RFC 7591 (dynamic client registration).

**Suggested wording:**

> Connect with Tessaract implements the OAuth 2.0 Authorization Framework (RFC 6749) and Bearer Token Usage (RFC 6750). It conforms to the OAuth 2.0 Security Best Current Practice (RFC 9700, BCP 240). Authorization-code clients must use PKCE (RFC 7636). The `tsq` CLI uses the Device Authorization Grant (RFC 8628). The authorization response carries the `iss` parameter (RFC 9207), and server metadata is published per RFC 8414. The implicit and resource-owner-password grants are not supported. Redirect URIs are matched by exact string comparison. Access tokens are accepted only in the `Authorization` header. This profile is consistent with the direction of the OAuth 2.1 Internet-Draft (draft-ietf-oauth-v2-1), which is a work in progress and not an RFC; we do not claim conformance to it as a standard.

The wildcard redirect request below would make the RFC 9700 line false. Resolve that before the doc is signed.

## 2. Grant list

| Client | Grant | Notes |
|---|---|---|
| Third-party web apps with a backend | Authorization code + PKCE (S256) | Confidential client: secret or private-key JWT, plus PKCE. |
| Third-party SPAs and mobile (public clients) | Authorization code + PKCE (S256) | No client secret. Refresh tokens are rotated with reuse detection, or sender-constrained (DPoP). |
| `tsq` on a developer's machine or interactive session | Device authorization (RFC 8628) | User approves on another device. Short `user_code`, rate-limited polling, 5–10 minute expiry. |
| `tsq` on unattended build servers | Client credentials, with a per-customer service-account client | The device grant needs a human at least once, so it is not a fit for CI jobs that run unattended. Scope these clients narrowly and make them revocable and rotatable. |
| Refresh token | Yes, for the grants above | Rotate on use. Revoke the whole family on reuse. |

**Not supported:** implicit grant and resource-owner password credentials. RFC 9700 forbids both.

**Rules for all grants:**
- PKCE is mandatory for every authorization-code request. Accept only `S256`, and reject `plain`.
- Authorization codes are single-use and live 60 seconds or less. Bind each code to the client, the `redirect_uri`, and the `code_challenge`.
- Access tokens are short-lived (5–15 minutes) and scoped to read-only dashboards.
- Return `iss` in every authorization response (RFC 9207).
- Per-client allowed grants and scopes are registered server-side. Reject any request outside them.

## 3. Redirect rules

1. **Exact string match** against pre-registered URIs (RFC 9700 §4.1.3). No wildcards, no prefix matching, no pattern matching.
2. HTTPS only. The only exceptions are native-app loopback (`http://127.0.0.1:<port>` or `[::1]`, where any port is allowed per RFC 8252) and private-use schemes (reverse-domain) for native apps.
3. Reject fragments, userinfo (`user@host`), and relative URIs.
4. If `client_id` or `redirect_uri` is invalid, show an error page. **Never redirect** to an unverified URI.
5. Make `state` or PKCE-based CSRF protection mandatory.
6. Never put tokens in the redirect URI. Only the code goes there.
7. `tsq` uses the device grant, so it needs no redirect URI at all.

## 4. Frontend asks

### Wildcard `https://*.preview.acme-partner.dev`: **No**

- If an attacker takes over any dangling subdomain (a common failure with preview hosts), they receive valid authorization codes for real customers' dashboards.
- Any XSS or open redirect on any preview deployment leaks codes the same way.
- It contradicts RFC 9700 §4.1.3, which the doc will claim conformance to.

**Alternatives, in order of preference:**
1. **Stable callback with relay.** The partner registers one URI, such as `https://auth.acme-partner.dev/callback`. That page forwards the user to the right preview afterwards. The partner owns the relay and validates its own `state`.
2. **Per-preview registration through an API.** Use dynamic client registration (RFC 7591) or a management API. CI registers each preview URL exactly when it deploys and deletes it on teardown.
3. **Separate test client.** Give previews a non-production client that can only see sandbox or demo tenant data. A wildcard there is a bounded risk, but still not RFC 9700-conformant, so exclude it from the production claim.

### Access token in the query string: **No**

- RFC 6750 §2.3 allows it only with warnings. RFC 9700 says not to send access tokens in URI query parameters. The OAuth 2.1 draft removes it.
- URLs leak through `Referer` headers, browser history, proxy and CDN logs, and our own access logs. We are a log-analytics vendor, so we would ingest customer tokens ourselves.
- **Server rule:** reject `access_token` as a query or form parameter with `400`, and strip it from logs.
- **Their fix:** adding `Authorization: Bearer <token>` in the fetch wrapper is a one-line change.
- **Better for SPAs:** use a backend-for-frontend (BFF) that holds the tokens and gives the browser a same-site session cookie. The IETF browser-based-apps BCP recommends this. I am not certain of its RFC status, so check before citing it.

## 5. Open items to confirm before signing

1. Check the OAuth 2.1 draft status on datatracker today.
2. Decide whether the unattended-CI path (client credentials) is in scope for v1. If it isn't, say in the doc that `tsq` is interactive-only.
3. Decide whether to adopt DPoP or PAR. If you adopt them, add the RFC numbers (9449, 9126) to the doc.