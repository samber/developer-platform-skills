# Cratebase idempotency pass

## Verdict on the plan

⚠️ Keys on the two POSTs only leaves two gaps. The skill says to verify claimed idempotency rather than trust the method (§1), and two of your endpoints fail that check.

| Endpoint | Method says | Actual behavior | Retry-safe? | Action |
|---|---|---|---|---|
| `GET /v2/orders` | idempotent | read-only | ✅ | None |
| `POST /v2/orders` | not idempotent | creates an order | ❌ | Accept `Idempotency-Key` |
| `POST /v2/refunds` | not idempotent | creates a refund | ❌ | Accept `Idempotency-Key`. Highest risk, see below. |
| `PUT /v2/orders/{id}/notes` | idempotent | appends a note on every call | ❌ | Accept `Idempotency-Key` (or redesign, see below) |
| `DELETE /v2/credits/{id}` | idempotent | decrements the balance on every call | ❌ | Accept `Idempotency-Key` (or redesign, see below) |

A retry after a dropped connection duplicates a note or double-decrements a credit balance. The credit case is a money bug.

The key header works on any method, so adding it to PUT and DELETE costs nothing structurally. All four write endpoints get the same contract.

**Optional redesigns that make the method claim true:**
- **Notes:** let the client supply the note ID (`PUT /v2/orders/{id}/notes/{note_id}`), so a repeat call overwrites instead of appending. A key is still the cheaper fix this quarter.
- **Credits:** make delete state-based. The first call marks the credit consumed and decrements; later calls are no-ops that return the same result. Pair it with a key anyway, because the response on a retry still has to match the original.

## Assumptions

I could not ask the skill's clarifying questions interactively. Each assumption below is a place to correct me:
- **Paradigm:** REST only.
- **Storage:** relational (Postgres-class) with unique constraints.
- **Refunds:** assumed to call an external payment processor mid-request. Please confirm.
- **Retry chains:** nothing longer than 24 hours (no DLQ replays, no scheduled re-runs). Please confirm.
- **SDKs:** not known. The SDK defaults below apply only if you ship them.
- **Deadline:** nothing that rules out a schema migration.

## Server design

### Key contract
- **Who mints it:** the client mints the key. The server never derives it from the payload, because two identical requests may both be intended.
- **Scope:** `(account_id, idempotency_key)`, never global.
- **Format:** the header is `Idempotency-Key`. Cap it at 255 characters and recommend a UUIDv4.
- **Payload guard:** store a request fingerprint, such as a checksum of the method, path and body. Reject a reused key with a different fingerprint with `409 invalid_idempotent_request`.
- **Failures:** store failures as well as successes, and replay the stored response verbatim. This is the Stripe v1 model. Decide it now and document it.

### Storage and TTL
- **Replay window:** 24h. After expiry, a reused key is a brand-new request.
- **Reaper threshold:** 72h, so a bad Friday deploy's failed requests survive the weekend.
- **Check before launch:** the 24h window is only safe if no retry chain you offer exceeds it. Enterprise customers often have queue replays, so check this explicitly.
- **Stored response:** keep status, the headers that matter, and the full body.

### Atomic claim (default rung: unique constraint)
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

INSERT INTO idempotency_keys (account_id, idempotency_key, request_fingerprint, locked_at)
VALUES ($1, $2, $3, now())
ON CONFLICT (account_id, idempotency_key) DO NOTHING
RETURNING id;
```
- **Winner:** a returned row means this caller proceeds.
- **Loser:** no row means the key exists. Branch on its state.
- **No check-then-insert:** that is a TOCTOU race.
- **One transaction:** the claim and the business mutation commit together. For orders, notes and credits, the claim, the mutation and the stored response share one transaction.
- **No bare Redis `SETNX`:** it has no fencing token.

### Three-state responses

| State | Response |
|---|---|
| Absent | Proceed as a first attempt. |
| In-flight (`locked_at` recent, no response stored) | `409 concurrent_idempotent_requests`, "wait and retry". Never let a second caller through. |
| In-flight, lock expired | Take over with an atomic conditional `UPDATE ... WHERE locked_at < $threshold`. Resume from `recovery_point`. |
| Complete, same fingerprint | Replay the stored status and body verbatim. |
| Complete, different fingerprint | `409 invalid_idempotent_request`. |

The two 409s carry distinct machine-readable codes. Error envelope, `retryable` flag and `Retry-After` belong to `api-error-design`.

### Refunds need recovery points
If refunds call a payment processor, one transaction cannot cover them. Split into phases:
1. **Phase 1 (txn):** claim the key, validate, and create a local refund row in state `pending`. Set `recovery_point = refund_created`.
2. **Processor call:** pass the processor its own idempotency key derived from the refund ID. Record intent before calling out.
3. **Phase 2 (txn):** record the processor refund ID. Set `recovery_point = processor_recorded`.
4. **Phase 3 (txn):** store the final response. Set `recovery_point = finished`.

A retry at `processor_recorded` must never refund again. Run a **completer** for abandoned in-flight requests and a **reaper** for expired keys. The reaper logs anything it could not finish for a human.

Orders, notes and credit decrements are single-database operations and need only the one-transaction rule.

## Client retry guidance and SDK defaults

- **Retry allowlist:** 429 (honor `Retry-After`), 502, 503, 504, connection timeouts and resets. Treat 500 cautiously. Never retry other 4xx or auth failures.
- **Read timeouts:** never retry a read timeout on a write without a key already attached.
- **Backoff:** full jitter, `sleep = random(0, min(cap, base * 2^attempt))`. Use base 1s and cap 30s.
- **Bounds:** bound attempts and total duration. A sensible default is 5 attempts and 60s overall.
- **Deadline:** one overall deadline at the top, with per-attempt timeouts inside it. Set single timeouts at 2-3x measured p99.
- **Logging:** log every retry with attempt, error and next wait.
- **Retry budget:** add a fleet-wide cap, for example stop retrying when retries exceed ~20% of traffic over a 1-minute window.
- **Libraries:** point integrators at tenacity or Resilience4j (or equivalent) before hand-rolled math.
- **If you ship SDKs:**
  - Retries on by default, with jitter and a bounded attempt count (AWS defaults to 3 total).
  - Auto-generate a key for the four write endpoints and reuse it across retries of one call.
  - Expose per-request key override, attempt count and max delay.
  - Document the defaults in the README.

## Integrator docs checklist

Because no standard defines these semantics (the IETF draft expired unratified in April 2026), your docs are the only normative source.

**Scope and header**
- [ ] List the endpoints that accept the key: `POST /v2/orders`, `POST /v2/refunds`, `PUT /v2/orders/{id}/notes`, `DELETE /v2/credits/{id}`.
- [ ] State that `GET` needs no key.
- [ ] Give the header name `Idempotency-Key` and the 255-character cap.
- [ ] Document the derivation ranking, with the default first:
  1. Event-derived, for example `refund-${orderId}-${reasonId}`.
  2. Request-scoped.
  3. A random UUID generated once and reused.
- [ ] Show the anti-pattern in a "never do this" box: a new value per attempt (`Date.now()`, a fresh `randomUUID()`).
- [ ] For critical calls, advise writing the intent and key to a durable queue before the first attempt.

**Semantics**
- [ ] State the scoping: keys are per account.
- [ ] Give the replay window as a concrete number (24h) and say what happens after it: the key is treated as a new request.
- [ ] Tell integrators to finish retry logic well inside the window.
- [ ] Document the payload-mismatch conflict: `409 invalid_idempotent_request`, with example JSON and the fix (new key, or resend the original payload).
- [ ] Document the in-flight conflict: `409 concurrent_idempotent_requests`, with example JSON and the advice to wait and retry.
- [ ] State that stored failures, including 500s, replay verbatim, and that the integrator needs a new key to re-attempt after a failure.
- [ ] State that a replayed response is identical to the original.

**Retry loop**
- [ ] Publish the retryable-status allowlist and the never-retry list.
- [ ] Provide a worked loop with numbers: `1s → 2s → 4s → 8s`, cap 30s, full jitter, 5 attempts, 60s overall deadline.
- [ ] Explain `Retry-After` handling on 429.
- [ ] Link the recommended retry libraries.
- [ ] If SDKs exist: list their defaults and which operations get automatic keys.

**Wording**
- [ ] Never write "exactly-once". Write instead: "Retries are safe within the documented key scope and window."
- [ ] Check that marketing and sales materials do not already claim exactly-once.

**Endpoint-specific notes**
- [ ] Notes: explain that a repeated call with the same key returns the original note, not a second one.
- [ ] Credits: explain that a repeated delete with the same key does not decrement twice.
- [ ] Refunds: explain that the same key never produces a second refund.

## Launch gates

1. **Concurrency gate (all four endpoints):** fire N identical concurrent requests with one key. Exactly one side effect executes. The other N-1 get the in-flight 409 or the stored replay. This is binary pass or fail.
2. **Crash-recovery gate (refunds):** kill the server between phases, then retry. The request resumes from its recovery point with zero repeated processor calls.
3. **Mismatch gate:** the same key with a different body returns `invalid_idempotent_request`.
4. **Post-launch alarms:** track duplicate side-effect rate, which should be zero within scope and window, and orphaned-key rate. Set the orphan baseline from your first month.

## Open items to confirm

1. Do refunds call an external processor?
2. What is the longest retry chain you expect from enterprise customers? It could push the 24h replay window higher.
3. Do you ship SDKs, or is this raw HTTP only?
4. What storage backs the key table? Anything other than a relational store with unique constraints changes the claim mechanism.
5. Note and credit endpoints: key only, or redesign as above?