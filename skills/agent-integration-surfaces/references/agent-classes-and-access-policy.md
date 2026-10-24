# Agent classes and access policy

Contents: agent classes, vendor tokens, default matrix, enforcement layers, reachability gate, failure modes.

## Agent classes

| Class | What it does | Honors robots.txt | Verify by |
| --- | --- | --- | --- |
| Training crawler | bulk fetch for model training | yes, for the major vendors | vendor IP list |
| AI search indexer | builds the index behind AI answers | yes, for the major vendors | vendor IP list |
| User-triggered fetcher | fetches one page because a user asked | varies by vendor, see below | vendor IP list |
| Hosted browser agent | drives the web UI from the operator's cloud | not applicable | Web Bot Auth signature, vendor IP list |
| Local browser agent | drives the user's own browser (extension, AI browser) | not applicable | nothing: same IP and user-agent as the user |
| Coding agent with a shell | runs your CLI, SDK and HTTP calls from a developer machine | not applicable | env-var detection in your CLI/SDK, credential |
| Customer agent fleet | calls your API unattended with a customer credential | not applicable | the credential |

Edge policy cannot target local browser agents. Their levers are a UI agents can drive (labelled fields, no CAPTCHA-only step) and an API or claim path. The first four rows need edge policy. The last two arrive through your own credentials and need identity design (see the identity reference).

## Vendor tokens

| Operator | Token | Class | robots.txt stance | IP list |
| --- | --- | --- | --- | --- |
| OpenAI | `GPTBot` | training | honored | `openai.com/gptbot.json` |
| OpenAI | `OAI-SearchBot` | AI search | honored | `openai.com/searchbot.json` |
| OpenAI | `ChatGPT-User` | user-triggered | "robots.txt rules may not apply" | `openai.com/chatgpt-user.json` |
| OpenAI | ChatGPT agent | browser agent | n/a | signs with Web Bot Auth |
| Anthropic | `ClaudeBot` | training | honored, plus `Crawl-delay` | published list |
| Anthropic | `Claude-SearchBot` | AI search | honored | published list |
| Anthropic | `Claude-User` | user-triggered | honored; blocking it stops answers fetching your page | published list |
| Google | `Google-Extended` | token only, gates Gemini training and grounding | honored | none, no separate crawler |
| Google | `Google-Agent` | browser agent on Google infrastructure | user-triggered fetchers "generally ignore robots.txt" | `user-triggered-agents.json` |
| Perplexity | `PerplexityBot` | AI search | honored | published list |
| Perplexity | `Perplexity-User` | user-triggered | "generally ignores robots.txt" | published list |
| Common Crawl | `CCBot` | training corpus many models use | honored | none |
| Apple | `Applebot-Extended` | token only, gates training | honored | none |
| Meta | `meta-externalagent` | training | honored | none; verify by reverse DNS or ASN |

The table lists operators whose robots.txt stance was checked; others exist (user-triggered fetchers from Meta and Microsoft among them). Token lists change. Re-read each vendor's crawler page before writing rules.

A robots.txt for the default matrix with training denied on marketing pages only (paths are examples):

```
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: CCBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: meta-externalagent
Disallow: /blog/
Disallow: /signup
Disallow: /app/

User-agent: OAI-SearchBot
User-agent: Claude-SearchBot
User-agent: PerplexityBot
Disallow: /signup
Disallow: /app/

User-agent: *
Disallow: /app/
```

Docs stay open to training, per the docs default. It states preference only: enforce the same rules at the CDN, and keep app access behind login.

## Default matrix

Start here, then change any cell the business decides otherwise, with the reason in the plan.

| Surface | Training | AI search | User-triggered | Hosted browser agent | Coding agent, fleet |
| --- | --- | --- | --- | --- | --- |
| Marketing site | business call: allow, deny or price | allow | allow | allow | allow |
| Docs | allow, models then know your API | allow | allow | allow | allow, markdown |
| Signup | deny | deny | allow read | allow verified agents; no CAPTCHA-only gate | CLI or API signup, or claim flow |
| Authenticated app | deny | deny | n/a | verified agent inside a user session; prefer API; money actions need out-of-band approval | n/a, use the API |
| API | n/a | n/a | credential required | credential required | agent credential |

Local browser agents inherit the human column. Coding agents and fleets arrive through your credentials, so their cells are decided in the identity design, not at the edge.

Denying training on docs is legitimate when the docs are the product. Say what it costs: models then answer from older, scraped copies.

## Enforcement layers

Ranked by how much they actually enforce:

- enforcement, strongest first: `credential on the API > CDN or WAF rule on a verified identity > CDN rule on user-agent > robots.txt > content signals`

- **robots.txt** states a preference to crawlers that read it. It never stops a user-triggered fetcher that ignores it.
- **Content signals** (`search`, `ai-input`, `ai-train`) are a CDN vendor convention carried in a header or robots.txt. They express preference, not enforcement. One CDN's markdown conversion defaults to `ai-train=yes`; override it when training is denied, or the two signals contradict.
- **Pay per crawl** answers `402 Payment Required` with a `crawler-price` header; a paying crawler retries with `crawler-exact-price` or pre-declares `crawler-max-price`. Paying crawlers must sign their requests. Use it only on surfaces where denial is the alternative.
- **CDN default blocks.** At least one major CDN blocks AI crawlers by default on newly onboarded domains. Assume a preset exists until the gate proves otherwise.
- **CAPTCHA** on signup blocks legitimate browser agents and lets determined bots through. Prefer an allow rule for verified signed agents plus an API or claim path for agents.

## Reachability gate

For each cell marked allow or deny:

1. Request the surface with the class's real user-agent string from an ordinary network, and record status and any challenge page.
2. Read the CDN or WAF rules for that token and for any "AI bots" preset; the rule decides, the status code only samples it.
3. For browser agents, open signup and login in a headless browser and record whether a challenge appears.
4. For classes you cannot impersonate (signed agents, vendor IP ranges), count 200s from verified traffic in the edge logs over a week.
5. Mark each cell pass, fail with the blocking rule, or unverified. An unverified cell is not a pass.

A request with a spoofed user-agent from your laptop tests your user-agent rules only. It says nothing about IP-verified or signature-verified rules.

## Failure modes

- Blocking "all AI bots" to stop training and losing user-triggered fetches and AI search with it.
- Allowing by user-agent string alone, which admits every scraper that copies it.
- A security team's preset overriding a docs team's robots.txt, unseen by both.
- CAPTCHA on signup while the product markets itself as agent-friendly.
- Treating the absence of agent traffic in logs as absence of demand when the edge blocks it.
