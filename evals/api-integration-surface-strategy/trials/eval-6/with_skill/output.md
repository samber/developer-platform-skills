# Nuvaris integration-surface roadmap, next year

I read the skill and its two reference files and followed its six steps. The skill normally interviews you one question at a time. I couldn't do that in a single deliverable, so I filled the gaps with explicit assumptions. Section 0 lists them, and any that's wrong changes the plan.

## 0. Assumptions to confirm

| # | Interview item | Assumed | If wrong |
|---|---|---|---|
| 1 | Buyer type | Both: an economic buyer (finance) plus a technical user proving it | If it's mostly finance buyers, add an embedded-component layer (Section 5). |
| 2 | Spec state | OpenAPI is a linted source of truth in CI | If it drifts, fixing it comes before everything else. |
| 3 | Depth | Not yet probed whether every spend flow is fully API-reachable | Shallow coverage would hit warehouse, CLI and agents alike. |
| 4 | Demand signals | Pipeline: two named lost deals (strongest). Agents: CS anecdotes only, no telemetry and no RFPs. | Agent demand is "customer questions only" until telemetry says otherwise. |
| 5 | Capacity | Two concurrent new-surface builds at most, from four engineers (the rest goes to run and support) | The concurrency gate scales with this number. |
| 6 | Deadline | None hard, but the lost deals make warehouse sharing urgent | A hard deadline would pull the warehouse even further forward. |
| 7 | Mandate | Compounding roadmap, not a one-off unblock | |

## 1. Audiences

| Consumer | Who writes the calling code | Buyer | Surface that persists for them |
|---|---|---|---|
| Finance and BI analysts | SQL and BI tools | Economic buyer | Warehouse share |
| Third-party integrators (ERP, HRIS) | A person | Technical user | REST, webhooks, SDKs |
| Platform and ops engineers | A person or a script | Technical user | CLI, SDKs |
| AI agents and assistants | An agent, on behalf of a customer user | Both | REST today, MCP later |

This is a per-audience map, not one ladder every consumer climbs.

## 2. Inventory

| Surface | Audience | Depth | Spec-derived? | Traffic share |
|---|---|---|---|---|
| REST | Integrators | To probe (see below) | Spec is source | Unknown |
| Webhooks | Integrators | To probe | Hand-built | Unknown |
| SDKs | Integrators | Generated | Yes | Unknown |
| Warehouse, CLI, MCP | | Absent | | |

- **Depth probe, week 1.** For each core spend flow, list the steps (create, approve, reimburse, reconcile, export, user and policy admin) and mark each one API-reachable or UI-only. Any UI-only step is a named gap. A warehouse share exposes read data, so gaps matter more for the CLI and for agents.
- **Telemetry gap.** You can't read client-type traffic today. Instrumenting it is the first plan item.
- **Spec stability.** Your spec is clean, but "stable" needs a declaration: a written no-breaking-changes policy plus a CI breaking-change check. Nothing derived (CLI, MCP) is scheduled until that is declared. This is the derivation gate.

## 3. Demand signals, weighted

1. **Two lost enterprise deals over Snowflake.** This is pipeline data, which carries the highest weight. It outranks everything else here.
2. **Agent traffic.** This is a CS report, not telemetry, so it is real but unmeasured. It justifies instrumenting and hardening. It does not yet justify building an MCP server.
3. **CLI.** No demand signal is named. Your staff engineer's spec is the only driver, and an internal proposal is the weakest signal tier. That makes the CLI the lowest-priority surface of the three, and the plan says so openly.

## 4. Candidate sequences

| | A. Spec-first derivation | B. Deal-driven | C. Blend (recommended) |
|---|---|---|---|
| Order | Telemetry and spec hardening, then SDK/CLI/MCP, warehouse last | Warehouse first, rest later | Warehouse first, with telemetry and the spec gate running in parallel as small items |
| Upside | Cleanest foundation | Fixes the lost-deal pattern fastest | Same as B, and adds the data that later re-ranks need |
| Downside | Ignores the deal blocker for months | CLI and MCP get scheduled on gut feel | Needs discipline to keep telemetry from being skipped |

**Recommendation: C.** It follows the skill's rule that a named deal blocker outranks volume metrics. It also follows the observed Segment pattern, where bulk/warehouse came mid-sequence because BI consumers demanded it. REST and webhooks are already done, so the "default rung" is already in place.

## 5. Ranked plan, per surface

| Order | Surface | Decision | Reversal cost |
|---|---|---|---|
| 0 | Telemetry and spec gate | Not a new surface. Do first, in weeks. | Low |
| 1 | Warehouse sharing (Snowflake) | Build | Medium |
| 2 | CLI | Build, thin and spec-derived | Not tiered in the skill. Treat as medium-high: the command surface and JSON output become contracts. |
| 3 | Agent access | Harden now. Build MCP only when a signal fires. | Medium (MCP tool names) |
| Later | Other warehouses, embedded components | Deferred | |
| Declined | GraphQL, gRPC, SQL/JDBC | Declined | |

### 0. Telemetry and spec gate (Q4 2026, about 2 to 4 weeks, 1 engineer)

- Tag every request by client type: SDK user-agent, CLI (future), known agent user-agents, raw HTTP. Twilio's SDK investment was justified by exactly this kind of data (77% of requests carried a helper-library user-agent).
- Add an explicit agent-client header convention, for example a documented `User-Agent` suffix. Without it, agent traffic is invisible.
- Run the depth probe from Section 2.
- Declare spec stability: a breaking-change check in CI and a versioning policy.

### 1. Warehouse sharing

- **Audience:** finance and BI consumers.
- **Signal:** the two lost deals.
- **Design owner:** `samber/developer-platform-skills@bulk-data-sharing-design`. The signal points to a direct Snowflake share, not rows synced through an ELT tool. If the lost prospects would accept Fivetran or Airbyte, `@etl-connector-strategy` is the cheaper alternative.
- **First step, this week:** call the two lost prospects and ask exactly what they needed. Was it a native Snowflake share, a marketplace listing, or just "the data in Snowflake by any means"? The answer changes the build size a lot.
- **Decisions for the design phase:**
  - Per-tenant isolation (this is financial data, so it must be provable).
  - A versioned, documented share schema. Schema changes ripple into customer SQL and dashboards, so use additive-only changes plus versioned views.
  - Freshness SLA and a deletion/retention story.
  - Cross-region and cross-cloud delivery.
  - Which tables are in the share, which are out, and why.
- **Scope rule:** one warehouse target only. Databricks, BigQuery and S3 exports wait until demand shows them.
- **Timeline (estimate):** design plus a design-partner pilot in Q4/Q1, GA by the end of Q1 or in Q2, depending on the discovery call.
- **Capacity:** 2 engineers.

### 2. CLI

Your staff engineer's spec has pretty ANSI tables. Keep the tables, but they can't be the only output. The skill's model is Plaid's 2025 CLI, which serves two audiences with one surface:

- **Humans:** readable table output, only when stdout is a TTY. Honor `NO_COLOR`.
- **Agents and scripts:** `--output json` on every command, plus automatic JSON when stdout is piped.
- **Streams:** data on stdout only. Progress, warnings and errors go to stderr.
- **Exit codes:** documented and stable (success, usage error, auth error, API error).
- **Contract:** the JSON shape is the public contract and is never ANSI-decorated. The table layout is explicitly *not* a contract. Pretty output that scripts parse becomes a Hyrum's Law trap.
- **Derivation:** generate commands from the OpenAPI spec where possible. Hand-write only auth, config and a few workflow commands.

- **Audience:** platform engineers and agents that shell out.
- **Signal:** none named. Before committing, check whether the staff engineer's case rests on customer asks, and gather that evidence. Q1 telemetry will show how many API users are scripters.
- **Design owner:** no sibling exists, so these decisions live here in the plan.
- **Timeline:** start in Q2, after the warehouse is in pilot and the spec gate is passed. GA is in Q2/Q3.
- **Capacity:** 1 engineer.

### 3. Agent access

Split this into two different things:

**3a. Make the existing API safe and legible for agents (now, small).**
Agents are already calling you. This is a spend-management API, so a mistaken agent can approve or move money.
- Scoped, least-privilege tokens, with read-only as the easy default.
- Human-confirmation or approval-threshold handling for money-moving writes.
- Idempotency keys, clear machine-readable errors, and sane rate limits.
- Audit logs that identify an agent as the caller.
- Review the REST contract with `samber/developer-platform-skills@public-api-design-review`.

**3b. MCP server (gated).**
- Park it until a signal fires: an RFP or security review requiring MCP, or telemetry showing agent traffic is material.
- When it fires, generate it from the OpenAPI spec, and prefer a managed platform over a hand-build. Every platform that shipped MCP (Stripe, Cloudflare partners, AWS) derived it from an existing API.
- Hand-building only makes sense if AI access to your data is itself the paid product. It isn't here.
- Treat auth as a real product requirement. Only about 8.5% of public MCP servers implement the mandatory OAuth 2.1.
- Do not plan any per-call agent-monetization revenue. It is speculative and the observed volumes are tiny.
- **Design owner:** `samber/developer-platform-skills@mcp-server-offering`.
- **Decision date:** the Q3 review (Section 7).

### Deferred and declined

- **GraphQL: declined.** No integrator has named a client-driven-access pain. It carries roughly 20-40% extra build overhead and a binding schema.
- **gRPC: declined.** No backend-streaming audience.
- **SQL/JDBC: declined.** The warehouse share covers BI. Revisit only if customers want live queries instead of shares.
- **Embedded components: deferred.** If the finance-buyer side of your deals needs approval or reconciliation widgets inside partner products, that's a separate question. The API foundation you already have is the right base for it.
- **More warehouse targets: deferred.** Add one at a time, only on evidence.

## 5b. Per-surface handoff table (coverage gate)

| Surface | Audience | Demand signal | Reversal tier | Owner | Design owner |
|---|---|---|---|---|---|
| REST | Integrators | Existing | Low (additive) / High (breaking) | Engineer 4 (run) | `public-api-design-review` |
| Webhooks | Integrators | Existing | Low-medium | Engineer 4 (run) | `webhook-platform-design` |
| SDKs | Integrators | Existing | High | Engineer 4 (run) | `sdk-portfolio-strategy` |
| Warehouse share | BI and finance | 2 lost deals | Medium | Engineers 1 and 2 | `bulk-data-sharing-design` |
| CLI | Platform engineers, agents | None named (staff-engineer proposal) | Medium-high (my call) | Engineer 3 | Inline, Section 5 |
| Agent access hardening | Agents | CS reports | Medium | Engineer 3, shared | `public-api-design-review` |
| MCP server | Agents | None yet (gated) | Medium | Unassigned until triggered | `mcp-server-offering` |
| GraphQL | None | None | High | n/a (declined) | `public-graphql-api-design` if ever revisited |
| gRPC | None | None | n/a (declined) | n/a | `public-grpc-api-design` |
| SQL/JDBC | None | None | n/a (declined) | n/a | `sql-jdbc-access-design` |
| Embedded components | Finance buyer | Unknown (assumption 1) | Medium | n/a (deferred) | Inline, to decide |

Owners are role placeholders. Name the real people and swap them in.

## 6. Quarterly shape

This is an estimate, not a commitment. It depends on the discovery call and on assumption 5.

| Quarter | Concurrent new surfaces (max 2) | What lands |
|---|---|---|
| Q4 2026 | 1 (warehouse) | Telemetry live, depth probe, spec gate, warehouse design and pilot |
| Q1 2027 | 1 (warehouse) | Warehouse GA, agent-access hardening shipped |
| Q2 2027 | 2 (warehouse hardening, CLI) | CLI beta |
| Q3 2027 | 1 (CLI) | CLI GA, MCP go/no-go |

The concurrency gate holds: no quarter has more than two new surfaces, and most have one.

## 7. Review cadence

- **First review:** January 2027, then quarterly.
- **Re-check at the next review:**
  - Telemetry: what share of traffic is agents, SDKs and scripters?
  - Did the deal-blocker log empty or refill?
  - Did the warehouse pilot partner convert?
  - Is there any real customer ask for the CLI?
- **Reopen the plan early if:**
  - A deal is blocked by a missing surface (for example another warehouse).
  - An RFP or security review requires MCP.
  - Telemetry contradicts the audience map.
  - A surface owner loses capacity.

## Failure modes to avoid

- Jumping to MCP because everyone is talking about agents.
- Shipping the CLI with tables as its only machine-readable output.
- Claiming "API-first" before the depth probe is done.
- Opening a second warehouse target before the first has a design partner.

## Questions that would change this plan

1. What exactly did the two lost prospects need from Snowflake: a native share, a listing, or just access by any route?
2. Who is the buyer in a typical deal: finance only, or finance plus a technical user?
3. Is the OpenAPI spec really enforced in CI, and are all spend flows reachable through the API?
4. How many surfaces can four engineers sustain? I assumed two.
5. Is there a hard date from a deal or an RFP?