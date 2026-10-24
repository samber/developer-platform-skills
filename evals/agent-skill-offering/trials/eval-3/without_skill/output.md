ℹ️ I didn't open the repo files, so this rests on how Claude Code resolves plugin versions and on your described routine. Check the three points under "Verify" first.

## Root cause

Claude Code decides "update available" by comparing version strings. It resolves the version in this order: `version` in the plugin's `plugin.json`, then `version` on the marketplace entry, then the git commit SHA. If a version string is set, a new commit with the same string is not an update.

Your routine puts the correct numbers in one commit too late:

1. release-please merges the release PR and tags `v2.6.0`. At that commit, `package.json` says 2.6.0, but `SKILL.md`, the manifests and `marketplace.json` still say the previous version.
2. Your script then bumps those files in a follow-up commit, which sits after the tag.
3. Anyone who installs or updates from the tag, or from a marketplace pinned to a ref or SHA, gets the stale version string. Claude Code compares it to what they already have and says "already latest".
4. Even on `main` it is fragile. `plugin.json` wins silently over the marketplace entry, so if any manifest is missed or drifts, the number users see is not the one you set in `marketplace.json`.

## What to change

1. **Bump versions in the release PR, not after the tag.** Add `extra-files` to the package in `release-please-config.json`, so the tag commit already carries the right numbers:
   - Claude Code `plugin.json`: `{"type":"json","path":".claude-plugin/plugin.json","jsonpath":"$.version"}`
   - The Codex, Cursor and Gemini manifests: the same shape, one entry per file.
   - `marketplace.json`: `jsonpath` `$.plugins[0].version` (or the matching index).
   - `SKILL.md`: type `generic`, with an `x-release-please-version` marker on the version line, for example `version: 2.6.0 # x-release-please-version`. Use `<!-- x-release-please-version -->` if the version is in the body.
2. **Delete the post-tag script and the follow-up commit.** Nothing should be pushed after the tag.
3. **Keep one source of truth per consumer.** For a plugin in the same repo as the marketplace, set `version` in `plugin.json` only, and drop it from the `marketplace.json` entry. If you keep both, release-please must bump both, and a CI check must enforce that they match.
4. **Add a CI check on the release PR and on tags.** Assert that every manifest, `SKILL.md` and `marketplace.json` equals `package.json`'s version. Run `claude plugin validate .` in the same job.
5. **Alternative: omit `version` everywhere.** The commit SHA then becomes the version and every push is an update. You lose the visible semver, and users get unreleased commits if the marketplace tracks `main`. I'd keep explicit versions.

## Fix for 2.6.0 and the two users

- Don't move or re-push the `v2.6.0` tag. Cached copies are keyed by version, so a retag won't reach anyone.
- Ship **2.6.1** after the config change above. The point is that its tag commit contains 2.6.1 in every file.
- Meanwhile, the two users can run `claude plugin marketplace update <marketplace>`, then `claude plugin update <plugin>`. If it still says "already latest", they should uninstall and reinstall the plugin. Clearing its folder under `~/.claude/plugins/cache` also works.

## Verify

1. Check `git show v2.6.0:.claude-plugin/plugin.json | grep version`. I expect the old number. That would confirm the diagnosis.
2. Check whether your marketplace entry pins a `ref` or `sha`, or tracks the default branch.
3. Check that no other manifest still carries a hard-coded older version than `plugin.json`.