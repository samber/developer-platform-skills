❌ Don't put "3% of traffic is AI agents" or "target 50% agent signups" on the slide. Neither number supports its claim. Re-cut the logs first (step 1 below, about 2 hours).

## Why the 3.1% fails

1. **It mixes four different things.** `Claude` also matches `ClaudeBot`, and `GPT` also matches `GPTBot`. Both are training crawlers, not agents acting for a user. `Cursor` is an IDE with a human at the keyboard.
2. **It undercounts real agents.**
   - Headless-browser agents send a normal Chrome UA.
   - Coding agents calling your API or docs often send `curl`, `node`, or `python-requests` UAs.
   - So 3.1% is neither the agent share nor a clean lower bound.
3. **The denominator is requests.** Requests count assets, API hits, and bot bursts. One bot session can make 200 requests, while one human signup is a handful. 3% of requests could be 0.3% of visitors or 10%. Also check whether SDK event ingestion from customers' end users is in these logs. For a product analytics SaaS it can swamp everything else.
4. **There is no baseline.** One month of data gives no trend.

## Why the 70% benchmark fails

- ⚠️ I did not verify Supabase's 70% or how they define "agent". Treat it as a vendor-reported number. It is likely counting databases created programmatically, for example through app-builder platforms.
- A database is a mandatory dependency that an agent must create to build an app. Analytics is an optional add-on. The two are different products, so Supabase's share is not a benchmark for you.
- You have no agent-signup baseline of your own, so "way behind" is unsupported.
- 50% is a target borrowed from someone else's number. It also has no definition and no owner. Agent signups are not the goal; activated and paying accounts are.
- You could hit 50% by making human signup worse. That is Goodhart's law.

## What to measure, ranked

1. **Split the actors.** Never report one "AI" bucket. Check vendor docs for current UA names.
   - Training crawlers: `GPTBot`, `ClaudeBot`, `CCBot`, `Bytespider`.
   - Search and retrieval bots: `OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot`.
   - User-triggered fetchers (a human asked an assistant): `ChatGPT-User`, `Claude-User`, `Perplexity-User`.
   - Unlabeled automation: headless browsers and scripts. Flag by behavior (no JS assets, a request rate no human reaches), not by UA.
   - Humans.
2. **Fix the denominator.** Report unique visitors or sessions on docs and marketing pages only. Exclude assets and the ingestion API. Report ingestion separately.
3. **Agent-assisted signups.** There is no single flag, so use several signals and report each:
   - Signup through CLI, API, device-code flow, or MCP.
   - Referrer from `chatgpt.com`, `claude.ai`, or `perplexity.ai`.
   - A required "how did you hear about us" field with an "AI assistant recommended it" option. This is the cheapest and most honest signal (about 30 minutes to add).
   - Programmatic API key creation within minutes of signup.
4. **Quality by cohort.** Compare agent-assisted and other signups on activation (first event ingested within 24 hours), 30/90-day retention, and paid conversion. This is the number the board cares about.
5. **Agent success rate.** Measure the share of agent-like sessions that complete the flow:
   - Docs fetches returning 200 versus 4xx.
   - SDK install to first event.
   - Signup blocked by CAPTCHA or email verification.

## Replacement slide (honest version)

- "At least 3% of requests self-identify as AI-vendor traffic, split into crawlers, assistant fetches, and agents. Lower bound; real agent share unknown."
- "We don't yet measure agent-assisted signups. Q4 goal: instrument 3 signals and publish a baseline."
- "Q1: set a target relative to that baseline, judged on activation and paid conversion, not signup count."

## Time to get real numbers

| Task | Effort |
| --- | --- |
| Re-cut last month's logs by actor class and unique visitors | about 2 hours |
| Add the signup question and referrer capture | about 30 minutes plus a deploy |
| A baseline you can trust | 4 to 6 weeks of data |

If the board meets before then, present the replacement slide, not a number.

**Next:** paste 20 sample `User-Agent` lines from the matched 3.1% (anonymized), and I'll tell you how many are crawlers versus fetchers versus agents.