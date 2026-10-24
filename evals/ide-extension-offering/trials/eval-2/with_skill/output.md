# Harrowgate VS Code extension: design review

**Plan status: provisional.** I couldn't ask you the interview questions, so the open assumptions are at the end. Please confirm them before you build.

**Verdict:** building the extension is right, because inline findings are a job that needs editor UI. Four of the seven design decisions break the extension contract and need changes. Two more need fixes in how they work, and one is fine.

## What to change, in priority order

| # | Your design | Verdict | Change |
|---|---|---|---|
| 1 | Auto-read `.env` for `HGATE_TOKEN` | ❌ Remove | Never read workspace files for credentials without an explicit user action. In an untrusted workspace, a cloned repo's `.env` could point the extension at an attacker's token. Scans would then run under the attacker's org. It is also the kind of file your own product flags. |
| 2 | API key in `harrowgate.apiKey` setting | ❌ Remove | Settings sync, dotfile repos and support screenshots all publish it. Use the CLI's login (see "Auth" below) or put a pasted key in `SecretStorage`. |
| 3 | `curl -sSL https://get.harrowgate.io \| sh` | ❌ Remove | Never use `curl \| sh` from an extension. It fails on locked-down fleets and in air-gapped dev containers, and it runs unreviewed remote code with the user's rights. Detect `hgate` on `PATH` and at a configurable path. If it's missing, show one message with a pinned-version install command and let the user run it. |
| 4 | Direct REST calls with axios | ❌ Replace | Two implementations of one behaviour drift. Your enterprise customers need the proxy, custom CA, SSO, region and retry handling the CLI already has. Run `hgate scan --json`. Keep the typed responses by generating the TypeScript types from a JSON schema that the CLI publishes for its `--json` output, so both sides share one contract. |
| 5 | Activate on `*` | ❌ Replace | Activate on specific events: your commands, your view, and `workspaceContains` for the manifest and lockfile patterns you scan. Check the CLI lazily, after activation. Keep the status always current with a status-bar item and a file watcher once activated. |
| 6 | Scans in the extension host, because spawning felt flaky | ⚠️ Fix the cause | Heavy work must run outside the extension host thread, which every other extension shares. Find out why spawning flaked. The usual causes are a GUI-launched `PATH` on macOS, a Windows `.cmd` shim, no timeout, or the remote `PATH` in a dev container. Then fix it with `spawn` and an args array, a resolved absolute CLI path, a timeout, and cancellation tied to a `CancellationToken`. |
| 7 | Findings as inline diagnostics | ✅ Keep | This is the job that justifies the extension. Build it from the CLI's `--json` output. Never print raw secret values into the Problems panel, hovers or the output channel. Show a redacted fingerprint and the rule. |

## Dev containers and Codespaces

Most of your enterprise customers work in dev containers and Codespaces, so this affects the whole design.

- **Set `extensionKind: ["workspace"]`.** The extension then runs on the remote host, so the CLI has to exist there. Your laptop install won't be seen.
- **Detect the CLI on the remote.** If it's missing, show the pinned install command, as in change 3. Document how to bake it into the dev container image or `postCreateCommand`.
- **Login can't come from the laptop.** A remote CLI can't see the laptop's session. There are two paths:
  - **Headless/Codespaces path:** the CLI reads `HGATE_TOKEN` from its own process environment, such as a Codespaces secret or `remoteEnv`. This replaces the `.env` idea. The user sets it, and the CLI reads it, not the extension.
  - **Interactive path:** if Harrowgate offers OAuth for desktop clients (Q4), promote a VS Code `AuthenticationProvider` and route callbacks through `env.asExternalUri`.
- **Open links with `env.openExternal`.**
- **Mark the listing "desktop only".** An extension that spawns processes can't run on vscode.dev.
- **Test one remote target.** Run the integration suite against a dev container and Codespaces before release.

## Auth

1. **Default:** reuse the CLI login through a command such as `hgate auth token --json`. Hold the token in memory only. Never write it to settings, logs or output channels. The CLI doesn't have this command yet, so see assumption A1.
2. **Promoted:** an `AuthenticationProvider` over your OAuth, if you offer OAuth to desktop clients.
3. **Fallback only:** a pasted key written straight to `SecretStorage` and masked in every log.
4. **Workspace trust:** declare `capabilities.untrustedWorkspaces` as `limited`. Disable scanning and CLI execution until `workspace.isTrusted`, and re-enable on `onDidGrantWorkspaceTrust`.
5. **Exposed keys:** if any prototype build with `harrowgate.apiKey` reached a user, rotate those keys.

## Missing from the design doc

**Registries and identity**
- **Publish the same packed `.vsix` to the VS Code Marketplace and Open VSX.** Cursor, VSCodium and Windsurf users otherwise get a lookalike.
- **Claim the VS Code publisher ID and the Open VSX namespace now.** File the Open VSX ownership claim, or the listing shows an unverified warning.
- **Start the verified-publisher clock early.** The badge needs the extension listed for 6+ months and a 6-month-old domain.
- **Publish the publisher and extension IDs on your docs.** Customer IT teams use them for `extensions.allowed` allowlists.

**Publishing**
- **Use short-lived credentials.** Publish with `vsce publish --oidc` or `--azure-credential`, plus `--packagePath`, and `ovsx publish --trusted-publishing`.
- **Date pressure:** global Azure DevOps PATs stop working on 2026-12-01, about five weeks from now, so don't build on one.
- **Scan the packed file.** Scan the packed `.vsix` for secrets before publishing.

**Telemetry**
- **Follow the host level.** Use `env.createTelemetryLogger` or `@vscode/extension-telemetry`, which honour `telemetry.telemetryLevel`. Your own setting can only narrow collection.
- **Collect no source, paths or tokens.** Ship `telemetry.json` and publish the event list.
- **Prefer server-side metrics.** Send a versioned `User-Agent` on every CLI and API call, e.g. `harrowgate-vscode/1.0.0 (vscode 1.104; linux-x64)`.

**Compatibility and fleets**
- **Publish a compatibility matrix.** List extension version, minimum `hgate` version, `engines.vscode` and API version.
- **Check the CLI version at activation.** Below the minimum, show one upgrade message, never a stack trace.
- **Set `engines.vscode`** at or below the Code-OSS base of the oldest fork your users run.
- **Honour `http.proxy` and custom CAs.** The CLI the extension spawns must honour them too.
- **Document offline `.vsix` install** for air-gapped fleets.
- **Add `SECURITY.md`** and a compromised-token runbook per registry.

**First run**
- **Add a walkthrough.** It should check the CLI, sign in, and show one real finding.

## Verdict per job

| Job | Surface | Verdict |
|---|---|---|
| See findings inline | Thin shell: diagnostics, status bar, walkthrough over `hgate --json` | **Go** |
| One-click login | Part of the same shell | **Go** |
| Agent access to scans | MCP server, not the extension | Out of scope here |
| Dashboards in a webview | Rich extension | **Starved**. Promote only for a job a tree view or quick pick can't show, and only with a staffed owner. |
| JetBrains plugin | Second codebase | **Starved**. Promote when JetBrains is your second-largest group and a Kotlin or Java owner exists. |

## First-release sequence

| # | Step | Effort | Depends on |
|---|---|---|---|
| 1 | Claim the VS Code publisher ID, Open VSX namespace and (if planned) JetBrains plugin ID. Publish the IDs on your docs. | an hour | – |
| 2 | Confirm the CLI contract: `--json` schema, exit codes, `auth token --json`, minimum version. | a week (CLI team) | – |
| 3 | Build the thin shell: CLI detection, scan command, diagnostics, status bar, trust gating. | a few weeks | 2 |
| 4 | Add remote support: `extensionKind`, remote CLI detection, `asExternalUri`, then dev container and Codespaces tests. | a week | 3 |
| 5 | Add the telemetry logger, `User-Agent`, `telemetry.json` and the walkthrough. | days | 3 |
| 6 | Set up OIDC publishing for both registries, package once, scan, publish the same file. | days | 1, 3 |
| 7 | Publish an early public version to start the verified-publisher clock. | – | 6 |

## Gates before the first release

- The `.vsix` hash is identical on both registries, and the packed-file secret scan is clean.
- Integration tests pass on the minimum and newest VS Code, Insiders, Cursor (or another main fork) and one remote target, against a real sandbox account.
- The compatibility matrix is filled, and a test covers the minimum-CLI check.
- No usage event fires with host telemetry at `error` or `off` (tested).
- Untrusted-workspace behaviour is tested.

## Assumptions and questions to confirm

| ID | Assumption | Drives | Who confirms |
|---|---|---|---|
| A1 | `hgate` supports `--json` output and a token or session command. If not, add them before the extension. | Changes 4 and the auth section | CLI owner |
| A2 | No language server exists. Diagnostics come from CLI output. | Architecture | Tech lead |
| A3 | VS Code and forks are your main editors. I don't know your JetBrains share. | Editors and registries | Product |
| A4 | Harrowgate has no OAuth for desktop clients yet, so the CLI login path is the default. | Auth | Platform team |
| A5 | A named owner exists for the extension after launch. | Go/no-go | You |
| A6 | Some customers use proxies with custom CAs or air-gapped machines. | Fleet support | Support |

If A1 is false, adding `--json` and a token command is the first task. The extension is only as stable as that contract.