# Skill plus CLI pairing

The Agent Skill teaches the workflow. The CLI executes it. This file covers the contract between them; the CLI's own design belongs to `samber/developer-platform-skills@cli-interface-design`, the skill's packaging and versioning to `samber/developer-platform-skills@agent-skill-offering`.

## Which path per class

- Coding agent with a shell: skill plus CLI. Skills cost about 100 tokens until loaded; a large MCP tool set costs thousands of tokens of definitions before the first call.
- Chat assistant without a shell, or access needing per-user remote auth: MCP.
- Customer fleet calling unattended: API plus SDKs; skill or MCP optional.
- Both shell and shell-less clients matter: ship both, from one source of truth (spec or command catalog), so they cannot disagree.

## Division of labor

| Lives in the skill | Lives in the CLI |
| --- | --- |
| when to use which command, in what order | the commands, flags and their reference (`--help`, `--help --json`) |
| checks between steps ("confirm the deploy is ready before linking a domain") | machine output on stdout, diagnostics on stderr |
| how to recover from named error codes | stable error codes and exit codes |
| which actions need the human | dry-run and confirm flags |
| login via the device grant | the login command and token storage |

Never copy flag lists into the skill. They drift on the next CLI release; point the agent at `--help --json` instead.

## CLI contract the skill depends on

- JSON on stdout only when `--json` (or agent mode) is set; banners, progress, warnings and update notices on stderr.
- Non-zero exit on failure, with a JSON error object carrying a stable `code` and `message`.
- No prompt when stdin is not a TTY; every prompt has a flag.
- Agent mode auto-enabled when an agent is detected, and always settable by flag.
- "Next step" hints as data fields, never as shell strings the agent executes verbatim.

## Incidents to design against

- Vercel's CLI auto-detected agent mode emitted JSON with suggested follow-up commands; it was rated a security vulnerability and fixed in a patch release. Treat any agent-facing "run this next" output as a command-injection surface: emit identifiers, not command lines built from untrusted data.
- The same CLI's agent mode ignored a scoping flag, so the agent acted on the wrong team.
- Cloudflare's Wrangler printed a skills install banner to stdout and broke every JSON parse until it moved to stderr off-TTY.

## Gates

- CI parses stdout of every `--json` command as JSON, in both normal and agent-detected mode.
- CI runs every documented skill workflow end to end against a sandbox account.
- The skill's version tracks the CLI's version (see `samber/developer-platform-skills@agent-skill-offering`).
