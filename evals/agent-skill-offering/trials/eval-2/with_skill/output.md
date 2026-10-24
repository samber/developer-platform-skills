**Verdict: do not merge.** Seven findings (5 blockers, 2 fixes). A replacement head is below.

**Blockers**

1. **`version: 2.3` at top level.** The spec has no such field. It is also unquoted, so YAML reads it as float `2.3`, not `2.3.0`. Use `metadata.version: "2.3.0"`.
2. **No `Skill version:` line in the body.** Some harnesses hide the frontmatter from the model, and `scripts/check-skill-version.py` checks this line. Add it as the first body line.
3. **One-sided version guard.** "If older, upgrade" lets a silently upgraded qn 2.4 or 3.0 pass. Replace it with the two-sided guard, which also tolerates patch differences and `dev` builds.
4. **`allowed-tools: Bash` pre-approves the tool with no prompt.** Remove it.
5. **Flag list in the body plus `references/flags.md`.** This is a pasted flag table and goes stale on the next release. The tool owns the flags and the skill owns when and why.
   - Delete `references/flags.md`. `qn <cmd> --help` already serves agents.
   - Your reason, "agents don't need to run --help", is the failure mode. A flag removed in 2.4 stays in the skill with the maintainer's authority.
   - Also, `--force`, `--no-verify` and `--legacy-auth` are risky. The list gives no guidance on when to use them.

**Fixes**

6. **`description: Helps with qn.`** This never triggers and has no tasks or tool name. Write what it does and when to use it, with the words users type.
7. **`compatibility: Requires qn >= 2.3.0`** is a second version string that goes stale. Use "Requires qn on PATH."

**Missing**

- **`license: Apache-2.0`.** You said the repo is Apache-2.0, and the skill's `license` must match it. Your message ended "Apache-2.0..", so confirm the exact license.
- **Location.** The file must live in the qn repo at `skills/qn/SKILL.md`, not a separate skills repo (lockstep rule 1).
- **Content.** The draft has no job-shaped workflow, no safe defaults and no real agent failures yet.

**Replacement head**

Assumptions in it, to check: I guessed the purpose from the command names, and I wrote the `--json` line from your `qn status` flag (`--json` on other commands is unconfirmed). Replace the bracketed lines with real content.

```markdown
---
name: qn
description: Drives the qn CLI to deploy, roll back and inspect qn services - choosing the right subcommand, safe defaults, reading JSON output and errors. Use whenever the user mentions qn, qn deploy, qn rollback or qn status, even if they never say "CLI".
license: Apache-2.0
compatibility: Requires the qn CLI on PATH.
metadata:
  version: "2.3.0"
---

# qn

Skill version: 2.3.0
Run `qn --version` first.
- Same major.minor: continue. If only the patch differs, mention the matching tag once.
- Major or minor differs, in either direction: trust `qn --help` over this skill's
  command names, and tell the user to install the skill from their version's tag.
- A development build reporting `dev`: continue.

For exact flags, run `qn <command> --help`; this skill covers which command to use and when.

## Roll back a bad deploy
1. [Find the target release: command and field from your CLI]
2. `qn rollback --to <target> --dry-run`; show the plan to the user.
3. Run without `--dry-run` only after the user confirms.

## Safe defaults
- Use `qn status --json` and read stdout only.
- [Rule for `--force`, `--no-verify`, `--legacy-auth`: ask the user first, never by default.]
- [Failure 1 from real agent misuse]
- [Failure 2]
- [Failure 3]
```

**Release wiring** (lockstep rules 2 to 4)

- Make `metadata.version` and the `Skill version:` line equal the code version, in the commit the tag points at. goreleaser runs after the tag, so bump first with `make release VERSION=x.y.z` running `scripts/check-skill-version.py x.y.z --write`.
- Gate 3 on the built binary must check that every `qn ... --flag` in the skill exists in `--help`. Version equality alone does not catch a removed flag.
- Release notes should print the tag-pinned install command.

**Next, under 2 minutes:** send me the three real mistakes agents make with qn, and the release tool (goreleaser or other). I will fill the placeholders and draft the gate script.