Start here: ship `Idempotency-Key` in the CLI. The exit codes matter less than that. The bug is that a timeout looks the same as a failure, and the retry guidance tells scripts to resend a non-idempotent POST.

# What went wrong

1. The LB timed out at 60s. The API may still have created the import. The CLI cannot know.
2. The CLI exited 1, the same code as "bad flag". The script could not tell "definitely failed" from "outcome unknown".
3. The script retried 3 times without an idempotency key, so the API created 4 imports.
4. The proposed rule "retry on any 5xx" would repeat this exactly. A 504 on `POST /imports` is the incident.

Immediate: credit the customer for 3 imports. Separately, ask the API team whether `imports create` can return 202 plus an id under 60s. The 60s timeout is the real trigger.

# Verdict on the team proposal

- **Adopt sysexits numbers (64–78) as the base.** They sit clear of shell codes (126, 127, 128+n) and Go's panic code (2).
- **Reject sysexits meanings as the retry contract.**
  - `EX_TEMPFAIL 75` means "try again later". It cannot separate "not processed, retry freely" from "maybe processed, retry only with the same key".
  - So add one code outside sysexits for unknown outcome (80).
- **Reject 255 for internal errors.**
  - It is `exit(-1)`, and ssh uses it.
  - Use `EX_SOFTWARE 70`, and recover panics into 70.
  - Go's default panic exit is 2, so 2 must never leak.
- **Reject "retry any 5xx".** Retry safety depends on whether the request was provably not applied, not on the status class.

# Exit-code table (2.0)

The primary property of each code is its retry class:
- **safe**: nothing was applied. Rerun as is.
- **key**: the outcome is unknown. Rerun only with the same idempotency key.
- **never**: rerun changes nothing until a human acts.

| Code | Name | Meaning | Retry |
|---|---|---|---|
| 0 | OK | All work succeeded. For bulk: every item succeeded. | n/a |
| 1 | FAILURE | Unclassified failure. Kept for compatibility. | never |
| 64 | EX_USAGE | Bad flags or args. Also idempotency key reused with a different payload (API 422 `idempotency_mismatch`). | never |
| 65 | EX_DATAERR | API rejected the content (400, 413, 422 validation), for example a malformed CSV. | never |
| 66 | EX_NOINPUT | Local file missing or unreadable, or the API returned 404 for a named resource. | never |
| 69 | EX_UNAVAILABLE | Service permanently unusable for this request (501, 505, endpoint sunset). | never |
| 70 | EX_SOFTWARE | Bug in the CLI. Includes recovered panics. Replaces 255. | never |
| 74 | EX_IOERR | Local I/O failure mid-read. | never until the host is fixed |
| 75 | EX_TEMPFAIL | Provably not applied: 429, 408, 409 key-in-flight, API-envelope 503, DNS, connect-refused or TLS failure before any byte was sent. | safe, honor `Retry-After` |
| 77 | EX_NOPERM | 401, 403, 402 or plan limit. | never |
| 78 | EX_CONFIG | Local config invalid or no API key. | never |
| 80 | OUTCOME_UNKNOWN | Request was sent, result not seen. Timeout or reset after send, 502, 504, 500 or non-envelope 5xx on a mutating command. Also SIGINT or SIGTERM mid-request (the exit stays 130 or 143, with the same stderr hint). | key |
| 81 | BATCH_MIXED | Bulk only. Some items succeeded and some failed, or the failures belong to different classes. | key, see below |

Rules:
- **Reads (GET):** every 5xx or timeout maps to 75, because retrying a read is harmless.
- **Mutating commands:** 500, 502, 504 and any 5xx without the API's JSON error envelope map to 80. The envelope proves the API itself answered. An LB-generated 503 has no envelope, so it is 80, not 75.
- **Reserved:** 2, 126, 127 and 128+n are never emitted by the CLI, except 130 and 143 above.
- **Contract:** the table is semver-protected. Add `pld help exit-codes` and a golden test that fails if any code changes.

Every failure also prints one stderr line, and `--output json` carries the same fields:

```
error: outcome unknown (timeout after 60s). Retry with: pld imports create --file nightly.csv --idempotency-key 7f3c...
{"exit_code":80,"retry":"key","idempotency_key":"7f3c...","request_id":"..."}
```

# CLI behavior changes

1. **Always send `Idempotency-Key`** on every mutating call.
   - The default is a random UUID per invocation. It covers the CLI's own internal retries.
   - Add `--idempotency-key` and the `PLD_IDEMPOTENCY_KEY` env var for caller-controlled keys.
2. **Resume after exit 80 (recommended).**
   - Store the key only on exit 80, in a state file keyed by `(account, command, file sha256)`.
   - The next identical invocation reuses that key, and the state is cleared on any definitive result.
   - This fixes the customer's script with no script change.
   - It is not stored on success, so a legitimate rerun of the same nightly file is never deduplicated.
   - It falls back to a random key if the state dir is not writable (ephemeral CI). Add `--no-resume` to opt out.
3. **Keep the CLI's internal retries to the safe class** (75, with a small cap). Surface 80 to the caller; do not hide it in loops.
4. **API team:** the key TTL must exceed the longest sane retry horizon, so ask for 24h. The same key with a different body must return 422.

# Retry guidance for script authors

1. Retry only on 75 and 80. Never retry on 1, 64, 65, 66, 69, 70, 74, 77, 78.
2. Create one key per logical job, outside the retry loop. Use a stable business identifier such as `nightly-2026-10-24`. Never reuse a key for a different payload.
3. Use exponential backoff with jitter: 2s base, 60s cap, 5 attempts max, plus an overall deadline. Honor `Retry-After` when printed.
4. On exhausted retries after 80, alert a human. Do not start a new job under a new key.

```bash
key="nightly-$(date +%F)"
for attempt in 1 2 3 4 5; do
  pld imports create --file nightly.csv --idempotency-key "$key"
  rc=$?
  case $rc in
    0) exit 0 ;;
    75|80) sleep $(( (2 ** attempt) + RANDOM % 3 )) ;;
    *) exit $rc ;;
  esac
done
exit 80
```

# `bulk-create` (up to 200 files)

"0 if at least one succeeded" hides failures, and a script cannot tell which files to redo. New contract:

- **Exit 0** only if all items succeeded.
- **Exit 81** on mixed results.
- **Exit the shared code** if every failure has the same class and none succeeded.
- **Per-file keys:** each file's key is `hash(batch-key, file sha256)`. A rerun with the same `--idempotency-key` replays the files that succeeded and retries only the failed ones. That is why 81 is retry class "key".
- **Report:** `--output json` writes one NDJSON line per file.
  - Fields: `path`, `status`, `import_id`, `exit_code`, `retry`, `idempotency_key`, `error`.
  - A script retries when no line has `retry:"never"`. Otherwise it alerts, because rerunning cannot fix those files.
- **Batch key:** auto-generate it and print it if the caller gives none, so exit 81 is always actionable.
- **Resume:** the exit-80 resume from the CLI section stores the batch key in the same way.

# Migration notes for 2.0

- **Breaking:** scripts that tested `$? -eq 1` for any failure now see 64–81. Plain `set -e` and `|| fail` still work, because every failure is nonzero.
- **Breaking:** `bulk-create` no longer returns 0 on partial success. Put this in the changelog and the upgrade guide.
- **Docs:** publish the retry-class column as the headline of the exit-code page, with the bash loop above.

# Open decisions for you

1. Ship the exit-80 resume state file in 2.0, or only `--idempotency-key`? I recommend shipping it.
2. Is 401 vs 403 distinction needed? I merged them into 77. Split only if scripts need to alert on expired credentials separately.

Next: send the API team the 24h key TTL, 422 mismatch and 202-fast-return asks (about 10 minutes).