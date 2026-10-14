**Next action (2 min):** don't ship v2 for the limit cut, and don't flip the number tonight. Contain the abuse tonight with targeted throttles. Cut the free tier to 300/hr on 2026-11-16 with notice. Keep `X-RateLimit-Reset` as epoch seconds and add seconds-remaining through a new header.

# Ostrafin change plan: free-tier rate limit and reset semantics

## Verdict

The platform lead and the colleague are each half right. The skill separates the two changes you bundled.

| Change | Breaking? | Regime |
|---|---|---|
| Free limit 1,000 → 300/hr | No | Limit-change notice policy: ≥ 6 weeks, staged rollout. No version bump, no 18-month window, no `Sunset` header. |
| `X-RateLimit-Reset` epoch → seconds-remaining | Yes | Silent change breaks client parsing with no visible error. It needs its own major announcement. |

- **Platform lead:** wrong on the limit. Rate limits are operational hints, not contract or SLA. IBM states that limits "can be adjusted… during the lifetime of the API and does not require a version update."
- **Platform lead, reset semantics:** right that a contract-level change needs versioning machinery. That machinery belongs to the reset swap, not the limit.
- **Colleague:** right that no v2 is needed for the limit.
- **Colleague, "tonight":** wrong. A 70% cut with zero notice breaks every well-behaved integrator and is not an emergency policy. Notice scales with blast radius, and Stripe's 6-week floor for large increases applies symmetrically to decreases.
- **Why v2 would hurt:** an 18-month window on the limit would hold the abuse fix for 18 months. Bundling the limit with the reset change would also hide which change broke which client.

## Assumptions

Correct any of these:

- REST only, so metering is request counting.
- Token bucket is enforced today.
- Free tier is keyed per API key.
- The abuse is adversarial scraping, possibly with several free keys per IP.
- Ostrafin's terms do not yet reserve the right to lower limits.

## Step 1: Tonight, contain the abuse (about 1 hour)

1. Identify the top abusive keys and IPs from gateway logs.
2. Throttle or suspend those principals only. Honest free users keep 1,000/hr.
3. Add a secondary guard keyed on request shape: concurrency, or many free keys per IP.
4. Publish the guard's existence and its trigger shape. A guard that callers find only by tripping it is a named failure mode.
5. Check the terms for a clause reserving the right to lower limits for platform stability. If it is missing, add it now.

An emergency reduction is legitimate only if reserved in writing. Targeting the abusers first avoids needing one.

## Step 2: Metering model and numbers

- **Algorithm:** keep the token bucket. Bucket depth is the burst. Refill rate is the sustained quota.
- **Sliding window:** adversarial pressure promotes it. Do the swap only if the gateway has a built-in one, since otherwise it is expensive and the secondary guard covers the abuse.
- **Sustained:** 300/hr, which is 1 token per 12 s.
- **Burst:** publish as a separate second number, never blended into one figure. Setting burst equal to sustained breaks legitimate spikes such as webhook fan-out and scheduled reports. Pick the depth from Step 3's observe data. I won't invent one.
- **Scope:** state whether the limit is per region or global. Per-region enforcement multiplies a caller's real throughput by the number of regions.
- **Key:** per API key for the free tier, with the per-IP secondary guard from Step 1.

## Step 3: Staged rollout (limit only)

Dates assume today is 2026-10-03, a Saturday.

| Date | Phase | Action |
|---|---|---|
| Mon 2026-10-05 | Observe + announce | Log real traffic against 300/hr with no enforcement. Send announcement email, changelog entry and docs banner. Include the reason, the new numbers (sustained and burst), the effective date and the override path. |
| 2026-10-26 | Baseline | Enforce at 600/hr. Send a reminder email. Measure per-key 429s. |
| 2026-11-09 | Warn | Final warning email to every free key above 300/hr in the observe data. |
| Mon 2026-11-16 | Refine | Enforce 300/hr, 6 weeks after the announcement. Tune burst from observed data. |

- Fintech customers may need more than 6 weeks. Treat 6 weeks as the floor.
- In-band signal: `X-RateLimit-Limit` shows the currently enforced number at every phase, so clients adapt without reading the changelog.

## Step 4: Headers and reset semantics

Do not change `X-RateLimit-Reset` in place.

- **Recommended:** keep `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset` (epoch seconds) unchanged. Add the IETF fields, additively:
  ```
  RateLimit-Policy: "default";q=300;w=3600
  RateLimit: "default";r=212;t=1480
  ```
  `t` is already seconds-remaining, so your goal is met with no break. `RateLimit-Policy` also lets well-behaved clients self-throttle before their first 429.
- **Cost:** the "both families" rung is the highest effort and the lowest durability. The draft is pre-RFC and syntax has already changed between drafts. Label the fields forward-looking in the docs. Cloudflare adopted both families in September 2025.
- **Check first:** can the edge emit structured fields cheaply? If not, the fallback is the legacy trio alone, with `Reset` semantics documented explicitly.
- **If the team insists on changing the legacy `Reset` meaning:**
  - This is the change that legitimately rides a version bump (v2).
  - Run that bump through `api-versioning-policy`, with the 18-month window and `Deprecation`/`Sunset` headers on v1.
  - Ship it as its own major announcement, separate from the limit cut and on a separate date.
  - v1 keeps epoch, v2 gets seconds-remaining.
- **Always:** do not emit the IETF fields alone. That breaks the clients you already have.
- **Document in all cases:** headers are advisory hints, not guarantees.

## Step 5: Throttle response

- Every throttle returns HTTP **429** with `Retry-After` in delay-seconds, never an HTTP-date.
- `Retry-After` takes precedence over any computed reset.
- The body uses the standard error envelope with code `rate_limit_exceeded`. The envelope is owned by `api-error-design`.
- The body also says which limit was hit: the sustained quota, the burst, or the secondary guard.
- Do not cache 429s.
- Publish retry guidance: honor `Retry-After`, back off exponentially with jitter, and state the consequence of hammering (key suspension). Client mechanics belong to `api-idempotency-retry`.

## Step 6: Override and upgrade path

- Publish a ticket-based override process with a lead time. Zyte's template: ≥ 24 h ahead for temporary increases, naming the key, the requests per minute and the dates.
- Overrides are keyed to the API key or org, never a person.
- State whether a paid plan implies higher limits.
- Publish the paid-tier numbers as the upgrade path.
- Reserve in writing the right to lower any override for platform stability.
- Decide which dimension no override can touch. Proposal: the secondary abuse guard.

## Step 7: Change-notice policy (publish this document too)

- Limit changes are non-breaking and need no version bump.
- Reductions get lead time proportional to blast radius, ≥ 6 weeks for large ones.
- Emergency reductions for platform stability are reserved in writing.
- Reset-semantics changes get a separate major announcement and are never silent.
- Published limits are operational hints, not an SLA. Check that no contract cites them as one.

## Gates

1. Machine-readability: 100% of throttle responses carry `Retry-After` and a documented error code.
2. Parity: the docs match the enforced config in both directions. Check that the secondary guard appears in the docs, and run the diff before 2026-11-16.

Baseline these in the first month: free-tier 429 rate, share of 429s retried inside the `Retry-After` window, limit-related support tickets, and override requests per quarter.

## Open questions

Answers can move the plan:

1. REST only, or GraphQL too?
2. Are the currently enforced and documented numbers both 1,000? Any drift is the first finding.
3. How many regions, and is the limit per region or global?
4. Can the edge emit IETF structured fields?
5. Do the terms already reserve the right to lower limits?
6. Is 2026-11-16 acceptable, or is there a hard date?

## Time estimate

- Step 1 containment: about 1 hour.
- Announcement and docs draft: about 2 hours.
- Header addition: about 1 to 2 engineering days if the edge supports structured fields.

**Next:** open gateway logs and list the top 10 free keys by request volume for the last 7 days.