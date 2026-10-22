# Verdict: don't build this plan yet

Fix three things first: the math doesn't hold, "retry all non-2xx" is wrong, and "cycle forever" is the costliest way to be polite.

## 1. The numbers contradict each other

- 19 attempts at a flat 45 s is 18 gaps × 45 s, about **13.5 minutes**, not 48 hours.
- Flat 45 s over 48 hours is about **3,840 attempts**, not 19.
- The two are only compatible with a widening schedule, which the plan rules out.
- Shopify's 19 attempts over 48 hours was an increasing-interval schedule. As I recall, Shopify has since cut it to about 8 retries over 4 hours, so check their current docs before citing them.
- Shopify also removed subscriptions after sustained failure. Copying their budget while cycling forever copies the number but not the policy.

## 2. A flat interval is worse than it is "predictable"

- Transient outages at carriers usually last seconds to hours. A flat 45 s hammers an endpoint that is already struggling, and gives it no recovery room.
- With no jitter, a carrier-wide or network-wide blip makes thousands of retries land on the same 45 s tick. That is a thundering herd, on your side and theirs.
- Predictability comes from a **documented schedule table**, not from a constant. "Retries at roughly 1, 2, 5, 10, 20, 30 min, then hourly-ish, ±20% jitter" is just as easy to document.

## 3. "Retry everything that isn't 2xx" is wrong

| Response | Action |
|---|---|
| 2xx | Success (include 202, 204) |
| 408, 425, 5xx, timeout, connection reset, DNS failure | Retry |
| 429 | Retry, and honor `Retry-After` |
| 400, 401, 403, 404, 410, 413, 422 | Mostly permanent. Retry only a few times, then park. Treat **410 Gone** as "stop now" |
| 3xx | Decide explicitly: follow or fail. Don't retry blindly |
| TLS or cert errors | Park quickly and notify. This is a config problem, not an outage |

Also define:
- a per-attempt timeout, such as 10–15 s
- a response body size cap
- worker concurrency per endpoint, so one slow carrier can't hold your workers

## 4. "Cycle forever" is not the kind option

- Dead endpoints cost real capacity for nothing. A single stuck event is **1,920 attempts per day**. At 1,000 dead endpoints that is about 22 req/s of pure waste, and it grows with every new event queued behind them.
- It is silent in a different way. Nobody tells the customer, and the failure sits unnoticed for months.
- Your wording is "retry until the budget runs out", then "keep cycling". So what happens when an event's budget is spent? The plan doesn't say. Is the cycling per event or per endpoint? Without a bound, backlog and storage are unlimited.
- "Never silently disable" is right. The alternative to a silent disable isn't endless retry. It is a **loud pause**.

## 5. Recommended design

**Schedule** (about 19 attempts over about 48 h, tune to taste):
- Attempts 1–6: 1, 2, 5, 10, 20, 30 min
- Then 1 h, 1 h, 2 h, 2 h, 3 h, 4 h, 4 h, 6 h, 6 h, 8 h, 8 h
- ±20% jitter on every delay
- A stable event ID and an `attempt` header on every try

**After the budget is spent:**
1. Park the event in a dead-letter store for 7–30 days. Never delete it silently.
2. Mark the endpoint **degraded**, then **paused** after a defined condition, such as 72 h of consecutive failure.
3. While paused, hold new events in the queue. Don't fan out per-event retries.
4. Send one **canary probe** every few hours. When it gets a 2xx, auto-resume and replay the backlog.
5. Notify the customer at thresholds such as 1 h, 24 h and 72 h, through email, a dashboard banner and an API status field.
6. Offer manual replay and resume.
7. Never delete the endpoint. A pause is reversible, visible and loud, so it isn't rude.

**Circuit breaker per endpoint:** when the recent failure rate is high, stop sending live traffic and probe only. This protects both sides and replaces the "forever cycle".

## 6. Other checks before building

- **At-least-once delivery:** document it, and give consumers an idempotency key. Retries will produce duplicates.
- **Ordering:** state whether you guarantee order per endpoint. Retries break it unless you block on the head of the line.
- **SSRF:** 9,000 customer-supplied URLs need an egress allowlist. Block private and metadata IP ranges, and re-resolve DNS per attempt.
- **Signing and replay:** sign each attempt with a fresh timestamp.
- **Metrics:** track delivery success rate, attempt-count histogram, queue age, and count of degraded or paused endpoints. Alert on queue age.

## Questions I'd settle before coding

1. What are your event volume and peak rate? That sets the real cost of any schedule.
2. Does the budget apply per event or per endpoint?
3. Do carriers need ordering?
4. What is the contractual or SLA window for delivery? That should drive the 48 h figure, not Shopify's.
5. Can customers see endpoint status in a dashboard or API?