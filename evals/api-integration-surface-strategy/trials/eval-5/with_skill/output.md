# Mirelet integration-surface plan: sanity check for Friday's roadmap review

## Verdict

**Don't approve the plan as written.** It ships four new surfaces at once, which means eight builds if each SDK language counts. Three of them (SDKs, GraphQL, the widget) are high-reversal-cost commitments made before the contract underneath them is stable or measured. The spec lives in a wiki and drifts, and nothing measures API usage. Any SDK you generate or hand-write now would be built on an unstable contract, and you couldn't tell afterwards which surface matters.

The ambition is fine. The sequence and the count are the problems.

**Recommended replacement:** this quarter, fix the spec, add telemetry, and ship webhooks. Add two generated SDKs only if the spec gate passes. Park GraphQL. Decide on the widget by Friday based on one question (below).

## Assumptions

I couldn't run the interview, so these are my assumptions. If any is wrong, the affected section changes.

| # | Interview question | Assumed answer | What changes if wrong |
|---|---|---|---|
| 1 | Buyer type | Fintech infrastructure, so a developer picks the tool, probably with a non-technical economic buyer in the same deal | If the buyer is non-technical and time-to-value must be hours, the widget moves up (candidate B) |
| 2 | Surfaces today | REST only, depth unprobed | Needs a depth check (see below) |
| 3 | Spec state | Drifts. A wiki page edited by hand is worse than "(b) exists but drifts", because CI can't lint it | None, this is as stated |
| 4 | Demand signals | None instrumented (answer d) | None, this is as stated |
| 5 | Agent demand | None | If an RFP requires MCP, schedule it last, as a derived layer |
| 6 | Capacity | Unknown. For 11 people I assume 1 surface at a time, 2 at most | Please give a real number |
| 7-9 | Deadline, one-off or compounding, effort ceiling | Not stated. I assume a compounding roadmap with no external deadline | A named deal deadline can pull one surface forward |

## What is wrong with the plan

1. **Spec first.** SDKs, generated docs and any later MCP server all derive from the OpenAPI file. Stripe, Twilio and Cloudflare each generate them from one source of truth, so a single change propagates everywhere. A hand-edited wiki page would force you to fix every SDK separately each time it drifts. This is the plan's central dependency, and it's fixable in days to a couple of weeks.
2. **Telemetry must come first.** The plan says "analytics after the surfaces are live", which is backwards, and it's the cheapest thing to fix. Twilio justified formalizing its SDKs with one number: 77% of REST requests already carried a helper-library user-agent. Without that data you can't rank anything later. You also can't find out whether anyone uses the SDKs, because there is no baseline to compare against.
3. **Five SDK languages at once.** Server SDKs have a high reversal cost because their method signatures end up in customer code (Hyrum's Law). Twilio added languages only once its tooling could support them sustainably. For an 11-person team, five languages means five release pipelines, five idiom reviews and five support queues, for years.
4. **GraphQL has no named pain.** GraphQL is the starved option: roughly 20-40% extra build effort, N+1 and authorization complexity, and a schema that binds you as a public contract. It earns a slot only when integrators confirm client-driven data access, mobile over-fetching or N+1 as a real problem. Shopify is the cautionary case: GraphQL-first, then significant pushback over verbosity. Stripe, a fintech, stayed REST throughout and is no worse for it.
5. **The widget depends on the API underneath.** An embedded component is a visual and behavioral contract partners build around. Retrofitting an API under a UI-first product is the expensive direction. Build it only if a non-technical buyer is a real part of your deals.
6. **REST depth is unverified.** "Works fine" can mean intake works but a later step (reporting, dispute handling, an admin action) still needs a manual touch. Partners find that mid-integration. Check this during the spec work, before declaring the API-first foundation sound.

## Candidate sequences

**A. Spec-first derivation (recommended).**
Spec and telemetry, then webhooks, then SDKs generated from the spec, with the widget gated on buyer evidence and GraphQL parked.
- This is the order Twilio, Segment, Stripe and Plaid converged on.
- It keeps early mistakes cheap, because additive REST and webhooks are easy to unwind.
- It produces the telemetry that ranks everything after.

**B. Embedded-led.** The widget comes right after the spec and telemetry work. Pick this only if the buyer is non-technical and time-to-value must be hours. Even then, build the API foundation underneath it first.

**C. Deal-driven.** Pull forward the single surface sales can name as blocking a deal. A named blocked deal outranks any volume metric. Pick this if a real deal is waiting.

## Proposed sequence

| When | Work | Gate to move on |
|---|---|---|
| Weeks 1-3 | OpenAPI file moved into the repo as source of truth, linted in CI, and checked against live behavior. Per-client telemetry added to the API (user-agent, endpoint, customer). REST depth probe per capability. | Derivation gate: spec is declared stable. No derived surface is scheduled before this. |
| Weeks 3-9 | Webhooks, designed with `webhook-platform-design`. Fintech needs this done carefully: signing, retries, event ordering, replay and a subscription lifecycle. | Webhooks live, with delivery metrics |
| Weeks 8-13 | Node and Python SDKs only, generated from the spec. These are my guess at your top two languages, and telemetry should confirm them. | Concurrency gate passes. Go, Java and Ruby wait for telemetry and demand. |
| Quarter end | Review with real traffic data | Re-rank GraphQL, the widget, and the remaining SDKs |

If your real capacity is 1, then SDKs slide into next quarter. That's fine, because "two surfaces done properly beat six done badly".

## Per-surface handoffs

Every surface carries all five fields, including the parked and declined ones.

| Surface | Audience | Demand signal | Reversal-cost tier | Capacity owner | Design owner |
|---|---|---|---|---|---|
| OpenAPI spec and CI | All derived surfaces | Internal dependency (spec drift) | Low (internal) | **TBD, name one person** | Inline decision, with `public-api-design-review` for the REST contract |
| API telemetry | Mirelet product and platform team | Internal dependency (no data today) | Low | **TBD** | Inline decision |
| Webhooks | Third-party integrators | Assumed from your plan. Confirm with customers asking for events. | Low-medium | **TBD** | `webhook-platform-design` |
| Node and Python SDKs | Developers writing server code | Unmeasured today, so telemetry must confirm | High | **TBD** | `sdk-portfolio-strategy` |
| Go, Java and Ruby SDKs | Same | None yet | High | Unowned | `sdk-portfolio-strategy` |
| Embedded widget | Non-technical operators (assumed) | Unconfirmed, so the buyer question decides | Medium | Unowned until the gate passes | Inline decision, no sibling skill covers it |
| GraphQL | Integrators with data-access pain | None named | High | Declined this quarter | `public-graphql-api-design` |
| MCP (not in your plan) | AI agents | None | Medium | Parked | `mcp-server-offering`, built last as a layer over the spec |

I can't fill in owners. Name them before Friday.

## Gates for the roadmap

- **Plan coverage:** every surface above has all five fields, no blanks.
- **Derivation:** no SDK, widget or generated docs start before the spec is declared stable.
- **Concurrency:** concurrent new-surface builds never exceed your capacity number.
- **Measurement:** telemetry is live before any new surface ships, so each surface gets its own baseline.

## Review date and triggers

Quarterly review, around early January 2027. Reopen the plan early if:
- a deal is blocked on a missing surface
- an RFP or security review starts requiring MCP
- telemetry contradicts the audience map
- an owner loses capacity

## What I need from you before Friday

1. How many surfaces can the team really sustain at once?
2. Who is the buyer: developers, non-technical operators, or both?
3. Is any deal blocked on a specific missing surface?
4. Can you name an owner for each scheduled surface?

If answers 2 and 3 point to a non-technical buyer or a blocked deal, the sequence changes to B or C.