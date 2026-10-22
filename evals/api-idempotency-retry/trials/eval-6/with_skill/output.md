# Quotanet SDK v2 retry defaults: review and recommendation

**Verdict:** don't ship the proposal. All three settings run against fleet-scale behavior, and the three failures compound. Below are the defaults I'd ship, how they hold up for 200-instance fleets, and what has to be true on the server first.

## What's wrong with the proposal

| Proposal | Problem | Why it matters at 200 instances |
|---|---|---|
| Retries off by default | Most callers never read past install. The defaults are the contract. Callers who need resilience write their own raw loops, usually without jitter, without key reuse and without a cap. | Hand-rolled loops are where synchronized retry storms and duplicates come from. The safe path should be the zero-config path. |
| Up to 10 attempts | AWS's default is 3 total attempts. 10 turns every failing call into up to 10x load. | One brownout becomes 200 instances all multiplying traffic against an already struggling service. Per-caller caps can't see this. |
| Fresh 30s timeout per attempt | The caller's real wait becomes 10 × 30s = 300s plus sleeps. | Each instance pins connections and threads for minutes. A 30s timeout is also not tied to measured p99. The target is 2-3x p99. |
| (Missing) No idempotency keys | Retries on POST without a key reuse the same non-idempotent request. | This is where duplicate writes come from. The SDK can't be safe by default without keys. |
| (Missing) No fleet-wide retry budget | Opt-in plus 10 attempts leaves nothing to bound aggregate retry load. | Each instance looks reasonable alone. The fleet amplifies. |

"Off by default" doesn't fix the safety problem. It moves it to code you don't control.

## Defaults to ship (identical in Python and Node)

| Setting | Default | Notes |
|---|---|---|
| Retries | **ON** | `max_retries=0` disables. Per-request override. |
| Max attempts | **3 total** (initial + 2 retries) | Matches the AWS anchor. Configurable, hard ceiling of 5. |
| Backoff | **Full jitter**: `sleep = random(0, min(cap, base * 2^attempt))`, `base=1s`, `cap=30s` | Not decorrelated, not equal jitter, never no jitter. Offer decorrelated jitter as an opt-in for latency-critical calls only. |
| `Retry-After` | Honored on 429/503, clamped to the remaining deadline | Beats the computed backoff when larger. |
| Overall deadline | **One per logical call: 40s** | Set once at the top, never reset per attempt. |
| Per-attempt timeout | **min(10s, remaining deadline)** | Placeholder. Set it to 2-3x your measured p99 for the slowest retryable endpoint, then adjust the overall deadline to fit about 3 attempts. |
| Retry budget | **Token bucket per client process**, AWS-style: 500 capacity, 14 tokens per transient-error retry, 5 per throttle retry, +1 per success. Empty bucket means fail fast. | See the fleet math below. |
| Idempotency keys | **SDK auto-generates a key for every POST and other unsafe call** | Minted once before attempt 1 and reused on every attempt. Caller can override. Exposed on the response and error objects so a manual retry can reuse it. |
| Retry logging | Every retry: attempt, error, next wait | Silent retry loops hide outages. |

### What gets retried

- **Retry:** 429 (honoring `Retry-After`), 502, 503, 504, connection timeouts and resets.
- **Retry with backoff as a special case:** `409 concurrent_idempotent_requests`. It means in flight, wait and retry.
- **Never retry:** other 4xx, auth failures, `409 invalid_idempotent_request` (payload mismatch, a client bug), and exceptions that are bugs.
- **500:** don't retry by default. If stored failures replay verbatim (Stripe v1 semantics), retrying a stored 500 with the same key just returns the same 500. Decide that explicitly (see the server prerequisites). Re-attempt semantics (v2) would make 500s retryable.
- **Read timeout on an unsafe call without a key:** never retry. With auto-keys this case shouldn't occur from the SDK, but it must hold for any path where the key is missing.

## Why this holds up at 200 instances

- **Amplification is bounded per call:** at most 3 requests instead of 10. Worst-case caller wait is capped at 40s instead of about 300s.
- **Fleet load is bounded by the budget.** Every instance's retries are capped to a share of its own traffic, so the aggregate retry load is also capped. The proposal had no such bound. Per-caller attempt caps alone cannot prevent amplification.
- **Jitter spreads the fleet.** 200 instances that failed together don't retry at the same instants.
- **Keys make retries safe.** A retry after a dropped connection replays or conflicts instead of duplicating.

## Server prerequisites (gate: do not flip the default before these hold)

The retry-by-default SDK is only safe if the server half exists. A key that is accepted but not honored is worse than no key.

1. **Atomic claim:** unique constraint on `(account_id, idempotency_key)`, with the claim and the business mutation in one transaction. Never check-then-insert. A bare Redis `SETNX` doesn't count.
2. **Three-state keys:** absent, in-flight, complete. Use distinct 409 codes: `invalid_idempotent_request` for payload mismatch and `concurrent_idempotent_requests` for in flight.
3. **Payload fingerprint** stored beside the key. The same key with a different body is rejected.
4. **Decision on stored failures:** replay verbatim (v1) or re-attempt (v2). This decides whether 500 is retryable.
5. **Replay window** of 24h (reaper around 72h), set from your longest real retry chain. If DLQ or scheduled re-runs exceed 24h, extend it. Reuse after expiry is a new request.
6. **Gates before release:**
   - Concurrency gate: fire N concurrent identical requests with one key. Exactly one side effect executes.
   - Crash-recovery gate, if any endpoint calls an external non-rollbackable system (a charge, an email): kill the server between phases, retry, and confirm zero repeated external calls.

If the server half can't be ready for the v2 ship date, ship the SDK with retries on for idempotent methods and pre-send connection failures only, keep POST retries off until the gates pass, and say so in the changelog. Don't ship retries-on with POST and no key support.

## Open inputs that could change the numbers

- **Measured p99** for your slowest retryable endpoint. It sets the per-attempt timeout (the 10s above is a placeholder).
- **Longest retry chain** (DLQ replays, scheduled re-runs). It sets the replay window.
- **Key store** (relational or KV). It sets the claim mechanism: unique constraint, or conditional-write OCC on a KV store.
- **Rate-limit policy:** whether SDK retries count against customer quota. That is `api-rate-limit-policy` territory, but decide it before launch. Retries that burn quota can turn a blip into a customer lockout.

## Docs to publish with v2

- The default table above, in each SDK README, with the same precision as the raw-HTTP contract.
- Which operations get automatic keys.
- Key scoping, the 24h window, both 409 codes, and whether failures replay.
- A worked retry loop with real numbers, for raw-HTTP integrators. Point Python callers to `tenacity` (`wait_exponential_jitter`, bounded by `stop_after_attempt | stop_after_delay`).
- No "exactly-once" wording anywhere. Write what is true: retries are safe within the documented key scope and window.

The skill's references were the source for these numbers (AWS default of 3 attempts and token costs, Brooker's jitter analysis, deadline propagation). I haven't verified them independently, and I haven't seen your server code.