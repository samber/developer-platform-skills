# Brightmoor throttle-response audit, redesign and retry guidance

I applied `api-rate-limit-policy` and read all four of its references. You didn't answer its eight clarifying questions, so I made assumptions, listed in § 8. Each one names the design choice it would change.

**Verdict:** drop the dedicated rate-limit JSON format. The fix is a standard 429 plus an RFC 9457 error body from `api-error-design`, one reason header, and the retry-timing fields.

## 1. Audit findings

| # | Finding | Why it hurts | Severity |
|---|---|---|---|
| 1 | The REST throttle returns **403** `{"error":"slow down"}`. | 403 means "authenticated but not allowed". No generic client or SDK retries it. | 🔴 |
| 2 | There is **no `Retry-After`** and no limit headers. | Integrators guess a delay, and guesses cluster into retry storms. | 🔴 |
| 3 | The **CDN caches the throttle response for 60 s**. | The throttle outlasts the real limit, and a cache key without the credential could serve one caller's throttle to others. Throttles must be uncacheable (RFC 6585 forbids caching a 429). | 🔴 |
| 4 | GraphQL returns **HTTP 200 with `THROTTLED`**, and the docs never mention it. | A client that checks only the status code treats it as success. This is the skill's named trap. | 🔴 |
| 5 | **Three limits** (per-key rate, per-org concurrency, search cap) produce an identical response. | Callers can't tell which they tripped. The org concurrency cap can be tripped by a sibling key. This is the GitHub "opaque secondary limit" failure. | 🟠 |
| 6 | The REST and GraphQL throttle conventions differ. | Clients must learn two mechanisms. Shopify has the same problem. | 🟠 |
| 7 | I can't tell whether the docs match the enforced limits. | Unverified, so the parity gate fails until the diff is done. | ⚠️ |

**Measurement gates today:**
- Machine-readability: **fails**. A 403 with a string is not a documented signal, and the GraphQL path is undocumented.
- Docs-versus-enforcement parity: **unmeasured**.

## 2. Don't invent a rate-limit format

The skill is explicit: the 429 body is "a plain instance of the API's error envelope… never invent a rate-limit-specific format". RFC 9457 exists so teams don't define their own. A custom format would also leave you with two error shapes to maintain.

What integrators are missing is **signals**, not a schema:
1. which limit they tripped,
2. when to retry,
3. whether retrying helps.

These ride on standard parts: the status code, a header, and extension members of the existing envelope. `api-error-design` owns the final envelope field names. Mine below are illustrative.

## 3. The redesigned REST throttle

**Status and headers (all three limits):**
- `429 Too Many Requests`.
- `Retry-After: <delay-seconds>`. Use integer seconds, never an HTTP-date.
- `Cache-Control: no-store`.
- `Brightmoor-Rate-Limited-Reason: key_rate | org_concurrency | search_cap`. This follows Stripe's `Stripe-Rate-Limited-Reason`.

**Limit-state headers (default rung: the legacy trio):**
- Send `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset` on every response, not only on throttles.
- Add `X-RateLimit-Resource: core | search`, borrowed from GitHub, so the trio says which budget it describes.
- **Scope:** the trio describes the per-key rate on `core` endpoints and the search cap on search endpoints.
- **Concurrency:** it is not a window limit, so it gets no trio. It signals through the reason header and `Retry-After`.
- **Reset semantics (decision to confirm):** seconds until reset, consistent with `Retry-After` and immune to client clock skew. Write this in the docs and never change it silently.
- **Upgrade trigger:** add `RateLimit-Policy` and `RateLimit` (IETF draft) when your edge emits them cheaply. Three simultaneous limits, one of them concurrency, is what the draft's multi-policy support is for. Don't ship the IETF fields alone: the draft is pre-RFC and has changed syntax, and GitHub and Stripe don't emit them.

**What `Retry-After` means per limit:**

| Reason | Meaning of the value | Caller action |
|---|---|---|
| `key_rate` | Time until the bucket has a token. | Wait, then retry. |
| `search_cap` | Time until the search budget refills. | Wait, and cache or batch searches. |
| `org_concurrency` | There is no window, only a short hint (judgment call: 1 s). A slot frees when any in-flight request in the org finishes. | Lower parallelism. Waiting alone doesn't fix a client that fans out too wide. |

**Example body (key rate):**

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 12
Cache-Control: no-store
Brightmoor-Rate-Limited-Reason: key_rate
X-RateLimit-Limit: <LIMIT>
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 12
X-RateLimit-Resource: core
```
```json
{
  "type": "https://docs.brightmoor.example/errors/rate-limit-exceeded",
  "title": "Rate limit exceeded",
  "status": 429,
  "detail": "This API key exceeded its request rate. Retry in 12 seconds.",
  "code": "rate_limit_exceeded",
  "reason": "key_rate",
  "retryable": true,
  "documentation_url": "https://docs.brightmoor.example/rate-limits#key_rate",
  "request_id": "req_...",
  "error": "slow down"
}
```

- Concurrency differs only in `reason: "org_concurrency"`, a `detail` that says the limit is shared across the org's keys, and `Retry-After: 1`.
- `error: "slow down"` is the legacy member, kept for the transition window (§ 5) so clients that match on it keep working. Remove it afterwards.
- The reason values are a closed set in the error catalog. Adding a fourth limit means adding a catalog entry, not a new format.

## 4. GraphQL

GraphQL has no equivalent of the REST envelope, and `public-graphql-api-design` owns that shape. For throttling, the policy is:

- **Now (additive, non-breaking):** keep the 200 with `THROTTLED`, and make it loud and complete:
  - Add `Retry-After`, `Cache-Control: no-store`, `Brightmoor-Rate-Limited-Reason` and the limit-state headers to that 200.
  - Add `extensions` on the error: `{"code":"THROTTLED","reason":"key_rate","retryAfter":12}`. Use the same reason values as REST.
  - Document it in the same page and with the same prominence as the REST 429.
- **Next API version or opt-in:** return a real **429** for pre-execution rejections.
  - All three limits are admission decisions, so no partial result exists to protect.
  - The change is breaking for GraphQL clients that drop non-2xx bodies, so route it through `api-versioning-policy`.
  - Don't flip it silently.
- **Open metering question:** if GraphQL currently counts requests against the per-key rate, it uses the wrong model. The skill says to meter GraphQL in cost points with a published formula, not requests. Treat that as a separate follow-up, not part of this pass.

## 5. Rollout and change notice

Rate-limit changes don't require a version bump, which is why the skill wants a written notice policy.

| Phase | Changes | Why this order |
|---|---|---|
| **Week 0 (hotfix)** | `Cache-Control: no-store` and a CDN bypass for throttle responses; purge cached throttles. Add `Retry-After`, the reason header and the limit headers to the *current* 403s and GraphQL 200s. | Purely additive, and it removes the worst harm. Verify by tripping a limit from two different keys and confirming the second never sees the first's response. |
| **Week 0** | Run the docs-versus-enforcement diff, in both directions (§ 7). | This establishes the parity baseline. |
| **Weeks 0–6** | Announce the 403→429 move, the new body and the GraphQL changes by email, the changelog and a docs banner. | 6 weeks is Stripe's lead time for large limit increases, applied symmetrically as a judgment call. |
| **After the notice** | REST switches to 429 with the RFC 9457 body, keeping the legacy `error` member. | Status-code matching is the contract clients are most likely to depend on. |
| **+1 release** | Drop the legacy `error` member. | Gives matching clients one more cycle. |

Rules to publish with it:
- Published numbers are operational hints, not an SLA.
- Brightmoor may lower limits for platform stability.
- Never change reset semantics silently.

## 6. Retry guidance for the docs (draft)

> ### Handling rate limits
>
> Brightmoor limits how fast you can call the API. When you exceed a limit, you get a throttle response. It is safe to retry.
>
> #### Which limit did I hit?
> Check `Brightmoor-Rate-Limited-Reason` (REST) or `errors[].extensions.reason` (GraphQL):
>
> | Reason | What it limits | What to do |
> |---|---|---|
> | `key_rate` | Requests per minute for one API key. | Wait for `Retry-After`, then retry. Spread calls out. |
> | `org_concurrency` | Requests in flight at once across **all keys in your organization**. | Cut parallelism. Another key or service in your org may be using the slots. |
> | `search_cap` | Calls to search endpoints. | Cache results, batch queries, and avoid polling search. |
>
> Limits and windows: **[table of published numbers: burst and sustained as two separate values per tier. Fill from the enforced config.]**
>
> #### How to detect a throttle
> - **REST:** HTTP **429**.
> - **GraphQL:** today, HTTP **200** whose `errors` array contains `extensions.code = "THROTTLED"`. A client that checks only the status code will treat this as success. **[Update when the 429 change lands.]**
>
> #### How long to wait
> 1. Read `Retry-After`. It is a whole number of seconds. Still handle an HTTP-date form defensively, and never wait a negative time.
> 2. Wait at least that long. When both `Retry-After` and a computed reset are present, `Retry-After` wins.
> 3. For repeated throttles, back off exponentially with jitter: `sleep = max(Retry-After, random(0, min(60 s, 1 s × 2^attempt)))`. Without jitter, throttled clients all retry at the reset boundary and trip the limit together.
> 4. Stop after a bounded number of attempts and surface the error.
>
> For `org_concurrency`, waiting alone doesn't help if you start the same number of parallel requests again. Reduce the number of simultaneous requests.
>
> #### Retry safely
> Retry write requests only with an idempotency key. See [client retries and idempotency].
>
> #### Plan ahead
> `X-RateLimit-Remaining` and `X-RateLimit-Reset` let you slow down before you hit a limit. These values are advisory: "5 remaining" does not guarantee five successful calls.
>
> #### What not to do
> - Don't retry immediately or in a tight loop.
> - Don't retry on every key at once.
> - Don't cache throttle responses.
> - **[Brightmoor to confirm: consequence for ignoring limits, e.g. key suspension.]** I can't invent that policy.
>
> #### Need higher limits?
> **[Describe the override process: who to contact, what to include (key or org, requested limit, dates), lead time, and that overrides are tied to the key or org and can be lowered for platform stability.]**
>
> Limits may change. We announce reductions at least **[6 weeks]** ahead.

Client-side mechanics (retry budgets, idempotency) belong to `api-idempotency-retry`. This page only sets expectations.

## 7. Verification before declaring done

1. **Machine-readability gate:** every throttle path (REST ×3 reasons, GraphQL ×3 reasons) carries `Retry-After`, the reason, and a documented code. Check that all six show up in a test.
2. **Parity diff, both directions:**
   - Every enforced limit is documented, including the concurrency and search guards (existence and trigger shape at minimum).
   - Every documented number matches the config. List the enforced values and the docs side by side.
3. **CDN test:** trip a limit with key A, then call as key B within 60 s and confirm B gets a normal response. Confirm 429s and `no-store` responses are never cached.
4. **Baselines to record in month one:**
   - 429 rate by reason and tier.
   - Share of retries that honor `Retry-After`.
   - Limit-related support tickets.
   - Override requests per quarter.

## 8. Assumptions and open questions

| Assumption | If wrong |
|---|---|
| REST and GraphQL both exist, with GraphQL possibly counting requests. | If GraphQL already uses cost points, skip the metering follow-up in § 4. |
| Token bucket is the algorithm, and burst and sustained exist but aren't published. | If it is a fixed window, name the boundary flaw in the docs and add jitter more aggressively. |
| Single-region enforcement. | If limits are per region, the true global rate is limit × regions. State the scope. |
| The edge can emit the legacy trio but not the IETF fields cheaply. | A cheap edge promotes the both-families rung now. |
| There is a firm date and low effort appetite. | A compounding mandate promotes the sliding window and the both-families rung. |
| No noisy-neighbor fairness work is in scope. | If one customer has degraded others, step 3 fairness layers move up. |

**Needed from you:**
1. The enforced numbers for all three limits, and the currently documented ones.
2. The `Retry-After` value your limiter can actually compute for concurrency.
3. A decision on reset semantics.
4. Your hammering-consequence policy and the override process, for the placeholders in § 6.