# Northwind Signal: Token Policy (draft for Friday's security review)

## 1. Two corrections to the brief

**"Hash every token" is right only for tokens we store.**
- Stored: refresh tokens, client secrets, authorization codes, opaque API keys. Hash all of these.
- Not stored: self-contained signed access tokens (JWTs). There is nothing to hash. If you want instant revocation, store only a `sid` or `jti` denylist entry.
- Plain SHA-256 with no salt is acceptable only because we generate every secret ourselves with at least 256 bits of CSPRNG entropy. Never apply it to a human-chosen secret.
- Hashing does not protect against an attacker with DB **write** access, who can insert the hash of a token they know. Restrict write privileges on these tables.

**"Rotate on every use and kill the session on reuse" is correct for the SPA and the wrong default for the other two clients.**
- It fits public clients, which can't authenticate (RFC 9700, the OAuth 2.0 Security BCP).
- A confidential server with several pods refreshing the same token will trip reuse detection by accident. One retried request after a lost response would kill a customer's whole integration.
- The better fix for server clients is to give them **no refresh token** at all (see 3.2 and 3.3).

## 2. Assumptions

Tell me which are wrong and I'll rework the affected section.

1. **Partner integrations** act as the tenant (machine-to-machine). The customer admin's install is a durable record on our side, not a refresh token.
2. **The Python worker** is also machine-to-machine, so it uses the same grant as partners but with stronger credentials.
3. **The SPA** acts as a logged-in admin user.
4. **Access tokens** are signed JWTs, validated statelessly.

## 3. Rules per client kind

### 3.1 React SPA (public client, embedded in the customer's admin panel)

| Item | Rule |
|---|---|
| Grant | Authorization code + PKCE (S256). No implicit flow, no password grant. |
| Access token | JWT, **5 min**, audience- and tenant-bound. Kept in memory only, never `localStorage`. |
| Refresh token | **Rotates on every use.** |
| Idle timeout | **30 min** without a refresh ends the session. |
| Absolute lifetime | **8 h** from login, then full re-authentication. |
| Reuse detection | A consumed token presented outside the grace window **revokes the whole family**. |
| Grace window | **10 s.** A retry of the just-consumed token issues a new sibling and revokes nothing. This covers lost responses and double tabs. |
| Storage in browser | HttpOnly, Secure cookie scoped to our auth domain, `SameSite=None; Partitioned` if the SPA runs in an iframe. Never readable by JS. |
| Sender binding | DPoP (RFC 9449) is optional for v1. Put it on the roadmap. |

**Embedding caveat:** third-party cookie blocking and storage partitioning will break refresh cookies in an iframe on some browsers.
- Preferred design: **no refresh token in the SPA.** The customer's backend mints a short launch token, and the SPA exchanges it for a 5-min access token. When that expires, the SPA asks the host page for a new launch token.
- Fall back to the rotating cookie above only where the embed is same-site.
- Decide this before Friday, because it changes the SPA section.

### 3.2 Partner server integrations (confidential, client secret)

| Item | Rule |
|---|---|
| Grant | `client_credentials`, tenant-scoped through the install record. |
| Access token | JWT, **15 min**. The client re-requests it with its secret. |
| Refresh token | **None issued.** Nothing to rotate, steal, or race on. |
| Client secret | `nws_sec_` prefix plus 32 random bytes. Shown once. Stored as SHA-256. |
| Secret lifetime | **Expires at 12 months.** Alerts at 60, 30 and 7 days. |
| Secret rollover | **Up to 2 active secrets per client**, so partners rotate without downtime. Old secret revoked on request or at expiry. |
| Revocation | Customer admin removes the install, or we revoke the client. Effective at the next token request. Outstanding access tokens live at most 15 min. |

If a partner needs user-delegated access (acting as a specific user), issue a refresh token with these rules:
- Require client authentication at the refresh endpoint.
- Rotate on every use.
- Treat reuse inside a **60 s** window as a concurrency retry. Reject with a retryable error and do not revoke.
- Treat reuse outside the window as theft and revoke the family.
- Set idle timeout to 30 days and absolute lifetime to 90 days.

### 3.3 Python worker on the customer's infrastructure

We don't control this host, so assume it can be compromised.

| Item | Rule |
|---|---|
| Grant | `client_credentials` with **`private_key_jwt`** (RFC 7523), or mTLS (RFC 8705). Client secret only as a fallback. |
| Credential | The customer keeps the private key. We store only the public key or JWKS, so there is no secret to hash. |
| Access token | JWT, **10 min.** Shorter than for partners because the host is outside our control. |
| Refresh token | **None.** |
| Key lifetime | Keys expire at 12 months. **2 active keys** allowed during rollover. |
| Scope | Narrowest scopes, one client per worker, per-client rate limits. |
| Detection | Alert on new source ASN or IP, and on a spike in token requests. Offer an optional IP allow-list. |
| Fallback secret | Same rules as 3.2, but expiry is **6 months**. |

## 4. Revocation triggers (all kinds)

- Logout.
- User disabled or removed.
- Password or MFA change.
- Role or permission downgrade.
- Customer admin removes an integration.
- Tenant offboarding.
- Reuse detected.

**Residual window:** revoking a family does not kill access tokens already issued.
- The exposure is at most 5 min (SPA), 10 min (worker), or 15 min (partners).
- Tell the security team this explicitly.
- If that is too long for admin actions, put `sid` in the JWT and check a TTL-bounded Redis denylist at the resource servers. The TTL equals the longest access TTL.

## 5. What the storage layer must support

Assuming PostgreSQL. Every table has `created_at`, and there is no `ON DELETE CASCADE`.

**`token_families`** (one row per session or grant)
- `id`, `tenant_id`, `subject_id`, `client_id`, `client_kind`, `scopes`, `dpop_jkt` (nullable)
- `last_used_at` (idle timeout), `absolute_expires_at`
- `revoked_at` (nullable), `revoked_reason` (enum: `reuse`, `logout`, `admin`, `credential_change`, `offboarding`)

**`refresh_tokens`**
- `id`, `family_id`, `token_hash bytea(32)` with a **unique index**
- `parent_id`, `expires_at`
- `used_at` (nullable), `replaced_by_id` (nullable)

**`client_secrets`**
- `client_id`, `secret_hash`, `prefix` and `last4` (for display and secret scanning)
- `expires_at`, `last_used_at`, `revoked_at`
- Several rows may be active at once.

**`client_public_keys`**
- `client_id`, `kid`, `jwk`, `not_before`, `expires_at`, `revoked_at`

**`security_events`**
- Reuse detections, revocations, and failed client authentications.
- Include IP, user agent, `family_id` and `client_id`.

### Requirements that are easy to miss

1. **Keep consumed tokens.** Reuse detection only works if used hashes stay in the table. Purge them only after the family's `absolute_expires_at` plus a 30-day audit window.
2. **Atomic consume.** In one transaction, run `UPDATE refresh_tokens SET used_at = now() WHERE token_hash = $1 AND used_at IS NULL AND expires_at > now() RETURNING …`. Insert the child token and update `last_used_at` in the same transaction.
   - One row returned means success.
   - Zero rows means a second query to classify the failure: unknown, expired, reused inside grace, or reused outside grace.
3. **Primary-only reads on the refresh path.** A lagging replica reports a consumed token as unused and defeats detection.
4. **Use the DB clock** (`now()`) for all expiry decisions, not app-server clocks.
5. **Family revocation must be cheap.** Index `family_id`, `(tenant_id, subject_id)` and `(tenant_id, client_id)`, so "revoke every session of this user or tenant" is one statement. Check `revoked_at` on every refresh.
6. **Soft revoke, never delete,** during the retention window. Use `revoked_at` and `revoked_reason`.
7. **Growth.** Rows are roughly sessions × (session length ÷ access TTL). An 8 h SPA session at a 5 min access TTL creates up to about 96 rows. Partition `refresh_tokens` by month and drop whole partitions at retention end.
8. **Never log tokens.** Log the first 8 hex characters of the hash, plus `family_id`.
9. **Rate-limit** the refresh and token endpoints per family and per client.

## 6. Decisions to confirm before Friday

1. SPA embed model: launch token exchange (preferred) or a rotating cookie?
2. Do any partners need user-delegated refresh tokens, or is `client_credentials` enough for all of them?
3. Is a 5–15 min residual window after revocation acceptable, or do we build the `sid` denylist?
4. Are the 12-month secret and key expiries acceptable to partners, given the commercial impact?

## References

- RFC 9700: OAuth 2.0 Security BCP
- IETF OAuth browser-based apps BCP (draft)
- RFC 7523: JWT client authentication
- RFC 8705: mTLS client authentication
- RFC 9449: DPoP