**Do first, today:** tell sales to stop confirming "works in M365 Copilot and Goose" in writing. Safe wording: "All 9 tools work in any MCP client. Interactive widgets show where the client supports MCP Apps." You have not tested either client yet.

I don't have your 9 tool names, so widget picks below are criteria, not a list.

## Four decisions to change before Q1

1. **Drop the stub result.** `{"rendered": true, "see": "widget"}` breaks three groups:
   - Overnight agents have no UI. Both gateway customers would get no data, and your 1.1% error rate would climb.
   - Clients that don't render widgets get an empty answer.
   - Even in a rendering client, the model can't see the data. It can't answer "which of those is idle?" and will re-call the tool or guess.

   Fix: keep the full result in the model-visible `content`. Put widget-only extras in `structuredContent` or `_meta`. The widget reads the same call, so widgets don't need a stub.

2. **Cut tokens a different way.** Your customers' hosts pay for result tokens, not Wrenfield. To cut them, trim fields, paginate, add a `concise` option, and drop null and duplicate keys. Check the saving before you plan around it: pull the median result size per tool from the last 30 days.

3. **Not 9 widgets.**
   - Widget only where interaction or visuals beat text: maps, timelines, multi-row triage, filters.
   - A single-record lookup (`get_vehicle_status`, `lookup_driver`) answers fine as text. A widget adds load time, a failure mode, and test surface.
   - Design gets its consistency from a shared widget shell and design tokens. It doesn't need a widget on every tool.
   - Ship 3 in Q1, measure, and decide on the rest in Q2.

4. **Treat route planning as a new risk class.** The server is read-only today. Dragging waypoints and committing a plan is a write path.
   - The tool must work headless first: waypoints in as parameters, route out as text.
   - The widget then enhances it.
   - Add a confirm step and an explicit auth scope for any write.
   - The web app's planner screen will not drop into a sandboxed iframe as-is. You need an embeddable component, CSP entries for map tile and API domains, a token strategy, and a bundle size check.

## Q1 plan (≈13 weeks, Jan 4 – Apr 2)

**Phase 0: before Jan 4 (≈3 days of work)**
1. Run a hello-world widget in Claude, GitHub Copilot/VS Code, M365 Copilot, and Goose. Record what renders, what is blocked, and what is silently dropped.
2. Test the same widget through both customers' gateways. Check whether `_meta` and `ui://` resources pass through. Ask them now.
3. Pull per-tool call volume, result size, and client mix from the logs. "Copilot" in your 60k calls may be GitHub Copilot, not M365.

**Phase 1: weeks 1–3, foundation**
1. Freeze the existing result schemas. Add golden-snapshot contract tests for all 9 tools.
2. Only add widget output when the client declares MCP Apps support. Everyone else gets today's response, byte-for-byte.
3. Build the shared widget shell: theming, loading, error, and empty states.
4. Tell the gateway customers in writing what stays stable. Add a canary: their overnight traffic runs against staging first.

**Phase 2: weeks 3–7, three widgets**
1. Score the 9 tools on spatial or temporal data, multi-row data, and need for interaction.
2. Build the top 3, with full model-visible results kept.
3. Instrument widget opens, interactions, and follow-up tool calls.

**Phase 3: weeks 6–11, route planner**
1. Weeks 6–7: headless `plan_route` tool, with tests for error cases and malformed waypoints.
2. Weeks 8–11: embeddable planner widget, with writes behind a confirm step.
3. Security review before week 10.

**Phase 4: weeks 12–13, gate and rollout**
1. Gradual rollout. Gateway customers opt in; they are not switched automatically.
2. Review the gate metrics below.
3. Decide the remaining 6 widgets for Q2 from data.

## Gate metrics (stop or continue)

- Tool-error rate stays ≤ 1.1%. Any rise on the gateway customers' traffic is a stop.
- Follow-up call rate per task does not rise.
- Widget interaction rate in clients that render them is high enough to justify the next widgets. Set the number in week 7.
- Median result tokens fall by an amount you pick in Phase 0.

## What the Phase 0 matrix can change

- If M365 Copilot or Goose don't render widgets, the plan still holds, because the tools work everywhere. Only the sales promise changes.
- If a gateway strips `_meta`, those customers stay on text. That is fine, since they're headless.

## Questions that change the plan

1. What are the 9 tool names and median result sizes?
2. Do both gateway customers have contractual SLAs on response shape?
3. Does route planning write anything today, or only compute?

**Next, under 2 minutes:** send sales the safe wording above.