# Connect with Tessaract: OAuth grants, redirect rules, security-review wording

I wrote this from memory and didn't check the RFC Editor index. Before legal signs, confirm the RFC numbers and statuses below at rfc-editor.org. Also check that OAuth 2.1 is still an Internet-Draft with no RFC number. It was one as of my knowledge.

## 1. Grant list

| Grant | Who uses it | Spec | Notes |
|---|---|---|---|
| Authorization code + PKCE (S256) | Third-party apps, including the partner SPA | RFC 6749 §4.1, RFC 7636 | PKCE is required for every client, confidential or public. Reject `plain`. |
| Device authorization | `tsq` on headless build servers | RFC 8628 | The user approves on a second device. No browser is needed on the build server. |
| Refresh token | Both of the above | RFC 6749 §6, RFC 9700 §4.14 | Rotate on every use and revoke the whole chain on reuse. Bind to client and user. Give them a finite lifetime. |
| Client credentials | Optional, for app-to-app or CI service accounts | RFC 6749 §4.4 | Only if you want machine identities with no user. This is a product decision. If yes, the token acts as the app, never as a customer user. |

**Not offered:**
- Implicit grant. RFC 9700 says not to use it.
- Resource owner password credentials. RFC 9700 says it MUST NOT be used.
- Loopback redirect for `tsq`. It needs a local browser, which headless hosts don't have.

**Device grant hardening (RFC 8628 §5):**
- The consent screen shows the client name, the requesting `tsq` host or IP and location hint, and requires explicit confirmation. Device-code phishing is the main attack here.
- The user code is short but high-entropy, and entry attempts are rate-limited per code and per account.
- The device code expires in 10 to 15 minutes. Enforce the polling `interval` and return `slow_down`.
- Scope is the minimum needed (read dashboards). Show the scope on the consent screen.

**Tokens and endpoints:**
- Access tokens are short-lived (5 to 15 minutes) and sent with the Bearer scheme (RFC 6750).
- Publish the authorization server metadata (RFC 8414).
- Include the `iss` parameter in authorization responses (RFC 9207), which protects against mix-up attacks.
- Provide revocation (RFC 7009). Introspection (RFC 7662) is needed if tokens are opaque.
- If tokens are JWTs, follow RFC 9068.
- Optional later: PAR (RFC 9126) and DPoP (RFC 9449).

## 2. Redirect URI rules

1. **Exact string match** against pre-registered URIs. This applies at the authorization request and again at the token request (RFC 9700 §4.1).
2. **No wildcards in host, path, or query.** `https://*.preview.acme-partner.dev` is **rejected**.
3. HTTPS only. The one exception is the loopback IP literals `127.0.0.1` and `[::1]` (RFC 8252 §7.3). A variable port is allowed only there, and only for native apps.
4. No fragments and no userinfo in registered URIs. Cap the number of URIs per client.
5. If `redirect_uri` is missing, unregistered, or invalid, show an error page. Never redirect to it.
6. Require `state` or PKCE, and always return `iss`.

**Why the wildcard fails:**
- Any dangling DNS record, subdomain takeover, or preview deployment someone else can claim under that suffix receives the authorization code.
- PKCE limits the damage, but the redirect rule is meant to stop this class of attack outright.
- Preview hosts are also the places most likely to run unreviewed code and log URLs.

**Ways to keep partner previews working:**
- **Preferred: one stable callback.** The partner registers a single exact URI, such as `https://auth.acme-partner.dev/callback`. Previews send users there, and the partner's own code hands the result back to the preview. We never see preview hosts. The partner must not turn this hop into an open redirect, so tell them to validate the return target against their own allow-list.
- **Programmatic exact registration.** Offer a client-management API (or RFC 7591 dynamic registration) so the partner's CI registers the exact preview URL at deploy time and deletes it on teardown. Use a short TTL and a per-client cap.
- **Dev-only clients.** A separate sandbox client ID with loose registration, test data only, and never connected to production tenants.

## 3. Access token in the query string

**No.** Reject `?access_token=` at the gateway and log it as a policy violation.

- RFC 6750 §2.3 allows it only as a last resort, and §5.3 warns about the leakage. The token ends up in access logs, browser history, proxies, and `Referer` headers. For a log-analytics product that handles customer data, that is unacceptable.
- The Authorization header is not hard in `fetch`:
  ```js
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
  ```
  The likely snag is CORS. Our API must answer preflight with `Access-Control-Allow-Headers: Authorization`. Check that before blaming the wrapper.
- For SPAs, recommend code + PKCE with the token held in memory. A small backend-for-frontend that keeps the tokens server-side is stronger (RFC 9700 §4.16).
- Never deliver tokens in the URL fragment either. That is implicit-grant behavior.

## 4. What to write in the security review doc

> **Specification conformance.** Connect with Tessaract implements the OAuth 2.0 Authorization Framework, **RFC 6749**, with Bearer Token Usage, **RFC 6750**. It supports the Authorization Code grant with Proof Key for Code Exchange, **RFC 7636**, and the Device Authorization Grant, **RFC 8628** (used by the `tsq` CLI). It follows the OAuth 2.0 Security Best Current Practice, **RFC 9700** (BCP 240). Native-app handling follows **RFC 8252** (BCP 212). Authorization server metadata follows **RFC 8414**, issuer identification follows **RFC 9207**, and token revocation follows **RFC 7009**.
>
> **Deliberate deviations and restrictions.**
> - Redirect URIs are matched by exact string. Wildcards are not supported.
> - PKCE (S256) is required for all clients.
> - The Implicit and Resource Owner Password Credentials grants are not supported.
> - Access tokens are accepted only in the `Authorization` header. The URI query parameter method (RFC 6750 §2.3) is disabled.
> - Refresh tokens are rotated, with reuse detection.

**Legal note:** do not write "OAuth 2.1 compliant". It is an IETF Internet-Draft (`draft-ietf-oauth-v2-1`) with no RFC number, so there is nothing for legal to cite. If asked, say "aligned with the practices consolidated in the OAuth 2.1 draft", and keep the RFC list above as the normative claim.

## Open decisions for you

1. Is client credentials in scope for v1, for CI service accounts?
2. Which partner-preview option do you want to offer: stable callback, programmatic registration, or both?
3. Are access tokens JWTs (RFC 9068) or opaque (introspection)?