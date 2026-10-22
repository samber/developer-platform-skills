# Tandemly integration surface order

## Recommendation

Build turnkey payroll connectors first, on a small private API contract. Then publish a narrow REST API with webhooks. Hold everything else until a named signal moves it.

Your board's "API-first" and Sales' "turnkey in an afternoon" are two layers of one plan, not rivals. The buyers are non-technical, so the turnkey layer closes deals. The REST API is the durable foundation underneath, and it ships second.

## Assumptions

I couldn't interview you, so I assumed the answers below. Correct any that are wrong, because several change the order.

| Interview item | Assumed answer |
|---|---|
| Buyer | Non-technical business buyer. Office managers and HR directors write no code. |
| Existing surfaces | None public. |
| Spec | None (no OpenAPI source of truth). |
| Demand signals | Sales names payroll connectors as the deal blocker. There is no per-client telemetry. |
| Agent demand | None known. |
| Capacity | One surface built at a time. One platform engineer, with contractors as extra hands but not extra owners. |
| Deadline | Soft. Deals are closing now, but there is no single RFP date. |
| Mandate | Compounding asset, with an immediate unblock inside it. |

## 1. Audiences and buyers

| Consumer | Who writes the calling code | Buyer | Surface that serves them |
|---|---|---|---|
| Office managers and HR directors | Nobody. They click through setup. | Non-technical economic buyer | Turnkey payroll connectors with a guided connect flow |
| Payroll vendors and integrators | A person at the vendor | Technical user in the deal | Public REST and webhooks |
| HR consultants and customer IT (later) | A person or a generator | Technical user in the deal | Public REST and webhooks |
| BI and analytics consumers | A person writing SQL | Nobody has asked yet | None scheduled |
| AI agents | An agent | Nobody has asked yet | None scheduled |

The first row is who closes deals. The second row is why a REST API still matters.

## 2. Inventory and the central dependency

| Surface | Audience | Depth | Spec-derived or hand-built | Traffic share |
|---|---|---|---|---|
| Public API | n/a | Absent | n/a | n/a |
| Payroll connectors | n/a | Absent (the sales demo is not a product) | n/a | n/a |
| Internal API used by your own UI | Your frontend | Unknown | Hand-built | No telemetry |

- **Spec dependency.** The spec is the plan's central dependency, and it doesn't exist. Every derived surface comes from it: the embedded connect flow, SDKs, docs, and MCP.
- **Foundation sprint.** The derivation gate forbids scheduling a derived surface before its contract is declared stable. So the plan starts with a short, narrow sprint to write and lint an OpenAPI spec. It covers only the resources the first connectors touch, such as employees, organizations, and compliance records.
- **Depth probe to run in that sprint.** For each capability a connector needs, check whether it is reachable by API end to end. The failure mode is a partial flow. If employee sync works but writing results back needs a manual step, "setup in an afternoon" fails mid-demo.

## 3. Demand signals, weighed

1. **Pipeline data (highest weight).** Sales says deals close on turnkey payroll integrations. Ask Sales for the named blocked deals and the specific payroll tools. Count both. Two or three payroll tools probably cover most of the pipeline.
2. **Telemetry (none).** You can't weigh it yet, so instrumenting it is an early plan item. Per-client tagging on the new API will show whether integrators exist at all.
3. **Community and board opinion (third).** The board's push for a public REST API is a real stakeholder signal. It is not a demand signal. No prospect has asked for it.
4. **Agent demand (none).** MCP stays parked.

## 4. Candidate sequences

**A. Spec-first (the board's version).** Public REST API and developer docs first, then connectors on top.
- Pro: the cheapest surface to reverse, and the best long-term foundation.
- Con: it ships nothing your buyers can use. With one engineer, deals stall for a quarter or more.

**B. Embedded-led with a thin foundation (recommended).** A narrow spec, then payroll connectors, then public REST and webhooks.
- Pro: it unblocks the named deals first and still builds the contract underneath.
- Con: it needs discipline to keep the foundation sprint small.

**C. Deal-driven one-off.** Hand-build the one or two connectors Sales names, with no shared contract.
- Pro: it's the fastest path to a demo.
- Con: it's the shallow-integration failure mode. The next connector costs as much as the first, and a public API later means redoing the work.

Candidate B takes C's focus on the one surface Sales named, and A's insistence on a real contract. A pure A is the wrong order for a non-technical buyer. A pure C leaves you with nothing durable.

## 5. Ranked and sequenced plan

Only one surface is in build at a time, to match your capacity.

| # | Surface | Status | Reasoning |
|---|---|---|---|
| 0 | Foundation: narrow OpenAPI spec, per-client telemetry, deal-blocker log | Start now | A prerequisite, not a surface. Keep it to a few weeks and only the resources the connectors need. |
| 1 | Payroll connectors with a guided, no-code connect flow | First, after the spec is declared stable | It addresses the named deal blocker. The buyer needs hours to value, not days. |
| 2 | Public REST (read-heavy v1) plus outbound webhooks | Second | This is the skill's default rung and your board's ask. It extends additively, so early mistakes are cheap. It serves payroll vendors and integrators. |
| 3 | Server SDKs | Deferred | They bake method signatures into customer code, which makes them high reversal cost. Schedule them only once REST is stable and telemetry shows integrators using it. |
| 4 | Bulk export or SQL access | Deferred | Schedule only when a BI blocker appears in the deal log. |
| 5 | MCP | Parked | Schedule it last, generated from the REST spec, only when RFPs or security reviews ask for it. |
| 6 | GraphQL, gRPC, CLI | Declined | No integrator has named a pain they would solve. |

**Build or buy for the connectors.** With one engineer, evaluate an embedded payroll-integration platform or unified payroll API before hand-building each connector. I haven't evaluated specific vendors. This is a decision to make in the foundation sprint, with Sales' payroll-tool list in hand. Buying shortens time to first connector. Hand-building gives more control per connector.

**Contractors.** Use them for connector number two onward, once engineer one has set the pattern. Don't use them to design the contract. Contractors raise the pace of one surface. They don't raise the number of concurrent surfaces.

## 6. Handoffs

Every surface carries all five fields, including the deferred and declined ones.

| Surface | Audience | Demand signal | Reversal-cost tier | Owner | Design owner |
|---|---|---|---|---|---|
| Payroll connectors and connect flow | Office managers, HR directors | Sales: named deal blockers | Medium | Platform engineer, then contractors | Decide inline in this plan. There is no sibling skill for embedded components. |
| REST v1 | Payroll vendors, integrators | Board request. Telemetry once instrumented. | Low if additive, high if breaking | Platform engineer | `public-api-design-review` |
| Webhooks | Integrators | Rides the REST surface | Low-medium | Platform engineer | `webhook-platform-design` |
| SDKs | Integrators | None yet. Needs telemetry showing helper-library share. | High | Unassigned (deferred) | `sdk-portfolio-strategy` |
| Bulk or SQL | BI consumers | None yet | Medium | Unassigned (deferred) | `bulk-data-sharing-design` or `sql-jdbc-access-design`, depending on the signal |
| MCP | Agents | None yet | Medium | Unassigned (parked) | `mcp-server-offering` |
| GraphQL | None | No named pain | High | n/a (declined) | `public-graphql-api-design` if ever promoted |
| gRPC | None | No streaming or latency need | n/a | n/a (declined) | `public-grpc-api-design` if ever promoted |
| CLI | None | None | n/a | n/a (declined) | Inline decision. Copy Plaid's pattern if ever built: table output for humans, JSON for agents. |

## 7. What to tell the board

- The roadmap includes a public REST API as step two, with webhooks.
- It follows connectors because the connectors are what the buyers use, and the public API is built on the same contract.
- Frame the contract as foundation work that has already started, not as a postponement.
- Ask the board to commit to a date for REST v1 rather than a position in a list.

## 8. Review cadence and reopen triggers

Review quarterly. The first review is early January 2027, since today is 2026-10-03. Reopen the plan early if any of these happens:

- A deal is blocked on a surface the plan defers.
- An RFP or security review asks for MCP compatibility.
- Telemetry shows integrator traffic that contradicts the audience map.
- The platform engineer leaves or loses capacity.

At each review, re-check three things rather than re-arguing the plan: the deal-blocker log, the per-client traffic share, and whether any agent signal has appeared.

## 9. Gates

- **Coverage gate.** Every surface in the table above carries all five fields. This passes as written.
- **Derivation gate.** The connect flow and everything after it waits until the narrow spec is declared stable. This is why step 0 comes first.
- **Concurrency gate.** One surface is in build at a time, matching the assumed capacity.

## Open questions

Please answer these, because each can change the order:

1. Which payroll tools has Sales named, and how many deals are blocked on each?
2. Is there a hard date, such as a named deal or RFP, that forces the first connector?
3. Can you really sustain two surfaces at once with contractor help? I assumed one.
4. Does any prospect or security review already ask for an API or for MCP?