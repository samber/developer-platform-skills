# Marrowfield extension 3.1.0 post-mortem: fix plan and release checklist

## Root cause

The failures share one cause: **the release assumed the user's environment matched the dev environment**.

- We assumed the CLI version, VS Code version and runtime location, and never checked any of them.
- We tested only latest VS Code stable, on a machine where the CLI is on PATH.
- The extension and the CLI ship independently, and nothing enforced their order.

| | Symptom | Root cause | Class |
|---|---|---|---|
| a | Stack trace on CLI 2.4 | Extension assumes `mfield promote` exists. CLI 2.6 shipped two days after the extension. Unhandled errors reach the UI. | Cross-component version skew, no error boundary |
| b | Cursor "not compatible" | `engines.vscode` was raised to `^1.106.0` for one API. Cursor's Code-OSS base is older. | Hard floor raised for an optional feature |
| c | Codespaces "CLI not found" | Probably the extension host can't see the container's PATH or runs on the wrong side. This is unconfirmed (see below). | Environment assumption |
| d | Flag `>= 3.1` | The flag gates on our own version, not on whether the feature can work. | Wrong proxy for capability |

## Fix plan

### Phase 0: stop the bleeding (today, about 1h)

1. **Kill the `promote` flag server-side.** This is the fastest mitigation and needs no release. It only works if the flag is read at runtime from a remote service. If it's baked into the bundle, skip to Phase 1.
2. Pin a support note: "Update CLI to 2.6+ (`<update command>`). Cursor users stay on 3.0.x until 3.1.1."
3. Confirm the Codespaces root cause (see Phase 1, item 3) so the hotfix targets the right thing.

### Phase 1: hotfix 3.1.1 (1–2 days)

**1. CLI capability gate (fixes a)**
- Add one constant, `MIN_CLI_FOR_PROMOTE = "2.6.0"`, in a single file.
- At activation and before running `promote`, run `mfield --version` and compare with real semver (`semver.gte`, with `coerce` for odd formats).
- If the CLI is too old, show: "Promote needs Marrowfield CLI 2.6+. You have 2.4.x." with an **Update CLI** button and a docs link. Never run the command.
- Secondary check: if the CLI exits with "unknown command", treat it as "CLI too old" and not as a crash.
- Wrap every `registerCommand` handler in one `safeCommand()` wrapper. It logs the full error to the Output channel, shows a short human message, and never puts a stack trace in a notification.
- Add a lint rule that bans a raw `registerCommand`.

**2. Lower `engines.vscode` (fixes b)**
- Set `engines.vscode` to the oldest version the extension truly needs. Check Cursor's base version under **Cursor → About**, and do the same for Windsurf and VSCodium.
- Guard the new API at runtime: `if (typeof vscode.<ns>.<newApi> === "function") { … } else { fallback or hide the feature }`.
- Pin `@types/vscode` to the same minimum. `vsce` then refuses a package whose `engines.vscode` is below `@types/vscode`, and the compiler rejects APIs newer than the minimum.
- Publish to Open VSX too, if we don't already. Cursor pulls from there.
- Users blocked on 3.1.0 never installed it, so they are not broken. They simply get 3.1.1.

**3. Codespaces and remote (fixes c)**

First confirm which of two causes applies. Ask an affected user to run **Developer: Show Running Extensions** and check whether Marrowfield is "Remote" or "Local".

- **Running local (UI side):** set `"extensionKind": ["workspace"]` in `package.json`, or `["workspace","ui"]` if there's a UI half. Anything that spawns the CLI must run next to the CLI.
- **Running remote, PATH mismatch:** the extension host inherits the server's env, not the user's shell rc. A CLI installed by a devcontainer feature or `postCreateCommand` into `~/.local/bin` or a profile-only PATH is invisible.

Either way, resolve the CLI in this order:
1. The `marrowfield.cliPath` setting.
2. PATH.
3. Known locations: `~/.local/bin`, `/usr/local/bin`, the npm global prefix, Homebrew paths, and `.cmd` shims on Windows.
4. A login-shell probe: `$SHELL -lc 'command -v mfield'`.

On failure, list the paths searched, the PATH value seen, and `vscode.env.remoteName`.

Add a **Marrowfield: Diagnose Environment** command. It prints the extension and VS Code versions, host app name, remote name, extension side, CLI path and version, and PATH. Support can then ask for one paste.

**4. Replace the flag (fixes d)**
- Use `enabled = remoteFlag("promote") && cliSupports("promote") && apiAvailable`.
- The remote flag is only a kill switch and rollout dial. It is never a proxy for "this build can do it".
- Never compare versions as strings. `"3.10" >= "3.1"` is true by luck and `"3.9" >= "3.10"` is wrong. Use semver, and remember that `3.1.0-beta < 3.1.0`.
- Better still, have the CLI report capabilities (`mfield capabilities --json`, or probe `mfield promote --help`). Then the extension needs no version table.

**5. Tests for 3.1.1**
- Unit tests for the capability gate at the pivot values: CLI 2.5.9, 2.6.0, 2.6.0-rc.1, 2.10.0 (string-compare trap), no CLI, garbage `--version` output, a timeout, and a non-zero exit.
- A test that a thrown error in any command handler yields a short message and no stack.
- Break the gate on purpose (always return true) and confirm the CLI-2.4 test fails.

### Phase 2: guardrails (next 2 weeks)

1. **Host and version matrix in CI** using `@vscode/test-electron` or `@vscode/test-cli`:
   - the minimum from `engines.vscode`
   - stable
   - insiders
2. **Remote matrix:** run the integration tests inside a devcontainer in CI, with the CLI installed the way the real devcontainer feature installs it. Add WSL and SSH remote as a manual item until automated.
3. **CLI matrix:** oldest supported CLI, latest CLI, and no CLI. The extension must degrade cleanly in all three.
4. **Cursor smoke test:** manual per release for now, with the version recorded in the checklist. Automate later if Cursor allows.
5. **Compatibility policy**, written in one doc:
   - which CLI versions each extension version supports (suggest the current minor and two prior)
   - the rule that `engines.vscode` only moves on a major release, or when the feature can't be guarded
6. **Release order rule:** CLI first, then the extension. The extension may ship dark, with the flag off, earlier. A CI step queries the registry or release channel and fails the extension release if `MIN_CLI_*` isn't published.
7. **Pre-release channel:** publish with `vsce publish --pre-release` and soak for 2–3 days before promoting to stable.
8. **Telemetry and alerts** (keep it privacy-respecting, with no paths):
   - activation or command failure rate by host app, VS Code version, `remoteName`, and CLI version bucket
   - alert when any bucket's error rate spikes after a release

## Release checklist

Copy this into the release PR template.

**A. Compatibility declaration**
- [ ] `engines.vscode` is unchanged, or the change is justified in the PR and is a major release.
- [ ] `@types/vscode` equals the `engines.vscode` minimum.
- [ ] Every new API newer than the minimum is feature-detected, with a fallback.
- [ ] Any new CLI dependency is recorded in the `MIN_CLI_*` constants.
- [ ] Any new CLI dependency has been **released and reachable** (registry, brew, etc.), and not just merged.
- [ ] The compatibility doc is updated.

**B. Code gates**
- [ ] Every CLI call goes through the shared resolver and `safeCommand()`.
- [ ] No user-visible message contains a stack trace.
- [ ] No version comparison is a string comparison.
- [ ] New flags gate on capability AND a remote kill switch, never only on extension version.
- [ ] `extensionKind` is correct for anything that spawns a local binary.

**C. Test matrix (all green or explicitly waived in the PR)**
- [ ] VS Code at the minimum, stable, and insiders
- [ ] CLI at the oldest supported, latest, and absent
- [ ] Devcontainer or Codespaces: CLI found, and a useful message when it isn't
- [ ] Manual smoke on Cursor, with its version recorded here: ___
- [ ] WSL or SSH remote, manual: ___
- [ ] Windows spawn (`.cmd` shim, spaces in the path)

**D. Rollout**
- [ ] Order: CLI released, then the extension published as pre-release, soaked 2–3 days, then promoted to stable.
- [ ] Open VSX published alongside the Marketplace.
- [ ] The new feature's flag is **off** at release and ramps up (5%, 25%, 100%) with dashboards open.
- [ ] The kill switch is verified to work **before** release.
- [ ] Release notes state the minimum CLI and VS Code versions.

**E. After release (first 48h)**
- [ ] Error-rate dashboards by host, remote, and CLI bucket have been checked at 1h, 24h, and 48h.
- [ ] Support and community channels have been checked for "not compatible", "not found", and stack-trace reports.
- [ ] Rollback is ready: previous version available, flag kill documented.

## Open questions

- **Is the `promote` flag read at runtime from a remote service?** If yes, Phase 0 step 1 works today. If it's static, the hotfix is the only fix.
- **Which side did the extension run on in Codespaces?** I'm inferring `extensionKind` or PATH from the symptom, but I can't confirm it without a repro. The "Show Running Extensions" check settles it in a minute.
- **What is Cursor's VS Code base version?** That sets the new `engines.vscode` floor. Look it up in **Cursor → About**, don't guess.
- **Does the CLI have a stable machine-readable version or capabilities output?** If not, adding one is a small CLI change that makes the extension gate much more robust.