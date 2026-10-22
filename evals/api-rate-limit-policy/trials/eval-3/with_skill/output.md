# Fairness plan for Kolstrom Analytics' multi-tenant data API

I followed `api-rate-limit-policy`, including its four references. The skill asks clarifying questions first. I couldn't ask, so the assumptions are listed below and the numbers depend on them.

## Recommendation: don't cut everyone to 4,000 req/min

- **It misses the cause.** The 2am pain is shared-resource contention, almost certainly a few heavy endpoints, not request count. 4,000 heavy requests a minute can still saturate the backend.
- **It punishes the wrong people.** Every well-behaved tenant loses headroom to fix one tenant's pattern.
- **It's a breaking change in practice.** Cutting a published limit needs about 6 weeks' notice. Stripe's 6-week lead time is the floor, applied to decreases as well as increases.
- **The fix is a shared bucket problem.** One org-level bucket per tenant lets the loudest tenant win by accident. The remedy is to isolate the work type (bulk vs interactive), not to shrink the cap.

## Assumptions to confirm

1. REST only, request counting. The 10,000/min cap is org-wide, enforced today as a single bucket per org key.
2. The 2am export hits a small set of heavy list or scan endpoints.
3. The limit is enforced globally. If it's enforced per region, real throughput is limit × regions, and the published limit must say which it is.
4. I assume well-behaved traffic and no adversarial scraping. That keeps the token bucket as the algorithm instead of a sliding window.
5. Effort ceiling: moderate, and no hard date. The first incident has already happened, so the fairness layers are justified.

## Design

### 1. Metering

- **Unit:** requests, using a **token bucket**. The refill rate is the sustained quota and the bucket depth is the burst allowance.
- **New unit for bulk endpoints:** add **in-flight concurrency** (Twilio-style). A job paced by concurrency is slowed, not stopped.

### 2. Tier numbers (proposed starting points, to be calibrated in the observe phase)

| Layer | Sustained | Burst depth | Keyed on |
|---|---|---|---|
| Org ceiling (all classes) | 10,000/min, unchanged | 1,000 | Org |
| Per identity, standard class | 3,000/min | 300 | Child key or service identity |
| Bulk/export class carve-out | 3,000/min | 300 | Org |
| Bulk concurrency | 8 in-flight | n/a | Org |

- Burst and sustained are published as two numbers.
- The 10,000 cap stays. Nobody who is within it today is newly in violation.
- The bulk class is a **sub-budget inside the 10,000**, not extra on top.
- The export class is defined by endpoint (for example `/export`, large scans, and list calls with large page sizes). Publish the list.

### 3. Fairness layers

1. **Tenant ceiling.** The 10,000/min cap stays.
2. **Per-identity limit.** This fixes the 40-seat problem. One shared org key cannot tell seats apart.
   - Issue **child keys or service identities** under the org: one per seat, and a dedicated one for the batch job.
   - The legacy shared key keeps working, treated as one identity capped at the org ceiling. No migration is forced.
   - Once the export runs on its own identity, the big tenant's own interactive users stop being starved by their export. That is the customer-facing benefit to sell.
3. **Bulk class carve-out with concurrency cap.** The export is paced, not blocked. At 3,000/min it drains about 180k requests an hour. Duration = N ÷ rate, so ask the customer for N.
4. **Work-conserving elasticity.** This avoids the paradox of throttling a tenant when spare capacity exists.
   - When fleet load is low, bulk may borrow up to about 6,000/min.
   - When p99 or worker utilization crosses a threshold, it falls back to 3,000/min.
   - The threshold is a number to set from your own p99 data.
5. **Weighted sharing across tenants.** Cap all tenants' combined bulk traffic at a share of fleet capacity (start at 25%). Divide it by tier weight, with Deficit Round Robin or similar, so a small tenant is never starved to zero. This is internal architecture. Publish only what callers can observe.
6. **Load shedding, disclosed.** Under fleet stress, bulk traffic is shed first, then reads, then writes. Shedding is keyed to system state, not the caller's behavior, so even a tenant within its quota can see a 429 with the load-shed scope. Say this in the policy. A fairness promise that omits it overclaims.

### 4. Headers

- **Default:** the legacy `X-RateLimit-Limit/Remaining/Reset` trio. Document that `Reset` is a UTC epoch timestamp, and never change that silently.
- **Which limit the trio reports:** the most constraining one.
- **Scope header:** add a proposed `X-RateLimit-Scope` with values `org`, `identity`, `bulk`, `concurrency` and `load-shed`. This is Stripe's `Stripe-Rate-Limited-Reason` idea, and the name is mine to adjust.
- **IETF fields:** `RateLimit` and `RateLimit-Policy` are a later rung, if your edge can emit them cheaply.

### 5. Throttle response

- Every throttle returns **HTTP 429 with `Retry-After` in delay-seconds**. Use jittered values so throttled clients don't retry in sync.
- The body uses your standard error envelope with `rate_limit_exceeded`. The envelope itself is owned by `api-error-design`.
- Published client guidance: honor `Retry-After`, back off exponentially with jitter, and expect bans for hammering.
- No throttle may be signaled inside a 200.

### 6. Override path (the big tenant is the first customer)

- Raising the bulk allowance goes through a **ticket** that names the org key or service identity, the requested rate, and the dates.
  - Temporary windows need at least 24h notice.
  - Permanent increases go through the account manager.
- Write down that a higher-priced plan does or doesn't imply higher limits.
- Reserve the right to lower any override for platform stability.
- Also offer the big tenant a better path than raw HTTP calls. Candidates are an **async export job** endpoint, or a negotiated off-peak window.

### 7. Change notice and rollout

Follow the observe → baseline → refine sequence.

1. **Observe (now, about 2 weeks).** Shadow-mode the new limits. Log which requests would have been throttled, per tenant and per class, across at least a few 2am runs.
2. **Baseline.** Enforce at a high ceiling.
3. **Refine.** Tighten using the observed data.

- Contact the big tenant **before** step 2. This is a new limit for them, so give it the 6-week notice.
- The earliest enforcement date for tightening is about **2026-11-14**, if notice goes out this week.
- Publish the policy document, including the load-shed disclosure.

### Stopgap before any of this ships

Ask the customer to cap their export client-side at 8 concurrent requests. Pace it via their account manager. This needs no policy change and might fix the 2am problem this week.

## Success gates

- **Primary outcome:** other tenants' p99 during the 2am window stays within a tolerance of their daytime baseline. Set that tolerance from your own data. I have no industry number.
- **Machine-readability:** 100% of throttle responses are a 429 with `Retry-After` and a scope value.
- **Docs-versus-enforcement parity:** documented limits equal enforced limits in both directions, including the bulk endpoint list and the existence of load shedding.
- **Baseline trends for the first month:** per-tier 429 rate, share of retries that honor `Retry-After`, and override requests per quarter.

## Open inputs needed

- Which endpoints and request volume the 2am export actually uses.
- Whether limits are enforced per region or globally.
- Whether your gateway can count concurrency and classify by endpoint.
- Fleet capacity numbers, to size the 25% bulk pool and the load-shed thresholds.