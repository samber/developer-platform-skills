# Keeping the meshline-sdk skill aligned

## What went wrong

Skipping the bump on the two patch releases was the right call. The problem is that `metadata.version` is carrying two meanings:

- **Skill content version:** did the skill text change?
- **SDK version it was checked against:** is it still true for 3.4.1?

Nothing in the file records the second one, so a reader can't tell "unchanged and still accurate" from "forgotten".

Also, `npx skills add bramwyn/agent-skills` should install whatever is on the repo's default branch. I'm assuming that, so check it. If so, users never see the version number, and what matters is that `main` is correct.

## Decisions

1. **Split the two meanings into two fields.**
   - `metadata.version` is the skill's own semver. It bumps only when the instructions change.
   - `metadata.verified-sdk-version` is the last meshline-sdk release someone actually checked the skill against. It moves on every verification, including no-change ones.
   - Your 3.2.0 looks like it mirrored the SDK number. I'd stop mirroring it, because that forces empty bumps on every patch. If you'd rather keep the mirror, say so and I'll redo the plan around that.
2. **Keep the skill in `bramwyn/agent-skills`.**
   - Moving it into the SDK repo would couple it better, because the skill would change in the same PR as the API.
   - It would also change the install line and split your three-skill review. Revisit this if the checks below miss more than two minors in a quarter.
3. **Review effort follows the changeset bump.**
   - `patch`: automated check only.
   - `minor` or `major`: a human reads the changelog, edits the skill if needed, and bumps `verified-sdk-version`.

Target frontmatter:

```yaml
---
name: meshline-sdk
description: ...
compatibility: meshline-sdk ^3.0.0
metadata:
  version: "3.2.0"
  verified-sdk-version: "3.4.1"
---
```

`compatibility` is a free-text field in the Agent Skills spec. Check that your installer tolerates it.

## Do now (about 30 minutes, one PR in agent-skills)

1. Read the 3.4.0 → 3.4.1 changelog entries.
2. Run the snippet typecheck below locally against 3.4.1.
3. Add `verified-sdk-version: "3.4.1"`. Leave `version` at 3.2.0, since no instruction text changed.
4. Put the bump rules in the agent-skills README:
   - Bump `version` when the skill body changes: patch for wording, minor for new coverage, major for removed or renamed guidance.
   - Never bump `version` for a verification-only change.

## Automation

Three pieces: a release hook in the SDK repo, plus a freshness check and a snippet typecheck in agent-skills.

**1. meshline-sdk release workflow: one added step after `changesets/action`.**

This **sends a `repository_dispatch` event to agent-skills** after each publish:

```yaml
- if: steps.changesets.outputs.published == 'true'
  env:
    GH_TOKEN: ${{ secrets.AGENT_SKILLS_DISPATCH_TOKEN }}
  run: gh api repos/bramwyn/agent-skills/dispatches -f event_type=meshline-sdk-released
```

- This assumes the `changesets/action` step has `id: changesets`.
- The token is a fine-grained PAT with `contents: write` on agent-skills only. Without it the dispatch fails.
- Add one line to the SDK PR template: `[ ] Public API changed → skill reviewed in bramwyn/agent-skills`.

**2. agent-skills: freshness check, `scripts/check-skill-freshness.mjs`.**

It fails when the skill's verified major.minor differs from npm `latest`. Patch gaps pass.

```js
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

const [skillPath, pkg] = process.argv.slice(2);
const frontmatter = readFileSync(skillPath, 'utf8').match(/^---\n([\s\S]*?)\n---/)?.[1] ?? '';
const verified = frontmatter.match(/^\s*verified-sdk-version:\s*"?(\d+\.\d+\.\d+)"?\s*$/m)?.[1];
if (!verified) {
  console.error('missing metadata.verified-sdk-version');
  process.exit(1);
}
// execFileSync throws on npm failure, so a registry error fails the check instead of passing it.
const latest = execFileSync('npm', ['view', pkg, 'version'], { encoding: 'utf8' }).trim();
if (!/^\d+\.\d+\.\d+$/.test(latest)) {
  console.error(`unexpected npm version: ${latest}`);
  process.exit(1);
}
const [vMajor, vMinor] = verified.split('.');
const [lMajor, lMinor] = latest.split('.');
if (vMajor !== lMajor || vMinor !== lMinor) {
  console.error(`skill verified against ${verified}, npm latest is ${latest}`);
  process.exit(1);
}
console.log(`ok: verified ${verified}, latest ${latest}`);
```

**3. agent-skills: snippet typecheck, `scripts/typecheck-skill-snippets.mjs`.**

It extracts the skill's TypeScript code blocks and compiles them against the latest published types. This catches renamed or removed APIs, which a version string never will.

```js
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';

const [skillPath, outDir] = process.argv.slice(2);
const markdown = readFileSync(skillPath, 'utf8');
const fence = /^```(?:ts|typescript)(?<info>[^\n]*)\n(?<code>[\s\S]*?)^```/gm;
mkdirSync(outDir, { recursive: true });
let count = 0;
for (const match of markdown.matchAll(fence)) {
  // A fence tagged "skip" (```ts skip) holds pseudo-code with ellipses.
  if (/\bskip\b/.test(match.groups.info)) continue;
  count += 1;
  // "export {}" gives every snippet its own module scope so top-level names don't collide.
  writeFileSync(`${outDir}/snippet-${String(count).padStart(2, '0')}.ts`, `${match.groups.code}\nexport {};\n`);
}
// Zero snippets would make the typecheck pass vacuously, so treat it as a failure.
if (count === 0) {
  console.error('no checkable snippets found');
  process.exit(1);
}
console.log(`extracted ${count} snippets`);
```

**Workflow, `.github/workflows/meshline-skill.yml` in agent-skills:**

```yaml
name: meshline-skill
on:
  pull_request:
    paths: ['skills/meshline-sdk/**', 'scripts/**']
  schedule: [{ cron: '0 7 * * 1' }]   # weekly safety net if a dispatch is missed
  repository_dispatch: { types: [meshline-sdk-released] }
  workflow_dispatch:
permissions: { contents: read, issues: write }
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - name: Freshness (not on PRs, so unrelated skill PRs never block on a new SDK minor)
        if: github.event_name != 'pull_request'
        run: node scripts/check-skill-freshness.mjs skills/meshline-sdk/SKILL.md meshline-sdk
      - name: Snippets compile against npm latest
        run: |
          work=$(mktemp -d)
          node scripts/typecheck-skill-snippets.mjs skills/meshline-sdk/SKILL.md "$work/src"
          cd "$work"
          npm init -y >/dev/null && npm pkg set type=module
          npm i --ignore-scripts meshline-sdk@latest typescript
          npx tsc --noEmit --strict --target es2022 --module nodenext --moduleResolution nodenext --skipLibCheck src/*.ts
      - name: Open one drift issue
        if: failure() && github.event_name != 'pull_request'
        env: { GH_TOKEN: '${{ github.token }}' }
        run: |
          open=$(gh issue list --label skill-drift --state open --json number --jq length)
          [ "$open" = "0" ] && gh issue create --label skill-drift \
            --title "meshline-sdk skill needs review" \
            --body "Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
          exit 0
```

- This **creates a GitHub issue** on drift. Create the `skill-drift` label once first, or `gh issue create` fails.
- Add a PR-template checkbox: `[ ] Skill body changed → metadata.version bumped`. A script for this isn't worth it yet.

## Flow after setup

1. A changeset publishes meshline-sdk, and the dispatch fires.
2. If it's a patch, the typecheck passes, the freshness check passes, and nothing happens.
3. If it's a minor or major, freshness fails and one issue opens in agent-skills.
4. Someone reads the changelog, fixes the skill if needed, and bumps `verified-sdk-version`. They bump `version` only if the text changed.

## Things I couldn't see

- **Snippets that aren't self-contained.** The typecheck needs most snippets to compile on their own. If many use `...` or undeclared variables, tag them `skip` or add the missing declarations once.
- **agent-skills release flow.** I don't know it. This plan doesn't depend on it, but if that repo auto-bumps versions or tags on merge, confirm that a `verified-sdk-version`-only change doesn't trigger a spurious release.
- **Backport `latest` tag.** If you publish a backport to the `latest` dist-tag, the freshness check compares against the wrong version.
- **Wrong `npm view` timing.** The dispatch fires right after publish. If npm hasn't propagated yet, the first run can see the old version. The weekly cron catches it.

Rollout is about 2–3 hours in total, split across both repos. The only secret is the dispatch PAT.