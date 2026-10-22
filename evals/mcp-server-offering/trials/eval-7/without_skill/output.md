# Ferrolane MCP decision: size and order of work

## Short answer

Sizing is the first problem. "Build an MCP server" sounds like a small feature. It is really your first public API, which reverses a deliberate company stance. The code is the small part. The commitments are the large part: auth, tenant isolation, support, security reviews, and a surface you can't easily withdraw.

Treat it as two decisions:

1. **Strategic:** do we end "no integrations"? This is hard to undo.
2. **Tactical:** do we ship something by January? This is reversible if scoped small.

Competitor announcements are not evidence of demand. Don't commit to a date until you have your own evidence. Collecting it takes about 3 weeks, and that fits inside the January window.

## Size of the decision

These are my estimates, not measurements. I don't know your stack.

| Item | Rough size |
|---|---|
| Thin, read-only MCP server over a clean internal service layer | 3–6 engineer-weeks |
| Same, if your web app talks to the DB directly (no service layer) | 8–12 engineer-weeks, because you'd be building the API underneath it |
| Ongoing cost after launch | About 0.25–0.5 engineer, plus support and security-review load |
| Reversibility | Low once customers build on it |

The recurring costs matter more than the build:

- **Auth.** You need OAuth per user, honoring existing permissions. Shared API keys would break tenant isolation.
- **Data egress.** Your customers' compliance documents will flow into their LLM contexts. Their security teams will ask about it, and your contracts and DPA may need a check.
- **Prompt injection.** Document text is untrusted input to a customer's agent. A malicious subcontractor PDF could carry instructions. Your server needs to treat document content as data, not instructions.
- **Precedent.** Once MCP exists, customers will ask for REST and webhooks. Decide now where the line is.
- **Support.** "Why didn't my agent see this?" tickets are new and hard to debug.

The risks are asymmetric:

- **Build and nobody uses it:** about 1–2 engineer-months, an ongoing tail, and the public-surface precedent.
- **Wait 3 weeks for evidence:** nearly free, and shipping later is still possible.

## Why I'm skeptical on demand (to be tested)

- Your buyers are construction compliance teams. Their integration surface is more likely Procore, Autodesk Construction Cloud, SharePoint, or email than MCP.
- A competitor's announcement says little about use. Check what they actually exposed and whether any customer talks about it.
- Panic in sales is a signal to investigate, not a requirement.

If sales can show lost or stalled deals, the picture changes quickly. That's what the first step asks for.

## What to do, in order

**Step 1: Get evidence from sales (this week, ~2 hours)**
- Ask the head of sales for every deal in the last 6 months where integrations, an API, or AI-agent access came up.
- Ask for the lost-deal reasons and whether the competitor's MCP was named.
- Ask what exactly they are afraid of, and whether it's one deal or a pattern.

**Step 2: Talk to people (weeks 1–2)**
- Interview 8–10 customers and 5 lost or stalled prospects.
- Ask which AI tools they use at work, what they'd want an agent to do with Ferrolane data, and whether their IT would allow it.
- Search your own sales-call transcripts and support tickets for "API", "integrate", "Copilot", "ChatGPT", and "Claude".
- Read the competitors' MCP docs and note what they expose and what they don't.

**Step 3: Recover the original reasoning (week 2)**
- Find out why "no integrations" was chosen. Likely reasons are support burden, security posture, or focus.
- Check which of those still hold. Write a one-page memo.
- Have legal or security check your customer contracts for restrictions on data flowing to third-party systems.

**Step 4: Go/no-go gate (end of October)**
Set the thresholds before you look at the data. For example: go if at least 3 deals, or any single large deal, were materially affected, or at least 5 customers describe a concrete use case. Otherwise no-go.

**Step 5a: If no-go**
- Give sales a positioning answer: workflow-first by design, with a stated reason.
- Give them an honest roadmap line with no date.
- Set a re-check date, for example end of Q1.

**Step 5b: If go, ship a narrow beta, not GA**
- **Scope:** read-only. Four to six tools, such as list documents, get review status, get findings, and search. No uploads and no writes.
- **Auth:** per-user OAuth reusing existing permissions.
- **Safeguards:** audit log, rate limits, per-tenant kill switch, and untrusted-content labeling on document text.
- **Distribution:** 3–5 design-partner customers, labeled beta.
- **Timeline:** build in November, with a code freeze before the holidays. Partners use it in December and January. GA in Q1 only if usage is real.
- **Promise to sales:** "beta with design partners in January", not "MCP live in January".

## Realistic timeline

Today is Oct 9, so January leaves about 12 weeks. After holidays and the evidence phase, you have roughly 7–8 build weeks. That's enough for a narrow beta if you decide by end of October. It isn't enough for a polished, supported GA.

## What would change my advice

- A single large deal blocked on it: go sooner.
- Your service layer is missing: the sizing doubles, so lean no-go for January.
- Customer contracts restrict third-party data flow: resolve that before any build.

## Questions for you

1. Is there a service or API layer under the web app, or does the app hit the database directly?
2. Why was "no integrations" chosen: support load, security, or focus?
3. Is the head of sales pointing at specific deals, or at the announcements?