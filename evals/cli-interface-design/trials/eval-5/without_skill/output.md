# fnm 3.5 release plan

## Verdict

**Don't ship these changes as 3.5.** Most of them break existing scripts, and under SemVer that makes the release 4.0. With about 2,000 customers running scripts, a breaking minor would break their pipelines with no warning.

**Recommended split:**
- **3.5 (next month):** everything new, plus deprecations. Nothing breaks.
- **4.0 (at least 3 months later, date announced in 3.5):** removals and default flips.

If you want one release, make it 4.0 next month. That skips the deprecation window and moves the cost to customers, so I don't recommend it.

## Change-by-change

| Change | Breaking? | 3.5 (additive) | 4.0 (removal) |
|---|---|---|---|
| `--out` → `--output` | Yes | Add `--output`. Keep `--out` as a hidden alias that warns. | Remove `--out`. |
| `--proj` → `--project` | Yes | Same as above. | Remove `--proj`. |
| `--env` → `--environment` | Yes | Same as above. | Remove `--env`. |
| `FNM_PROJ` → `FNM_PROJECT` | Yes | Read both. The new one wins. Warn if only the old one is set. | Stop reading `FNM_PROJ`. |
| Delete `fnm sync-legacy` | Yes | Keep it working. Print a deprecation warning and hide it from `--help`. | Replace with a stub that exits non-zero and prints a clear message. |
| `createdAt` → `created_at` in `--json` | Yes | Emit both keys on every object. | Emit only `created_at` (the v2 schema becomes the default). |
| `datasets list --json`: array → `{items, total}` | Yes | Default stays a bare array. Add an opt-in for the new shape (see below). | The envelope becomes the default. |
| Table colors | Mostly no | Ship it, with the rules below. | — |
| Table column order | Yes, for anyone using `awk`, `cut` or `grep` on tables | Opt-in only (`FNM_TABLE_LAYOUT=v2`). | New order becomes the default. |

## Design decisions

1. **One opt-in for the future JSON shape.** Add `--json-schema-version=2` and the env var `FNM_JSON_SCHEMA=2`.
   - v2 emits `created_at` only and the `{items, total}` envelope.
   - v1 is the default in 3.x, with `createdAt` plus `created_at` and a bare array.
   - In 4.0, v2 becomes the default and `=1` stays as an escape hatch for the whole 4.x line.
2. **Emitting both date keys is additive.** Only the array-to-object change cannot coexist with the old shape, so it needs the opt-in.
3. **Deprecation warnings go to stderr only.**
   - Print each one once per run, in the same format everywhere, and never inside the JSON on stdout.
   - Add `FNM_NO_DEPRECATION_WARNINGS=1` to silence them.
   - Warn about scripts that capture with `2>&1`, because they will see the warnings.
4. **Precedence and conflicts.** The order is flag, then env var, then config. If an old and a new flag are both given with different values, exit with an error. Don't pick one silently.
5. **Colors.**
   - Color only when stdout is a TTY, and honor `NO_COLOR` and `--no-color`.
   - Never emit ANSI codes into pipes or files.
   - Color alone must not carry meaning, so statuses keep their text labels.
6. **Table contract.** State in the docs that table output is not a stable interface and that scripts should use `--json`. Say this in the 3.5 release notes. Don't rely on it alone to protect customers.
7. **Migration helper.** Add `fnm doctor --scan <dir>` to find deprecated flags, env vars, `sync-legacy` calls and `createdAt` usage in customers' scripts. A `--fix` mode for the simple renames is optional.
8. **Measure before removing.** If `fnm` has usage telemetry, count calls using the deprecated forms and `sync-legacy` before 4.0. "Nobody uses it" should be a number. If there's no telemetry, the 3.5 warnings plus a customer survey are your signal.

## Timeline

Today is 2026-10-24, and 3.5 lands in November.

| When | Work |
|---|---|
| Week 1 | Aliases, env var fallback, warnings, dual `created_at`, `--json-schema-version`, colors. Contract tests for both old and new forms. |
| Week 2 | Golden-file tests for v1 and v2 JSON on every `--json` command. `fnm doctor --scan`. Draft the migration guide and changelog. |
| Week 3 | Release candidate to 5–10 design-partner customers with real scripts. Fix what they find. |
| Week 4 | Ship 3.5. Same-day docs: migration guide, deprecation table, 4.0 date. Email all customers. |
| Month 2–3 | Monitor deprecated-form usage. Send reminders at 60 and 30 days before 4.0. |
| 4.0 (≥3 months after 3.5) | Remove the deprecated items, flip the defaults, ship the new table layout. Publish the final migration guide. |

## Test gates for 3.5

- Every old flag, env var and JSON key still works, with a warning.
- Every new flag, env var and key works with no warning.
- v1 and v2 JSON are checked against golden files for each `--json` command.
- Exit codes are unchanged.
- No warning text ever lands on stdout.
- No ANSI codes appear when piped or when `NO_COLOR` is set.
- Run a set of real customer-style scripts unchanged against 3.5, then against 3.4.1, and compare the output.

## Open questions

1. Is table output documented as a stable interface anywhere? If it is, the column reorder waits for 4.0 regardless.
2. What replaces `sync-legacy`? The warning and the 4.0 error should name the replacement.
3. Is there usage telemetry, or will warnings and a survey be your only signal?
4. Does `--output` collide with anything existing, such as an `-o` short flag or an `--output <format>` meaning? Does `FNM_ENV` exist and need a rename too?
5. Do other commands return bare arrays? If so, decide now whether they get the envelope in v2 too, so you only break once.
6. Is a 3-month minimum before 4.0 acceptable? Six months is safer for customers with slow-moving CI.