**Don't merge the RC to main. Two of your three plans ship it to everyone.**

## 1. Main is what stable users install

- `/plugin marketplace add moorhaven/moor` tracks the default branch.
- Your directory submission has an empty branch field, so it also tracks main.
- If 2.0.0-rc.1 merges to main, every new install and every directory user gets the RC, however you label it. ❌

**Fix:**
1. Cut the RC from a `next` branch (or `rc`) and tag `v2.0.0-rc.1` there. Main stays on 1.9.4.
2. Merge to main only for 2.0.0 final.
3. Ask the Claude directory team, or edit your submission if it allows, to pin the branch to `main` explicitly. An empty field means "whatever's default" and is a risk during a RC period. ⚠️ I don't know their process for changing a pending submission, so check.

## 2. Don't keep the manifests at 1.9.4 on the RC branch

- Claude Code decides whether to update a plugin by comparing the manifest version. Content with an unchanged version can be served from cache, so RC adopters may silently stay on old files.
- Support can't tell which build someone runs.
- The tag (`v2.0.0-rc.1`) and manifests (`1.9.4`) would disagree.

Set `2.0.0-rc.1` consistently in:
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json` (the plugin entry)
- the skill frontmatter version, if you carry one
- `package.json` for the Node CLI

Semver orders `1.9.4 < 2.0.0-rc.1 < 2.0.0`, so the final release still upgrades cleanly. Check that nothing in the CLI's update check compares versions with a naive parser that rejects the `-rc.1` suffix.

## 3. A "normal" GitHub release becomes Latest

- Tick **Set as a pre-release** and untick **Set as the latest release**. Otherwise `releases/latest`, install scripts and badges resolve to the RC.
- If the CLI publishes to npm, use `npm publish --tag rc`. A plain publish moves `latest`, and `npm i moor` then installs the RC for everyone. 🔴 This is the highest-impact slip.
- Early adopters still find a pre-release on the Releases page. Link it from the README.

## 4. README

A 25-word tagline plus the install block won't carry a major RC. Add a short RC section:
- How to install the RC. Marketplace add supports a ref, something like `/plugin marketplace add moorhaven/moor#next`. Verify the exact syntax before you publish it.
- How to go back to stable (`1.9.4`).
- What breaks in 2.0, as 3–5 bullets, with a link to the migration guide or the release notes.
- Where to report problems (issues link or label `rc`).

Keep the stable install block as the default. The RC instructions go below it, clearly labelled.

## Also before tagging
- 2.0.0 is a major bump. Check that the changelog and migration notes exist, listing each breaking change with before/after.
- Run a cold install of the RC from the `next` ref on a clean machine. Confirm it reports `2.0.0-rc.1`.
- Confirm a plain `/plugin marketplace add moorhaven/moor` still gives 1.9.4.

## Questions for you
- What actually breaks in 2.0? That sets how much README and migration text you need.
- Does the CLI publish to npm, or only ship through GitHub?
- Does your pending directory submission let you pin the branch without resubmitting?

I didn't inspect the Moorhaven repo, so the manifest paths above are the usual ones. Check them against your tree.