# Retry signaling for the Quotamill API

I did not put the multiplier and jitter formula in the error body spec. The skill I followed (`api-error-design`) limits error design to the fields the server sends. Backoff algorithms and jitter belong to the sibling skill `api-idempotency-retry`. A formula also doesn't belong in the body for three reasons:

- **A body field becomes a contract.** Once a formula ships in the body, you can't change it without a version boundary.
- **It repeats on every response.** The same text would sit in every 429, 500 and 503.
- **It doesn't stop the hammering.** Your three integrators retried instantly because nothing told them to wait. A server-supplied wait does that better than a shared formula.

The design below makes the server decide the wait. The integrator's job is then "wait at least `retry_after`", which is the same for everyone without a formula. If you still want a published client algorithm, I can draft it with `api-idempotency-retry` as a separate docs page that the catalog links to.

## 1. Retry matrix

| Status | Code | `retryable` | `Retry-After` header | Notes |
|---|---|---|---|---|
| 400 | `VALIDATION_ERROR` | false | no | The same request fails the same way. |
| 401 | `INVALID_TOKEN` / `MISSING_TOKEN` | false | no | Fix the credentials first. Don't retry unchanged. |
| 404 | `NOT_FOUND` | false | no | |
| 409 | `CONFLICT` | false | no | Re-read the resource, then send a new request. Not an unchanged retry. |
| 429 | `RATE_LIMITED` | true | **always** | The value comes from the limiter. `api-rate-limit-policy` owns it. |
| 500 | `INTERNAL_ERROR` | true | **always** | Retry only a bounded number of times, because a real bug fails every time. |
| 503 | `SERVICE_UNAVAILABLE` | true | **always** | |

The skill also lists 408, 502 and 504 as retryable. You don't return them today, so they are not in the matrix. If a gateway adds them, copy the 503 row.

## 2. Retry fields

All error bodies are RFC 9457 `application/problem+json`. Every error carries these extension members:

- `retryable`: boolean, present on every error. Generic handlers branch on it without a status table.
- `retry`: an object, present only when `retryable` is true.
  - `retry_after`: integer seconds, minimum wait before the next attempt. It always equals the `Retry-After` header.
  - `max_retries`: integer, the number of retries the server considers reasonable for this error.
- `request_id`: echoes `X-Request-ID`, so the ID survives a copy-paste into a ticket.
- `documentation_url`: the stable anchor for the code in the catalog.

Server rules for the values:

1. **Jitter the wait on the server.** Spread `retry_after` across a range, for example 5 to 9 seconds, instead of sending the same number to every client. This breaks up the synchronized retry waves you saw last week, and no client formula is needed.
2. **Raise `retry_after` as load rises.** Send a larger value on 503 when you are shedding load. The 500 floor is 5 seconds.
3. **Use whole seconds only.** `Retry-After` takes either a delay in seconds or an HTTP-date. Use seconds so every client parses it.
4. **Keep 500 bounded.** Send `max_retries: 2` on 500 and a higher number on 429 and 503. This stops a persistent bug from absorbing unlimited retries.
5. **Never put internals in a 500 body.** No stack traces, SQL text or internal paths.

## 3. Example responses

**429**

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 7
X-Request-ID: req_3b1c9a02

{
  "type": "https://api.quotamill.example/errors/rate-limited",
  "title": "Rate Limited",
  "status": 429,
  "detail": "Request rate exceeded for this API key. Wait 7 seconds before retrying.",
  "instance": "/v1/quotes",
  "code": "RATE_LIMITED",
  "retryable": true,
  "retry": { "retry_after": 7, "max_retries": 5 },
  "documentation_url": "https://docs.quotamill.example/errors#RATE_LIMITED",
  "request_id": "req_3b1c9a02"
}
```

**500**

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/problem+json
Retry-After: 6
X-Request-ID: req_5e6f7a8b

{
  "type": "https://api.quotamill.example/errors/internal",
  "title": "Internal Error",
  "status": 500,
  "detail": "An unexpected error occurred. Retry after 6 seconds. If it persists, contact support with the request_id.",
  "instance": "/v1/quotes",
  "code": "INTERNAL_ERROR",
  "retryable": true,
  "retry": { "retry_after": 6, "max_retries": 2 },
  "documentation_url": "https://docs.quotamill.example/errors#INTERNAL_ERROR",
  "request_id": "req_5e6f7a8b"
}
```

**503**

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/problem+json
Retry-After: 30
X-Request-ID: req_1a2b3c4d

{
  "type": "https://api.quotamill.example/errors/service-unavailable",
  "title": "Service Unavailable",
  "status": 503,
  "detail": "The quote engine is temporarily overloaded. Retry after 30 seconds.",
  "instance": "/v1/quotes",
  "code": "SERVICE_UNAVAILABLE",
  "retryable": true,
  "retry": { "retry_after": 30, "max_retries": 3 },
  "documentation_url": "https://docs.quotamill.example/errors#SERVICE_UNAVAILABLE",
  "request_id": "req_1a2b3c4d"
}
```

**409** (non-retryable shape; 400, 401 and 404 look the same)

```http
HTTP/1.1 409 Conflict
Content-Type: application/problem+json
X-Request-ID: req_7c8d9e0f

{
  "type": "https://api.quotamill.example/errors/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "The quote was modified since you read it. Fetch the current version, then resubmit.",
  "instance": "/v1/quotes/q_123",
  "code": "CONFLICT",
  "retryable": false,
  "documentation_url": "https://docs.quotamill.example/errors#CONFLICT",
  "request_id": "req_7c8d9e0f"
}
```

## 4. Catalog entries

Publish each code on one page with a stable anchor, for example `## RATE_LIMITED (HTTP 429) {#RATE_LIMITED}`. For each code, state:

- the HTTP status it uses
- its cause
- whether it is retryable
- whether `detail` is safe to show end users
- the fix path

Add these lines to the retryable codes:

- **`RATE_LIMITED`, `SERVICE_UNAVAILABLE`, `INTERNAL_ERROR`:** "Wait at least `retry.retry_after` seconds before the next attempt. Stop after `retry.max_retries` attempts. Never retry immediately."
- **Contract line:** "`code` and `retryable` are stable. `detail` text may change without notice."

In OpenAPI, give every endpoint a `responses` entry per status, with one named example per code. The 429, 500 and 503 examples must include the `Retry-After` header and the `retry` object.

## 5. Gaps and gates

**Gaps in this draft**

- **POST retry safety:** I assumed `POST /v1/quotes` creates something. If it does, a retry after a 500 can duplicate it unless the client sends an idempotency key. That also belongs to `api-idempotency-retry`.
- **429 values:** the actual limits and the `retry_after` for 429 come from `api-rate-limit-policy`.
- **Audit not done:** I did not audit your current responses. Please send 5 to 10 real error responses from different endpoints so I can check every existing code, field and message against the new surface. Clients may already branch on them, so the migration must map old identities to new ones.

**Gates before shipping**

- Every endpoint and every status uses this one envelope.
- Every code a client can see is in the published catalog and in each endpoint's documented examples.
- Every 429, 500 and 503 response sends `Retry-After`, and it equals `retry.retry_after`.

**Questions for you**

- Are you REST-only?
- Are your consumers third-party integrators, agents, or both?
- Do any clients already match on current code or message strings?