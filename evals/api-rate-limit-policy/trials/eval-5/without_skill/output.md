# Brightmoor throttling: audit and redesign

I worked from your description only. I didn't inspect the gateway, CDN config, or GraphQL server, so anything marked **verify** is an assumption to check.

## Verdict

- Don't invent a dedicated rate-limit JSON format. Use **HTTP 429**, **`Retry-After`**, and **RFC 9457 `application/problem+json`**, with one extension member (`limit`) that names the limit tripped. That closes the "which limit?" gap without a new spec for integrators and SDKs to learn.
- The CDN caching is the most urgent bug, because it affects other customers. Fix it first.

## Audit

| # | Finding | Severity | Why it matters |
|---|---|---|---|
| 1 | CDN caches throttle responses for 60s | 🔴 | One throttled caller's response can be served to others sharing a cache key. Even without cross-caller leakage, a 2s throttle becomes a 60s outage. Origin counters also stop seeing traffic during that time. |
| 2 | REST returns 403 | 🔴 | 403 means "authenticated, not allowed". SDKs, gateways, and retry middleware treat it as non-retryable. Integrators debug their permissions instead of their request rate. |
| 3 | No timing information | 🟠 | Clients guess, usually with a fixed sleep or a tight loop. That produces retry storms. |
| 4 | GraphQL returns 200 with `THROTTLED` in `errors[]` | 🟠 | HTTP-level monitoring, proxies, and retry middleware all see success. The code is also undocumented, so integrators learn about it from production incidents. |
| 5 | Three limits, one indistinguishable response | 🟠 | The three limits need different client fixes (see below). A single "slow down" makes the right fix impossible to pick. |
| 6 | Throttle state isn't visible on successful responses | 🟡 | Clients can't pace themselves and only learn the limit by hitting it. |

**Verify:**
- Whether the CDN caches by status-code rule (error caching TTL) or by an explicit path rule. 403 isn't heuristically cacheable under RFC 9110, so someone configured this.
- Whether authenticated API traffic is cached by the CDN at all. If 200s are cached, the origin's per-key counters undercount.
- Whether throttled requests are guaranteed to be rejected before any side effect. The retry guidance below depends on this.

### Why the three limits need distinct signals

| Limit | Resets by | Correct client reaction |
|---|---|---|
| Per-key rate | Time (window) | Wait `Retry-After`, then resume. Pace requests. |
| Per-org concurrency | An in-flight request finishing, not time | Cap in-flight requests with a semaphore. Waiting alone doesn't help. Other keys in the same org count against it. |
| Search-endpoint cap | Time, but only for search | Slow or queue search calls. Everything else still works. |

## Redesign

### 1. Status codes

- **REST:** `429 Too Many Requests`. Never 403.
- **GraphQL, request rejected before execution:** also `429`, same headers. Use the same `THROTTLED` code inside the errors array.
- **GraphQL, partial throttle** (one field throttled, others resolved): keep `200` with partial `data` and a path-scoped `THROTTLED` error. Document this as the only case where `THROTTLED` arrives with a 200.
- **Compatibility:** clients that rely on GraphQL's 200 need a transition. Gate the 429 on `Accept: application/graphql-response+json`, or on an API version, then make it the default after the deprecation window.

### 2. Limit identifiers (shared by REST, GraphQL, headers, docs)

| `limit` | Meaning |
|---|---|
| `key-rate` | Per-API-key request rate |
| `org-concurrency` | Per-organization in-flight requests |
| `search-rate` | Search-endpoint cap |

**Open question:** what is the search cap's scope, per key or per org? The body's `scope` field must state it.

If several limits trip at once, `limit` names the one with the longest wait. The `RateLimit` headers list all of them.

### 3. REST response

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 12
Cache-Control: no-store
RateLimit-Policy: "key-rate";q=1000;w=60
RateLimit: "key-rate";r=0;t=12

{
  "type": "https://developers.brightmoor.example/problems/rate-limit/key-rate",
  "title": "Per-key request rate exceeded",
  "status": 429,
  "detail": "This API key sent more than 1000 requests in 60 seconds. Retry in 12 seconds.",
  "limit": "key-rate",
  "scope": "api_key",
  "quota": 1000,
  "window_seconds": 60,
  "retry_after_seconds": 12,
  "error": "slow down"
}
```

- The `type` URI is a placeholder domain. It should resolve to a docs page per limit.
- `error: "slow down"` is a deprecated field kept for the transition. Remove it at the version where 403 goes away.
- Concurrency variant: `limit: "org-concurrency"`, `scope: "organization"`, `quota` = max in-flight, plus `in_flight`. Omit `window_seconds`. Make `Retry-After` a short estimate and document it as one.
- `Cache-Control: no-store` must be on every throttle response, REST and GraphQL.

### 4. GraphQL response

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/graphql-response+json
Retry-After: 12
Cache-Control: no-store
RateLimit-Policy: "search-rate";q=30;w=60
RateLimit: "search-rate";r=0;t=12

{
  "errors": [{
    "message": "Search rate exceeded. Retry in 12 seconds.",
    "extensions": {
      "code": "THROTTLED",
      "type": "https://developers.brightmoor.example/problems/rate-limit/search-rate",
      "limit": "search-rate",
      "scope": "api_key",
      "retry_after_seconds": 12
    }
  }]
}
```

The extension fields mirror the REST body, so one parser handles both.

### 5. Headers on every response

- **`Retry-After`** (RFC 9110, stable): integer seconds on every 429. This is the contract clients depend on.
- **`RateLimit-Policy` and `RateLimit`** (IETF HTTPAPI draft): send on all responses, not only 429s, with one named item per limit. The draft is still evolving, so treat these as additive and confirm the current syntax before shipping. Don't add `X-RateLimit-*` unless you already have integrators depending on them.
- **CORS:** add all of the above to `Access-Control-Expose-Headers`, or browser clients can't read them.

### 6. Rollout

1. **Now, no breaking change:**
   - Add `Cache-Control: no-store` to throttle responses.
   - Exclude 403 and 429 from CDN error caching and verify with a test.
   - Add `Retry-After`, the problem-style fields, and `limit` to the existing 403 body.
   - Document `THROTTLED`.
2. **Next:** ship 429 behind an opt-in (API version or `Accept`) and publish the docs and changelog.
3. **After a deprecation window** (I'd suggest 90 days; your call): make 429 the default and drop `error`.
4. **Observability:** count throttles by `limit` and by key or org, and alert on any throttle response served from CDN cache.
5. **Tests:** one contract test per limit for REST and GraphQL, asserting status, headers, `limit`, and `Cache-Control`.

---

## Docs draft: Handling rate limits

**Page: Rate limits and retries**

When you send requests too fast, Brightmoor rejects them. REST returns **HTTP 429**. GraphQL returns **HTTP 429** with a `THROTTLED` error code. In the one case where a GraphQL query is partly throttled, you get a 200 with `THROTTLED` on the affected field.

The response tells you which limit you hit.

### The three limits

| `limit` | What it caps | How to fix it |
|---|---|---|
| `key-rate` | Requests per API key per time window | Wait for `Retry-After`, then slow your request rate. |
| `org-concurrency` | Simultaneous in-flight requests across your whole organization | Limit parallel requests. All keys in your organization share this limit. |
| `search-rate` | Requests to the search endpoint | Slow or queue search calls. Other endpoints are unaffected. |

### Read the response

- `Retry-After`: seconds to wait before retrying. For `org-concurrency` it's an estimate, because the limit frees up when a request finishes.
- `limit`: which limit you hit, in the response body (REST) or `extensions` (GraphQL).
- `RateLimit-Policy` and `RateLimit`: your quota and what remains, sent on every response. Use them to slow down before you hit a limit.

### Retry rules

1. **Retry only on 429** (and 5xx). Never retry 403: that is a permissions problem.
2. **Wait at least `Retry-After`**, plus 0–1 second of random jitter so clients don't retry in lockstep.
3. **No `Retry-After`?** Use exponential backoff with full jitter: base 1s, double each attempt, cap 60s.
4. **Give up after 5 attempts** and surface the error. Don't retry forever.
5. **For `org-concurrency`, don't just retry.** Add a semaphore so your client never exceeds N in-flight requests. Retrying without limiting parallelism keeps you throttled.
6. **For `search-rate`, debounce and cache.** Keep sending other requests normally.
7. **Retry only requests that are safe to repeat.** Reads are always safe. Throttled requests are rejected before they run, so retrying a write after a 429 does not duplicate it. *(Confirm before publishing.)* Don't blindly retry writes that failed with a timeout or 5xx.

### Example (TypeScript)

```ts
const MAX_ATTEMPTS = 5; // beyond this, failing is better than hammering the API
const BASE_DELAY_MS = 1_000;
const MAX_DELAY_MS = 60_000; // keep waits bounded when the server gives no hint
const JITTER_MS = 1_000; // spreads clients that were throttled at the same time

async function fetchWithRetry(url: string, init?: RequestInit): Promise<Response> {
  for (let attempt = 0; ; attempt++) {
    const res = await fetch(url, init);
    if (res.status !== 429 || attempt === MAX_ATTEMPTS - 1) return res;

    const retryAfter = Number(res.headers.get("Retry-After"));
    const waitMs = Number.isFinite(retryAfter) && retryAfter > 0
      ? retryAfter * 1_000 + Math.random() * JITTER_MS
      : Math.random() * Math.min(MAX_DELAY_MS, BASE_DELAY_MS * 2 ** attempt);

    await new Promise((r) => setTimeout(r, waitMs));
  }
}
```

For GraphQL, check `errors[].extensions.code === "THROTTLED"` as well as the HTTP status, and use `extensions.retry_after_seconds` if the header isn't readable.

### Browser clients

Read `Retry-After` and `RateLimit` from cross-origin responses. Brightmoor exposes them through CORS, so no extra setup is needed.

---

## Decisions I need from you

1. Is the search cap per key or per org?
2. Do you want the GraphQL 429 opt-in through `Accept` or through an API version?
3. Is a 90-day window for dropping 403 and `error` right?
4. Do you confirm that throttled requests never execute side effects? The retry guidance depends on it.