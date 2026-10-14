# Sanity check: 99.9% partner SLO and "capped below 99.7%" claim

## Verdict

⚠️ **Don't write the spec as asked.** The SLO idea is fine. The cap claim is wrong or contradicts the SLO, depending on what "two other vendors" means. Resolve that first.

## 1. The math doesn't say "below 99.7%"

For hard serial dependencies, availability multiplies.

| Chain | Availability | Monthly downtime (30d) |
|---|---|---|
| Us 99.9% alone | 99.900% | 43.2 min |
| Us + 2 vendors, all 99.9% | 0.999³ = **99.7003%** | 129.5 min |
| Us 99.9% + 2 vendors at 99.95% | 99.80% | 86.4 min |

- ❌ Three components at 99.9% give a cap of about 99.70%, not "below 99.7%".
- ⚠️ "Below 99.7%" holds only if some component is under 99.9%. Ask which numbers she used.
- ℹ️ The 99.9% figures are probably vendor contractual SLAs. Measured reality usually differs.

## 2. The two claims contradict each other

Who are the two vendors?

**A. Our upstream vendors (inside our stack).**
- Our own availability is then capped by them: 99.9% × 99.9% × 99.9% ≈ 99.7%.
- ❌ We can't honestly publish a 99.9% SLO unless we have fallbacks or redundancy.
- To hit 99.9% with two hard-dependency vendors at 99.95%, our own code would need to be 100% available.
- Vendors would need about 99.99% each before 99.9% becomes realistic.
- Partners would also read "capped at 99.7%" as "your 99.9% is fiction".

**B. The partner's other vendors (their stack).**
- Then the cap is on the partner's own end-to-end availability, not ours.
- It's their math to do, not a claim for us to publish.
- It's also not a hard cap (see section 3).

Decide A or B before writing anything.

## 3. "Cap" is the wrong word even when the math applies

- 🟠 The product formula assumes hard, independent, serial dependencies.
- Retries, queues, idempotent replays, caching, and fallbacks all beat it. Partners can raise their end-to-end figure.
- Correlated failures, such as a shared cloud region, push the real number above the product.
- Soft dependencies (non-critical calls) don't count at all.
- Better message: "Availability composes multiplicatively across hard dependencies. Here's how to design around that." Offer a worked example. Don't assert a ceiling.

## 4. Other holes to close in the spec

1. **Baseline first.** 🔴 Measure the last 6–12 months per partner before committing to 99.9%. If we're at 99.8%, we've published a breach.
2. **SLO vs SLA.** A published SLO becomes a de facto SLA. Get Legal and Sales aligned on:
   - credits
   - contract language
   - explicit "target, not guarantee" wording
3. **SLI definition.**
   - What counts as a good event: 5xx rate, latency threshold, or both.
   - Where it's measured: edge or load balancer, not app logs.
   - What's excluded: partner-caused 4xx, 429s under their rate limit, announced maintenance.
   - Request-based or time-based.
4. **The same 99.9% for all 40 partners is a poor fit.**
   - Low-traffic partners give noisy SLIs. At 100 requests a month, one failure is 99%.
   - Integration types differ (webhook, REST, batch).
   - Alternatives:
     - One global SLO, with per-partner reporting.
     - Tiers, such as critical-path and best-effort.
5. **Budget math.** 99.9% leaves about 43 min a month. One bad deploy or one vendor incident can spend it. Define:
   - burn-rate alerts
   - what happens when the budget is spent (internal release freeze, partner comms)
6. **Vendor disclosure.** ⚠️ Check our vendor contracts for confidentiality before naming vendors or quoting their SLAs in the portal.
7. **Portal scope.** Decide what is published: the target, the monthly actual, or live burn. Show the actual with a one-month lag, not the live budget. Live burn invites disputes.
8. **Cost.** 40 partners × SLI pipeline × dashboard × review is real SRE work. Size it before promising it.

## 5. Questions to ask her before you write

1. Are the two vendors ours (A) or the partners' (B)?
2. Where does the 99.7% figure come from? Which per-component numbers?
3. Is 99.9% an SLO (target) or an SLA (contract)?
4. Is there a current per-partner availability baseline?
5. Per-partner SLOs, or one global SLO with per-partner reporting?
6. Who owns the budget policy and partner comms when it's spent?

## 6. Suggested spec shape

1. Goals and non-goals (SLO, not SLA).
2. SLI definition, measurement point, exclusions.
3. Baseline data and target justification.
4. SLO tiers or global target, with the vendor-dependency math done on our side (case A) or dropped (case B).
5. Error budget policy and burn alerts.
6. Portal content, refresh cadence, partner-facing wording.
7. Legal review, vendor-confidentiality check.
8. Rollout: pilot with 3–5 partners, then all 40.

## Suggested pushback line

"Three 99.9% components multiply to about 99.70%, so we can't both publish 99.9% and say partners are capped below 99.7%. Which dependencies are inside our SLO? Let's baseline first, then fix the wording."