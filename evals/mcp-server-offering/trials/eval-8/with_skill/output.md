# Bramwell MCP launch: review of the Q4 plan

I read the `mcp-server-offering` skill and its four references. Bramwell hasn't answered the skill's six clarifying questions, so I've marked every place where the verdict depends on an unknown.

## Verdict

Don't ship this as one mid-November release. It puts the skill's three rollout stages into one drop. It also launches a Critical-tier delete and a UI that no one has validated with customers, about five weeks out. I recommend a staged plan (see "What I'd ship instead").

## Holes, ranked

### 1. One release skips every gate (🔴)

The skill's rollout is read-only launch, then graduated writes, then the interactive UI. Each stage has a go/no-go gate. Your plan ships all three at once, so you'd have no error-rate baseline, no audit-trail history and no approval-flow evidence before the riskiest tools go live.

The only exception is hard RFP pressure. If MCP appears as a hard requirement in actual buyer RFPs, accelerate. If it doesn't, you can't justify skipping stages. Which one is it?

### 2. Five weeks isn't enough for what's listed (🔴)

The skill budgets a weekend for a demo-grade server. A production-grade one takes months plus standing maintenance. Your scope needs all of this by mid-November:
- OAuth 2.1 resource-server behavior
- server-side risk tiers
- approval flows
- audit logging
- idempotency
- an MCP Apps UI with its own build, tests, accessibility and security review

Something will be cut under deadline pressure, and it will probably be the safety layer.

### 3. `delete_project` is a Critical-tier tool with no safety story (🔴)

The skill's failure-mode list includes "a destructive tool that is live-only", and the skill notes undo is largely absent across the ecosystem. Required before this tool exists:
- **Disabled by default**, per the Critical tier.
- Server-side enforcement. Client-side prompts and annotation hints fail the "can't bypass by switching clients" test.
- A `dry_run: true` that returns what would be deleted (tasks, comments, attachments).
- Approval on every call.
- A soft delete underneath. Without one, nothing is recoverable.

My recommendation is to cut it from this release. An agent that can delete a customer's project has little upside next to the incident risk. The skill's own precedent: an unattended agent closed thousands of tickets, and that's what prompted Cloudflare to build tiered gates.

### 4. The other three writes need tiers too (🟠)

Every write tool needs exactly one risk tier and at least one named safety pattern, or the safety-coverage gate fails.

| Tool | Proposed tier | Notes |
|---|---|---|
| `create_task` | Contained Write | Idempotency key required, so a retry doesn't duplicate. |
| `assign_task` | Contained Write, treat as high | It notifies a real person. The skill promotes dry-run and caps for tools that message humans. |
| `close_task` | Contained Write | Highest unattended-loop risk. Needs a per-credential rate cap. |
| `delete_project` | Critical | Disabled by default, or cut. |

Approval is affordable on contained writes only while early write volume is low. When background agents run unattended, promote the risk-tiered server-side gates.

The skill also says a tool that both reads and irreversibly writes is two tools. Check whether any of your twelve do.

### 5. The dashboard is a Stage-3 item with an unresolved gate (🔴)

The skill's gate before investing in an MCP Apps UI is to ask two or three design partners whether their security teams will allow iframe-rendered third-party UI inside their assistant. The skill calls this an open question, not a settled yes. Has anyone asked? Marketing is about to put it in the launch post.

### 6. The differentiator claim is weak (🟠)

The skill lists the MCP Apps day-one launch partners (January 2026): Asana and monday.com are among them. Those are project-management competitors who shipped interactive UI in assistants months before you. "Triage your board in chat" isn't unique. At best it's parity.

The use case itself is a good fit, since the skill names "stepping through a queue item by item (triaging issues)" as a valid MCP App job. The problem is positioning and timing.

### 7. The dashboard won't render for everyone (🟠)

Support varies by host, and the skill says to re-check the community matrix before promising any host to a customer. As of 2026-09 that matrix lists Claude, ChatGPT, Cursor, VS Code Copilot and Microsoft 365 Copilot, among others. Headless and background agent clients get only the plain result.

A launch post that implies "everyone gets the dashboard" over-promises. Name the hosts. Test in at least two hosts plus one without the extension.

### 8. A click in the dashboard isn't approval (🔴)

If the dashboard lets users close or assign tasks directly, those calls must pass the same risk-tier gate as a model call. Triage is bulk by nature: clicking through 40 tasks makes approval fatigue near-certain, and the skill warns that fatigue trains users to click through. Make the dashboard read-only at launch, or route its writes through the same gates plus rate caps.

### 9. Every tool must work without the UI (🟠)

The dashboard-backed tool has to return the full structured and text result on every call. The UI is a richer view of that data, not the only path. Does your design do that?

### 10. Untrusted content flows through the dashboard (🟠)

Task titles, descriptions and comments are written by other people. They reach the model through tool results and render in the UI. This is a prompt-injection and XSS path, and it's worse when the same assistant also holds write tools. This point goes beyond the skill text. The skill's relevant rule is to render user-supplied data as data and escape it, because the sandbox protects the host and not your app. Add a tool-description review for injection as well.

### 11. Auth readiness is unknown (🟠)
- Does Bramwell already run an OAuth 2.1 authorization server? If not, MCP is your first OAuth consumer, and that's a larger project (`oauth2-provider-design` territory).
- Required on the server: protected-resource metadata (RFC 9728), audience validation (RFC 8707), issuer validation (RFC 9207) and a stateless design. Never forward the caller's bearer token to your own API.
- With 3,000 customers, enterprise security review will check exactly this.

### 12. Twelve tools are within range, but check the shape (🟡)

12 sits in the 5-15 band. But `create_task`, `assign_task`, `close_task` and `delete_project` read like CRUD endpoint names, which is the mirror-the-API trap. Ask whether workflow tools would serve better, for example a "triage a board" read tool and a single `update_task`. Name them `bramwell_verb_noun` in snake_case, set annotations honestly, and write descriptions that say how each tool differs from its neighbors.

### 13. Versioning and measurement aren't mentioned (🟡)
- **Tool-surface contract:** tool descriptions and schemas are an interface. Before launch you need a surface hash and golden-prompt tests in CI. Ship description edits through code review, not as docs fixes.
- **Telemetry:** OpenTelemetry from the first call, with a baseline for call volume, error rate and client distribution. Without it you can't pass any later gate. Registry downloads aren't usage.
- **Success criteria:** the plan doesn't define any. The skill's stage-transition thresholds (error rate under 2%) are defaults to calibrate against your own first month.

### 14. The launch post must be evidence-clean (🟡)

Don't cite "78% of enterprises use MCP in production" or "28% of Fortune 500" (both debunked), or download counts presented as usage. If you need a baseline, use the Stacklok survey: about 41% of software organizations in limited-to-broad production (n=300, Dec 2025).

### 15. Existing community server (🟡)

Has anyone already built a Bramwell MCP server? That's a demand signal. It's also a displacement job: a first-party server published well tends to retire the unofficial one.

## What I'd ship instead

Assumes no hard RFP deadline. If there is one, say so and I'll re-plan.

**Mid-November (Stage 1, read-only):**
- A curated read-only set of workflow tools, with the exact list depending on your other eight.
- OAuth 2.1, OpenTelemetry and registry publication from day one.
- **Hosting:** use a managed platform unless you need a custom policy layer in your own infrastructure.
- **Launch post:** lead with "Bramwell works in your assistant, safely, read-only first", not the dashboard.

**Q1 (Stage 2, graduated writes), gated on sustained real-client volume and under 2% error:**
- `create_task`, `assign_task` and `close_task` with server-side tiers, approval, idempotency, attribution and async audit.
- A verified read-only lockdown. Test that write tools are absent under it.
- `delete_project` stays off, or arrives last with dry-run and approval.

**After design-partner validation (Stage 3):**
- The triage dashboard, built for the single workflow with the most value.
- Announce it when it ships, not before.

## Gates for the current plan

| Gate | Status |
|---|---|
| Safety coverage | ❌ No tiers or patterns defined. `delete_project` fails outright. |
| Auth conformance | ⚠️ Unknown. Needs your answer on the authorization server. |
| Evidence hygiene | ⚠️ Pass only if the post avoids the do-not-cite list. |
| Curation (5-15, named well) | ✅ Count passes. ⚠️ Naming and workflow shape are unverified. |

## Questions I need answered

1. Has MCP appeared in real RFPs or security questionnaires? Is a community server already out there?
2. Is the public API a stable REST/GraphQL contract the tools can derive from?
3. Is read-only acceptable at launch? Which writes do agents need, and which notify people?
4. Remote endpoint or local? What multi-tenant edge infrastructure exists?
5. Do you run an OAuth 2.1 authorization server today?
6. Is the mid-November date fixed by a procurement deadline or by marketing? What's the engineering-hours ceiling?
7. Have any design partners been asked about iframe UI in their assistants?
8. What are the other eight tools?