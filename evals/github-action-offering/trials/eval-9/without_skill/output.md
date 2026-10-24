# Sanity check: oxleaf-action plan

I checked this from the plan alone, since you ruled out `skill-wip/`. I didn't look at the action repo, and I didn't query GitHub.

| Item | Verdict |
|---|---|
| `runs.using: node24` in v3.4.0, move the v3 tag | ✅ Go, with conditions (1) |
| Delete v1 tags | ❌ Don't (2) |
| Keep `token` input | ✅ Right call, but the reason is wrong (3) |
| Board-deck usage numbers | ⚠️ Two of three sources don't give what you expect (4) |
| Keep the macOS / ARM README line | ⚠️ Only if CI proves it (5) |

## 1. node24 in v3.4.0

- **Risk.** If node20 is gone, hosted runners probably already force your action onto node24. In that case the declaration just removes the warning. The real exposure is self-hosted runners that are too old.
- **Minimum runner.** node24 needs a recent runner (I recall v2.327.1 or later; verify). Old Linux distros with an old glibc and old macOS versions can fail.
- **Semver.** A minimum-runner bump moved under a floating `v3` tag is a silent breaking change for those users. GitHub's own actions treat it as a major. Pick one:
  - Ship 3.4.0 if a canary passes, with the runner requirement at the top of the release notes.
  - Ship v4 if you want the clean contract.
- **Before moving the `v3` tag:**
  1. Tag `v3.4.0` first, and write down the old `v3` SHA for rollback.
  2. Run the CI matrix on node24: hosted Linux, macOS arm64, Linux arm64, and Windows.
  3. Run a canary on `@v3.4.0` in 2–3 real repos, including one self-hosted.
  4. Move `v3` last.
- **Build chores.** Set CI `node-version: 24`, bump `engines` and `@types/node`, rebuild `dist/`, and check that dependencies still work.
- **v2.** It probably shows the same warning. Decide whether it gets a patch or a deprecation notice.

## 2. Deleting v1 tags

Don't.

- **It contradicts itself.** You say "still a few users" and "nobody should be on it". Those users will get `unable to resolve action` on their next run, with no warning.
- **It breaks pins too.** It kills `@v1` and every `@v1.x.y`.
- **It's hard to undo.** You can re-push a tag, but the damage lands first.
- **Do this instead:**
  1. Count v1 users with the code-search queries in section 4.
  2. Ship a final v1.x that logs a deprecation warning and points to the migration guide.
  3. Add a README and Marketplace deprecation note.
  4. Set a sunset date (for example 6 months out), then re-count.
  5. Only then decide. Leaving the tags costs nothing.

## 3. Keeping `token`

Keep it, because removing an input is a breaking change and belongs in v4. The effort isn't the argument.

- **Warning.** Add a `deprecationMessage` in `action.yml`, plus a runtime warning when `token` is used.
- **Precedence.** Define it when both inputs are set. `api-key` should win.
- **Secrets.** Make sure `token` is masked in logs.
- **Removal.** Schedule it for v4.

## 4. Board-deck numbers

- **Marketplace installs.** There is no public install count for Actions, only stars. The count exists for GitHub Apps. Don't put "installs" in the deck.
- **"Used by".**
  - It comes from the dependency graph, counts public repos only, and lags.
  - It includes forks and abandoned repos.
  - It counts repos, not runs or users.
  - You can't split it by major.
  - It's a lower bound on public usage, and says nothing about private repos.
- **Code search for `uses: oxleaf/oxleaf-action@`.**
  - It's public, default-branch only, and excludes forks by default.
  - Results are capped, and it counts files, not repos.
  - It matches READMEs, docs, and vendored copies.
  - It misses quoted forms (`uses: "oxleaf/…"`), subpath forms, and reusable workflows.
  - Use it to split by version, which is what the v1 decision needs: `oxleaf-action@v1`, `@v2`, `@v3`. Dedupe by repo.
- **Presenting them.**
  - Label the numbers "public repos referencing the action, as of 2026-10-24", with the method in a footnote.
  - Don't add the sources together, because they overlap.
  - Don't call them "users".
  - If the board needs active usage, you need a real signal. Add telemetry only if it fits your privacy stance.

## 5. macOS and ARM self-hosted claim

A JS action is mostly platform-agnostic, so the claim is plausible. It's only true if the node24 runtime and your dependencies run there.

- Add CI jobs on `macos-latest` (arm64), `ubuntu-24.04-arm`, and `windows-11-arm` if you claim Windows.
- Hosted CI can't prove "self-hosted". Reword it, for example: "Tested on GitHub-hosted macOS and ARM64 runners. Self-hosted runners need runner ≥ 2.327.1 (node24)." Verify the version first.
- Keep the line once those jobs are green.

## Suggested order

1. Run the v1/v2/v3 code-search counts. They take 10 minutes and settle the v1 question.
2. Add the CI matrix on node24.
3. Run the canary, then tag `v3.4.0` and move `v3`.
4. Publish the v1 deprecation notice and the `token` warning.
5. Build the deck slide with the caveats in section 4.

Next step for me: if you want, I can draft the release notes and the CI matrix workflow.