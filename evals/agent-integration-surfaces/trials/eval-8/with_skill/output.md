**Do first (10 min):** open the CDN admin console. Find any "block AI bots", managed robots.txt or bot-fight preset, and note whether it is on. Everything else depends on that answer.

# Agent integration plan: Hollins Grid

## Verdict

Most of "everything" is deleted for this launch. Your ceiling is config only (CDN console plus the docs team's config) and your date is 2 weeks. Together these cut every rung that needs engineering.

What survives:

- The reachability gate
- Edge-log measurement
- The Context7 claim and docs markdown
- Optionally, api-catalog as background work

I cannot confirm "agent-ready" as a claim with this scope. I can confirm "our docs and API spec are readable and discoverable by AI assistants and coding agents." Give the CMO that wording (see Launch wording below).

## Assumptions (overturn any of them)

| Interview answer | Default used | Why |
| --- | --- | --- |
| 1. Agent classes that matter | Chat assistants and AI search first, since buyers shortlist observability tools with them. Coding agents second, via the OpenAPI spec | Unanswered. Not enough evidence for fleets |
| 2. What agents do | Read docs, pricing and contact info. Call the API with the customer's existing key | Unanswered |
| 3. Surfaces | Public API plus OpenAPI spec. No CLI, no MCP, no Agent Skill | Unanswered; you named none |
| 5. Edge | Preset status unknown | The gate decides |
| 6. Signals | None collected | No baseline exists |
| 7. Destructive operations | Read-mostly API; no money movement | Unanswered. If the API can delete dashboards or alert rules, tell me and C moves up |

Given by you: sales-led only (answer 4), SSO-only login, config-only ceiling (answer 10), 2-week date (answer 8).

## 1. Agent class × surface matrix

| Surface | Training | AI search | User-triggered fetch | Hosted browser agent | Coding agent / fleet |
| --- | --- | --- | --- | --- | --- |
| Marketing site | CMO call; default allow (no paywalled content) | allow: buyers shortlist through AI answers | allow | allow | allow |
| Docs and OpenAPI spec | allow: models then know your API | allow | allow | allow | allow, markdown |
| Pricing, plans, contact-sales | allow | allow | allow | allow | allow, markdown |
| Contact-sales form | deny | deny | allow read | allow verified agents; no CAPTCHA-only gate | n/a |
| App (SSO) | deny | deny | n/a | deny at the edge: no agent path exists | n/a. Local browser agents inherit the human's session |
| API | n/a | n/a | credential required | credential required | existing customer key. Unchanged |

Notes:

- Do not use a blanket "block AI bots" setting. It also blocks `Claude-User`, `ChatGPT-User` and AI search, which are the readers that matter before a sales call.
- Denials must live in CDN rules, not in robots.txt alone. OpenAI and Google user-triggered fetchers may ignore robots.txt.
- If the CMO wants training denied on marketing pages, deny `GPTBot`, `ClaudeBot`, `CCBot`, `Google-Extended`, `Applebot-Extended` and `meta-externalagent` on `/blog/` (path is an example). That is one line per token and per class.

## 2. Reachability gate (runs first; every rung scores zero until it passes)

| Class | Surface | Status | Blocking rule | Owner |
| --- | --- | --- | --- | --- |
| AI search (`OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`) | marketing, docs, pricing | unverified | check preset | CDN admin |
| User-triggered (`ChatGPT-User`, `Claude-User`, `Perplexity-User`) | marketing, docs, pricing, spec URL | unverified | check preset | CDN admin |
| Hosted browser agent | contact-sales form | unverified | check CAPTCHA | CDN admin |
| Training crawlers | docs | unverified | check preset vs CMO decision | CDN admin, CMO |
| Any class | app (SSO) | expect deny | confirm rule exists | CDN admin |

Steps:

1. Read the CDN rule set for each token above and for any "AI bots" preset. The rule decides; a status code only samples it.
2. Request each public surface with each real user-agent string from an ordinary network. Record the status and any challenge page.
3. A spoofed UA from your laptop tests only UA rules. For IP- or signature-verified classes, count 200s from verified traffic in edge logs over 7 days. Otherwise mark them unverified, which is not a pass.
4. Fix accidental blocks now. A deliberate security-team setting that blocks an "allow" cell goes to its owner with the cost named. Do not change it silently.
5. Check that the OpenAPI spec URL is fetchable by the allowed classes. A WAF rule on `/openapi.json` is a common silent failure.

## 3. Identity and delegation

No new credentials ship in this window. The model for each class:

| Class | Identified by | Authority | Credential | Scope, lifetime | Sponsor | Revocation |
| --- | --- | --- | --- | --- | --- | --- |
| Crawlers, fetchers, browser agents | CDN verified-bot category or vendor IP list. A UA string is a claim, not an identity | none: public pages only | none | n/a | n/a | edge rule |
| Customer agent fleet | the customer's existing API key | the customer's | existing key | whatever it is today | the customer's admin | rotate the key |

Gaps I cannot close with config:

- A customer who pastes an API key into an agent leaves the agent holding a long-lived key. There is no per-agent revocation. Rung C (agent-labelled, scoped, short-lived keys) fixes this.
- The exit criterion "zero paths where an agent holds a human's long-lived key" is therefore not met. Listed, not hidden.
- SSO-only login means no agent can authenticate to the web app. That is correct for now. Do not build around it.

## 4. Execution path per class

- **Coding agents and chat assistants:** read docs and the OpenAPI spec. No CLI, so no Agent Skill.
- **Fleets:** call the API with customer keys. No change.
- **Shell-less chat clients that act on a user's account:** would need MCP. No evidence they exist yet (see Deleted rungs).

## 5. Signup path

Deleted. Hollins Grid is sales-led with SSO-only login, so there is no self-serve account for an agent to create.

An agent cannot "sign up", and the plan must not pretend otherwise. The agent-readable replacement is a pricing/contact page in markdown that says plainly: "Sales-led. Contact sales at <URL>. SSO-only login." That way an agent comparing tools routes the buyer correctly instead of guessing.

## 6. Discovery listings and files

| Item | Owner | Effort | When |
| --- | --- | --- | --- |
| Context7: search for an existing third-party entry, then claim it with `context7.json` | docs team | low | week 1 |
| Context7 config: `projectTitle` ≤100 chars, `description` ≤500 chars, `excludeFolders` for old docs. No promotion text; it is rejected | docs team | low | week 1 |
| Context7 refresh call on push to the default branch | docs team CI config | low | week 1. Skip if the docs team cannot add a CI step |
| Markdown via `Accept: text/markdown` on docs, pricing, plans, limits and status pages, if the CDN offers conversion | CDN admin | low | week 2 |
| `/.well-known/api-catalog` (RFC 9727) pointing at the OpenAPI spec | docs team or CDN static response | minutes | background task, not a launch milestone |

Rules for the markdown item:

- Return `Content-Type: text/markdown; charset=utf-8` and `Vary: Accept`.
- Never send `noindex` on the negotiated response of a canonical URL.
- Override the CDN's default content signal if training is denied. One CDN's conversion defaults to `ai-train=yes`, which would contradict a deny.
- Test conversion on a real page before announcing it.

Only English docs are indexed by Context7. Old docs folders must be named `*deprecated*`, `*legacy*`, `*archive*` or `old`, or listed in `excludeFolders`. A folder named `v1-docs` gets indexed as current.

## 7. Agent-safe API checklist

None of it is verifiable without engineering. The docs team can read the OpenAPI spec and docs to mark each item:

| Item | Status | Hand-off |
| --- | --- | --- |
| Stable machine error codes, failing field, next step | unverified | `api-error-design` |
| Idempotency key on mutating calls | unverified | `api-idempotency-retry` |
| Published rate limits, per credential, `Retry-After` on 429 | unverified | `api-rate-limit-policy` |
| User-generated fields marked untrusted (dashboard names, alert text) | unverified. Likely fails | engineering backlog |
| Spend cap per agent credential | n/a: sales-led, no purchases through the API | n/a |
| Sandbox or test mode | unverified | `api-test-mode-design` |
| Dry-run or confirm token on destructive operations | unverified | `cli-interface-design` / `mcp-server-offering` |

## 8. Measurement plan

Start in week 1. The baseline needs about 7 days of logs, and no rung can show it worked without one.

1. In the CDN logs, add an agent-class field: `crawler`, `search`, `fetcher`, `browser`, `human`, `unknown`. `unknown` is a value, never null.
2. Classify with the CDN's verified-bot category or vendor IP lists. A UA token alone is low confidence. Label it as such.
3. Baseline: visits by class × surface (marketing, docs, spec, pricing, contact form). Record 200 vs 403/429/challenge per class. Record the top 10 docs pages fetched by AI classes.
4. Re-measure at day 14 and day 30 after the fixes.

Reporting rules:

- Write "at least N%, from edge-log classification". Do not publish one headline "agent share" number.
- Never sum crawler hits and API calls.
- Never report downloads as agent usage.
- Skip env-var detection and MCP `clientInfo`. No CLI or MCP exists, so there is nothing to tag.
- The agent funnel (resources, claim rate) does not apply. Funnel stage 1 and the "blocked at the edge" failure point are the only stages you can measure now.

## 9. Ranked rungs, in execution order

| # | Rung | Owner | Delegated skill | What moved it |
| --- | --- | --- | --- | --- |
| 0 | Reachability gate and fixes | CDN admin | none (this skill) | Always first. A CDN preset blocks everything else silently |
| 1 | A: edge-log classification and baseline | CDN admin | none | Config-only ceiling shrinks A to edge logs. It runs first so the later rungs have a baseline |
| 2 | B: Context7 claim, docs and pricing markdown | docs team, CDN admin | `coding-agent-docs-optimization` | Date (answer 8) keeps only what ships in 2 weeks. Efficiency rank 2 |
| 3 | G: api-catalog | docs team | none | Public spec exists. Background only. Almost no reader yet |

Schedule:

1. Days 1-2: run the gate. Start logging with the class field.
2. Days 3-5: fix blocks. Decide the training policy with the CMO.
3. Days 5-10: claim Context7. Turn on markdown for docs, pricing and plans if the CDN supports it.
4. Days 10-14: re-run the gate. Check the day-14 measurements. Finalize the launch wording.

### Deleted rungs

| Rung | Reason | Trigger to revisit |
| --- | --- | --- |
| C. Agent credentials and delegation | Needs engineering (config-only ceiling). It is the rung I would build first with a quarter of one engineer. Reasons: highest value, and the long-lived-key gap above | Any destructive API operation, or customers pasting keys into agents |
| D. Skill plus `--json` CLI | No CLI exists. Ceiling blocks building one | Logs show shell agents failing, or a CLI is built for other reasons |
| E. MCP server | Needs engineering. The CMO asking for it is not evidence that shell-less clients or per-user remote access exist | A customer or RFP names MCP, or logs show chat clients calling the API |
| F. Provision-then-claim signup | Sales-led with no self-serve path (answer 4) | Never, unless the sales model changes |
| Agent card | The product exposes no agent for other agents to talk to. An agent card never replaces the OpenAPI spec | Hollins Grid ships its own agent |

If the 2-week window were removed and one engineer had a quarter, the order would become: A, B, C, then D and E only on log evidence. F stays deleted either way.

## Launch wording

Say: "Hollins Grid docs, pricing and API spec are readable by AI assistants and coding agents."

Do not say any of these:

- "Agents can sign up." Sales-led and SSO-only make this false.
- "MCP server" or "CLI skill." They do not exist.
- "X% of our traffic is agents." No method yet, and anything from env vars is a floor.

## Exit criteria status

| Criterion | Status |
| --- | --- |
| Zero "allow" cells fail | Open: gate not yet run |
| 100% of "deny" cells enforced at the edge | Open: confirm rules exist |
| Every credential names scope, lifetime, sponsor, revocation | Not met: existing keys are long-lived. Listed in section 3 |
| Every agent-facing surface emits an agent-class field, and a baseline exists | Open: starts week 1 |
| Every rung scheduled with an owner or deleted with a reason | Met |

## Next action

Open the CDN console now. Find the AI-bot preset or bot-management rules and tell me whether anything blocks `ClaudeBot`, `GPTBot`, `ChatGPT-User` or `Claude-User`. That answer starts the gate.