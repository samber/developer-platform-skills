# Pellucid Billing agent integration plan

**Next action (today):** run the reachability gate in step 2 against your own edge. Nothing below works until it passes.

I haven't run any request against Pellucid's edge, so every gate result below is still to be measured. Where the interview left a question open, I print the default I assumed so you can overturn it.

## 0. What the Slack report and the security claim actually mean

- **CAPTCHA isn't why Claude Code can't sign up.** Claude Code and Cursor's agent run a shell and call your CLI or API. They never see the signup page. If they hit it, it's through a local browser agent. That is the one class edge rules can't target, because it has the user's own IP and user-agent. A CAPTCHA-only step blocks it for good, and agents shouldn't solve CAPTCHAs.
- **The September edge settings don't "keep every AI agent out".**
  - `GPTBot` and `ClaudeBot` are training crawlers. Disallowing them says nothing about `Claude-User`, `Claude-SearchBot`, `OAI-SearchBot`, `PerplexityBot`, `Google-Agent` or the Meta and Microsoft fetchers.
  - `ChatGPT-User` is a user-triggered fetcher. OpenAI says robots.txt rules "may not apply" to it.
  - robots.txt is a preference, not enforcement. What actually protects the dashboard is login plus a credential. Nothing in the setup you described counts as dashboard protection.
- **The "Block AI bots" preset probably hurts you.** It likely blocks AI search and user-triggered fetches of your docs and pricing. Devs asking an assistant about the Pellucid API then get stale or scraped answers. Nobody has measured this.

## 1. Defaults I assumed

| Question | Default | Effect |
| --- | --- | --- |
| Agent classes that matter | Coding agents with a shell (Claude Code, Cursor). No evidence yet of shell-less clients or customer agent fleets. | D is in. E has no evidence yet. |
| Surfaces | REST API, `pb` CLI with `--json` on most commands. Public OpenAPI spec unknown. | D is cheap. G depends on the spec. |
| Date | 6 weeks (customer summit). | Hard-date re-rank. |
| Money movement | Refunds. | C moves above everything. E and F wait on write-safety. |
| Channel | Standing, not one-off. | C and F compound after the summit. |
| Effort | One engineer for the quarter. | C through F are affordable but must be sequenced. |

## 2. Reachability gate (first, week 1)

For each "allow" cell, request the surface with the class's real user-agent from an ordinary network. Then read the CDN rule that fired. The rule decides; the status code only samples it.

| Class | Surface | Test | Status |
| --- | --- | --- | --- |
| User-triggered (`Claude-User`, `ChatGPT-User`, `Perplexity-User`) | docs, pricing, API reference | UA request plus rule read | unverified |
| AI search (`Claude-SearchBot`, `OAI-SearchBot`, `PerplexityBot`) | marketing, docs | same | unverified |
| Hosted browser agent | signup | headless browser, record the challenge | unverified |
| Coding agent, CLI | API host | `pb` and plain `curl` from a laptop | unverified |

- A spoofed user-agent tests your UA rules only. For IP-verified or signature-verified classes, count 200s in the edge logs over a week. An unverified cell is not a pass.
- Fix accidental blocks now: the preset on docs, and the preset on the API hostname. Check that the preset isn't also challenging `api.` or CLI traffic.
- The preset was a deliberate security decision, so don't flip it silently. Hand it to the security owner with the cost named: "AI answers can't fetch our docs or pricing". Ask for a split: block training crawlers everywhere, and allow search and user-triggered fetchers on marketing and docs. Enforce at the CDN, not in robots.txt alone.

## 3. Agent class × surface matrix

| Surface | Training | AI search | User-triggered | Hosted browser agent | Coding agent / fleet |
| --- | --- | --- | --- | --- | --- |
| Marketing, pricing | business call (currently deny) | allow | allow | allow | allow |
| Docs | business call. Allow is the default, because models then know your API. If deny stays, say so: models answer from older scraped copies. | allow | allow | allow | allow, as markdown |
| Signup | deny | deny | allow read | allow verified agents. No CAPTCHA-only gate. | CLI or API, later claim flow |
| Dashboard | deny | deny | n/a | verified agent inside a user session. Prefer the API. Refunds need out-of-band approval. | n/a, use the API |
| API | n/a | n/a | credential required | credential required | agent credential |

- Local browser agents inherit the human column. Their levers are labelled form fields and an API path, not edge rules.
- Replace "one `Disallow: /` per token" with per-class lines. Each vendor needs one line per class.
- Use CDN rules on verified identity (vendor IP list or Web Bot Auth signature). A UA match alone admits every scraper that copies the string.
- Content signals and pay-per-crawl are optional. Skip them for now.

## 4. Identity and delegation (answer to "read the live secret key from an env var")

**No.** A live key is a human's long-lived credential, and Pellucid can issue refunds.

- One leaked agent context (a transcript, a log, a prompt injection through an invoice field) exposes the whole account.
- Revoking that key takes the human's integration down with it.
- No log line can say "agent X acted for user Y".

What to do instead:

| Field | Value |
| --- | --- |
| Agent class | coding agent with a shell |
| Identified by | the credential you issue |
| Authority | the user's grant, narrowed |
| Credential | agent-labelled restricted key. Test mode by default. No refund scope unless the user adds it. |
| Scope | read invoices, create invoices. `refunds:create` is a separate scope. |
| Lifetime | days, never "until revoked" |
| Sponsor | the human who created it, shown in the key list |
| Revocation | per key, from the user's settings, without logging the human out |
| Approval gate | every refund and every live-mode write goes to `pending_approval`. The user confirms by email or push, outside the agent's session. |

- **Minimal C ships inside the 6 weeks.** That means agent-labelled scoped keys plus the out-of-band approval gate. Money wins inside the window.
- **Defer the device grant** (RFC 8628 for `pb login`) until after the summit. It has no money risk of its own but costs more engineering.
- **One listed exception.** A coding agent driving a human's logged-in `pb` inherits the per-install session. Bound it with refresh-token rotation, an absolute lifetime and the narrowest scopes the CLI needs. Per-agent revocation is impossible on that path. Tag its calls through env-var detection.
- **Web Bot Auth** proves the operator, not the user. Never attach user permissions to a signature.
- Hand key format and rotation to `api-auth-key-management`. Hand grants and consent to `oauth2-provider-design`.

## 5. Execution path per class

- **Coding agents (Claude Code, Cursor): Agent Skill piloting `pb --json`.** The CLI exists, so this is low effort and ships before the summit.
- **Customer fleets:** API plus SDKs. No work needed beyond C.
- **MCP:** see rung E below.

**Skill-to-CLI contract:**
- JSON on stdout only. Banners, progress and update notices go to stderr.
- Non-zero exit on failure, with a JSON error object carrying a stable `code`.
- No prompt when stdin isn't a TTY. Every prompt has a flag.
- Agent mode is auto-detected and always settable by flag.
- Next-step hints are data fields (identifiers), never shell strings built from untrusted data.
- Refund commands take `--dry-run` and a confirm token. They don't prompt.
- "Most commands" is the gap. List the commands without `--json` and close it.
- CI parses stdout of every `--json` command as JSON, in normal and agent mode. CI also runs each documented skill workflow against a sandbox account.
- The skill carries the workflow order and recovery from named error codes. It never copies flag lists; it points at `--help --json`. The skill's version tracks the CLI's.
- Hand-offs: `cli-interface-design`, `agent-skill-offering`.

## 6. Signup path

- **Within 6 weeks:** a human signs up once, with the CAPTCHA unchanged for humans. The agent then runs on the scoped key from step 4. That fixes the "Claude Code can't sign up" complaint for the common case.
- **Edge:** add an allow rule for verified signed agents, so hosted browser agents don't hit a CAPTCHA-only gate. Don't build CAPTCHA bypasses and don't let agents automate the human form.
- **Provision-then-claim (F) is starved:** it needs signup, billing and abuse controls rebuilt. Promote it to rung 1 only if the baseline shows agents already creating a meaningful share of new accounts. Its design, when you get there:
  - Unauthenticated call returns a test-mode resource, a single-use `claim_url` and `expires_at`.
  - Unclaimed resources stay in test mode only. Live mode starts at claim.
  - Terms of Service are accepted at claim, and unclaimed resources hold no personal data.
  - Add per-IP and per-signature creation caps, plus a kill switch.

## 7. Discovery

- **Context7:** search for a third-party entry first, then claim it with `context7.json`. Name old docs folders `*deprecated*` or `*legacy*`, or list them in `excludeFolders`. Add a refresh call on push to the default branch.
- **Markdown:** serve `Accept: text/markdown` for docs, pricing, plan limits and status pages. Send `Vary: Accept` and don't send `noindex` on canonical URLs.
- **api-catalog (RFC 9727):** publish it as a background task only if a public OpenAPI spec exists. If there is none, delete the rung.
- **Agent card:** deleted. Pellucid exposes no agent that other agents talk to.

## 8. Agent-safe API checklist

| Item | Status | Owner |
| --- | --- | --- |
| Stable machine error codes, failing field, next step | verify | `api-error-design` |
| Idempotency key on every mutating call. Required on refunds, since agents retry blindly. | verify | `api-idempotency-retry` |
| Published limits, keyed per agent credential, `Retry-After` on 429 | verify | `api-rate-limit-policy` |
| Customer-supplied fields (names, memo, descriptions) marked untrusted. An agent reading an invoice is a prompt-injection path. | likely fail | API team |
| Refund spend cap per agent credential, plus out-of-band confirmation | build | step 4 |
| Test mode for end-to-end runs without real side effects | verify | `api-test-mode-design` |
| Dry-run or confirm token on destructive calls | build | `cli-interface-design` |

## 9. Measurement (before any rung ships)

- Put an agent-class field on every request record: crawler, search, fetcher, browser, coding, fleet, human, unknown. `unknown` is a value, not a null.
- Append the detected agent to the CLI and SDK user-agent: `pb/x.y.z (darwin; arm64) agent/claude-code`. Log it server-side as its own field.
- Check `AI_AGENT`, `AGENT`, `CLAUDECODE` and similar variables. Many harnesses set none, so env detection is a floor.
- Classify edge logs by vendor token confirmed against IP lists. Count the blocks too: absence of agent traffic in logs may just mean the edge blocked it.
- Funnel: visits by class → agent-created signups → claim rate → activated → paid → API calls per agent credential → failure points (blocked at the edge, stopped at a prompt, failed auth).
- Report agent share as "at least N%, from env-var detection". Never sum crawler hits and API calls. Never report package downloads as agent usage. Neon's 80% and Supabase's 60–70% are company claims about database creations, not targets for you.

## 10. Ranked rungs and the 6-week schedule

| Order | Rung | Weeks | Owner | Delegated to | Why it sits here |
| --- | --- | --- | --- | --- | --- |
| 0 | Gate fixes | 1–2 | platform + security | – | Every rung scores zero while the preset blocks them |
| 1 | A. Measurement | 1–2 | platform | – | Baseline before anything else |
| 2 | B. Docs markdown, Context7 claim | 2–3 | DevRel / docs | `coding-agent-docs-optimization` | Cheap and fast. Needs the gate fix. |
| 3 | C (minimal). Scoped agent keys, refund approval gate | 2–5 | platform + security | `api-auth-key-management` | Money-moving, so it outranks all but the gate |
| 4 | D. Skill + `--json` CLI | 3–5 | CLI engineer | `cli-interface-design`, `agent-skill-offering` | CLI exists, so effort is low. Serves the summit. |
| 5 | E. MCP | after summit, or a read-only demo | platform | `mcp-server-offering` | See below |
| 6 | F. Provision-then-claim | after summit | product + platform | – | Starved until the baseline shows agent signups |
| 7 | G. api-catalog | background | docs | `discovery-and-content-serving` | Only if a spec exists |

Week 6 is rehearsal and buffer.

**On the CEO's MCP ask.** A stakeholder asking for a surface is not evidence that its client class exists. Claude Code and Cursor have shells, and the skill plus CLI serves them better and costs fewer tokens. MCP earns its place for shell-less chat clients or per-user remote auth. Two ways to proceed:

- **Recommended for the summit:** demo skill plus CLI with Claude Code and Cursor. Treat MCP as the next rung, triggered by evidence of shell-less clients or customers asking for it. Get that evidence from the Slack threads and sales calls.
- **If the CEO still wants a live MCP:** ship a **read-only, test-mode** server. No refund tool. Write tools wait for C and the approval gate. Keep it generated from the same spec or command catalog as the CLI so they can't disagree.

I haven't checked either route against Pellucid's actual API, so confirm the read-only scope list with whoever owns the spec.

**Deleted:** the agent card (no agent endpoint). G is deleted if no public OpenAPI spec exists.

## 11. Exit criteria

- Zero "allow" cells fail, or each is listed as unverifiable with the reason. Every "deny" cell is enforced at the edge, not only in robots.txt.
- Every agent credential names scope, lifetime, a sponsoring human and per-agent revocation. The bounded `pb` session is the one listed exception.
- Every agent-facing surface emits the agent-class field, and a baseline exists before the first rung ships.
- Every rung has an owner and a week, or a deletion reason.

## 12. Decisions I need from you

1. Who owns the CDN preset? They need the cost named: AI answers can't fetch docs or pricing.
2. Should docs allow training crawlers? The default is yes. Deny is legitimate if the docs are the product.
3. Is there a public OpenAPI spec? That decides G.
4. Which client does the CEO have in mind for MCP, and which customers asked? That decides whether E moves up.