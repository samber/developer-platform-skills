Couldn't verify the plan against real files or docs. The `sdg` repo isn't in this working directory (no `skills/sdg`, no `.github/workflows`), and WebFetch and WebSearch were denied. The points below come from memory. Confirm each against the ClawHub and OpenClaw docs before you act.

## Verdict by plan item

| Item | Verdict |
|---|---|
| `metadata.openclaw: {"requires": {"bins": ["sdg"]}}` | ✅ Good, with two conditions. |
| `openclaw.plugin.json` at repo root | ❌ Drop it. |
| Publish from CI with ClawHub's reusable `skill-publish.yml` | ⚠️ Unverified. Don't trust it blind. |
| `icon` and `documentationUrl` in `marketplace.json` | ⚠️ Likely off-schema and duplicated. |
| "Apache-2.0 is fine on ClawHub" | ❌ Premise likely wrong. |

## Details

**1. Frontmatter (`skills/sdg/SKILL.md`)**
- OpenClaw's loader reads frontmatter as single-line keys. Keep `metadata` as one-line JSON, for example `metadata: {"openclaw": {"requires": {"bins": ["sdg"]}}}`. A multi-line YAML map may be ignored.
- `requires.bins` is a gate. If `sdg` isn't on PATH, OpenClaw marks the skill ineligible. Users then see nothing and no error.
- Add an install hint next to it (OpenClaw `install` spec, or install steps in the SKILL.md body) so users can fix the missing binary.
- Other agents ignore the `openclaw` key, so Claude Code and Codex users aren't affected.

**2. `openclaw.plugin.json`: drop it**
- That manifest describes OpenClaw plugins, which are code extensions with an `id` and a config schema.
- A skill-only repo gets discovered through ClawHub, not through this file.
- A wrong or partial manifest can fail strict validation, or make OpenClaw treat the repo as a broken plugin.
- Add it only if `sdg` ships a real plugin. Then it needs its own design and review.

**3. CI publish**
- Check that `skill-publish.yml` exists, find its repo path, and read its inputs and secrets. I can't confirm any of that.
- If it exists, pin it by commit SHA, not `@main`. The workflow runs with your publish token, so a moving ref means someone else can push code that runs with that token.
- Store the ClawHub token as a repo secret, scoped to a release environment.
- Trigger on the `v3.1.0` tag, and fail if the tag version differs from the SKILL.md version.
- If the reusable workflow is missing, fall back to `clawhub publish` in a job you own.
- Do a manual first publish before automating, to see what ClawHub validates.

**4. `marketplace.json`**
- This is the Claude Code plugin marketplace file. I don't believe `icon` and `documentationUrl` are documented fields there. `homepage` is the usual one.
- Check that the schema accepts the extra fields, because strict validation can reject the whole marketplace.
- "Both files carry them" means two copies that will drift. Pick one source of truth. If `openclaw.plugin.json` goes, the problem goes with it.

**5. License: the main risk**
- ClawHub, as I recall, publishes every skill under MIT-0 (no attribution required) and lets you pick no other license. I recall this from its terms, and I haven't re-read them.
- If that's right, the ClawHub copy is MIT-0 whatever your repo says.
  - Users of that copy lose the Apache-2.0 attribution and NOTICE terms.
  - They also lose its patent grant.
- The GitHub repo stays Apache-2.0. Only the published copy changes.
- Sedgebrook's "fine keeping Apache-2.0" holds only if they understand the ClawHub copy won't be Apache-2.0. Ask them to confirm that. If it's unacceptable, skip ClawHub and let OpenClaw users install from GitHub.
- Don't claim "Apache-2.0" on the ClawHub listing.

## Next action
Read the ClawHub license and publishing pages. Confirm the MIT-0 term and the `skill-publish.yml` path and inputs (about 10 minutes). Then send Sedgebrook the license question before touching CI.

Once those two facts are in, I can draft the SKILL.md frontmatter and the tag-triggered workflow.