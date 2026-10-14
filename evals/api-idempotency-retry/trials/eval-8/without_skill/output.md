# Cratebase idempotency pass: findings, recommendation, docs checklist

## 1. The plan has a gap: PUT notes and DELETE credits are not idempotent

The HTTP spec defines idempotency by intended server state, not by how the endpoint is implemented. Two of your endpoints break that contract:

| Endpoint | Spec says | Cratebase does | Retry outcome |
|---|---|---|---|
| `PUT /v2/orders/{id}/notes` | idempotent | appends a new activity-log entry per call | ❌ duplicate notes |
| `DELETE /v2/credits/{id}` | idempotent | decrements balance per call | ❌ **balance drained repeatedly** |
| `GET /v2/orders` | safe | read-only | ✅ |
| `POST /v2/orders` | not idempotent | creates | ❌ needs key |
| `POST /v2/refunds` | not idempotent | moves money | ❌ needs key |

Many HTTP clients, SDKs, proxies, and load balancers retry PUT and DELETE automatically because the spec says it's safe. Your two non-idempotent endpoints will therefore be retried silently, with no integrator code involved. That makes them riskier than the POSTs. The credit decrement is the worst case, since it is a money-adjacent side effect.

## 2. Recommendation

**Fix the DELETE at the resource level, not with a key.**
1. Make credit deletion a state transition: `active → deleted`.
2. Apply the balance decrement only on that transition, in the same DB transaction.
3. Make it race-safe with a conditional update (`UPDATE ... WHERE id=? AND deleted_at IS NULL`) or a row lock. Two concurrent DELETEs must not both decrement.
4. A repeat DELETE returns the same outcome as the first, with no second decrement. Pick 204 for both, or 404 on repeat, and document it.
5. Per your SQL rules, use soft delete (`deleted_at`).

**For PUT notes, pick one:**
- **A (ship now, non-breaking):** accept `Idempotency-Key` on this PUT as well. Document it as required for safe retries.
- **B (cleaner, breaking):** replace it with `POST /v2/orders/{id}/notes` plus the key, or make the PUT idempotent by a client-supplied `note_id`. Deprecate the PUT in a new version.

Do A before launch and plan B.

**Accept `Idempotency-Key` on three endpoints, not two:** `POST /v2/orders`, `POST /v2/refunds`, `PUT /v2/orders/{id}/notes`.

**Make the key required on `POST /v2/refunds`.** Return 400 when it is missing. A double refund is the most expensive failure here. Keep it optional on orders and notes at first, with a plan to require it later.

**Add a business-level backstop on refunds.** Cap the cumulative refunded amount at the order total, so a key bug or key reuse still cannot over-refund.

## 3. Server behavior to specify (decide before writing docs)

| Decision | Recommended |
|---|---|
| Key scope | per account (or API key) + method + path. The same key on different endpoints is independent. |
| Key format | opaque string, 1–255 chars, UUIDv4 suggested |
| Request fingerprint | hash of method, path, and body. Store it with the key. |
| Same key, same fingerprint | replay the stored response (status and body) with `Idempotent-Replayed: true` |
| Same key, different fingerprint | `422`, error code `idempotency_key_reused` |
| Same key, original still in flight | `409`, code `idempotency_request_in_progress`, with `Retry-After` |
| Missing key where required | `400`, code `idempotency_key_required` |
| Retention (TTL) | 24h from first use. Document the exact number. |
| What gets stored | 2xx and deterministic 4xx business errors. Don't store 401/403/429 or validation failures rejected before processing. Those never consume the key. |
| 5xx / crash mid-request | Treat as not completed only if the key record and the business write share one transaction. Otherwise a crash leaves a key claimed with no result. |
| Atomicity | insert key record and perform the write in one transaction, or use a lock-then-complete state machine |
| Side effects | Replays must not re-fire webhooks, emails, or payment-provider calls. Pass a derived key to any downstream provider. |

## 4. Integrator docs checklist

**Concept**
- [ ] What an idempotency key is and why retries need it
- [ ] Which endpoints accept it, which require it (refunds), and which don't need it (GET)
- [ ] Table of endpoint, key support, and retry safety, including the PUT notes caveat
- [ ] Statement that DELETE credit is safe to retry, with the exact repeat-call response

**Generating keys**
- [ ] Format, length limit, allowed characters
- [ ] Recommend UUIDv4 or a random string. Warn against timestamps, sequential IDs, or hashes of user data.
- [ ] One key per logical operation, never per attempt
- [ ] Generate and persist the key before the first attempt, so a process restart can resend the same key

**Behavior**
- [ ] Scope: per account, method, and path
- [ ] First request stores the result. A retry returns the identical status and body, plus `Idempotent-Replayed: true`.
- [ ] Reuse with a different body returns 422. Say what counts as "different" (body, path, method), and that header changes don't.
- [ ] Concurrent duplicate returns 409. Show the retry guidance with `Retry-After`.
- [ ] Retention window (24h) and what happens after expiry: the key is treated as new and the operation runs again
- [ ] Which responses are cached and which are not (validation, auth, rate limit)
- [ ] Missing key on refunds returns 400

**Retry guidance**
- [ ] Which errors to retry: network errors, timeouts, 5xx, 409, 429
- [ ] Which not to retry: 4xx other than 409 and 429
- [ ] Exponential backoff with jitter, with a sample schedule
- [ ] Retry with the same key and the same body
- [ ] A timeout does not mean failure: always retry with the key before creating anything new
- [ ] Don't reuse a key after a 422

**Per-endpoint specifics**
- [ ] `POST /v2/orders`: what a replay returns (same order ID), and that a new key creates a new order
- [ ] `POST /v2/refunds`: required, plus the cumulative-refund cap and its error code
- [ ] `PUT /v2/orders/{id}/notes`: key behavior, and that one call appends one entry
- [ ] `DELETE /v2/credits/{id}`: repeat behavior and that the balance changes once

**Errors**
- [ ] Table of codes (`idempotency_key_required`, `idempotency_key_reused`, `idempotency_request_in_progress`) with HTTP status, JSON example, and recommended action

**Examples**
- [ ] curl and one SDK sample showing the key header
- [ ] Walkthrough: timeout, retry with the same key, replayed response
- [ ] Walkthrough: the 422 mismatch case
- [ ] Sample retry wrapper that persists the key before sending

**Operational**
- [ ] Webhooks: replays don't emit duplicate events. Recommend consumers dedupe on event ID anyway.
- [ ] Sandbox behaves identically to production
- [ ] Changelog entry and a migration note for the PUT/DELETE behavior fixes, since integrators may depend on the old behavior
- [ ] Support contact and how to find a request by key in the dashboard or logs

## 5. Before launch

1. ⚠️ Fix the DELETE credit decrement and its race condition.
2. ⚠️ Decide A or B for PUT notes.
3. Write tests for each of these:
   - sequential replay
   - concurrent duplicates
   - mismatched body
   - crash between key insert and business write
   - expired key
   - double DELETE on the same credit
4. Run a deliberate-regression check: break the key check and confirm the tests fail.
5. Decide the TTL and the 5xx caching policy before the docs go out. Those numbers are hard to change once integrators depend on them.

I didn't read anything under `skill-wip/` or the codebase, so the endpoint behavior above comes only from your description.