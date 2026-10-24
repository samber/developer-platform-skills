# Tarnwood skill versioning and manifests

I wrote this without reading any repo files. I assumed the package directories are `tw-cli/` and `tw-sdk-js/`, so adjust the paths if they differ. Everything below is untested.

## Decisions

1. **Split the skill in two.** `tarnwood-cli` and `tarnwood-sdk-js` replace the single `tarnwood` skill.
   - The tools release independently (`tw-cli-v4.2.0`, `tw-sdk-js-v2.1.3`). One skill version can't track both.
   - Labelling the skill 4.2.0 makes the SDK half claim a version that isn't its own.
   - Descriptions trigger better when each one covers a single tool.
2. **Version each skill independently of the tools.**
   - A skill version tracks the skill's own content. It bumps when the instructions change, not when the CLI ships.
   - Both new skills start at `1.0.0`.
   - Compatibility with a tool version goes in a separate field, `metadata.compatible-with`.
3. **Make the skill self-contained.** Don't make it just point to `AGENTS.md`.
   - `AGENTS.md` is always loaded in this repo, so a pointer adds nothing here.
   - Anywhere the skill is installed without the repo, the pointer is dead.
   - A skill that only redirects also gives the agent nothing to act on once it triggers.
   - Put the commands, flags, and gotchas in `SKILL.md`. You can add one line saying `AGENTS.md` holds repo-specific conventions, as a supplement.
4. **Treat "teammates say it works great" as weak evidence.**
   - They use it in this repo, where `AGENTS.md` already loads, so the skill is never tested on its own.
   - Before shipping, run a few tasks in a clean checkout or another project with `AGENTS.md` removed. Compare results with and without the skill.

## Files

### `.release-please-manifest.json`

```json
{
  "tw-cli": "4.2.0",
  "tw-sdk-js": "2.1.3",
  ".claude/skills/tarnwood-cli": "1.0.0",
  ".claude/skills/tarnwood-sdk-js": "1.0.0"
}
```

### `release-please-config.json`

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "separate-pull-requests": true,
  "include-component-in-tag": true,
  "include-v-in-tag": true,
  "packages": {
    "tw-cli": {
      "release-type": "go",
      "component": "tw-cli"
    },
    "tw-sdk-js": {
      "release-type": "node",
      "component": "tw-sdk-js",
      "package-name": "tw-sdk-js"
    },
    ".claude/skills/tarnwood-cli": {
      "release-type": "simple",
      "component": "tarnwood-cli-skill",
      "extra-files": ["SKILL.md"]
    },
    ".claude/skills/tarnwood-sdk-js": {
      "release-type": "simple",
      "component": "tarnwood-sdk-js-skill",
      "extra-files": ["SKILL.md"]
    }
  }
}
```

Resulting tags:
- `tw-cli-v4.2.0`
- `tw-sdk-js-v2.1.3`
- `tarnwood-cli-skill-v1.0.0`
- `tarnwood-sdk-js-skill-v1.0.0`

The first two match your existing tags, so the manifest versions line up with them.

### `.claude/skills/tarnwood-cli/SKILL.md` (frontmatter)

The `# x-release-please-version` comment lets release-please rewrite that line on each release.

```yaml
---
name: tarnwood-cli
description: >-
  Use the Tarnwood CLI (tw-cli, Go) - run commands, pass flags, read output,
  fix errors. Use whenever a task mentions tw-cli, the `tw` command, or
  Tarnwood command-line workflows. Not for the JavaScript SDK - use tarnwood-sdk-js.
metadata:
  version: "1.0.0" # x-release-please-version
  compatible-with: "tw-cli >=4.2.0 <5.0.0"
---
```

### `.claude/skills/tarnwood-sdk-js/SKILL.md` (frontmatter)

```yaml
---
name: tarnwood-sdk-js
description: >-
  Use the Tarnwood JavaScript/TypeScript SDK (tw-sdk-js) - install, initialise
  the client, call the API, handle errors and types. Use whenever a task imports
  tw-sdk-js or mentions the Tarnwood JS SDK. Not for the CLI - use tarnwood-cli.
metadata:
  version: "1.0.0" # x-release-please-version
  compatible-with: "tw-sdk-js >=2.1.0 <3.0.0"
---
```

Body structure for both skills:
1. Quick start (install, one working example).
2. Common tasks, each with a verified command or snippet.
3. Gotchas and error → fix table.
4. Last line: "Repo-specific conventions live in the root `AGENTS.md`, if present."

## Migration steps

1. **Move the file.** Run `git mv .claude/skills/tarnwood .claude/skills/tarnwood-cli`. Then create `tarnwood-sdk-js/` and split the existing content by tool.
2. **Rewrite the skill bodies.** Copy the needed material from `AGENTS.md` into each skill. Don't link to it.
3. **Add the two release-please files** at the repo root and commit them.
4. **Use scoped Conventional Commits.** Use `feat(tarnwood-cli-skill): ...` and `fix(tarnwood-sdk-js-skill): ...`. Release-please bumps by path, so only commits touching a skill's directory bump that skill.
5. **Tell teammates the skill was renamed.** `/tarnwood` becomes `tarnwood-cli` and `tarnwood-sdk-js`, and anyone who pinned the old name needs to update.

## Checks and risks

- **Skill drift.** Nothing forces a skill update when a tool ships a breaking change. Add a PR checklist item, or a CI check that fails when a major tool bump lands without a skill commit. Also update `compatible-with` when you widen the range.
- **Skill changelogs.** The `simple` release type writes `version.txt` and `CHANGELOG.md` into each skill directory. If you don't want them in the skill bundle, tell me and I'll switch to a workflow that bumps only `SKILL.md`.
- **Local validation.** Run `npx release-please release-pr --dry-run --config-file=release-please-config.json --manifest-file=.release-please-manifest.json --repo-url=<owner>/<repo>`. Confirm it proposes no bump for `tw-cli` or `tw-sdk-js` and sees the two new skill components.