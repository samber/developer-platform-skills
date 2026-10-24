# Tarnwood: skill versioning and manifests

**Not run.** I read `agent-skill-offering`, its references, and `check-skill-version.py`. I had no access to the Tarnwood repo, and writes to `/tmp` were denied, so I ran nothing. Every path, name, and `<placeholder>` below is an assumption. Run the gates once on a branch before trusting them.

## Verdict on the plan

| Your plan | Verdict | Why |
|---|---|---|
| One skill covering both tools, `metadata.version` 4.2.0 | ❌ Split into two | Lockstep rule 2 needs the skill version to equal the code version. A single skill at 4.2.0 can never equal SDK 2.1.3. The skill's monorepo rule says each tool gets its own skill, checked against its own version and tag prefix. |
| Skill lives in `.claude/skills/tarnwood/` | ❌ Move it | That directory serves agents working on the repo. Users of the published tools never see it. |
| Skill just points at root `AGENTS.md` | ❌ Don't | `AGENTS.md` is contributor-facing and unversioned. It describes HEAD for both tools. It is not in the npm package or the Go module zip, so the pointer dangles for users. Mine it for the skills' workflows and keep it for contributors. |
| "Teammates say it works great" | ⚠️ Not evidence | Teammates run HEAD code with `AGENTS.md` loaded. That tests neither version-matching nor an outside user. Treat it as a useful early signal only. |

## Layout

This assumes `tw-cli/` has its own `go.mod` and `tw-sdk-js/` has its own `package.json`. Both are release-please package paths.

```
release-please-config.json
.release-please-manifest.json        {"tw-cli": "4.2.0", "tw-sdk-js": "2.1.3"}
.claude-plugin/marketplace.json      (no version anywhere)
.github/workflows/skill-gates.yml
scripts/check-skill-version.py       (copied from the skill)
scripts/check-skill-content-cli.sh   (to write, gate 3)
tw-cli/
  skills/tw-cli/SKILL.md (+ references/)
  .claude-plugin/plugin.json
  .codex-plugin/plugin.json
  .cursor-plugin/plugin.json
tw-sdk-js/
  skills/tw-sdk-js/SKILL.md (+ references/)
  .claude-plugin/plugin.json
  .codex-plugin/plugin.json
  .cursor-plugin/plugin.json
  package.json                       "files": [..., "skills"]
.claude/skills/tw-cli    -> ../../tw-cli/skills/tw-cli     (symlink)
.claude/skills/tw-sdk-js -> ../../tw-sdk-js/skills/tw-sdk-js
```

- **Skills inside each tool's directory.** The Go module zip and the npm tarball then carry the skill, so it ships with the code. A root `skills/` cannot reach either artifact.
- **One plugin per tool.** A plugin manifest holds one `version`. Two tools at independent versions need two plugins, so the manifests sit in each tool's directory, not at the repo root.
- **Symlinks keep one copy.** They keep teammates working without a second copy that drifts. Delete `.claude/skills/tarnwood/` in the same PR and tell teammates the new names.
- **Rename rule.** `tarnwood` becomes `tw-cli` and `tw-sdk-js`. It was never published, so no stub skill is needed. If any outside install used the old name, keep a stub for one major.
- **Installer discovery.** Installers discover a root `skills/` most reliably, and I haven't confirmed that `gh skill` or `npx skills` find nested `tw-cli/skills/…`. Test-install each channel before the first release. If one fails, use root `skills/<name>/` and copy it into the npm package in `prepack`. In that case release-please paths become `/skills/tw-cli/SKILL.md`, with a leading slash for repo root.

## Version wiring (release-please)

Release-please bumps the skill in the release PR, so the bump is in the commit the tag points at. Extra-file paths are relative to each package path. That is my reading of the release-please docs, so confirm it on the first release PR.

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "include-component-in-tag": true,
  "packages": {
    "tw-cli": {
      "release-type": "go",
      "component": "tw-cli",
      "extra-files": [
        { "type": "generic", "path": "skills/tw-cli/SKILL.md" },
        { "type": "json", "path": ".claude-plugin/plugin.json", "jsonpath": "$.version" },
        { "type": "json", "path": ".codex-plugin/plugin.json", "jsonpath": "$.version" },
        { "type": "json", "path": ".cursor-plugin/plugin.json", "jsonpath": "$.version" }
      ]
    },
    "tw-sdk-js": {
      "release-type": "node",
      "component": "tw-sdk-js",
      "extra-files": [
        { "type": "generic", "path": "skills/tw-sdk-js/SKILL.md" },
        { "type": "json", "path": ".claude-plugin/plugin.json", "jsonpath": "$.version" },
        { "type": "json", "path": ".codex-plugin/plugin.json", "jsonpath": "$.version" },
        { "type": "json", "path": ".cursor-plugin/plugin.json", "jsonpath": "$.version" }
      ]
    }
  }
}
```

The generic updater only touches annotated lines, so both version lines in each `SKILL.md` carry the marker:

```yaml
metadata:
  version: "4.2.0" # x-release-please-version
```
```markdown
Skill version: 4.2.0 <!-- x-release-please-version -->
```

- **Source of truth:** `.release-please-manifest.json`.
- **Tags:** `tw-cli-v4.2.0` and `tw-sdk-js-v2.1.3`, which gives `--tag-prefix tw-cli-` and `--tag-prefix tw-sdk-js-`.
- **Never edit the five version fields by hand.**

⚠️ **The first pinnable tags come after the skills merge.** `tw-cli-v4.2.0` and `tw-sdk-js-v2.1.3` contain no skill. The first tag-pinned installs are the next releases of each tool, for example 4.2.1 and 2.1.4. Say this in the README.

### One-time bootstrap

Run from the repo root. It **writes versions into the skill and manifest files**.

```bash
python3 scripts/check-skill-version.py tw-cli-v4.2.0 --tag-prefix tw-cli- --write \
  --skills-dir tw-cli/skills \
  --manifest tw-cli/.claude-plugin/plugin.json \
  --manifest tw-cli/.codex-plugin/plugin.json \
  --manifest tw-cli/.cursor-plugin/plugin.json

python3 scripts/check-skill-version.py tw-sdk-js-v2.1.3 --tag-prefix tw-sdk-js- --write \
  --skills-dir tw-sdk-js/skills \
  --manifest tw-sdk-js/.claude-plugin/plugin.json \
  --manifest tw-sdk-js/.codex-plugin/plugin.json \
  --manifest tw-sdk-js/.cursor-plugin/plugin.json
```

Per the script's docs, it keeps the annotations and line endings. Check `git diff --stat` before committing. You should see only version lines changing.

## Skills

Each skill owns WHEN and WHY. Flags and arguments stay with `tw --help` and the SDK's type definitions. I haven't seen your current skill, so the bodies below are skeletons.

### `tw-cli/skills/tw-cli/SKILL.md`

```markdown
---
name: tw-cli
description: <what + when: the commands and tasks users type, e.g. "Drives the tw CLI to …"; mention tw-cli by name; under 1,024 chars>
license: <repo SPDX id>
compatibility: Requires the tw CLI on PATH.
metadata:
  version: "4.2.0" # x-release-please-version
---

Skill version: 4.2.0 <!-- x-release-please-version -->
Run `tw --version` first.
- Same major.minor: continue. If only the patch differs, mention the matching tag once.
- Major or minor differs, in either direction: trust `tw --help` over this skill's
  command names, and tell the user to install the skill from their version's tag.
- A development build reporting `dev`: continue.

For exact flags, run `tw <command> --help`; this skill covers which command to use and when.
```

### `tw-sdk-js/skills/tw-sdk-js/SKILL.md`

```markdown
---
name: tw-sdk-js
description: <what + when: the tasks users type, e.g. "Writes code against the Tarnwood JS SDK …">
license: <repo SPDX id>
compatibility: Requires <npm-package-name> installed in the project.
metadata:
  version: "2.1.3" # x-release-please-version
---

Skill version: 2.1.3 <!-- x-release-please-version -->
Before writing code, read the installed <npm-package-name> version
(`node_modules/<npm-package-name>/package.json` "version"). If major or minor differs
from this skill, prefer the package's type definitions over this skill's examples,
and tell the user which skill tag matches their version.
```

- **Binary name:** I assumed `tw`. Confirm it.
- **No `allowed-tools`.**
- **No second version string** in the prose.
- **No flag tables.**
- **Self-contained skills.** Don't make `tw-sdk-js` depend on `tw-cli` text, because that couples two release streams. Cross-reference by name only.
- **Content source.** Fill each skill's workflows from your three real agent failures per tool, plus whatever in `AGENTS.md` is user-facing.

## Manifests

### `tw-cli/.claude-plugin/plugin.json`

```json
{
  "name": "tw-cli",
  "version": "4.2.0",
  "description": "<one line>",
  "author": { "name": "<owner>" },
  "homepage": "<docs URL>",
  "repository": "<repo URL>",
  "license": "<SPDX id>",
  "keywords": ["tarnwood", "cli", "agent-skills"]
}
```

### `tw-cli/.codex-plugin/plugin.json`

```json
{
  "name": "tw-cli",
  "version": "4.2.0",
  "description": "<one line>",
  "author": { "name": "<owner>" },
  "homepage": "<docs URL>",
  "repository": "<repo URL>",
  "license": "<SPDX id>",
  "skills": "./skills/",
  "interface": {
    "displayName": "Tarnwood CLI",
    "shortDescription": "<short>",
    "developerName": "<owner>",
    "category": "Developer Tools",
    "capabilities": [],
    "websiteURL": "<docs URL>"
  }
}
```

The `category` and `capabilities` values are unverified guesses. Check them against the Codex plugin docs.

### `tw-cli/.cursor-plugin/plugin.json`

```json
{
  "name": "tw-cli",
  "displayName": "Tarnwood CLI",
  "version": "4.2.0",
  "description": "<one line>",
  "author": { "name": "<owner>" },
  "homepage": "<docs URL>",
  "repository": "<repo URL>",
  "license": "<SPDX id>",
  "skills": "./skills/"
}
```

### `tw-sdk-js` manifests

Same three files with these changes:

- `name`: `tw-sdk-js`
- `version`: `2.1.3`
- `displayName` / `interface.displayName`: "Tarnwood JS SDK"
- keywords and descriptions adjusted

### Root `.claude-plugin/marketplace.json`

```json
{
  "name": "tarnwood",
  "owner": { "name": "<owner>" },
  "description": "Agent skills for the Tarnwood CLI and JS SDK",
  "plugins": [
    { "name": "tw-cli", "source": "./tw-cli" },
    { "name": "tw-sdk-js", "source": "./tw-sdk-js" }
  ]
}
```

- **No `version` in either entry.** When both are set, the plugin manifest silently wins.
- **Don't pass this file to gate 2.** It carries no version to check.
- **Marketplace pinning is only partly tag-pinned.** `/plugin marketplace add OWNER/REPO#tw-cli-v4.2.1` pins the whole repo, so the other plugin there is at an arbitrary version. Tell users to install only the plugin matching the tag: `/plugin install tw-cli@tarnwood`.

### Left out on purpose

- **Gemini.** `gemini-extension.json` must sit at the repo or archive root, and a root file would carry one version for two tools. Add it later if Gemini users appear, as a per-tool release archive.
- **OpenClaw.** The `metadata.openclaw` block is a spec deviation, so add it only if OpenClaw users matter. Then add `--allow-nested openclaw` to gate 2 and name the CLI binary under `requires.bins`.

### Placeholders to fill from your existing package metadata

- `<owner>`
- `<docs URL>`
- `<repo URL>`
- `<SPDX id>`
- `<npm-package-name>`

Never publish placeholder owners. Add a CI `grep` for `<` in the manifests.

### Plugin folder caveat

`tw-sdk-js/` holds `package.json` and a lockfile. Claude Code then installs the SDK's npm dependencies into the plugin cache on every install and update, and the directory submission holds it for review. Accept this for now. The cleaner fix is a plugin subfolder that holds only `skills/`, with every manifest path repointed.

## CI gates

The release-please PR is the pre-tag gate: the tag is created when that PR merges. Rule 4 holds only if the gates run on that PR.

⚠️ **PRs opened with `GITHUB_TOKEN` don't trigger `pull_request` workflows.** Run release-please with a PAT or GitHub App token. Then make `skill-gates` a required check on `release-please--*` branches.

```yaml
name: skill-gates
on:
  pull_request:
    paths: ["tw-cli/**", "tw-sdk-js/**", "scripts/**", ".release-please-manifest.json"]
  push:
    tags: ["tw-cli-v*", "tw-sdk-js-v*"]   # backstop only
jobs:
  version:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        component: [tw-cli, tw-sdk-js]
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Gate 2, version equality
        env:
          COMP: ${{ matrix.component }}
        run: |
          if [ "$GITHUB_REF_TYPE" = tag ]; then
            case "$GITHUB_REF_NAME" in "$COMP"-v*) ver="$GITHUB_REF_NAME" ;; *) echo "other component's tag"; exit 0 ;; esac
          else
            ver="$(jq -er --arg c "$COMP" '.[$c]' .release-please-manifest.json)"
          fi
          python3 scripts/check-skill-version.py "$ver" --tag-prefix "$COMP-" \
            --skills-dir "$COMP/skills" \
            --manifest "$COMP/.claude-plugin/plugin.json" \
            --manifest "$COMP/.codex-plugin/plugin.json" \
            --manifest "$COMP/.cursor-plugin/plugin.json"
```

`jq -e` fails on a missing key, so a typo cannot fall back to an empty version.

| Gate | Run on | What it does for Tarnwood |
|---|---|---|
| 1. Spec validation | PR and release PR | Pin `skills-ref==<version>` and run it on both skill directories. |
| 2. Version equality | PR, release PR, tag backstop | The job above. |
| 3a. Content check, CLI | PR and release PR | Build the CLI with release stamping (`goreleaser build --snapshot --clean --single-target`). Extract each `tw …` invocation from `tw-cli/skills/**/*.md`. Run `tw <subcommand path> --help 2>&1`. Assert every flag name appears, with dashes stripped, at every subcommand level. In the other direction, fail on a new public command the skill never mentions, with a small allowlist file. Assert the archive contains `SKILL.md`: add `skills/**` to `archives.files`. Fail with file, line, and token. |
| 3b. Content check, SDK | PR and release PR | Extract the ```` ```ts ```` blocks from `tw-sdk-js/skills/**`, run `tsc --noEmit` against the built package, and mark pseudo-code with a ```` ```text ```` fence. Run `npm pack --dry-run 2>&1 \| grep skills/`. |
| 4. Changed-surface | PR only | If the `tw --help` tree or the SDK's exported API changed and no file under the matching `skills/` changed, fail unless the `skill-unaffected` label is set. |
| 5. Golden agent tasks | Deferred | Build once agents are a main user channel, or after the first issue traced to a wrong skill. |
| 6. Security scan | PR and release PR | Add `uvx snyk-agent-scan@<pinned> --ci --dangerously-run-mcp-servers --skills ./tw-cli/skills` and a second run for `./tw-sdk-js/skills`. `SNYK_TOKEN` comes from a secret. Skip on fork PRs. It uploads skill content to Snyk. |

Gates 3a and 3b, plus the Go and npm packaging asserts, are the ones that catch the real drift. Version equality only proves someone bumped a string. I have not written `check-skill-content-cli.sh` or the SDK extractor, because they depend on your command tree and my output would be untested.

## Install commands

Add this block to each release note, by script, with the tag filled in. Test each line once before publishing it.

```
Agent skill for this release (tw-cli v4.2.1):
  npx skills add https://github.com/<owner>/<repo>/tree/tw-cli-v4.2.1/tw-cli/skills/tw-cli
  gh skill install <owner>/<repo> tw-cli@tw-cli-v4.2.1
  /plugin marketplace add <owner>/<repo>#tw-cli-v4.2.1   then   /plugin install tw-cli@tarnwood
Already installed? Re-run with the new tag.
```

The SDK block is identical with `tw-sdk-js` and its own tag. In the README, print the same commands with a `<tw-cli-v…>` placeholder and `tw --version`, so the README never goes stale. `npm install` of the SDK also delivers its skill, because `skills` is in `files`.

## Open questions

I couldn't ask these. Each answer changes a step.

1. Paths: do `tw-cli/` and `tw-sdk-js/` have their own `go.mod` and `package.json`?
2. CLI binary name, npm package name, and the repo's license?
3. Do users install the CLI through Homebrew or a release download? If so, the skill never reaches them. Print the install command in `tw --help` or first-run output, and consider a bundled `tw skills install` later.
4. Three real agent failures per tool. They become the skills' first content and the tests for gate 5.
5. Do other skills or `AGENTS.md` files, community ones included, already exist for these tools?
6. Deadline, and effort ceiling: is this a one-off fix or a standing release practice?

## Rule check

| Lockstep rule | Status |
|---|---|
| 1. Same repo as the code | ✅ One skill per tool, in the tool's directory. |
| 2. `metadata.version` equals the code version, same commit | ✅ release-please extra-files, plus the `Skill version:` body line. |
| 3. Every tag contains a matching skill | ✅ From the next release of each tool. The two current tags are exempt. |
| 4. A stale skill fails before the tag exists | ⚠️ Only once the release-PR check is required and release-please uses a PAT or App token. Content gates 3a and 3b are still to be written. |
| 5. Rename or removal is a breaking change | ✅ The `tarnwood` rename is internal-only. Stub it if any outside install used the old name. |