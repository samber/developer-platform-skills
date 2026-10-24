# Marrowfield IDE extension: post-mortem fix plan and release checklist

Status: **provisional**. I haven't seen your repo, so the open assumptions are at the bottom.

**Next action (today):** open an Insiders/Cursor/Codespaces repro session and start the 3.1.1 hotfix (section 2).

## 1. Root cause: one broken rule, four times

The skill's contract says the extension is a thin shell over the CLI. It gates on what the CLI reports and never ships ahead of it. All four incidents are that rule broken.

| # | Symptom | Root cause | Rule broken |
| --- | --- | --- | --- |
| a | Stack trace on CLI 2.4 | The extension shipped Tuesday and the CLI shipped Thursday. The command ran `mfield promote` with no version check and no error handling. | Extension must not ship ahead of the CLI. A CLI below the minimum gets one message with the upgrade command, never a stack trace. |
| b | Cursor says "not compatible" | `engines.vscode` was raised to `^1.106.0` for one API. A Code-OSS fork on an older base can't install it. | The floor must sit at or below the oldest fork's base. APIs forks lack must be feature-detected. |
| c | Codespaces "CLI not found" | Cause not yet proven (see 2.4). | In remote workspaces the CLI is found on the remote host, and `extensionKind` is set deliberately. |
| d | Flag `extensionVersion >= 3.1` | The flag gates on the extension's own version, so it is on for a 3.1.0 extension paired with CLI 2.4. | Gate on capabilities the CLI or API reports, not on the extension's version. |

Amplifier: you test on latest VS Code stable only. The gates require min host, newest, pre-release, one fork and one remote target. Four of those five cells were untested, and each incident sits in an untested cell.

## 2. Fix plan

### 2.1 Immediate (hotfix 3.1.1, same day)

Published versions never republish, so roll forward with a patch. Ship the same packed `.vsix` to the VS Code Marketplace and Open VSX.

1. **Gate `promote` on the CLI.**
   - At activation, lazily run `mfield --version`. Parse it as semver, not as a string.
   - Below 2.6.0, hide or disable *Promote preview*. If a user triggers it anyway (palette, keybinding), show one message: "Promote needs Marrowfield CLI 2.6+. Run `<upgrade command>`" with an Upgrade button.
   - Wrap every CLI spawn so a non-zero exit or "unknown command" becomes that message. Raw exception text never reaches a notification. Log details to the output channel with secrets masked.
2. **Lower `engines.vscode`** to the Code-OSS base of the oldest Cursor/Windsurf/VSCodium build your users run.
   - Check Cursor's base in Help > About, and write the number down (A2).
   - Pin `@types/vscode` to the same floor. Otherwise the compiler accepts APIs the floor lacks, which is how the bump happened.
   - Feature-detect the new API (`if (typeof vscode.x?.newApi === 'function')`). Without it, fall back or hide the feature on older hosts.
3. **Replace the flag** `extensionVersion >= 3.1` with `cliCapabilities.includes('promote')`, or `cliVersion >= 2.6.0` until the CLI reports capabilities (see 2.3). A remote flag may remain as a kill switch that only turns the feature off.
4. **Codespaces**: diagnose before fixing, because the cause is unproven. Reproduce in a Codespace and in a plain dev container, then check in order:
   1. `extensionKind`. If `ui` is listed first, the extension runs on the laptop and looks for the CLI there, which would fit "installed in the container, not found". A CLI-spawning extension should be `["workspace"]`.
   2. The extension host's `PATH` versus the terminal's. A CLI installed to `~/.local/bin` via a devcontainer feature or `postCreateCommand` can be absent from the host's environment, or installed after activation.
   3. Detection cached as "not found" and never retried.
   4. A Windows-only or macOS-only binary-name assumption.

   Then fix the actual cause, whichever it is, and add:
   - a `marrowfield.cli.path` setting;
   - a "Re-check CLI" command;
   - an output-channel line listing every path searched.

   If the repro points to something else, the plan changes. Don't ship a guess.
5. **Changelog** for 3.1.1: "Lowered minimum VS Code to X; promote requires CLI 2.6+; fixed CLI detection in remote workspaces".
6. **Announce** in the 3.1.0 release issue and the docs. CLI 2.4 users get the upgrade command. Cursor users get "update to 3.1.1".

**Version scheme check:** if you use the odd-minor-pre-release convention, `3.1.x` is on the pre-release channel. Confirm how 3.1.0 was published. If it went out as a stable release on an odd minor, the Marketplace's channel meaning is muddled, and the next minor (3.2.0) should be the stable line. A pre-release that is stuck must stay above stable (A5).

### 2.2 Short term (this sprint)

- **Test matrix in CI** (`@vscode/test-cli`): min `engines.vscode`, current stable, Insiders. Add Cursor via a manual smoke test or `@vscode/test-electron` pointed at its executable, plus one dev-container/Codespaces target. Run these against CLI min supported, N-1, and latest.
- **Unit test the CLI-too-old path** with a fake `mfield` shim that prints `2.4.0` and exits 1 on `promote`. The test fails if a stack trace reaches the UI.
- **Compat matrix** published in the README and docs (below), updated every release.
- **Regression-prove the gates** per your own rule: break the code on purpose (remove the version check, set the floor back to 1.106) and confirm the tests fail.

### 2.3 Structural (next quarter, needs the CLI owner)

- Add `mfield capabilities --json` (for example `{"cli":"2.6.0","features":["promote"],"apiVersion":"..."}`). This lets the extension gate on facts rather than on version arithmetic. The contract belongs to the CLI interface design, so it needs the CLI owner. Until then, use the version fallback.
- Treat a missing JSON field as a version mismatch, not a crash.
- Move to a **release train**: CLI release first, then the extension. A feature spanning both is not released until the CLI containing it is on the registry and the install path. The extension's release pipeline checks that required CLI version is published and fails otherwise.

## 3. Compatibility matrix (publish with 3.1.1)

| Extension | Min CLI | Min VS Code (`engines.vscode`) | API version | Status |
| --- | --- | --- | --- | --- |
| 3.1.1 | 2.4.0 (A3); `promote` needs 2.6.0, capability-gated | ≤ oldest Cursor base (A2) | per CLI | supported |
| 3.1.0 | 2.6.0 de facto, unenforced | 1.106.0 | per CLI | superseded by 3.1.1 |
| 3.0.x | 2.4.0 (A3) | previous floor (A4) | per CLI | security fixes until `<date>` |

## 4. Release checklist (every release)

**Before building**
1. List what changed. If the release uses a new CLI feature, confirm that CLI version is **already published** (release train).
2. If `engines.vscode` changed: it may only *rise* in a minor, with a changelog line, and never above the oldest fork's base (Q3 users). `@types/vscode` equals the floor.
3. Any API that is new, proposed, or chat/language-model related is feature-detected. Check each against the fork's host version.

**Gates, all must pass**
4. Integration tests green on: min host, newest stable, Insiders, Cursor (or the main fork), one remote target (dev container/Codespaces). All run against a real sandbox account.
5. Minimum-CLI check covered by a test: CLI below minimum gives a single message and no stack trace.
6. Feature flags reference CLI/API capabilities, never `extensionVersion`.
7. Untrusted-workspace behaviour tested.
8. No usage event fires with host telemetry at `error` or `off` (tested).
9. Compatibility matrix updated.
10. Secret scan of the packed `.vsix` is clean.

**Publish**
11. `vsce package` once. Publish that exact file to both registries (`vsce publish --packagePath … --azure-credential` or `--oidc`; `ovsx publish … --trusted-publishing`). Confirm identical hashes. Global Azure DevOps PATs stop working 2026-12-01, so move off PATs if you haven't.
12. Version is `major.minor.patch`, and the channel matches the odd/even convention.

**After publish (first 48 h)**
13. Install from each registry into a clean VS Code, Cursor and Codespace and run the main job once.
14. Watch weekly active users by version (from the server-side `User-Agent`), first-run success (CLI found, login done, first job done) and the share of users on supported versions.
15. Rollback is roll-forward: republish the last good code as a higher patch. Keep the hotfix path rehearsed.

## 5. Process changes

- Put a **"no extension release before its CLI"** rule in the release runbook, with the checker in CI.
- Replace "tested on latest stable" with the matrix in section 4 in your definition of done.
- Add a line to the post-mortem record: root cause was untested cells plus gating on extension version.

## Assumptions (confirm before treating the plan as final)

| ID | Assumption | Drives | Who confirms |
| --- | --- | --- | --- |
| A1 | A single VS Code-API extension, no JetBrains plugin, published to both registries | Sections 2 and 4 | Extension owner |
| A2 | Oldest fork users run is Cursor; its Code-OSS base is unknown | The `engines.vscode` floor | Extension owner, check Help > About in Cursor |
| A3 | The oldest CLI you still support is 2.4.0 | The compat matrix and the version gate | CLI owner |
| A4 | The pre-3.1 floor is known and still works | The 3.0.x row | Extension owner |
| A5 | You may or may not use the odd/even pre-release convention | Version numbers | Release owner |
| A6 | The Codespaces cause is unproven; `extensionKind` and `PATH` are the top hypotheses | 2.1 step 4 | Repro in a Codespace |

I left out telemetry, auth and deprecation steps because none of the four incidents touched them.