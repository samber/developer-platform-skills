# Agent integration plan for `drift`: how the skill and CLI split the work

I applied the `agent-integration-surfaces` skill and read its references on the skill-to-CLI pairing, identity and delegation, and measurement. I haven't run the interview, so the defaults below are assumptions for you to overturn.

## Verdict

- **CLI:** owns execution and the machine contract: the commands, their flags and reference, JSON on stdout, errors, and exit codes.
- **Skill:** owns judgment: when to use which command, in what order, what to check between steps, how to recover from errors, and what needs a human. It stays short.
- **MCP server:** serves the chat-assistant customers, because a skill can't reach a client with no shell.
- **Source of truth:** build the MCP server and the CLI's `--help --json` from one command catalog, so they can't drift apart.

## Your three current-state problems

| Today | Problem | Fix |
| --- | --- | --- |
| `drift --json` prints a "new version available" line before the JSON | It breaks every JSON parse. Cloudflare's Wrangler shipped the same bug with a skills install banner. | Send banners, progress, warnings and update notices to stderr. Suppress them entirely when `--json` is set, in agent mode, or when stdout isn't a TTY. |
| SKILL.md copies the flags for all 40 commands | The copy drifts on the next CLI release. It also costs tokens on every load for commands a given workflow never touches. | Delete it. The skill points the agent at `drift <cmd> --help --json`. It keeps only workflows, ordering, checks, and error-code recovery. |
| Agent mode prints `next: run drift domains add <name>`, with `<name>` taken from the project's display name in your API | The display name is untrusted user-generated content, placed in a command line. This is the pattern Vercel's CLI shipped and had rated a security vulnerability. | Emit data, never a shell string. Use `"next": {"command": "domains.add", "args": {"project_id": "prj_123"}}`. Use stable IDs, not display names, and mark the display name as untrusted if it appears at all. |

## Division of labor

| Skill (`drift-deploy`) | CLI (`drift`) |
| --- | --- |
| The handful of real workflows (deploy, link domain, roll back, inspect logs) and their order | All 40 commands, their flags, and `--help --json` as the only reference |
| Checks between steps, such as "confirm the deploy is ready before linking a domain" | JSON on stdout only when `--json` or agent mode is set; diagnostics on stderr |
| Recovery for named error codes | Non-zero exit on failure, plus a JSON error object with a stable `code` and `message` |
| Which actions need the human: production deploys, domain removal, anything that costs money | `--dry-run` and confirm flags; no prompt when stdin isn't a TTY, and every prompt has a flag |
| The login procedure via the device grant | The `login` command and token storage |
| Choosing the next step | Next-step hints as data fields only |

The skill's version should track the CLI's version.

## Execution path per class

- **Claude Code users (shell):** skill plus `--json` CLI. This path has low effort because the CLI already exists. A skill costs about 100 tokens until loaded, while a large MCP tool set costs thousands before the first call.
- **Chat assistant users (no shell):** an MCP server. You said these customers exist, which is the evidence that keeps MCP in the plan.
  - Confirm how many of them there are before sizing it. A stakeholder request alone doesn't justify a rung.
  - Scope the first release to read and low-risk operations. Gate destructive and money-moving tools behind write-safety: dry-run or a confirm token, never a prompt.
  - Use per-user remote auth. Publish RFC 9728 protected-resource metadata so clients can discover how to authenticate.
- **Customer fleets:** the API plus SDKs, if any exist. This is optional.

## Identity and delegation

- **Claude Code on a local CLI:** the agent inherits the human's per-install session. This is an accepted exception.
  - Bound the session with refresh-token rotation, an absolute lifetime, and the narrowest scopes the CLI needs.
  - Per-agent revocation isn't possible on this path, so list that as a known limit.
  - Tag calls by detecting the agent from env vars, such as `agent/claude-code` in the user-agent.
- **Login:** use the device grant (RFC 8628). The agent prints a code, the human approves in a browser, and no password reaches the agent.
- **Chat assistants over MCP:** each connection gets its own delegated, scoped, short-lived token. Record the actor chain (`act`) so logs show "agent X for user Y".
- **Production deploys, domain changes, and billing:** require approval through a channel the agent can't answer, such as email or a push notification. A confirm button in the same session doesn't count.

## Agent-safe checks specific to `drift`

- Deploy and domain mutations accept an idempotency key, because agents retry blindly.
- Errors carry a stable `code`, the failing field, and a next step as a field.
- Add a sandbox or test project so a skill workflow can run end to end without real side effects.
- Mark every user-controlled field in responses (project names, log lines) as untrusted content. Reading them is a prompt-injection path.

## Gates

1. CI parses stdout of every `--json` command as JSON, in both normal and agent-detected mode. That would have caught the update banner.
2. CI runs every documented skill workflow end to end against a sandbox account.
3. A test fails if any `next` hint contains a string built from API-supplied text.
4. A test confirms a scoping flag such as `--team` is honored in agent mode. Vercel's agent mode ignored it and acted on the wrong team.

## Order of work

1. **Quick fixes (days):** move the update notice to stderr, remove the flag copy from the skill, and change `next` to data fields. These ship the CLI contract that the skill and MCP both depend on.
2. **Measurement tags:** add the agent dimension to CLI and API requests, and baseline it before anything else ships. Env-var detection is a floor, so report it as "at least N%".
3. **Skill rewrite:** keep only the workflows and error recovery, and add the CI gates above.
4. **MCP server for chat assistants:** generate it from the same command catalog and start read-only.
5. **Agent-labelled credentials:** per-agent scoped tokens with a sponsoring human and per-agent revocation.

## Assumptions to overturn

I defaulted the unanswered interview questions to no hard date, a standing agent channel, and one engineer for a quarter. These would change the plan:

- **Hard date:** it cuts the plan to the quick fixes, measurement, and the skill rewrite.
- **Money-moving or destructive operations:** these promote the credentials and approval gate above MCP.
- **Edge blocks:** if CDN bot rules or CAPTCHAs sit in front of the API, run the reachability gate first, since a block fails every later step silently.

Two questions would sharpen this. How many customers use the chat assistants, and do any commands move money or delete production data?