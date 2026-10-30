# Sanity check: "3% of traffic is AI agents" and "50% agent signups by Q4"

I followed the `agent-integration-surfaces` skill, including its measurement and access-policy references. I haven't seen your logs, CDN config or signup data. Everything below comes from the numbers you gave me.

## Verdict

- ❌ **"3% of our traffic is AI agents."** Don't put this on a slide. The 3.1% is a count of requests whose User-Agent contains three strings. It is not a share of agent traffic.
- ❌ **"Supabase is at 70%, so we're way behind, target 50%."** Don't use it as a benchmark. Supabase's figure is a company claim with no disclosed counting method, and it counts database creations. Your product isn't infrastructure that agents provision by default.
- ✅ **What to say instead:** "We have a baseline of at least X% of signups from detectable agents, measured by method M. We're building the instrumentation to track it properly."

## Why 3.1% doesn't mean 3% agent traffic

1. **A User-Agent is a claim, not an identity.** Anyone can send `ChatGPT-User`. The skill's rule is to confirm with the vendor's IP list or a verified Web Bot Auth signature. Your number can include scrapers copying those strings.
2. **Your three substrings mix different populations.**
   - `GPT` matches `GPTBot`, which is a training crawler.
   - `GPT` also matches `ChatGPT-User`, which fetches one page because a person asked.
   - `Claude` matches `ClaudeBot`, `Claude-SearchBot` and `Claude-User`, which are training, search indexing and user-triggered fetching.
   - Those are three jobs with different intent. The skill says never to merge them into one "agent traffic" number.
3. **It misses most agents that matter to a SaaS.**
   - **Coding agents (Claude Code, Cursor and similar):** they run your SDK, CLI or plain HTTP calls from a developer machine. The User-Agent is your SDK's or `curl`'s, not "Cursor". They are invisible to this grep unless your SDK tags them.
   - **Local browser agents (an AI browser or extension):** they send the same IP and User-Agent as the human, so they can't be told apart.
   - **Hosted browser agents (ChatGPT agent and similar):** they identify through Web Bot Auth signatures or vendor IP ranges, not a friendly User-Agent.
   - **Customer agent fleets:** they arrive through the customer's API credential.
4. **Your edge may be hiding demand.** If a CDN or WAF "block AI bots" preset is on, blocked agents never reach nginx. Absence from the logs is not absence of demand. The skill calls this a failure mode.
5. **Requests are the wrong unit for a board.** One crawler can make thousands of requests. A board cares about signups, activated projects and revenue.

So 3.1% is neither a floor nor a ceiling. Spoofing inflates it and the blind spots deflate it. The skill's rule is to report agent share as "at least N%, by method M", never as a headline number.

## Why the Supabase comparison fails

- The skill lists Supabase's 60–70% and Neon's 80% as company-reported. The counting methods are undisclosed, and they count database creations, not paid workloads.
- Both sell infrastructure that coding agents provision by default. The skill says to use them as evidence that the channel exists, never as a target for a different product.
- A "50% by Q4" target has four holes:
  - **No baseline.** You can't call it behind without your own number.
  - **No detection method.** You can't target a share you can't count.
  - **Part of your funnel can't be agent-created.** Sales-led accounts have no self-serve path, so they can't be agent signups.
  - **Q4 is close.** It's 2026-10-30. If you mean calendar Q4, that's about two months. If you mean fiscal Q4, tell me which.
- A target set without a baseline also becomes a vanity number. If you hit it by counting more things, nothing has changed.

## What to measure

Count these in order. Items 1–3 are the baseline. Without a baseline, nothing later can show it moved.

### 1. Reachability gate (do first, about one day)

For each agent class you want to admit, request the marketing site, docs, signup and API. Record the status code, any CDN or WAF rule hit, and any CAPTCHA.

- Check whether a "block AI bots" preset or a signup CAPTCHA is on. These silently zero every later effort.
- Fix accidental blocks. If a block is deliberate, such as an anti-training rule, take it to its owner with the cost named. Don't change it silently.
- A spoofed User-Agent from your laptop only tests your User-Agent rules. For IP- or signature-verified classes, count verified 200s in edge logs over a week.

### 2. Classify traffic by agent class, not by string

Store a class field on every request record: `crawler`, `search`, `fetcher`, `browser`, `coding`, `fleet`, `human`, `unknown`. `unknown` is a value, not a null. Report each class separately and never sum them.

| Source | Detects | Confidence |
| --- | --- | --- |
| CDN logs with IP-list or signature verification | crawlers, fetchers, hosted browser agents | high once verified |
| User-Agent token alone (your current method) | anything claiming to be an agent | low, spoofable |
| Env vars read by your SDK or CLI (`AI_AGENT`, `AGENT`, `CLAUDECODE`) | coding agents | self-report, a floor only |
| MCP `clientInfo`, if you ship an MCP server | which MCP client connected | client-declared |
| Agent-labelled credential type | agent calls on your API | high, you issued it |

Many agent harnesses set no env var, so env detection undercounts. Treat it as a floor.

### 3. Tag your own SDK and CLI

- Append the detected agent to your SDK and CLI User-Agent, for example `brightmoor-sdk/2.1.0 (linux) agent/claude-code`.
- Log it server-side as its own field. For a product analytics SaaS, the strongest signal is likely **who installed the tracking snippet or SDK**, not who visited your website.

### 4. The agent funnel (this is the board metric)

1. Agent visits, by class and surface.
2. Agent-created signups or projects.
3. **Claim rate:** created, then claimed by a human.
4. Claimed to activated, then to paid. Here activated could mean "first event ingested".
5. API calls by agent class and by agent credential.
6. Failure points: blocked at the edge, stopped at a prompt, failed auth, error codes by class.

Claim rate and claimed-to-paid separate agent usage that becomes revenue from free-tier churn. That is what the board needs to see.

### 5. Reporting rules for the deck

- State the method and the floor caveat on the slide. For example: "At least N% of new self-serve signups in October came from detectable coding agents (SDK env-var detection)."
- Don't sum crawler hits and agent API calls.
- Don't use package downloads as agent usage.
- Report self-serve and sales-led separately. Agents mostly matter to the self-serve path.

## Suggested slide

> **AI agents: baseline in progress**
> - Known so far: X% of requests claim an AI User-Agent. This is a spoofable upper-ish signal, not a share of agents.
> - Now instrumenting: verified edge classification, SDK/CLI agent tagging, agent-created signup and claim funnel.
> - Q1 deliverable: first baseline of agent-created signups, claim rate and activation, with method stated.
> - Target: set after the baseline. External benchmarks (Supabase 70%, Neon 80%) are company claims about infrastructure provisioning and not comparable.

## Assumptions to check

I haven't asked you the skill's interview questions. Where I've guessed, correct me. The ranking below changes if any assumption is wrong.

- **Agent classes that matter:** coding agents with a shell and some hosted browser agents.
- **Humans get in through** self-serve signup with a free tier, plus sales-led accounts.
- **What an agent breaks:** it can write to ingestion and project settings. I'm assuming there are no money-moving operations.
- **Date and effort (defaults):** no hard date, a standing agent channel, one engineer for a quarter.
- **Unknown to me:** whether you have a public API, an SDK, a CLI, an MCP server, or a CDN preset in front of nginx.

## Ranked plan (default order)

| Order | Rung | Why | Owner |
| --- | --- | --- | --- |
| 0 | Reachability gate | Gate failures zero every rung below | Platform or infra |
| 1 | A. Measurement tags | Highest efficiency, and it is the baseline | Data or analytics |
| 2 | B. Docs markdown and Context7 claim | Cheap, helps coding agents read current docs | DevRel or docs |
| 3 | C. Agent credentials and delegation | Agents act for users without a human's long-lived key | Platform and security |
| later | D. Skill plus `--json` CLI | Add once logs show shell agents failing at login or prompts | Platform |

- **F (provision-then-claim signup) is deferred.** It is expensive and needs signup, billing and abuse controls rebuilt. It moves to rung 1 only if the baseline shows agents already create a meaningful share of new accounts. Sales-led accounts have no self-serve path, so F doesn't apply to them.
- **E (MCP server) and G (discovery files) are deleted for now.** E needs evidence of shell-less or per-user remote clients. G needs a public OpenAPI spec. Revisit when that evidence exists.

## Next steps

1. Answer these two so I can finalize the plan: do you have a CDN or WAF in front of nginx, and do you ship an SDK or CLI? (~2 min)
2. Run the reachability gate on signup and docs this week.
3. Ship SDK and CLI agent tagging and the class field before the board deck, even if the first baseline is small.
4. Replace the "3%" and "50% by Q4" lines with the slide above.