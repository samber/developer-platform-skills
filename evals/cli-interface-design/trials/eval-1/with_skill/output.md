# Kestrelhost CLI design spec (v0.1)

I read the `cli-interface-design` skill and its five references and followed them. I couldn't ask you the clarifying questions, so each unanswered one is an assumption below. Correct any that are wrong, because several change the design.

## Assumptions

| Question | Answer or assumption | What it changes |
|---|---|---|
| 1. Audiences | Stated: developers at a terminal and GitHub Actions are the main audiences, with Cursor and Claude Code users growing. **Assumed:** CI breaks the business first, because a hung or ambiguous deploy step blocks customers' releases. | Machine output, exit codes and non-interactive safety come before polish. |
| 2. API shape | Stated: 160 endpoints, 28 resources, OpenAPI YAML edited by hand after each release. **Assumed:** the YAML is not checked against the running backend in CI, and resources also have action endpoints such as restart and rollback. | Blocks the generated layer (see "Answer to the requester"). |
| 3. Multi-call and local jobs | Stated: deploy-and-know-when-live, log tailing, and webhook forwarding to localhost. **Assumed:** the API has no log-stream or webhook-event-stream endpoint yet, but does have a deployment status. | Three API-side dependencies, each blocking one command (see "API-side dependencies"). |
| 4. Auth | **Assumed:** API keys only, no OAuth server, no scoped or expiring keys, no test mode. | Login is key-based. Safe agent tokens depend on API work. |
| 5. Async, destructive, idempotency | **Assumed:** deploys are async. Deleting services, volumes, domains and secrets is irreversible. No idempotency keys exist. | Retries after a send are unsafe until the API adds keys, so the CLI returns exit 6 instead of retrying. |
| 6. Existing CLI | None ships, so there are no scripts to break yet. | The contract can be set freely now, and then it freezes. |
| 7. Location | **Assumed:** a meaningful EU share and some enterprise buyers. | No client telemetry in v1. |
| 8. Timing and effort | Stated: 8 weeks, two engineers. **Assumed:** a compounding product surface, not a one-off launch. | Keeps the default layer rung and a hard cut line. |

## Answer to the requester

**Every endpoint is reachable on day one, so coverage is 100%, through `kestrel api <method> <path>`.** It inherits auth, pagination, `--json`, retries and the confirmation guard. The 12 or so curated commands carry the jobs customers asked for (deploy, logs, webhooks).

A generated command-per-endpoint tree does not give "never drifts" while the YAML is edited by hand. The CLI would be exactly as accurate as the YAML, and it would freeze every drift into a public contract that can only change on a major version. `api` talks to the real backend, so it cannot drift at all.

A pure mirror also cannot do the three jobs support named. Log tailing, webhook forwarding to localhost and deploy-and-wait each need more than one call, or a local process, so a mirror would drop the reasons to install the CLI.

**What promotes a generated layer later** (all must hold):
1. The backend team gates the OpenAPI file in CI, either by generating it from code or by running contract tests of the live API against it.
2. `api` usage shows sustained demand for per-endpoint commands.
3. The 1.x curated surface is stable.

Item 1 is the real fix for drift. Put it on the backend team's roadmap now. It costs them little and it is the precondition for the generated layer.

## Audiences and jobs

| Job | Audiences | API calls involved | Local-only part |
|---|---|---|---|
| Authenticate | human, CI, agent | key validation (`GET /me` or similar) | credential store |
| Deploy and know it is live | human, CI, agent | create deployment, poll deployment status | none |
| Resume or check an operation | CI, agent | get operation | none |
| Tail service logs | human mostly. Agents for debugging. CI rarely. | log stream endpoint | stream reconnect, bounded duration |
| Forward webhook events to localhost | human only | event stream (new) | HTTP POST to `localhost` |
| Inspect services and deployments | human, agent | list, get | none |
| Anything else | CI, agent | any endpoint | none |

## Command layers

- **Chosen rung:** curated workflow commands plus the raw `api` escape hatch.
  - What moved it: the multi-call and local jobs (question 3), the 8-week, two-engineer limit, and the hand-maintained spec.
- **Escape hatch:** `kestrel api <method> <path> [-d @file|-|k=v] [--paginate] [--idempotency-key K]`.
  - Inherits: auth, `--profile`, `--json` (always on, since the body is JSON), `--limit`/`--all`, retries, `--debug`, `--dry-run`, and the severity table (below), which is keyed by method and path.
  - Raw JSON input (`-d @file`, `-d -`) also serves agents.
- **Starved option:** a generated `kestrel <resource> <verb>` layer under the curated one.
  - Promotion trigger: the three conditions in "Answer to the requester".
  - Until then, `api` plus the 160-endpoint OpenAPI file's own docs are the reference.

## Grammar

- **Order:** `noun verb`, plural nouns (`gh`/`stripe` style). Verbs are uniform across resources and the resource set is closed, so `verb noun` would give no gain.
- **Verb set:** `list`, `get`, `create`, `update`, `delete`. Add `tail`, `listen`, `wait` and `rollback` only where a job needs them. Never use `update` and `upgrade` for different things.
- **Two job-shaped top-level verbs:** `deploy` (shorthand for `deployments create` plus waiting) and `wait`. They are named after jobs, not resources, because the job is what people search for.
- **No prefix abbreviations and no default subcommand.** Each would block future commands.
- **Flags over positionals** beyond one target. `-` means stdin and `@file` means a payload file.

Command tree (v1, top two levels):

```
kestrel login | logout | auth status
kestrel deploy [SERVICE]
kestrel wait OPERATION_ID
kestrel services     list | get
kestrel deployments  list | get | rollback
kestrel logs         tail | list
kestrel webhooks     listen
kestrel api          METHOD PATH
kestrel schema                      # command tree + --json schemas as JSON
kestrel completion   bash|zsh|fish|powershell
kestrel version
```

**Reserved for plugins (not implemented in v1):**
- the `plugin` and `plugins` top-level names;
- the executable convention `kestrel-<name>` on `PATH`, discovered kubectl-style;
- the rule that built-in commands can never be shadowed.

Plugins are not a day-one goal, but scripts wrapping `kestrel --json` with a frozen exit-code contract already behave like plugins. A plugin mechanism comes later (see "Open items"), and it must not hand the stored token to plugins by default.

## Contract surface

- **Frozen:**
  - command and subcommand names, flag names and meanings;
  - env var names (`KESTREL_*`) and config keys;
  - `--json` shapes and field names, and the `--format ndjson` line types;
  - exit codes, and which stream carries what.
- **Unstable:** human tables, wording, colors and spinners. State this in the docs so scripts parse `--json` and never the table.
- **Rules:**
  - Adding a field is safe. Renaming, retyping or removing one is breaking.
  - Bare `--json` returns a documented default field set. `--json all` returns full objects. `--json id,status` returns only named fields.
  - Deprecation: a stderr warning naming the replacement, an alias for 12 months or 2 minor releases (whichever is longer), and removal only in a major.
- **Enforcement:**
  - A JSON Schema per `--json` command, published.
  - Golden-output contract tests against a staging Kestrelhost environment, run in CI.
  - These tests also catch API-spec drift for the curated commands.

## Configuration

- **Precedence:** flag > env var > project config (`kestrel.toml` in the repo, no secrets) > user config > default.
- **Env prefix:** `KESTREL_` (`KESTREL_TOKEN`, `KESTREL_PROFILE`, `KESTREL_API_URL`, `KESTREL_NO_INPUT`, `KESTREL_NO_UPDATE_CHECK`).
- **Token override notice:** an explicit token (flag or env) beats a stored profile, with a stderr notice when it overrides a logged-in account.
- **Profiles:** named profiles for accounts, teams and base URLs. A project directory binds to a profile by name through `kestrel.toml`.
- **Config location:** XDG directories (`%APPDATA%` on Windows). Use a lock file on writes, because agents run commands in parallel.
- **Network:** honor `HTTPS_PROXY`, `NO_PROXY` and a custom CA bundle (`KESTREL_CA_BUNDLE`).
- **Secrets:** never a flag-only value. Accept them from env, a file, or stdin.

## Output and exit codes

- **`--json` coverage:** every command that returns data or mutates state, including `deploy`, `wait` and `rollback`.
  - Exceptions: `logs tail` and `webhooks listen`, which are streams. They use `--format ndjson` instead, and passing `--json` fails with usage error 2 naming `--format ndjson`.
- **Streams:**
  - Human mode: result on stdout. Progress, warnings, deprecation notices and errors on stderr.
  - `--json` mode: exactly one JSON document on stdout, either the success shape or `{"error": {...}}`. Stderr stays free text.
- **List envelope (from v1):**
  ```json
  {"data": [{"id": "svc_1", "name": "api", "status": "live"}], "has_more": true, "next_cursor": "c_42"}
  ```
- **Async mutation shape (identical whether it waited or not):**
  ```json
  {"operation_id": "op_9", "state": "live", "result": {"deployment_id": "dep_3", "url": "https://api-x.example.app"}}
  ```
- **Error object:** `code`, `message`, `request_id`, `operation_id` (or `null`), `retry` (`safe`, `resume` or `never`), `docs_url`, `hint`.
- **TTY:** color, spinners and prompts only on a terminal. Honor `NO_COLOR`, `--no-color` and `TERM=dumb`. Never use a pager by default.

| Code | Meaning | Caller action |
|---|---|---|
| 0 | Success, including an idempotent no-op. A deploy that reached `live` counts. | continue |
| 1 | Failure not covered below. This includes a deployment that ended `failed` (error code `deployment_failed`, with the reason). | stop, read the error |
| 2 | Usage error: unknown flag, missing argument, or a missing value in non-interactive mode. | fix the invocation, never retry |
| 3 | Not found | branch |
| 4 | Authentication required or token expired | re-authenticate |
| 5 | Safe to rerun: rate limited (429), 503 with `Retry-After`, or a DNS, connect or TLS failure before send. | rerun with backoff |
| 6 | Outcome unknown: wait timeout, or connection lost after sending a non-idempotent call. | `kestrel wait <operation-id>` or `get`. Never rerun a create without your own `--idempotency-key`. |
| 7 | Partial failure in a bulk operation | read per-item results |
| 130 / 143 | Interrupted (Ctrl-C / SIGTERM) while waiting. The CLI detached and printed the resume command. | resume or stop |

- Streams (`logs tail`, `webhooks listen`) exit 0 on Ctrl-C, because stopping is their intended end.
- Avoid BSD sysexits and the shell-reserved range above 125.
- Each code gets an automated test.

## Auth

| Context | Flow | Token type, scope, lifetime | Available now? |
|---|---|---|---|
| Desktop | `kestrel login` opens the dashboard page that creates an API key. The user pastes it, or pipes it with `--with-token`. | API key, unscoped (assumed), no expiry (assumed) | Yes |
| SSH, containers, dev boxes | `kestrel login --with-token < key` | same | Yes |
| CI | `KESTREL_TOKEN` env var, from the CI secret store | dedicated key per pipeline | Yes. Scoped, expiring keys are an API dependency. |
| Agents | `KESTREL_TOKEN` with a read-only, narrowly scoped key | read-only scope | **Blocked on scoped keys** |

- **Storage:** OS credential store. If none exists, warn on stderr before writing a plaintext file with owner-only permissions.
- **Commands:** `auth status` (identity, which source won, expiry, mode) and `logout`.
- **No token-printing command.** Malware has harvested tokens through exactly such a command (s1ngularity, August 2025).
- **Redaction:** secrets are redacted from all output, including `--debug` traces.
- **Deferred:** OAuth device and PKCE flows, until an authorization server exists.

## Lists and long-running operations

- **List limit:** default `--limit 30`. It fits one screen for a human and keeps an agent's context small. `--all` fetches everything. `has_more` and `next_cursor` are always in the envelope. Pager flags are separate from pagination flags.
- **Waiting:** `deploy` and other async mutations wait by default, in every context.
  - Progress goes to stderr.
  - Default `--wait-timeout 10m`: an image pull plus health checks usually fits, and it stays below typical CI job caps. On timeout the CLI exits 6 with the operation ID.
  - `--no-wait` returns the operation ID immediately.
  - `kestrel wait <operation-id>` resumes.
- **Ctrl-C or SIGTERM during a wait:** detach, print the operation ID and the resume command, exit 130 or 143. Cancelling server-side is a separate explicit command, `deployments cancel`, in a later release.
- **"Live" is defined once:** the new revision passes health checks and receives 100% of traffic. Terminal states are `live`, `failed`, `rolled_back` and `canceled`. On `failed`, the CLI prints the failure reason and the last 20 log lines to stderr.
- **Retries:** transient failures retry up to 3 times with exponential backoff (1s, 2s, 4s, capped at 8s), honoring `Retry-After`.
- **Idempotency:** one key per invocation, reused across retries, and `--idempotency-key` is accepted.
  - Until the API supports keys, the CLI never retries a POST after the request was sent. It exits 6.

## Logs and webhook forwarding (the two local jobs)

**`kestrel logs tail SERVICE`**
- Flags: `--since 5m`, `--instance`, `--level`, `--format ndjson`.
- It reconnects on a dropped stream, resuming from a cursor, with bounded backoff.
- NDJSON line types: `log`, `status`, `error`. A fatal error is the last line, before the non-zero exit.
- **Off a terminal, the default max duration is 5 minutes.** A stderr notice names `--duration` and `--max-lines`, and `--duration 0` means unbounded. Reason: an agent or CI step running an unbounded tail would hang its shell.
- `logs list` returns bounded history in the normal `--json` envelope.

**`kestrel webhooks listen --forward-to http://localhost:3000/hooks`**
- The CLI opens an outbound stream to a Kestrelhost relay and POSTs each event to the local target. It prints the status code and latency per event, and reports delivery results back for the dashboard.
- **Loopback only by default.** A non-loopback target needs `--allow-remote-target`. This prevents a stolen session from exfiltrating events.
- `--events deployment.live,...` filters. Events are forwarded with the original signature headers.
- The signing secret is printed only with `--print-secret`.
- Event payloads are untrusted input and are never interpreted by the CLI.
- Replay and trigger commands come later.

## Errors and help

- **Error rewrite:** every error states what failed, why, and the next command. The API error code and request ID are always kept.
  - Example: `Service "api" not found. Run: kestrel services list` (code `service_not_found`, request `req_8f2a`).
- **Typos:** suggest the closest command or flag, never auto-run it.
- **Unknown flags:** rejected by name before any API call, listing the valid flags.
- **Help:** `kestrel`, `kestrel help <cmd>`, `<cmd> --help` and `-h` all work. Each command's help leads with 2 to 3 examples, then flags with defaults, then a docs link.
- **Help topics:** `exit-codes`, `output`, `environment`, `contract`.
- **Completion:** bash, zsh, fish and PowerShell from the first release.
- **Debug:** `--debug` prints a redacted HTTP trace to stderr.

## Severity table

One table, read by the curated commands and by `api`, keyed by command and by method plus path template. Anything not listed falls to a fail-closed default: unknown `DELETE` is severe, unknown `POST`/`PUT`/`PATCH` is moderate, `GET` is mild.

| Command or method + path | Grade | Terminal behavior | Non-interactive flag |
|---|---|---|---|
| `deploy`, `GET *`, `webhooks listen` | mild | none | none |
| `deployments rollback`, `POST /services/{id}/restart` | moderate | confirm | `--yes` |
| `PATCH /services/{id}` (config or env change) | moderate | confirm | `--yes` |
| `DELETE /webhooks/{id}` | moderate | confirm | `--yes` |
| `DELETE /services/{id}` | severe | type the service name | `--confirm=<name>` |
| `DELETE /volumes/{id}` (data loss) | severe | type the volume name | `--confirm=<name>` |
| `DELETE /domains/{id}`, `DELETE /secrets/{id}` | severe | type the name | `--confirm=<name>` |
| Revoking an API key or deleting a project or team | severe | type the name | `--confirm=<name>` |
| Bulk delete | severe | type the count | `--confirm-count=<n>` |

- `--yes` never skips a severe confirmation.
- A CI check requires that every `DELETE` operation in the OpenAPI file has an explicit grade. A new endpoint that ships ungraded fails the build. This is the one place the hand-maintained spec is useful, as a checklist.
- When stdin is not a terminal, the CLI never prompts. It fails immediately and names the missing flag. `--no-input` forces that behavior on a terminal too.
- `--dry-run` on mutating commands where the API can validate without committing (API dependency).
- Update checks, first-run notices and banners stay silent off a terminal.

## Agent readiness

- **Self-description:** `kestrel schema` prints the command tree, flags and `--json` schemas as JSON.
- **Bounded output:** small default fields and limits, totals, explicit empty results ("0 services found"), and truncation markers naming the flag that shows more.
- **Input hardening:** validate IDs, paths and payloads as untrusted. A `../../` in a service name must produce a validation error.
- **What bounds an agent is its token, not a confirmation prompt.** An agent can read the name it needs from its own output. Hand agents a read-only, scoped key, ideally limited to a staging project.
  - Until scoped keys exist, recommend a separate team or project for agent use. Say plainly in the docs that the CLI cannot yet restrict an agent.
- Shipping an Agent Skill with the CLI belongs to `agent-skill-offering`. The GitHub Action wrapper belongs to `github-action-offering`, and its contract inherits this CLI's flags and exit codes.

## Versioning and lifecycle

- **CLI SemVer,** separate from the API version. Each CLI release pins an API version, with an `--api-version` override.
- **Deprecation:** the window and alias policy are in "Contract surface".
- **Update check:** at most daily, only on a terminal, never in CI, disabled by `KESTREL_NO_UPDATE_CHECK`. Never self-update without consent.
- **Telemetry:** none in client v1.
  - Measure adoption server-side instead: send a `User-Agent` of `kestrel/<version>` plus a command header, and compare CLI share of API traffic and `api` usage per endpoint in the server logs.
  - Revisit in a 2.0 with advance notice. Opt-in is the default for the assumed EU and enterprise audience. Turning collection on in a minor release is ruled out.
- **Distribution:** binaries, Homebrew and signing belong to `sdk-package-publishing`.

## API-side dependencies

| Need | Owner | Blocks which command |
|---|---|---|
| Deployment status with terminal states (`live`, `failed`, `rolled_back`, `canceled`) and a failure reason | Backend | `deploy`, `wait` |
| Log stream endpoint (SSE or WebSocket) with resumable cursor | Backend | `logs tail` |
| Webhook event stream or relay for developers | Backend | `webhooks listen` |
| Idempotency keys on create endpoints | Backend | safe retries, `deploy` |
| Scoped, expiring API keys | Backend | CI hygiene, agent tokens |
| CI gate on the OpenAPI file (generate from code or contract-test it) | Backend | promoting the generated layer, severity-table check |
| `--dry-run` validation on mutating endpoints | Backend | `--dry-run` |
| Stable error codes with request IDs | Backend | error rewrite |

## Release cut line

| Command or capability | v1 (week 8) | Later | Reason |
|---|---|---|---|
| `login`, `logout`, `auth status` | ✅ | | everything needs it |
| `api` with the severity table | ✅ | | gives 100% reach and guards deletes |
| `deploy`, `wait`, `deployments get/list` | ✅ | | top support request |
| `logs tail`, `logs list` | ✅ | | top support request |
| `webhooks listen` | ✅ | | top support request |
| `services list/get`, `deployments rollback` | ✅ | | small, high-use |
| `schema`, `completion`, `--json` on all commands | ✅ | | agent and CI readiness |
| Other curated resource commands | | ✅ | add only where `api` usage is busy |
| Generated resource layer | | ✅ | needs CI-gated spec |
| `webhooks trigger/replay`, `deployments cancel` | | ✅ | not asked for yet |
| Plugin mechanism | | ✅ | names reserved now |
| OAuth login, client telemetry | | ✅ | need an auth server, a 2.0 and a notice |

Suggested plan for two engineers:
- Weeks 1-2: contract, skeleton, auth, `api`, exit codes.
- Weeks 2-4: `deploy` and `wait`.
- Weeks 3-5: `logs tail`.
- Weeks 5-7: `webhooks listen`.
- Week 7: contract tests, help, completion.
- Week 8: release and docs.

**Risk:** all three jobs need new API endpoints. If a dependency is not ready by week 3 for its command, cut that command to v1.1 rather than ship a polling hack that becomes a frozen contract.

## Open items

| Decision | Owner | Due |
|---|---|---|
| Confirm the answers to questions 2-5 and 7 (spec accuracy, auth, idempotency, EU share) | PM | before week 1 |
| Does `deploy` take an image, or build from source? This spec assumes an image or the current config. | PM + backend | before week 2 |
| Binary name: `kestrel` may collide with the ASP.NET web server name in search. Consider `kh`. | PM | before week 1 |
| Commit dates for the backend dependencies above, especially log and event streams | Backend lead | week 1 |
| CI gate or generation for the OpenAPI file | Backend lead | roadmap, before the 1.x promotion review |
| Plugin mechanism design and token-handoff policy | PM + engineering | after v1 |
| Client telemetry decision for 2.0 | PM + legal | after v1 |

## Gates

These are acceptance criteria for the build. None has been tested yet.

- [ ] Contract coverage: every command that returns data or mutates state has `--json` (except the two streams, with `--format ndjson`). The frozen list and a JSON Schema per command are published.
- [ ] Non-interactive run: every command with stdin closed and stdout piped completes, or fails fast naming the missing flag. Every wait and stream is bounded.
- [ ] Exit-code table tested: one automated test per code.
- [ ] Severe-action guard: curated commands and `api` both read the severity table. No blanket `--yes`.
- [ ] Secret hygiene: no secret accepted only as a flag. None printed in default, verbose or debug output.