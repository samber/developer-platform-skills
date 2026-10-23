# Registry publishing rules

Per-registry requirements for publishing, authenticating, signing, versioning and removing an IDE extension. Read during step 6, and again before any removal or rename.

Contents:

- VS Code Marketplace
- Open VSX
- JetBrains Marketplace
- Other editors
- Comparison table

## VS Code Marketplace

**Identity:**

- Create the publisher at `marketplace.visualstudio.com/manage`. The publisher ID and each extension name are permanent.
- Add publisher members by user ID, not email. Give CI the Contributor role, never Owner.
- Verified publisher badge: DNS TXT record on an apex domain (not a subdomain) that serves HTTPS and answers `HEAD` with 200; an extension listed for at least 6 months; a domain registered at least 6 months; about 5 business days of review. Changing the publisher display name revokes the badge.

**Authentication for publishing:**

- Global Azure DevOps personal access tokens stop working on 2026-12-01, and the classic `vsce` PAT recipe ("All accessible organizations", scope Marketplace > Manage) uses one. Treat any PAT-based CI as a dated liability.
- `vsce publish --azure-credential`: Microsoft Entra ID with workload identity federation or a managed identity, no stored secret.
- `vsce publish --oidc`: GitHub Actions OIDC, no PAT. Register a trusted-publishing policy (repository and workflow) on the Marketplace first; the job needs `permissions: id-token: write, contents: read` and Node 22+. It never falls back to a PAT, so delete the PAT path instead of keeping it as a silent backup.
- Pass `--packagePath <file>.vsix` to every `vsce publish`; without it vsce packages again from source.
- PAT failures, while they last: 401 means wrong scope, 403 means wrong organization setting; a "custom" expiry can be the same day, so `vsce verify-pat` passes and tomorrow's publish fails.
- Never pass a token on the command line or let an agent run `vsce login`; read it from a CI secret.

**Packaging and versions:**

- Use `@vscode/vsce` from `devDependencies`, not the deprecated unscoped `vsce` package.
- Versions are `major.minor.patch` only; semver pre-release suffixes (`-beta.1`) are rejected, and a published version can never be republished.
- Pre-release channel: `vsce package --pre-release`, then publish that file; `engines.vscode >= 1.63.0`, odd minor for pre-release and even minor for release (`0.3.x` pre-release, `0.2.x` release). VS Code installs the highest version, so keep pre-release above stable. Both share one listing and one README; write it channel-neutral.
- Platform-specific builds: `vsce package --target <target>` for `win32-x64`, `win32-arm64`, `linux-x64`, `linux-arm64`, `linux-armhf`, `alpine-x64`, `alpine-arm64`, `darwin-x64`, `darwin-arm64`, `web`. An untargeted package is universal.
- `vsce publish patch|minor|major` also commits and tags; avoid it when your release workflow owns tags.
- Listing: PNG icon of at least 128 px (no SVG icon), HTTPS image URLs in the README, at most 30 keywords, `repository` set, `engines.vscode` set to a real minimum (never `*`).

**Trust controls the Marketplace runs:** multi-engine malware scan on every upload and update, a later rescan, sandboxed dynamic analysis, name-squatting checks, secret scanning that blocks packages carrying verified credentials, and a Marketplace signature VS Code checks at install. Since VS Code 1.97, users see a publisher-trust prompt for third-party publishers.

**Terms:** Marketplace offerings may be used only with Microsoft's in-scope products (Visual Studio, VS Code, GitHub Codespaces, Azure DevOps). VS Code forks therefore install from Open VSX or their own gallery.

**Compromised publish token:** revoke every publish token and audit publisher members, then per registry:

- VS Code Marketplace: publish a clean higher patch at once and report the bad version to Marketplace support; unpublish the whole extension only when no clean build exists.
- Open VSX: delete the bad version, publish the clean patch.
- JetBrains: hide the update in the vendor console and contact Marketplace support.

**Removal:**

| Action | Effect | Reversible |
| --- | --- | --- |
| Deprecate (comment on the `microsoft/vscode-discussions` "Deprecated extensions" thread, naming a replacement extension or setting) | Listing struck through, warning badge, optional migrate button | Yes |
| Unpublish (`vsce unpublish <publisher>.<name>` or the manage page) | No new installs; listing and stats kept | Yes |
| Remove | Listing and stats deleted; name reserved forever, even for you | No |

## Open VSX

Vendor-neutral registry run by the Eclipse Foundation. Read by VSCodium, Cursor (behind its own proxy), Eclipse Theia, Kiro and other Code-OSS builds.

**Identity:**

- Sign in with GitHub, link an Eclipse Foundation account with the same GitHub username, and accept the Open VSX Publisher Agreement.
- `ovsx create-namespace <name>` creates the namespace but does not verify it: listings show an unverified-publisher warning until an admin grants ownership.
- Claim ownership through an issue on `EclipseFdn/open-vsx.org` with brand evidence (a GitHub account with at least a year of history; for a name matching your Marketplace publisher, proof of control). Expect days.
- Claim the namespace before launch so nobody else publishes under your brand.

**Publishing:**

- Accepting the Publisher Agreement grants the Eclipse Foundation rights to redistribute what you publish; have legal read it before publishing a proprietary-licensed extension.
- **Default:** trusted publishing. Register a trusted-publisher policy on the namespace, then `ovsx publish <file>.vsix --trusted-publishing` from GitHub Actions or GitLab CI exchanges the workflow's OIDC token for a publish token valid a few minutes. `--trusted-publishing` fails loudly when no ID token is available; a `--pat` or `OVSX_PAT` always takes precedence, so remove them from that job.
- **Fallback:** an access token scoped to the namespace (and extension where offered), on a Contributor-role account so a leak cannot reassign members. Tokens now expire; calendar the rotation before the expiry the profile shows.
- Tokens carry the `ovsxp_` prefix so scanners detect them.
- `ovsx publish <file>.vsix`, using the same file you uploaded to the Marketplace; two builds from source can differ.
- Every upload is scanned: name squatting, blocklist and secret checks reject it; threat scanners can quarantine it for admin review. A flagged version cannot be reactivated; publish a fixed patch.

**Deprecation and removal:**

- Deprecate by pull request to `extension-control/extensions.json` in the `open-vsx/publish-extensions` repository: mark it deprecated, name the replacement, keep it downloadable. A nightly job applies it, so it shows the day after merge.
- `ovsx unpublish` or the web UI deletes a version but keeps its number reserved; only an admin purge frees it. Deletion is refused while other extensions depend on yours.

## JetBrains Marketplace

**Identity:** a vendor profile; the plugin `<id>` in `plugin.xml` cannot change after the first public release, and a new ID is a new plugin with no upgrade path.

**Review:**

- The first upload is manual, through the web UI; later uploads can use the IntelliJ Platform Gradle Plugin `publishPlugin` task.
- Every new plugin and every update gets automated checks and manual review. JetBrains guarantees no time frame; ask after 3-4 working days of silence.
- Approval needs an original name (30 characters maximum), an English description, valid vendor details, a working build for at least one JetBrains product, a Developer EULA (always) and a privacy policy (when the plugin collects personal data).
- Statistics or telemetry need the user's explicit permission, and the plugin must send nothing while it is not in use. Lookalike logos, trademark misuse, broken links and internal-API use get rejected.
- JetBrains may unpublish a plugin whose author ignores adjustment requests.

**Compatibility:**

- `since-build` is required; `until-build` is optional and best left open, unless you publish one build per IDE release. Branch numbers follow the release: 2025.3 = 253, 2026.1 = 261.
- The IntelliJ Platform Gradle Plugin 2.x defaults `untilBuild` to `<sinceBuild major>.*`, a pinned upper bound. Set `pluginConfiguration.ideaVersion.untilBuild = provider { null }` for open-ended compatibility, and check the generated `plugin.xml`.
- Build against the lowest supported platform version; run Plugin Verifier (`verifyPlugin`) across the range. The Marketplace also runs it on upload.
- JetBrains ships three platform majors a year, so budget one verification pass per major.

**Signing and tokens:** the Marketplace signs every plugin; author signing (`signPlugin`, certificate chain and key from environment variables) is optional, but unsigned plugins show a warning at install. An expired author certificate breaks the release at `signPlugin`. The publish token comes from the profile and lives in the CI secret store.

**Channels:** `default` plus custom channels (`eap`, `beta`) that users add as a custom repository URL.

**Paid plugins:** a `product-descriptor` in `plugin.xml` (code, release date, release version; `optional="true"` for freemium). Changing the release date or version starts a new paid major and resets trials.

**LSP:** the platform LSP API needs 2023.2+ and runs only in commercial IDEs (plus the free tier of unified PyCharm since 2025.1), not open-source IntelliJ builds or Android Studio.

## Other editors

- **Visual Studio (not Code):** separate extension type (`.vsixmanifest`), uploaded to the Visual Studio Marketplace web UI.
- **Neovim, Emacs, Sublime Text, Zed:** reach them through the language server and the JSON schema; document the client configuration. Zed also has its own extension format (`extension.toml`).

## Comparison table

| | VS Code Marketplace | Open VSX | JetBrains Marketplace |
| --- | --- | --- | --- |
| Pre-publication review | automated scans | automated scans, quarantine | automated plus manual, every version |
| Publish auth | Entra or GitHub OIDC; global PATs end 2026-12-01 | trusted publishing (GitHub, GitLab OIDC); expiring scoped token | profile token |
| Identity proof | DNS TXT, 6-month wait | ownership issue | vendor profile |
| Removal | deprecate, unpublish, remove | deprecate (replacement, downloadable), delete version | hide update, JetBrains-side unpublish |
| Permanent | publisher ID, extension name | namespace, version numbers | plugin `<id>` |
| Who may install | Microsoft products only | any editor | JetBrains IDEs |
| Compatibility key | `engines.vscode` | same manifest | `since-build` / `until-build` |
