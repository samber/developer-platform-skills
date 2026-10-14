# Nuvaris surface roadmap, next year

## Recommendation

Sequence the work: **warehouse sharing first, agent access second, CLI third and thin.** Warehouse sharing is the only surface with lost revenue attached. Agent access is mostly hardening what you already have. The CLI is the least strategic of the three, because your OpenAPI spec and SDKs already cover the scripting use case.

Four engineers can't do all three at full depth. Fund warehouse sharing with two engineers, agent access and CLI with one, and keep one flex engineer for the first half. Cut CLI scope before you cut warehouse scope.

## Unknowns to settle in the first two weeks

These change the plan, so answer them before committing dates.

1. **What did the two lost prospects actually ask for?** Possible answers are a Snowflake Secure Share, a connector or ETL feed, or just "export to Snowflake". Get the exact wording from the sales call notes and ask the prospects' data teams directly. A Secure Share is a different build from a scheduled export.
2. **Which Snowflake cloud and region do those prospects sit in?** Native sharing works within one cloud region. Cross-region and cross-cloud sharing needs replication, which adds cost and latency.
3. **Do you already have an internal warehouse or lake with clean per-tenant transaction data?** If not, building that pipeline is most of the work, not the sharing layer.
4. **What does the current API traffic from AI assistants look like?** Pull user-agent and token data. Check which assistants they are, which endpoints they hit, and read-versus-write ratio. Customer success's anecdote is a hypothesis until the logs confirm it.
5. **What are the compliance constraints on exporting spend data?** Think SOC 2 scope, PII in cardholder and employee fields, and contractual data-residency terms.

## Surface 1: Warehouse sharing

**Goal:** a customer's data team can query their own Nuvaris transactions in Snowflake without building a pipeline.

**Design decisions**
- **Start with Snowflake Secure Data Sharing.** It's zero-copy and gives the customer live data, which is what the lost deals wanted.
- **Isolate tenants hard.** Use per-customer shares or secure views with row-level filtering. Test cross-tenant leakage explicitly. For a spend product, a leak is a company-ending bug.
- **Publish a versioned data contract.** Cover tables, column semantics, currency and timezone handling, soft-delete behavior, and freshness SLA. Treat schema changes like API breaking changes.
- **Decide pricing and packaging early.** Warehouse sharing is likely an enterprise-tier feature. Settle that before launch so sales can quote it.
- **Add Databricks Delta Sharing and BigQuery later,** only when a signed or pipeline deal asks. Don't build them speculatively.

**Phasing**
- **Q1:** discovery with the two lost prospects and 3–5 design partners. Build the internal per-tenant export pipeline if missing. Draft the data contract.
- **Q2:** private beta with design partners on one Snowflake region. Run a tenant-isolation test suite and an audit-log review with security.
- **Q3:** GA for the main regions, with replication for others if demand justifies the cost. Publish docs and a sample dbt or SQL starter.
- **Q4:** the second warehouse (Databricks or BigQuery) if pipeline demands it. Consider a Snowflake Marketplace listing for discoverability.

**Success measures:** the two lost deals are re-engaged or similar deals are won, design-partner time-to-first-query, freshness SLA met, and zero isolation incidents.

**Main risks:** the internal data pipeline is bigger than expected, cross-region replication costs, and data-quality complaints now exposed to customers' analysts.

## Surface 2: Agent access

**Goal:** AI assistants can use Nuvaris safely and effectively, and customers stay in control of what they do.

**Start with measurement.** Understand current agent traffic before building anything (unknown 4). The answer decides how much of this is real demand.

**Build in this order**
1. **Agent-readable API.** Improve OpenAPI descriptions so a model can pick the right endpoint: clear operation summaries, examples, and error messages that say what to do next. Publish `llms.txt` and docs in Markdown. This is cheap and helps every agent immediately.
2. **Scoped, revocable credentials.** Add narrow API tokens or OAuth scopes: read-only, per-resource, and expiring. Add a per-token audit trail that distinguishes agent calls from human ones. This is the foundation for everything else.
3. **Safety on writes.** Spend management means agents can approve payments or change budgets. Require idempotency keys on writes, add dry-run or preview modes, and support a **human-approval step** for high-risk actions such as approvals above a threshold. Start agents on read access by default.
4. **MCP server.** Build a thin remote MCP server over the existing API, with a deliberately small tool set (a dozen or fewer well-named tools, not one per endpoint). Use OAuth for auth. Generate as much as possible from the OpenAPI spec so it doesn't become a second API to maintain.
5. **Agent-aware limits.** Rate limits and quotas tuned for agent loops, with clear 429 responses and retry guidance.

**Phasing**
- **Q1:** traffic analysis, `llms.txt`, OpenAPI description cleanup, scoped tokens design.
- **Q2:** scoped tokens and audit trail shipped. Read-only MCP server in beta with a few customers.
- **Q3:** write tools behind approval flows. MCP GA. Admin controls for customers (enable, disable, view agent activity).
- **Q4:** iterate from usage data. Consider listings in assistant directories.

**Success measures:** share of API traffic from scoped agent credentials, task success rate on a fixed set of agent test tasks, and zero unapproved high-risk actions.

**Main risks:** prompt injection through transaction fields (merchant names and memos are attacker-controlled text that an agent will read), an over-broad write surface, and customer security teams blocking adoption without admin controls.

## Surface 3: CLI

**Goal:** developers and operators can script and explore Nuvaris from a terminal and from CI.

**Feedback on your staff engineer's spec.** Pretty ANSI tables are fine as the interactive default, but they can't be the primary design. A CLI's most important consumers are scripts, CI, and increasingly agents, and all of them need machine output.

Change these in the spec:
- **Detect a TTY.** Pretty tables only when stdout is a terminal. Otherwise emit JSON.
- **Add `--output json|table|yaml` on every command,** and make the JSON schema stable and documented.
- **Define exit codes and put errors on stderr** in a structured form.
- **Support non-interactive auth:** tokens from environment variables for CI, plus a browser login for humans. Reuse the same scoped tokens as agent access.
- **Respect `NO_COLOR`** and don't prompt when there's no TTY. Add `--yes` for destructive actions.
- **Generate commands from the OpenAPI spec** rather than hand-writing them, with hand-built commands only for a few workflows (login, a "tail recent transactions" view, config). This keeps maintenance close to zero as the API grows.

**Scope guard:** ship a small command set. Cover auth, listing and getting core resources, an export command, and webhook testing and replay (a real pain point worth solving). Don't rebuild every endpoint by hand.

**Phasing**
- **Q2:** revise the spec as above. Build the generated core and auth. Internal dogfooding.
- **Q3:** public beta. Distribute through Homebrew, a binary release, and a package manager your customers use.
- **Q4:** GA, plus shell completion and a CI-friendly GitHub Action if usage justifies it.

**Success measures:** weekly active CLI users, share of CLI calls using JSON output (a sign scripts are using it), and webhook-replay usage.

**Main risk:** a hand-built, table-first CLI becomes a maintenance burden that lags the API.

## Cross-cutting work

- **One identity and permission model** across SDKs, CLI, MCP, and warehouse access: scoped tokens, audit logs, and admin controls. Build it once in Q1–Q2.
- **Docs treated as a product** for humans and agents alike. Add a single "ways to integrate" page that tells a reader which surface to pick.
- **A release and versioning policy** so the data contract, MCP tool set, and CLI output schemas don't break consumers silently.

## Capacity view

| Quarter | Engineer 1–2 | Engineer 3 | Engineer 4 |
|---|---|---|---|
| Q1 | Warehouse pipeline and contract | Traffic analysis, scoped tokens | Tokens and permission model |
| Q2 | Warehouse private beta | MCP read-only beta | CLI core |
| Q3 | Warehouse GA | MCP writes and approvals, GA | CLI beta |
| Q4 | Second warehouse or marketplace | Iterate on agent usage | CLI GA |

## What I'd cut first if capacity slips

1. CLI polish (completions, Actions)
2. The second warehouse target
3. MCP write tools (keep read-only until the approval flow is solid)

Don't cut the tenant-isolation testing or the audit trail.

## Next steps

1. Get the exact asks from the two lost deals (unknown 1).
2. Pull the agent-traffic breakdown (unknown 4).
3. Send your staff engineer the CLI feedback above.