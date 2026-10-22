# Quorrel integration-surface plan: what to build first

**Build the warehouse/bulk telemetry export first. Do not start with the Terraform provider or the CLI.**

Run two non-surface prerequisites alongside it: make the OpenAPI spec the CI-linted source of truth, and break down the 61% Python user-agent share by account. The CLI and Terraform provider come next, generated from that spec. The Python library gets stabilised, not expanded.

I followed `api-integration-surface-strategy` in full, including its reference tables. The skill's interview is interactive and I had no answers, so the assumptions are listed in section 8. A few of them could change the order.

## 1. Answer to leadership: "pick by what the community wants"

Community is Quorrel's brand, and it is a real audience. But it is the weakest demand signal for deciding build order. The skill weights signals like this:

| Rank | Signal | Quorrel's instance | Weight |
|---|---|---|---|
| 1 | Pipeline blockers | Two enterprise renewals stalled on warehouse export | Highest. Few accounts hit it, but those accounts churn or block deals. A named blocker outranks any volume metric. |
| 2 | Usage telemetry by client type | 61% of REST traffic carries the Python library's user-agent | Strongest volume signal. |
| 3 | Community asks | 400+ reactions for a Terraform provider and CLI | Real, but cheap to emit. It needs confirming against signals 1 and 2 before it schedules anything alone. |

The community is not ignored. It owns slots 2 and 3 in the sequence below, and it gets a public, dated answer now (section 7). A brand built on community also takes a hit when a stalled renewal turns into churn.

## 2. Audience map

| Consumer | Writes the calling code | Buyer type | Surface they need |
|---|---|---|---|
| Enterprise data and BI teams | Analyst or data engineer | Economic buyer (renewal) | Bulk/warehouse export |
| Python developers | A person using the library | Technical user | REST via Python SDK (exists) |
| Platform/infra engineers and OSS community | Person or Terraform | Technical user | Terraform provider, CLI |
| AI agents | Agent client | None observed | Nothing yet |

Quorrel looks like the "both in the same deal" buyer type. A developer adopts the tool, and an economic buyer renews it. A surface that reaches only one side stalls the deal, so the community asks and the warehouse export serve different halves of the same deal rather than competing.

## 3. Inventory and the central dependency

| Surface | Audience | Depth | Spec-derived or hand-built | Traffic share |
|---|---|---|---|---|
| REST API | All developers | Unknown, must probe | Unknown | 100% of REST |
| Python library | Python developers | Exists | Unknown | 61% of REST |
| Other surfaces | n/a | Not stated | n/a | n/a |

Two checks must run before anything derived is scheduled:
- **Spec state.** The CLI, the Terraform provider and any generated SDK all derive from the REST contract. If the OpenAPI spec drifts or is missing, fixing it comes first.
- **Depth check, which matters most for Terraform.** A provider can only manage what the API can do end to end. If dashboards, alerts or sources still need a UI-only step, the provider ships half-working. This is the "shallow API-first" failure mode.

## 4. Reading the signals

- **Warehouse export (rank 1).** This is the only signal tied to revenue, and the deadline is already running. It is also an audience the community asks do not cover: BI consumers, not developers.
- **61% Python user-agent (rank 2).** The Twilio precedent is 77% helper-library traffic, which justified formalising and then generating its SDKs. Read this as follows:
  - It confirms the Python library is Quorrel's main client, so it must be maintained and its release path made reliable.
  - It does not request a new surface. It supports generating SDKs from the spec later, not building more languages now.
  - Verify it before relying on it. One large customer's pipeline can dominate a user-agent share. Break it down by account and by endpoint.
- **400+ reactions (rank 3).** One issue is a concentrated ask, and it is worth acting on. Two facts are missing:
  - How the reactions split between the Terraform provider and the CLI.
  - Whether the reacting accounts are paying or evaluating.
- **AI agents.** No signal was reported, so MCP stays parked.

## 5. Candidate sequences

| | A: Deal-driven | B: Community-led (leadership's ask) | C: Spec-first |
|---|---|---|---|
| Order | Bulk export, then CLI, then Terraform provider | Terraform provider and CLI, then bulk export | Spec and telemetry work, then derived surfaces, then bulk export |
| Pro | Unblocks the named renewals. Bulk export has medium reversal cost. Spec work runs in parallel. | Honours the brand and the loudest ask. | Cleanest foundation. |
| Con | Community waits a quarter or two, mitigated by a public roadmap answer. | Renewals stay blocked. A provider's resource schema lives in customers' state files, so its reversal cost is high. It may also be built on an API that is not deep enough. | Delays the revenue fix with nothing to show. |
| Fit | Matches signal weighting, deadline and reversal-cost logic | Fails on weighting and on commitment risk | Right idea, wrong place for it |

**Recommendation: A.** Spec work from C runs inside it as a prerequisite, not as its own phase.

## 6. The sequenced plan

All three rows below are surfaces except the spec and telemetry work, which is a prerequisite. Concurrent new-surface builds stay within the capacity number (assumed 1, see section 8).

| Slot | Work | Why now |
|---|---|---|
| Parallel prerequisite | OpenAPI spec as linted source of truth in CI. Depth audit of REST. Per-account and per-endpoint breakdown of the 61%. Per-client telemetry kept permanently. | Gates everything derived. Cheap. Not a surface. |
| 1 | Bulk/warehouse telemetry export | Named deal blocker with a deadline. |
| 2 | CLI | Lowest-risk community ask. Thin over REST. Also serves agents. |
| 3 | Terraform provider | Highest reversal cost of the three, so it goes last and only after the contract is stable. |
| Deferred | Additional SDK languages | Only once the spec generates them and capacity allows. |
| Parked | MCP | No agent signal. When one appears, generate it over the REST spec. |
| Declined | GraphQL, gRPC | No integrator-confirmed pain. |

**Slot 1 detail.**
- The export's shape (file/lake exports or rows pushed through an ELT tool) depends on what the two blocked customers use. Ask them before choosing.
- Version the export schema from day one, because it ripples into customer SQL and dashboards.

**Slot 2 detail.** There is no sibling skill for the CLI, so its design lives here:
- Readable table output for humans.
- JSON for agents.
- Clean stdout/stderr separation.
- This is Plaid's dual-audience pattern.

**Slot 3 gate.** Schedule the Terraform provider only after both are true:
- The depth audit shows every resource the provider would manage is fully API-accessible.
- The contract is declared stable.

If the audit fails, the audit's findings become the work item. The provider moves down until they are fixed.

**Handoffs (all five fields).** The skill's coverage gate requires every surface, scheduled, deferred or declined, to carry audience, demand signal, reversal-cost tier, owner and design owner. Owners are not named in the brief, so every owner is a placeholder.

| Surface | Audience | Demand signal | Reversal tier | Owner | Design owner |
|---|---|---|---|---|---|
| Bulk/warehouse export | BI/data teams | 2 stalled renewals (rank 1) | Medium | TBD, name before kickoff | `@bulk-data-sharing-design`, or `@etl-connector-strategy` if rows sync via an ELT tool |
| CLI | Developers, agents | 400+ reactions (rank 3) | Not tiered by the reference. Treat as medium-high because command names are baked into scripts (my judgment). | TBD | Inline, in this plan |
| Terraform provider | Platform engineers | 400+ reactions (rank 3) | High, because resource schemas live in customer state | TBD | Inline. No dedicated sibling. |
| Python library (existing) | Python developers | 61% UA share (rank 2) | High | TBD | `@sdk-portfolio-strategy` |
| Other SDK languages | Developers | None yet | High | TBD | `@sdk-portfolio-strategy` |
| MCP | Agents | None | Medium | TBD | `@mcp-server-offering`, when scheduled |
| GraphQL | n/a | None | High | n/a | `@public-graphql-api-design`, if ever |
| gRPC | n/a | None | n/a | n/a | `@public-grpc-api-design`, if ever |
| REST contract | All | Existing | Low additive, high breaking | TBD | `@public-api-design-review` |

I could not verify the sibling skills' existence beyond the names this skill lists.

**Gates.**
- **Derivation gate:** the CLI, provider and any generated SDK are scheduled only after the contract is declared stable. This plan satisfies that.
- **Concurrency gate:** at most one new surface in flight under the assumed capacity.

## 7. What to tell the community now

Post a short, dated reply on the Terraform/CLI issue:
- Say what is being built first and why.
- Give the CLI and provider order.
- Name the prerequisite (a stable API contract).

This costs almost nothing, and it addresses the brand risk leadership raised. It matters more than the build order does for the loudest voices.

## 8. Assumptions and what would flip the order

I assumed the following without confirmation:
- Buyer type is "both in the same deal".
- Team capacity is one new surface at a time.
- The REST API and Python library exist, with unknown depth and spec state.
- Quorrel has no webhooks, SQL or MCP surface today. Webhooks were not mentioned, so I did not plan them.

Answers that would change the plan:
- **A renewal deadline before a bulk export could ship.** Then ship the fastest interim, such as scheduled file dumps, with the production export behind it.
- **Capacity of two surfaces.** Run the CLI alongside the export, but never the provider.
- **The depth audit fails.** The provider drops below the audit's findings. The CLI may also be limited.
- **The 61% is one account.** The SDK signal collapses to that account's needs.
- **The reactions are mostly from paying or evaluating accounts.** Move the CLI up and shorten the community wait.
- **RFPs start requiring MCP.** Generate it over the REST spec, last.

## 9. Review cadence

Review quarterly. Reopen early on any of these:
- A new deal blocked on a missing surface.
- Agent demand moving from "none" to RFPs.
- Telemetry contradicting the audience map.
- A scheduled surface's owner losing capacity.

At the next review, re-check:
- The deal-blocker log.
- The per-account user-agent breakdown.
- The depth audit result.

## Prepare before the next review

- Name an owner for each scheduled surface.
- Ask the two blocked accounts what their warehouse is, which sets the export shape.
- Run the per-account breakdown of the 61%.