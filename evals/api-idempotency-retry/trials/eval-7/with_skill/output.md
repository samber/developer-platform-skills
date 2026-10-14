# Vaultberry `POST /v1/subscriptions`: duplicate-charge fix and landing-page copy review

I followed `api-idempotency-retry` and its three references. I haven't seen your handler code, so I made some assumptions, listed at the end. Part 1 is the design fix and Part 2 is the copy verdict.

## Part 1: The design fix

### Root cause

The idempotency key and the subscription row lived in the same transaction as the PSP call, and a card charge can't be rolled back.

1. The charge succeeded at the PSP.
2. The process crashed before commit, so the transaction rolled back.
3. The rollback erased the key claim, the subscription row and every trace of the charge.
4. The retry saw an absent key and ran as a first attempt, so the customer was charged again.

The skill's rule is that the claim and the business mutation commit as one unit. That rule holds for each local phase. It does not mean the whole request, including a foreign call, goes in one transaction. A claim that rolls back together with the effect it is meant to guard gives you no protection.

### New design: three atomic phases around each foreign call

Each phase commits before the next external call. The key row stores a `recovery_point`.

```sql
CREATE TABLE idempotency_keys (
  id                  BIGSERIAL PRIMARY KEY,
  account_id          BIGINT NOT NULL,
  idempotency_key     TEXT NOT NULL,              -- client-minted, max 255 chars
  request_fingerprint TEXT NOT NULL,              -- payload checksum
  locked_at           TIMESTAMPTZ,                -- non-NULL = in flight
  recovery_point      TEXT NOT NULL DEFAULT 'started',
  subscription_id     BIGINT,
  psp_idempotency_key TEXT,                       -- persisted BEFORE the PSP call
  psp_charge_id       TEXT,
  response_status     INT,
  response_body       JSONB,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (account_id, idempotency_key)            -- the atomic claim
);
```

| Phase | Transaction contents | `recovery_point` after commit |
|---|---|---|
| 1 | Claim the key with `INSERT ... ON CONFLICT DO NOTHING RETURNING id`. Store the fingerprint. Create the subscription row as `pending_payment`. Generate and store `psp_idempotency_key`, derived deterministically, e.g. `sub-charge:{account_id}:{key}`. | `subscription_created` |
| Foreign call 1 | Charge the PSP, passing the stored `psp_idempotency_key`. | |
| 2 | Store `psp_charge_id`. Set the subscription to `active`. Insert the receipt into a transactional outbox, in the same transaction. | `charge_recorded` |
| Foreign call 2 | A worker drains the outbox and sends the email, with a dedupe key if the provider supports one. | |
| 3 | Store `response_status` and `response_body`. Clear `locked_at`. | `finished` |

Four design rules follow:

- **Intent before effect.** The PSP idempotency key is committed in phase 1, before the PSP is called. A crash between the charge and phase 2 then leaves evidence on disk, and the retry reuses the same PSP key.
- **Two layers of dedupe.** Our key table collapses duplicate client requests. The PSP key collapses the one window we can't close ourselves, which is a crash after the PSP accepted the charge but before we recorded it. Without the PSP key, that window always produces a double charge.
- **Local invariant as a last guard.** Add a unique index on `charges(subscription_id)`, or an equivalent constraint on `psp_charge_id`. A bug in the resume logic then fails loudly instead of billing twice.
- **The email leaves the request path.** An outbox row committed with the charge record means a mail-provider outage or crash can't trigger a re-charge, and the API response isn't blocked on the mailer. A rare duplicate receipt is acceptable. A duplicate charge is not.

### What a retry does at each crash point

| Crash point | Key state on retry | Behavior |
|---|---|---|
| Before phase 1 commits | Absent | The retry runs as a first attempt and wins the claim. |
| After phase 1, before or during the PSP call | In flight, `recovery_point = subscription_created` | If the lock is fresh, return `409 concurrent_idempotent_requests`. If the lock expired, take over and call the PSP with the stored PSP key. The PSP returns either the original charge or a new one, never two. |
| After the PSP charged, before phase 2 (last week's incident) | Same as above | On takeover, call the PSP with the same key and receive the original charge. Record it and continue. Zero duplicate charges. |
| After phase 2, before the email is sent | In flight, `recovery_point = charge_recorded` | Skip the charge. The outbox worker sends the email. |
| After phase 3 | Complete | Replay the stored response verbatim, with no re-execution. |

### Claim and recovery mechanics

- **Claim mechanism.**
  - Default to the unique constraint on `(account_id, idempotency_key)`, with the loser decided by the `INSERT` failure.
  - Takeover is one conditional update: `UPDATE ... SET locked_at = now() WHERE locked_at < now() - $lock_timeout`.
  - Your request spans foreign state mutations, which is the skill's trigger for promoting row lock plus SERIALIZABLE. If your team already runs SERIALIZABLE workloads, that is the richer option. It is not required to fix this bug.
- **Lock timeout.** Set it above your PSP client timeout plus a margin, so a live-but-slow original isn't taken over.
- **Safety net against a paused original.** A taken-over original that wakes up and charges again is deduped by the PSP key. This is the fencing guarantee the claim alone doesn't give you.
- **PSP retention window.** If the PSP's idempotency retention is shorter than our resume horizon, the resume path must look up the charge at the PSP by `subscription_id` metadata before it calls the charge endpoint again. After that window, never blindly re-charge.
- **Stored failures.**
  - A terminal card decline is stored and replayed verbatim, so the retry gets the same decline. The client needs a new key to attempt a new payment.
  - A transient error, such as a PSP timeout or a 5xx, is not stored as terminal. The key stays in flight and resumes.
  - Document this choice. The skill flags an undecided answer as a design gap.
- **Payload mismatch.** The same key with a different body returns `409 invalid_idempotent_request`. The in-flight conflict uses the distinct code `concurrent_idempotent_requests`.
- **Background jobs.**
  - A **completer** finds keys with an expired lock and a `recovery_point` that is not `finished`, and pushes them through using only the key table.
  - A **reaper** deletes records past the reaper threshold and logs anything it couldn't finish for a human.
- **Retention.** Use a replay window of about 24 hours and a reaper threshold of about 72 hours. Raise the replay window if your longest retry chain is longer than 24 hours (a DLQ replay, for example).

### Client side

- **Key derivation.** Recommend event-derived keys, e.g. `subscribe-{accountId}-{planId}-{checkoutSessionId}`. If no stable identifier exists, use a request-scoped key, then a UUID reused across retries. Document a fresh key per attempt as the anti-pattern.
- **Retry loop.** Use full jitter, `sleep = random(0, min(cap, base * 2^attempt))`, with a worked example such as 1s, 2s, 4s, 8s capped at 30s.
- **What to retry.** Retry 429 (honoring `Retry-After`), 502, 503, 504, and connection timeouts or resets. Retry 500 cautiously. Never retry other 4xx errors.
- **Limits.** Bound both attempt count and total duration. Use one overall deadline, not a fresh timeout per attempt.
- **SDKs.** Default retries on, with an attempt cap of about 3, and auto-generate a key for this endpoint.

### Verification before you call it fixed

- **Concurrency gate.** Fire N identical concurrent requests with one key. Exactly one charge and one subscription must exist. The other N-1 get a 409 or the stored replay.
- **Crash-recovery gate.** Kill the process at each boundary in the table above. The PSP test double must record one charge per key. The key crash-point is after the PSP charge and before phase 2, which is last week's incident.
- **Mutation check.** Temporarily remove the stored `psp_idempotency_key` and confirm the crash test fails. A test that can't fail proves nothing.
- **Alarm.** Duplicate side-effect rate is zero by design within the key scope and window. Alert on any non-zero value. Track the orphaned-key rate and set its baseline from your first month of data.

### Clean up the incident

- Query the PSP for subscriptions with more than one charge in the last week, not only the one reported, and refund the duplicates.
- Add the unique-charge guard above so the same class of bug fails loudly next time.

## Part 2: Copy review

> "guaranteed exactly-once delivery, powered by idempotency keys"

**Verdict: not approved. Engineering can't sign off on this wording.**

- **"Exactly-once delivery" is provably false.** Over an unreliable network you get at-least-once delivery, and duplicates are collapsed on top of it. What idempotency keys give you is effectively-once execution, within the scope where you implement it.
- **"Guaranteed" overreaches.** The guarantee holds only inside the documented conditions: the endpoint accepts the key, the same account sends the same key and payload, and the retry arrives inside the replay window. After the window, a reused key is a new request.
- **It contradicts the design above.** Receipt emails are at-least-once, so a duplicate email is possible. "Exactly-once" would be false on the same page that describes this endpoint.
- **"Delivery" names the wrong thing.** It sounds like messages or webhooks. This is about safe retries of API writes.

**Approved replacements** (pick one):

- Headline: "Retry safely. Send an `Idempotency-Key` with any write, and a retry returns the original result instead of repeating it."
- Alternative: "Safe retries on every write endpoint, built on idempotency keys."
- Fine print: "Keys are scoped per account and stored for 24 hours. A retry with the same key and the same payload returns the original response. After 24 hours, the key is treated as a new request."

If marketing wants a stronger line, use "Charged once per request, even when your client retries." That is true under the same conditions, which the fine print states.

Before publishing, confirm the page links to the real contract. It should list which endpoints accept the key, the 24-hour window, the two 409 codes and the retry schedule. Also search the site and the sales decks for "exactly-once" and correct every occurrence.

## Assumptions and open questions

I couldn't ask the skill's clarifying questions, so I assumed the following. Each one would change the design if it's wrong.

1. **REST only.** gRPC would add native deadline propagation.
2. **Relational DB with unique constraints and transactions.** You already use transactions, so this seems safe. A conditional-write KV store would change the claim mechanism.
3. **PSP idempotency support.** I assumed the PSP honors an idempotency key on charge creation, as Stripe-style PSPs do. If it doesn't, the post-charge crash window needs lookup-by-metadata reconciliation instead.
4. **Mail provider dedupe.** I assumed the mail provider may not dedupe. I designed for at-least-once email.
5. **Longest retry chain, ship date and effort ceiling are unknown.** Please check for DLQ replays or scheduled re-runs longer than 24 hours. A hard ship date favors the unique-constraint design. A mandate for every future endpoint favors investing in SERIALIZABLE and the completer.

Please send the handler and the table schema if you want a line-level review.