# Recommendation: don't switch to a fixed one-minute window

The policy wording is also wrong today, so fix the docs whichever way you decide.

## 1. The docs describe the wrong algorithm

Your docs say "token bucket", but the behavior they describe is a **leaky bucket used as a queue (a shaper)**:

- Requests enter a per-key queue.
- The queue drains at exactly 25/s, however many requests pile up.

A token bucket works differently. Tokens accrue at a fixed rate up to a capacity. A request spends a token and goes through immediately, or it is rejected. That means a token bucket allows bursts up to the bucket size, while your described limiter allows none. Your output is a flat 25/s.

Customers who read "token bucket" will assume they can burst and then be throttled. Your limiter instead delays them. Either the docs or the implementation is off, and you should confirm which.

The wording has two further gaps:

- **"No matter how many pile up" implies an unbounded queue.** Latency then grows without limit. State the maximum queue depth, the maximum wait, and what happens on overflow (for example HTTP 429 with `Retry-After`).
- **The unit isn't clear.** It's unclear whether the limit is per key, per endpoint, or per account.

## 2. Why the fixed window is a real downgrade

The average rate matches: 25/s × 60 = 1,500/min. The shape of traffic does not.

| | Current (queue, 25/s) | Fixed window (1,500/min) |
|---|---|---|
| Max burst to your backend | About 1 request at a time | 1,500 instantly at window start |
| Boundary effect | None | Up to 3,000 in a few seconds: 1,500 at the end of one window, 1,500 at the start of the next |
| Excess traffic | Delayed (queued) | Rejected until reset, up to about 59 s |
| Retry behavior | Client sees latency | Clients retry at the reset and stampede together |
| Customer-visible contract | "25 per second" | "1,500 per minute", a different promise |

The practical effects:

- **Backend load:** the rate-quote backend sees spikes up to 120× the current per-second peak (3,000 in a few seconds versus 25/s). That matters if the limiter exists to protect the carriers, databases, or rate engines behind the API.
- **Client behavior:** logistics integrations often fire batches, such as a cart of 200 lanes at once. Today they get slow but successful responses. Under a fixed window they get a burst of successes followed by a long block of 429s. Some will see that as an outage.
- **Contract:** if any customer contract, SLA, or published guarantee says 25 requests per second, the switch is a breaking change. At minimum it needs a changelog entry and notice.

## 3. What the engineer actually wants is simplicity

The real goal is simpler gateway code, and you can get that without the window's problems. The options below are in order of preference:

1. **Token bucket (capacity N, refill 25/s)**
   - State is two numbers per key: tokens and last-refill timestamp. It's about as simple as a window counter.
   - It's atomic in Redis with a short Lua script.
   - It matches what your docs already claim.
   - A modest burst capacity (25 to 100) gives friendly behavior and bounded backend load.
   - It rejects instead of queueing, so there's no queue, no drain worker, and no latency tail. This is probably where most of the simplification comes from.
2. **GCRA (generic cell rate algorithm)**
   - It needs one timestamp per key and gives smooth enforcement.
   - It's the leanest of the options.
3. **Sliding-window counter**
   - It approximates a true sliding window from two adjacent fixed windows.
   - It removes the boundary double-burst, though it doesn't smooth traffic.
4. **Keep the queue**
   - Choose this only if customers depend on delayed-but-successful behavior and your backend needs strict smoothing.

## 4. What to do

1. **Don't ship the fixed window as proposed.**
2. **Ask the engineer what is complex today.** If it's the queue and drain worker, a token bucket with rejection removes that complexity. If it's something else, such as distributed state or clock handling, the same alternatives apply.
3. **Decide the intended behavior:** smoothing (delay) or enforcement (reject with a small burst allowance). Then make the docs match that choice.
4. **Fix the docs either way.** Use "leaky bucket / queue" if you keep today's behavior, or "token bucket" if you move to one. State the rate, burst size, queue depth and timeout if any, per-key scope, and the 429 and `Retry-After` behavior.
5. **Before any change, check four things:**
   - Real per-key traffic shape: how often keys exceed 25/s and for how long.
   - Backend headroom for a burst.
   - Contract and SLA language mentioning 25/s.
   - Which customers currently rely on queueing, from p99 latency on throttled keys.
6. **If you change behavior,** roll it out behind a flag or shadow mode first. Log what the new limiter would have rejected before enforcing it. Announce the change with a changelog entry.

I haven't seen your gateway code, traffic data, or contracts. The recommendation rests on the policy as you described it, and the checks in step 5 could change the details.