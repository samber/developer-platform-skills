# Ferroline limiter: should we switch to a fixed 1,500/min window?

**Recommendation: do not switch to a fixed window.** The "simpler gateway code" argument may be valid, but a fixed window is the weakest option for a public, paid API. Fix the policy wording first, then pick token bucket, or keep the leaky bucket if a fragile downstream needs it.

I followed the `api-rate-limit-policy` skill and its references. I could not ask its clarifying questions, so the gaps are listed at the end. I did not look at Ferroline's gateway or docs, only your description of them.

## 1. The wording is already wrong

Your docs say "token bucket". What you describe is a **leaky bucket**: requests queue per key and drain at a constant 25/s no matter how many pile up. The skill calls this naming trap the most commonly inverted pair in this space. The test it gives is whether idle time banks burst capacity or output stays constant. Yours stays constant, so a quiet client gets no burst headroom.

That matches the failure mode "a policy that names token bucket but describes leaky-bucket behavior". Any decision, including this one, should start by correcting the docs.

Related gaps in the wording:
- **One blended number.** Only "25/s" is published. The skill wants burst and sustained as two explicit numbers. Here burst is effectively zero because the queue absorbs everything.
- **Undefined overflow.** "No matter how many pile up" implies an unbounded queue. 1,500 queued requests means the last one waits 60 seconds. Most HTTP clients time out first and retry, which adds duplicate load. The docs must state the queue cap and what happens past it: a 429 with `Retry-After`.
- **Scope.** The docs do not say whether the limit is per region or global. A per-region limit multiplies a caller's real throughput by the number of regions.

## 2. Why a fixed window is the wrong replacement

1,500/min averages to the same 25/s, but it makes a different promise.

- **Boundary doubling.** A client can send 1,500 requests at the end of one window and 1,500 at the start of the next. That is 3,000 requests in about a second, 120× the pace your docs promise today.
- **Burst inside a window.** All 1,500 can arrive in one second, 60× the current pace. This is the skill's "burst = sustained" problem, with the burst uncontrolled.
- **Retry stampede.** Throttled clients synchronize their retries at the reset boundary. The IETF draft itself concedes this failure mode.
- **Wrong tier for this API.** The skill reserves fixed window for internal or low-stakes limits where the 2× flaw is harmless. It ranks it last on value for a public developer API (`token bucket > sliding window > leaky bucket > fixed window`).
- **Backend protection.** If your rate engines or carrier connections are the bottleneck, a fixed window removes the smoothing you have today.

The skill's effort ranking also does not make fixed window the cheapest option. Check the "much simpler" claim against your actual gateway.

## 3. What to do instead

1. **Rewrite the docs to describe the behavior.** Say it is a leaky bucket (or whatever you end up with), give the queue cap, and name the overflow response. Diff the docs against the enforced config in both directions. The skill's gate is zero drift, including any secondary guards.
2. **Choose the algorithm by one question: is a burst a threat or a feature?**
   - **Token bucket (default).** Pick it if a burst is fine. Shipping-rate calls are typically bursty, such as checkout fan-out and scheduled batch quoting, so burst headroom is a feature. Publish two numbers: refill of 25/s sustained, and a bucket depth set from observed traffic. Do not guess the depth.
   - **Keep the leaky bucket.** Pick this if bursts hurt a fragile downstream, such as carrier APIs with their own limits. Then keep it, fix the name, and add a cap with 429s.
3. **If simplicity is the real goal,** a token bucket needs only a counter and a timestamp per key, refilled lazily, with no queue or drain worker. This is my inference, not something the skill states. Verify it on your gateway.
4. **Throttle response.** Return HTTP 429 with `Retry-After` in delay-seconds, with the error envelope owned by `api-error-design`. Publish backoff with jitter.
5. **Headers.** Default to the legacy `X-RateLimit-Limit/Remaining/Reset` trio, and document whether `Reset` is epoch or seconds-remaining. Changing reset semantics silently is the one change the skill says needs its own major announcement.

## 4. If you change enforcement anyway

- A move from queued to 429 changes behavior. Clients that never saw a 429 may have no retry logic.
- Treat any decrease as needing at least 6 weeks' notice. That is the skill's symmetric floor, taken from Stripe's lead time for large increases.
- Roll out in three stages: observe (shadow-log the candidate algorithm), baseline (enforce at a high ceiling), then refine from observed data.
- Reserve the right in writing to lower limits for platform stability, and say the numbers are operational hints, not an SLA.

## What would change this answer

- **Is any limit enforced differently from what the docs say?** If so, that drift is the first finding.
- **Is the traffic adversarial or scraped?** If yes, sliding window is promoted, not fixed window.
- **Is there a fragile downstream?** If yes, keep the leaky bucket.
- **Do enterprise customers need more than 25/s?** If so, you need a published override path with lead times. That is a separate step.
- **What is the deadline and effort ceiling?** A hard date favors keeping what the gateway enforces today, with corrected docs. A multi-year contract favors token bucket or sliding window.

The one thing to confirm before acting is what the limiter actually does on overflow today: queue, drop, or 429.