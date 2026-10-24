# Quarrystone `qs` list and streaming design (spec v0.1)

**Next action:** reject the `--all` → one-JSON-per-line change, and ship the 1.x plan in section 7.

## Verdicts

| Request | Verdict | Replacement |
|---|---|---|
| `--all` switches output to NDJSON | ❌ Reject | `--all` only paginates. NDJSON is `--format ndjson`. |
| Pipe `objects list` through the pager always | ❌ Reject | Pager on a TTY only, when output exceeds the screen. It does not fix truncation. |
| `logs tail --json`: plain-text "connection lost", exit 1 | ❌ Bug | Reconnect, then a JSON `error` line, text to stderr, exit 5. |
| `--jq` | ⏳ Defer | Ship after the envelope and field selection are frozen (v2.1). External `jq` works now. |
| `--json` with all 40 fields | ✅ Accept | `--json all`. Bare `--json` stays at the 9 default fields. |

Why `--all` as NDJSON is wrong:
- One flag would change the output format. `qs objects list --json --all | jq '.data[]'` breaks on the same command that worked without `--all`.
- Streaming NDJSON must be an explicit format flag, never a side effect of `--all`. The stream rule in `cli-interface-design` step 5 says this.
- The real bug is silent truncation. `--all` as NDJSON does not signal it.

## Assumptions

I could not ask. Each assumption says what it changes.

| Question | Assumption | If wrong |
|---|---|---|
| Today's `objects list --json` shape | Bare array of 20 | If it is the API's `{objects, next}` object, the 2.0 flip is smaller. |
| API cursor | Opaque `next_cursor`, key-ordered, supports `limit` up to a max | Without a cursor, `--all` cannot ship. Blocks everything below. |
| API `since` or cursor on the log stream | Exists | Without it, reconnect leaves gaps. Emit a `gap` line (section 4). |
| Request-log objects have no top-level `type` field | True | If one exists, nest items under `data` from the start. A contract test checks this. |
| Audience | CI scripts (reconciliation) and humans, plus agents | Scripts break the business. Table polish ranks last. |

## 1. List contract

Flags on `qs objects list`:

| Flag | Meaning | Default and reason |
|---|---|---|
| `--limit N` | Return at most N objects. Fetches several pages if N exceeds the API page size. | 20. It equals today's behavior. Changing it silently alters what existing scripts reconcile. |
| `--all` | Follow `next_cursor` until exhausted. Pagination only. | Off. |
| `--cursor C` | Resume from a cursor. | None. |
| `--json [fields\|all]` | One JSON document. | Bare gives the 9 default fields, frozen. |
| `--format ndjson` | Streaming lines (section 2). Mutually exclusive with `--json`, exit 2. | Off. |
| `--no-pager` | Disable the pager. | Pager auto on a TTY (section 5). |

- `--limit` and `--all` together exit 2.
- Both flags take field selection: `--json key,size,etag`, or `--format ndjson --fields key,size`.
- `all` returns the API's full objects (40 fields). Its field set grows additively, so the `all` set is not frozen. Scripts that need stability name their fields.
- Envelope, in every `--json` list:

```json
{"data":[{"key":"a/b.png","size":123}],"has_more":true,"next_cursor":"c_42"}
```

- `--json --all` returns one envelope with `has_more:false` and `next_cursor:null`. It buffers in memory. For very large buckets use `--format ndjson`: size the buffer as objects × bytes per object.
- Empty result: `{"data":[],"has_more":false,"next_cursor":null}`. Human mode prints "0 objects found".
- Listing a bucket with concurrent writes is not a snapshot. Objects added or deleted mid-listing can be missed or seen. Document this on the reconcile page.

## 2. NDJSON list stream (`--format ndjson`, new)

One line per record, each with a `type`:

```
{"type":"item","key":"a/b.png","size":123}
{"type":"item","key":"a/c.png","size":456}
{"type":"end","count":2,"has_more":false,"next_cursor":null}
```

- The `end` line is the completeness proof. A stream with no `end` line is incomplete. Reconcile scripts must check it.
- With `--limit N`, `end` carries `has_more:true` and a `next_cursor`.
- Failure mid-stream ends with an `error` line, then a non-zero exit:

```
{"type":"error","error":{"code":"stream_disconnected","message":"Connection lost after 41200 objects.","request_id":"req_8f2a","retry":"safe","fetched":41200,"next_cursor":"c_9931","hint":"Resume: qs objects list --format ndjson --all --cursor c_9931"}}
```

- Exit code is 5 (safe to rerun). The command is read-only.
- Retry on 429 and 503 with bounded backoff, honoring `Retry-After`. Default 5 attempts, with jittered backoff capped at 30 s. Honoring `Retry-After` keeps it polite. After the cap, emit the `error` line above.
- Request the API's maximum page size for `--all`. Fewer round trips.
- In human mode with a pager, quitting the pager (SIGPIPE) stops pagination. This saves API calls.

## 3. `--jq` (deferred to v2.1)

Why defer: step 5 says offer an in-CLI filter only after `--json` is stable. It is not stable until the envelope and the `all` and field-selection contract ship and have schemas.

Rules when it ships:
- `--jq` implies `--json`. The filter sees the envelope, so a script writes `.data[].key`. This differs from GitHub's bare-array shape.
- `--jq` with bare or no field list evaluates against `all`. Otherwise `--json --jq '.data[].etag'` silently returns `null` for a field outside the default 9. An explicit field list restricts the document, and the docs say so.
- Strings print raw. Everything else prints as JSON.
- Errors bypass the filter. The standard `{"error":{...}}` document is emitted, with the exit code.
- `--jq` with `--format ndjson` exits 2. Use external `jq -c`.
- Pin the dialect (gojq) and document it.
- Contract test: `--jq` on a field outside the selection must fail, not print `null`.

Until then, customers use `qs objects list --json --all | jq '.data[]'`.

## 4. `logs tail` streaming

| Case | Behavior |
|---|---|
| Stream | `qs logs tail --format ndjson`. Request lines gain `"type":"event"` (additive). Other fields unchanged. |
| `--json` on `tail` | Deprecated synonym for `--format ndjson`. It warns on stderr, names the replacement, and stays through the window: 12 months or 2 releases, whichever is longer. It is removed only in a major. Existing parsers keep working. |
| Connection drops | Auto-reconnect with bounded backoff, resuming from the last event cursor. Emit `{"type":"progress","state":"reconnecting","attempt":2}` on stdout. Text goes to stderr. |
| Reconnect cannot replay | Emit `{"type":"gap","from":"<ts>","to":"<ts>"}`. A lossy stream says so. |
| Retries exhausted | Last stdout line is `{"type":"error","error":{"code":"stream_disconnected","retry":"safe","last_event_id":"...","hint":"Resume: qs logs tail --since <ts>"}}`. Exit 5. "connection lost" text goes to stderr only. |
| Idle | Client read timeout, so a half-open connection is detected and not hung. It needs server heartbeats (see dependencies). |
| Auth expired mid-stream | `error` line with the auth code, exit 4. |
| Ctrl-C or SIGTERM | `{"type":"end","reason":"interrupted"}`, exit 130 or 143. |
| Clean end (`--duration`, `--max`) | `end` line, exit 0. |

Consumers filter on `type == "event"`.

Exit 5 and not 1: tail is read-only and the failure is transient, so rerunning is safe. Exit 1 is the "read the error" bucket.

## 5. Pager

- Page only when all hold: stdout is a TTY, `TERM` is not `dumb`, output exceeds the terminal height, and the mode is human.
- Never page `--json`, `--format ndjson`, `logs tail`, or piped output.
- Resolve the pager from `QS_PAGER`, then `PAGER`, then `less -FRX`. `-F` quits when output fits one screen. `--no-pager` and a config key disable it.
- If the pager fails to start, print directly.
- A pager does not fix truncation. After the pager closes, print this footer on stderr:

```
20 objects shown, more available. Use --all, or --all --format ndjson to stream, or --cursor c_42.
```

- The pager (display) and `--limit`/`--all` (API pagination) stay separate flags.

## 6. Exit codes touched

| Code | Meaning | Caller action |
|---|---|---|
| 0 | Success. Truncated lists still exit 0. | Check `has_more`. |
| 2 | Usage error: `--json` with `--format ndjson`, `--limit` with `--all`, `--jq` with ndjson | Fix the invocation. |
| 4 | Auth required or expired, including mid-stream | Re-authenticate. |
| 5 | Safe to rerun: stream drop, 429, 503 | Resume with `--cursor` or `--since`. |
| 130, 143 | Interrupted | Resume or stop. |

Each code needs an automated test.

## 7. Release plan

The `--json` shape of a shipped command is a frozen contract. Adding fields is safe. Changing bare array to envelope is breaking.

| Release | Ships |
|---|---|
| 1.x minor (additive only) | `--all`, `--cursor`, `--format ndjson` for list and tail, `--json all` and field selection, `type` on tail lines, `error` line on drop, exit 5, pager rules, `--json` on `tail` marked deprecated. `--json` on `objects list` prints a stderr warning when `has_more` is true. Opt-in envelope: `QS_JSON_ENVELOPE=1`. Bare array stays the default. `--json --all` returns one array of everything. |
| 2.0 | Envelope becomes the default. `QS_JSON_ENVELOPE=0` restores the bare array for 12 months or 2 releases. |
| 2.1 | `--jq`. |
| 3.0 | Remove the bare-array escape and the `--json` synonym on `tail`. |

Customer action, the 3 reconcile customers: tell them to add `--all`, or `--format ndjson` and check for the `end` line. That fixes them today, before 2.0.

## 8. Tests (gates)

1. Contract coverage: JSON Schema for the list envelope, each NDJSON line type, and the error document. Run golden tests against the test environment.
2. Kill the connection mid-stream (list and tail). Assert the last stdout line is `error`, stderr has the text, the exit code is 5, and there is no `end` line.
3. `--json --all` equals the concatenated `ndjson` items, including on a bucket larger than one page.
4. Piped stdout never pages (pty test). The pager quits on one screen. Quitting the pager stops pagination.
5. Mutual-exclusion flags exit 2 before any API call.

## API-side dependencies

| Need | Blocks |
|---|---|
| Stable opaque `next_cursor` and a documented max page size | `--all`, `--cursor`, all list streaming |
| `since` or cursor on the log stream | Gapless tail reconnect |
| Server heartbeat on the log stream | Idle detection |
| No top-level `type` field in log or object schemas (or nest under `data`) | NDJSON line shape |

## Open items

| Decision | Owner | Due |
|---|---|---|
| Confirm today's `objects list --json` shape | Eng | Before 1.x branch |
| Confirm cursor and `since` support | API team | Before 1.x branch |
| 2.0 date and customer notice | Product | Before 1.x release notes |

**Next:** confirm the cursor and `since` support with the API team. That is a 15-minute question, and it blocks `--all` and the tail reconnect.