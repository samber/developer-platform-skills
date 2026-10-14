# Latchkey MCP server: investment case (one-pager for CFO review)

**Draft, 2026-10-09. Items in [brackets] need Latchkey data before this goes to the CFO.**

## Recommendation

Fund a **staged, read-only-first MCP server** with a fixed initial scope and a parking rule. Do not approve a permanent team on the strength of adoption statistics. The evidence supports MCP as a defensive, procurement-driven investment. It does not support a revenue-growth claim.

## Why now

- **Buyers are asking.** Forrester predicts 30% of enterprise app vendors will launch their own MCP servers (Predictions 2026, Nov 2025). It tells tech leaders to "interrogate their business app vendors on their approach to MCP." Analysts describe MCP as "the new checkbox on RFPs." That is a qualitative signal, so we attach no percentage to it.
- **Adoption is real but moderate.** A Dec 2025 survey of 300 senior technical leaders (Stacklok) found about 41% of software organizations in limited-to-broad MCP production.
- **Production is hard for buyers.** Only 11-14% of enterprise agentic pilots reach production. They stall on identity, audit and access-control gaps. A server that ships with scoped credentials, OAuth 2.1 and audit logging addresses those gaps, and that is what passes security review.
- **We start from a good position.** Latchkey has had a public REST API since 2021. The tools can be derived from that stable contract rather than hand-built in parallel. This is a defensive duplicate of an existing surface, not a new acquisition channel. The channel case applies only to vendors with no public API.
- **Proven impact is concentrated in a few vendors.** Atlassian is the strongest first-party dataset: 5M+ tool calls per working day, about a third of them writes, and 44% more accurate answers using 48% fewer tokens. Atlassian is far larger than Latchkey, so read it as proof the channel can work, not as a forecast for us.

## What we would build

- **Surface:** 5-15 workflow-level tools for HR-onboarding jobs (for example `latchkey_list_onboardings`, `latchkey_get_new_hire_status`), not a one-tool-per-endpoint mirror. The median real-world server has 5 tools.
- **Stage 1 (weeks): read-only.**
  - OAuth 2.1 from day one.
  - OpenTelemetry from the first call.
  - Official MCP registry listing.
  - Managed hosting, which absorbs the protocol's spec churn. This is the default unless a deadline or residency constraint says otherwise.
- **Stage 2 (about a quarter): graduated writes, only if Stage 1 passes its gate.**
  - Server-side risk tiers.
  - Human approval on contained writes.
  - Irreversible tools disabled by default.
  - Idempotency keys and audit trail.
  - HR data is sensitive, so writes that touch people records or message employees stay gated.
- **Stage 3: differentiation,** such as an interactive approval UI. Not in this request.

## Cost and headcount

- A simple hand-built API-integration server is estimated at 150-250 hours. Production-grade, with auth, safety patterns and observability, takes months and carries a standing annual maintenance commitment. This is an analyst estimate, not an audited figure.
- **Ask:** [X engineers for Y weeks] for Stage 1, plus a maintenance allowance of [Z%] of one engineer. Request Stage 2 headcount only after the Stage 1 gate passes.
- Budget real engineering time for tool descriptions. They are the highest-leverage quality lever and need the same review as code.
- **Reliability work:** budget engineering time for transport and protocol reliability, justified by our own staging and production error data, not by an outage statistic (see "Figures deliberately left out").

## Decision gates

| Gate | Condition |
|---|---|
| Stage 1 → 2 | Sustained tool-call volume from real agent clients (not demo spikes) and tool-error rate under 2% |
| Accelerate | MCP appears as a hard requirement in actual buyer RFPs: go straight to Stage 2 |
| Park | Flat call volume and no RFP demand after two full quarters: keep Stage 1 as low-maintenance table stakes and defer the production build |

The 2% threshold is a default drawn from one vendor's practice. We re-baseline it against our first month of telemetry.

## Success measures (in-server telemetry only)

- Call volume, success and error rate, per-tool usage, active customers, and client distribution.
- Number of the ~600 customers with at least one active agent connection.
- RFP and security-questionnaire mentions of MCP [count from sales].
- Registry listings and package downloads measure install interest, not usage, so they are excluded.

## What we do not claim

- No revenue attribution. Even leaders rarely publish it, and most MCP servers earn little directly.
- No market-share or "everyone is doing it" statistics.
- The real exposure is the risk of being filtered out of agent-assisted procurement and of a community-built server filling the gap. That is why the plan is cheap, staged and reversible.

## Evidence still needed from Latchkey

1. How many RFPs or security questionnaires in the last 2-4 quarters mention MCP or agent access?
2. Are customers or a community-built Latchkey MCP server already filling the gap?
3. Which write actions do customers genuinely need, and which touch employee data or send messages?
4. Do we already run an OAuth 2.1-capable authorization server?
5. Is there a hard date, such as a named renewal or RFP?

## Figures deliberately left out of this draft

- **"78% of enterprises use MCP in production"** and **"28% of the Fortune 500 run production MCP deployments."** An independent tracker debunked both. The citable baseline is the ~41% above. A CFO or board member who checks the 78% will discount the whole page.
- **"73% of outages start at the transport/protocol layer."** This is a single-vendor analysis with no independent corroboration. The conclusion that we should budget for reliability work holds on its own merits. Support it with Latchkey's own incident data, or label it "directional, vendor-reported" if cited at all.
- **"Stripe and Linear have driven real revenue from their MCP servers."** I can't support this line. Both are private companies and have published no MCP-specific adoption or revenue metrics. Commentary linking revenue to their MCP servers tends to conflate their agent-platform statistics with MCP-server usage. Replace it with the Atlassian first-party figures above, which are verifiable.