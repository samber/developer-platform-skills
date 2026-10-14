# Corvale MCP tool surface redesign plan

I read the `mcp-server-offering` skill and its references. I couldn't ask the skill's clarifying questions interactively, so each answer below is an assumption you should confirm. Section 8 lists them and says what each one changes.

I only know six of your 74 tool names. The target surface below is a hypothesis built from those six and from typical freight-invoicing jobs. Validate it against your telemetry and tickets (step 1 of the sequence) before building.

## 1. Diagnosis

| Symptom | Likely cause | Fix |
|---|---|---|
| Claude and Cursor pick the wrong tool | Near-duplicate tools (`getInvoiceById` / `getInvoiceList`, `getCarrier` / `getCarrierRates`). Descriptions are probably auto-copied from OpenAPI summaries. Names are unprefixed camelCase, so they collide with other servers' `getX` tools. | Collapse to workflow tools. Rewrite every description. Use `corvale_` snake_case names. |
| Agent "runs out of room" | 74 tool definitions load before any work starts. Tool metadata alone can consume 40–50% of the context window. | Cut the surface to 5–15 tools and trim response payloads. |
| `patchInvoice` and `deleteInvoice` exist | Live-only destructive tools, with no tier, dry-run, or approval gate. The skill lists this as a direct review finding. | Hotfix now (section 2), then redesign (section 4). |

The industry pattern is that curated beats comprehensive. The median across 1,412 analyzed servers is 5 tools (Bloomberry, a single-source analysis, so directional). Vendor guidance converges on 5–15 tools designed top-down from workflows. Mirroring endpoints is the named anti-pattern, and you have shipped it.

## 2. Week 0 hotfix (before any redesign)

1. Check what `deleteInvoice` does in v3: hard delete, soft delete, or void.
2. Remove or disable `deleteInvoice` on the current server. Nothing about the redesign needs it live.
3. Gate `patchInvoice`, and every other write in the 74, with at least a scoped read-only credential option. Verify by test that a read-only credential cannot reach the write tools. One documented vendor bug shipped write tools despite the read-only flag being set.
4. Check whether the server forwards the caller's bearer token to your REST API. The spec forbids that (confused deputy). If it does, put it on the fix list.

## 3. Tool inventory (do before designing)

1. Export all 74 tools. Tag each with the job it serves, its REST verb, and its 6-month call count from server logs.
2. Pull the wrong-tool tickets. Turn each into a **golden prompt**: the user's task, plus the tool the agent should have called. This corpus is your before/after benchmark.
3. Measure the baseline. Count the tokens of the serialized `tools/list` response, and score the golden prompts in Claude and Cursor against the current server.
4. Classify every tool:
   - **Merge into a workflow tool.** Reads and sub-resource reads go here.
   - **Expose as a write tool, tiered.** Invoice mutations go here.
   - **Drop from MCP.** Admin and config endpoints (users, API keys, webhooks, carrier and rate CRUD) stay in REST. They are rarely agent jobs, and MCP is not a mirror of REST.

## 4. Target surface

Names use a `corvale_` prefix, verb-first snake_case, so they don't collide with other servers' tools. The count is 5 tools at launch and 9 after writes. Both fit the 5–15 range.

### Stage 1: read-only (5 tools)

| Tool | Replaces | Risk tier | Notes |
|---|---|---|---|
| `corvale_search_invoices` | `getInvoiceList` and filtered list variants | Read Only | Filters: status, carrier_id, date range, amount range. `limit` defaults to 25. Returns a cursor and `has_more`. `format`: json or markdown. |
| `corvale_get_invoice` | `getInvoiceById` and its sub-resource GETs | Read Only | Takes an absolute `invoice_id`. `include` is an enum array: `line_items`, `carrier`, `payments`, `audit_trail`. Nothing is inlined by default. |
| `corvale_find_carriers` | `getCarrier` and the carrier list | Read Only | One tool for lookup by name, SCAC code, or id. |
| `corvale_get_carrier_rates` | `getCarrierRates` | Read Only | Takes `carrier_id` plus lane and effective-date filters. It stays separate because its parameters and payload size differ from carrier lookup. |
| `corvale_audit_invoice` | Several GETs the agent chains today | Read Only | Composite workflow tool. It compares an invoice against contracted rates and returns the discrepancies. Build it only if your data supports it, and confirm with the inventory. |

### Stage 2: graduated writes (up to 4 more tools)

| Tool | Replaces | Tier | Safety patterns |
|---|---|---|---|
| **`corvale_update_invoice`** | `patchInvoice` | Contained Write | Enumerated editable fields, not a free-form JSON patch. `dry_run` returns a before/after diff. Idempotency key. Human approval. Attribution plus async audit. |
| **`corvale_approve_invoice`** | Status-transition endpoints, if any | Contained Write | Affects payment, so add a spend cap and approval. |
| **`corvale_dispute_invoice`** | Dispute endpoints, if any | Contained Write | If it messages a carrier, treat it as a message to a human. `dry_run` previews the message. Approval is required. |
| **`corvale_void_invoice`** | `deleteInvoice` | Critical | Disabled by default. If enabled: `dry_run`, approval, and soft-delete or void semantics only. |

Rules for every tool:

- **One risk tier per tool.** If a tool both reads and irreversibly writes, split it into two.
- **Poka-yoke parameters.** Use enums over free strings and absolute IDs over relative ones.
- **Honest annotations.** Set read-only, destructive, and idempotent hints, but treat them as hints. Enforcement stays server-side.
- **Errors inside the result.** Return actionable messages. Never leak internals as protocol errors.
- **Cap payloads.** Return summaries by default, and paginate and truncate large invoice and line-item arrays. This directly addresses "runs out of room".

### Description template

Descriptions are the highest-leverage lever. Write each one for an agent that has never seen your product. Example for the most-confused pair:

- **`corvale_search_invoices`**: "Find invoices matching filters (status, carrier, date range, amount). Use when you don't yet have an invoice_id. Returns up to 25 summary rows, with no line items. To read one invoice's full detail, call `corvale_get_invoice` with an id from these results."
- **`corvale_get_invoice`**: "Get one invoice by its invoice_id. Use after search, or when the user gives an id. Pass `include` to add line_items, carrier, payments, or audit_trail. To find invoices by criteria, use `corvale_search_invoices` instead."

Each description states when to use the tool, what it returns, and how it differs from its nearest neighbor.

## 5. Safety model

The default rung from the skill applies:

1. Scoped credentials plus a verified read-only mode from day one.
2. Human approval on every Contained Write.
3. Critical tools disabled by default.

Re-rank with these points:

- **Promote dry-run and spend caps immediately.** Invoice approval and dispute messaging touch money and carrier communication.
- **Build the risk-tiered server-side gates** (classify each call, then pass it, enrich it with attribution and audit, or block it). Do this as soon as any customer runs unattended agents or write volume outgrows human approval.
- **Don't promise undo.** Undo and rollback are largely absent ecosystem-wide. Your substitute is attribution plus an audit trail, so tell customers that plainly.
- **Server-side only.** Enforcement lives on your server. Client-side prompts and annotations alone fail the "can't bypass by switching clients" test.

## 6. Migrating 6 months of existing users

Layer 3 of the skill (names, descriptions, schemas) has no spec-level versioning. A rename is a breaking change for agents that key on tool names. Your goal is to remove tools, so the skill's default of aliasing old names would defeat the context savings if every alias were advertised.

1. **Ship the new surface at a new endpoint** (for example `/mcp/v2`) or behind an opt-in header. Keep the 74-tool surface running unchanged.
2. **Announce a deprecation window of at least 90 days.** Use machine-readable response-header signaling, and tell customers who call the old tools. Per-customer call logs tell you who.
3. **Optional:** accept calls to old names on the new endpoint without advertising them in `tools/list`. This preserves saved prompts and configs at zero context cost. It is my judgment, not skill guidance, so test it in Claude and Cursor before relying on it.
4. **Remove the old endpoint after the window.**
5. From here on, treat description edits like code:
   - Hash names, descriptions, and schemas, and fail CI on drift.
   - Run the golden-prompt suite in CI after every description edit.
   - Put a version marker in the response envelope and log it on every call.

Your REST v3 contract is stable, public, and four years old. Derive the tools from it rather than hand-building a parallel surface. Composite tools like `corvale_audit_invoice` orchestrate existing REST calls server-side.

## 7. Sequence and gates

| Phase | Work | Exit gate |
|---|---|---|
| 0 | Hotfix (section 2) | Delete and write exposure closed. Read-only lockdown verified by test. |
| 1 | Inventory, golden prompts, baseline (section 3) | Baseline token count and wrong-pick rate recorded. |
| 2 | Build and test the 5 read tools. Check OAuth 2.1 conformance. Add OpenTelemetry. Publish to the official MCP registry (DNS-verified namespace) and the third-party directories. | Golden prompts beat the baseline in Claude and Cursor. Tool-error rate under 2%. Real agent clients, not demo spikes. |
| 3 | Add writes behind the tiers in section 5, one tool at a time | Clean audit trail, zero unattributed writes, and a proven approval flow. |
| 4 | Deprecate the old surface (section 6) | Old-tool call volume near zero after the window. |
| Later | Consider an MCP Apps UI for one workflow, such as an approval queue or audit view | Ask 2–3 design customers whether their security teams allow iframe UI in their assistant. Open question industry-wide. |

Treat the 2% error threshold as a default and calibrate it against your own first month.

### Success metrics

- Wrong-tool tickets per month. This is your lead indicator.
- Tokens used by `tools/list`, before and after.
- Golden-prompt pass rate per client.
- Per-tool call volume, error rate, active users, and client distribution (OTel spans).
- Registry downloads measure install interest, not usage. Don't report them as adoption.

### Gates, binary

- Every write tool has exactly one tier and at least one named safety pattern.
- Auth conformance for the remote server: protected-resource metadata published, token audience validated, no passthrough upstream, stateless instances.
- Surface stays within 5–15 tools.
- No debunked statistics in internal business cases.

## 8. Assumptions to confirm

| # | Question | If the answer differs |
|---|---|---|
| 1 | Are buyers asking for MCP in RFPs? Is a community server filling gaps? | A hard RFP deadline accelerates Stage 2 and favors managed hosting. A community server means the new official server should displace it. |
| 2 | What do `deleteInvoice` and `patchInvoice` actually do in v3 (hard delete or void, field whitelist)? | Hard delete makes the Week 0 hotfix more urgent. |
| 3 | Which writes do agents actually need? Which are irreversible, financial, or message a carrier? | Shapes the Stage 2 tool list and which safety patterns lead. |
| 4 | Hosting: remote multi-tenant or local stdio? Do you have a managed platform? | The skill's default is remote managed. Local stdio is out for enterprise fleets. |
| 5 | Do you run an OAuth 2.1 authorization server today? | If not, MCP is your first OAuth consumer, which adds scope. |
| 6 | Delivery date and effort ceiling? Are customers already running unattended agents? | Unattended agents promote the server-side policy gates. |
| 7 | Do you have per-tool call logs and tickets, or only anecdotes? | Without logs, step 3 starts with instrumenting the current server. |

## 9. Evidence notes

- Atlassian's disclosure is the strongest first-party dataset: grounded agents gave 44% more accurate answers using 48% fewer tokens. It's directional for your case, because it measures grounding, not tool pruning. Run your own before/after to produce your own number.
- Stacklok's survey (Dec 2025) puts about 41% of software organizations in limited-to-broad MCP production. It's the citable baseline.
- I did not use the circulating "78% of enterprises" or "28% of Fortune 500" figures. They are debunked.