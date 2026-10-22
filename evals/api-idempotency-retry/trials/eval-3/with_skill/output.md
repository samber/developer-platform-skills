# Parcelry shipping API: fixing duplicate labels on client retry

**Do not ship the 10-second rule, and do not send the email as the fix.** Fix the server, then improve the docs and SDK defaults.

Your client did what a correct client does. The bug is that your key store has only two states, seen and not seen. A key needs three: **absent**, **in-flight** and **complete**.

I haven't seen your schema, store or carrier contract, so I made the assumptions below. Each one changes a specific step.

## Assumptions

| # | Assumption | What changes if it's wrong |
|---|---|---|
| 1 | REST API, `POST /shipments` or similar | gRPC would carry the deadline natively |
| 2 | Postgres or another relational store | A KV store means conditional-write OCC instead of a unique constraint |
| 3 | The carrier call buys a label and is charged, and can't be rolled back | If it were rollbackable, the request could be one transaction |
| 4 | SDKs plus raw-HTTP integrators | Without SDKs, the docs carry everything |
| 5 | Longest retry chain is unknown to me | If a DLQ or re-run window exceeds 24h, lengthen the replay window |

Please confirm 2 and 5. Assumption 3 is the one that drives the design.

## Why the engineer's proposal fails

1. **It reproduces your incident.** The carrier call took 40s, so at 10s the original is alive and healthy. The rule would let the retry through while the first attempt is still running.
2. **No timeout guess can fix it.** Any threshold shorter than the worst-case carrier latency lets a live request through. A longer one just delays the same bug. "Seems stuck" and "is slow" look identical from the outside.
3. **It breaks a hard rule of the design.** The second caller must never be let through because the first one "seems stuck." Both the conflict response and the replay response are deliberate and distinct.
4. **The carrier charge can't be undone.** A second execution means a second label and a second charge.

## What to build

### 1. Claim the key before doing any work

Use a unique constraint on `(account_id, idempotency_key)`. Insert first and let the database pick the winner:

```sql
INSERT INTO idempotency_keys
  (account_id, idempotency_key, request_fingerprint, locked_at)
VALUES ($1, $2, $3, now())
ON CONFLICT (account_id, idempotency_key) DO NOTHING
RETURNING id;
```

- A returned row means this caller won the claim and runs the flow.
- No row means the key exists, so read its state and branch.
- Never use `SELECT` then `INSERT`. Concurrent retries would both see "absent."
- The claim and the first local mutation commit together in one transaction.

### 2. Store the in-flight state, with a fingerprint

Add `locked_at`, `recovery_point`, `request_fingerprint`, `response_status` and `response_body` to the key row.

| State | Condition | Response |
|---|---|---|
| Complete | `response_status` set, fingerprint matches | Replay the stored status and body verbatim |
| Complete | Fingerprint differs | `409 invalid_idempotent_request` (client bug) |
| In-flight | `locked_at` recent, no response | `409 concurrent_idempotent_requests`, "wait and retry" |
| In-flight, lock expired | `locked_at` older than the lock timeout | A takeover caller resumes from `recovery_point`, never from the start |

- Use two distinct machine-readable codes for the two 409s. The shape of the error response belongs to `api-error-design`.
- Store failures as well as successes, and decide explicitly whether a stored failure replays verbatim or may be re-attempted.
- This is the incident's fix. The retry at 10s hits an in-flight key and gets a 409 instead of a second label.

### 3. Promote the row lock and SERIALIZABLE claim, because the carrier call has side effects

The default claim is the unique constraint. The skill promotes the richer lifecycle (`locked_at` plus recovery points) when a request mutates foreign state, and the carrier does. Check how fluent your team is with SERIALIZABLE before you commit to it. A hard ship date or a ban on schema migrations may force you to keep the plain constraint and add `locked_at` and `recovery_point` columns only.

### 4. Split the flow into phases around the carrier call

```
Phase 1 (txn): claim key, validate, create shipment row, record intent  -> 'shipment_created'
  -- foreign mutation: buy the label from the carrier --
Phase 2 (txn): record carrier label ID and charge reference             -> 'label_purchased'
Phase 3 (txn): store the final response                                 -> 'finished'
```

- Record **intent before** calling the carrier. A crash between the call and the response then leaves evidence instead of a silent duplicate.
- On resume at `shipment_created`, first look up whether the carrier already issued a label for your shipment reference. Only buy if none exists.
- If the carrier accepts its own idempotency or reference key, pass your key through.
- At `label_purchased`, never buy again. Continue to the next phase.

### 5. Set the lock timeout from the worst case, not from a guess

- Put a hard server-side timeout on the carrier call.
- Set the lock timeout above that timeout plus a margin.
- A takeover is allowed only after that point, and only through an atomic `UPDATE ... SET locked_at = now() WHERE locked_at < $threshold`.
- This is the safe version of the engineer's idea: take over from a *crashed* worker, resuming from a recovery point.

### 6. Run recovery as background jobs

- A **completer** pushes abandoned in-flight requests to completion using only keys and recovery points.
- A **reaper** deletes records past the retention threshold and logs anything it couldn't finish for a human.

### 7. Set retention

- Replay window is about 24h, longer if your longest retry chain is longer. Set it from the retry chain, not from storage cost.
- Reaper threshold is about 72h.
- After expiry, a reused key is a brand-new request.

## The client side

The email to clients should become a docs and SDK change.

- **The client's 10s timeout was reasonable.** What is unreasonable is a 40s carrier call behind a synchronous endpoint. Two options:
  - Return `202` plus a status URL for label purchase, which suits a 40s effect.
  - Or document the real p99 so clients set timeouts at 2-3x p99.
- **Publish the full contract:** header name, max key length, scope, replay window as a number, both 409 codes, whether stored failures replay, and a worked retry loop.
- **Recommended key derivation:** event-derived first (for example `shipment-${orderId}`), then request-scoped, then a UUID generated once and reused. Document a fresh key per attempt as the anti-pattern.
- **Backoff:** full jitter, `random(0, min(cap, base * 2^attempt))`. Bound both attempts and total duration, and propagate one overall deadline.
- **Retry allowlist:** 429 (honoring `Retry-After`), 502, 503, 504, and timeouts. Don't blanket-retry 500s or 4xx errors.
- **SDK defaults:** retries on, bounded attempts (AWS uses 3 total), and auto-generated keys for unsafe operations. Most callers never read the docs, so these defaults are the real contract.
- **If PM still wants to contact clients,** send them the new contract and a note that retries are now safe. Don't ask them to stop retrying.
- Don't write "exactly-once." Write that retries are safe within the documented key scope and window.

## Cleaning up what already happened

- Find existing duplicate labels, then void the second label and refund the carrier charge where the carrier allows it.
- Do this before launch. Otherwise the duplicate rate stays hidden.

## Gates before you call it done

1. **Concurrency gate:** fire N identical concurrent requests with one key. Exactly one carrier call must happen. The other N-1 get the in-flight 409 or the stored replay.
2. **Slow-carrier gate:** make the carrier take 40s, retry at 10s, and assert one label.
3. **Crash-recovery gate:** kill the server after `label_purchased` and retry. It must resume with zero repeated carrier calls.
4. **Production alarm:** the duplicate side-effect rate within the documented scope and window should be zero. Treat any non-zero value as a regression, not a tuning target.
5. **Orphaned-key rate:** set a baseline from your first month and watch the trend.

## Order of work

1. The three-state claim, plus a hard carrier timeout and a lock timeout above it.
2. Phased flow with intent recorded and carrier lookup before any re-buy.
3. Gates 1 to 3 passing.
4. Completer and reaper.
5. Docs, SDK defaults and the client communication.
6. Duplicate cleanup.