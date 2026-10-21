# Distribution channels, pinning and manifests

Installer flags and manifest schemas change fast; each tool's own documentation is the authority on exact syntax, and a README command copied from here is worth a test install first.

## Contents

- Channel table
- Git-based installs and refs
- Bundled with the code
- Manifest fields
- Release-note install block

## Channel table

No installer reads `SKILL.md` `metadata.version`. They resolve a git tag, a commit, or a plugin manifest `version`.

| Channel | Pin syntax | Unpinned / update behaviour | Version source used |
| --- | --- | --- | --- |
| GitHub CLI skills (`gh skill`) | `gh skill install owner/repo skill@v1.4.0`, or `--pin <tag-or-sha>` | Unpinned resolves the latest tagged release, then default-branch HEAD. Pin explicitly: the recorded ref after an unpinned install is not guaranteed to be a tag. `gh skill update` skips pinned skills. | Git tag or SHA; writes repo, ref, pin and tree SHA into the installed `SKILL.md` frontmatter |
| skills installer (`npx skills`) | `npx skills add owner/repo#v1.4.0`, or a `/tree/<ref>/<path>` URL | Without a ref, follows the default branch; a branch ref floats, a tag or SHA holds. | None; project lockfile `skills-lock.json` records `ref` and a content hash |
| Claude Code plugin marketplace | `/plugin marketplace add owner/repo#v1.4.0`; a third-party marketplace entry's `source` with `ref` and/or 40-char `sha` (sha wins) | Version = `plugin.json` `version`, else marketplace entry, else commit SHA. A set but unbumped `version` makes update report "already latest". | Manifest `version` or commit SHA |
| Cursor plugins | Marketplace add with a git ref | Follows git commits rather than the manifest `version`; update timing is set by the editor. | Commit |
| Codex plugins / skill installer | `--ref <ref>` (default `main`), or a `/tree/<ref>/<path>` URL | Re-install at the new ref; plugin-level pinning less documented. | Ref; manifest `version` |
| Gemini CLI extensions | `gemini extensions install <repo> --ref=<branch-or-tag-or-commit>` | Git installs track HEAD of the ref; GitHub-Releases installs check the release marked Latest. `--auto-update`, `--pre-release` exist. | Ref or release; `gemini-extension.json` `version` displayed |
| Package registry (npm, PyPI, crates.io, Go modules) | The package version itself | Upgrading the package upgrades the bundled skill. | The package version |

Mixed-manifest trap: one installer keys its cache on manifest `version`, another ignores it. The lockstep rule resolves it: bump every plugin manifest from one source on every release, and never leave one manifest set but unbumped.

## Git-based installs and refs

- Curated marketplaces pin exact commits: in one official plugin marketplace, nearly every git-sourced entry carries a `sha`, and only one pins a version tag. Expect a curator to bump your `sha`; make each tag's commit the one worth pinning.
- Users who install from the default branch get whatever is merged, including unreleased features. Two fixes, pick one:
  - Keep the default branch equal to the latest release; develop on a `dev` branch and merge at release time.
  - Leave development on the default branch and print the tag-pinned command everywhere users copy install commands.
- Renames: ship them in a major release with a stub skill under the old name pointing at the new one. Some marketplaces also carry an append-only old-name -> new-name map; add an entry there as a supplement, never as the only signal.

## Bundled with the code

The only rung where the skill version equals the code version by construction.

- **npm**: put skills at `skills/<name>/SKILL.md` (or `dist/skills/<name>/`) inside the published package and list them in `files`. The skills installer can link skills from installed dependencies so they update with the package (the sync command is marked experimental; check its current name and flags). A `package.json` `skills` array can also declare skill sources; pin git ones to a ref.
- **CLI with an install subcommand**: Playwright's CLI ships its skill inside the npm package; `playwright-cli install --skills` copies `SKILL.md` and `references/` into the workspace, so the installed skill always equals the installed CLI.
- **Framework with bundled docs**: Next.js bundles its docs in the package (`node_modules/next/dist/docs/`); the project generator writes an `AGENTS.md` telling agents to read them, and the dev server refreshes it. Use this for knowledge every call needs; keep skills for workflows.
- **Separate skills repo, for contrast**: Supabase releases its skills apart from its CLI, so each skill states minimum CLI versions per command. The lockstep rule removes the need for those lines.
- **Go library**: the module zip already carries `skills/`, so `$GOMODCACHE/<module>@<version>/skills/` is a version-matched copy an agent can be pointed at.
- **Go binary**: embed `skills/*/SKILL.md` and `skills/*/references` with `//go:embed` from the module root (embed cannot reach parent directories), and expose `<tool> skills install` / `<tool> update` that writes or syncs them. Record the synced version in a small state file so the binary can detect drift.
- **Python**: include `skills/` as package data and expose a console command that copies them into the agent's skills directory.
- **Container image**: copy `skills/` into the image at a documented path for agents running inside it.

Runtime drift notice: on each run, read the recorded skill version, compare with the binary's version, and on mismatch print one line an agent can act on. Skip it in CI and for dev builds, and offer an environment variable to silence it.

## Manifest fields

All at repo root, all pointing at `./skills/`.

- `.claude-plugin/plugin.json`: `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`.
- `.claude-plugin/marketplace.json`: `name`, `owner`, `plugins[]` with `name` (equal to the plugin) and `source: "./"`. Leave `version` out of the entry: when both are set, `plugin.json` silently wins and the validator warns.
- `.codex-plugin/plugin.json`: plugin fields plus `skills: "./skills/"` and an `interface` block (`displayName`, `shortDescription`, `developerName`, `category`, `capabilities`, `websiteURL`).
- `.cursor-plugin/plugin.json`: plugin fields plus `displayName` and `skills: "./skills/"` (`rules: "./rules/"` only if the repo ships Cursor rules). Updates follow commits; keep `version` bumped anyway for gate 2.
- `gemini-extension.json`: `name`, `version`, `description`; must sit at repo root or archive root. The extension's `skills/` directory is discovered without extra fields. Gallery crawlers index public repos tagged with the `gemini-cli-extension` topic.

Copy `author`, `homepage`, `repository` and `license` from the repo's existing package metadata; never leave placeholder owners in a published manifest.

## Release-note install block

Generate this in the release job so the tag is never typed by hand:

```
Agent skill for this release:
  gh skill install owner/acme acme-cli@v1.4.0
  /plugin marketplace add owner/acme#v1.4.0
  npx skills add owner/acme#v1.4.0
  gemini extensions install https://github.com/owner/acme --ref=v1.4.0
Already installed? Re-run with the new tag, or `acme skills update` if bundled.
```
