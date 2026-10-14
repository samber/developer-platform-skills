**Do first:** in the security doc, do not write "OAuth 2.1 (RFC xxxx)". No RFC number exists for OAuth 2.1. It is still an Internet-Draft (`draft-ietf-oauth-v2-1`, at -15 in March 2026 per the skill's reference). I could not re-check the datatracker from here. Look it up before you file.

Assumptions, since this is greenfield and I didn't ask the skill's clarifying questions. Correct any that are wrong and the answer changes:
- Third-party apps include server-side and SPA clients.
- Some apps need their own identity, not just a user's.
- Org admins can gate installs.

## 1. Grant list

| Grant | Use | Rule |
|---|---|---|
| `authorization_code` + PKCE S256 | Third-party apps, SPAs, anything with a browser | PKCE mandatory for every client, public and confidential. Reject requests without it. Code is single-use, 10 min max. |
| `device_authorization` (RFC 8628) | `tsq` CLI | One-time human approval from any browser, not on the build server. |
| `refresh_token` | All of the above | Rotation with token-family reuse detection. Grace window 10-30 s from day one. |
| `client_credentials` | App-identity or org-wide access, unattended CI | Confidential clients only. Admin-issued. App-identity scopes need admin consent. |

Never implement `implicit` or the password grant.

Token policy:
- Access token: about 1 hour.
- SPA refresh token: 24 h cap.
- Other refresh tokens: 90-day inactivity cap.
- Store all tokens hashed. Keep the predecessor hash plus a timestamp for the grace window.

**`tsq` on headless build servers:** the device grant needs a human once. After that, an unattended server has two options:
1. Hold the rotating refresh token in the CI secret store. Rotation writes a new token on every use, so concurrent jobs race and trip reuse detection.
2. Use `client_credentials` with a service credential an admin issues.

For CI, I recommend option 2. Keep the device grant for developer laptops and interactive sessions.

## 2. Redirect rules

1. **Exact string match only.** No wildcards, prefixes, or patterns. RFC 9700 says pattern matching caused real attacks in the wild.
2. **Reject `https://*.preview.acme-partner.dev`.** A wildcard makes any subdomain takeover or dangling preview host a code-theft path. The host would receive authorization codes from your authorization server.
3. **Register every redirect URI explicitly at app registration.** Registration is manual and reviewed. Offer partners either:
   - **Option A (recommended):** one stable callback, for example `https://auth.acme-partner.dev/callback`. That page redirects to the right preview deployment using the app's own `state` value, checked against its own allowlist.
   - **Option B:** an API call in the partner's deploy pipeline that registers each preview URL exactly, and removes it at teardown. Cap the number of live URIs per client.
4. **HTTPS required.** The only exception is loopback `http://127.0.0.1` or `[::1]` for native apps, where the port may vary (RFC 8252). This is the sole deviation from exact matching.
5. The device grant has no redirect URI.
6. **Runtime check:** reject any `/authorize` whose `redirect_uri` is not an exact member of the registered set. Add a test with a near-miss URI such as a trailing slash or an extra subdomain.

## 3. Token in the query string

**No.** Never accept `?access_token=` on any endpoint.
- Query strings land in access logs, browser history, proxies, and Referer headers.
- RFC 9700 and OAuth 2.1 forbid it.
- Accept the Authorization header only. The POST-body form (RFC 6750 §2.2) is only for form-encoded POSTs.

Tell the frontend team the header is a few lines in their fetch wrapper:

```ts
const apiFetch = (url: string, init: RequestInit = {}) =>
  fetch(url, { ...init, headers: { ...init.headers, Authorization: `Bearer ${token}` } });
```

Two caveats for an SPA:
- A browser SPA is a public client. It needs auth code + PKCE and a 24 h refresh cap with rotation.
- If they still dislike holding tokens in browser storage, offer a backend-for-frontend that keeps tokens server-side.

## 4. What to write in the doc

Copy-ready text:

> Tessaract's authorization server implements the OAuth 2.0 Authorization Framework (RFC 6749) and Bearer Token Usage (RFC 6750). It requires PKCE (RFC 7636) for all clients and supports the Device Authorization Grant (RFC 8628). It conforms to the security requirements of *OAuth 2.0 Security Best Current Practice*, RFC 9700 (BCP 240, January 2025). It follows the OAuth 2.1 profile (`draft-ietf-oauth-v2-1`, an Internet-Draft that is not yet published as an RFC). Tessaract does not implement the implicit or resource-owner password grants. It matches redirect URIs by exact string comparison. It does not accept access tokens in URI query strings.

For legal:
- The normative, numbered documents are **RFC 6749, 6750, 7636, 8628 and 9700 (BCP 240)**.
- OAuth 2.1 has no RFC number. Cite it only as a draft.
- Add RFC 7009 (revocation) and RFC 8414 (discovery) if you ship those endpoints.
- Before launch, re-check whether OAuth 2.1 has been published and update the sentence.

## Next step (2 min)

Answer the three assumptions above, mainly whether CI needs `client_credentials` and whether org admins gate installs. Then I can draft the scope taxonomy and consent screen, which is step 2 of the skill.