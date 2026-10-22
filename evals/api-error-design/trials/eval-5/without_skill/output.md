# Quotamill API: retry signaling spec (draft v1)

## Assumptions

- Errors are JSON, shaped as RFC 9457 `application/problem+json` plus a `retry` object.
- Quote creation (`POST`) accepts an `Idempotency-Key` header. If it doesn't, **500s on POST must be marked `retryable: false`** until it does. Blind retries could create duplicate quotes.

## 1. Response headers

- `Retry-After: <integer seconds>` on every 429 and 503, and on any other status where the server wants a minimum wait. Use the integer form only, never an HTTP-date.
- Set the header to `ceil(retry.after_ms / 1000)`. The body carries the precise value.
- Clients must honor `Retry-After` on any status, even ones not listed here.

## 2. Error body

```json
{
  "type": "https://api.quotamill.example/errors/service-unavailable",
  "title": "Service temporarily unavailable",
  "status": 503,
  "code": "overloaded",
  "request_id": "req_8f2c1a",
  "retry": {
    "retryable": true,
    "action": "retry",
    "after_ms": 4200,
    "max_attempts": 4,
    "requires_idempotency_key": false,
    "backoff": {
      "base_ms": 500,
      "multiplier": 2,
      "cap_ms": 30000,
      "jitter": "half"
    }
  }
}
```

| Field | Type | Meaning |
|---|---|---|
| `retryable` | bool | `true` means the same request may succeed later without changes. |
| `action` | enum | `retry`, `reauthenticate`, `refetch`, `fix_request`. Tells the client what to do instead of retrying blindly. |
| `after_ms` | int or null | Minimum wait before the next attempt. The server computes it and adds its own jitter. `null` means client backoff only. |
| `max_attempts` | int | Maximum retries after the first failure. |
| `requires_idempotency_key` | bool | If `true`, retry only when the original request carried an `Idempotency-Key`. |
| `backoff` | object | Parameters for the algorithm in section 3. Always present when `retryable` is `true`. |

Rules:
- Clients must use `backoff` values from the body. The defaults below apply only if the object is missing.
- The server can tune constants during an incident without integrators redeploying. The algorithm stays fixed.
- Non-retryable errors send `"retryable": false` and omit `after_ms` and `backoff`.

## 3. Backoff algorithm (normative)

Defaults: `base_ms = 500`, `multiplier = 2`, `cap_ms = 30000`, `jitter = "half"`, `max_attempts = 4`.

For retry number `n`, counting from 0 for the first retry:

```
ceiling_n = min(cap_ms, base_ms * multiplier^n)
wait_n    = after_ms + ceiling_n / 2 + uniform(0, ceiling_n / 2)
```

- `after_ms` is `retry.after_ms`, or 0 if absent or null.
- `uniform(0, x)` draws a real number from [0, x].
- This is "equal jitter" and gives at least half the ceiling. Full jitter can return about 0 ms. Your incident was instant retries, so the floor matters more than the last bit of spread.
- Retry wait ranges at the defaults:

| n | `wait_n` with `after_ms = 0` |
|---|---|
| 0 | 250–500 ms |
| 1 | 500–1000 ms |
| 2 | 1–2 s |
| 3 | 2–4 s |
| 4 | 4–8 s |

Client requirements:
1. **Draw randomness independently per client and per attempt.** Never seed it from the request ID, a timestamp rounded to the second, or a fixed seed. Identical formulas are safe only with independent draws. Deterministic jitter re-synchronizes the herd.
2. Recompute `after_ms` and `backoff` from each new error response. Don't reuse values from the first failure.
3. Stop and surface the error when `n >= max_attempts`.
4. Stop and surface the error when `wait_n` would exceed the caller's remaining deadline.
5. Retry at one layer only. Don't stack SDK retries under application retries or gateway retries.
6. Keep the same `Idempotency-Key` across all attempts of one logical request.

Conformance test: make the random source injectable. With `u` fixed at 0 and `after_ms = 0`, `wait_n` must equal `ceiling_n / 2`. With `u` at its maximum it must equal `ceiling_n`.

## 4. Per-status contract

| Status | `retryable` | `action` | `after_ms` | Notes |
|---|---|---|---|---|
| 400 | false | `fix_request` | – | Include field-level errors. Retrying unchanged never helps. |
| 401 | false | `reauthenticate` | – | Refresh or re-issue the credential, then send one new request. This is not a backoff retry. |
| 404 | false | `fix_request` | – | Treat as permanent. If quotes are created asynchronously, document that separately. |
| 409 | depends on `code` | see below | see below | Never retry blindly. |
| 429 | true | `retry` | limiter reset time, jittered | `Retry-After` required. `max_attempts: 4`. |
| 500 | true only if safe | `retry` | `null` | `requires_idempotency_key: true` for POST. `max_attempts: 2`, because many 500s are deterministic bugs. |
| 503 | true | `retry` | load-based, jittered | `Retry-After` required. Scale `after_ms` up with shed level. `max_attempts: 4`. |

409 by `code`:
- `idempotency_key_in_progress`: `retryable: true`, `after_ms` about 1000, `max_attempts: 5`.
- `version_conflict`: `retryable: false`, `action: refetch`. The client re-reads, re-applies its change, and sends a new request.
- `idempotency_key_reused`: the key was reused with a different body. `retryable: false`, `action: fix_request`.

Gateway statuses 502 and 504 are not in your list. If a proxy or CDN emits them, clients treat them as 503 with `after_ms = null`.

## 5. Server-side obligations

1. Add jitter to `after_ms` before sending it. If every 429 says `1000`, you create the herd yourself. Use `limiter_reset + uniform(0, 0.25 * limiter_reset)`.
2. Rate-limit retries. Count a retry as a request, and let the 429 limiter apply to it. A client that ignores `Retry-After` hits 429 again with a larger `after_ms`.
3. Under overload, return 503 before doing work. Retry guidance is useless if the error path is expensive.
4. Log `request_id` and the `Idempotency-Key` on every error. This lets you measure retry compliance: time between attempts per client, against `after_ms`.

## 6. Client retry budget (recommended)

- Cap retries at 10% of a client's request volume over a rolling minute. Once the budget is spent, fail fast.
- Add a circuit breaker. After 5 consecutive 503s, stop sending for the largest `after_ms` seen, then probe with a single request.

## 7. Rollout

1. Ship headers and body fields for 429 and 503 first. They carry the most value and the least risk.
2. Ship the idempotency-key requirement and the 500 and 409 semantics next.
3. Publish the algorithm and test vectors in the public docs, with a reference implementation in each SDK you maintain.
4. Email the three integrators who hammered you with the spec and a deadline. Name them in your internal notes only.

## Decision for you

Does `POST /quotes` currently accept an `Idempotency-Key`? If not, add it before rollout step 2. Until then, 500 on POST stays non-retryable.