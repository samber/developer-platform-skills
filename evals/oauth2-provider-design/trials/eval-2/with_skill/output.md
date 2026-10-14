# Northwind Signal token policy (draft for Friday's security review)

I built this from the `oauth2-provider-design` skill and its protocol-baseline reference. Both your instincts are right, but each needs one change before the security team sees it. The hashing rule collides with the reuse grace window, so the storage layer has to be designed for both. Rotation also needs a different shape for each of your three clients.

## Assumptions to confirm

I didn't get to ask these, and each one changes a row below.

1. The SPA and the partner integrations act on behalf of a signed-in user, using `authorization_code` with PKCE.
2. The customer's Python worker acts as the app itself (machine-to-machine), not on behalf of a person. If it acts for a user, treat it as the partner row, with the device flow if it is headless.
3. You issue opaque access tokens, not JWTs. If you issue JWTs, they can't be revoked mid-life, so the TTLs below become a hard ceiling.

## Rules for all clients

- PKCE S256 is mandatory for every client, including the ones with a secret.
- Redirect URIs are matched exactly. No implicit or password grant.
- Bearer tokens go in the Authorization header only, never in a query string.
- Authorization codes are single-use with a maximum 10-minute lifetime.
- Refresh tokens rotate by default and belong to a family, traceable to the original grant. Retrofitting families later is much harder.

## TTLs and rotation per client kind

| | React SPA (public) | Partner server-side (confidential) | Python worker (confidential, app identity) |
|---|---|---|---|
| Grant | `authorization_code` + PKCE | `authorization_code` + PKCE + client secret | `client_credentials` |
| Access token | 30 min | 60 min | 60 min |
| Refresh token | Rotating, family-bound | Rotating, family-bound | None. It re-authenticates with its credentials. |
| Refresh idle timeout | 8 h | 90 days | n/a |
| Refresh absolute cap | 24 h, then full re-login | 365 days, then re-consent | n/a |
| Reuse grace window | 20 s | 30 s | n/a |
| Reuse outside the window | Revoke the family | Revoke the family | n/a |
| Live-token cap | 10 per user per client, oldest revoked | 10 per grant | n/a |
| Credential rotation | n/a | Two active secrets at once, 90-day rotation | Two active secrets at once, 90-day rotation |

**Where the numbers come from:**
- The skill sets the ~1-hour access token as the cross-provider convergence point.
- The skill backs the 24-hour SPA cap with Microsoft's SPA refresh limit and the 90-day idle timeout with Microsoft's non-SPA limit.
- The skill backs the 10-token cap with GitHub, and the 10–30 s grace window with the Django OAuth Toolkit and Keycloak defaults.
- The 30-minute SPA access token, the 365-day partner cap, the 8-hour SPA idle timeout, and the 90-day secret rotation are my judgment, not from the skill. Treat them as defaults the security team can argue with.

**SPA.** A refresh token in browser storage is the highest-exposure asset you have, so it gets the hardest cap. Because the SPA is embedded in your customers' admin panels, a third-party-iframe context may partition or block storage. Keep tokens out of `localStorage`, ideally behind a backend-for-frontend. The skill doesn't cover this, so verify it with your front-end team.

**Partners.** The skill allows non-rotating refresh tokens for confidential clients, because client authentication already constrains who can redeem them. I still recommend rotation, since it is the skill's default and Salesforce now mandates it for all connected apps. Partners with multiple workers will refresh concurrently, and they will trip reuse detection unless they serialize refreshes. Put "refresh single-flight, persist the new token before using it" in the partner docs and the SDK.

**Python worker.** `client_credentials` gives it no refresh token, so there is nothing to rotate. The risk moves to the client credential. Support two active secrets with an overlap window so the customer can rotate without downtime, and consider `private_key_jwt` for this customer. The `private_key_jwt` suggestion is mine, not from the skill.

## Your two beliefs, adjusted

**"Rotate on every use, kill the session on reuse": yes, with three amendments.**

1. **Grace window.** Without one, a multi-tab SPA or a network retry looks like theft and logs out real users. Reuse inside the window is not an attack. Reuse outside it revokes the whole family.
2. **Scope of the kill.** Revoke the family, meaning that one grant and its live access tokens. Don't revoke every grant the user has. Revoking the family is safe because the attacker may hold an earlier or later token in the chain than the one that tripped the check.
3. **What it tells you.** Per RFC 9700 §4.14, the server can't tell which party sent the stale token. It's a tripwire, not an investigation tool. Log every trip with client, family, and age of the replayed token, and track the trip rate. A rising rate means attacks or a window that is too tight.

**"SHA-256 every token": yes, with one design decision.** SHA-256 is correct for high-entropy random tokens (at least 128 bits from a CSPRNG), and it needs no salt or slow hash. The conflict is that the grace window must recognize a token that was just consumed. A hash-only store can recognize that token, but it can't hand back the successor's cleartext, because only the successor's hash is stored.

My proposed resolution (my reasoning, not the skill's, so the security team should review it):
- Keep the predecessor's hash with a `consumed_at` timestamp.
- If the predecessor is re-presented inside the window, mint a new successor from the same parent. Don't try to return the original one.
- Sibling successors stay valid until one is used. After that, the others are consumed and fall under the normal rule.

Django OAuth Toolkit documents this exact tension, and its resolution is to retain the predecessor's hash with a validity timestamp. Don't drop hashing to avoid the problem.

## What the storage layer must support

1. **Hashed lookup.** One indexed column holds each token's SHA-256 hash. Token cleartext is never stored or logged. Client secrets are hashed the same way.
2. **Refresh token record.** It needs `family_id`, `parent_hash`, `client_id`, `user_id`, `grant_id`, `scopes`, `created_at`, `consumed_at`, `expires_at`, and `revoked_at`. Use soft revocation, never `ON DELETE CASCADE`, so you keep the evidence after a reuse event.
3. **Family record.** It tracks `absolute_expires_at`, the revoked state and reason, and the last-used time for the idle timeout.
4. **Atomic consume.** Use a compare-and-set, such as `UPDATE ... SET consumed_at = now() WHERE hash = $1 AND consumed_at IS NULL`, and check the affected row count. Two concurrent refreshes must not both succeed. This also gives you the race-safe grace-window decision.
5. **Family revocation that also kills access tokens.** Opaque access tokens are checked against the database, so revoking a family takes effect immediately. Link access tokens to their `family_id`.
6. **Live-token cap.** Enforce it at issue time and revoke the oldest.
7. **Revocation and introspection.** Provide `/revoke` (RFC 7009) and `/introspect` (RFC 7662) endpoints, plus admin and user views: revoke by client, by user, or by customer org.
8. **Two active secrets per confidential client**, each with its own `created_at` and `expires_at`.
9. **Cleanup job.** Purge expired and revoked rows after a retention period you choose. Keep reuse-event audit rows longer.
10. **Reuse-event log.** One row per trip, with the dimensions listed above.

## Gates before the review

- **Reuse test.** In staging, replay a consumed refresh token outside the window. The family must be revoked and its access tokens must stop working.
- **Concurrency test.** Run concurrent refreshes inside the window. They must produce no false-positive logout.
- **Protocol test.** Confirm that no implicit or password grant is advertised, that a request without PKCE is rejected, and that redirect matching is exact.
- **Baselines from launch.** Track the reuse-trip rate, refresh failures by client kind, and the number of live families per client.

## Open decisions for the security team

- The 365-day partner cap and 90-day idle timeout. These trade re-consent friction against exposure.
- Whether the worker customer gets `private_key_jwt` or a rotated secret.
- Whether to move to DPoP later. The skill says to promote it only for financial or health data or long-lived agent tokens, and it has little client-library support today.