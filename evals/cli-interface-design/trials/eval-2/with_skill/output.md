# `orn` CLI interface fix (spec v1)

**Next action:** ship the five "now" items in section 9. They remove the CI hang and the table scraping. The exit-code split waits for a major release.

## 1. Answer to the requester

Your fix idea has two parts. Both are wrong in the same way.

- **`--yes` plus "CI must set `PAGER=cat`" puts the burden on every customer.**
  - A CLI must never block off a terminal. GitHub Actions has no TTY on stdin or stdout, so `orn` should never prompt or page there.
  - The CLI fix means no workflow edits and no docs lookup.
  - The AWS CLI v2 default pager (2019) had the same effect: scripts blocked until someone pressed `q`.
- **`--yes` is still right, but it must be the second line of defence.**
  - Off a TTY, `orn deploy` fails at once with exit 2 and says "pass `--yes`". It never waits for input.
  - `--yes` skips only a *moderate* confirmation. It never skips a *severe* one (section 7).
- **The scraping problem needs a published contract, not a fix.**
  - Declare tables unstable and freeze `--json`. Then put `--json` on `deploy` and every other command that returns data or changes state.
  - Today only 2 commands have `--json`. The deploy command is the one agents parse most, and it has none.

## 2. Assumptions

I could not ask the questions, so each answer below is an assumption. Correct any that is wrong. The last column says what changes.

| Question | Assumption | What changes if wrong |
|---|---|---|
| Who runs the CLI? | CI and coding agents break the business. Humans run it too. | Human-only means prompts matter more than `--json`. |
| API spec | Hand-maintained | No generated layer. Keep the curated commands plus `orn api`. |
| Multi-call or local jobs | Deploy-and-wait is the main one. The API gives a deployment ID and a state endpoint. | Already covered. |
| Auth | API keys and a dashboard login exist. | CI token scope is an API-side dependency (section 12). |
| Async and destructive operations | Deploy is async. Service delete is irreversible. Rollback exists. | If there is no rollback, grade production deploy *severe*. |
| Idempotency keys | The API does not accept them yet. | Dependency in section 12. Until then, a timed-out create is "outcome unknown" (exit 6). |
| Existing scripts | Customers test `$? -ne 0` and parse the table. | Changing exit codes needs the staged rollout in section 8. |
| Deadline and effort | Small team, fast fix. | Self-description and the generated layer go to "later". |

## 3. Jobs and audiences

| Job | Audience | API calls | Local-only part |
|---|---|---|---|
| Deploy service and learn when it is live | CI, agent, human | create deployment, poll state | wait loop, progress |
| Check or resume a deployment | CI, agent | get deployment | none |
| List and inspect services | all | list, get | none |
| Reach any other endpoint | agent, power user | any | none |

## 4. Command layers and grammar

- **Rung:** curated commands plus a raw escape hatch.
  - Keep `orn deploy` as the frozen curated entry point.
  - Add `orn deployments get|list|wait|cancel` as the follow-up commands.
- **Escape hatch:** `orn api <method> <path>`.
  - It inherits auth, `--json`, `--no-input` and the severity table from section 7.
- **Generated layer:** promote it only when the OpenAPI spec is checked in CI and `orn api` shows sustained per-endpoint demand.
- **Grammar:** `noun verb`, plural nouns, verbs `list|get|create|update|delete|wait|cancel`. `deploy` is the one deliberate exception.
  - Reject prefix abbreviations and a catch-all subcommand.
  - Reserve `orn plugin` and `orn extension`.

## 5. Contract surface

- **Frozen:**
  - command and flag names, env var names, config keys
  - `--json` shapes and field names
  - the exit-code table
  - the stream rules in section 6
- **Unstable:** every human table, wording, colour and spinner.
  - Publish this in the docs and in `orn help output`.
  - Scripts and agents must parse `--json`, never the table. That ends the regex breakage.
- **Enforcement:**
  - a JSON Schema per `--json` command
  - golden-output contract tests against a test environment
  - one test per exit code
- **Changes:** adding a field is safe. Renaming, retyping or removing one is breaking.
  - Bare `--json` returns a documented default field set.
  - `--json all` returns full objects.
  - `--json id,state` returns only the named fields.

## 6. Output, streams and exit codes

**Streams**

| Mode | stdout | stderr |
|---|---|---|
| Human (terminal or piped) | the result table | progress, warnings, errors |
| `--json` | exactly one JSON document, success or `{"error": …}` | progress and free-text hints |

- Errors move from stdout to stderr in human mode. Today they go to stdout.
- Colour, spinners, pagers and prompts exist only on a TTY. Honour `NO_COLOR`, `--no-color` and `TERM=dumb`.
- A list uses one envelope from v1: `{"data":[…],"has_more":false,"next_cursor":null}`.
- Timestamps use RFC 3339 UTC. Absent values are `null`, never a missing key.

**Pager.** The pager runs only when stdout is a TTY, the command is a list or log view, and the output is longer than one screen.

- It never runs for `deploy`, with `--json`, or off a TTY.
- It is controlled by `ORN_PAGER` and `--no-pager`. It does not follow the system `PAGER` implicitly.

**`orn deploy --json` shape.** It is identical whether the command waited or not.

```json
{
  "deployment_id": "dep_3",
  "service": "api-gateway",
  "environment": "production",
  "state": "succeeded",
  "waited": true,
  "url": "https://api-gateway.example.com",
  "started_at": "2026-10-24T09:00:00Z",
  "finished_at": "2026-10-24T09:04:12Z"
}
```

With `--no-wait` the same keys are returned, with `state` set to `queued` and `finished_at` set to `null`.

**Error object (under `--json`, on stdout)**

```json
{
  "error": {
    "code": "deployment_failed",
    "message": "Deployment dep_3 failed: health check timed out.",
    "request_id": "req_8f2a",
    "operation_id": "dep_3",
    "retry": "never",
    "docs_url": "https://docs.example.com/errors/deployment_failed",
    "hint": "Run `orn deployments get dep_3` for details."
  }
}
```

**Exit codes.** Each code tells the caller to do something different.

| Code | Meaning | Caller action |
|---|---|---|
| 0 | Success, including a no-op | continue |
| 1 | Failure not covered below, including a deployment that ran and failed | read the error |
| 2 | Usage error, including "confirmation needed, pass `--yes`" | fix the invocation |
| 3 | Not found | branch |
| 4 | Authentication required or token expired | re-authenticate |
| 5 | Safe to rerun: 429, or 503 with `Retry-After`, or failure before the server accepted the request | rerun with backoff |
| 6 | Outcome unknown: wait timeout, or connection lost after sending | `orn deployments wait <id>`; never rerun a create blind |
| 7 | Partial failure in a bulk operation | read per-item results |
| 130 / 143 | Interrupted by SIGINT / SIGTERM; the CLI detached and printed the resume command | resume or stop |

Do not use sysexits values or the 126–127 and above-128 shell range for other meanings.

## 7. Safe without a terminal

**Rules**

- When stdin is not a TTY, never prompt. Fail at once with exit 2 and name the missing flag.
- `--no-input` and `ORN_NO_INPUT=1` force the same behaviour on a terminal.
- Update checks, notices and telemetry banners stay silent off a TTY.

**Severity table.** The curated commands and `orn api` both read it, keyed by command and by method plus path.

| Command or method + path | Grade | Terminal | Non-interactive |
|---|---|---|---|
| `services list`, `services get`, `deployments get\|list\|wait`, `GET *` | mild | none | none |
| `deploy` to a non-production environment | mild | none | none |
| `deploy` to `production` | moderate | confirm `[y/N]` | `--yes` |
| `deployments cancel` | moderate | confirm | `--yes` |
| `services delete`, `DELETE /services/*` | severe | type the service name | `--confirm=<name>` |
| Bulk operations | severe | type the count | `--confirm-count=<n>` |

- `--yes` never skips a severe confirmation.
- Offer `--dry-run` on every mutating command where the API can validate without committing.
- A confirmation stops mistakes, not an agent set on proceeding. What bounds an agent is its token (section 10).

## 8. Long-running deploys

- **Wait by default**, in every context. Progress goes to stderr, one plain line per state change off a TTY.
- **`--wait-timeout`** defaults to `15m`. Deploys take 2–10 minutes, so 15 minutes leaves headroom, and the wait stays bounded.
- **Poll** the state endpoint every 2 s, backing off to a 10 s cap, to stay under the API rate limit.
- **`--no-wait`** returns the deployment ID immediately.
- **`orn deployments wait <id>`** resumes a deployment and honours the same timeout and exit codes.
- **Ctrl-C or SIGTERM** (a cancelled CI job) detaches. It does not cancel. The CLI prints the deployment ID and `orn deployments wait dep_3`, then exits 130 or 143.
- **Wait timeout** exits 6 and prints the same resume command.
- **Retries:** the CLI retries transient failures at most 3 times with bounded backoff and honours `Retry-After`. It sends one idempotency key per invocation, reuses it on automatic retries, and accepts `--idempotency-key`.

## 9. Release cut line

| Capability | Ship | Reason |
|---|---|---|
| No prompt off a TTY, exit 2 naming `--yes` | now (patch) | Removes the 6 h hang. |
| `--yes`, `--no-input`, `ORN_NO_INPUT` | now | Documents the CI path. |
| No pager off a TTY or under `--json`; `--no-pager` | now | Removes the second hang. |
| `--json` on `deploy`, `deployments *`, and every other data or mutating command; the JSON error object on stdout | now (minor, additive) | Ends table scraping. |
| `--wait-timeout`, `--no-wait`, `deployments wait`, detach on SIGINT or SIGTERM | now | Needs only the existing state endpoint. |
| Errors to stderr in human mode | next minor | Release note required. |
| Exit codes 3–7 | next major, or opt-in `ORN_EXIT_CODES=2` in a minor | Scripts testing `== 1` break. AWS CLI v2 listed changed return codes as a breaking change. |
| JSON Schemas, contract tests, `orn commands --json` self-description | later | Not needed to stop the two problems. |
| Idempotency keys | when the API supports them | API dependency. |

## 10. Agent readiness

- Agents parse `--json`, `--json id,state`, and the exit code.
- The default output is small. An empty list prints an explicit "0 deployments found". Truncation names the flag that shows more.
- Validate identifiers, paths and payloads as untrusted input. A `../../` in a service name must hit a validation error.
- **Hand an agent a scoped token:** `ORN_TOKEN`, scoped to one service and environment, expiring, read-only unless it must deploy. Use test mode by default.

## 11. Help and errors

- Rewrite API errors to say what failed, why, and the next command. Keep the API error code and request ID.
- Reject unknown flags by name before any API call. Suggest the closest command on a typo and never auto-run the suggestion.
- `orn help output` documents the stream rules and exit codes. `orn help env` documents the env vars. Each command's help leads with 2–3 examples.
- Ship shell completion and a redacted `--debug` trace. Never print a secret.

## 12. API-side dependencies

| Need | Blocks |
|---|---|
| Idempotency key on create deployment | Exit 5 on a timed-out create; safe `--idempotency-key` reruns |
| Scoped, expiring service tokens | The agent and CI token advice in section 10 |
| Stable `state` enum (`queued`, `running`, `succeeded`, `failed`, `cancelled`) | The `--json` schema and exit mapping |

## 13. Gates

- [ ] **Contract coverage:** `--json` on every data or mutating command; the frozen list and schemas are published. *Open: only 2 commands have `--json` today.*
- [ ] **Non-interactive run:** every command with stdin closed and stdout piped finishes or fails fast naming the flag. *Add a CI test that runs `orn deploy` with no TTY and asserts exit 2 within 1 s.*
- [ ] **Exit-code table tested:** one automated test per code.
- [ ] **Severe-action guard:** `orn api DELETE /services/x` demands `--confirm=x`, same as `services delete`.
- [ ] **Secret hygiene:** no secret accepted only as a flag; none printed in normal, verbose or debug output.

## 14. Open items

| Decision | Owner |
|---|---|
| Is production deploy moderate or severe (does rollback exist)? | product |
| Ship exit codes in a major, or opt-in in a minor? | CLI lead |
| Add idempotency keys to the deployments API | API team |

**Next:** answer the first open item (does rollback exist for a production deploy?). It sets whether `--yes` is enough in CI.