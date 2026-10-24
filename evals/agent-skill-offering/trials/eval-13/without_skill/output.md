# Thornquist: validation fix and `thorn` → `thornquist-cli` rename

I haven't opened the Thornquist repo, so the causes below are ranked suspects, not confirmed findings. "Couldn't validate that repository" gives no detail, so the first step is to get the real error.

## Part 1: Get through validation

**Step 1: Run the validator locally (about 5 minutes).** From the repo root, run `claude plugin validate .`. It prints the actual failure, so you can skip guessing at the rest.

**Step 2: Fix the suspects in this order.**

1. **Move `plugin.json` into `.claude-plugin/`.** This is the most likely cause. Claude Code looks for the manifest at `.claude-plugin/plugin.json`, and a root-level file isn't found. Move it with `git mv plugin.json .claude-plugin/plugin.json`. Keep `skills/`, `commands/` and similar directories at the repo root, not inside `.claude-plugin/`. If the manifest uses relative paths, fix them to start with `./`.
2. **Confirm the skill layout.** The skill must sit at `skills/<name>/SKILL.md`. The frontmatter needs `name` and `description`. The name must be lowercase with hyphens and match its directory.
3. **Replace the `README.md` → `docs/README.md` symlink with a real file.** Fetchers that use GitHub's API or zipballs often don't resolve symlinks. Do `git rm README.md`, then `git mv docs/README.md README.md`. Fix the relative image links inside it, because they currently resolve from `docs/`.
4. **Check the `tests/ export-ignore` line in `.gitattributes`.** This only matters if the validator fetches a `git archive`. In that case `tests/` is missing, so any manifest path that points into `tests/` fails. Remove the attribute temporarily to test. If that fixes it, stop referencing `tests/` from the manifest.
5. **Trim `docs/` assets (optional).** The 3 MB PNG and 600 KB PDF are unlikely to cause the failure, and I don't know the validator's size limits. Compressing the PNG is cheap and helps clone time. Keep the originals, per your convention, and use an `-optimized` suffix for the new file.
6. **Pin prettier in the helper script.** Add `prettier` to `devDependencies` and call `npm exec prettier` or `node_modules/.bin/prettier`. An unpinned `npx prettier` downloads code at run time. That can fail offline and security scanners flag it. It's probably not the validation error, but it's worth fixing now.
7. **Check the repo basics.** The repo must be public, and you must submit the exact `https://github.com/<owner>/<repo>` URL, with no `.git` suffix and no `/tree/...`. The manifest must be valid JSON with a semver `version`. `package.json` and `package-lock.json` at the root are fine.

**Step 3: Re-validate.** Run `claude plugin validate .` until it's clean. Then resubmit.

**If it still says "Couldn't validate"**, bisect. Make a throwaway branch containing only `.claude-plugin/plugin.json`, `skills/`, and `README.md`, then submit that. Add directories back until it breaks. The last one added is the cause.

## Part 2: Rename `thorn` → `thornquist-cli` in 2.4.1

**Decision for you first:** do you want to submit the listing under the old name or the new one? If validation passes this week, the listing would carry `thorn` and then change a week later. I recommend landing the rename on a branch now and submitting under `thornquist-cli`. If 2.4.1 must stay the cut-over, submit as-is and accept the rename after listing.

**Scope: what changes and what doesn't**

| Item | Change? |
|---|---|
| `skills/thorn/` directory → `skills/thornquist-cli/` | Yes. Use `git mv` to keep history. |
| `name:` in `SKILL.md` frontmatter | Yes. It must equal the directory name. |
| `name` in `.claude-plugin/plugin.json` (and any marketplace entry) | Yes, if the plugin name is also `thorn`. This changes the namespace from `thorn:...` to `thornquist-cli:...`. |
| README, docs, examples, `/thorn` invocations, CI, tests | Yes. Use `git grep -nE '\bthorn\b'` and review each hit. |
| `bin` entry in `package.json` (the `thorn` CLI binary) | **No, unless you intend it.** The skill name and the CLI command are separate. Renaming the binary breaks every user's scripts. |
| npm package name | Not part of this ask. Leave it. |

**Release steps for 2.4.1**

1. Run `git mv skills/thorn skills/thornquist-cli`.
2. Edit the frontmatter `name`, the manifest `name`, and docs.
3. Run `git grep -nE '\bthorn\b'` and check that the only remaining hits are the CLI binary and intentional prose.
4. Bump `version` in `package.json` and `.claude-plugin/plugin.json`, and refresh `package-lock.json` with `npm install --package-lock-only`.
5. Add a CHANGELOG entry with a migration note: "Skill renamed `thorn` → `thornquist-cli`. Update any `/thorn` invocations. The `thorn` CLI binary is unchanged."
6. Run `claude plugin validate .`, tests and lint. Then tag `v2.4.1`.

**Risks to decide on**

- **Semver:** a rename breaks anyone who invokes the skill or the plugin by name. Strict semver would make this 2.5.0 or 3.0.0, not a patch. Shipping it as 2.4.1 is your call. If you do, state the rename in the changelog.
- **Old name:** the skill can't be aliased in place. To soften the break, ship a stub `skills/thorn/SKILL.md` for one release. It would say "renamed to thornquist-cli" and point users there. Remove it in 2.5.0.
- **Installed users:** anyone who installed `thorn` must reinstall under the new name or update through the marketplace. Say this in the release notes.

## Next actions

1. Run `claude plugin validate .` and send me the output if it isn't clean after Step 2.
2. Answer the submit-name question above.
3. Confirm whether the `thorn` binary stays as is, and whether you accept a patch bump for a breaking rename.

I can make the edits once you've answered the submit-name question and the `bin` question.