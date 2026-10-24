# Harrowgate Mail `hgm`: agent-ready CLI design spec (v1) and launch-post guidance

I followed `cli-interface-design` and its references. No interview was possible, so the Assumptions section says what each guess changes.

## Short answers

1. **Global `--yes`: no.** The stuck prompt is real, but the fix is `--confirm=<name>` for severe operations. Add `--no-input` so scripts and agents fail fast instead of hanging. `--yes` skips only moderate prompts and never a severe one.
2. **`hgm api delete /v1/domains/dom_7f21` must be guarded.** The escape hatch reads the same severity table as the curated commands, keyed by method and path. The API must enforce the guard as well, because `curl` skips the CLI.
3. **`--template ../../.ssh/id_rsa`:** treat every path, ID and payload as untrusted input. Resolve the path, then require it to sit inside the working directory. Reject it before any network call, and uploads must be an allowlisted file type.
4. **Launch post:** drop both numbers. "4-32x" is a vendor-published figure nobody has independently measured. "55k" is Anthropic's figure for five MCP servers together, not one server and not ours. Section 8 has copy you can ship and a measurement plan that would let you publish your own number.

## Assumptions

| Question | Assumption | What it changes |
|---|---|---|
| Audiences | Developers, CI and coding agents; agents are the growth bet | Machine output and non-interactive behavior come first |
| API shape | OpenAPI spec exists, not CI-gated | Generated layer stays parked |
| Multi-call or local jobs | Webhook forwarding to localhost, event log tail, domain verification wait | Curated layer is justified |
| Auth | API keys only, no scoped keys yet | Scoped and test-mode keys become an API-side dependency |
| Async work | Domain verification is async; sends accept idempotency keys | `--wait`, `wait <op-id>` and retry rules apply |
| Existing CLI | `hgm` ships today and customers parse its output | Changes follow the deprecation window, with no silent breaks |
| Customers | EU and enterprise buyers | Telemetry is opt-in |
| Deadline | Launch post pending | Fix the three incidents before the post claims "agent-ready" |

## Answer to the requester

- Every endpoint is reachable on day one through `hgm api <method> <path>`. It inherits auth, `--json`, pagination, `--idempotency-key` and the severity table.
- Curated commands carry the jobs: send, domains, templates, webhooks, logs.
- A generated per-endpoint layer is promoted only once the OpenAPI spec is CI-gated and `api` usage shows sustained demand.
- The customer's `--yes` request is answered by the severity model and scoped tokens below.

## Audiences and jobs

| Job | Audiences | Local-only part |
|---|---|---|
| `login`, `auth status` | human, CI | browser or device flow |
| `send`, `messages get` | all | none |
| `domains add/verify/list/get/delete` | all | none (verify waits) |
| `templates upload/list/get/delete` | all | reads a local file |
| `webhooks listen --forward-to` | human, agent | localhost forwarding |
| `logs tail` | all | stream |
| `describe` | agent | none |

## Command layers and grammar

- **Rung:** curated workflow commands plus the raw `api` escape hatch.
- **Order:** `noun verb`, plural nouns, verbs `list|get|create|update|delete`, plus `wait`.
- **Reserved names:** `api`, `auth`, `describe`, `wait`, `extension`.
- **Tree:** `domains`, `templates`, `messages`, `webhooks`, `logs`, `auth`, `api`, `describe`, `wait`.
- **Rejected:** prefix abbreviations and a catch-all default subcommand.

## Contract surface

- **Frozen:** command and flag names, env vars (`HGM_*`), config keys, `--json` shapes, the exit-code table, and which stream carries what.
- **Unstable:** human tables, wording and colors.
- **Enforcement:** a JSON Schema per `--json` command, golden tests against a test-mode account, and a test per exit code.
- **Deprecation:** stderr warning plus an alias for 12 months or 2 releases, whichever is longer. Removal happens only in a major release.

## Configuration and output

- **Precedence:** flag > `HGM_*` env > project config > user config > default.
- **Explicit tokens:** a token in a flag or env var beats a stored profile, with a stderr notice.
- **Secrets:** never accepted as a flag value. Use `HGM_API_KEY`, `--api-key-file`, or stdin.
- **Network:** honor proxy variables and a custom CA bundle. Lock the config file against concurrent writes, since agents run in parallel.
- **`--json`:** on every command that returns data or mutates state. Stdout carries one document per run.
- **Lists:** `{"data":[…],"has_more":…,"next_cursor":…}`. Default `--limit 20`, so an agent's context stays small. `--all` is explicit and truncation is reported in the envelope.
- **Error object:** `{"error":{"code","message","request_id","operation_id","retry","docs_url","hint"}}`.

### Exit codes

| Code | Meaning | Caller action |
|---|---|---|
| 0 | Success or idempotent no-op | continue |
| 1 | Other failure | read the error |
| 2 | Usage or validation error, including missing confirmation and rejected paths | fix the invocation; never retry |
| 3 | Not found | branch |
| 4 | Authentication required, expired, or token lacks scope | re-authenticate or use a broader token |
| 5 | Safe to rerun (429, 503 with `Retry-After`, failure before send) | rerun with backoff |
| 6 | Outcome unknown (timeout after send, other 5xx) | `wait <op-id>` or `get`; never rerun blind |
| 7 | Partial failure in a bulk operation | read per-item results |
| 130 | Interrupted; CLI detached and printed the resume command | resume or stop |

## Auth

| Context | Flow | Token |
|---|---|---|
| Desktop | PKCE with loopback redirect, or key paste | scoped, expiring |
| SSH or container | device grant, if the API gains one; otherwise key via stdin | same |
| CI and agents | `HGM_API_KEY` env var | scoped, expiring, **test-mode by default** |

- Store credentials in the OS keychain. If none exists, warn loudly before writing an owner-only file.
- Ship `auth status` (identity, winning source, expiry, mode, scopes) and `auth logout`.
- **No `auth token` print command.** A token-print command was used to harvest tokens in the s1ngularity malware.
- Redact secrets in all output, including `--debug`.

## Severity table (shared by curated commands and `hgm api`)

Lookup is by command, or by method plus path pattern. The `api` command matches the path against the same table.

| Operation | Grade | Terminal | Non-interactive |
|---|---|---|---|
| `GET` anything, `domains verify`, `templates list/get` | mild | none | none |
| `templates upload/update`, `webhooks create/update`, `send` in test mode | moderate | confirm | `--yes` |
| `DELETE /v1/domains/{id}` (`domains delete`) | **severe**: removes the domain and emails 40 senders | type the domain name | `--confirm=<domain name or id>` |
| `DELETE /v1/templates/{id}`, webhooks, keys | severe if live traffic references it | type name | `--confirm=<name or id>` |
| Any bulk or filtered mutation | severe | type the count | `--confirm-count=<n>` |
| Live-mode `send` to more than N recipients | severe | confirm count | `--confirm-count=<n>` |
| **Unlisted `POST/PUT/PATCH/DELETE` via `api`** | **moderate by default; unlisted `DELETE` is severe** | confirm | `--yes` for moderate, `--confirm` for `DELETE` |
| GraphQL mutations, if any | severe unless listed | as above | as above |

### Behavior for incidents 1 and 2

- **Incident 1: stuck prompt.** With stdin not a TTY, or with `--no-input`, never prompt. Exit 2 with: `Deleting mail.acme-corp.example is severe: it notifies 40 verified senders. Re-run with --confirm=mail.acme-corp.example`. Add `"error":{"code":"confirmation_required","flag":"--confirm"}` under `--json`.
- **Incident 2: ungated `api delete`.** The path contains only `dom_7f21`, so the CLI first does a read (`GET /v1/domains/dom_7f21`) to resolve the name and the impact. It then asks for the name, or accepts `--confirm=<name or id>`. If the lookup fails, it asks for the raw ID.
- **Dry run:** `--dry-run` on every mutating command prints the impact without committing: `would delete domain, would email 40 senders`. The API needs a validate-only mode for this.
- **Why `--confirm=<name>` is not a security boundary:** an agent set on proceeding can read the name from its own output. It stops mistakes only. The real boundary is the credential.

### Customer answer on `--yes`

> We won't add a global `--yes`. It would turn every destructive guard off for agents and humans alike. For automation, pass `--confirm=<name>` on the specific severe operation. Better, give the agent a restricted key: test-mode, read-only, or scoped without `domains:delete`. Then it cannot delete a domain no matter what it types.

## Input hardening (incident 3)

Applies to every file path, resource ID and payload.

1. **Paths:** resolve with symlinks (`realpath`). Require the result to be inside the current working directory or a declared `--root`. Reject `..` escapes, absolute paths outside the root, and dot-directories such as `.ssh`, `.aws` and `.git`.
2. **Type and size:** `templates upload` accepts only the template extensions and MIME types the API supports, up to a stated size cap. A private key fails on type even if the path check is bypassed.
3. **Errors:** exit 2 with `path_outside_root`, naming the flag and the rule. Make no network call.
4. **Other inputs:** IDs must match `^[a-z]+_[A-Za-z0-9]+$`. Reject `?`, `#` and `%` in IDs and in `api` paths that would change the target. Reject control characters in names.
5. **Server-side:** the API rejects non-template content regardless of the client.
6. **Test cases:** `../x`, absolute `/etc/passwd`, a symlink to `~/.ssh/id_rsa`, `..%2f`, a 0-byte file, and a file over the size cap.

## Agent readiness

- **Self-description:** `hgm describe --json` prints the command tree, flags, severity grades and output schemas.
- **Bounded output:** small default fields, `--limit 20`, totals, explicit empty results ("0 domains found"), and a truncation marker naming `--all`.
- **Waits and retries:**
  - Async mutations wait by default with `--wait-timeout 120s`, on a state that normally resolves in seconds to minutes. That is a default to tune against real verification latency.
  - `--no-wait` returns the operation ID; Ctrl-C or SIGTERM detaches and prints `hgm wait <op-id>`.
  - The CLI sends an idempotency key per invocation, reuses it on retries, and accepts `--idempotency-key`.
- **Token to hand an agent:** a test-mode, scoped, expiring key. Document this on the agents page.
- **Help:** two or three examples per command, plus topics for exit codes, env vars and output.

## API-side dependencies

| Need | Blocks |
|---|---|
| Scoped, expiring, test-mode keys (`domains:delete`, read-only) | the token advice and the customer's real fix |
| Server-side guard on severe `DELETE`s (confirm parameter or token scope), so `curl` is covered | incident 2 |
| Validate-only or dry-run mode with impact counts | `--dry-run` |
| Operation status endpoint | `wait` |
| Server-side template content-type validation | incident 3 |

## Release cut line

| Capability | v1 | Later |
|---|---|---|
| Severity table with `api` coverage, `--confirm`, `--no-input` | ✅ | |
| Path and ID hardening | ✅ | |
| Exit-code table with tests | ✅ | |
| `describe` | ✅ | |
| Scoped keys documentation | ✅ (needs API) | |
| Generated per-endpoint layer | | on trigger |
| Telemetry | | opt-in only, announced in a major version |

## Gates

- ⏳ **Contract coverage:** schemas and `--json` on every data or mutating command.
- ⏳ **Non-interactive run:** test every command with stdin closed and stdout piped.
- ⏳ **Exit codes:** one test per code.
- ⏳ **Severe-action guard:** tests that `hgm api delete /v1/domains/dom_7f21` fails without confirmation. A mutation test: remove the table entry and see the test go red.
- ⏳ **Secret hygiene:** no secret flag, nothing printed in debug.

## 8. Launch post: what to put in

**Cut both claims.**

| Claim | Problem |
|---|---|
| "MCP costs 4-32x more tokens than our CLI" | Vendor-published and not independently measured. It compares someone else's setup, not Harrowgate's. |
| "MCP eats 55k tokens of context" | Anthropic's figure for five MCP servers together, not one. It says nothing about a Harrowgate MCP server. |

The evidence is mixed. One practitioner benchmark found CLI and MCP close in success rate and cost once tool design was controlled for. Tool design moves results more than the protocol does.

**What you can say today:**
- The CLI is built for terminal-native agents and CI. It has one JSON document on stdout, a published exit-code table, `--no-input`, bounded default output, and `hgm describe` for self-description.
- Anthropic's Claude Code best practices call CLI tools "the most context-efficient way to interact with external services". Cite that as a quote, not as a measurement of Harrowgate.
- Destructive operations need an explicit `--confirm`. Say how the guard works, not that it makes agents "safe".

**Suggested copy:**

> `hgm` is built for the agents already in your terminal. Every command speaks JSON, fails fast instead of prompting, and tells an agent exactly which flag it's missing. Destructive actions need an explicit `--confirm`, and you can hand an agent a test-mode or scoped key so it can't delete what it shouldn't.

**To publish your own number later:**
1. Fix a task set: send a message, add and verify a domain, upload a template.
2. Count tokens for `hgm describe` plus the calls made, against your MCP server's tool definitions plus calls, on the same model.
3. Publish the method, versions and raw data, and report success rate next to tokens.
4. If you do not ship an MCP server, say nothing about MCP cost.

Hold the "agent-ready" headline until the three fixes ship. The post would otherwise invite the same incidents in public.

## Open items

| Decision | Owner | Due |
|---|---|---|
| Confirm API-side guard and scoped keys | API team | before launch |
| Pick N for the live-send bulk threshold | product | before launch |
| Confirm `--wait-timeout` against real verification latency | CLI team | before launch |
| Decide whether an MCP server ships (it affects the post) | product | before the post |

## Self-review notes

- I did not verify the existing `hgm` code, the API's scopes, or whether `hgm` has an MCP counterpart. Each of these is an assumption.
- I took the 40-sender impact from your incident description, so the dry-run example text is illustrative.