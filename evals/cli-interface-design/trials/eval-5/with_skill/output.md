# Fennimore `fnm` 3.5 release plan

I read `cli-interface-design/SKILL.md`, its spec template and its output and exit-code contract. I did not read the other three reference files: command-layer patterns, auth, and agent-readiness. They don't bear on this change. Nothing was run, and I had no access to the `fnm` code, the docs or usage data.

## Answer

You can't ship the full cleanup as a 3.5 minor under SemVer. Only the table restyle can go out as-is.

In `cli-interface-design` step 3, flag names, env var names, command names and `--json` shapes are frozen. Human tables are the only unstable surface. Renaming, retyping or removing a frozen element is breaking, and the skill says to ship such changes only in a major release.

With about 2,000 customers running scripts, 3.5 should add the new names next to the old ones and warn. 4.0 removes the old ones.

| Change | In 3.5 | In 4.0 |
|---|---|---|
| `--out` → `--output`, `--proj` → `--project`, `--env` → `--environment` | New flags work. Old flags stay as aliases and warn on stderr. | Remove the aliases. |
| `FNM_PROJ` → `FNM_PROJECT` | `FNM_PROJECT` works. `FNM_PROJ` is still read and warns on stderr. | Stop reading `FNM_PROJ`. |
| Delete `fnm sync-legacy` | Command still works. It is hidden from help and warns on stderr. | Delete it. |
| `createdAt` → `created_at` in `--json` | Both fields are emitted, and the schema documents both. | Drop `createdAt`. |
| `datasets list --json` bare array → object with items and total | Opt-in through `--json-version 2` or `FNM_JSON_VERSION=2`. Default stays a bare array. | Make v2 the default. |
| Table colors and new column order | Ship it, with the care described below. | No change. |

## Assumptions

I couldn't ask the eight clarifying questions, so these are assumptions. If one is wrong, tell me and I'll rework the plan.

| Question | Assumption | What it changes |
|---|---|---|
| Who runs `fnm` | CI pipelines are the main users (the 2,000 customers have scripts). | They break first, so deprecations must be loud on stderr and quiet on stdout. |
| Existing contract | "Tables are unstable" has never been published. | If it was published, drop the non-TTY caveat in the table section. |
| Telemetry | None is installed. | You can't measure deprecated-flag usage, so removal is gated on time and releases, not on usage. |
| Release cadence | Minor releases roughly monthly. | Two releases pass in about two months, so the 12-month floor decides when 4.0 can ship. |
| Other lists | Other list commands may also return bare arrays. | See Open items. |
| `--output` | It isn't already used for something else, such as format. | If it is, the rename collides and needs a different name. |
| `--out` meaning | It means a file path. | It matters for the `--output` collision check above. |

## Contract changes in detail

### Flags and env var

- Both spellings are accepted. If both are given with different values, exit 2 and name the conflict.
- Precedence is unchanged: flag > env > project config > user config > default. `FNM_PROJECT` beats `FNM_PROJ` when both are set.
- The warning goes to stderr, never stdout. Example: `warning: --proj is deprecated, use --project. Removal no earlier than 4.0.`
- Warn on every use, not once a day. Flags in scripts are definitely in use, and stderr doesn't break parsing.
- `--help`, shell completion and examples show only the new names. Old flags are hidden but still work.
- Audit config-file keys. If a config key `proj` or `env` exists, it is frozen too. Add `project` and `environment` as aliases the same way.
- Audit the wrappers: the GitHub Action, any IDE extension, and `fnm api` defaults. They inherit these flags.

### `fnm sync-legacy`

- Keep it working in 3.5. Its output and exit codes are frozen like any command.
- It warns on stderr and disappears from help.
- Delete it in 4.0 only. "Nobody should use it" is a belief, not a measurement. Without telemetry, the only evidence is that nobody complains during the window.
- Don't turn telemetry on in a minor release to find out. The skill rules that out (step 11).

### `createdAt` → `created_at`

- Emit both keys in v1 output. Adding a field is safe, and the values stay identical (RFC 3339 UTC).
- Field selection accepts both, so `--json id,createdAt` keeps working.
- Add `created_at` to the published JSON Schema and mark `createdAt` deprecated.
- A script reading the field can't be detected, so there is no runtime warning. Announce it in the release notes, the docs and the schema.
- In `--json-version 2`, emit only `created_at`.

### `datasets list --json`

- A bare array can't become an object in place. That breaks every `jq '.[]'` script.
- Opt-in v2 shape:

  ```json
  {"data": [{"id": "ds_1", "created_at": "2026-11-02T09:00:00Z"}], "total": 42, "has_more": true, "next_cursor": "c_42"}
  ```

- `total` is what you asked for. `has_more` and `next_cursor` make truncation visible to scripts and agents (skill step 7). Without them a script reads the first page as the full list.
- Give the list a bounded default `--limit` and an explicit `--all`. Pick the number and write down why.
- In v1 mode, print one stderr line telling scripts that the shape changes in 4.0 and how to opt in. The shape change affects every caller, so a warning is justified here.
- One switch, `--json-version 2` or `FNM_JSON_VERSION=2`, lets customers migrate every `--json` command at once. It is new frozen surface, so add it deliberately. Reject any value other than 1 or 2 with exit 2.
- If you'd rather not add a global switch, the fallback is a per-command `--envelope` flag. That is cheaper now but needs more flags later.

### Table restyle

- Tables are the unstable surface, so you may restyle them in a minor release.
- Colors only on a TTY. Honor `NO_COLOR`, `--no-color` and `TERM=dumb`. Off when piped unless `FORCE_COLOR` is set.
- The new column order is the real risk. If tables were never declared unstable, some of the 2,000 scripts probably parse them with `awk` or `cut`. Apply the new order on a TTY only. Keep the old order when stdout is piped until 4.0. This costs one TTY check.
- Add the "tables are unstable, parse `--json`" statement to the docs in 3.5.

## Timeline

1. **3.5, next month.** Ship all of the above. Update the docs the same day, as you planned. The release notes list every deprecation with its replacement.
2. **3.6 and 3.7.** Fix anything customers report. Nothing is removed.
3. **4.0, no earlier than about November 2027.** The skill's default is 12 months or 2 releases, whichever is longer. Then:
   - remove the aliases, `FNM_PROJ` and `sync-legacy`;
   - drop `createdAt`;
   - make the v2 JSON shape the default;
   - ship a migration guide with a one-line `sed` or `jq` recipe per rename.

   Don't promise a date in the 3.5 warnings. Say "no earlier than 4.0".

## Tests required before release

- Golden-output contract tests for v1: the output differs from 3.4.1 only by the added `created_at`.
- Alias tests for each flag, the env var and each config key: both spellings work, a conflict gives exit 2, and the warning is on stderr only.
- Under `--json`, stdout is exactly one JSON document, with or without a deprecation warning.
- JSON Schema for the v1 and v2 shapes, with v2 checked against `datasets list`.
- Piped table output keeps the old column order.
- Exit codes are unchanged. Re-run the existing exit-code tests.

## Open items

| Decision | Owner | Due |
|---|---|---|
| Opt-in switch: global `--json-version` (recommended) or per-command `--envelope` | CLI lead | before 3.5 freeze |
| Do other list commands also move to the envelope in v2? Recommended: yes, all at once, so there is one migration. | CLI lead | before 3.5 freeze |
| Default `--limit` value for lists, with the reason | CLI lead | before 3.5 freeze |
| Confirm `--output` doesn't already exist or collide | CLI lead | start of work |
| Confirm no config keys or wrappers use the old names | CLI lead | start of work |
| Was "tables are unstable" ever published? This decides the non-TTY table rule. | Docs owner | before 3.5 freeze |
| Does `sync-legacy` mutate state? If so, grade it in the severity table. | CLI lead | before 3.5 freeze |

## Gates

The skill's five gates are untouched by this change:

- [ ] Contract coverage: the JSON Schemas above exist, and the frozen list is updated with the deprecations.
- [ ] Non-interactive run: warnings never prompt.
- [ ] Exit-code table tested.
- [ ] Severe-action guard: unchanged.
- [ ] Secret hygiene: unchanged.