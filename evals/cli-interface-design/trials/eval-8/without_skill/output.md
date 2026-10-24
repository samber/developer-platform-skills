# Quarrystone CLI: list and streaming design

## Decisions

1. **`--all` means "fetch every page". It never changes output shape.** Today's proposal makes one flag control both scope and format, so `--json --all` would return a different type than `--json`. That breaks parsers and surprises people.
2. **A new `--ndjson` flag controls streaming.** `--all --ndjson` streams a huge bucket. `--all --json` still returns one valid JSON array.
3. **Truncation must never be silent.** The reconciliation-script bug is a silent-truncation bug, so we fix that directly.
4. **`stdout` carries data only.** Every diagnostic goes to `stderr`.
5. **`--jq` is built in (embedded gojq).** It lives on the same axis as `--json`.
6. **Full records come from `--fields`, not from changing `--json`.**
7. **The pager is conditional, not always on.**

## 1. Pagination and `--all`

| Command | Behavior |
|---|---|
| `objects list` | One page (default 20). |
| `objects list --limit N` | One page of N, capped at the API maximum. |
| `objects list --cursor C` | Resume from a cursor. |
| `objects list --all` | Follow cursors until exhausted. |
| `objects list --all --json` | One valid JSON array, written incrementally. |
| `objects list --all --ndjson` | One JSON object per line, constant memory. |

- The CLI writes `[`, then each item separated by commas, then `]`, as pages arrive. Its own memory stays flat. Consumers that parse the whole array still buffer, which is why `--ndjson` exists.
- `--json` and `--ndjson` are mutually exclusive. `--ndjson` implies JSON output.

### Making truncation visible

- **Now (minor release):** keep the array shape, which is backward compatible. When a page is truncated and `--all` was not given, write this to `stderr`, in every mode:
  `qs: showing 20 objects; more available. Use --all or --cursor <c>.`
  Skip the notice when the user passed an explicit `--limit`. They asked for a page.
- **Limit of the notice:** scripts that run `2>/dev/null` won't see it. We should be honest about that in the changelog.
- **Next major:** list `--json` returns the envelope `{"items":[…],"next_cursor":"…"|null}`. A script that ignores `next_cursor` then fails loudly, because it must unwrap `items`. Announce the change in the minor release.
- **Strict mode:** add `--fail-if-truncated` and the matching `QS_FAIL_IF_TRUNCATED=1`. A truncated page then exits with code 3. This is the safe default for CI.
- **Table output:** end with a footer line, such as `20 shown · more available (--all)`. The footer goes to `stderr`, so piped tables stay clean.

### Failure mid-`--all`

- **Array mode:** an error mid-stream leaves invalid JSON. That is the right outcome, because the parse fails instead of accepting a partial bucket. Print the error to `stderr` and exit non-zero.
- **NDJSON mode:** a cut stream still looks valid, so the exit code is the only signal.
  - Exit non-zero (code 75, see section 2).
  - Document that a consumer must check the exit status.
  - On success, optionally emit `{"_end":true,"count":N}` as the last line, behind `--ndjson-trailer`. It's opt-in because a trailer changes the "every line is an object" contract.

## 2. `logs tail --json`

`logs tail` already uses the right shape. It is unbounded, so NDJSON fits. The bug is a plain-text line in the data stream.

- **Never write non-record output to `stdout` in `--json` mode.**
- **Errors go to `stderr`.** In `--json` mode they are a JSON object:
  `{"error":{"code":"connection_lost","message":"…","retryable":true,"last_event_id":"…"}}`
- **Exit codes** let scripts tell failures apart:

  | Code | Meaning |
  |---|---|
  | 0 | Clean end (EOF, Ctrl-C). |
  | 1 | Unexpected error. |
  | 2 | Usage error. |
  | 3 | Truncated and `--fail-if-truncated` was set. |
  | 75 | Connection lost or timed out. Retryable. |
  | 77 | Authentication or permission failure. |

- **Reconnect by default**, with exponential backoff and jitter. Cap it with `--max-retries` (default 5) and `--no-reconnect`.
  - Resume from the last delivered event ID or timestamp, using the same `--since` mechanism.
  - If the server can't resume, say so on `stderr` as `gap possible`. Don't pretend the stream is complete.
- **Gap markers are opt-in.** `--include-events` emits `{"_event":"reconnected","gap":true}` lines in-band. By default `stdout` has one schema: request records only.
- Reconnect notices go to `stderr`.

## 3. `--jq`

- `--jq '<expr>'` implies `--json`. It matches gh's behavior.
- Validate the expression before any network call. A compile error exits 2.
- **Scope:**
  - Without `--ndjson`, the expression runs once over the whole document.
  - With `--ndjson` (and in `logs tail`), it runs per record, and each result prints on its own line.
  - Never silently buffer a stream to apply a filter.
- String results print raw, like gh. Other values print as compact JSON. Add `--jq-pretty` only if people ask.
- **`--jq` sees the full record.** It behaves as if `--fields all` were set.
  - Otherwise `--jq '.[].etag'` returns `null` for any field outside the default 9, and a missing field looks like an empty one.
  - Document this rule next to the flag.
- A runtime jq error exits 1 with the record number on `stderr`.
- `--jq` and `--ndjson` can combine. `--jq` and the table output cannot, and that combination is a usage error.

## 4. Fields

- **`--json` stays a bare boolean** and keeps its 9-field default. That default is a frozen contract: never remove or rename a field. Adding fields later is acceptable.
- **`--fields a,b,c`** picks specific fields.
- **`--fields all`** returns every field (all 40).
- **`--fields` with no value** lists the valid names and their types.
- Unknown field names exit 2 and list the valid ones.
- **Why not `--json=a,b` like gh?** pflag's optional-value flags (`NoOptDefVal`) don't accept the space form `--json a,b`. It would silently parse `a,b` as a positional argument.
- **Payload cost:** all 40 fields are about four times the bytes. If the API supports field selection or an `expand` parameter, pass `--fields` through to the server. If it doesn't, filter client-side and say so in the help text.

## 5. Pager

Piping through the pager always is the wrong fix. The user's real problem is the 20-row truncation, and a pager over 20 rows adds nothing. The footer and `--all` solve that problem.

Use the pager only when all of these hold:
- `stdout` is a TTY.
- The output is the human table, not `--json`, `--ndjson`, or `--jq`.
- The command is not `logs tail` or any other follow command.
- The rendered output exceeds the terminal height.
- `--no-pager` and `QS_NO_PAGER` are unset.

Details:
- Resolve the pager as `QS_PAGER`, then `PAGER`, then `less -FRX`. `-F` exits if the output fits one screen. `-R` keeps color. `-X` avoids clearing the screen.
- `--all` in a terminal streams into the pager. Table column widths can't be computed ahead of time on a huge bucket, so use fixed widths with truncation, or sample the first page.
- When the user quits the pager (broken pipe), cancel the in-flight requests and exit quietly. Never keep fetching pages into a closed pipe.
- Never page `stderr`, and set `NO_COLOR` when output is not a TTY.

## 6. Compatibility and rollout

| Release | Change |
|---|---|
| Minor | `--limit`, `--cursor`, `--all`, `--ndjson`, `--fields`, `--jq`, `--fail-if-truncated`, the `stderr` truncation notice, `logs tail` output fix with its exit codes, conditional pager. Default shapes unchanged. |
| Minor changelog | Say plainly: "`qs objects list --json` has always returned one page. Scripts that treat it as the whole bucket are wrong. Use `--all`." |
| Next major | List `--json` returns the `{items, next_cursor}` envelope. |

- The `logs tail` change is a bug fix, not a breaking change. Plain text in a JSON stream was never a contract.
- Contact the three customers with the reconciliation scripts directly. They need `--all` and a check on the exit status.

## 7. Tests to ship

- **Pagination:** a bucket of exactly 20 items (no truncation), 21 items (truncation, notice shown), and 0 items.
- **`--all` with an API failure on page 3:**
  - Array mode leaves invalid JSON and a non-zero exit.
  - NDJSON mode exits 75.
- **`logs tail`:** drop the connection mid-stream and assert that `stdout` parses line by line as JSON, with `stderr` carrying the error and exit code 75.
- **`logs tail` reconnect:** assert the stream resumes with no duplicates.
- **`--jq`:** compile error (exit 2, no network call), per-record mode, and a field outside the default 9.
- **`--fields`:** unknown field, `all`, and the bare listing.
- **Pager:** TTY vs non-TTY, `--json`, `--no-pager`, and closing the pager mid-`--all`.
- **Mutation check:** remove the truncation notice and confirm a test fails.

## Open questions for you

1. Does the API return a `next_cursor` (or an equivalent "more available" signal), and what is the maximum page size? Everything above depends on it.
2. Can `logs tail` resume from an event ID or timestamp? If not, drop the "resume" claim and keep only the gap notice.
3. Is the next major release on a date? The envelope change needs a deadline.
4. Is server-side field selection available, or only client-side filtering?