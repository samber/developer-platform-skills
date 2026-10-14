# Lumapay `POST /v1/transfers` dedup design

## Change to the meeting decision

I recommend **not** building the SHA-256-body-as-key design in one global table. The skill I followed for this (`api-idempotency-retry`) rejects it for four reasons:

1. **It drops legitimate payouts silently.** Two identical transfers (same vendor, same amount) in one day have identical bodies. The second would be treated as a retry and never paid, with no error to the customer. That is a worse failure than a double payout, because it is invisible and the vendor simply goes unpaid. A server-inferred key can't tell "network retry" from "I really want two".
2. **A global table leaks across tenants.** If two customers send byte-identical bodies, the second could be handed the first's stored response. Scope must be `(account_id, key)`.
3. **It misses retries whose bodies differ.** A retry that carries a timestamp or request ID hashes differently and gets through. This is the same failure as a fresh key per attempt.
4. **"Clients change nothing" can't hold for money movement.** Only the client knows whether a request is a retry or a new intent. The fix is a one-line client change, which the SDKs can make for most integrators (see Rollout).

**What survives from the meeting:** the SHA-256 of the body is kept as a *fingerprint* stored next to the key. It is used only to catch a reused key with a different payload.

## Assumptions

You didn't specify these, so I assumed them. Each changes the design if wrong.

- **API style:** REST/JSON.
- **Store:** PostgreSQL, so unique-constraint claiming is available.
- **Mid-flight external call:** a payout rail or bank call that can't be rolled back, so the request is multi-step with recovery points.
- **Longest retry chain:** unknown. I assumed 24h. Check it against your DLQ replay and scheduled re-run windows. If any chain is longer than the replay window, a late retry becomes a new payout.
- **Other endpoints:** I covered only `/v1/transfers`. Enumerate every other state-changing endpoint (refunds, batch payouts, beneficiary creation) and apply the same contract.

## 1. How keys work

- **Header:** `Idempotency-Key`, minted by the client and never derived by the server. Maximum length is 255 characters.
- **Scope:** unique on `(account_id, idempotency_key)`. `account_id` comes from authentication, never from the body.
- **Fingerprint:** SHA-256 of the canonicalized body, stored with the key.
- **Replay window:** 24h. After expiry a reused key is treated as a brand-new request.
- **Reaper threshold:** 72h. Records stay available to humans for recovery, for example after a bad Friday deploy.
- **Stored outcomes:** both successes and failures, replayed verbatim (status, relevant headers, body).
- **Failure policy (decided, not left open):** a stored terminal result replays verbatim, including 4xx. To make a fresh attempt after a failed transfer, the client uses a new key. A transfer whose rail outcome is unknown is not "failed". It stays in-flight until the completer resolves it.

```sql
CREATE TABLE idempotency_keys (
  id                  BIGSERIAL PRIMARY KEY,
  account_id          BIGINT NOT NULL,
  idempotency_key     TEXT NOT NULL,
  request_fingerprint TEXT NOT NULL,
  locked_at           TIMESTAMPTZ,
  recovery_point      TEXT NOT NULL DEFAULT 'started',
  response_status     INT,
  response_body       JSONB,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (account_id, idempotency_key)
);
```

**Atomic claim.** Never run `SELECT` and then `INSERT`, because concurrent retries would both see "absent". Insert first and let the unique constraint pick the winner:

```sql
INSERT INTO idempotency_keys (account_id, idempotency_key, request_fingerprint, locked_at)
VALUES ($1, $2, $3, now())
ON CONFLICT (account_id, idempotency_key) DO NOTHING
RETURNING id;
```

- **A row comes back:** this request won and proceeds as a first attempt.
- **No row comes back:** read the existing record and branch on its state (section 2).
- **Same transaction:** the claim and the first business mutation, the local transfer row, commit together.
- **Not a lock:** don't use Redis `SETNX` as the claim. Without a fencing token it is unsafe.

**Multi-step phases.** Record intent before the foreign call, so a crash leaves evidence:

| Phase | Work | `recovery_point` |
|---|---|---|
| 1 (txn) | Claim the key, validate, create the transfer row with status `created` | `transfer_created` |
| *foreign call* | Submit to the payout rail. Pass the transfer ID as the rail's own reference if it supports one. | |
| 2 (txn) | Record the rail reference | `rail_submitted` |
| 3 (txn) | Store the final response | `finished` |

A retry or the completer resumes from `recovery_point`. At `rail_submitted` the money has moved, so it never submits again.

**Background jobs.**
- **Completer:** pushes abandoned in-flight keys to completion using only keys and recovery points.
- **Reaper:** deletes records past 72h and logs anything it couldn't finish for a human.

## 2. What the API returns on a duplicate

A key has three states, not two.

| Situation | Response |
|---|---|
| Key absent (the first attempt, or a retry after the network dropped before arrival) | Normal processing, `201` |
| Key complete, same fingerprint | Stored status and body verbatim, plus `Idempotent-Replayed: true`. No re-execution. |
| Key complete, different fingerprint | `409` with code `invalid_idempotent_request`. Message: "This idempotency key was already used with a different request payload. Use a new key, or resend the original payload." |
| Key in-flight (lock fresh, no stored result) | `409` with code `concurrent_idempotent_requests`, a `Retry-After` header, and "A request with this idempotency key is currently in progress. Wait and retry." |
| Key in-flight, lock expired (original crashed) | The caller takes over with a conditional `UPDATE ... WHERE locked_at < $threshold` and resumes from `recovery_point`. |
| Key older than 24h | Treated as a new request. |

- **Never run alongside:** don't let a second request through because the first "seems stuck".
- **Two codes:** the two `409`s carry distinct machine-readable codes so SDKs can handle them differently. Exact envelope and `retryable` flags belong to your error-design standard.

## 3. What we tell integrators about picking keys

> **Send an `Idempotency-Key` on every `POST /v1/transfers`. One key per *intended payout*, reused on every retry of that payout.**
>
> Choose the key by what you want to happen:
> - **Best: derive it from your own business identifier.** For example `payout-${invoiceId}` or `transfer-${batchId}-${vendorId}`. A retry then can't produce a different key. This is the default recommendation.
> - **If no stable ID exists at call time:** use a request-scoped key such as `${yourRequestId}-transfer`.
> - **If you're a stateless script:** generate one random UUID per payout and **persist it before the first send**, so it survives a restart.
>
> **Two identical payouts on the same day are fine.** If you really mean to pay the same vendor the same amount twice, give them different keys, because they are different intents. We will execute both.
>
> **Don't:**
> - Generate a new key per attempt (`Date.now()`, a fresh `randomUUID()` in the retry loop). That defeats the protection.
> - Hash the body to make the key. That reproduces the bug where genuine twins collapse into one.
> - Reuse a key across different payouts, such as `vendor-123-2026-10-03`.
>
> **Contract:**
> - **Scope:** keys are per account.
> - **Window:** replays are guaranteed for 24 hours. Finish your retries well within that. After 24 hours the same key creates a new transfer.
> - **Reuse with a changed body:** returns `409 invalid_idempotent_request`. Don't retry it. Fix the bug.
> - **Concurrent duplicate:** returns `409 concurrent_idempotent_requests`. Wait for `Retry-After` and retry with the **same** key.
> - **Failed transfer:** a stored failure replays. To try again, use a new key.
> - **Guarantee:** retries are safe within this scope and window. We don't claim "exactly-once delivery", which is impossible over a network.

**Recommended retry loop for raw-HTTP integrators:**
- **Retry only:** 429 (honoring `Retry-After`), 502, 503, 504, and connection timeouts or resets. Treat 500 with caution.
- **Never retry:** other 4xx, auth failures, and `invalid_idempotent_request`.
- **Backoff:** full jitter, `sleep = random(0, min(30s, 1s · 2^attempt))`.
- **Bounds:** at most 5 attempts and 60s total. Set one overall deadline with per-attempt timeouts inside it.
- **Timeout per attempt:** about 2-3x your measured p99.
- **Logging:** log every retry (attempt, error, next wait).
- **Libraries:** use your language's library (tenacity, Resilience4j) rather than hand-rolled math.
- **Never retry a read timeout on this POST without a key in place.**

## 4. Rollout, since "clients change nothing" isn't possible

1. **Find the 43.** Identify which accounts produced last month's duplicates. They are the first customers to onboard to keys. Separately, reconcile those payouts. That is a ledger issue, not part of this design.
2. **Ship the server side** as optional, with the claim, fingerprint, and replay behavior above.
3. **Ship SDK defaults:**
   - Retries on, with full jitter and the bounds above.
   - **Auto-generated key per call, reused across that call's retries.**
   - A per-request key override.
   - Document these defaults in the README as precisely as the HTTP contract.
   - Most integrators will then get protection with no code change.
4. **Measure keyless adoption.** During the transition, log keyless transfer requests per account, plus same-account same-fingerprint repeats within a short window. This is **observe-and-flag only, never block**, so it can't recreate the dropped-twin bug.
5. **Enforce.** Make the header required on `/v1/transfers` and return `400` when it is missing. Announce a date in the changelog.

## 5. Acceptance tests

- **Concurrency gate:** fire 50 concurrent identical requests with one key. Exactly one transfer and one rail call occur, and the other 49 get `409 concurrent_idempotent_requests` or the stored replay.
- **Twin test:** two identical bodies with different keys both execute.
- **Crash gate:** kill the server between phases 2 and 3, then retry. The request resumes with zero repeated rail calls.
- **Mismatch test:** the same key with a different body returns `409 invalid_idempotent_request`.
- **Tenant isolation:** the same key string from two accounts never collides.
- **Production alarm:** the duplicate-payout rate within the documented scope and window should be zero. Any non-zero value means a gate regressed.
- **Orphaned keys:** track the claimed-but-never-completed rate and set the baseline from your first month.

## Open questions that could change this

1. What is the longest retry chain (DLQ replays, scheduled re-runs)? It may need a window longer than 24h.
2. Does the payout rail accept its own idempotency reference? If so, pass the transfer ID through.
3. Do you have an effort ceiling on the claim mechanism, such as a ship date that rules out a migration? The unique-constraint default is the cheapest option.
4. Which other endpoints besides `/v1/transfers` change state?