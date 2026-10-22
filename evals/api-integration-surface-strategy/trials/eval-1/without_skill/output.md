# Integration-Surface Plan: Q4 2026 and Q1 2027

## Recommendation

Fix the API foundation first, ship webhooks, and ship a small read-only MCP server built on that foundation. Do not launch per-call agent pricing. Revisit pricing once you have real agent traffic.

- **MCP is a thin layer over your API.** Today the API covers about 60% of the product, the spec is wrong, and nothing is pushed to customers. An MCP server on that base would be a demo, not a product.
- **Webhooks have the strongest demand signal.** Inventory customers sync stock, POs, and orders with ERPs and storefronts. Polling is their only option today. I'm inferring this from the product category, so confirm it in the Phase 0 interviews.
- **MCP still gets a date.** Once the spec is accurate, a curated read-only MCP is about 3–4 engineer-weeks. That gives the CEO a real "AI-native" answer this quarter without distorting the roadmap.

## Assumptions to check

- Two engineers at roughly 70% availability after on-call and support gives about 30 engineer-weeks per quarter. Adjust the plan if the real figure is lower.
- The API is versionable and has some auth and rate-limiting today.
- "Zero agent traffic" means you have checked user-agents and OAuth clients. If you haven't, add that to Phase 0.

## Q4 2026 (Oct–Dec)

### Phase 0: Discovery (weeks 1–2, about 2 engineer-weeks)

1. Rank endpoints by call volume and by customer count from the logs.
2. List the missing 40% of functionality and rank it by customer demand.
3. Interview 10–15 customers, mixing large and small, about their integration pain: ERP sync, storefront sync, reporting, manual CSV work.
4. Ask each of them directly: "Are you using or planning AI agents against inventory data?" Record the answers verbatim.
5. Tag agent traffic going forward (see Phase 3).

**Output:** a one-page ranked list of integration needs. It also becomes your evidence base for the CEO.

### Phase 1: Make the spec true (weeks 1–5, about 5 engineer-weeks)

1. Generate OpenAPI from the code, or add contract tests that diff live responses against the spec.
2. Make **CI fail on drift**. This is the real fix. A rewritten file will rot again within a year.
3. Standardize errors, pagination, filtering, and idempotency keys on write endpoints.
4. Add scoped API keys (read-only vs read-write, per resource group) and per-key rate limits. MCP and webhooks both depend on these.
5. Publish the reference docs from the spec.

**Exit criterion:** the contract tests are green in CI and the published docs match the live API.

### Phase 2: Webhooks v1 (weeks 4–10, about 6 engineer-weeks)

1. Use a transactional outbox so events are never lost or duplicated at the source.
2. Ship 6–8 events, chosen from the Phase 0 interviews. Likely candidates:
   - `inventory.adjusted`
   - `inventory.low_stock`
   - `purchase_order.created` and `purchase_order.received`
   - `order.fulfilled`
   - `item.created` and `item.updated`
3. Sign every delivery with HMAC and a timestamp, and retry with exponential backoff.
4. Give customers a delivery log, a manual replay, and subscription management via both the API and the UI.
5. Document event payloads in the same spec.

**Exit criterion:** 3 design-partner customers are running in production.

### Phase 3: MCP server beta (weeks 8–12, about 4 engineer-weeks)

1. Build a **remote** server with OAuth. Tokens are tenant-bound and use the Phase 1 scopes.
2. Ship **read-only** tools only, about 10–15.
3. Design tools around tasks, not endpoints, for example `find_low_stock_items`, `get_item_history`, and `list_open_purchase_orders`. Mirroring the REST API 1:1 produces poor tool quality.
4. Treat free-text fields (item names, notes, supplier comments) as untrusted input. They can carry prompt injection into a customer's agent.
5. Log every call with the client ID. Tag all agent traffic from this point on.
6. Dogfood it internally, then give it to 3–5 willing customers.

**Exit criterion:** the beta is live, with a usage dashboard showing calls by client and tool.

### Q4 capacity

| Item | Engineer-weeks |
|---|---|
| Phase 0 | 2 |
| Phase 1 | 5 |
| Phase 2 | 6 |
| Phase 3 | 4 |
| API gap-closing (start) | 5 |
| Buffer | 5 |
| **Total** | **27** |

Start closing API gaps in parallel at low priority, in the order Phase 0 produced. About 30 engineer-weeks are available, so the buffer is real.

## Q1 2027 (Jan–Mar)

1. **Close the API gaps (about 10 engineer-weeks).** Take the highest-demand missing functionality first. Target 85% of *usage-weighted* functionality, not 100% of features.
2. **Webhooks v1.1 (about 4 engineer-weeks).** Add the events customers requested and improve observability: failure alerts and an endpoint-health view.
3. **MCP write tools (about 5 engineer-weeks), only if the read-only beta shows usage.** Required guardrails:
   - dry-run or explicit confirmation
   - idempotency keys
   - quantity and value limits
   - a full audit log
   - separate write scope
4. **Developer experience (about 4 engineer-weeks).** Generate TypeScript and Python SDKs from the spec, add worked examples, and publish an `llms.txt`.
5. **Buffer and maintenance (about 7 engineer-weeks).**

## Pricing: do not charge agents per call

- **You can't identify "agents" reliably.** An agent calling your API looks like any script. You'd be pricing a category you can't measure.
- **It taxes your most engaged customers.** A customer who integrates deeply is less likely to churn. Per-call fees punish exactly that behavior, and customers will route through plain scripts to avoid them.
- **There is no demand data yet.** Zero agent traffic means there is no volume to price. Any number you pick now is a guess.
- **Customers may see it as double-billing.** They already pay for the product, and the agent acts on their data on their behalf.

**What to do instead:**

1. Include API, webhooks, and MCP in current plans, with generous rate limits.
2. Meter by client and tool from day one, so the data exists.
3. Run the decision gate below at the end of Q1.
4. If the CEO wants a revenue story now, offer tiered rate limits or higher webhook and API quotas on upper plans. That's a normal packaging lever and it carries no new risk.

## Decision gate (end of March 2027)

Review these numbers:

- Number of customers with weekly MCP calls.
- Read-to-write ratio, once write tools exist.
- Webhook adoption: customers with active subscriptions, and events delivered.
- Share of API traffic coming from agent clients.
- Interview signal: how many customers asked for agent access unprompted.

Suggested decision rules, which you should adjust to your own numbers:

- Fewer than about 5 customers using MCP weekly: keep it in maintenance mode and put the effort into the API and webhooks.
- Sustained growth in agent traffic: design usage-based pricing with real data, in Q2.
- Either way, report the numbers to the CEO with the plan, not a recommendation alone.

## Explicitly not doing

- Per-call agent billing (see above).
- Hand-written SDKs. Generate them.
- GraphQL, A2A, or other protocols.
- MCP marketplace listings and marketing launches, until usage exists.
- 100% API coverage as a goal.

## Risks

| Risk | Mitigation |
|---|---|
| CEO sees the plan as "not AI-native" | Frame the MCP beta as the AI-native deliverable, with a date. Show that it ships on solid infrastructure and that the gate decides expansion. |
| Spec drift returns | CI contract tests (Phase 1). |
| Webhook reliability issues hurt trust | Outbox, retries, replay, and 3 design partners before general availability. |
| Tenant data leaks through MCP | Tenant-bound tokens, scope tests, security review before the beta opens. |
| Two engineers is thin | The buffer covers slips. If Phase 2 runs late, cut MCP scope, not webhooks. |

## Talking points for the CEO

- "We'll have an MCP server in beta by end of December. It's built on a verified API, so it won't break on customers."
- "No customer has asked for it yet, so we'll ship read-only first, measure, and expand with data."
- "We'll decide on agent pricing in March using real usage, not before. Charging early risks hurting the integrations that keep customers."

I can also draft the Phase 0 customer interview script, or the MCP tool list for the Phase 3 beta, if you want either.