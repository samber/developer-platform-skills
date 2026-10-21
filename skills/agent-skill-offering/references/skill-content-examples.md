# Skill content examples for a shipped CLI or library skill

## Frontmatter

```yaml
# ✓ Good - quoted version in metadata only, binary declared without a version number
---
name: acme-cli
description: Drives the acme CLI to deploy, roll back and inspect acme services - choosing the right subcommand, safe defaults, reading JSON output and errors. Use whenever the user mentions acme, acme deploy, acme rollback, or an acme.yaml file, even if they never say "CLI".
license: MIT
compatibility: Requires the acme CLI on PATH.
metadata:
  version: "1.4.0"
---

# ✗ Bad - top-level version (no such spec field), unquoted, allowed-tools pre-approves tools without a prompt, vague description
---
name: acme
version: 1.4
description: Helps with acme.
allowed-tools: Bash
---
```

## Body opening

```markdown
// ✓ Good - script-maintained version line, two-sided and patch-tolerant guard,
//          ownership of WHAT handed to --help
Skill version: 1.4.0
Run `acme --version` first.
- Same major.minor: continue. If only the patch differs, mention the matching tag once.
- Major or minor differs, in either direction: trust `acme --help` over this skill's
  command names, and tell the user to install the skill from their version's tag.
- A development build reporting `dev`: continue.

For exact flags, run `acme <command> --help`; this skill covers which command to use and when.

// ✗ Bad - one-sided guard: a silently upgraded acme 2.0 passes it
Written for acme-cli 1.4.x. If `acme --version` is older, tell the user to upgrade.

// ✗ Bad - no version anchor, copies the flag table that the next release will change
acme deploy supports --env, --region, --timeout, --legacy-auth, --no-verify ...
```

## Workflow section

```markdown
// ✓ Good - job-shaped, with the failure agents actually hit
## Roll back a bad deploy
1. `acme releases list --json` and pick the previous `id` with status "healthy".
2. `acme rollback <id> --dry-run`; show the plan to the user.
3. Run without `--dry-run` only after the user confirms.
Agents often call `acme deploy --previous`; that flag does not exist. Use `rollback`.

// ✗ Bad - command-group dump with no decision in it
## Releases commands
- list
- get
- rollback
```

## Output parsing

```markdown
// ✓ Good
Pass `--json` and read stdout only; progress and warnings go to stderr.
Exit code 3 means "nothing to deploy", not failure.

// ✗ Bad
Parse the table output (columns may change between versions).
```

## Library guard

```markdown
// ✓ Good - the agent reads the installed version from the project, not from memory
Skill version: 4.2.0
Before writing code, read the installed acme-sdk version (`node_modules/acme-sdk/package.json`
"version", the `go.mod` require line, `pip show acme-sdk`, or `Cargo.lock`). If major or
minor differs, prefer the package's bundled docs and type definitions over this skill's
examples, and tell the user which skill tag matches their version.

// ✗ Bad - assumes the latest API
Use `client.charges.create()` (the v4 API).
```
