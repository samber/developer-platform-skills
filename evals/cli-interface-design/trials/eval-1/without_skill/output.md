# Kestrelhost CLI: Design Spec (v0.1, draft for review)

## 1. Decision summary

- **Ship a hybrid CLI, not 160 flat commands.** A generated layer covers every endpoint. A small hand-built layer covers deploy, logs and webhook forwarding, which are the three things customers ask for.
- **Product's 100% coverage and no-drift goals are met, but by the generated layer plus a `kestrel api` escape hatch.** Coverage was never the problem. Discoverability and workflows are.
- **Plugins are not in v1.** v1 ships one cheap extension seam (external executables on `PATH`, labelled experimental) and an output contract that plugins and agents can rely on.
- **The three workflows depend on backend capabilities that may not exist.** These are a deploy status resource, a log stream and a webhook event tap. §10 lists them as gating questions to settle in week 1.

### Why not "one command per endpoint" alone

- A raw mapping gives the user `kestrel deployments create`, then a separate poll of `kestrel deployments get` in a loop.
- It cannot tell a customer "your deploy is live". CI users need that most, since exit 0 has to mean live.
- Log tailing and webhook forwarding are streaming and local-listener behaviors. They are not CRUD, and no OpenAPI file describes them.
- 160 commands across 28 resources makes `--help` unusable as a map of the product.

Generation stays the right foundation. It just can't be the whole product.

## 2. Users and priorities

| Audience | Needs | Design consequence |
|---|---|---|
| Developer at a terminal | Fast deploy feedback, readable output, discoverable help | Human output when stdout is a TTY, curated help |
| GitHub Actions and other CI | Deterministic exit codes, no prompts, machine output | `KESTREL_TOKEN`, `--no-input`, stable JSON, `--wait` semantics |
| Cursor and Claude Code users (growing) | Parseable output, self-description, safe non-interactive use | JSON everywhere, `kestrel schema`, structured errors, `--dry-run` |
| Plugin authors (someday) | A stable surface to build on | Output and exit-code contract now, plugin protocol later |

CI and agent users need the same things: no TTY assumptions, structured output and explicit failure. We build for both with one set of rules (§6).

## 3. Command architecture

Three layers, resolved in this order. A hand-written command wins over a generated one at the same path.

```
kestrel
├── Core workflows (hand-built)
│   ├── login / logout / whoami
│   ├── deploy
│   ├── logs
│   └── webhooks listen
├── Resources (generated, 28 groups)
│   └── kestrel <resource> <verb> [args] [flags]
│       e.g. kestrel services list, kestrel domains create
├── kestrel api <METHOD> <path>   (raw escape hatch)
└── Utility: schema, completion, version, update
```

### 3.1 Generated layer

- **Naming:** `kestrel <resource> <verb>`. The resource is the plural noun taken from the OpenAPI tag. Verbs are the standard set `list|get|create|update|delete`, derived from method plus path shape.
- **Non-CRUD operations** (e.g. `POST /services/{id}/restart`) become `kestrel services restart <id>`. The verb comes from `operationId` or the path tail.
- **Overrides:** a small checked-in `cli-overrides.yaml` renames commands, hides operations (internal or deprecated), sets aliases, and marks destructive operations. It is the only place a human edits generated behavior.
- **Flags:** each path parameter is a positional argument. Each query parameter is a flag. Request bodies accept flags for top-level scalar fields and `--body @file.json` or `--body -` for everything else.
- **Help:** `kestrel --help` lists Core commands first, then Resources, in alphabetical order, with one line each. Per-operation help comes from the OpenAPI `summary` and `description`.
- **Destructive operations** (all `DELETE`, plus those flagged in overrides) prompt on a TTY and fail on non-TTY unless `--yes` is passed.
- **Idempotency:** every `POST` sends an `Idempotency-Key` if the API supports it. See §10 question 5.

### 3.2 Drift protection ("never drifts")

The CLI follows the YAML, so the YAML must follow the API. That is the real drift risk, and it sits outside the CLI.

1. **CI regenerates on every spec change.** The generated code is committed so spec changes appear as a reviewable diff. CI fails if `make generate` produces a diff.
2. **Spec lint in CI** (Spectral or equivalent), requiring `operationId`, `summary` and tags on every operation. A missing one fails the build, not the user's `--help`.
3. **Contract test against staging.** Run a spec-driven fuzzer (e.g. Schemathesis) from the backend release pipeline. This catches hand-edited YAML that no longer matches reality.
4. **Hand-built commands are the other drift surface.** Each one declares the operations it uses. CI fails if the new spec removes or changes one of them.
5. **Release rule:** the backend release pipeline triggers a CLI patch release when the spec changes. No human remembers to do it.

If the backend team cannot commit to step 3 (or to generating the spec from code), "never drifts" is not a promise we can make. Say so to Product now.

### 3.3 The `kestrel api` escape hatch

- `kestrel api GET /v1/services --query status=running` and `kestrel api POST /v1/domains --body @d.json`.
- Handles auth, base URL, pagination (`--paginate`) and output formatting.
- Covers any endpoint that is new, hidden or badly generated, so coverage holds even when generation fails on one operation.
- It costs about two days and makes the 100% claim true by construction.

## 4. Core workflows

### 4.1 `kestrel deploy`

Goal: after the command returns, the user knows whether the new version is live.

```
kestrel deploy [--service <name>] [--image <ref>] [--wait=true] [--timeout 10m]
```

- **Resolve the target** from flags, then from `kestrel.yaml` in the working directory, then fail with a hint. Never guess in non-TTY mode.
- **Create the deployment**, then stream status transitions to stderr.
- **Define "live" exactly.** Live means the new revision passes health checks and receives traffic. Not merely that the container started. The CLI reports the phase it is waiting on.
- **`--wait` is the default.** `--wait=false` returns the deployment ID immediately for users who poll themselves.
- **Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Live and healthy |
| 1 | Generic or unexpected error |
| 2 | Usage error |
| 3 | Auth error |
| 4 | Deploy failed (build, start or health check). The CLI prints the failing phase and the last 20 log lines |
| 5 | Timed out before live. The deployment keeps running; the CLI prints how to check it |
| 6 | Rolled back automatically (only if the platform does this) |

- **Machine output:** `--output json` prints one final object `{deployment_id, service, revision, status, url, duration_s}`. Progress goes to stderr only.
- **Interrupt:** Ctrl-C stops waiting, not the deployment. The CLI prints the ID and the command to resume with `kestrel deploy status <id>`.

### 4.2 `kestrel logs`

```
kestrel logs <service> [--follow] [--since 15m] [--lines 100] [--instance <id>] [--filter <text>] [--output json]
```

- Default is the last 100 lines and exit. `--follow` streams until interrupted.
- Reconnects automatically after a dropped stream. It resumes from the last timestamp and prints a single "reconnected" notice to stderr, with no duplicate lines.
- JSON output is one object per line (NDJSON) with `timestamp`, `instance`, `stream` (stdout|stderr) and `message`.
- Colors only on a TTY. `NO_COLOR` is honored.
- During a deploy, `kestrel logs --deployment <id>` shows build and rollout logs. This lets `deploy` failures link straight to the evidence.

### 4.3 `kestrel webhooks listen`

```
kestrel webhooks listen --forward-to http://localhost:3000/hooks [--events service.deployed,...] [--service <name>]
```

- Opens an outbound stream from Kestrelhost to the CLI and replays matching events as HTTP `POST`s to the local URL. It needs no inbound port and no tunnel.
- Prints a one-line summary per event: time, type, local response status, latency.
- **Signing:** events are signed with a development-only secret that the CLI prints once at startup. The user's handler can verify them the same way it verifies production webhooks.
- Failures from the local server show the status and the first 200 bytes of the response body. The CLI does not retry in v1. A `kestrel webhooks replay <event-id>` command (generated or hand-built) re-sends one event.
- Scoped to the authenticated project. Streams are short-lived tokens and are not stored.

## 5. Authentication and configuration

- `kestrel login` uses a browser-based device flow. On a headless machine it prints a URL and a code.
- **CI:** `KESTREL_TOKEN` (project-scoped API token). If set, it overrides stored credentials. No prompts, ever, when it is set or when stdin is not a TTY.
- **Precedence:** flag, then env var, then `kestrel.yaml`, then user config.
- **Storage:** OS keychain where available, otherwise a `0600` file under the XDG config directory. Tokens are never printed. `--debug` redacts them.
- **Profiles:** `--profile` or `KESTREL_PROFILE` for multiple accounts. Base URL is overridable with `KESTREL_API_URL` for staging.
- **`whoami`** prints the account, project and token scopes. It is the first command in every support thread.

## 6. Output and agent contract (applies to every command)

This is the contract CI, agents and future plugins depend on. Breaking it needs a major version.

1. **stdout is data, stderr is messages.** Progress, hints and warnings never go to stdout.
2. **Format is chosen by TTY.** A TTY gets tables and colors. A pipe gets JSON. `--output json|table|yaml|text` forces one.
3. **JSON is stable.** Field names follow the API response. We add fields, never rename or remove within a major version. Lists are arrays at the top level or under a documented `items` key (decide once and apply everywhere).
4. **Errors are structured.** In JSON mode, errors go to stderr as `{"error":{"code":"...","message":"...","hint":"...","request_id":"..."}}`. The `request_id` is always included, so support can find the request.
5. **Exit codes are documented** (§4.1 table) and shared by every command.
6. **`--no-input`** disables all prompts and fails with a clear error where input would be needed. It is implied by non-TTY stdin.
7. **`--dry-run`** is available on every mutating command. It prints the request that would be sent and exits 0 without sending it.
8. **`kestrel schema <command>`** prints the command's flags, arguments and response shape as JSON Schema. Agents can then discover the CLI without scraping `--help`.
9. **Pagination:** `--paginate` follows all pages. Without it, the CLI prints the first page and a warning on stderr when more exist. It never silently truncates.
10. **Rate limits:** the CLI honors `429` and `Retry-After`, with bounded retries, and reports the wait on stderr.
11. **No telemetry in v1** beyond a `User-Agent` of `kestrel-cli/<version>`. Any usage analytics need a separate decision.

### Agent-specific additions (small, high value)

- Ship an `AGENTS.md` snippet and a Claude Code skill file in the docs. They teach the three workflows, the exit codes and the `--output json` rule.
- `kestrel docs <topic>` prints plain-text docs offline.
- An MCP server is out of scope for v1. If demand shows up, it can wrap the same generated operations.

## 7. Plugins (deferred, with one seam)

**v1 ships:**

- **External-executable discovery.** `kestrel foo` runs `kestrel-foo` from `PATH` when no built-in `foo` exists. This is the git/gh model.
- **A documented environment contract.** The CLI passes `KESTREL_API_URL`, `KESTREL_TOKEN` and `KESTREL_OUTPUT` to the plugin. This is the entire plugin API.
- **Reserved names.** All built-in and generated command names are reserved and cannot be shadowed.
- Cost is about one to two days. It is labelled **experimental** in docs, with no compatibility promise beyond the env contract and §6.

**v1 does not ship:** a plugin installer, a registry, an in-process plugin API, hooks into built-in commands or a manifest format.

**Why wait:** a plugin ecosystem is a permanent compatibility commitment. We have no plugin authors yet and no evidence of what they would build. The output contract in §6 is what keeps the door open. Revisit after two quarters of usage data and at least three concrete plugin requests.

## 8. Technology and distribution

- **Language:** Go with cobra. It produces a single static binary, handles cross-compilation and suits CI use.
- **Generator:** a small in-repo Go program that reads the OpenAPI file and emits cobra commands using the override file. Avoid heavy general-purpose generators. They fight the override and help requirements.
- **Releases:** goreleaser for darwin/linux/windows on amd64 and arm64. Publish checksums and signed artifacts.
- **Install paths:** Homebrew tap, a `curl | sh` installer script, and apt/yum packages if time allows. Containers get a published `kestrelhost/cli` image.
- **GitHub Actions:** an official `kestrelhost/setup-cli` action that installs a pinned version and reads `KESTREL_TOKEN` from secrets. Include a copy-paste deploy workflow in the docs.
- **Versioning:** SemVer. The CLI sends its version to the API. It warns on stderr, at most once a day, when it is more than one minor version behind. Warnings are disabled in CI and with `KESTREL_NO_UPDATE_CHECK`.

## 9. Eight-week plan (two engineers)

| Weeks | Engineer A | Engineer B |
|---|---|---|
| 1 | Generator skeleton, override file, spec lint in CI | Auth (`login`, token storage, `whoami`), HTTP client, output layer, exit codes |
| 2 | Generated layer end to end for all 28 resources, `kestrel api` | `deploy` against the real API, status polling |
| 3 | `schema`, `--dry-run`, pagination, destructive-op guard | `deploy` polish, failure output, `--wait` semantics |
| 4 | Contract test against staging, drift CI jobs | `logs` (read and follow, reconnect) |
| 5 | Packaging: goreleaser, Homebrew, installers | `webhooks listen` (forwarding, signing) |
| 6 | GitHub Action, docs, agent snippets | `webhooks listen` polish, `webhooks replay` |
| 7 | Plugin seam, shell completion, help curation | End-to-end tests of the three workflows, Windows pass |
| 8 | Private beta with 5 to 10 customers (include CI and Claude Code users) | Bug fixes from beta, release checklist |

**Cut order if time slips:** (1) Windows polish, (2) apt/yum packages, (3) plugin seam, (4) `webhooks replay`, (5) the curl installer. Never cut `kestrel api`, the exit-code contract or the contract test.

**Critical path:** backend work for the deploy status, log stream and webhook tap (§10). If any of the three is missing, its CLI work cannot start. Raise this in week 1 with the backend lead.

## 10. Open questions (decide in week 1)

1. **Deploy status:** does the API expose per-deployment phases and a health-based "live" signal? If not, the backend must add it. The CLI cannot infer it reliably.
2. **Log streaming:** is there an SSE or WebSocket endpoint with resume-from-timestamp? Plain REST list endpoints will not support `--follow`.
3. **Webhook event tap:** is there a development stream of real events, with a dev signing secret? If not, this is a backend feature, not a CLI feature, and it needs its own estimate.
4. **Spec accuracy:** who owns the contract test against staging (§3.2 step 3)? Without an owner, drop "never drifts" from the launch message.
5. **Idempotency keys:** does the API honor `Idempotency-Key` on `POST`? CI retries are unsafe without it.
6. **Token model:** do project-scoped tokens with limited scopes exist? CI users should not need a personal full-access token.
7. **Declarative config:** is `kestrel.yaml` (service name, project) acceptable in v1, or should deploy target flags only be supported at launch?
8. **Success metrics:** which of these will we track? Suggested: share of deploys from the CLI or CI, `kestrel api` usage by endpoint (a signal of missing curated commands), and support tickets mentioning "how do I deploy / tail logs / test webhooks".

## 11. Out of scope for v1

- Plugin installer, registry or in-process API
- MCP server
- Interactive TUI or dashboard
- Local development environment or container emulation
- Telemetry beyond `User-Agent`
- Declarative infrastructure (apply/diff of whole projects)

## 12. Assumptions I made

- Go is acceptable to the team. The user's other tooling is Go-heavy, but the spec doesn't depend on the language.
- The API already has auth tokens, per-service IDs and some form of deployment resource.
- "Live" means health-checked and serving traffic. If Kestrelhost defines it differently, §4.1 changes but its structure does not.
- The OpenAPI file has `operationId` and tags on most operations. If not, the spec lint in §3.2 will find the gaps fast.