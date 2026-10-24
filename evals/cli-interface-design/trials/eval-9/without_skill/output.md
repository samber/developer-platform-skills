# Nettlebrook `nb`: errors and help redesign

## Decisions

| Ask | Decision |
|---|---|
| (a) Auto-run the closest match for every typo | ❌ No, for flags and commands alike. Suggest only. One narrow exception: a TTY confirm prompt for read-only commands. |
| (b) `--regoin` silently ignored | 🔴 Bug. Unknown flags become a hard error (exit 2) before any API call. Also show the effective region in output. |
| (c) Raw `{"code":"FLG-4031"}` | Catalog-driven errors with what happened, why, what to do, plus request ID and docs link. |
| (d) 60-flag help dump | Layered help: a short default, grouped flags, examples, and a full reference on request. |
| `nb env` shorthand | ✅ Yes, as an explicit alias, not generic prefix matching. |
| Bare `nb` runs `nb flags list` | ⚠️ Not as asked. Show a short home screen with the current context instead. A fallback is below. |

## 1. Why not auto-run typo corrections

(b) is the same failure as (a) in a different place. In both, the CLI guesses what the user meant instead of stopping. The `nb enviroments list` case worked only because the guess was right and the command was read-only.

- **Fuzzy matching can be wrong on mutating commands.** `nb flags delet` could land on `delete`, or on a neighbour such as `deploy`. The commands change production feature flags.
- **Scripts break silently.** A CI job with a typo would "work" today. It would then change behavior when a new command shifts which name is closest.
- **Flags are worse.** A wrong flag guess changes the target (env, region, project), and that is how (b) shipped the wrong config.
- **Users can't learn the real syntax.** They keep typing the typo.

**Rule:** the CLI never executes something the user did not type.

**Keeping the delight (read-only commands only):**

- Conditions: stdin and stderr are a TTY, exactly one candidate, and the candidate is tagged read-only (`list`, `get`, `describe`).
- Behavior: ask, and default to yes.

```
$ nb enviroments list
Error: unknown command "enviroments".
Run `nb environments list` instead? [Y/n]
```

- In non-TTY mode, in CI, or with `NB_NO_PROMPT=1`: print the error and suggestion, exit 2.
- Flags are never offered a prompt. They get a suggestion only.

**Matching spec:**

- Use Damerau-Levenshtein distance, with a maximum of 2 edits and at most a third of the input length.
- Show at most 3 candidates, ranked by distance, then by usage.
- Unknown commands and unknown flags use the same code path.

## 2. Unknown flags are errors

Parse strictly. Any unrecognized flag exits 2 before the first network call.

```
$ nb flags list --regoin eu-west
Error: unknown flag --regoin for `nb flags list`.
Did you mean --region?

Nothing was run. Re-run with: nb flags list --region eu-west
Usage: nb flags list [--env <name>] [--region <name>] [--project <id>]
```

Related fixes for (b):

- **Flag in the wrong place.** If a flag exists on a sibling or child command, say so: `--region is a flag of `nb flags list`, not `nb flags``.
- **Show the target on every command.** One line on stderr, so a silent default can't hide:

  ```
  Context: project=checkout env=production region=us-east (default)
  ```

  Suppress it with `--quiet`. In `--json` mode, put it in a `context` field.
- **Mutating commands need an explicit target.** If the default region is applied implicitly and the org has more than one region, `create`, `update`, `delete`, `toggle` and `deploy` either require `--region` or ask for confirmation. Reads only print the context line.
- **Test:** every command has a test that an unknown flag exits 2 and makes zero HTTP calls.

## 3. Errors

**Pipeline:** API response → catalog lookup by `code` → render. The catalog ships inside the CLI, so errors render offline.

**Human format (stderr):**

```
Error FLG-4031: <title>
  <what happened, in one sentence, naming the resource>
  Why:  <likely cause>
  Fix:  <command or action to take>
  Docs: https://docs.nettlebrook.example/errors/FLG-4031
  Request ID: req_8f2c… (include this when contacting support)
```

Illustration only. I don't know what FLG-4031 means, so the text below is invented to show the shape:

```
Error FLG-4031: Permission denied
  Your token cannot change flag "new-checkout" in production.
  Why:  the token has the "viewer" role for this project.
  Fix:  ask a project admin for the "editor" role, or run `nb auth login`.
  Docs: https://docs.nettlebrook.example/errors/FLG-4031
  Request ID: req_8f2c…
```

**Catalog entry** (one per code):

- `title`
- `what` (template with placeholders)
- `why`
- `fix` (optional command)
- `docs`
- `exit_class`: usage, auth, not-found, conflict, server, network

**Fallbacks, in order:**

1. Code not in the catalog, but the API sent a `message`: show it, plus the code, HTTP status, request ID and docs link by pattern.
2. Code not in the catalog and no message: `Error FLG-9999 (HTTP 403). This CLI version has no description for this code. Update with `nb upgrade`, or see <docs link>.`
3. Non-JSON body, timeout or DNS failure: a network-class error that names the host and suggests `nb doctor`, retries and `--debug`.

**Contract details:**

- **Raw body.** `--debug` prints the raw response body and headers, with tokens redacted.
- **Machine output.** With `--json`, errors go to stderr as `{"error":{"code","title","message","hint","request_id","docs","http_status"}}`.
- **Exit codes.**

  | Code | Meaning |
  |---|---|
  | 0 | success |
  | 1 | runtime or server error |
  | 2 | usage error |
  | 3 | auth or permission error |
  | 4 | not found |
  | 5 | conflict |
  | 6 | network error |

- **Ask the API team.** Return `message`, `request_id` and `docs_url` alongside `code`, so the CLI isn't the only place errors get explained.
- **CI check.** Fail the build if the API's published error-code list contains a code missing from the catalog.

## 4. Help

**Principles:**

- Default help fits one screen (about 25 lines).
- Flags are grouped by purpose, not alphabetical.
- Every page ends with 2 or 3 real examples.
- The full reference is one command away. It is never the default.

**Layers:**

| Command | Shows |
|---|---|
| `nb` | Home screen (see §5) |
| `nb --help` | Top-level commands, global flags, examples |
| `nb flags --help` | Subcommands with one-liners, top flags, examples |
| `nb flags list --help` | That command's flags, grouped, common ones first |
| `nb flags list --help-all` | Every flag, including rare and deprecated ones |
| `nb help <topic>` | Concepts: `targeting`, `output`, `auth`, `errors` |

**Mockup of `nb flags --help`:**

```
Manage feature flags.

Usage: nb flags <command> [flags]

Commands:
  list      List flags in the current project and environment
  get       Show one flag with its rules
  create    Create a flag
  toggle    Turn a flag on or off in an environment
  update    Change a flag's description, tags or rules
  delete    Delete a flag

Targeting (apply to every command):
  --env <name>        Environment (default: from `nb config`)
  --region <name>     Region (default: from `nb config`)
  --project <id>      Project

Output:
  --json              Machine-readable output
  --quiet             Hide the context line

Examples:
  nb flags list --env staging
  nb flags toggle new-checkout --env production --on
  nb flags get new-checkout --json

More: `nb flags <command> --help`, or `nb flags <command> --help-all` for every flag.
```

**Flag grouping inside `nb flags list --help`:**

- Targeting: `--env`, `--region`, `--project`.
- Filtering: `--tag`, `--status`, `--search`, `--owner`.
- Output: `--json`, `--columns`, `--sort`.
- Pagination: `--limit`, `--cursor`.
- Rare or deprecated flags: `--help-all` only.

**Audit the 60 flags once:**

- Most are probably per-subcommand flags that got flattened onto the parent. Move each to the command it belongs to.
- Merge duplicates and delete dead ones.
- Promote shared flags (`--env`, `--region`, `--project`, `--json`) to one global group.
- Aim for no command with more than about 12 visible flags.

## 5. `nb env` and bare `nb`

**`nb env`**

- Register it as an explicit alias of `environments`, and list it in help: `environments (alias: env)`.
- Do not enable generic prefix matching. A future `entitlements` or `endpoints` command would turn today's `en` shortcuts ambiguous.
- Add the alias to shell completion.

**Bare `nb`**

- Reason against running `nb flags list`:
  - A first-time or logged-out user gets an auth error instead of orientation.
  - It sends an API call from a no-argument command.
  - It prints data from whichever env and region are the default, which is the (b) failure mode.
  - Everyone expects `nb` alone to explain itself.
- Recommended home screen:

  ```
  Nettlebrook CLI v1.8.0
  Context: project=checkout env=production region=us-east (default)

  Common commands:
    nb flags list           List flags
    nb flags toggle <key>   Turn a flag on or off
    nb environments list    List environments (alias: nb env list)
    nb auth login           Sign in

  Run `nb --help` for all commands.
  ```

- If you still want bare `nb` to list flags, require all of these:
  - a TTY
  - an authenticated session
  - the context line printed first
  - an opt-in via `nb config set default-command flags list`

  Never do it in non-TTY mode.

## 6. Acceptance tests

1. `nb enviroments list` in a non-TTY exits 2, suggests `environments list`, and makes no API call.
2. The same command in a TTY prompts, and `n` exits 2 without running anything.
3. `nb flags delet` (mutating candidate) never prompts. It suggests only.
4. `nb flags list --regoin eu-west` exits 2, suggests `--region`, and makes zero HTTP calls.
5. Every command prints the context line, including the `(default)` marker.
6. A mutating command with an implicit region in a multi-region org demands `--region` or confirmation.
7. A known code renders the full block. An unknown code renders the fallback with its HTTP status and request ID. A non-JSON body renders a network-class error.
8. `--json` errors parse against the schema, and `--debug` redacts tokens.
9. `nb flags --help` is at most 30 lines and has no flag listed twice. `--help-all` lists every registered flag.
10. `nb env list` equals `nb environments list`. `nb en` is a usage error.
11. Bare `nb` makes no network call.

## 7. Rollout

1. **Ship first (fixes the shipped-wrong-config risk):** strict unknown-flag errors, plus the context line.
2. **Then:** suggestions and the read-only TTY prompt, followed by the error catalog and exit codes.
3. **Then:** the help restructure, the flag audit, the `env` alias and the home screen.
4. **Changelog:** unknown flags now fail. Scripts that passed ignored flags will start exiting 2, so announce it and offer `NB_LENIENT_FLAGS=1` for one release.

## Open questions for you

- Are you fine with the mutating-command rule in §2: explicit region, or confirm, in multi-region orgs?
- What does FLG-4031 mean, and can the API team add `message`, `request_id` and `docs_url`? I invented the example text above.
- Which of the 60 flags actually belong to the parent `flags` command?