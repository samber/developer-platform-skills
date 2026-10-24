# Agent traffic measurement

Contents: detection sources, tagging, funnel, published anchors, reporting rules.

## Detection sources

| Source | Detects | Confidence |
| --- | --- | --- |
| CDN or edge logs: crawler token confirmed by IP list or signature | crawlers, fetchers, browser agents | high once verified |
| User-agent token alone | anything claiming to be an agent | low, spoofable |
| Env vars read by your CLI or SDK | coding agents on developer machines | self-report, floor only |
| MCP `initialize` `clientInfo` name and version | which MCP client connected | client-declared |
| Credential type (agent-labelled key, delegated token with `act`) | agent calls on your API | high, you issued it |
| Claim flow state | agent-created resources | exact |

Env-var conventions compete, with no governing body: `AI_AGENT=<name>` (promoted by one platform vendor's detection library), `AGENT=<name>` (used by several agents), and agent-specific variables such as `CLAUDECODE`. Check all of them. Many harnesses set none, so env detection undercounts.

## Tagging

- Append the detected agent to your CLI and SDK user-agent: `mycli/4.2.0 (darwin; arm64) agent/claude-code`. Log it server-side as its own field.
- Log MCP `clientInfo` per session.
- Store the agent class on every request record: crawler, search, fetcher, browser, coding, fleet, human, unknown. `unknown` is a value, not a null.
- Instrument before shipping the first rung. A rung with no baseline cannot show it moved anything.

## Agent funnel

1. Agent visits by class and surface.
2. Agent-created resources or signups.
3. Claim rate: created to claimed by a human.
4. Claimed to activated, then to paid.
5. API calls by agent class and by agent credential.
6. Failure points: blocked at the edge, stopped at a prompt, failed auth, error codes by agent class.

Claim rate and claimed-to-paid separate agent usage that becomes revenue from free-tier churn.

## Published anchors

Company-reported, counting methods undisclosed, counting creations rather than paid workloads:

- Neon (via Databricks): over 80% of databases created by agents (2025).
- Supabase: over 60%, later 70%, of new databases launched by AI tools (2026).

Both sell infrastructure coding agents provision by default. Use them as evidence that the channel exists, never as a target for a different product.

## Reporting rules

- Report agent share with its method and its floor caveat: "at least N%, from env-var detection".
- Never sum crawler hits and agent API calls into one "agent traffic" number; they are different populations.
- Never report package downloads as agent usage.
