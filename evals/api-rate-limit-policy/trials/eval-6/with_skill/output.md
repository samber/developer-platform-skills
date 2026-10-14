# Vantiq Cloud: limit-increase process

I followed `api-rate-limit-policy` (steps 2, 3, 6, 7 and the measurement gates). The skill says to ask its clarifying questions first. I couldn't ask them, so the assumptions I made are listed at the end. Please correct them.

## 1. Verdict on Sales' proposal

| Sales' ask | Verdict | Why | Instead |
|---|---|---|---|
| Public row "Enterprise: 500,000 requests/day" | ❌ Don't publish | The top tier publishes a process, not numbers. A public figure becomes an entitlement that every Enterprise buyer will cite, and it caps the next prospect who wants 20x. It also contradicts "case-by-case". | Publish "Custom limits, arranged with your account team" plus a link to the process page (§2). |
| Increases granted at the AE's discretion | ⚠️ Change | Verbal grants are keyed to nothing and documented nowhere, so they are an anti-pattern. The AE owns the commercial conversation. Engineering owns capacity approval. | Written request, named approver, limit register (§3). |
| Attached to the customer admin's user account | ❌ Don't | Overrides must key to the authenticated principal. When the admin leaves or changes role, the limit silently disappears or moves. | Key to the organization and its named API keys or service identities (§3). |
| Prospect assumes Enterprise plan means higher limits | ❌ Fix now | This assumption is common and is the OpenAI-style gap. Both prospects may already believe it. | State in writing that the plan does not raise limits; limits are activated separately (§4). |

## 2. Public text

**Pricing page, tier row**

> **Enterprise:** custom limits. The Enterprise plan does not change API limits by itself. Limits are agreed in writing with your account team and activated on your organization's API keys. See [How to request higher limits].

**Limits page, section "Requesting higher limits"** (publish as-is)

1. **Who can request.** Any organization on Pro or Enterprise.
2. **What we need.** Organization ID, the API keys or service identities to raise, the target limit (sustained rate, burst, and daily quota), the endpoints involved, expected traffic shape (steady, batch, or spiky), start date, and whether the need is temporary or permanent.
3. **Lead time.** The times below are proposals; confirm them against capacity planning.
   - Temporary increase: ≥ 2 business days before the start date.
   - Permanent increase up to 5x Pro: ≥ 10 business days.
   - Permanent increase above 5x Pro: ≥ 6 weeks, the Stripe-style planning floor for large increases.
4. **Decision.** We answer in writing within 5 business days with approve, approve with changes, or decline plus the reason.
5. **What a grant means.**
   - It is a ceiling, not a guarantee. Published and granted limits are operational limits, not an SLA, unless your order form says otherwise in so many words.
   - We may lower a grant to protect platform stability. We give ≥ 6 weeks' notice, except for emergency reductions.
6. **What no grant changes.** Per-endpoint-class limits on expensive operations (bulk export, search) and the concurrency cap are set separately. A higher request quota does not raise them, but you can request them in the same ticket. *(Placeholder: replace with your actual expensive endpoint classes.)*
7. **Where to see your limits.** The `X-RateLimit-*` headers on every response show your current limit. The dashboard shows your active grant and its expiry. *(Confirm with the developer portal owner.)*

## 3. Internal process (not published)

**Flow**

1. The AE or customer files the request via a support ticket or form. A verbal request is not valid. The AE may attach commercial context, but the form is the record.
2. Platform engineering reviews capacity: fleet headroom, noisy-neighbor impact, and the region question.
3. Approval needs two sign-offs: the AE (commercial) and platform engineering (capacity). Neither can grant alone.
4. Platform engineering applies the grant to the limit register and the enforcement config, then confirms to the customer in writing.
5. The grant gets a review date. Temporary grants carry an expiry. Permanent grants are reviewed every 12 months against actual usage.

**Limit register (source of truth, one row per grant)**

| Field | Example / rule |
|---|---|
| Org ID | Always the organization. Never a user ID or email. |
| Keys / service identities covered | Named API keys. Re-keying means updating this row. |
| Sustained rate, burst, daily quota | Three explicit numbers. A single blended figure is not allowed. |
| Endpoint-class carve-outs | Each class listed with its own number. |
| Region scope | Global or per-region, stated. |
| Type, start date, expiry or review date | |
| Requester, AE, approving engineer, ticket link | |
| SLA flag | Default "no". "Yes" only if the order form says so. |

**Rule: the register generates the enforcement config.** Nobody edits the gateway by hand. This is how documentation and enforcement stay in parity, one of the two measurement gates.

**Principal keying.** The grant attaches to the org and its API keys. The customer admin's user account is irrelevant to the limit. Admin turnover is handled by an org-level contact change, not a limit change.

## 4. Contract and order-form language

Give this to Sales for both prospects before signature. I'm not a lawyer, so have Legal review it.

> "The Enterprise plan does not itself increase API rate limits. API limits are set out in the Limits Schedule attached to this order, keyed to Customer's organization ID [ID]. Limits in the Schedule are operational ceilings, not a service-level commitment, and Vantiq may reduce them for platform stability on ≥ 6 weeks' notice (or immediately in an emergency). Changes are requested via the process published at [URL]."

If a prospect insists on a committed number, that is an SLA decision. Escalate it to Legal and platform engineering. Don't let it happen through the limits page or an AE email.

## 5. Draft Limits Schedule for the two prospects

I don't know your Pro numbers. I assumed Pro ≈ 50,000 requests/day, since 500k is "roughly 10x". These figures are a starting point, to be replaced with each prospect's real traffic profile.

| Dimension | Starting grant | Reasoning |
|---|---|---|
| Daily quota | 500,000/day | The ask. Averages ≈ 5.8 req/s. |
| Sustained rate (token refill) | ≈ 15 req/s (placeholder) | About 2.5x the daily average. Leaves room for business-hours skew without allowing a full day's quota in minutes. |
| Burst (bucket depth) | ≈ 900 requests (placeholder) | About 1 minute of sustained rate. Covers webhook fan-out and scheduled reports. |
| Per-user cap inside the org | Set a value per prospect | Stops one seat from spending the whole org budget. |
| Endpoint-class carve-outs | Unchanged from Pro until requested | Expensive operations stay isolated. |

The daily quota alone is not enough, because it lets a tenant spend 500k requests in one burst. The sustained rate and burst depth are the fairness numbers.

Roll out in three steps for each grant:
1. Observe: log the prospect's real traffic with no enforcement.
2. Baseline: enforce at a high ceiling.
3. Refine: tighten or loosen from the data.

## 6. Fairness and throttle behavior

- A 10x tenant can hurt neighbors. Keep the three layers: org ceiling, per-user cap, per-endpoint-class carve-out.
- Say in the docs that load shedding is separate from rate limiting. A well-behaved tenant under its grant can still be shed under fleet stress.
- Every throttle returns HTTP 429 with `Retry-After` in delay-seconds. Never put a throttle inside an HTTP 200.
- Headers on a granted org's responses show that org's granted limit, not the Pro default. `Reset` semantics must be documented and never silently changed.
- Document any secondary or abuse guard, including its trigger shape.

## 7. Change notice for grants

- Increases take effect on the agreed date.
- Decreases need ≥ 6 weeks' notice, applied symmetrically with the increase lead time. Emergency reductions are reserved in writing.
- Notices go in-band (headers), by email to the org contact on file, and to the AE.

## 8. Measurement gates

- ✅ **Machine-readability:** 100% of throttles carry a 429 with `Retry-After`. Any undocumented 200-throttle fails the gate.
- ✅ **Documentation-enforcement parity:** diff the register and published text against the gateway config in both directions each quarter. Zero drift allowed.
- ℹ️ **Trends to baseline in the first month:** per-tier 429 rate, share of retries inside the `Retry-After` window, limit-related tickets, override requests per quarter.
- ⚠️ **Signal:** two prospects both at about 10x is already a data point. If override requests keep coming each quarter, Pro is set too low or Enterprise needs a published default tier. Revisit then.

## 9. Assumptions and questions

I need your answers to these:

1. What is the exact Pro limit, and its window? Does the published number match what the gateway enforces? Any drift is the first finding.
2. Is the API REST-only? I assumed so. If GraphQL exists, it needs cost-point metering, not request counting.
3. Is the API multi-region? If so, state whether a limit is per region or global. A per-region limit multiplies real throughput by the region count.
4. Which endpoints are expensive, and what carve-out numbers apply to them?
5. Has one customer ever degraded others' latency? That sets the priority of the fairness layers.
6. What is the deadline for these two negotiations, and what is the engineering effort ceiling? With a low ceiling, the fairness layers in §6 would be deferred until the first noisy-neighbor incident.
7. Do the two prospects' traffic profiles, such as batch jobs or webhooks, justify the placeholder burst and rate numbers?
8. Who is the named platform approver, and can the register generate gateway config today?
9. Can the developer portal show a customer's active grant and expiry? If not, that is a dependency for `developer-portal-design`.