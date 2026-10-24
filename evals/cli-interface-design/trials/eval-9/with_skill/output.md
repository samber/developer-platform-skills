# Nettlebrook `nb` errors and help spec (v0.1)

Verdict on the support load:

| Ask | Decision |
|---|---|
| (a) Auto-run the closest match for every typo | **No.** Print the full corrected command, exit 2, run nothing. |
| (b) `--regoin` ignored | **Bug.** Reject unknown flags by name before any API call. Echo the resolved region on every list. |
| (c) Bare `{"code":"FLG-4031"}` | **Fix.** Local error catalog, request ID, and a next command. |
| (d) 60-flag `nb flags --help` | **Fix.** Split by command, 12 flags max per page, examples first. |
| `nb env` shorthand | **Yes, as a declared alias.** No prefix matching. |
| Bare `nb` runs `nb flags list` | **No.** Bare `nb` prints short help. |

Next action: find where the flag parser lets unknown flags through, which is probably a "pass unknown flags" setting. That one line caused the wrong-config incident, so fix it first.

## Assumptions

I could not ask the batch of questions, so each answer below is an assumption.

| Question | Assumption | What it changes |
|---|---|---|
| Audiences | Developers at a terminal, plus CI. Agents are rising. | Exit codes and `--json` errors matter as much as prose. |
| API shape | Resource verbs are uniform. Errors return only `{"code": "..."}`. Request ID travels in a response header, likely `X-Request-Id`. | The CLI must hold the error text. Owner: API team. |
| Multi-region | Region and environment are scopes on most calls. The built-in default region is `us-east`. | Scope must be visible, never silent. |
| Existing CLI | It ships and users script it. | Every change below is additive except unknown-flag rejection. See "Release cut". |
| Out of scope | Auth, telemetry, pagination, and versioning are untouched. | They stay as they are, listed in Open items. |

## Answer to the requester

**(a) Why not auto-run.** The users who loved it were helped by the guess. They did not need the CLI to execute it. Printing the exact corrected command gives the same win:

```
$ nb enviroments list
Error: unknown command "enviroments" for "nb".
  Did you mean: nb environments list
Run `nb help` to see all commands.
```

Exit code is 2. Nothing ran and no request was sent. The user presses up-arrow, fixes one word, and re-runs.

Auto-run has three costs.

- **Mutations.** Take an illustrative case: `nb flags toggle checkout --environment prd` guessed to `prod` flips a production flag from a typo. Flags are state.
- **Frozen typos.** Scripts that include the typo keep working, so you must support `enviroments` forever.
- **Flag typos.** `--regoin` guessed as `--region` runs a call the user never specified.

**(b) Why it happened.** The parser accepted an unknown flag and dropped it. The fix has three parts.

1. Unknown flags fail before the API call, name the flag, and suggest the closest valid one.
2. Every list prints its scope, so a wrong default is visible even when the user typed nothing wrong.
3. Mutating commands refuse to use the built-in default region. The region must come from a flag, env var, or config. In human mode, one line on stderr names the source.

**`nb env`.** Register `env` as an explicit alias of `environments`. It is declared, listed in help, and frozen.

- Do not enable prefix matching (`nb envir`, `nb fl`). Prefix matching makes every future command that shares a prefix ambiguous or breaking.
- The alias costs one reserved name. Accept that.

**Bare `nb`.** Do not default to `flags list`. A catch-all default blocks future top-level commands. It also makes a mis-typed or empty CI invocation call the API silently, and (b) shows what a silently wrong scope does. Show help instead. `nb flags list` is the first example, so the shortcut costs the user nothing.

## Errors

### Rules

1. Every error states what failed, why, and the next command.
2. Every error carries the API code and request ID.
3. Unknown command or flag exits 2 before any network call.
4. The CLI never executes a suggestion and never prompts for one.

### Human mode (stderr)

The text below is hypothetical. It assumes FLG-4031 means the token lacks write scope. The API team must give the real meaning.

```
Error: this token cannot change flags in "prod". [FLG-4031]
  The token has read-only access to this environment.
  Next: nb auth status      show which token and account are in use
        nb auth login       log in with a write-capable account
  Request ID: req_8f2a
  Docs: https://<docs-host>/errors/FLG-4031
```

### Fallbacks, so no error is ever a bare code

| Situation | Output |
|---|---|
| Code missing from this CLI's catalog | `Error: the API rejected the request (FLG-9999, HTTP 422). This CLI version has no description for this code. Request ID: req_... Docs: <docs-host>/errors/FLG-9999. Next: update the CLI.` |
| Body is not JSON (proxy page, gateway) | `Error: unexpected response from <host> (HTTP 502). It did not come from the Nettlebrook API. Check HTTPS_PROXY and NO_PROXY.` |
| No code, but a status | Generic text per status. 401: `nb auth login`. 404: name the resource and a `list` command. 429: say when to retry. 5xx: print the request ID. |
| Request ID absent | Print `Request ID: unavailable`. Never omit the line, so support can see the gap. |

### Typo suggestions

- Candidates are the valid siblings at that level: commands, subcommands, or flags.
- Use Damerau-Levenshtein distance of 2 or less, case-folded.
- Show up to 3. For a flag, suggest the full corrected invocation.
- No candidate under the threshold: list the valid ones. Never guess.

Unknown flag example:

```
$ nb flags list --regoin eu-west
Error: unknown flag --regoin for "nb flags list". (No request was sent.)
  Did you mean: --region
  Valid flags: --environment, --region, --limit, --all, --tag, --json
  Run `nb flags list --help` for examples.
```

### Scope echo (the second half of the (b) fix)

Every command that reads or writes scoped data prints one stderr line in human mode:

```
Region: eu-west (--region)   Environment: prod (profile "default")
```

- The source is one of `--flag`, `NB_REGION`, project config, user config, or `built-in default`.
- `--json` adds the same data to the envelope:

```json
{"data": [], "has_more": false, "next_cursor": null,
 "scope": {"region": "us-east", "region_source": "default", "environment": "prod"}}
```

An empty list reads "0 flags found in prod / us-east". Never print a bare empty table.

### `--json` mode

Stdout carries exactly one document. Under `--json`, the error goes to stdout, as the skill's stream rules require.

```json
{"error": {
  "code": "FLG-4031",
  "message": "This token cannot change flags in \"prod\".",
  "request_id": "req_8f2a",
  "operation_id": null,
  "retry": "never",
  "docs_url": "https://<docs-host>/errors/FLG-4031",
  "hint": "Run `nb auth status` to see which token is in use."
}}
```

Client-side failures get their own codes, for example `usage_unknown_flag`, `usage_unknown_command`, and `config_region_required`. A usage error adds `"suggestions": ["--region"]`.

### Exit codes

| Code | Meaning | Caller action |
|---|---|---|
| 0 | Success, including an idempotent no-op and help shown | continue |
| 1 | Failure not covered below | read the error |
| 2 | Usage error: unknown command, unknown flag, missing required value | fix the invocation; never retry |
| 3 | Not found | branch |
| 4 | Authentication required, token expired, or token lacks scope | re-authenticate |
| 5 | Safe to rerun: 429, 503 with `Retry-After`, failure before the server accepted the request. Reads that hit other 5xx also map here. | rerun with backoff |
| 6 | Outcome unknown: timeout or 5xx after sending a non-idempotent call | `get` or `list` to check; rerun only with `--idempotency-key` |
| 130 | Interrupted | resume or stop |

Partial-failure code 7 is not needed until a bulk command exists.

### Error catalog

- Store it as data, one entry per API code: `message`, `why`, `next` (list of commands), `retry` class, and `exit_code`.
- Ship it inside the CLI. Add a CI check that fails when the API's code list contains a code the catalog lacks.
- The CLI never prints an API code alone.

## Help

### Rules

1. `nb`, `nb help <cmd>`, `nb <cmd> --help`, and `-h` all work.
2. Each command page: summary, 2 to 3 examples, flags with defaults, then a docs link.
3. A page lists 12 flags at most. Test this in CI.
4. Global flags and env vars appear as one line pointing to a help topic.
5. Grouping commands (`nb flags`) list subcommands only. They never list their children's flags. This is the likely cause of the 60-flag dump.

### Bare `nb`

```
nb - Nettlebrook feature-flag CLI

Usage: nb <command> [flags]

Common:
  nb flags list                 List flags in the default environment
  nb flags get <key>            Show one flag
  nb environments list          List environments  (alias: env)
  nb auth login                 Log in

Commands: flags, environments (env), auth, api
Run `nb <command> --help` for examples and flags.
Topics: nb help global | output | exit-codes | environment-variables
```

Exit 0. The page shows the raw `api` escape hatch and the `help` topics. The command list above is illustrative; use the real verb set.

### Grouping command, `nb flags --help`

```
Manage feature flags.

Usage: nb flags <command>

Commands:
  list      List flags
  get       Show one flag
  create    Create a flag
  update    Change a flag's settings
  delete    Delete a flag (confirmation required)

Run `nb flags <command> --help` for examples and flags.
```

### Leaf command, `nb flags list --help`

```
List feature flags in one environment and region.

Usage: nb flags list [flags]

Examples:
  nb flags list --environment prod
  nb flags list --region eu-west --json
  nb flags list --all --json | jq '.data[].key'

Flags:
  -e, --environment <name>  Environment to read (default: from profile)
      --region <name>       Region to read (default: from profile, else us-east)
      --tag <tag>           Only flags with this tag (repeatable)
      --limit <n>           Max flags returned (default 50)
      --all                 Fetch every page
      --json [fields]       Machine output; bare --json gives the default fields

Global flags and environment variables: nb help global
Exit codes: nb help exit-codes
Docs: https://<docs-host>/cli/flags-list
```

The default values above are placeholders. Each real default needs a one-line reason in the spec.

### Cutting the 60

| Cause | Fix |
|---|---|
| Child flags merged into the parent page | Parents list subcommands only. |
| Global flags repeated on every page | One line plus `nb help global`. |
| One command with dozens of rule fields (for example `create`) | Take rules as a payload: `--from-file flag.json` or `-` for stdin. Keep 8 to 10 convenience flags. Print the payload schema with `nb flags create --schema`. |
| Rarely used flags | Group them under headings (Filtering, Output) in the leaf page. Document the rest in a help topic. |

### Help topics

`nb help global`, `output`, `exit-codes`, and `environment-variables`. Each cross-cutting contract is written once and linked from the leaf pages.

### Also ship

- Shell completion from the first release. It includes the `env` alias.
- `nb commands --json` prints the command tree, flags, and schemas, so agents and tests do not scrape help text.
- `--debug` prints a redacted HTTP trace to stderr.

## Contract

- Frozen: command names, the `env` alias, flag names, exit codes, the error object, `scope` in the envelope, and `usage_*` error codes.
- Unstable: help wording, error prose, tables, and suggestion text. State this in the docs, so scripts branch on `error.code` and the exit code, never on prose.
- The `suggestions` list in `--json` is unstable too. Document it as a hint.

## Tests

Each test below fails today for at least the first two.

1. **Unknown flag.** For every command, pass `--zzz`. Assert exit 2, the flag named in the message, and zero HTTP requests. Use a mock server and count requests.
2. **Typo suggestion.** `enviroments` and `--regoin` both print the suggestion. No request is sent and the suggestion is not executed.
3. **No auto-run.** Assert that no command path calls the dispatcher with a corrected argument vector.
4. **Alias.** `nb env list` equals `nb environments list`. `nb envir list` fails with exit 2.
5. **Bare `nb`.** Prints help, exit 0, zero HTTP requests.
6. **Scope echo.** A list with no region flag prints `us-east (built-in default)`. `--region eu-west` prints `(--region)`. A mutation with only the built-in default exits 2 with `config_region_required`.
7. **Catalog coverage.** Every API error code has an entry. An unknown code, a non-JSON body, and a missing request ID each produce the fallback text.
8. **Help budget.** No page lists more than 12 flags. Every leaf page has at least 2 examples.
9. **Non-interactive.** Run every error path with stdin closed and stdout piped. None may prompt or hang.

Mutation check: reintroduce the "pass unknown flags" setting. Test 1 must fail.

## API-side dependencies

| Need | Owner | Blocks |
|---|---|---|
| Error body with `message`, `request_id`, `docs_url` beside `code` | API team | Catalog drift. Until then, the CLI reads the request ID from the header. |
| Stable list of error codes, with meaning and retry class | API team | Catalog and its CI check |
| Real meaning of FLG-4031 and the other top error codes | Support, from the ticket data | Catalog text |

## Release cut

| Capability | v1 | Later | Reason |
|---|---|---|---|
| Strict unknown-flag rejection | yes | | Fixes the wrong-config incident. Breaking for scripts that pass unknown flags, so ship it in a major version, or in a minor version with a stderr warning for one release and then the error. |
| Typo suggestions, scope echo, error catalog | yes | | Additive |
| `env` alias, bare-`nb` help | yes | | Additive |
| Help split and 12-flag budget | yes | | Help text is unstable |
| `--schema`, `nb commands --json` | | yes | Agent readiness. Needs schemas first. |

## Open items

| Decision | Owner | Due |
|---|---|---|
| Confirm the parser setting that dropped `--regoin` | CLI engineer | first, before the rest |
| Fill the catalog with real code meanings | Support plus API team | before release |
| Require an explicit region for mutations: ship in v1 or warn first | Product | before release |
| Sections not covered here: auth, pagination, telemetry, versioning, severity table | CLI owner | separate pass |

## Gates

- [ ] Non-interactive run: tests 5 and 9
- [ ] Exit-code table tested: tests 1, 2, 6
- [ ] Contract coverage: not assessed here
- [ ] Severe-action guard: not assessed here
- [ ] Secret hygiene: not assessed here. Error text must never echo token fragments.

Status: errors and help are designed. The unknown-flag fix, the scope echo, and the catalog are the three changes that remove the support load.

Next: open the CLI's parser setup and confirm why `--regoin` passed through. That takes about 15 minutes.