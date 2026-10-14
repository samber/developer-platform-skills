# Quotanet v2 SDK retry and timeout defaults

**Verdict:** the proposal gets all three numbers wrong for 200-instance fleets. I'd ship retries on, 3 total attempts, and an overall deadline, plus a retry budget and jitter, which the proposal lacks.

## Problems with the proposal

1. **Retries off by default.** Most integrators never opt in, so every transient 503, connection reset or 429 reaches their users. Off-by-default does not make fleets safer. Retry storms come from unbounded or unjittered retries, not from retries being on. The common practice among comparable SDKs (Stripe, OpenAI, Anthropic, AWS) is on by default with a small count.
2. **Up to 10 attempts.** In an outage or throttling event, a 200-instance fleet sends up to 10× its normal load into a service that is already struggling. That 10× multiplies again if the integrator's own code also retries. Attempts 4 to 10 rarely rescue a request. They mostly add load while the service recovers.
3. **A fresh 30 s timeout per attempt.** The worst case is 10 × 30 s plus backoff, which is over 5 minutes per call. Each hung call holds a thread, a socket and a pool slot, so a degraded Quotanet can exhaust the caller's connection pool and take down the caller's own service.
4. **Missing pieces.** The proposal has no jitter, no `Retry-After` handling, no idempotency rule for writes, no retry budget and no cancellation rule. For fleets, the missing jitter and budget matter most. Synchronized retries from 200 instances arrive as waves.

## Defaults I'd ship

| Setting | Default | Why |
|---|---|---|
| `max_retries` / `maxRetries` | **2** (3 total attempts) | Catches nearly all transient faults. Caps amplification at 3×. `0` disables. |
| Connect timeout | **5 s** | A connect that takes longer than 5 s is almost always a dead host. Fail fast and retry elsewhere. |
| Per-attempt timeout | **30 s** | Keeps the team's proposed value, and a single-attempt call behaves the same as before. See the caveat below. |
| **Overall deadline** | **60 s** | Bounds the total across attempts and sleeps. Each attempt gets `min(30 s, time left)`. |
| Backoff | **Exponential, full jitter**: `sleep = random(0, min(8 s, 0.5 s × 2^n))` | Jitter is what stops 200 instances from retrying in lockstep. |
| `Retry-After` | **Honored** | Use `max(jittered backoff, Retry-After)`. If it exceeds the time left in the deadline, fail immediately instead of sleeping. |
| Retry budget | **10% per client process** | A token bucket where each success earns 0.1 retry tokens, with a small floor of about 10 so cold clients can still retry. Once empty, errors surface without retrying. This bounds the fleet's extra load to about 1.1× even in a full outage. |

**What gets retried:**
- Connection errors and timeouts before a response arrives, plus 408, 429, 502, 503 and 504. 500 is retried only for idempotent methods.
- GET, HEAD, PUT and DELETE are retried.
- **POST is retried only if the SDK attaches an auto-generated idempotency key to it.** If the Quotanet API doesn't honor idempotency keys yet, retry POST only on pre-send connect failures. This is the one dependency to confirm before shipping.
- Never retry other 4xx responses, and never retry after the caller cancels. In Node that means `AbortSignal`, and in Python it means cancellation or the caller's own deadline.

**Sketch (both SDKs should use the same names):**

```python
client = Quotanet(
    max_retries=2,
    timeout=Timeout(connect=5, read=30, total=60),
    retry_budget=RetryBudget(ratio=0.1, min_per_sec=10),  # None disables
)
```

```ts
const client = new Quotanet({
  maxRetries: 2,
  timeout: { connectMs: 5_000, attemptMs: 30_000, totalMs: 60_000 },
  retryBudget: { ratio: 0.1, minPerSec: 10 }, // null disables
});
```

## Load in the worst case

| | Proposal | Recommended |
|---|---|---|
| Total attempts per call | up to 10 | up to 3 |
| Worst-case call duration | ~300 s + backoff | 60 s hard cap |
| Fleet load during full outage | up to 10× | about 1.1× (budget-capped) |
| Retry timing across instances | unspecified | jittered |

## Supporting changes

- **Server side:** send `Retry-After` on every 429 and 503. Accept an attempt-number header (for example `X-Quotanet-Retry-Attempt`) so you can see retry load in your own metrics.
- **Observability:** expose the attempt count on responses and errors. Log each retry at debug level and log budget exhaustion at warn level. Without this, integrators can't tell retries are happening.
- **Docs and release notes:** v2 is a major version, which is the right moment to change behavior. State plainly that retries are now on, and give the opt-out (`max_retries=0`). Add a "running large fleets" section that explains the budget and when to tune it.
- **Tuning ceiling:** let integrators raise `max_retries`, but document that the budget still applies. Warn above about 5.

## Caveats

I didn't inspect any code, and I don't know Quotanet's actual latency or its idempotency support.
- **30 s per attempt:** keep it only if your p99 is well under about 10 s. If p99 is a few seconds, drop it to 10 to 15 s so a slow attempt gets retried sooner.
- **10% budget and 60 s deadline:** both are starting points. Validate them in a load test that simulates a partial outage across about 200 clients.