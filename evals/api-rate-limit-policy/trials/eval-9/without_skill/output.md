# Corvana rate-limit audit: what to fix

## Bottom line

Fix the 50-concurrent-connection rule first, because it is the one that can breach your SLA. The "global vs per-region" mismatch is mostly a wording problem, and the sandbox 10x is the likeliest driver of the ticket spike.

## Findings, ranked by risk

| # | Gap | Risk | Why |
|---|---|---|---|
| 1 | Unlisted 50-connection block | 🔴 High | A key can be blocked while well under 1,200/min. The MSA promises 1,200/min, so the block can break the SLA. |
| 2 | "Global" in docs and MSA vs per-region in reality | 🟠 Medium | The wording is wrong, but the effect is probably benign (see below). |
| 3 | Sandbox at 12,000/min | 🟠 Medium | Load tests pass at 10x the production limit, then production returns 429s. |
| 4 | Support tickets doubled | ℹ️ Symptom | Probably a mix of #1–#3. The cause is unverified. |

### 1. Concurrency rule

- 1,200/min is 20 req/s. At 3 s latency that is about 60 in-flight requests, which is already over 50.
- Slow endpoints, batch jobs and retries after timeouts can therefore trip the block while the key stays inside its SLA-backed rate.
- If the block returns a plain 429, customers read it as a rate-limit error. The docs say they are under the limit, so they file a ticket.

### 2. Global vs per-region

- Per-region enforcement gives a customer at least 1,200/min in every region, and up to 4,800/min if traffic is spread across all four.
- If the MSA clause is a floor ("you can send 1,200/min"), you are probably compliant on this point.
- If the clause is a cap ("never more than 1,200/min"), you are generous, not in breach. That can still matter for customers whose compliance or cost-control relies on a hard global cap.
- Either way, the word "global" is false and sits in a contract-referenced document.
- Do not "fix" this by making enforcement truly global. That would cut effective limits for multi-region customers, which is a breaking change, and it adds cross-region counter synchronization.

### 3. Sandbox

- Developers load-test at 12,000/min, ship, and hit 1,200/min per region in production.
- Check whether sandbox keys are also exempt from the 50-connection rule. If so, the sandbox differs from production on two axes.

## What to do

### This week

1. **Quantify the SLA exposure.**
   - Query gateway logs for the last quarter: how many enterprise keys were blocked by the concurrency rule?
   - Of those, how many were under 1,200/min at the time?
   - That count is your actual breach exposure.
2. **Have legal read the exact MSA wording.**
   - Decide whether it is a floor or a cap, and whether it says "global".
   - Identify every contract that cites the number.
3. **Stop the bleeding on enterprise keys.**
   - Raise or exempt the concurrency threshold for keys under an SLA, pending the permanent fix.
   - This is a gateway config change. Get sign-off from whoever owns anti-abuse.
4. **Triage tickets.**
   - Sample 100–200 limit-related tickets from last quarter.
   - Tag each as one of: concurrency block, per-region confusion, sandbox-to-prod surprise, or enterprise SLA complaint.
   - This tells you which fix moves the number most. Do not assume the split.

### Next 2–4 weeks

5. **Rewrite the docs page.**
   - Replace "Global limit" with precise wording. Draft below, subject to legal review.
   - Add a "Limits" table covering rate, concurrency, regions, sandbox, 429 behavior and retry guidance.
6. **Make the concurrency limit a documented, tiered limit.**
   - Publish it as a documented limit (for example "50 concurrent connections by default; higher on enterprise plans").
   - Scale the threshold to plan tier and endpoint latency instead of using one arbitrary number.
   - You can keep other abuse heuristics undisclosed in general terms. This one is a customer-facing limit and must be published.
7. **Make errors distinguishable.**
   - Use a separate error code and message for concurrency blocks versus rate-limit 429s.
   - Return `RateLimit-*` headers, plus a region header and a current-connections header.
   - Include a docs link in the error body.
8. **Fix the sandbox.**
   - Default it to production limits, including the concurrency rule.
   - Offer an explicit opt-in for a higher load-test limit, with a response header that says "sandbox elevated limit".
   - Document that sandbox results do not predict production headroom otherwise.
9. **Amend the MSA language at the next renewal, or by addendum.**
   - Promise a floor, such as "at least 1,200 requests/min per API key in each region".
   - Define how the concurrency limit interacts with the SLA, and state that it is a documented limit, not an anti-abuse exception.

### Ongoing

10. **Stop drift.**
    - Generate the docs limits table from gateway config, or add a CI check that compares them.
    - Require legal and docs review for any change to a limit that an MSA cites.

## Draft docs wording (needs legal review)

> **Rate limits.** Each API key may send up to 1,200 requests per minute **in each region** (us-east, eu-west, ap-south, sa-east). Limits are enforced independently per region and are not shared between them.
>
> **Concurrent connections.** Each key may hold up to 50 concurrent connections by default (higher on enterprise plans). Exceeding this returns `concurrency_limit_exceeded`, a different error from `rate_limit_exceeded`.
>
> **Sandbox.** Sandbox keys follow the same limits as production unless you enable the load-test mode, which raises the rate limit to 12,000/min.

## Verify before acting

- The exact MSA clause wording, and whether it says "global".
- Whether sandbox keys bypass the concurrency rule.
- What the concurrency block returns today (status code and body).
- Whether counters fail over across regions, since a failover could reset or double a customer's budget.
- How many enterprise keys the concurrency rule actually hit.

## Do not

- Do not silently edit the docs to say "per region" without legal seeing it. The text is tied to an SLA.
- Do not change gateway enforcement to match the docs. Change the docs to match reality, unless you decide the global cap is worth building.
- Do not blame the ticket spike on a single cause before the triage in step 4.