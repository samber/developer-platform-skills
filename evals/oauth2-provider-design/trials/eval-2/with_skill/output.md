Policy below. Two corrections to your plan come first, because both change what you write on Friday.

## Corrections to your plan

1. **Hashing every token is right, and it fits with rotation.** Hashing only changes how you look a token up. You must keep consumed refresh-token hashes, with a `consumed_at` timestamp, until the whole family expires. Without them you cannot detect reuse or honour a grace window. Django OAuth Toolkit documents this tension. Resolve it by keeping the predecessor's hash, not by dropping hashing.
2. **Reuse should kill the grant family, not the "session".** A family is the chain of refresh tokens descended from one consent. Revoke that family only. Leave the user's other grants alone.
3. **Rotation without a grace window logs out real users.** The trigger is two tabs or a network retry presenting the same just-consumed token. RFC 9700 §4.14 describes reuse detection as a tripwire. It cannot tell attacker from victim. A 10–30 s grace window keeps false positives down.

## Token policy

| | SPA (public) | Partner server (confidential) | Customer Python worker (confidential) |
|---|---|---|---|
| Grant | `authorization_code` + PKCE S256 | `authorization_code` + PKCE S256, plus `client_credentials` for app-identity calls | `client_credentials` (recommended) |
| Auth code | single-use, 60 s | single-use, 60 s | none |
| Access token | 30 min | 1 h | 1 h |
| Refresh token | rotate every use | rotate every use | none |
| Refresh idle limit | 8 h | 90 days | n/a |
| Refresh family absolute cap | 24 h, then full re-auth | 12 months, then re-consent | n/a |
| Reuse grace window | 30 s | 30 s | n/a |
| On reuse outside grace | revoke family | revoke family and notify the partner | n/a |

**Sourced numbers:**
- 1 h access tokens are the cross-provider convergence point.
- The 24 h browser cap and the 90-day idle limit come from Microsoft.
- The 10–30 s grace window and the 10-minute code maximum come from the skill.

**My judgment, which you can push back on:**
- The 30 min SPA access token. I went shorter than the 1 h baseline because the token lives in a browser.
- The 8 h SPA idle limit.
- The 12-month partner cap.
- The 60 s code lifetime.

Rotation is mandatory for the SPA, because OAuth 2.1 requires sender-constrained or rotated refresh tokens for public clients. For confidential clients it is optional under 2.1. I still apply it because it is the default rung, Salesforce now enforces it, and your security team will ask.

### SPA
- PKCE is mandatory. Use exact redirect URI matching.
- Keep the refresh token in memory only, or put the SPA behind a backend-for-frontend. Never use `localStorage`.
- Embedded in a customer's admin panel, you will be hit by third-party cookie and storage partitioning. That is a reason to keep the 24 h cap and silent re-auth.

### Partner servers
- Exact redirect matching. Use `client_credentials` only for app-identity scopes.
- Allow two active client secrets per client, so partners can rotate without downtime.
- A reuse trip fires a webhook and email to the partner. Partners with several workers will trip it first.
- Cap live grants at 10 per user and client. The oldest is auto-revoked, as GitHub does.

### Customer Python worker
- Use `client_credentials`. A headless, long-running process is the worst case for rotation. If it crashes between receiving a new refresh token and saving it, the family gets revoked.
- Register a separate `client_id` per customer deployment. Revoking it then affects only that customer.
- If the worker must act as a user, use `device_authorization` (RFC 8628) with rotating refresh and a 30 s grace window.
- A worker on a refresh path must have a single refresher and must persist the new token before using it.
- Do not add DPoP or mTLS now. The skill defers them to financial or health data and long-lived agent tokens. Revisit if this customer's scopes reach other users' data.

## What the storage layer must support

1. **Token hashing.**
   - Store SHA-256 of codes, access tokens, refresh tokens, and client secrets.
   - Generate tokens with at least 256 bits of randomness. Plain SHA-256 is safe only because the input is high-entropy.
   - Put a unique index on `token_hash` and look up by hash.
2. **Opaque access tokens.** The database can then revoke them instantly. If you issue JWTs instead, the short TTL is your only revocation mechanism.
3. **A `grants` table, one row per consent. Its id is the family id.** Columns:
   - `client_id`, `user_id`, `org_id`
   - `scopes_granted`, kept separately from the scopes requested
   - `absolute_expires_at`, `revoked_at`, `revoke_reason`
   - `created_at`
4. **A `refresh_tokens` table.** Columns:
   - `token_hash`, `grant_id`, `parent_id`
   - `consumed_at`, `idle_expires_at`, `created_at`
   - Do not delete consumed rows until the grant's `absolute_expires_at` has passed. Reuse detection needs them.
5. **An atomic single-use consume.**
   ```sql
   UPDATE refresh_tokens SET consumed_at = now()
   WHERE token_hash = $1 AND consumed_at IS NULL
   RETURNING grant_id;
   ```
   - If a row is returned, issue the successor.
   - If no row is returned, load the row.
     - If `consumed_at` is within the grace window, issue a new sibling child from the same parent. You cannot replay the first successor, because only its hash is stored.
     - Otherwise, set `grants.revoked_at` in the same transaction.
6. **Access-token revocation by family.** Access tokens carry `grant_id`. Introspection checks `grants.revoked_at`. Make sure resource servers cannot cache this check beyond a few seconds.
7. **Per-tenant data rules.**
   - Soft delete only.
   - `created_at` on every table.
   - No `ON DELETE CASCADE`. A grant is user-owned data.
8. **Audit and alerting.**
   - Log every reuse trip and every revocation, with the client and the reason.
   - Track the reuse-trip rate. It signals both attacks and a grace window that is too tight.
9. **A purge job** for expired families, after your retention period.

## Tests for the review

- Replay a consumed refresh token outside the grace window. The whole family must be revoked.
- Two concurrent refreshes inside the grace window must not log anyone out.
- Absent or wrong PKCE must be rejected for every client, including confidential ones.
- Verify by test, not assertion, that the discovery document advertises no implicit or password grant.

## Open questions that could change the table

1. Does the Python worker act as the customer's user or as an app? I assumed an app.
2. Is the SPA embedded in an iframe, or loaded as a script on the customer's origin?
3. Greenfield, or are there live integrations? A retrofit changes the rotation rollout.
4. Do any scopes reach other users' data or PII? If so, partner apps need a verification tier before they ship.

Next, in about 20 minutes: paste the TTL table into your policy doc and send answers to open questions 1 and 2. I'll tighten the worker and SPA rows.