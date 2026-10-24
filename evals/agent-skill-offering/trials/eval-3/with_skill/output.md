# Fix for Claude Code "already latest" after 2.6.0

## Why users see "already latest"

Claude Code takes a plugin's version from `plugin.json` `version`. If that is unset, it uses the marketplace entry's `version`, and if that is unset too, the commit SHA. When the version is set, update only fetches once that string changes. If the string still says 2.5.x, it reports "already latest".

Your routine breaks this in three ways.

1. **The tag points at the wrong commit.** release-please creates the `v2.6.0` tag on the release-PR merge commit. That commit has a bumped `package.json` but old skill and manifest versions. Your script's bump lands in a later commit, so the tag never contains it.
   - Anyone who added the marketplace at `#v2.6.0` gets a plugin still labelled 2.5.x.
   - Anyone who updates between the tag and your follow-up push sees nothing new.
   - The npm 2.6.0 tarball carries the stale skill too, if `skills/` is in `files`.
2. **The version is set in two places.** `plugin.json` wins over the marketplace entry. Your `marketplace.json` entry version is either redundant or, if your script bumps it but misses `plugin.json`, misleading. `claude plugin validate --strict .` warns about this.
3. **A hand-run script can silently skip a file.** If it missed `.claude-plugin/plugin.json` once, that manifest never changed and the cache never refreshed.

I haven't seen your repo. Confirm the cause in one minute:

```bash
git show v2.6.0:.claude-plugin/plugin.json | grep '"version"'
git show v2.6.0:skills/hollowmere-ledger/SKILL.md | grep -iE 'version'
```

If either prints 2.5.x, the diagnosis is confirmed.

## What to change

### 1. Bump everything in the release PR

Stop running the post-tag script. Make release-please bump every version field in the release PR, so the tag commit contains them. `package.json` stays the single source of truth.

`release-please-config.json`:

```json
{
  "packages": {
    ".": {
      "release-type": "node",
      "extra-files": [
        { "type": "generic", "path": "skills/hollowmere-ledger/SKILL.md" },
        { "type": "json", "path": ".claude-plugin/plugin.json", "jsonpath": "$.version" },
        { "type": "json", "path": ".codex-plugin/plugin.json", "jsonpath": "$.version" },
        { "type": "json", "path": ".cursor-plugin/plugin.json", "jsonpath": "$.version" },
        { "type": "json", "path": "gemini-extension.json", "jsonpath": "$.version" }
      ]
    }
  }
}
```

The generic updater only edits annotated lines, so annotate both version lines in `SKILL.md`:

```yaml
metadata:
  version: "2.6.0" # x-release-please-version
```

```
Skill version: 2.6.0 <!-- x-release-please-version -->
```

Keep the `Skill version:` line in the body, outside any code fence. Some harnesses never show the model the frontmatter.

### 2. Remove `version` from the marketplace entry

In `.claude-plugin/marketplace.json`, delete `version` from the `plugins[]` entry.
- Keep `name` equal to the plugin name and `source: "./"`.
- Keep `version` only in `.claude-plugin/plugin.json`.
- A top-level marketplace `version` or `metadata.version` describes the marketplace file itself, not the plugin. Leave it out of the release bump.

### 3. Gate the release PR so a miss fails before the tag

Copy `check-skill-version.py` from the agent-skill-offering skill into `scripts/`.

On the release-please PR (and every PR), run it against `package.json`:

```bash
python3 scripts/check-skill-version.py "$(node -p "require('./package.json').version")" \
  --skills-dir skills \
  --manifest .claude-plugin/plugin.json \
  --manifest .claude-plugin/marketplace.json \
  --manifest .codex-plugin/plugin.json \
  --manifest .cursor-plugin/plugin.json \
  --manifest gemini-extension.json
```

It checks `metadata.version`, the `Skill version:` line and every manifest. It rejects a malformed `version:` key.

Add a few more checks:
- Make the check a required status on the release PR. That way a forgotten file blocks the merge instead of shipping a stale tag.
- Re-run it on tag push (`v*`) as a backstop.
- Add `npm pack --dry-run 2>&1 | grep skills/` to prove the tarball ships the skill.
- Add `claude plugin validate --strict .`.
- Add a content check: compile or type-check the code blocks in `SKILL.md` against the built package.
- Add an agent-skill security scan (Snyk Agent Scan) over `skills/`.

### 4. Repair 2.6.0 with a 2.6.1 patch release

Don't move the published `v2.6.0` tag.
1. Land the config, annotation and marketplace changes in a `fix:` commit, for example `fix: bump skill and plugin manifests in release PR`.
2. release-please opens the 2.6.1 release PR with all fields bumped.
3. Merge it. The tag now points at a commit whose skill and manifests say 2.6.1.

Bump the skill on every release, patch releases and prereleases included (`2.7.0-rc.1`), even when the skill text didn't change. The version is the cache key.

### 5. Unblock the two reporters

After 2.6.1 ships, they should run:

```
/plugin marketplace update <marketplace-name>
/plugin update hollowmere-ledger@<marketplace-name>
```

If that still says "already latest", they should uninstall and re-add the marketplace at the tag: `/plugin marketplace add hollowmere/<repo>#v2.6.1`.

### 6. Pin installs to tags

Generate this block in every release note:

```
Agent skill for this release:
  /plugin marketplace add hollowmere/<repo>#v2.6.1
  gh skill install hollowmere/<repo> hollowmere-ledger@v2.6.1
  npx skills add hollowmere/<repo>#v2.6.1
  gemini extensions install https://github.com/hollowmere/<repo> --ref=v2.6.1
```

- In the README, use a `v<installed-version>` placeholder so it never goes stale.
- Users who add the marketplace from the default branch get merged-but-unreleased skill text under the last released version. Keep a `stable` branch moved only at release and point docs and any directory submission at it.
- Cursor follows commits, not the manifest version, and Gemini follows its ref. Keep their `version` fields bumped anyway, because the version check covers all five manifests.

## Open questions

These could change the plan:
- Do tags look like `v2.6.0` or carry a prefix? A prefixed tag needs `--tag-prefix` in the check.
- Does the npm package ship `skills/` in `files`? If it does, 2.6.0 on npm carries the stale skill too, and 2.6.1 fixes that.
- Are there maintenance branches? Run the same bump and gates on them.