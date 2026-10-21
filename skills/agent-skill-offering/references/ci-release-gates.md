# CI and release gates

## Contents

- Where each gate runs
- Gate 2: version equality
- Gate 3: content check for a CLI
- Gate 3: content check for a library
- Gate 4: changed-surface check
- Gate 5: golden agent tasks
- Gate 6: security scan
- Plugin-tool agreement checks
- Release-tool hooks
- Spec validator in CI

## Where each gate runs

| Gate | Pull request | Release job (on tag) |
| --- | --- | --- |
| 1 Spec validation | yes, on `skills/**` changes | yes |
| 2 Version equality | yes, against the version source of truth | yes, before the tag is created (release PR or `make release`); again on the tag as a backstop |
| 3 Content check | yes | yes, against the release build, before tagging |
| 4 Changed-surface | yes | no |
| 5 Golden agent tasks | optional, nightly | yes, once adopted |
| 6 Security scan | yes, on `skills/**` changes | yes |

Put gates 2 and 3 before the tag and before any publish step. A failure on the tag itself means deleting that tag; a failure after the registry upload leaves a published release with a stale skill.

## Gate 2: version equality

GitHub Actions example, tag-triggered backstop. On pull requests, run the same command with the version read from the source-of-truth file, or for tag-only repos from `git describe --tags --abbrev=0` (checkout with `fetch-depth: 0`):

```yaml
on:
  push:
    tags: ["v*", "*-v*", "*/v*"]  # plain, release-please component, and Go submodule tags
jobs:
  skill-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Skill version matches tag
        run: |
          python3 scripts/check-skill-version.py "$GITHUB_REF_NAME" \
            --skills-dir skills \
            --manifest .claude-plugin/plugin.json \
            --manifest .claude-plugin/marketplace.json \
            --manifest .codex-plugin/plugin.json \
            --manifest .cursor-plugin/plugin.json \
            --manifest gemini-extension.json
```

Copy `scripts/check-skill-version.py` into the tool's repo (for example `scripts/`) rather than referencing this skill's install path. When the version lives in a file, pass that value instead of the tag and add a second check that the tag equals it. For monorepo tags (`acme-cli-v1.4.0`, `cli/v1.4.0`), add `--tag-prefix acme-cli-` or `--tag-prefix cli/`.

## Gate 3: content check for a CLI

Assert, in both directions, that the skill and the built binary agree.

1. Build the binary the release will publish, with the same version stamping. With goreleaser, run `goreleaser build --snapshot --clean --single-target` in a `skill-gates` job and make the publishing job depend on it.
2. Extract candidate invocations from fenced code blocks and inline code in `skills/**/*.md`: lines starting with the binary name. Skip blocks marked as bad examples (for example lines under a `✗` label) and record intentionally-wrong invocations in the allowlist instead.
3. Stale direction: for each invocation, split into subcommand path and flags. Run `<bin> <subcommand path> --help 2>&1` and assert every flag appears in its output. Capture stderr too, and compare flag names without leading dashes: Go's standard `flag` package prints help to stderr and shows `-yes` for a flag users type as `--yes`. Do not assert exit code 0, since some parsers exit 2 after printing help; assert the output is help text, not an "unknown command" error. Check nested subcommands at every level, not only the first two tokens.
4. New-surface direction: diff the public command list against the last release's and fail on any added command the skill never mentions and the allowlist does not exempt. Never require coverage of the whole surface: that pushes the skill toward the command dump it should avoid.
5. When the skill tells agents which JSON fields to read, run the command with `--json` against a fixture or dry-run and assert each documented field is present.
6. Assert the packaged artifact contains the skill: `tar tzf dist/*.tar.gz | grep SKILL.md`, `npm pack --dry-run 2>&1 | grep skills/`, or the wheel's file list.
7. Fail with the file, line and missing token.
8. Fail on allowlist rot too: an allowlisted "removed" flag that exists again means the skill and the allowlist are both wrong.

Real drift this catches, from public issue trackers: a skill naming a JSON field absent from the payload type (the old checker compared only the first two tokens); a skill listing two commands after a third command group shipped; a skill listing four backends while the code supported six; a CLI-bundled skill still teaching APIs removed a major version earlier while every check stayed green.

A machine-readable command tree makes steps 3-4 robust: add a hidden `commands --json` subcommand (cheap in any CLI framework), or use the framework's doc generator. Without one, parsing the top-level usage text works but breaks whenever the usage layout changes.

Allowlist whole invocations or tokens the skill names on purpose to say they are gone ("`--legacy` was removed in 2.0"), in a small file next to the check, never by loosening the parser.

## Gate 3: content check for a library

- Extract fenced code blocks in the library's language from the skill.
- Compile or type-check each one against the release build: `go vet` on generated `_test.go` example files, `tsc --noEmit` on extracted `.ts` files, `python -m py_compile` plus an import smoke test, `cargo check` on a scratch crate.
- Mark intentional pseudo-code blocks with a fence label the extractor skips (for example `text`).

## Gate 4: changed-surface check

On pull requests:

1. Generate the public-surface snapshot on base and head: CLI help tree, exported API list (`go doc -all`, `api-extractor`, a stub generator). Run the head's snapshot script against both builds; the base may predate the script.
2. If the snapshot changed and no file under `skills/` changed, fail with "public surface changed; update skills/ or add label skill-unaffected".
3. Let the label bypass the gate, so a reviewer decides, never the author's silence.

## Gate 5: golden agent tasks

- Pick 3-10 tasks from real agent failures (interview question 4), each with a binary pass condition: command exit code, a file produced, a test passing.
- Run each task with and without the skill installed, on a pinned agent and model, against the built tool. Record two numbers per release: trigger rate (the agent loaded the skill) and pass rate.
- A low trigger rate is a description problem, or a sign the knowledge belongs in always-loaded docs (step 1 of the skill), not a content problem.
- Treat a drop between releases as a release blocker only once the suite is stable; until then, report it.
- Published benchmarks show skills help on average but least in software-engineering tasks, so expect small, noisy gains and judge on your own tasks.

## Gate 6: security scan

- Run an agent-skill security scanner over `skills/` in CI. Snyk Agent Scan checks skills for prompt injection, malicious code and downloads, credential handling, secrets and third-party content exposure (`docs/risks.md` in its repo lists every risk):

```yaml
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0
      - name: Run Snyk Agent Scan
        run: uvx snyk-agent-scan@latest --ci --dangerously-run-mcp-servers --skills ./skills
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

- `SNYK_TOKEN` comes from a repository or organization secret; never write the token inline.
- `--dangerously-run-mcp-servers` starts and contacts every MCP server the scanned configs declare, so run it only on trusted code, never on `pull_request_target` from forks. With only `./skills` as target it starts nothing; `--ci` requires it.
- Fork pull requests get no secrets, so the scan fails there: skip the step with `if: github.event.pull_request.head.repo.full_name == github.repository` and rely on the release-job run.
- `--ci` fails the job on findings or runtime failures and requires `--dangerously-run-mcp-servers`.
- `--skills` is an on/off switch, on by default; `./skills` is the scan target.
- `ubuntu-latest` ships no `uv`, hence the `setup-uv` step, pinned to a commit SHA because the action publishes no major-version tag.
- The scan uploads skill content to Snyk; clear that for private repos.
- Pin a version (replace `@latest` with `@<version>`) to make release gates reproducible: the scanner's output and risk names change between releases, so gate on the exit code, never on parsed output.
- Treat a "third-party content exposure" finding as a design defect: remove the instruction that makes the agent fetch and follow remote content. When fetching is the tool's purpose, mark fetched content as data, never instructions, and pass `--ignore-risks third_party_content_exposure` with the reason in a comment.
- Admission scanners are evadable, so a clean scan is a floor, never a trust claim.

## Plugin-tool agreement checks

Some plugin CLIs ship their own agreement gates: a validate command that warns when `plugin.json` and the marketplace entry both set `version`, and a tag command that refuses to tag when they disagree. Run them in the release job in addition to `scripts/check-skill-version.py`.

## Release-tool hooks

Bump every version field in the commit the tag points at. A bump made after tagging never reaches the tag.

- **release-please**: list each `SKILL.md` as `{type: generic, path: skills/<name>/SKILL.md}` and annotate both version lines: `version: "1.4.0" # x-release-please-version` in the frontmatter and `Skill version: 1.4.0 <!-- x-release-please-version -->` in the body (the generic updater only touches annotated lines; `scripts/check-skill-version.py --write` keeps both annotations). List JSON manifests with `{type: json, path: ..., jsonpath: $.version}`. The bump lands in the release PR, which the tag then points at.
- **Any tool**: after the bump step, run `git diff --exit-code` in CI on a fresh bump to catch a file the bump config forgot.
- **changesets**: run a small script in the `version` step that writes the new package version into skills and manifests, before the version PR merges.
- **goreleaser**: it runs after the tag exists, so it cannot bump. Bump beforehand (make target or release PR), then use `before.hooks` to run gate 2 with `{{ .Version }}`, list `skills/**` in `archives.files`, and put the tag-pinned install block in `release.footer`.
- **Plain tags**: a `make release VERSION=x.y.z` target that bumps, runs gates, commits, tags and pushes in one step:

```make
release:
	python3 scripts/check-skill-version.py $(VERSION) --write --skills-dir skills $(MANIFESTS)
	go build -o ./bin/acme ./cmd/acme && ./scripts/check-skill-content.sh ./bin/acme
	git commit -am "chore: release v$(VERSION)"
	git tag v$(VERSION) && git push origin HEAD v$(VERSION)
```

`MANIFESTS` holds one `--manifest <path>` per manifest file. Build an explicit binary path: `go build ./...` with several packages writes no binary, and the check would silently run whatever `acme` is on PATH. Add the release version stamping (`-ldflags`) the real build uses. `check-skill-content.sh` stands for whatever gate 3 script the repo wrote.

## Spec validator in CI

The spec's reference validator `skills-ref` is published on PyPI as an alpha (Python 3.11+); its own repository calls it a demonstration artifact. Pin its version (`pip install skills-ref==<version>`), check the installed entry-point name before writing the CI command, and expect the pin to need bumping when the spec moves.
