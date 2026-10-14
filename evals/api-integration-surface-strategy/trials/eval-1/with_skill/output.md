# Veltrix integration-surface plan, Q4 2026 – Q1 2027

**Next action:** this week, start logging API traffic by API key and user-agent, and diff the OpenAPI file against the live API. Everything below depends on those two results.

I followed `api-integration-surface-strategy`. Its interview is one question at a time, so I filled the answers from your message and marked the guesses. Please correct any wrong ones. The plan changes if the buyer answer or the capacity answer is wrong.

## Bottom line

- **Don't ship an MCP server this quarter.** An MCP server is a thin layer over an API. Yours covers about 60% of the product, and its spec no longer matches the live API. An agent would hit manual walls on 40% of tasks and call endpoints that don't behave as documented.
- **Give the CEO a dated path instead.** Fix the contract, add webhooks, then show an internal MCP demo generated from the verified spec at the end of Q1. A public beta follows in Q2 only if a demand trigger fires.
- **Don't plan per-call agent revenue.** Label it speculative. It has no baseline here (zero agent traffic) and no proven market (see § Per-call pricing).

## 1. Audiences and buyers

| Consumer | Who writes the calling code | Buyer type | Status |
|---|---|---|---|
| Third-party integrators (ERP, e-commerce, shipping) | Developer or consultant | Mixed: ops buyer plus a technical user (assumed) | Served by the REST API, poorly |
| Customer IT teams and BI users | Developer or analyst | Technical user | No evidence of demand yet |
| Non-technical operators | Nobody, they want turnkey integrations | Business buyer | Unknown. Needs confirming. |
| AI agents | An agent | n/a | Zero traffic, zero asks |
| First-party developers | Your team | n/a | Not relevant here |

The buyer-type answer is a guess (mixed). If your buyers are non-technical operations managers who need integrations in hours, an embedded layer moves up. Even then, the API foundation comes first, because retrofitting one later is the expensive direction.

## 2. Inventory

| Surface | Audience | Depth | Spec-derived? | Traffic share |
|---|---|---|---|---|
| REST API | Integrators | **Partial: ~60% of functionality** | No, hand-built | Unknown: no per-client telemetry |
| OpenAPI file | Everyone downstream | Stale, drifts from live API | Hand-written a year ago | n/a |
| Webhooks | n/a | **Absent** | n/a | n/a |
| SDKs, CLI, MCP, bulk, GraphQL | n/a | Absent | n/a | Agent traffic confirmed zero |

**Shallow-coverage flag:** a 60% API means customers finish integrations and then hit a UI-only step. Before claiming "API-first" anywhere, probe each capability and list which flows can't be completed end to end.

**Central dependency:** the spec. Docs, SDKs and MCP all derive from it. At Stripe, Twilio and Cloudflare one OpenAPI source feeds every surface. A drifting spec gets fixed before any derived surface is scheduled.

## 3. Demand signals, weighted

1. **Pipeline and sales blockers (highest weight):** none known. Ask sales for a blocked-deal log going back 12 months.
2. **Telemetry by client type:** not instrumented. Instrumenting it is Q1 work.
3. **Community and customer asks:** webhooks and an SDK are plausible asks, but nobody has asked yet. Run 10–15 customer calls in weeks 1–2.
4. **Agent demand:** none. Logs show zero agent traffic and no customer has asked about MCP. This leaves MCP parked.

The CEO's conference conviction is real, but it is a hype signal and not a demand signal. It does earn a cheap internal demo.

## 4. Candidate sequences and recommendation

| | A. Spec-first (recommended) | B. Embedded-led | C. Deal-driven |
|---|---|---|---|
| Order | Telemetry → spec → coverage → webhooks → derived surfaces by signal | API foundation → embedded components for operators | One surface that sales names |
| Fits when | No named blocker, spec broken, 2 engineers | Buyers are non-technical and need hours-to-value | A deal is blocked on a surface |
| Verdict | **Take this.** Cheapest to reverse, and everything later derives from it. | Revisit if the customer calls show non-technical buyers | **Switch to this the day a blocker is named** |

The CEO's MCP-first option is not on the menu. MCP and SDKs presuppose a stable contract, and every platform that shipped MCP generated it over an existing API.

**Capacity assumption:** two engineers sustain one new surface at a time. Spec, telemetry and coverage work count as foundation, not new surfaces. I also assumed roughly half their time goes to this plan, so please confirm.

## 5. Two-quarter schedule

### Q4 2026 (13 weeks)

| Weeks | Work | Owner | Exit gate |
|---|---|---|---|
| 1–2 | Log API traffic by key, endpoint and user-agent. Send sales a blocker-log request. Hold 10–15 customer calls. Measure spec drift against the live API. | Eng 1 telemetry; Head of platform runs the calls | Baseline traffic share by client type |
| 3–6 | Reconcile the spec. Add CI linting and contract tests against the live API. Write an additive-only change policy. | Eng 1 | **Contract declared stable** (CI green, drift zero) |
| 3–13 | Coverage depth: rank the missing 40% by customer asks and support tickets. Ship the top flows end to end. | Eng 2 (~30%) | Each shipped flow completes with no UI step |
| 7–13 | **Webhooks MVP.** Core inventory events (stock changed, low-stock threshold, PO received). | Eng 1 | Signed, retried, documented |
| 10–12 | **Internal MCP demo.** Generated from the verified spec, read-only, not offered to customers. 2–3 days. | Eng 2 | Demo for the CEO. No public commitment. |
| 13 | Quarterly review (see § 7) | Head of platform | Q1 slot allocated by evidence |

### Q1 2027: one new surface, chosen by evidence at the week-13 review

| If the review shows | Build |
|---|---|
| A named blocked deal | That surface (sequence C) |
| Written agent demand (proposed trigger: one RFP or security review requiring MCP, or 3+ customers asking in writing, or agent traffic above 1% of calls) | **Public read-only MCP beta**, generated from the spec, OAuth-scoped to existing customer auth, no per-call pricing |
| Telemetry or calls show strong demand for helper libraries | One generated SDK, in the customers' most common language |
| BI or warehouse asks | Bulk export design, not SQL access |
| None of the above | Keep extending coverage toward ~85–90%, add webhook events, keep MCP internal |

The agent-demand thresholds are my proposals, not sourced figures. Adjust them.

## 6. Per-surface handoffs

| Surface | Status | Audience | Demand signal | Reversal tier | Owner | Design owner |
|---|---|---|---|---|---|---|
| REST (extend) | Scheduled | Integrators | Weak: 60% coverage gap, to confirm via calls and logs | Low (additive) / High (breaking) | Eng 2 | `public-api-design-review` |
| OpenAPI and docs | Scheduled (foundation) | All derived surfaces | Spec drift is a hard dependency | n/a | Eng 1 | `public-api-design-review` |
| Webhooks | Scheduled, Q4 | Integrators | **Inferred** (no webhooks means polling). Confirm via telemetry and calls. | Low-medium | Eng 1 | `webhook-platform-design` |
| MCP, internal demo | Scheduled, Q4 | CEO and internal | None. Hype only. | None (not public) | Eng 2 | `mcp-server-offering` |
| MCP, public beta | Conditional, Q1 | Agent clients | Needs a trigger from § 5 | Medium | Eng 2 | `mcp-server-offering` |
| Generated SDK | Deferred | Integrators | None yet. Needs telemetry or asks. | High | TBD | `sdk-portfolio-strategy` |
| Bulk export or ETL | Deferred | BI users | None yet | Medium | TBD | `bulk-data-sharing-design` or `etl-connector-strategy` |
| Embedded components | Deferred | Operators | Unknown. Depends on the buyer-type answer. | Medium | TBD | Inline: revisit if calls show non-technical buyers |
| SQL/JDBC | Declined | BI users | None | Medium-high | n/a | `sql-jdbc-access-design` if reopened |
| GraphQL | Declined | n/a | No integrator-confirmed pain. It adds 20–40% build overhead and a binding schema. | High | n/a | `public-graphql-api-design` if reopened |
| gRPC | Declined | n/a | No streaming or latency-budget audience | High | n/a | `public-grpc-api-design` if reopened |
| CLI | Declined | n/a | None. If built, use readable tables for humans and JSON on stdout for agents. | Low-medium | n/a | Inline |
| Per-call agent pricing | Declined | n/a | None | n/a | n/a | n/a |

## Per-call pricing

- **Zero baseline:** you have no agent traffic to meter, so any revenue forecast would be invented.
- **Unproven market:** the skill's reference notes say per-call agent payments are unproven and that the x402 protocol's volumes collapsed after peaking in Q4 2025. Re-check those figures before quoting them to the CEO.
- **Retention risk:** an API in customers' production code is a retention asset. Metering it could push your existing 400 customers away.
- **Safer alternative:** include MCP in existing plans with fair-use rate limits. Measure for a quarter, then revisit pricing if agent traffic is real.

## 7. Review cadence

- **Next review:** week 13 of Q4, then quarterly.
- **Early-reopen triggers:**
  - A deal is blocked on a missing surface.
  - An agent-demand signal appears (RFP, written asks, agent traffic).
  - Telemetry contradicts the audience map.
  - A scheduled surface's owner loses capacity.
- **Evidence to re-check:** traffic share by client type, spec drift (should be zero), the blocker log, share of flows completable end to end, webhook polling-versus-push adoption.

## Gates

- **Coverage gate:** every surface above has all five fields. ✅
- **Derivation gate:** MCP, SDKs and docs are scheduled only after the week-6 contract-stable declaration. ✅
- **Concurrency gate:** at most one new surface runs at a time. Webhooks occupy the slot in Q4. ✅

## Questions to confirm

1. Who is the buyer: developers, non-technical operators, or both?
2. What share of the two engineers' time is really available?
3. Does the CEO have an external date, such as a customer, board or conference commitment? If so, the demo is the right deliverable for it.
4. Do any customers already export data to BI tools by CSV? That would move bulk export up.

I didn't write `developer-platform-context.md` because you didn't ask me to. The decisions above are ready to record there if you want them saved.