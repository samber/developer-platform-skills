**First action:** open your CDN console and check whether bot protection challenges AI user agents. Most "agent-ready" failures start there. Run this from any terminal:

```bash
for ua in "GPTBot" "ClaudeBot" "PerplexityBot" "Mozilla/5.0"; do
  printf "%s -> " "$ua"
  curl -s -o /dev/null -w "%{http_code}\n" -A "$ua" https://docs.hollinsgrid.example/
done
```

Any 403 or 429 on the docs, pricing or OpenAPI URL is the first fix. Replace the host with your real one. I have not run this against your site.

## The honest frame

With zero engineering, you can ship **agent-readable**. You cannot ship **agent-actionable**. Sales-led, SSO-only means three of your asks don't fit the product.

- **Agent signup:** no self-serve exists, so there is nothing to sign up for. Skip it.
- **A2A agent card:** it describes a running agent with an endpoint. You have none. A card that points nowhere is a false claim. Skip it.
- **Product MCP server and CLI:** these need hosting, auth and security review. For an observability platform they would expose customer telemetry. That is a Q1 project, not a 2-week one.

Two things I don't know yet. Both change the ranking:
1. Which docs platform (Mintlify, ReadMe, GitBook, Docusaurus, other)?
2. Which CDN and plan tier (Cloudflare, Fastly, Akamai, CloudFront)?

## Ranked list

Rank = value to a real agent, divided by effort, with no false claims.

### Do now (config only)

| # | Item | Owner | Effort |
|---|------|-------|--------|
| 1 | **Unblock AI crawlers** at CDN and `robots.txt` | CDN admin | 1–2 h |
| 2 | **Agent-readable docs**: `llms.txt`, `llms-full.txt`, `.md` page variants | Docs team | 0.5–2 days |
| 3 | **OpenAPI discoverability**: stable URL, linked from `llms.txt`, `Link` header | CDN admin + docs | 1 h |
| 4 | **Docs MCP server** (read-only), if the docs platform has a toggle | Docs team | 1–4 h |
| 5 | **Public "buying and security" page** an agent can parse | Docs + product marketing | 2–3 days |

### Do if time allows

| # | Item | Why it's lower |
|---|------|---------------|
| 6 | **Agent skill file** (`SKILL.md`) that teaches an agent your API | Customers must get tokens through SSO, so the skill documents that handoff. Needs a real test run. |
| 7 | **Score before and after** with `npx is-agentic` or Frase's free checker | Gives the CMO a number to quote. |

### Do not do now

| Item | Reason |
|------|--------|
| Agent signup | No self-serve product. |
| A2A agent card / MCP server card | No agent or server exists to describe. |
| Product-API MCP server | Needs engineering and a security review. Plan for Q1, read-only first. |
| CLI | Needs engineering. |

## How to do each one

**1. Unblock crawlers (CDN admin)**
- In the CDN bot or WAF settings, allow GPTBot, ChatGPT-User, OAI-SearchBot, ClaudeBot, PerplexityBot and Google-Extended on docs, pricing and the OpenAPI path. Exclude the authenticated app.
- Remove any JS challenge on those paths.
- Block training-only crawlers (for example CCBot) if legal wants that. Don't block the search-and-cite bots.
- `robots.txt` must not `Disallow` them.
- Some CDNs have a "block AI bots" default toggle. Check it. It may already be on.

**2. Agent-readable docs (docs team)**
- Most docs platforms generate `llms.txt` and per-page `.md` automatically. Turn it on.
- If not, host static files. Template for `llms.txt` (a plain-text file at the site root, written in Markdown format):

```markdown
# Hollins Grid

> Enterprise observability platform. Sold through sales only; no self-serve signup. Login is SSO-only.

## Docs
- [Getting started](https://docs.hollinsgrid.example/start.md): concepts and architecture
- [API reference](https://docs.hollinsgrid.example/api.md): REST API overview and auth

## API
- [OpenAPI spec](https://docs.hollinsgrid.example/openapi.json): public, versioned

## Buying
- [Buying and security](https://hollinsgrid.example/buying.md): plans, SSO, compliance, how to contact sales
```

- If your CDN offers Markdown content negotiation (serves `.md` when the client sends `Accept: text/markdown`), enable it. Check your plan tier.

**3. OpenAPI discoverability**
- Pin the spec to one stable URL.
- Add a CDN response-header rule on the docs root: `Link: </openapi.json>; rel="service-desc"`.
- List the spec in `llms.txt`.

**4. Docs MCP server**
- Several docs platforms host a read-only MCP server for your docs as a toggle. Ask the docs team to check theirs.
- If it exists, this is the honest "we have an MCP server" line. It serves docs, not customer data or product actions.
- Don't announce it as a product MCP.

**5. Buying and security page**
Agents shortlist vendors from public text. "Contact sales" with nothing behind it gets skipped. Publish only what legal approves:
- Who it's for and what it monitors.
- How pricing works (model and unit, even without numbers).
- SSO providers supported and compliance badges (SOC 2, ISO, GDPR).
- How to start: a sales contact and the typical process.

Serve it as plain HTML with a `.md` twin. Don't put it behind a form.

## What to tell the CMO

Don't claim "agent signup", "agent-native" or "MCP-enabled product". Claim this instead:

> "Hollins Grid is agent-readable: our docs, API spec and buying information are open to AI assistants and coding agents, with a documentation MCP server."

Only use the MCP clause if item 4 ships. Product actions for agents are a roadmap item.

## 2-week plan

1. **Days 1–2:** crawler unblock, then rerun the `curl` loop. Run the baseline score (item 7).
2. **Days 3–6:** docs team ships items 2, 3 and 4.
3. **Days 5–9:** write and approve item 5 with legal.
4. **Days 10–11:** item 6, only if the first five are done.
5. **Day 12:** rerun the score and the `curl` loop. Test `llms.txt` and the MCP server from a real agent.
6. **Day 13:** freeze and give the CMO the final claim wording.

## Open risks

- Legal may refuse to publish the buying page in time. Fallback: ship items 1–4 and drop the "buying" claim.
- Hosted docs MCP may not exist on your platform. Fallback: drop it and the MCP wording.
- Some CDN features (Markdown negotiation, bot controls) may need a higher plan.

**Next:** tell me your docs platform and CDN vendor. I'll turn items 1–4 into exact click paths.