# Wrenfield MCP server: Q1 plan

I read the skill and all three references. The plan follows its staged rollout and does not go all-in, and it changes three parts of your brief.

## 1. Decisions up front

1. ❌ **Drop the stub result** (`{"rendered": true, "see": "widget"}`). Every app-backed tool keeps returning its full structured and text result.
2. ❌ **Drop "a widget on all 9 tools."** Decide per tool. `get_vehicle_status` and `lookup_driver` stay plain.
3. ✅ **Build one app in Q1: route planning.** Dragging waypoints is interaction that text can't carry. Gate it on a design-partner check.
4. ✅ **Treat the two overnight-agent customers as the design target.** The skill says to design for the most demanding consumer type. That is an unattended agent behind its customer's gateway, which never renders a UI.
5. ⚠️ **Don't confirm the M365 Copilot and Goose promise to the prospect yet.** Test it in W2–3 first (section 5).

## 2. Why the brief changes

**The stub breaks the server for most of your traffic.**
- The skill's rule: "Keep every app-backed tool complete without its UI." The extension is opt-in on both sides. Hosts without it, headless clients and background fleets get only the plain result.
- Your overnight agents and any Copilot surface without the extension would receive `{"rendered": true}` and nothing else.
- Even in a host that renders the app, the model sees only the stub. A follow-up like "which vehicles have been idle over 2 hours?" has no data behind it, so the model either guesses or calls the tool again.
- The stub also corrupts your metrics. Calls would return success while the task fails, so the 1.1% error rate would go blind.
- Switching existing tools to stubs changes behavior for today's 60k calls a day. That is a layer-3 breaking change (section 4).

**Cut token cost with other levers.**
- Honor a `limit` parameter, defaulting to 20–50 items, and return cursor and has-more fields.
- Offer a concise format alongside the full one.
- Trim fields the model doesn't need.
- Measure tokens per call before and after.

**Nine widgets is nine front-ends.** Each one needs its own build, tests, accessibility and security review, and it is maintained as long as the tool exists. The skill names lookups and status checks as having nothing to gain from a UI. "Consistent UI reads premium" is a design argument, not a user-job argument. A consistent look can come from a shared design kit on the apps that earn one.

**Your existing planner doesn't transfer for free.**
- The MCP version runs in a sandboxed iframe with deny-by-default CSP, so it must bundle into one HTML file.
- Map-tile and API origins must be listed in `_meta.ui.csp`, minimally.
- It can't use your web app's session. It reaches data only through the server's tools, which pass your OAuth and risk gates.
- Budget it as a second implementation of the planner, not a re-embed.

**Planning is not dispatching.** If sending the route to drivers messages real people, that is an irreversible write on a server that is read-only today. The skill requires exactly one risk tier per tool, so this becomes two tools.

## 3. Where you stand

- Stage 1 (read-only) looks passed. You have 60k calls a day from real clients and a 1.1% tool-error rate, against the under-2% gate.
- I can't confirm the rest of Stage 1 from what you told me: OAuth 2.1, OpenTelemetry, registry publication. Q1 begins by checking those.
- Your telemetry is the evidence for the business case, not external statistics. If you cite market data, use Stacklok's ~41% of software organizations in limited-to-broad MCP production (Dec 2025 survey). Never cite the "78% of enterprises" or "28% of the Fortune 500" figures. Atlassian's numbers are their disclosure, not a forecast for you.

## 4. Q1 plan

Weeks are relative to the Q1 start.

### Phase A: baseline and conformance (W1–3)

1. **Baseline telemetry.**
   - Pull per-tool call volume, errors and latency.
   - Break down client share (Claude, Copilot, gateway traffic) and average response tokens per tool.
   - Add OpenTelemetry spans and request IDs if missing.
2. **Auth audit against the 2026-07-28 spec revision.** Each item is binary pass or fail:
   - protected-resource metadata published (RFC 9728);
   - token audience validated (RFC 8707);
   - issuer validation (RFC 9207);
   - no bearer-token passthrough upstream;
   - instances stateless and interchangeable behind a load balancer.
3. **Design-partner check (the gate for the app).** Ask 2–3 customers, including at least one of the two overnight-agent customers, whether their security teams allow iframe-rendered third-party UI in their assistant. The skill calls this an open question, not a settled yes.
4. **Freeze the current surface for versioning.**
   - Hash names, descriptions and schemas.
   - Write golden-prompt tests for the 9 tools. These are fixed representative tasks that must still select the right tool.
   - Log a version marker on every call.
5. **Name audit.**
   - The skill wants verb-first, service-prefixed names such as `wrenfield_get_vehicle_status`.
   - Add the prefixed names as new tools and alias the old ones. Renaming silently breaks agents that key on names.
   - Announce a deprecation window of at least 90 days with response-header signaling.
6. **Registry.** Publish to the official registry under a DNS-verified namespace, and list in third-party directories.

### Phase B: enterprise-fleet safety (W3–8)

The overnight agents make unattended callers real, and the skill says to promote risk-tiered gates at exactly that point. Build them before any write tool ships.

1. **Scoped credentials.**
   - Issue per-customer, per-agent credentials.
   - Make the overnight agents' default read-only.
   - Test that write tools are actually absent under lockdown. A documented GitHub bug shipped write tools despite the flag.
2. **Server-side risk tiers.** Use Read Only, Minimal Impact, Contained Write and Critical, enforced before the handler runs. Switching clients must not bypass them.
3. **Attribution and async audit.** Log customer, agent and session on every write, asynchronously so it adds no latency.
4. **Idempotency keys on every write.** Per-credential rate limits, with the policy from `api-rate-limit-policy`.
5. **Gateway friendliness.** Keep tool names stable and request IDs correlatable, because the gateway sits in front of you and has its own logs. Deliver the metrics the gateway can't see.
6. **Honest gap.** Rollback doesn't exist. Attribution plus audit stand in for reversibility, so say so to customers.

### Phase C: route planning (W4–11)

| Tool | Tier | Notes |
|---|---|---|
| `wrenfield_plan_route` | Minimal Impact | Computes a proposed route and returns the full structured result. Persists nothing. Candidate for the app. |
| `wrenfield_save_route_draft` | Contained Write | Approval-gated, idempotency key, attributed. |
| `wrenfield_dispatch_route` | Critical | Messages drivers. Disabled by default, enabled per customer, and never for unattended credentials. |

- With these three the surface is 12 tools, inside the 5–15 range.
- `dispatch_route` ships in Q1 only if a customer or RFP asks for it. Otherwise it moves to Q2. Nobody can approve a dispatch at 3 a.m., so the overnight agents can't have it in any case.
- **The app (starts after the W3 design-partner gate).**
  - The model proposes a route, the user drags waypoints, and the app calls `plan_route` again to re-validate.
  - Build it with the official toolkit: single-file bundle, `registerAppTool` and `registerAppResource`.
  - Declare only the origins it loads.
  - Escape all driver, vehicle and address data in the UI.
  - Version the `ui://` resource together with the tool's result shape.
  - Any save or dispatch the app triggers goes through the same tier gate as a model call. A click is not approval.
- **If the design partners say no to iframes.** Ship `plan_route` as a plain tool that returns a link to your existing web planner. It costs days.
- **Test matrix.** Run the app in at least two hosts, plus one client without the extension to prove the plain result completes the job.

### Phase D: measure and decide (W10–13)

- Track app-rendered versus text-only calls per client, and completion of the interactive job: route adjusted, draft saved.
- If the app renders but isn't used, retire it and keep the tool.
- Re-baseline thresholds on your own telemetry. The 2% error gate is one vendor's default, not a standard.
- Decide Q2: more apps, `dispatch_route`, or stay put.

## 5. The sales promise (M365 Copilot and Goose)

- As of 2026-09 the community extension matrix lists both Microsoft 365 Copilot and Goose, so it is plausible. The skill says to re-check before promising a host to a customer.
- W2–3: test the 9 existing tools and `plan_route` in both hosts, covering the OAuth flow and tenant restrictions. Treat the app separately, because support for the extension varies by host.
- Until then, sales can say "works in any MCP client with OAuth." They can't say the widgets render in those hosts.
- Ask sales which exact words the prospect heard, and whether any of it was written into a contract or RFP answer.

## 6. Cut line and kill rules

- **If Phase A fails the auth audit**, fix it first. Phase C slips, because enterprise buyers and the overnight customers need it.
- **If the design partners reject iframes**, ship the link-out.
- **If an RFP makes MCP writes or UI a hard requirement**, accelerate. The skill allows that override.
- **If call volume goes flat and no RFP demand shows up for two quarters**, park the server at maintained read-only. Right now you're far from that: 60k calls a day.
- **No "all in" on UI before the apps' usage data exists.** Retire any app that isn't used.

## 7. Done criteria (the skill's four gates)

- **Safety coverage:** each write tool has exactly one tier and at least one named pattern, and the irreversible one is approval-gated or disabled.
- **Auth conformance:** metadata published, audience validated, no passthrough.
- **Evidence hygiene:** no do-not-cite figures in any deck.
- **Curation:** 5–15 tools, named per convention.

## 8. What I need from you

I assumed the answers in brackets. Tell me which are wrong.

1. What are the other 7 tools? [Mostly lookups and lists, so no apps. A live-fleet map would be the second app candidate, in Q2.]
2. Is OAuth 2.1 live today, and is OpenTelemetry in? [Not verified, so Phase A checks both.]
3. Has MCP appeared in RFPs or security questionnaires? [Unknown, so the staged plan holds.]
4. What does the route "save" or "dispatch" do in your web app today? Does it message drivers? [Yes, so it is a Critical write.]
5. What do the overnight agents actually do? [Read-only pulls, so read-only credentials are enough.]
6. Which dates does Q1 cover, and is there a launch deadline? [Roughly 13 weeks from the start.]
7. Is your hosting managed or self-hosted? [Unknown. The skill defaults to managed; self-hosted only if the server is the product or you need a custom policy layer.]
8. What exactly did sales promise, and in what form? [Verbal only.]