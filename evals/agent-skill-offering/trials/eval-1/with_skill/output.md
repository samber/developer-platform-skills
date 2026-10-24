Move the skill into the meshline-sdk repo. Make `changeset version` rewrite its version. Add one gate script that fails the release before publish.

I read the skill, its `ci-release-gates.md` and `distribution-channels.md`, and the header of its version script. I didn't touch your repos. Nothing below has run. The Node gate script and both workflows are untested, so run them once locally first.

## Root cause

- The skill sits in `bramwyn/agent-skills`, which has its own release clock. That breaks the lockstep rule (rule 1), so drift was inevitable.
- "Patch release, skill text didn't change, skip the bump" is a rationalization the skill rejects by name. The version is the lookup key. A skill saying 3.2.0 on the 3.4.1 tag reads as stale to every check and every user.
- "Accurate for 3.4.0" is unproven. A version string never proved it. Step 1 below tests it.

## Assumptions

Correct me if any is wrong.

- `meshline-sdk` is a single-package repo at `bramwyn/meshline-sdk`.
- Changesets tags releases as `v3.4.2`. A monorepo would use `meshline-sdk@3.4.2` instead.
- Users are coding agents with a shell.
- Node is 20 or newer.
- The repo is public.

## Plan

Total is about half a day. Do the steps in order.

1. **Check current content, 10 min.** Pack 3.4.1 and type-check the existing skill's `ts` blocks against it, using the script in step 5. A failure means the skill was already wrong and needs fixing first. A pass means the claim held.
2. **Move the skill in, 20 min.** Run **`git mv`** or copy it to `meshline-sdk/skills/meshline-sdk/SKILL.md`. Keep the name `meshline-sdk`, because the name is public API (rule 5).
   - Set `metadata.version: "3.4.1"`, quoted.
   - Set `compatibility: "Requires meshline-sdk installed from npm"`, with no version number.
   - Set `license` to the repo's license.
   - Put the version guard below at the top of the body.
3. **Ship it in the npm package, 5 min.** Edit `package.json`:
   ```json
   {
     "files": ["dist", "skills"],
     "scripts": {
       "version-packages": "changeset version && python3 scripts/check-skill-version.py \"$(node -p \"require('./package.json').version\")\" --write --skills-dir skills"
     }
   }
   ```
   The `--write` flag rewrites `metadata.version` and the `Skill version:` body line in the version PR. That is the commit the tag points at. Copy `scripts/check-skill-version.py` from the skill into `scripts/`.
4. **Replace the old copy with a stub, 15 min.** In `bramwyn/agent-skills`, replace the meshline skill with a stub under the same name. It says "moved, run `npx skills add bramwyn/meshline-sdk#v<your-installed-version>`". Do the same for the other two libraries, each into its own repo.
5. **Write the gates, about 1.5 h.** Add `scripts/skill-gates.sh`, `scripts/check-skill-content.mjs`, and the two workflows below.
6. **Cut a patch release, 15 min.** Add a changeset such as "docs: ship the agent skill in the package". Tags up to v3.4.1 have no skill, so the first tag-pinned install exists only after this release.
7. **Update the docs, 10 min.** Replace the install line:
   ```
   npx skills add bramwyn/meshline-sdk#v<your-installed-version>
   ```
   Show `npm ls meshline-sdk --depth=0` beside it, so the README never goes stale.

### Version guard (top of SKILL.md body)

```
Skill version: 3.4.1
Read the installed version with `npm ls meshline-sdk --depth=0`.
- Same major.minor: continue. If only the patch differs, mention the matching tag once.
- Major or minor differs, in either direction: trust the installed package's types and
  README over this skill's API names, and tell the user to install the skill from their
  version's tag.
- A local or development build: continue.
```

Name no other version anywhere in the prose. Both the check script and `--write` read the `Skill version:` line.

### `scripts/skill-gates.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

VERSION="$(node -p "require('./package.json').version")"

# Gate 2: version equality (metadata.version, body line, no top-level `version:`).
python3 scripts/check-skill-version.py "$VERSION" --skills-dir skills

# Pack the artifact the release will publish. Run `npm run build` before this script.
DEST="$(mktemp -d)"
TARBALL="$DEST/$(npm pack --silent --pack-destination "$DEST")"

# Gate 3a: the package must contain the skill. Write the list to a file:
# `tar | grep -q` under pipefail can fail on SIGPIPE.
tar tzf "$TARBALL" > "$DEST/files.txt"
grep -qx 'package/skills/meshline-sdk/SKILL.md' "$DEST/files.txt"

# Gate 3b: every ts code block in the skill type-checks against the packed SDK.
node scripts/check-skill-content.mjs "$TARBALL"
```

### `scripts/check-skill-content.mjs`

```js
import { execFileSync } from "node:child_process";
import { mkdtempSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const SKILLS_DIR = "skills";
// Only ts/typescript fences are checked. Label pseudo-code blocks `text` to skip them.
const TS_FENCE = /^```(?:ts|typescript)\n([\s\S]*?)^```/gm;

const tarball = resolve(process.argv[2]);
const work = mkdtempSync(join(tmpdir(), "skill-content-"));
let count = 0;

for (const rel of readdirSync(SKILLS_DIR, { recursive: true })) {
  if (!rel.endsWith(".md")) continue;
  const text = readFileSync(join(SKILLS_DIR, rel), "utf8");
  for (const m of text.matchAll(TS_FENCE)) {
    const line = text.slice(0, m.index).split("\n").length + 1;
    // `export {}` makes each block its own module, so top-level names never collide.
    writeFileSync(
      join(work, `block-${count++}.ts`),
      `// ${SKILLS_DIR}/${rel}:${line}\n${m[1]}\nexport {};\n`,
    );
  }
}

// A check that finds nothing to check must fail, never pass.
if (count === 0) {
  console.error("no ts code blocks found under skills/: nothing was checked");
  process.exit(1);
}

writeFileSync(join(work, "package.json"), JSON.stringify({ private: true, type: "module" }));
writeFileSync(
  join(work, "tsconfig.json"),
  JSON.stringify({
    compilerOptions: {
      strict: true, noEmit: true, module: "nodenext",
      moduleResolution: "nodenext", target: "es2022", skipLibCheck: true,
    },
    include: ["*.ts"],
  }),
);

execFileSync("npm", ["install", "--no-audit", "--no-fund", tarball, "typescript", "@types/node"], {
  cwd: work, stdio: "inherit",
});

try {
  execFileSync("npx", ["tsc", "-p", "."], { cwd: work, stdio: "inherit" });
} catch {
  console.error(`type-check failed. Line 1 of each block-N.ts names its source file:line. Scratch dir: ${work}`);
  process.exit(1);
}
console.log(`ok: ${count} code blocks type-check against the packed SDK`);
```

Limits of this gate:

- It catches removed or renamed exports and wrong signatures in code blocks.
- It does not catch identifiers named only in prose. Keep API names inside code blocks.
- A block that imports a third-party package needs that package installed, or the `text` label.

### `.github/workflows/skill-gates.yml` (pull requests)

```yaml
name: skill-gates
on:
  pull_request:
    paths: ["src/**", "skills/**", "package.json", "scripts/**", ".github/workflows/skill-gates.yml"]
jobs:
  gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm run build
      - run: bash scripts/skill-gates.sh
      # Gate 1, spec validation: confirm the `skills-ref` CLI name locally, pin its version,
      # then add `validate skills/meshline-sdk` here.
      # Gate 6, security scan: Snyk Agent Scan needs SNYK_TOKEN and uploads skill content,
      # so skip it on fork PRs.
```

### `.github/workflows/release.yml` (gates run before publish)

```yaml
name: release
on: { push: { branches: [main] } }
permissions: { contents: write, pull-requests: write, id-token: write }
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm, registry-url: "https://registry.npmjs.org" }
      - run: npm ci && npm run build
      - run: bash scripts/skill-gates.sh        # must come before the publish step
      - id: changesets
        uses: changesets/action@v1
        with:
          version: npm run version-packages
          publish: npx changeset publish
          createGithubReleases: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
      - if: steps.changesets.outputs.published == 'true'
        env: { GH_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
        run: |
          TAG="v$(node -p "require('./package.json').version")"
          BODY="$(gh release view "$TAG" --json body -q .body)"
          gh release edit "$TAG" --notes "$BODY

          Agent skill for this release:
            npx skills add bramwyn/meshline-sdk#$TAG
            gh skill install bramwyn/meshline-sdk meshline-sdk@$TAG
          Already installed? Re-run with the new tag."
```

- ⚠️ A version PR opened with `GITHUB_TOKEN` does not trigger `skill-gates.yml`. The gate in the release job still runs on merge, before publish and before the tag. To get the check on the PR too, open it with a PAT or GitHub App token.
- **Mutation check:** on a scratch branch, rename one export the skill uses. The gates must fail. Then set a stale `metadata.version`. The gates must fail again. Without both, the gates are unproven.

## Install channels

- **Default: tag-pinned `npx skills add bramwyn/meshline-sdk#v3.4.2`.** The release note prints it.
- **Free bonus:** the skill now ships inside the npm package, so `node_modules/meshline-sdk/skills/meshline-sdk/` always matches the installed version. This is the strongest rung for an npm SDK and costs one `files` entry. The skills installer can link skills from installed dependencies, but its sync command is marked experimental. Check its current name before documenting it.
- An unpinned `npx skills add` follows the default branch, so it can document unreleased features. Print the pinned form everywhere.
- Users who installed from `agent-skills` hold a stale copy. The stub and the release note tell them to reinstall at their version's tag.

## Deferred

- **Changed-surface check (gate 4).** Add it when a skill-unaffected PR slips through. About 1 h with `api-extractor`. Fail a PR when the public API report changes and nothing under `skills/` changed, unless a `skill-unaffected` label is set.
- **Golden agent tasks (gate 5).** Add it once agents are a main user channel, or after the first issue traced to a wrong skill.
- **Plugin manifests (Claude, Codex, Cursor, Gemini).** Skipped to stay light. Add them when users ask. Pass each file to the script with one `--manifest` flag.
- **ClawHub and OpenClaw.** Skipped. Pass `--version` to ClawHub if you add it.

## Open questions

1. Is `meshline-sdk` a single-package repo with `v*` tags?
2. Does the skill ship a `scripts/` folder? If yes, the Snyk scan becomes mandatory.
3. Is the repo public? Snyk uploads skill content.

## Record these for the next release run

- **Version source:** `package.json`, bumped by `changeset version`.
- **Tag format:** `v<semver>`.
- **Gates:** check-skill-version, packaged-skill assertion, ts-block type-check. Gates 1 and 6 are pending.
- **Channel:** tag-pinned `npx skills add bramwyn/meshline-sdk#v<version>`, plus bundled in npm.
- **Old repo:** `agent-skills` keeps stubs only.

Next: run step 1 now. Pack 3.4.1 with `npm pack`, then run `node scripts/check-skill-content.mjs <tarball>` against a checkout holding the current skill. Its result decides whether step 2 starts with a content fix.