# Design review: Harrowgate VS Code extension

Six of your seven decisions need changes before you build. Fix the three blockers first, since each would fail an enterprise security review. I haven't seen the code or the API, so where I point at a risk, check it against your actual behavior.

## 🔴 Blockers

**1. Remove `curl -sSL … | sh`.**
- It runs unverified remote code, silently, from a security vendor's extension. It also assumes `curl`, a writable `PATH`, and often root, and dev containers (especially Alpine or minimal images) frequently lack all of those.
- Ship the CLI as a platform-specific VSIX (`vsce package --target linux-x64 | linux-arm64 | alpine-x64 | darwin-arm64 | win32-x64`). Containers on Apple Silicon are linux-arm64 and Alpine is musl, so both targets matter.
- Alternatively, download a pinned version into `context.globalStorageUri`. Verify a SHA-256 baked into the extension at build time plus a signature (cosign or minisign).
- Ask for consent before downloading, and add a `harrowgate.cliPath` override for air-gapped networks.
- Publish a dev container Feature (`ghcr.io/harrowgate/features/hgate`) so the CLI is installed at image build time, not at runtime.

**2. Store the key in `SecretStorage`, not a `harrowgate.apiKey` setting.**
- Settings are plaintext in `settings.json`. They get synced, pasted into bug reports, and committed in dotfiles or `.vscode/settings.json`. Syncing a credential across machines is a leak path, not a feature.
- Use `context.secrets`, with a browser or device-flow "Sign in" command. Issue read-only, org-scoped tokens that you can revoke.
- Resolution order: `SecretStorage`, then the process env `HGATE_TOKEN`, then the CLI's own credential store. Dev containers and Codespaces inject env vars through `remoteEnv` and Codespaces secrets, so that path already works for your enterprise users.
- Mark `harrowgate.apiBaseUrl` and `harrowgate.cliPath` as `"scope": "machine"`. A workspace-scoped value lets a malicious repo redirect your token to its own server or point you at its own binary. That is code execution plus token exfiltration from simply opening a repo.

**3. Don't auto-read `.env`.**
- The workspace is untrusted input. A planted `.env` with an attacker's `HGATE_TOKEN` would make the extension send results (or file content) to the attacker's org.
- A secrets scanner that parses `.env` files and holds their contents will also get flagged by its own customers' scanners and reviewers.
- Cut it. The process environment covers the legitimate case (see #2).
- If customers insist, make it an explicit opt-in command that reads one named variable, and never log or echo the value.

## 🟠 Should change

**4. Choose one scan engine.**
- The question: what does the extension send to the API? For secrets scanning, uploading file contents off the machine is a data-egress problem for most of your customers. If it sends only manifests or hashes, say so in the doc.
- If the CLI contains the parsing, lockfile resolution, and secret-detection logic, calling the API directly forces a second implementation that will drift.
- Either run `hgate scan --format json` (or SARIF) as a child process with a versioned output schema, or generate one typed client from your OpenAPI spec and use it in both the CLI and the extension.
- "Faster" is unmeasured. Process spawn costs tens of milliseconds, and scan time is dominated by analysis and network. Benchmark before deciding.
- Prefer built-in `fetch` over axios, and test behind a corporate proxy with a custom CA. Enterprise customers will have both, and your transport must honor `http.proxy` and `http.proxyStrictSSL`.

**5. Don't scan inside the extension host, and find the real cause of the "flaky" spawns.**
- The extension host is shared by every installed extension. A CPU-heavy scan there causes "extension host unresponsive" for all of them, and users will blame you.
- Flaky spawns usually come from `PATH` resolution. A GUI-launched VS Code on macOS often has a different `PATH` than the terminal. Containers differ again.
- Resolve the binary to an absolute path once, use `execFile` with no shell, and set an explicit `cwd`, timeout, and `AbortSignal`.
- Debounce scans, cap concurrency, and trigger on lockfile saves, not keystrokes.

**6. Replace `*` activation.**
- Use `onStartupFinished` plus `workspaceContains:**/{package-lock.json,go.mod,requirements.txt,…}` and `onCommand`.
- Keep the scan status current with a `FileSystemWatcher` on manifests and lockfiles.
- `*` slows every window and appears on startup-time audits.

**7. Declare dev container, Codespaces, and trust behavior in `package.json`.**
```json
"extensionKind": ["workspace"],
"capabilities": {
  "untrustedWorkspaces": { "supported": "limited",
    "description": "Scanning is disabled until the workspace is trusted." }
}
```
- `workspace` makes the extension run in the container next to the files, not on the UI side.
- Gate the CLI spawn on `vscode.workspace.isTrusted`.
- github.dev and vscode.dev have no Node. Either ship a `browser` entry point or state explicitly that the extension doesn't support web-only mode.
- Document the egress hosts customers must allowlist for locked-down containers.

**8. Harden the diagnostics.**
- Never put a secret's value in the diagnostic message, hover, Output channel, or telemetry. Diagnostics are visible to other extensions and to AI assistants reading the Problems panel. Use redacted previews such as `AKIA…[redacted]`.
- Map transitive dependency findings to the declaring line in the manifest, since a lockfile line is meaningless to the user. Set `source: "Harrowgate"` and `code` with `codeDescription.href`.
- Add a quick-fix code action (upgrade to the patched version).
- Clear stale diagnostics on rescan, and show a "scanned at <time>" status item.
- Test a 100k-line lockfile.

## 🟢 Add before launch

- **Enterprise policy:** use the setting `policy` field so admins can lock the base URL, telemetry, and auto-update through group policy.
- **Telemetry:** use `vscode.env.createTelemetryLogger`, which respects the user's telemetry setting, and publish what you collect.
- **Distribution:** publish to Open VSX as well as the Microsoft Marketplace, since Cursor, Theia, and other forks use Open VSX. Sign the VSIX.
- **Version skew:** define a supported CLI range and API version, and have the extension show a clear error outside it.
- **Multi-org tokens:** some of your 900 customers have several orgs. Decide how the user picks one.
- **Multi-root workspaces and monorepos:** decide whether you scan per folder or per workspace.

## Revised architecture

1. The extension is thin: UI, diagnostics, and auth only.
2. It resolves the credential (`SecretStorage`, then env var), never a workspace file.
3. It locates or installs a pinned, verified `hgate` binary in the workspace extension host.
4. It runs `hgate scan --format json` as a child process with cancellation.
5. It maps findings to redacted diagnostics.
6. Activation is event-driven, and everything is gated on workspace trust.

## Decisions I need from you

1. Does the extension send file content to the API, or only metadata?
2. Does the CLI have a stable machine-readable output (JSON or SARIF)?
3. Can you issue scoped, revocable tokens through a login flow?
4. Do you need air-gapped support at launch?

The answers decide between the "child process" and "shared typed client" routes in #4.