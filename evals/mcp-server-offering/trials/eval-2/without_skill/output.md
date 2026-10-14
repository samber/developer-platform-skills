# MCP server for Latchkey: headcount case (draft)

I left out three of your four claims, and the fourth is reworded. None of them has a source I can verify, and a CFO will ask for one. Notes on each are at the end, under "What I changed".

---

## The ask

Approve **[N] engineer(s) for [N] months** to build and run a Latchkey MCP server. MCP is a standard that lets AI assistants such as Claude and ChatGPT call our product directly. Release it in stages, with a go/no-go review at each stage.

## Why now

- **We already have the hard part.** Our public REST API has been live since 2021. An MCP server is a thin layer over it, so we are not building new product logic.
- **Our buyers' users are moving into AI assistants.** HR and IT admins at our ~600 customers can already ask an assistant to look things up or run tasks. If we have no MCP server, our product is invisible in those workflows.
- **Competitors can ship the same thing.** Any HR-onboarding vendor with an API can build this. Being early matters most if customers start asking for it in RFPs.

## What we would build

1. **Stage 1, read-only (about [X] weeks).** Employee onboarding status, task lists, document completion. Low risk and quick to ship.
2. **Stage 2, write actions (about [X] weeks).** Assign tasks, trigger workflows, send reminders. This needs per-customer permissions and audit logs.
3. **Stage 3, hardening.** Rate limits, monitoring, security review, and docs.

## Cost

| Item | Estimate |
|---|---|
| Engineering ([N] FTE × [N] months, fully loaded) | $[ ] |
| Security review and pen test | $[ ] |
| Hosting and monitoring | $[ ]/yr |
| Ongoing maintenance after launch | [N] FTE-fraction |

Size the engineering line against Stage 1 and 2 only. Hardening is where the real cost sits, because transport reliability, auth, and per-tenant permissions are what a production service needs. Budget for it as an explicit line item, not a percentage taken from an outage statistic.

## Evidence we can stand behind

Fill these in from our own data before this goes to the CFO. They are stronger than any industry statistic.

- **Customer demand:** [N] of ~600 customers, or [N] open deals, have asked about AI-assistant or MCP integration. Source: CS and sales notes.
- **API baseline:** [N] customers actively call the REST API, at [N] calls/month. This sizes the likely adopter pool.
- **Market signal:** MCP is a widely adopted open standard, and major vendors, including Stripe and Linear, have published MCP servers. This shows the category exists. It says nothing about revenue.

## How we will measure success

- Stage 1: [N] customers connected within [N] days of launch.
- Stage 2: [N] customers using write actions weekly.
- Business: [N] deals where MCP was cited, or [N]% lift in retention or expansion for connected accounts versus a matched group.
- **Kill rule:** if Stage 1 shows fewer than [N] connected customers after [N] days, pause Stage 2 and reassign the headcount.

## Risks

- **Low adoption.** We cap spend at Stage 1 until demand shows up.
- **Security and data exposure.** HR data is sensitive. Stage 2 is gated on a security review.
- **Standard churn.** MCP is young and the spec is still moving. Budget for upkeep.

## Decision requested

Approve Stage 1 now at $[ ]. Release Stage 2 and 3 funding when the Stage 1 targets are met.

---

## What I changed, and what to do before sending

- **"78% of enterprises use MCP in production" and "28% of the Fortune 500 run production MCP deployments"** are cut.
  - They are hard to square with each other. The Fortune 500 are the largest enterprises, so a 28% rate there against 78% overall would be surprising.
  - Find the original survey. Check who was surveyed and how "production" was defined. Then keep one figure, with its source and date.
- **"73% of outages start at the transport/protocol layer"** is cut.
  - It has no obvious source, and I couldn't tie it to MCP. Even if it were real, it wouldn't tell you how many engineers to hire. I replaced it with a hardening line item sized from your own estimate.
- **"Stripe and Linear have driven real revenue from their MCP servers"** is reworded to "have published MCP servers."
  - As far as I know, neither company has publicly attributed revenue to its MCP server. If you read a specific claim, send me the link and I'll check it. Without a source, this is the line most likely to hurt your credibility.
- **Do not send this with the brackets unfilled.** Your own demand and cost numbers carry the case. If you give me the customer-request count, API usage, and a rough team cost, I'll fill in the table and tighten the draft to one page.