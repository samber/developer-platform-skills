**Next action (15 min):** run `tools/list` against your prod MCP server and count tokens in the JSON. That baseline is the number every later step is measured against. I haven't seen your 74-tool list, so the domain groupings below come from your examples. Check them against real endpoints and logs.

## Diagnosis

1. **Tools mirror endpoints, not tasks.** `getInvoiceById` vs `getInvoiceList` and `getCarrier` vs `getCarrierRates` look almost the same to a model. Auto-generated names and OpenAPI summaries don't say when to use each tool or when not to. That is the wrong-tool problem.
2. **74 schemas load into context on every session.** Rough guess: 300–600 tokens each, so 20–40k tokens before any work. Measure it. This is "runs out of room". Their other MCP servers may add to it.
3. **Responses are probably full REST payloads.** Unbounded lists and nested objects fill the context a second time.
4. **`patchInvoice` and `deleteInvoice` sit next to the read tools.** There is no scoping, no destructive hint, and no dry run.

## Design rules

1. One tool per **agent task**, not per endpoint. Target 12–16 tools.
2. Merge list and get-by-id into `search_*` and `get_*`. Fold sub-resources into `get_*` through an `include` enum.
3. Flat parameters, enums over free strings, and every field described.
4. Every tool description answers three questions: what it does, when to use it, and when not to (name the sibling tool).
5. Responses are bounded: default limit 20, cursor pagination, `detail: "concise" | "full"`, and a truncation message that says how to narrow the query.
6. Errors tell the agent the next step, for example "carrier_id not found; call `search_carriers` with the name".
7. Every tool carries MCP annotations: `readOnlyHint`, `destructiveHint`, `idempotentHint`.
8. Names are `verb_noun` in snake_case, with one verb per meaning: `search`, `get`, `create`, `update`, `void`.

## Proposed surface (about 14 tools)

| New tool | Replaces | Notes |
|---|---|---|
| `search_invoices` | `getInvoiceList` and filter variants | Filters: status, carrier, date range, amount, free text. Cursor. `detail` param. |
| `get_invoice` | `getInvoiceById` and sub-resource getters | `include`: line_items, payments, documents, audit_trail |
| `create_invoice` | `postInvoice` | Flat params. |
| `update_invoice` | `patchInvoice` and field-specific patches | Partial update, `dry_run` flag. |
| `transition_invoice` | approve, submit, dispute endpoints | `action` enum. Each value is listed in the description with its preconditions. |
| `void_invoice` | `deleteInvoice` | Requires `reason`. `destructiveHint`. Off by default (see toolsets). |
| `search_carriers` | `getCarrierList` | Match by name, SCAC, or status. |
| `get_carrier` | `getCarrier`, contacts, docs | `include` enum. |
| `find_rates` | `getCarrierRates` | Different task: filter by lane, mode, and date. Description says "for quotes, not carrier profile". |
| `list_reference_data` | status, currency, and mode lookup endpoints | `type` enum. Replaces about 5 tiny tools. |
| Others (4–6) | Rest of the 74 | Cluster by task using the method below. |

### Example description

```
search_invoices: Find invoices matching filters. Use to locate invoices when
you don't have an ID, or to list a carrier's or status's invoices.
Not for fetching one known invoice: use get_invoice.
Returns max 20 per page (concise by default). If truncated, narrow filters
or pass `cursor`.
```

## Finding the other 4–6 tools

1. Export 30 days of MCP tool-call logs. Count calls per tool. Expect a heavy long tail.
2. Mine support tickets for wrong-tool pairs. This gives a confusion list.
3. Write the top 15 agent jobs, such as "reconcile a carrier's open invoices" or "dispute an invoice".
4. Group endpoints by job. Aim for one tool per job.
5. Leave endpoints with near-zero usage out of the new server. REST still covers them.

## Delivery

1. **Don't touch REST v3.** Build the new MCP layer as a hand-written facade over it. Stability stays, and the MCP contract is free to change.
2. **Ship the new server beside the old one** (for example `/mcp/v2`). Never list both sets in one session, or context cost doubles.
3. **Add toolsets selected by token scope:**
   - `read` (default)
   - `billing-write`
   - `admin` (adds `void_invoice`)

   Fewer tools get listed and writes are opt-in.
4. **Deprecate the old server on a fixed date.** Proposal: 90-day notice, banner in docs, email to active MCP users from the logs, sunset at 6 months. Confirm the window against your contracts.
5. **Optional later:** for the long tail, add a read-only `search_api` plus `call_api` pair behind a flag. Don't ship generic passthrough for writes.

## Evals (gate before launch)

1. Build 60–100 tasks from real tickets and top jobs. Each has a prompt, the expected tool sequence, and an end state.
2. Run old vs new on Claude and on Cursor with at least two models.
3. Track:
   - correct first-tool rate
   - task completion
   - tool calls per task
   - tokens in `tools/list`
   - tokens per response
   - error rate
4. Set targets after the baseline. Proposal: `tools/list` under 6k tokens and first-tool accuracy ≥ 90%. Both are placeholders until you have a real baseline.
5. Re-run the eval on every description change.

## Timeline

This assumes 1–2 engineers plus you as PM. Adjust it to your team.

1. **Week 1:**
   - baseline token count
   - log and ticket analysis
   - eval set drafted
   - safe quick win: rewrite descriptions on the old 74 and add annotations
2. **Week 2:** finalize the tool list, review with support, write schemas and descriptions.
3. **Weeks 3–5:** build the facade, response shaping, and toolsets. Run evals each week.
4. **Week 6:** beta with the "runs out of room" customer and 2–3 others.
5. **Week 7:** launch `/mcp/v2` and start the deprecation clock.

## Risks

- **Customer prompts and agents hardcode old names.** Mitigation: the parallel server and the deprecation notice.
- **Over-merging makes `update_invoice` and `transition_invoice` too broad.** Mitigation: evals catch it, and splitting later costs little.
- **Small gains if context is mostly other servers.** Mitigation: ask that customer for their full MCP list.

## Questions

1. Can you share the endpoint list and 30 days of call logs?
2. Which writes are safe for agents with no human confirmation?
3. Is token scoping already in the auth layer, or does it need building?

**Next:** send me the endpoint list and I'll draft the final tool schemas and descriptions.