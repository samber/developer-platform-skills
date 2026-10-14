# Retrying requests

Retries recover from brief failures, but careless retries can turn a small incident into a large one. During an outage, thousands of clients retrying on a fixed schedule send the same burst of traffic every 100 ms, and that keeps the service down. Follow the rules below to avoid that.

## Summary

- Retry only errors that can succeed on a second attempt (see the table below).
- Wait with **exponential backoff and full jitter**. Never use a fixed delay.
- If the response has a `Retry-After` header, wait at least that long.
- Make at most **5 attempts** (1 initial request and 4 retries), and give up after a total time limit.
- Retry `POST` requests only when you send an idempotency key.
- Never retry in a tight loop, and never retry from many parallel workers without a shared limit.

## Which errors to retry

| Result | Retry? | Why |
|---|---|---|
| Network error, connection reset, timeout | Yes | Usually temporary. See the idempotency note below. |
| `408 Request Timeout` | Yes | Temporary. |
| `429 Too Many Requests` | Yes, after waiting | You are over the rate limit. Honor `Retry-After`. |
| `500 Internal Server Error` | Yes, with backoff | Often temporary. Stop if it persists. |
| `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout` | Yes | The service is overloaded or restarting. |
| `400`, `401`, `403`, `404`, `405`, `409`, `422` and other `4xx` | **No** | The request itself is wrong. Repeating it gives the same result. Fix it first. |
| `2xx`, `3xx` | No | Success or redirect. |

Do not retry `4xx` errors other than `408` and `429`. Retrying them wastes your rate limit and adds load without any chance of success.

### Idempotency

Retrying is safe for `GET`, `PUT` and `DELETE`, because repeating them has the same effect as sending them once.

A `POST` is different. If a request times out, you cannot know whether the server processed it. Retrying it without protection can create a duplicate record, such as a second charge or ledger entry. Send an idempotency key with every `POST` and reuse the same key on every retry of that request:

```
Idempotency-Key: 6f1c2a3e-8d4b-4c7a-9e55-0b2f6d1a7c42
```

Generate one new key per logical operation, not per attempt.

## How long to wait

Use exponential backoff with full jitter:

```
delay = random(0, min(cap, base * 2^(attempt - 1)))
```

With `base = 0.5 s` and `cap = 30 s`, the upper bound for each retry is 0.5 s, 1 s, 2 s and 4 s. The actual wait is a random value between zero and that bound.

- **Backoff** gives a struggling service room to recover.
- **Jitter** (the randomness) stops clients that failed at the same moment from retrying at the same moment. Without jitter, backoff only moves the burst to a later time.
- **`Retry-After`**: if the response includes it, wait at least that long, even if your computed delay is shorter.
- **Total deadline**: stop retrying after about 60 seconds, or earlier if your own caller has a shorter timeout. Return the error to your caller instead of retrying forever.
- **Per-request timeout**: set a connect timeout (for example 3 s) and a read timeout (for example 10 s). A request with no timeout can hang and never reach the retry logic.

## During an incident

- If most of your requests fail, stop sending them. Pause for a minute, then try a single probe request. This is the idea behind a circuit breaker.
- Cap the number of retries across all your workers combined. For example, allow retries to add no more than 10% to your normal request volume.
- Do not retry from several layers at once (a client library, then a proxy, then your own code). Retries multiply: 5 attempts at each of 3 layers gives 125 requests for one call.

## Example

This Python example uses only the `requests` library and implements the rules above.

```python
import random
import time
import uuid

import requests

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}
MAX_ATTEMPTS = 5          # 1 initial request + 4 retries
BASE_DELAY_S = 0.5
MAX_DELAY_S = 30.0
TOTAL_DEADLINE_S = 60.0   # give up after this much total time
TIMEOUT = (3.05, 10)      # (connect, read) seconds


def request_with_retry(method, url, **kwargs):
    headers = dict(kwargs.pop("headers", {}) or {})
    if method.upper() == "POST":
        # One key per logical operation, reused on every retry.
        headers.setdefault("Idempotency-Key", str(uuid.uuid4()))

    started = time.monotonic()
    last_response = None
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        retry_after = None
        try:
            last_response = requests.request(
                method, url, headers=headers, timeout=TIMEOUT, **kwargs
            )
            last_error = None
            if last_response.status_code not in RETRYABLE_STATUS:
                return last_response  # success, or an error that retrying won't fix
            retry_after = _retry_after_seconds(last_response)
        except (requests.ConnectionError, requests.Timeout) as err:
            last_error = err

        if attempt == MAX_ATTEMPTS:
            break

        # Full jitter: random wait between 0 and the exponential bound.
        delay = random.uniform(0, min(MAX_DELAY_S, BASE_DELAY_S * 2 ** (attempt - 1)))
        if retry_after is not None:
            delay = max(delay, retry_after)  # never wait less than the server asked

        if time.monotonic() - started + delay > TOTAL_DEADLINE_S:
            break
        time.sleep(delay)

    if last_error is not None:
        raise last_error
    return last_response  # last retryable response; let the caller handle it


def _retry_after_seconds(response):
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return max(0.0, float(value))  # seconds form; ignore the HTTP-date form
    except ValueError:
        return None


# Usage
resp = request_with_retry(
    "POST",
    "https://api.ledgerhawk.example/v1/transactions",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={"amount": 1200, "currency": "EUR"},
)
resp.raise_for_status()
```

If you only need to test from a shell, `curl` has basic retry support, but it does not add jitter or an idempotency key for you:

```bash
curl --retry 4 --retry-delay 1 --retry-max-time 60 \
     --connect-timeout 3 --max-time 10 \
     -H "Authorization: Bearer $LEDGERHAWK_API_KEY" \
     https://api.ledgerhawk.example/v1/accounts
```

`curl --retry` retries on timeouts and on `408`, `429`, `500`, `502`, `503` and `504`, and it honors `Retry-After`. Use it for scripts, not for production integrations.

---

**Before publishing, check these against the real API.** I could not verify them from here.

- The header name `Idempotency-Key`, and which endpoints accept it. If `POST` endpoints do not support it yet, change the idempotency section to say not to retry `POST` after a timeout or `5xx`, and to check for the created resource first.
- Whether the API sends `Retry-After` on `429` and `503`. If it does not, either add it or remove that guidance.
- Whether any `409` or `5xx` responses are safe to retry. If so, list them.
- The example hostname and endpoints are placeholders.