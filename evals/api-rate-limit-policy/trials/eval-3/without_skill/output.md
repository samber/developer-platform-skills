# Fairness design for Kolstrom's multi-tenant limits

## Recommendation

Don't cut everyone to 4,000 req/min. Keep the 10,000 cap as the contractual ceiling, and add three layers on top of it. The first is cost-weighted limits. The second is per-tenant concurrency caps with workload classes. The third is weighted fair queuing that only takes effect under contention.

The big tenant is slowed only while other tenants are waiting. When the system is idle they still get the full 10,000.

## Why the 4,000 cut is the wrong fix

- **The cap measures the wrong thing.** The cap counts requests. The 2am pain comes from shared resources such as DB connections, scan I/O and worker threads. An export request that scans a million rows is not the same load as a point lookup.
- **It may not stop the problem.** 4,000 expensive requests a minute can still saturate the backend. Nothing in the design ties the cap to the resource that is actually contended.
- **It punishes the wrong people.** Most tenants never approach 4,000, so the cut changes nothing for them. It hits only your heaviest, highest-paying customers, which is a soft hard-block.
- **It is a contract and trust problem.** The big tenant is within their stated limit. Cutting it unilaterally gives them a legitimate grievance.

## The design

### 1. Meter cost, not just requests

- Keep `10,000 req/min` as the headline cap, since it is the contract.
- Add a second budget in cost units per minute. Each request costs units based on endpoint weight plus rows scanned or bytes returned.
- Start by weighting export and scan endpoints at 5 to 20 units and point reads at 1. Calibrate against real resource use from your traces.
- Exceeding the cost budget is a throttle, not a violation. Say so in the docs.

### 2. Concurrency caps per tenant

This is the highest-value control. By Little's law, in-flight requests equal rate times latency. A tenant at 10,000 req/min with 2-second export calls holds about 330 connections. At 200 ms it holds about 33.

- Cap in-flight requests per tenant, for example 10 to 15% of the worker or DB pool. Excess requests wait in a queue rather than failing.
- Queue with a bounded wait of a few seconds. Return `429` with `Retry-After` only after that.
- The cap stays below the point where one tenant can exhaust the shared pool, whatever their request rate.

### 3. Workload classes with reserved capacity

- Two classes: **interactive** (default) and **bulk**.
- Classify by endpoint, by an `X-Workload: bulk` header, or automatically for requests above a cost threshold or in a long pagination run.
- Reserve capacity for interactive, for example 60 to 70% of the pool, so bulk can never take it.
- Give bulk a guaranteed floor, for example 20%, so it is never starved.
- Make it work-conserving. Bulk may borrow idle interactive capacity and gives it back immediately when interactive demand returns.
- The big tenant's 2am export lands in bulk. Their dashboards and interactive calls still land in interactive.

### 4. Weighted fair queuing between tenants

- At dispatch, schedule per-tenant queues with deficit round robin or weighted fair queuing. Weights come from plan tier.
- Under contention, each tenant with waiting work gets a proportional share.
- With no contention, one tenant can use everything, up to their caps.
- A tenant with one request in the queue never waits behind another tenant's 5,000.

### 5. Adaptive backpressure

- Watch a health signal such as interactive p99, DB queue depth or pool wait time.
- When it crosses a threshold, shrink the bulk concurrency limit with AIMD: back off multiplicatively, recover additively.
- This means no one has to guess a magic number for 2am. The system finds the level that keeps interactive latency inside its SLO.

### 6. Smooth the burst

- Use a token bucket with a bounded burst, for example no more than 2x the sustained rate over any 10-second window.
- A batch that fires 10,000 requests in the first few seconds of a minute is more harmful than the same volume spread evenly. Smoothing costs the big tenant almost nothing.

### 7. Seats sharing one org key

One org key shared by 40 seats means one runaway script can eat the org's whole budget and starve the other 39 seats. Do not give each seat its own full cap, because that lets an org multiply its limit by 40.

Use a hierarchy: **org cap, then per-credential share, then workload class.**

- Recommend or issue per-seat or per-service credentials under the org key. They are attributable and revocable, and usage rolls up to the org cap.
- Guarantee each active seat a minimum share, for example `org_cap / active_seats`. Seats may borrow unused share, so a single busy seat can still use most of the org budget when others are idle.
- Until per-seat credentials exist, attribute by a client-id header, `User-Agent` or source IP. Treat this as best-effort only.
- Put the batch export job on its own credential so it cannot starve the humans in the same org.

### 8. Give the big tenant a better path

- Offer an async export endpoint: `POST /exports`, then poll or webhook, then download. It runs on a dedicated pool or read replica and is rate-shaped on your side.
- Ask whether the 2am window is fixed. A staggered or longer window lowers peak load.
- If they need guaranteed throughput, sell dedicated capacity. That turns a support problem into a commercial one.

## What clients see

- Send `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`, plus `Retry-After` on any `429`.
- Return a machine-readable reason, such as `concurrency`, `cost_budget` or `org_seat_share`, so customers can tell why they were throttled.
- Prefer delay over rejection. A `429` is the last resort after the bounded queue wait.

## Starting numbers

These are placeholders to calibrate, not measurements:

| Control | Starting value |
|---|---|
| Interactive reserved share | 60-70% |
| Bulk guaranteed floor | 20% |
| Per-tenant concurrency cap | 10-15% of pool |
| Burst allowance | 2x sustained, 10s window |
| Queue wait before `429` | 2-5s |
| Per-seat guaranteed share | `org_cap / active_seats` |

## Rollout

1. **Measure first (about 1 week).** Replay or inspect the 2am window. Identify which resource saturates, such as DB connections, CPU or I/O. Find per-tenant cost per request. If the data shows the bottleneck is somewhere unexpected, change the design to match.
2. **Shadow mode.** Compute concurrency, cost and fair-share decisions, but log them without enforcing. Check what would have been throttled and for whom.
3. **Enforce workload classes and concurrency caps** for bulk traffic only.
4. **Enable weighted fair queuing and adaptive backpressure.**
5. **Roll out the per-seat layer** with customer notice and docs.
6. **Tell the big tenant before enforcement.** Explain that their limit is unchanged and that bulk traffic is now scheduled around other tenants.

## Success criteria

- **Interactive p99** at 2am returns to baseline, within a stated SLO.
- **Big tenant's export** still completes within an agreed window, with its bulk throughput never below the 20% floor.
- **Zero tenants** throttled while the system has idle capacity.
- **Alerts** fire on interactive p99 breach, bulk queue age and per-tenant `429` rate.
- **Replay test:** rerun the 2am load against staging before and after.

## Message for support

> We're not lowering anyone's cap. The 2am slowdown comes from one workload sharing capacity with everyone, not from a limit violation. We're adding scheduling that gives interactive traffic priority and lets bulk jobs use whatever is free. Everyone keeps their current limits, and bulk exports are queued rather than blocked.

## Open questions

- Which resource saturates at 2am? This decides whether concurrency, cost units or a read replica matters most.
- Is the 10,000 cap in the big tenant's contract, or only a default?
- Can seats get individual credentials, or must everything stay on one shared key?