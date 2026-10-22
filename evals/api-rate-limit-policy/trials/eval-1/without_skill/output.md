# Loamly API Rate Limit Policy (draft)

## Summary

Loamly limits API use to keep the service reliable for every partner. Limits apply per API key, per minute, and cover the REST and GraphQL endpoints together.

| Plan | Price | Requests per minute, per API key |
|---|---|---|
| Free | $0 | 300 |
| Growth | $49/mo | 1,500 (5×) |
| Scale | $299/mo | 6,000 (20×) |

Requests to REST and GraphQL draw from the same per-minute allowance. A GraphQL request counts as one request, subject to the query limits below.

## How limits are counted

- **Window:** limits are measured over a rolling 60-second window per API key.
- **What counts:** every request that reaches the API counts, including requests that return an error. Requests rejected with `429` also count.
- **Shared allowance:** one key's REST and GraphQL calls share a single counter.

## GraphQL query limits

One GraphQL request can ask for far more data than one REST call. All plans therefore have these limits, in addition to the request limit:

- **Maximum query depth:** 10 levels.
- **Maximum query complexity:** 1,000 points per request. Each requested field costs 1 point, and list fields multiply their children's cost by the requested page size.
- **Maximum page size:** 100 items per list field.
- **Batching:** one operation per HTTP request. Batched arrays of operations are not supported.

A query that exceeds these limits is rejected with `400` and an error message naming the limit. Rejected queries still count toward the request limit.

## Rate limit headers

Every response includes:

| Header | Meaning |
|---|---|
| `RateLimit-Limit` | Your key's requests-per-minute allowance |
| `RateLimit-Remaining` | Requests left in the current window |
| `RateLimit-Reset` | Seconds until the window resets |

## When you exceed the limit

The API returns `429 Too Many Requests` with a `Retry-After` header (in seconds). For GraphQL, the HTTP status is also `429`, with a standard error body.

Recommended client behavior:

1. Stop sending requests until `Retry-After` has elapsed.
2. Retry with exponential backoff and jitter.
3. Read `RateLimit-Remaining` and slow down before you reach zero.

Repeatedly ignoring `Retry-After` may lead to temporary suspension of the key.

## Fair use

- Creating additional API keys does not raise your limit. Limits are also enforced across all keys belonging to one account, at the plan's per-key figure times 3.
- Don't split traffic across accounts to avoid limits.
- Limits may change with at least 30 days' notice, published in the changelog.

## Higher limits

If Scale doesn't meet your needs, contact sales for a custom limit.

---

## Notes for you (not for publication)

1. **"One number covering both surfaces" doesn't hold up for GraphQL.** A single GraphQL request can fan out into thousands of database reads, so 300 requests per minute doesn't bound GraphQL load the way it does for REST. I kept your headline number and added depth, complexity, and page-size caps. Without them, one partner could degrade the service while staying under 300. This is the main departure from your brief.
2. **The multipliers are my proposal.** Your price ratio is about 6× (49 → 299), so I chose 5× and 20×. The 20× is a deliberate premium for Scale, not a proportional figure. Please confirm both against your real infrastructure headroom and expected partner volume before publishing.
3. **Account-level cap (3× per-key).** This stops people from multiplying their limit with extra keys. If you want the policy simpler, drop it and enforce one limit per account instead of per key. That is simpler to explain and harder to game.
4. **Open decisions:**
   - Whether the complexity numbers (1,000 points, depth 10, page size 100) fit your schema. Treat them as placeholders until you test them against real queries.
   - Whether to publish burst behavior. I left it unspecified (rolling window). A token-bucket model would allow short bursts.
   - Whether Free should keep the full 300 or a lower figure, given that it costs you the same to serve.