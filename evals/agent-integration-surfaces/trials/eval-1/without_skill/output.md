**Do first (15 min):** find out what blocks agents. Run these against your signup URL and a dashboard URL.

1. `curl -sI -A "ClaudeBot" <url>`
2. `curl -sI <url>` with the default curl UA
3. Open signup in a normal browser and note where the CAPTCHA fires.

Then check CDN logs for hits on the "Block AI bots" rule. I can't see your config, so everything below about your setup rests on what you told me.

## What is wrong in the current story

- **robots.txt blocks nothing.** It is a request that compliant crawlers honor. Claude Code and Cursor run on the dev's machine and act on the dev's behalf with curl, a browser, or the CLI. They don't depend on it.
- **The CDN preset only catches bots that identify themselves.** It does not stop an agent driving a browser or curl from a dev's laptop. Nobody should tell the CEO "every AI agent is kept out of the dashboard."
- **The dashboard is protected by auth, not by bot rules.** Verify login, MFA, and rate limits are what guard it.
- **The CAPTCHA is the real signup blocker.** It is app-level, separate from the preset. Agents shouldn't pass it. A human should.
- **The `GPTBot`, `ClaudeBot` and `ChatGPT-User` rules likely hurt you.** `ChatGPT-User` is a user-triggered fetch. If it can't read your docs, devs asking an assistant how to integrate get worse answers. The list also misses other agent UAs (for example `Claude-User`, `OAI-SearchBot`, `PerplexityBot`).
- **Fix:** exempt docs, `openapi.json`, and `llms.txt` from the preset. Keep it on signup, dashboard, and API auth. This is a 1-day change for security and the platform team.

## Decisions to lock in week 1

1. **Signup stays human.** Keep the CAPTCHA. Add a device-authorization login (OAuth device grant, RFC 8628) to `pb login`:
   - The CLI prints a code.
   - The human opens the browser, passes the CAPTCHA once, and approves.
   - The CLI gets a scoped token.
   - An agent can then drive everything after that.
2. **No live secret key in an env var.** Reject the engineer's proposal:
   - A live key is full-power, unscoped, and revocable only by rotation.
   - It leaks into transcripts, logs, shell history, and child processes.
   - Any prompt-injected text the agent reads can exfiltrate it.
   - It can issue refunds.
3. **Credential model:**
   - OAuth 2.1 with scopes for the remote MCP server.
   - Short-lived tokens.
   - Test mode by default.
   - Scoped, read-only restricted keys for headless CI.
   - Every token is tagged with an agent or client ID, so the audit log shows who did what.
4. **Refunds:** not a plain tool in v1. Two options, ranked:
   - **Recommended:** the tool creates a pending refund request. A human approves it in the dashboard or via MCP elicitation.
   - **Fallback:** refunds are off by default, behind a `refunds:write` scope plus per-token caps and idempotency keys.
   - Tool annotations like `destructiveHint` are hints, not security. Enforce everything server-side.
5. **Prompt injection is a design input.** Invoice memos, customer names, and line items are untrusted text. An agent that reads them and can also move money is the dangerous mix. Keep the refund path gated, never let tool output approve actions, and cap amounts.

## Build plan (6 weeks)

**Week 1: decisions and quick wins**
- Run the curl tests.
- Exempt docs from the preset.
- Write the scope list and a one-page threat model.
- Sign off on the credential model above.

**Week 2: auth**
- Device-flow login for `pb`.
- OAuth with scopes for the MCP server.
- Test-mode default.
- Audit log with client ID.

**Week 3: read-only MCP**
- About 8 to 12 task-shaped tools, not one tool per endpoint. Examples: find invoice, customer summary, list overdue, search docs.
- Pagination, structured output, and error messages that tell the agent what to do next.
- Dogfood internally.

**Week 4: writes**
- Create and update draft invoices.
- Refund-request flow with human approval.
- Rate limits and idempotency keys.
- Fix the `pb` commands that still lack `--json`. Add `--no-input` and stable exit codes.

**Week 5: hardening**
- Red-team prompt injection through invoice fields.
- Build an agent eval of 15 to 20 real tasks and run it on Claude Code and Cursor.
- Write agent docs: `llms.txt`, OpenAPI, and an `AGENTS.md` snippet.
- Security review.

**Week 6: freeze and rehearse**
- Freeze code by day 3.
- The demo runs on a sandbox account in test mode, never a real prod-data account.
- Record a backup demo.
- Publish to the MCP registry.

**Summit scope:** read tools plus draft writes plus the gated refund request. If week 4 slips, cut refunds first, not security.

## About the MCP server and the CLI

- `pb --json` is a valid agent path today. Claude Code uses CLIs well.
- Wrap the API (via your OpenAPI spec) for the remote server. Don't wrap `pb`, since a remote server can't shell out to a user's machine and that would add a second auth layer.
- A local stdio MCP over `pb` is a fast week-2 prototype for internal demos only.

## Questions for you (answer when you can)

1. Does the API support scoped keys, OAuth, or neither today? This sets week 2's size.
2. Must refunds be in the summit demo, or is "agent drafts, human approves" enough?
3. Who owns the CDN config, and can you get the docs exemption approved this week?

**Next action:** run the three curl tests and paste the status codes here. I'll fold them into the threat model.