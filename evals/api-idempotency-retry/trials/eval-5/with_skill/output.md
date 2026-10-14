# Retrying requests

*Rewritten page for Ledgerhawk's public API docs. Items marked **[CONFIRM]** are assumptions about Ledgerhawk's server behaviour. Verify each one, or ship the matching server feature, before you publish.*

---

Networks drop connections, and servers sometimes shed load. A well-behaved client retries a few times and then stops. A badly behaved one turns a short incident into a long one. This page tells you what to retry, how long to wait, and when to give up.

## The short version

1. Retry only `429`, `502`, `503`, `504`, and connection errors or timeouts. Retry `500` once at most.
2. Never retry other `4xx` responses. The same request will fail the same way.
3. Send an `Idempotency-Key` on every `POST`, and reuse the same key on every retry of that request.
4. Wait with exponential backoff and full jitter. If the response has a `Retry-After` header, wait at least that long.
5. Cap both the number of attempts (5) and the total time (60 seconds).
6. When the deadline passes, fail and surface the error. Don't retry in the background forever.

Do not use "retry any error, 5 times, 100 ms apart". If a thousand clients fail together, they all retry together at +100 ms, +200 ms and so on. That recreates the spike that caused the failure. This is what made last month's outage worse.

## Which responses to retry

| Response | Retry? | Notes |
|---|---|---|
| `429 Too Many Requests` | Yes | Wait at least `Retry-After` seconds. |
| `502`, `503`, `504` | Yes | Wait at least `Retry-After` if it is present. |
| Connection reset, DNS failure, connect or read timeout | Yes | Only if the request is safe to repeat (see below). |
| `500 Internal Server Error` | Once | Some 500s are bugs that fail the same way every time. Retry once, then stop. |
| `409` with code `concurrent_idempotent_requests` **[CONFIRM]** | Yes | Your first attempt is still running. Wait, then retry with the same key. |
| `409` with code `invalid_idempotent_request` **[CONFIRM]** | No | You reused a key with a different body. Fix your client. |
| `400`, `401`, `403`, `404`, `422`, any other `4xx` | **No** | The request is wrong. Retrying cannot fix it. |

### When a retry is safe

A read timeout means you don't know whether Ledgerhawk processed the request. Retrying a request that creates or changes money-related state can apply it twice.

- `GET`, `PUT`, and `DELETE` requests are safe to retry.
- A `POST` is safe to retry only if you sent an `Idempotency-Key` header with the first attempt.
- Never retry a `POST` without a key after a timeout or connection error. Check the resource's current state first.

## Idempotency keys

Send `Idempotency-Key: <value>` on every `POST`. The header is for retry safety only; `GET`, `PUT`, and `DELETE` don't need it. If Ledgerhawk has already processed a request with that key, it returns the stored result instead of running the operation again.

- **Mint the key on your side**, once per logical operation, before the first attempt. Reuse that same key on every retry.
- **Never generate a new key per attempt.** A fresh `uuid4()` or `Date.now()` on each retry defeats the whole mechanism.
- **Prefer a key derived from your own data**, such as `transfer-${transferId}`. It is the same on every retry by construction. If you have no stable identifier, generate a random UUID once and store it with the pending operation.
- **Keys are scoped to your account** **[CONFIRM]**. Two accounts using the same string never collide.
- **Keys are remembered for 24 hours** **[CONFIRM]**. After that, the same key is treated as a new request. Finish your retries well inside that window.
- **Same key plus a different body** returns `409 invalid_idempotent_request` **[CONFIRM]**. It is never silently replayed.
- **Same key while the first request is still running** returns `409 concurrent_idempotent_requests` **[CONFIRM]**. Wait and retry.
- **Failures are stored too** **[CONFIRM: decide whether stored 5xx results replay or re-execute, and state it here]**.

Retries are safe within these rules. We don't promise "exactly-once" delivery, because no system can promise it over a network.

## How long to wait

Use **exponential backoff with full jitter**:

```
wait = random(0, min(30 s, 1 s × 2^attempt))
```

`attempt` starts at 0 for the first retry. The random part is the important bit. Without it, every client that failed at the same moment retries at the same moment.

Upper bound of the wait before each retry:

| Retry | Wait is a random value between… |
|---|---|
| 1 | 0 and 1 s |
| 2 | 0 and 2 s |
| 3 | 0 and 4 s |
| 4 | 0 and 8 s |

Rules:

- **Honor `Retry-After`.** If the response includes it, wait at least that long, and add up to 1 s of random jitter on top. Don't shorten it. If it is longer than your remaining time budget, stop.
- **Cap attempts at 5 total** (the first try plus 4 retries).
- **Cap total time too.** Set one overall deadline, 60 seconds is a good default. Give each attempt a timeout within it, and don't start a new overall timeout on each retry.
- **Set request timeouts deliberately.** Use roughly 2 to 3 times your measured p99 latency. Don't use the operating system default, which can be minutes.
- **Log every retry**: attempt number, status or error, and the wait before the next try.
- **Use a retry budget in multi-instance deployments.** Five retries across 100 instances adds hundreds of extra requests per second to a service that is already struggling. Allow retries only while they are a small share of your traffic (the example below uses roughly 10% of successful calls). Beyond that, fail fast.
- **Stop when the service is clearly down.** If most of your recent calls are failing, pause new work instead of retrying every call on its own schedule. A circuit breaker library does this for you.

Prefer your language's retry library over hand-written loops: `tenacity` (Python), `Resilience4j` (JVM), `p-retry` (Node). Configure it with the values on this page.

## Example

This is a complete, copyable client. It sets a single overall deadline, generates a key once per `POST`, retries only the allowed cases, applies full jitter, honors `Retry-After`, and enforces a retry budget.

### Python (`requests`)

```python
import random
import time
import uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

MAX_ATTEMPTS = 5            # first try + 4 retries
BASE_DELAY_S = 1.0          # first backoff ceiling
MAX_DELAY_S = 30.0          # no single wait ceiling above this
TOTAL_DEADLINE_S = 60.0     # overall budget across all attempts
ATTEMPT_TIMEOUT_S = 10.0    # set to ~2-3x your measured p99
RETRYABLE_STATUS = {429, 502, 503, 504}
MAX_500_RETRIES = 1         # some 500s are bugs that never succeed
IDEMPOTENT_METHODS = {"GET", "PUT", "DELETE", "HEAD", "OPTIONS"}
RETRYABLE_409_CODE = "concurrent_idempotent_requests"  # [CONFIRM]


class RetryBudget:
    """Process-wide cap: retries may be about 10% of successful calls.

    Starts with a small reserve so isolated blips are still retried."""

    def __init__(self, max_tokens=10.0, per_success=0.1):
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.per_success = per_success

    def record_success(self):
        self.tokens = min(self.max_tokens, self.tokens + self.per_success)

    def try_spend(self):
        if self.tokens < 1:
            return False
        self.tokens -= 1
        return True


budget = RetryBudget()


def retry_after_seconds(resp):
    value = resp.headers.get("Retry-After")
    if not value:
        return 0.0
    if value.isdigit():
        return float(value)
    try:  # HTTP-date form
        when = parsedate_to_datetime(value)
        return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())
    except (TypeError, ValueError):
        return 0.0


def is_retryable(resp, n500):
    if resp.status_code in RETRYABLE_STATUS:
        return True
    if resp.status_code == 500:
        return n500 < MAX_500_RETRIES
    if resp.status_code == 409:
        try:
            return resp.json().get("code") == RETRYABLE_409_CODE
        except ValueError:
            return False
    return False


def request_with_retries(method, url, **kwargs):
    method = method.upper()
    headers = dict(kwargs.pop("headers", {}))

    # Mint the key ONCE, outside the loop. Reuse it on every attempt.
    # Better still: derive it from your own data, e.g. f"transfer-{transfer_id}".
    if method == "POST":
        headers.setdefault("Idempotency-Key", str(uuid.uuid4()))

    # Without a key, a timeout leaves you unsure whether the write happened.
    safe_to_retry = method in IDEMPOTENT_METHODS or "Idempotency-Key" in headers

    deadline = time.monotonic() + TOTAL_DEADLINE_S
    n500 = 0

    for attempt in range(MAX_ATTEMPTS):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break

        wait_floor = 0.0
        try:
            resp = requests.request(
                method, url, headers=headers,
                timeout=min(ATTEMPT_TIMEOUT_S, remaining), **kwargs,
            )
        except (requests.ConnectionError, requests.Timeout) as exc:
            if not safe_to_retry or attempt == MAX_ATTEMPTS - 1:
                raise
            print(f"attempt {attempt + 1}: {exc!r}")
        else:
            if resp.status_code < 400:
                budget.record_success()
                return resp
            if not is_retryable(resp, n500) or attempt == MAX_ATTEMPTS - 1:
                return resp  # let the caller handle the final error
            if resp.status_code == 500:
                n500 += 1
            wait_floor = retry_after_seconds(resp)
            print(f"attempt {attempt + 1}: HTTP {resp.status_code}")

        # Full jitter. A Retry-After header is a floor, plus up to 1 s of jitter.
        wait = random.uniform(0, min(MAX_DELAY_S, BASE_DELAY_S * 2 ** attempt))
        if wait_floor:
            wait = wait_floor + random.uniform(0, 1)

        if wait >= deadline - time.monotonic():
            break  # not enough time left to wait and retry
        if not budget.try_spend():
            break  # retry budget exhausted: fail fast
        print(f"  retrying in {wait:.2f}s")
        time.sleep(wait)

    raise TimeoutError(f"{method} {url} still failing after retries")


# Usage
resp = request_with_retries(
    "POST",
    "https://api.ledgerhawk.example/v1/transfers",
    headers={"Authorization": "Bearer <token>",
             "Idempotency-Key": "transfer-8f3a91"},
    json={"amount": 1500, "currency": "EUR"},
)
```

### Node (`fetch`)

```js
const MAX_ATTEMPTS = 5;
const BASE_DELAY_MS = 1000;
const MAX_DELAY_MS = 30_000;
const TOTAL_DEADLINE_MS = 60_000;
const ATTEMPT_TIMEOUT_MS = 10_000; // ~2-3x your measured p99
const RETRYABLE = new Set([429, 502, 503, 504]);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function retryAfterMs(res) {
  const v = res.headers.get("retry-after");
  if (!v) return 0;
  if (/^\d+$/.test(v)) return Number(v) * 1000;
  const t = Date.parse(v);
  return Number.isNaN(t) ? 0 : Math.max(0, t - Date.now());
}

export async function requestWithRetries(url, init = {}) {
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);
  // Mint the key once, outside the loop.
  if (method === "POST" && !headers.has("Idempotency-Key")) {
    headers.set("Idempotency-Key", crypto.randomUUID());
  }
  const safe = method !== "POST" || headers.has("Idempotency-Key");
  const deadline = Date.now() + TOTAL_DEADLINE_MS;
  let n500 = 0;

  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    const remaining = deadline - Date.now();
    if (remaining <= 0) break;
    const last = attempt === MAX_ATTEMPTS - 1;
    let floor = 0;
    try {
      const res = await fetch(url, {
        ...init, method, headers,
        signal: AbortSignal.timeout(Math.min(ATTEMPT_TIMEOUT_MS, remaining)),
      });
      if (res.ok) return res;
      const retryable =
        RETRYABLE.has(res.status) || (res.status === 500 && n500++ < 1);
      if (!retryable || last) return res;
      floor = retryAfterMs(res);
    } catch (err) {
      if (!safe || last) throw err; // network error or timeout
    }
    let wait = Math.random() * Math.min(MAX_DELAY_MS, BASE_DELAY_MS * 2 ** attempt);
    if (floor) wait = floor + Math.random() * 1000;
    if (wait >= deadline - Date.now()) break;
    console.warn(`retrying in ${Math.round(wait)}ms (attempt ${attempt + 1})`);
    await sleep(wait);
  }
  throw new Error(`${method} ${url} still failing after retries`);
}
```

The Node version leaves out the retry budget and the `409 concurrent_idempotent_requests` handling to stay short. Add both before running it in a fleet, or use `p-retry` with the same constants.

## Checklist before you ship

- [ ] Every `POST` sends an `Idempotency-Key` that stays the same across retries.
- [ ] Only the responses in the table above are retried. Nothing retries a `400`, `401`, `403`, `404`, or `422`.
- [ ] Waits use random jitter, never a fixed delay.
- [ ] `Retry-After` is respected.
- [ ] Attempts are capped at 5 and total time at 60 seconds.
- [ ] Each retry is logged.
- [ ] A fleet-wide retry budget or circuit breaker is in place.

---

## Notes for the Ledgerhawk team (remove before publishing)

**1. Server prerequisite.** The page assumes the `Idempotency-Key` header is implemented and tested, and that `Retry-After` is sent on 429 and 503 responses. If either is missing, don't publish the `POST` retry advice yet.

- The key must be stored per account, with the atomic claim and payload-mismatch handling the page promises.
- Only the stateless `GET`/`PUT`/`DELETE` guidance is safe to publish without it. Without keys, a `POST` retry after a timeout can duplicate a write.
- All **[CONFIRM]** items need an owner: the 24-hour window, both 409 code names (borrowed from Resend's conventions), key scoping, and whether stored 5xx results replay or re-execute.
- Before publishing, fire N concurrent identical requests with one key and confirm that exactly one side effect happens.

**2. Why the old advice made the outage worse.** The loop was "retry on any error, 5 times, 100 ms apart".

- It had no jitter, so clients failing together retried together.
- Its total wait was about half a second, so it never backed off.
- It retried non-retryable errors.
- It had no total deadline.
- A fleet of 100 instances, each retrying up to 5 times, can multiply load on a struggling service many times over while each instance looks reasonable on its own.

**3. Server-side mitigations.** The page fixes only the client half. Add these on your side:

- Send `Retry-After` on 429 and 503.
- Shed load early during overload.
- Alert on a rising ratio of retried to first-attempt requests.

**4. SDKs.** If you ship SDKs, make this page's behaviour their default:

- Retries on, with full jitter, 5 attempts, and a total deadline.
- An auto-generated `Idempotency-Key` on every `POST`, with a per-request override.
- Document the defaults in each SDK README.

**5. Wording.** The page never claims "exactly-once". If marketing material does, correct it.

**6. Numbers to tune.** 5 attempts, 1 s base, 30 s cap, 60 s deadline, and a 10 s attempt timeout are sensible defaults, not measured values. Set the per-attempt timeout from Ledgerhawk's real p99 latency, and make the replay window cover your longest retry chain (queue replays, scheduled re-runs).

**7. Skipped clarifying questions.** The skill says to ask about REST versus gRPC, the key store, multi-step requests, SDK languages, and the longest retry chain. I couldn't ask, so I assumed REST, a client-minted key, and a 24-hour window. Multi-step endpoints that call external systems (for example a payout) need recovery points server-side, and I haven't designed those here.