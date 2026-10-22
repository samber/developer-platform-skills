# Dedup design for `POST /v1/transfers`

## First, a change to what the meeting agreed

I'd drop "SHA-256 of the body as the dedup key in one global table". It fails on your own constraint, and it fails in two more ways.

1. **It can't tell a retry from a second transfer.** Two same-day transfers to one vendor for the same amount have identical bodies, so they hash to the same value. The second one gets rejected or swallowed, and a vendor goes unpaid with no signal to the customer. That is as bad as a double payout, and harder to notice.
2. **A global table leaks across customers.** Customer A and customer B can send byte-identical bodies. B's request would collide with A's row, and a replay would return A's stored response to B. The key must be scoped to the account.
3. **Body hashes miss real retries.** A retry that re-serializes the JSON (key order, whitespace) or includes a timestamp or nonce gets a different hash and is paid twice.

Hashing is still useful, but only as a fingerprint to detect misuse of a key. It shouldn't be the key.

**Recommendation:** a client-supplied `Idempotency-Key` header, scoped per account. The client has to send a key, which is a small change for integrators, but it's the only way to carry intent. Section 5 gives an interim server-only guard for clients that haven't migrated.

## 1. How keys work

- The client sends `Idempotency-Key: <opaque string, 1–255 ASCII chars>` on `POST /v1/transfers`.
- Uniqueness is `(account_id, key)`. The account comes from the API credential, never from the body.
- The server stores a fingerprint with each key: SHA-256 of `method + path + canonicalized JSON body`. Use RFC 8785 JCS canonicalization so re-serialization doesn't change the hash. The fingerprint detects "same key, different request".
- The record is created in the same DB transaction as the transfer, so there is no state where a transfer exists without its key, or the reverse.

```sql
CREATE TABLE idempotency_keys (
  id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  account_id       BIGINT      NOT NULL REFERENCES accounts(id),
  key              TEXT        NOT NULL,
  request_hash     BYTEA       NOT NULL,       -- SHA-256 fingerprint
  state            TEXT        NOT NULL,       -- 'in_progress' | 'completed'
  transfer_id      BIGINT      NULL REFERENCES transfers(id), -- nullable until created
  response_status  SMALLINT    NULL,           -- nullable until completed
  response_body    JSONB       NULL,           -- nullable until completed
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at       TIMESTAMPTZ NOT NULL,       -- created_at + retention
  UNIQUE (account_id, key)
);
```

No `ON DELETE CASCADE`, per your SQL conventions. Expired rows are purged by a job.

### Request flow

1. Validate auth and the key format.
2. `INSERT ... (account_id, key, request_hash, state='in_progress') ON CONFLICT DO NOTHING`. The unique index is the lock, so concurrent retries can't both win.
3. If the insert won:
   1. Create the transfer.
   2. Set `state='completed'`, store the response, and commit.
4. If it conflicted, read the existing row and branch on the table below.

## 2. What the API returns

| Situation | Response |
|---|---|
| First request | `201 Created` with the transfer. |
| Same key, same fingerprint, completed | Original status and body, plus the header `Idempotent-Replayed: true`. |
| Same key, original still running | `409 Conflict`, error `idempotency_key_in_progress`, with `Retry-After: 2`. |
| Same key, different fingerprint | `422 Unprocessable Entity`, error `idempotency_key_reuse`. Nothing is executed. |
| Missing key (after enforcement date) | `400`, error `idempotency_key_required`. |
| Key expired | Treated as a new request. |

Rules for what gets stored:

- Store terminal outcomes once execution began: success, or a business rejection such as insufficient funds.
- Don't store failures that happened before any side effect, such as auth, validation, `429`, or a transient `5xx` where no transfer was created. A retry must be able to run for real.
- Error bodies use your standard error envelope. `idempotency_key_reuse` should name the key, never echo the other body.

**Retention:** 7 days, longer than the Stripe-style 24h, because payouts carry real money and some clients run retry queues. After expiry a retry creates a new transfer. State that limit in the docs.

## 3. Rail-level protection

Derive a deterministic idempotency reference from `transfer_id` for the downstream bank or payout rail, if it supports one. Then an internal worker retry can't double-send either, independent of the API-layer fix.

## 4. What we tell integrators about picking keys

> **One key per payout intent, not per HTTP attempt.**
>
> 1. Generate a UUIDv4 when you create the payout in your own system, and store it with that record before the first send.
> 2. Reuse the same key and the same body on every retry of that payout: network errors, timeouts, `5xx`, `409 in_progress`.
> 3. Use a new key for every distinct transfer, even when vendor, amount, and day are identical. Two same-day payments of the same amount are two intents and get two keys.
> 4. Don't derive keys from the body, a hash of the body, or vendor + amount + date. That reproduces the double-payment-or-blocked-payment problem on your side.
> 5. Don't reuse a key with a different body. You'll get `422 idempotency_key_reuse`, which means a bug in your client.
> 6. Keys are remembered for 7 days. Don't retry a request older than that without first checking whether it was created (`GET /v1/transfers`, filtered by your `reference`).
> 7. If you retry after a timeout and get the original response back with `Idempotent-Replayed: true`, the payout was already created. Don't send it again.

Ship this with a worked retry example in each official SDK, and have the SDKs generate and persist a key automatically when the caller doesn't pass one.

## 5. Rollout: "clients don't have to change anything"

That goal can't be fully met. Without a key, the server can't know whether identical bodies are a retry or a deliberate repeat. Here's a staged path that limits the damage:

1. **Now (log only):** compute the fingerprint per `(account_id, fingerprint)` and log repeats within a window. Check your 43 duplicates first: how many customers, and what was the gap between the two requests? That sets the window, probably tens of seconds to a few minutes. It also tells you who to contact directly.
2. **Interim guard (no key sent):** a repeat of the same account and fingerprint inside that short window returns `409 possible_duplicate` with the original `transfer_id`. The escape hatch is that any request carrying an `Idempotency-Key` skips the guard. A customer with a legitimate repeat sends a fresh key and goes through. This is the only path where the hash makes a blocking decision, and it's temporary.
3. **Key supported and documented:** SDKs updated, top duplicate-offenders contacted.
4. **Key required:** an announced date, a sunset header on keyless requests beforehand, then `400 idempotency_key_required`. Remove the interim guard.

## 6. What to measure

- Replay count (`Idempotent-Replayed`): the retries you're now absorbing.
- `idempotency_key_reuse` rate: a rising count points to a broken client.
- `possible_duplicate` rate and how many are followed by a keyed override: shows how many blocks were false positives.
- Duplicate payouts per month (target 0), recomputed with the same `(account, vendor, amount, short window)` query you used to find the 43.

## Open questions for you

- Does your payout rail accept its own idempotency reference? That decides how strong section 3 can be.
- Is 7 days right for retention, given your longest client retry queue?
- Which fields should be in the fingerprint? I assumed the full body. If some fields are legitimately mutable on retry (like a client timestamp), exclude them.