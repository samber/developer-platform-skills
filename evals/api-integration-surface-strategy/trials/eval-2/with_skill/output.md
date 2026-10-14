**Answer: no. GraphQL should not replace REST, and it should not be the next public surface.** Fix the shipment-list over-fetch inside REST this sprint. Keep GraphQL as a gated option, and promote it only if integrators confirm the pain.

I did not run the skill's one-question-at-a-time interview. You asked for the full deliverable in one pass, so the assumptions below are marked. Correct any that are wrong, because they re-rank the plan.

## Assumptions (verify these)

1. **Buyer (Q1):** developers or technical integrators use the API, and logistics ops buyers sit on the economic side. That is a layered posture, so API-first holds.
2. **Spec (Q3):** OpenAPI is the linted source of truth in CI. If it drifts, fix that before any new surface.
3. **Demand (Q4):** no pipeline blocker names GraphQL. Integrators have complained about nothing. The only signal is the mobile team's own over-fetch.
4. **Agents (Q5):** no agent or MCP demand is stated.
5. **Capacity (Q6):** 6 engineers sustain 1 new surface at a time, 2 at most.
6. **Deadline (Q7):** none stated.

## 1. Audiences

| Audience | Who writes the code | Surface today |
|---|---|---|
| Third-party integrators | Humans | REST + webhooks (live, stable) |
| First-party mobile app | Mobile team | Same public REST (over-fetches on shipment list) |
| Agents, BI | None signalled | None; not scheduled |

The only party asking for GraphQL is first-party. It is not a public-contract problem, and that changes the fix.

## 2. Why not GraphQL-led

- **The promotion test fails.** The framework promotes GraphQL only on named pain that integrators confirm. Mobile over-fetching is a real, named pain, but integrators have not confirmed it, so it is not yet a public-surface case.
- **The "REST is legacy" claim is not supported.** Postman 2025 shows 93% REST adoption against 33% GraphQL. Stripe has never shipped a public GraphQL API. Shopify went GraphQL-first, marked REST legacy in October 2024, and took heavy developer pushback over verbosity. Cite that case in both directions.
- **Reversal cost is the highest tier.** A GraphQL schema is a tight, binding public contract (Hyrum's Law). REST is cheap to extend additively, and yours is stable.
- **Effort is high for your team.** Expect roughly 20-40% overhead on the initial build, plus N+1 and authorization complexity. You have 6 engineers and no GraphQL experience. Mistakes made on a public schema are the expensive kind.
- **"Replace" is the worst variant.** It forces every external integrator to migrate for no benefit to them. Even a Stripe-style two-endpoint overlap would mean running both contracts for years. Of the possible moves, this one carries the most breakage risk for the least demand.
- **Paradigm switches are two-year decisions.** Committing now means two years of ownership by a team with no experience.

## 3. Three candidate sequences

| | Sequence | Cost | Verdict |
|---|---|---|---|
| A | **REST-additive fix.** Add sparse fieldsets (`?fields=`), a slim `/shipments` summary shape, and optional `expand=`. | Low, additive, reversible | **Recommended** |
| B | **A, plus an internal-only GraphQL BFF for mobile.** The mobile team owns it. It is not public and not documented. | Medium, contained | Option if A proves insufficient |
| C | **Public GraphQL, replacing REST.** | Highest | Reject |

Sequence B keeps reversal cost low, because the only clients are apps you ship yourselves and you can break them on your own schedule. But the 6-person platform team would still own a runtime they have never operated. Ask the mobile lead to staff it, or skip it.

## 4. Plan

**Do now:**

1. Measure first. Log the shipment-list payload size and unused-field share per mobile request. Roughly 1 day, as my estimate. Without it you cannot tell whether the over-fetch justifies any new surface.
2. Ship sparse fieldsets and a summary shape on the shipment list. Roughly 3-5 days, as my estimate, if the spec generates the handlers. Mobile adopts it in the next release.
3. Instrument per-client telemetry on the public API: user-agent split, endpoint traffic share, and client type. This is the signal that re-ranks every later decision.

**Next, one surface at a time (concurrency cap: 1):**

- SDKs, generated from the OpenAPI spec, once telemetry shows how many integrators use helper libraries (Twilio's trigger was 77% of requests carrying a helper-library user-agent).
- MCP: parked. Schedule it only if RFPs or security reviews ask for it, and derive it from the spec rather than hand-building it.

**Declined for now:** public GraphQL. Record why: no integrator-confirmed pain, high reversal cost, no team experience.

## 5. Handoffs

| Surface | Audience | Demand signal | Reversal tier | Owner | Design owner |
|---|---|---|---|---|---|
| REST, extended | Integrators, mobile | Live, plus mobile over-fetch | Low (additive) | Platform | `public-api-design-review` |
| Webhooks | Integrators | Live | Low-medium | Platform | `webhook-platform-design` |
| Generated SDKs | Integrators | Pending telemetry | High | TBD | `sdk-portfolio-strategy` |
| MCP | Agents | None yet | Medium | Parked | `mcp-server-offering` |
| Public GraphQL | Integrators | None (declined) | High | None | `public-graphql-api-design` (only if promoted) |
| Internal mobile BFF (option) | Mobile team | Mobile over-fetch | Contained (internal) | Mobile lead | Inline decision |

## 6. What committing to GraphQL would actually mean

If you promote it later, you commit to all of this:

1. A public schema contract that every integrator builds against. Deprecations are visible but binding.
2. A parallel REST and GraphQL stack, because you cannot drop REST without breaking live integrators. That doubles the docs, the SDKs, and the support load.
3. New authorization design at field level, and N+1 defenses such as dataloaders, query depth and cost limits, and persisted queries.
4. New observability, because per-endpoint metrics no longer map to per-query cost.
5. Training and hiring for a skill the team does not have. Plan on 20-40% extra effort on the initial build.

## 7. Review triggers

Reopen this plan early if any of these happens:

- Two or more integrators independently confirm over- or under-fetch pain.
- A deal is blocked on a missing GraphQL surface.
- Telemetry shows sparse fieldsets did not fix the mobile problem.
- Mobile staffs and owns the internal BFF.

Otherwise review quarterly. At the next review, re-check three things: the payload measurement, the integrator feedback, and the telemetry split.

## 8. How to take this to the mobile lead

His pain is real. His fix is mismatched to it. Show him the payload measurement, offer sparse fieldsets in days, and offer Sequence B if he staffs it. Do not tell him REST is not legacy. Let the data answer.

**Next:** run the step 1 measurement on the shipment-list endpoint. It decides everything else.