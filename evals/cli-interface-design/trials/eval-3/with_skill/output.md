# `pld` 2.0 exit codes and retry guidance

I made these assumptions because I couldn't ask first. If any is wrong, the affected rows change.

| Question | Assumption | What it changes |
|---|---|---|
| Who runs `pld` | CI and cron scripts are the audience that breaks the business, since the nightly script is the incident | The table is designed for scripts. Exit codes are frozen API. |
| Does `imports create` wait for the import? | It is a synchronous upload today, so the load balancer's 60s cut hits it | The API-side dependency below, an async 202, is the real fix for the timeout. |
| Idempotency | The API accepts `Idempotency-Key` and keeps keys for a window of 24h or more | The "safe to rerun" rules below depend on this. |
| Existing scripts | Some test `$? -eq 1` or `$? -eq 0` on bulk | These are breaking changes. They ship in 2.0 with a migration note. |

## What caused the four imports

1. The load balancer returned a 504 at 60s, but the import was probably already running or created.
2. The CLI collapsed that into exit 1, the same code as "bad flag" or "file not found". The script could not tell "retry" from "stop".
3. The script retried three times without an idempotency key. Each retry was a new create, so four imports were billed.

The team proposal would make this worse:

- **"Retry on any 5xx" is the bug.** A 5xx after the request was sent means the outcome is unknown, so a blind retry duplicates the create. Only "nothing reached the server" and "the server refused with 429, or 503 plus `Retry-After`" are safe to rerun.
- **sysexits.h is not a safe standard to adopt.**
  - It is not widely known. Few CLIs use it, and current FreeBSD documentation marks it deprecated.
  - It has no code for "outcome unknown" or "partial failure", and those are the two classes this incident needs.
  - `EX_TEMPFAIL` (75) would merge "safe to rerun" with "outcome unknown". That merge is exactly what the proposal's retry rule already does.
  - A script author must learn our own table anyway. A small table where each code means a different caller action beats a famous table that maps badly onto HTTP.
- **255 is the wrong code for internal errors.** The range above 125 is shell-reserved (126, 127, 128+N). AWS CLI v2 ships 252–255, and scripts testing `$? -gt 128` misread those as signals. Fatal CLI bugs use `1` with `error.code: "internal_error"` and the request ID. A server 500 is a separate case and maps to 6 (see the mapping below).

## Exit-code table (frozen from 2.0)

| Code | Meaning | Caller action |
|---|---|---|
| 0 | Success, including an idempotent replay that returned the original result | continue |
| 1 | Failure not covered below: 4xx validation, conflict, quota, `idempotency_key_reused`, CLI bug | stop, read the error. Never retry. |
| 2 | Usage error: unknown flag, missing argument, more than 200 files in `bulk-create` | fix the invocation. Never retry. |
| 3 | Not found | branch |
| 4 | Authentication required, or token expired | re-authenticate |
| 5 | Safe to rerun: nothing reached the server, 429, 503 with `Retry-After`, or any failure when you supplied your own `--idempotency-key` | rerun the same command with backoff |
| 6 | Outcome unknown: timeout, connection lost after sending, or 500/502/503/504 without your own key | do not rerun blind. Check with `pld imports get/list`, or `wait <operation-id>`. |
| 7 | Partial failure in a bulk operation | read the per-item results |
| 8 | Permission denied (403: authenticated but not allowed) | stop. Re-login won't help. Change the token's scope or role. |
| 130 / 143 | Interrupted by SIGINT / SIGTERM. The CLI detaches and prints the operation ID and resume command. | resume or stop |

I added code 8 to the template's 0–7. A 403 needs a different action from code 4, because re-authenticating cannot fix it.

### HTTP and transport mapping

| Observed | Exit |
|---|---|
| DNS, connect or TLS failure before sending | 5 |
| 429; 503 with `Retry-After` | 5 |
| 401 | 4 |
| 403 | 8 |
| 404 | 3 |
| Other 4xx | 1 |
| 500, 502, 504, 503 without `Retry-After`, timeout after sending (the incident's 504 falls here) | 6 |
| Any retryable failure when the caller passed `--idempotency-key` or `PLD_IDEMPOTENCY_KEY` | 5 |
| Wait timeout on an accepted operation | 6, with the operation ID in the output |

A key the CLI generates itself does not move 6 to 5. A script that reruns the whole command gets a new generated key, so the server cannot deduplicate it.

### Changes from 1.x

- Generic `1` is now split into 2–8. Scripts testing `-ne 0` keep working. Scripts testing `-eq 1` break.
- The bulk-create exit code changes (see below).
- Document this in the 2.0 migration guide.
- Publish the table as `pld help exit-codes`, and add one automated test per code. The `imports create` timeout path needs a test that asserts exit 6 against a stub that returns 504 after the request body is read.

## Idempotency in the CLI

1. Send one `Idempotency-Key` on every create. Generate it once per invocation, and reuse it on the CLI's own automatic retries.
2. Accept `--idempotency-key` and `PLD_IDEMPOTENCY_KEY` so scripts can supply a stable key.
3. On exit 5 or 6 without a caller key, print the generated key in the error. `--json` mode carries it in the error object (`"idempotency_key"`, `"retry": "resume"`). The hint reads: "Rerun with `--idempotency-key <key>` to retry safely."
4. Retry automatically inside one invocation: up to 3 attempts, 1s/2s/4s backoff with jitter, honoring `Retry-After`. The key makes this safe even for 5xx. Three attempts keeps total added delay under about 10s, short enough for cron.
5. Set the client request timeout above the load balancer's 60s only if the API stays synchronous. Otherwise use the async fix below.

## Retry guidance for script authors

Replace "retry on 5xx" with this:

1. **Read the exit code, not the HTTP status.**
   - 0: done.
   - 1, 2, 3, 4, 8: stop and alert. Retrying changes nothing.
   - 5: rerun with backoff.
   - 6: never rerun a create without your own key. Check first with `pld imports list --json` or `pld wait <operation-id>`.
   - 7: read the per-item results.
2. **Pass your own stable key on every create in a script.** Derive it from what makes the job unique, so any rerun of the same logical job is deduplicated:

```sh
key="nightly-$(date -u +%F)-$(sha256sum nightly.csv | cut -c1-16)"
for attempt in 1 2 3; do
  pld imports create --file nightly.csv --idempotency-key "$key" --json > out.json
  rc=$?
  case $rc in
    0)   break ;;
    5|6) sleep $((attempt * 30)) ;;   # safe: the key deduplicates
    *)   exit $rc ;;
  esac
done
```

3. **Use a new key for a new job.** Reusing a key with a different payload returns `idempotency_key_reused` (exit 1). That is a script bug, not a transient fault.
4. **Don't retry past the key retention window.** Document it, for example "24h", and keep it at least as long as the longest plausible retry horizon.

## `imports bulk-create`

The current "0 if at least one succeeded" rule hides failures from every script that checks only `$?`.

- **All files accepted:** exit 0.
- **Any item failed or has unknown outcome:** exit 7. This is a breaking change from 0, announced in the 2.0 migration guide.
- **Whole run aborted before any item was sent** (usage error, 401, 403, more than 200 files, pre-flight validation): the matching code from the table, with no per-item results.
- **Output:** `--json` returns `{"data": [...], "errors": [...]}`. Each item records its file, status (`created`, `failed`, `unknown`), an error code, and its own `retry` class (`safe`, `resume`, `never`).
- **Keys:** derive each item's key from the base key plus a hash of the file, `<base>:<sha256(file)>`. A rerun of the whole command with the same base key then recreates nothing that already exists. Without a caller key, print the base key on exit 7.
- **Confirmation:** bulk creates confirm the count: `--confirm-count=<n>`, and `--yes` does not skip it. Imports are billed, and a mistaken count costs money.
- **Exit 7 caller action:** rerun with the same base key, and only the failed or unknown files are attempted again.

## API-side dependencies

| Need | Owner | Blocks |
|---|---|---|
| Make `imports create` async: return 202 with an operation ID within a few seconds, and process the import after the request ends | API team | Removes the load-balancer timeout entirely. The CLI default then becomes `--wait` with a bounded `--wait-timeout`. |
| Key store: retention of at least 24h, same key plus same payload returns the original response, same key plus different payload returns a documented error, same key while still in flight returns 409 | API team | Exit 5 on caller-supplied keys. Reject any retry rule that assumes this before it exists. |
| `Retry-After` on every 429 and deliberate 503 | API / LB team | The mapping to exit 5 |
| Operation status endpoint, and filtering imports by key | API team | `wait`, and the "check before rerun" step for exit 6 |

## Open items

| Decision | Owner |
|---|---|
| Key retention window length | API team |
| Whether the async `imports create` ships before the CLI 2.0 date | API team |
| Refund or credit handling for the four existing duplicate imports | Billing / support, outside this spec |

## Gates

- Exit-code table: one automated test per code, as above.
- Non-interactive run: still to be verified, for `bulk-create --confirm-count` with stdin closed.
- Secret hygiene: untouched. The idempotency key is not a secret, so printing it is fine.
- Contract coverage and severe-action guard: not reviewed here. This answer covers only exit codes, retries and bulk behavior.