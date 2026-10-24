**Verdict: don't merge yet.** The `description` is a blocker. The rest are fixes or things to verify. I reviewed only the text you pasted, so I haven't checked the flags against the real CLI.

## Blockers

1. **`description: Helps with qn.` won't trigger.** Agents pick skills from this line alone. It needs what the skill does and when to use it, with trigger phrases (deploy, roll back, check status, environment, region).
2. **`allowed-tools: Bash` grants every shell command.** The skill only needs `qn`, so scope it to `Bash(qn:*)`. A skill that can deploy and roll back shouldn't carry blanket shell access.
3. **Risky flags have no guardrails.** `--force`, `--no-verify` and `--legacy-auth` skip safety checks, and `qn deploy` and `qn rollback` have side effects. Add rules such as:
   - Never pass these flags unless the user asks for them.
   - Confirm the target `--env` before deploying.
   - Run `rollback --dry-run` first.

## Fixes

4. **The version info is inconsistent.** `version: 2.3` looks like the CLI version but is probably the skill's version. Move it to `metadata:` and label it, e.g. `metadata: {version: "1.0.0"}`. The body says "2.3.x", but `compatibility` says `>= 2.3.0`, so qn 2.4 passes one rule and fails the other. Pick one rule. I'd use `>= 2.3.0` in both places and drop "older → upgrade" in favor of "older than 2.3.0 → stop".
5. **`references/flags.md` is never linked from the body.** Agents only load it if the body tells them to. Add something like "Read `references/flags.md` for flag values and defaults." Also generate that table from `qn --help` at release time, or it will drift from the CLI.
6. **The commands section is a bare flag list.** Add these:
   - What each flag takes (`--timeout` takes a duration, `--to` takes a revision).
   - The required positional arguments.
   - What success and failure look like (exit codes, `--json` output shape).
   - Workflow order, such as `status --json` before and after a deploy.
7. **`Our repo is Apache-2.0..` is in the wrong place and has a typo.** Put it in frontmatter as `license: Apache-2.0`. Don't put it in the body, where it wastes agent context.
8. **Line 9 ("We also keep a copy…") is written for humans.** Write skill text as imperatives for the agent, which also fixes item 5.

## Suggested head

```markdown
---
name: qn
description: Runs the qn CLI to deploy services, roll back releases, and check deployment status. Use when the user asks to deploy, ship, roll back, revert, or check status of a service with qn, or mentions qn environments or regions.
license: Apache-2.0
compatibility: Requires qn >= 2.3.0 on PATH
metadata:
  version: "1.0.0"
allowed-tools: Bash(qn:*)
---

# qn

1. Run `qn --version`. If it reports older than 2.3.0, stop and ask the user to upgrade.
2. Read `references/flags.md` for flag values and defaults before building a command.

## Commands

- `qn deploy`: `--env`, `--region`, `--timeout`, `--force`, `--no-verify`, `--legacy-auth`
- `qn rollback`: `--to`, `--dry-run`
- `qn status`: `--json`, `--watch`

## Rules

- Confirm `--env` and `--region` with the user before `qn deploy`.
- Never pass `--force`, `--no-verify`, or `--legacy-auth` unless the user asks for it by name.
- Run `qn rollback --dry-run` and show the result before the real rollback.
- Prefer `qn status --json` over `--watch`, which does not exit.
```

## Questions for you

- Is `version: 2.3` the skill's version or the CLI's? I assumed the skill's.
- Is `--legacy-auth` deprecated? If so, say so in the skill, or drop it from the list.
- Does `qn status --watch` block until interrupted? I assumed it does. If it doesn't, adjust the last rule.