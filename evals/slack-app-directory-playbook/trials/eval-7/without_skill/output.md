Web lookup was denied (WebSearch and WebFetch both refused), so I checked none of this against Slack's current docs. I can't confirm that `mcp:connect` exists as a scope, or how the Slackbot MCP client treats listings. Treat every Slack-specific claim below as "verify before relying". The tool-description advice is general MCP practice and holds regardless.

## Do first (15 minutes)

1. Open Slack's current Marketplace guidelines and the Slackbot MCP client docs.
2. Search both for `mcp:connect`. Check whether Slack documents it as a scope an app can request, and whether a Marketplace app can use it as its only feature.
3. Ask Slack's Marketplace review contact (or the app-review form) this question: "Is an app whose sole function is registering a remote MCP server with Slackbot eligible for listing?" This answer decides the whole plan.

## Biggest risk: "only feature is connecting an MCP server"

- Slack's review historically rejects apps with no functionality inside Slack. Your app gives users nothing in Slack itself. The value comes from Slackbot calling your tools.
- If Slack has a dedicated MCP-connector listing type, you are fine. If not, expect "insufficient functionality" or "does not provide a Slack experience".
- Fallback: add a small native surface that reuses the same backend:
  - a `/lumatrace` slash command or App Home tab showing connection status
  - alert notifications posted to a channel, driven by `create_alert`
  - an unfurl for Lumatrace trace links
- Timeline: "list it next month" is risky. First-pass review often takes weeks, and rejections restart the queue. Plan for a later date, or ship the app as a directly installable (unlisted) app first.

## Change 1: tool descriptions (your stated gap)

One-word descriptions fail for two reasons. The model picks tools from descriptions, and reviewers read them as evidence of what the app does with user data.

For each tool, write:
- what it does, in one sentence
- when to use it, and when not to
- each parameter: type, format, allowed values, example
- what it returns, including size limits and truncation
- side effects, stated plainly

Starting drafts, adjust to your real behavior:

- `search_logs`: "Search Lumatrace log events by query within a time range. Read-only. Use to find errors or patterns. Do not use to fetch a known trace; use `get_trace`. Parameters: `query` (Lumatrace query string, example `service:api level:error`), `start`/`end` (ISO 8601, default last 1 hour), `limit` (1–100, default 20). Returns matching events, newest first, truncated at the limit."
- `get_trace`: "Fetch one distributed trace by ID, with spans, durations, and errors. Read-only. Use after `search_logs` surfaces a trace ID. Parameters: `trace_id` (32-character hex string)."
- `create_alert`: "Create a new alert rule in Lumatrace. **Writes data**: it creates a persistent rule that can notify people. Confirm the condition and recipients with the user before calling. Parameters: `name`, `condition` (query plus threshold), `window`, `notify` (channel or email)."

Also:
- Set MCP tool annotations: `readOnlyHint: true` on the two read tools; `destructiveHint` and `readOnlyHint: false` on `create_alert`. Reviewers and clients both use these.
- Add `title` and a strict `inputSchema` with `description` on every field.
- Add `outputSchema` or document the output shape.

## Change 2: scopes and data access

- Request the minimum scopes. If `mcp:connect` is the only one needed, request only that. Remove anything extra.
- Justify each scope in the submission in one line. A "required" scope with no in-Slack use needs a clear reason.
- Decide what Slack data, if any, flows to your server. Logs and traces may contain secrets and personal data. State whether Slackbot passes user messages or channel content to your tools.

## Change 3: auth and security (reviewers check these hardest)

- Use OAuth 2.1 with PKCE for the MCP server, per the MCP authorization spec. No static API keys pasted into Slack.
- Scope tokens per user and per workspace. A Slack user must see only their own Lumatrace tenant's data.
- Make `create_alert` safe: confirmation step, rate limit, audit log entry, and recipient allowlist so it can't be used to spam.
- Treat log content as untrusted input. Logs can carry prompt-injection text aimed at Slackbot. Strip or label it, and never let log content trigger `create_alert` on its own.
- Use HTTPS with a valid certificate, and handle token revocation and uninstall (delete tokens, stop access).
- Run an external security check or pen test summary if Slack asks. Have it ready.

## Change 4: listing and compliance assets

Prepare these for submission:
1. Privacy policy URL covering Slack data and log data handling.
2. Terms of service and support contact with a stated response time.
3. App description, icon, and screenshots showing the real flow in Slackbot.
4. Test workspace and test credentials with seeded sample logs and traces, so reviewers can run all three tools.
5. A short demo video of each tool end to end.
6. Data retention and deletion statement.
7. Uptime and error handling: clear errors on timeout, expired auth, empty results.

## Change 5: the name and branding

Follow Slack's naming rules. Don't imply Slack endorsement. Check whether "Lumatrace for Slack" or similar passes.

## Order of work

1. Confirm eligibility with Slack (see "Do first"). Half a day, mostly waiting.
2. Rewrite tool descriptions and annotations. About 2 hours.
3. Auth and `create_alert` safeguards. About 2 to 5 days, depending on your current auth.
4. Compliance assets and demo. About 2 days.
5. Submit. Add buffer for at least one rejection cycle.

## Next action

Search the Slack docs for `mcp:connect` and send Slack the eligibility question. If you paste the doc text or Slack's reply here, I'll tighten this plan against the actual rules.