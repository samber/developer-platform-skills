# Tollbridge VS Code extension: launch plan review

Status: **provisional**. The interview questions were unanswered, so open assumptions are listed at the end. I applied the `ide-extension-offering` skill and its three references.

**Yes, change several things. Four items would break or damage the launch:**

1. **`1.0.0-beta.1` is rejected.** The VS Code Marketplace accepts only `major.minor.patch`.
2. **`vsce publish minor` in CI is wrong in three ways.** It bumps the version, commits and tags, and it rebuilds from source instead of publishing the file you tested.
3. **The Azure DevOps PAT stops working on 2026-12-01.** That is about 3 weeks after your launch, whatever its 90-day expiry says.
4. **`tollbridge-dev` is permanent.** You cannot rename it later. The extension ID is `<publisher>.<name>`, and customer allowlists key on it.

## Findings, ranked by blast radius

| # | Your plan | Problem | Change |
| --- | --- | --- | --- |
| 1 | Publisher `tollbridge-dev`, "rename later" | The publisher ID and extension name are permanent, and removal reserves the name forever. Security teams at 3,000 paying teams will allowlist the ID, so a rename strands them. | Decide the final publisher ID **before the first publish**. Claim `tollbridge` now if it is free. If marketing's brand is not final, ship under the ID you can live with. Do not plan on moving. Keep the display name editable, but note that changing it revokes a verified badge. |
| 2 | `vsce publish minor` on every tag | It bumps, commits and tags, which collides with a release workflow that already owns tags. It also re-packages from source, so the shipped bytes differ from what you tested. A tag-triggered bump can loop. | Run `vsce package` once, scan the packed `.vsix` for secrets, run tests against it, then `vsce publish --packagePath tollbridge.vsix`. The version comes from `package.json`, set before tagging. |
| 3 | Global PAT ("all accessible organizations"), created by the CTO | Global Azure DevOps PATs stop working on **2026-12-01**. The all-organizations scope is far too broad, since a leak lets an attacker push an update to every install. It is also tied to one person's account, and a "90-day" custom expiry can be shorter than it looks. | Use `vsce publish --oidc` from GitHub Actions, with a trusted-publishing policy registered on the Marketplace (repo and workflow). Set `permissions: id-token: write, contents: read` and use Node 22+. Alternatively use `--azure-credential` with workload identity. Give CI the **Contributor** role, never Owner. **Delete the PAT** once OIDC works. The OIDC path never falls back to a PAT, so do not keep one as a silent backup. Revoke the current PAT now. |
| 4 | Marketplace only, `.vsix` sideload for Cursor and VSCodium | Marketplace terms limit use to Microsoft products. Cursor and VSCodium users search **Open VSX** and install whatever matches your name, possibly a stranger's lookalike. | Publish the **same `.vsix`** to Open VSX. Create the namespace (`ovsx create-namespace tollbridge`) and file the ownership claim on `EclipseFdn/open-vsx.org`, or the listing shows an unverified warning. Publish with `ovsx publish tollbridge.vsix --trusted-publishing` from CI, with no `OVSX_PAT` in that job. Have legal read the Open VSX Publisher Agreement first, because it grants Eclipse redistribution rights. If you cannot get trusted publishing working, use a namespace-scoped token on a Contributor account and calendar its expiry. Keep the sideload instructions only as the offline and air-gapped path. |
| 5 | Version `1.0.0-beta.1` "so people know it's early" | Rejected by the Marketplace (see above). | Use the pre-release channel: **odd minor for pre-release, even minor for release**. Recommended: ship `0.1.0` with `vsce package --pre-release`, then publish that file. Go GA at `1.0.0` (even minor). After GA, pre-release builds are `1.1.x`, which must stay above stable. Put "Beta" in the README and the listing description. Pre-release and release share one listing and README, so write both channel-neutral. Set `engines.vscode >= 1.63.0`. |
| 6 | Icon is the SVG logo | The Marketplace needs a PNG of at least 128 px. SVG icons are not accepted. | Export a PNG at 256 px or more. Keep the SVG for the README, but with HTTPS image URLs. |
| 7 | Apply for the verified badge on launch day | The badge needs an extension listed for **6+ months**, a **6-month-old apex domain** (with an HTTPS site that answers `HEAD` with 200) and a DNS TXT record. Review takes about 5 business days. A launch-day application cannot succeed. | Start the clock now by publishing the beta publicly. Apply around May 2027. Until then, publish the publisher ID and extension ID on your own domain's docs so buyers and IT can allowlist them. Check the domain's registration date today. |

## Gaps the plan does not mention

These matter for a paid product that runs unsandboxed on customer source.

- **Architecture.** Wrap the Tollbridge CLI, or a language server if it exists, with a `--json` contract. The extension holds no migration logic and makes no hand-written API calls. Detect the CLI on `PATH` (and a configurable path). If it is missing, offer a pinned install, never `curl | sh`. Below the minimum CLI version, show one upgrade message, not a stack trace.
- **Auth.**
  - Default: reuse the CLI login through a command that prints the session as JSON, for example `tollbridge auth token --json`.
  - Hold the token in memory only. Never read the CLI's credential file, and never write tokens to settings or logs.
  - Fallback: a pasted key in `SecretStorage`, masked in every output channel.
  - If the product already has desktop OAuth, promote to a VS Code `AuthenticationProvider`.
- **Workspace trust.** An extension that runs the CLI against project files declares `capabilities.untrustedWorkspaces` as `"limited"` or `false`. Guard the code with `workspace.isTrusted`.
- **Telemetry.** Use `env.createTelemetryLogger` or `@vscode/extension-telemetry`, so VS Code's `telemetry.telemetryLevel` wins and your own setting can only narrow collection. Collect no SQL, file paths, usernames or tokens, because this is a schema tool. Ship `telemetry.json` and publish the event list. For usage numbers, prefer a server-side versioned `User-Agent` on CLI and API calls (`tollbridge-vscode/0.1.0 (vscode 1.104; darwin-arm64)`).
- **Remote workspaces.** Set `extensionKind` deliberately. For Remote-SSH, WSL, dev containers and Codespaces, find the CLI on the remote host and route OAuth through `env.asExternalUri`. If you spawn processes, state "desktop only" on the listing.
- **Fleets.** At 3,000 paying teams, expect allowlists, proxies with custom CAs and air-gapped machines. Honour `http.proxy` and custom CAs in the extension and in the CLI it spawns, and document offline `.vsix` install and the `extensions.allowed` ID.
- **Compatibility floor.** Set `engines.vscode` at or below the Code-OSS base of the oldest fork your users run, and feature-detect APIs forks lack.
- **Security hygiene.** Add `SECURITY.md` with a contact. Review any `extensionDependencies` or `extensionPack` entries. Write a compromised-token runbook per registry before launch.
- **Deprecation.** Plan this now: never remove a listing, deprecate it with a named replacement.
- **JetBrains.** Do not build it for launch. Revisit only if JetBrains users are your second-largest group and a second Kotlin or Java owner exists.

## Offering plan

### Verdict per job

| Job | Demand evidence | Surface | Extension part | Verdict |
| --- | --- | --- | --- | --- |
| Run and review migrations, see migration status | assumption A1 | CLI | commands, tree view, diagnostics | **Go** (thin shell) |
| Validate and complete migration config (if JSON or YAML) | assumption A2 | JSON Schema on SchemaStore, if the file name is distinctive | none | **Go**, as a schema |
| Log in once for terminal, CI and editor | assumption A3 | CLI login | first-run walkthrough | **Go** |
| Agent-driven migrations | none stated | MCP server | optional one-click setup | **Go later** (a named job is needed) |
| Rich dashboards in webviews | none | extension | webview | **No-go** (starved, needs a staffed owner) |

### Ranking

- Step 1 default rung: a JSON schema for config files, plus a thin shell over the CLI. It moves up when a job needs more than a tree view, quick pick or diagnostic.
- Step 1 starved option: a rich webview extension, promoted only with a staffed owner and a job native UI cannot show.
- Step 2 default family: one VS Code-API extension on both the Marketplace and Open VSX. The starved family is a JetBrains plugin, promoted when JetBrains is the second-largest user group and a second owner fits the effort ceiling.
- Interview answers that moved a rung: Q7 (a 2-week deadline) kept every default rung. Nothing is promoted.

### Editors and registries

| Family | Share of our users | Registry | Owner | Verdict or promotion condition |
| --- | --- | --- | --- | --- |
| VS Code | assumption A4 | VS Code Marketplace | assumption A5 | Go |
| Cursor, VSCodium, Theia, Kiro | assumption A4 | Open VSX | same owner | Go (same `.vsix`) |
| JetBrains | unknown | JetBrains Marketplace | none | Go later |
| Neovim, Zed, others | unknown | none | none | Document the schema and CLI config, no plugin |

### Architecture

- Shared core: the Tollbridge CLI, with `--json` and exit codes. Add a language server only if migration files need language features.
- Extension holds: UI only. Activate on specific events, never `*`. Bundle with esbuild.
- Runs on: desktop and remote workspaces. Not vscode.dev, if it spawns the CLI.

### Identity

| Registry | ID or namespace | Claimed | Verification status |
| --- | --- | --- | --- |
| VS Code Marketplace | decide today: `tollbridge` (preferred) or `tollbridge-dev` | no | Badge eligible about 6 months after first public listing |
| Open VSX | same string as the publisher | no | Unverified until the ownership issue is granted |
| JetBrains | n/a | n/a | n/a |

### Auth and trust

- Login path: CLI login reuse. Promote to an `AuthenticationProvider` if desktop OAuth exists.
- Secret store: `SecretStorage`.
- Untrusted workspaces: `"limited"`, with CLI execution disabled until trust is granted.
- Usage measurement: server-side `User-Agent`. Client events only if needed, through the host-level gate, with the event list published.

### First release sequence

| # | Step | Effort | Depends on |
| --- | --- | --- | --- |
| 1 | Decide the final publisher ID. Claim it on the Marketplace and as an Open VSX namespace. File the Open VSX ownership claim. | an hour, plus days waiting | - |
| 2 | Revoke the CTO's global PAT. Register trusted-publishing policies on both registries. Give CI the Contributor role. | a day | 1 |
| 3 | Set the version to `0.1.0` and the PNG icon. Fix the manifest (`engines.vscode`, `repository`, keywords, `capabilities.untrustedWorkspaces`). | an hour | - |
| 4 | Build the CLI wrapper, auth, telemetry gate, walkthrough and version check. | about a week | - |
| 5 | CI: `vsce package --pre-release`, secret scan, tests, record the SHA-256. Then `vsce publish --packagePath --oidc` and `ovsx publish --trusted-publishing` of that exact file. | a day | 2, 3, 4 |
| 6 | Publish IDs and the compatibility matrix on your own docs. Add `SECURITY.md`. Write the token-compromise runbook. | a day | 1 |
| 7 | Dry-run on a throwaway extension name before the real tag. | an hour | 2 |

### Compatibility matrix (first row)

| Extension | Min CLI | Min VS Code (`engines.vscode`) | JetBrains `since-build` | API version | Status |
| --- | --- | --- | --- | --- | --- |
| 0.1.x (pre-release) | assumption A6 | >= 1.63.0 floor, set to oldest fork base (A4) | n/a | assumption A6 | beta |

### Release and support

- Cadence: same train as the CLI. The extension never ships ahead of the CLI it calls.
- Host versions tested: the `engines.vscode` minimum, current stable, Insiders, the main fork (Cursor), and one remote target (dev container). Use a real sandbox account.
- Owner and triage rhythm: assumption A5. Triage weekly, and answer every review under 4 stars.
- Metrics: weekly active users by version (from `User-Agent`), first-run success (CLI found, login done, first migration run), share on supported versions, tickets per release.

### Gates before the tag

- The same `.vsix` hash on both registries, and a clean secret scan of the packed file.
- Integration tests green on the minimum and newest host, Insiders, the main fork and one remote target.
- The minimum-CLI check is covered by a test.
- No usage event fires with host telemetry at `error` or `off` (tested).
- Untrusted-workspace behaviour is tested.
- No PAT remains in CI secrets.

### Assumptions

| ID | Assumption | Step it drives | Who confirms |
| --- | --- | --- | --- |
| A1 | Customers want to run and review migrations from the editor, backed by support tickets or requests | 1 | Product |
| A2 | Tollbridge config is JSON or YAML with a distinctive file name | 1 | Engineering |
| A3 | The CLI has a token or session-status command with JSON output | 4 | CLI owner |
| A4 | Most customers use VS Code, some use Cursor or VSCodium, and the oldest fork base is known | 2, 5 | Support or sales data |
| A5 | A named team owns the extension, with on-call coverage and a TypeScript skill set | 8 | Engineering lead |
| A6 | CLI and API minimum versions are defined | 5 | CLI owner |
| A7 | Marketing will not change the brand again after launch | 6 | Marketing |

## Revised release plan

1. **Today:**
   - Settle the publisher ID.
   - Revoke the global PAT.
   - Claim the publisher and the Open VSX namespace, and file the ownership claim.
2. **This week:**
   - Set up OIDC publishing on both registries.
   - Convert the icon to PNG.
   - Fix the version to `0.1.0` pre-release.
   - Build the shell, auth and telemetry.
3. **Before the tag:**
   - Package once, scan, and test the packed file.
   - Dry-run the publish on a throwaway extension.
4. **Launch:**
   - Push the tag. CI publishes the same `.vsix` to both registries.
   - Publish the IDs on your own docs.
5. **After:**
   - Verified-badge application around May 2027.
   - GA at `1.0.0` when the beta is stable.

I did not check the unanswered facts above, such as the domain age and Cursor usage share. The plan stays provisional until A1–A7 are confirmed.