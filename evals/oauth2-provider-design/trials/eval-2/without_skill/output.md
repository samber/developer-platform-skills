# Northwind Signal token policy (draft for Friday's security review)

## Decisions to confirm before Friday

1. **Partner integrations.** I assumed they use `client_credentials`: the partner acts as itself, with no end user. If partners also act on behalf of a customer admin (authorization code flow), use the "delegated variant" rows below.
2. **SPA token placement.** Third-party cookie blocking can break an iframe embed. I assumed a top-level or same-site embed where the refresh token lives in JS memory only. If you embed in an iframe, you need a BFF or a host-page token handoff, and the policy changes.

## Where I'd adjust the two inputs

- **SHA-256 hashing: agreed, with a scope fix.**
  - Hash anything we store and later look up by presented value: refresh tokens, authorization codes, client secrets, and opaque access tokens if we use them.
  - Don't hash JWT access tokens. We don't store them, so there is nothing to hash. If we log `jti`, log that, never the token.
  - Plain SHA-256 is correct only because every token is 256-bit CSPRNG output. Don't use bcrypt or argon2 here. They are the wrong tool for per-request lookups, and high-entropy inputs don't need them. Never apply this scheme to anything a human chooses.
  - Hashing protects against a read-only database leak. It doesn't protect against an attacker who can write rows. Say so in the policy.
- **Rotation with reuse detection: agreed for the SPA, with a grace window.**
  - Strict "any reuse kills the session" produces false positives. Two tabs refresh at once, or a response is lost on a flaky network and the client retries.
  - Because we store only hashes, we can't replay the previous response. The grace rule below handles this.
  - For server-side clients, treat reuse as a signal to alert on, with a longer grace window, since retries are routine there.

## Token parameters per client kind

| | **React SPA (embedded)** | **Partner server-side** | **Customer Python worker** |
|---|---|---|---|
| Grant | Authorization code + PKCE, public client | `client_credentials` | `client_credentials` |
| Client auth | None (PKCE only) | Client secret | `private_key_jwt` (asymmetric key); mTLS is the alternative |
| Access token | JWT, **10 min**, carries `sid` | JWT, **30 min** | JWT, **15 min** |
| Refresh token | Yes, **rotating**, in JS memory only, never `localStorage` | None | None |
| Refresh idle timeout | **4 h** | n/a | n/a |
| Refresh absolute lifetime | **24 h**, then full re-auth | n/a | n/a |
| Reuse grace window | **10 s**, predecessor only | n/a | n/a |
| Credential lifetime | n/a | Secret: rotate every **90 days**, hard expiry **12 months** | Key: rotate every **180 days**, hard expiry **12 months** |
| Credential overlap | n/a | 2 active secrets max, overlap ≤ **30 days** | 2 active public keys max (via JWKS or upload) |
| Assertion lifetime | n/a | n/a | `exp` ≤ **60 s**, `jti` single-use |

**Delegated variant for partners** (authorization code flow):
- Confidential client with a rotating refresh token.
- Idle timeout 30 days, absolute lifetime 180 days.
- Reuse grace window 60 s, because server retries are normal.
- Reuse revokes the family and notifies the partner's technical contact.

**Authorization codes** (all flows that use them):
- TTL 60 s, single use, stored hashed.
- A second use revokes every token issued from that code.

### Rotation rules

1. **Every refresh issues a new refresh token and invalidates the old one.** The new token keeps the same `family_id`. Idle and absolute clocks are set at issue time. The absolute deadline never extends.
2. **Reuse of a used token outside the grace window:**
   - Revoke the whole family.
   - Write an audit event.
   - The SPA user re-authenticates.
3. **Grace window (SPA):**
   - The predecessor is accepted for 10 s only if its successor has never been presented.
   - We mint a sibling child, and the earlier child is marked superseded.
   - Once the successor has been used, any reuse of the predecessor counts as theft.
   - The SPA should also serialize refresh across tabs with the Web Locks API, which makes grace-window hits rare.
4. **Expired tokens:**
   - A token presented after its idle or absolute expiry is rejected with no theft alert, to avoid noise.
   - Alert only when a used or revoked token is presented while its family is still within its absolute lifetime.
5. **Client secret rotation is partner-initiated:**
   - Show the secret once.
   - Allow at most 2 active secrets.
   - Record `last_used_at` so partners can see when the old one is safe to retire.

## What the storage layer must support

### 1. Token tables

Refresh tokens (and authorization codes) need these columns:

- `token_hash` (32 bytes, **unique index**)
- `family_id`, `parent_id`
- `client_id`, `tenant_id`, `subject`, `scopes`
- `status` (`active` / `used` / `revoked`)
- `created_at`, `idle_expires_at`, `absolute_expires_at`
- `used_at`, `replaced_by`, `grace_until`
- `revoked_at`, `revoked_reason`

Client credentials need their own table:

- `secret_hash` or `public_key`
- `client_id`, `created_at`, `expires_at`
- `last_used_at`, `revoked_at`

Constraints on both:
- No `ON DELETE CASCADE`.
- Every row has `created_at`.

### 2. Keep used tokens until the family expires

If we delete a rotated token's row, a replayed token looks unknown instead of stolen, and detection stops working. Retain rows until `absolute_expires_at` plus an audit retention period (suggest 90 days). After that, purge via a scheduled job, or soft-delete if you want to keep your usual rule.

### 3. Atomic consume

Consume with a single compare-and-set statement, and insert the child row in the same transaction:

```sql
UPDATE refresh_tokens
SET status = 'used', used_at = now()
WHERE token_hash = $1 AND status = 'active' AND idle_expires_at > now()
RETURNING *;
```

- Zero rows means the token is unknown, expired, or reused.
- A follow-up read, on the primary, decides which.
- A read-then-write version races, and two parallel refreshes would both succeed.

### 4. Strong consistency on the refresh path

- Reuse detection needs read-your-writes on the primary.
- Replica lag turns a theft into a false "unknown token".
- In multi-region setups, route token endpoints to a single writer.

### 5. Bulk revocation

Indexes and queries for these kill switches:
- by `family_id`
- by `subject`
- by `client_id`
- by `tenant_id`

You need these for incident response, such as "revoke everything for one tenant" or "revoke one partner".

### 6. Access token revocation

- JWTs can't be recalled, so residual exposure after a revoke is the TTL: 10 / 30 / 15 min.
- For the SPA, resource servers check `sid` against a revoked-session set held in an in-memory or Redis set with TTL of 10 min (the access TTL).
- For machine clients, accept the TTL and revoke the credential. The security team should sign off on that tradeoff.

### 7. `jti` replay cache (worker)

- A store with TTL, keyed by `(client_id, jti)`, unique and expiring after the 60 s assertion lifetime.
- Redis `SET NX EX 60` works, or a table with a unique constraint and a cleanup job.

### 8. Audit log (append-only)

Events: issued, refreshed, reuse-detected, grace-hit, family-revoked, secret-created, secret-rotated, secret-expired. Include `client_id`, `tenant_id`, `subject`, IP and user agent where available. Alert on reuse-detected and on spikes in grace hits.

### 9. Token format and hygiene

- 32 bytes from a CSPRNG, base64url-encoded, with a typed prefix such as `nws_rt_` and `nws_cs_`. The prefix lets secret scanners detect leaks.
- Never log tokens or secrets.
- Return plaintext exactly once, at creation.

## Residual risks to list in the policy

- A write-capable database attacker can insert known hashes.
- Revoking a machine credential leaves up to one access TTL of exposure.
- XSS in the SPA can use the in-memory refresh token while the page is open. The mitigations are a strict CSP and the 24 h absolute lifetime.