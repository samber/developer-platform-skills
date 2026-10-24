# Moorhaven `moor` 2.0.0-rc.1: pre-RC changes

I haven't seen the moor repo. This is based on the skill's rules and what you told me. Four things need changing before the RC: the version plan, the release type, the default-branch install, and the README.

## 1. Don't keep the skill and manifests at 1.9.4

Bump them all to `2.0.0-rc.1`. Keeping 1.9.4 breaks the lockstep rule (a tag must contain a skill matching its code version) in three ways:

- **Gate 2 fails.** Version equality compares `metadata.version`, the `Skill version:` body line and every manifest against the tag `v2.0.0-rc.1`. A skill at 1.9.4 would fail it. The skill says to bump on every release, prereleases included.
- **The skill flags itself as stale.** The step-3 guard compares `moor --version` (2.0.0-rc.1) with the skill (1.9.4). The major differs, so the skill tells the agent to distrust its own command names and tells the user to reinstall.
- **Claude Code may not refresh.** The plugin installer keys its cache on the manifest `version`. Someone on 1.9.4 who updates to the RC sees "already latest" and keeps the old skill.

"Nothing is final" is an argument for bumping. If 2.0 changes commands or flags, a 1.9.4 skill teaches the old ones with your authority. The content check (gate 3) should run against the RC build.

**Do:**
- Run `check-skill-version.py 2.0.0-rc.1 --write` with every `--manifest`: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and the codex, cursor and gemini manifests if you ship them.
- Keep `version` out of the `plugins[]` entry in `marketplace.json`. `plugin.json` wins silently when both are set.
- Make the bump part of the commit the tag points at. Run gates 1, 2, 3 and 6 before the tag exists, plus `claude plugin validate --strict .`.
- Note that I couldn't run the script's `--help` here. Confirm it accepts `-rc.N` versions before relying on it.

## 2. A normal GitHub release is wrong; mark it a prerelease

- `gh skill install` without a pin resolves the latest tagged release. A normal release makes the RC the install for everyone who doesn't pin.
- Tick "Set as a pre-release". Latest-release resolution then skips it.
- Early adopters find it through the release page and an explicit command. Put this block in the RC release notes only, not in the README's main install section:

```
Agent skill for this RC:
  /plugin marketplace add moorhaven/moor#v2.0.0-rc.1
  npx skills add moorhaven/moor#v2.0.0-rc.1
  gh skill install moorhaven/moor moor@v2.0.0-rc.1
```

- Check the exact skill name for the `gh skill` line.
- Your CLI is on Node. If you publish to npm, use `npm publish --tag next` so `latest` doesn't move. This is outside the skill, but it's the same failure on another channel.

## 3. Don't cut the RC from main if main is what users install

Your docs say `/plugin marketplace add moorhaven/moor`. With `source: "./"`, that installs the default branch, so everyone adding the marketplace gets whatever is merged on main.

- If the RC bump lands on main, those users get 2.0.0-rc.1 skill text. This goes against the skill's rule to keep prereleases off every default install.
- **Fix:** cut the RC from a `next` branch, or tag a commit off main whose bump never merges back. `main` stays at 1.9.4 until 2.0.0 final.
- If 2.0 code is already merged on main, the skill text there may already document unreleased features. Tell me, and we'll check what main says today.
- Create a `stable` branch at the `v1.9.4` tag commit. Move it only on final releases.

## 4. Directory submission with an empty branch field

The empty branch field follows the default branch. Every merge becomes a candidate version, and it goes live if auto-publish is on or someone selects Publish. An RC merged to main would become a listing candidate.

**Do:**
1. Open `claude.ai/directory/manage` and check whether auto-publish is on. Turn it off now if it is.
2. Set **Branch or tag** to `stable`. I don't know whether the field is editable after submission. If it isn't, withdraw and resubmit.
3. Confirm `stable` at `v1.9.4` passes the directory checks listed in section 5.
4. Do not select Publish on any candidate that carries `2.0.0-rc.1`.

A tracked branch only works if it is moved at each final release. Moving it at 2.0.0 is part of the final release checklist.

## 5. README: 25 words fails the directory check

The directory blocks a README under 40 words. Code blocks don't count, so the install block adds nothing.

Rewrite the README with these parts, in the 60 to 120 word range:

- What `moor` does and who it is for, in plain prose.
- A tag-pinned install block with a placeholder, so it never goes stale:

```
moor --version
/plugin marketplace add moorhaven/moor#v<your-installed-version>
npx skills add moorhaven/moor#v<your-installed-version>
```

- One line saying the skill must match the installed CLI version.

Drop the unpinned `/plugin marketplace add moorhaven/moor` line from the README and docs. Also confirm there is a `LICENSE` file or a `license` field.

## 6. Other directory checks to run (source "./" makes the repo the plugin folder)

- **Likely holds:** more than 512 files, and a root `package.json` with a lockfile. Both send the submission to a reviewer. The lockfile also makes Claude Code install `moor`'s npm dependencies into the plugin cache on every install and update. Moving the plugin to a subfolder holding `skills/` fixes both. That would be a bigger change, so decide after the RC.
- **Likely blocks:**
  - `.gitattributes` with `export-ignore` is common in Node repos, so grep for it.
  - `.DS_Store` files.
  - An `npx` launcher that isn't pinned to an exact version.
- **Name check:** the README, `LICENSE` and file names must be valid on Windows and macOS.

## Order of work

1. Pause directory auto-publish and set the branch to `stable`.
2. Create the `stable` branch at the `v1.9.4` tag.
3. Create the `next` branch for the RC.
4. On `next`: bump versions with `--write` and update the skill for 2.0 behavior.
5. Run the gates, then tag `v2.0.0-rc.1`.
6. Publish the GitHub release as a prerelease with the install block above.
7. Rewrite the README to 40 or more words with pinned install commands.

## Questions for you

- Is 2.0 code already merged on main?
- Is the directory submission still pending, or already live?
- Does a release tool (release-please, changesets, goreleaser) cut your tags, or is it manual? That decides where the bump hook goes.
- Does `moor` have `--json` output? The agent-facing design is covered by `cli-interface-design`.