# Lumenwick `lumen` release and install: risks and fixes

This is a review of what you described. I haven't seen your repo, workflow or script, so the findings rest on your description alone. Items are ordered by risk.

## Verdict

At 2,000 downloads a week, the main risk is that `curl | sh` with sudo makes your release pipeline a root-level remote-execution channel. Anyone who controls the release assets, the script host, or the signing secrets can run code as root on every new install. The signing you have today doesn't protect that path. Fix the first four items before you publish the install docs.

## 1. Stop replacing assets on a published release (high)

- A replaced asset breaks every checksum, pinned hash and package manifest that saw the old file. Homebrew, Nix, scoop and anyone's lockfile will fail or silently differ.
- Nobody can tell afterwards which binary a user actually ran.
- Ship the fix as a new patch version (for example `v1.4.1`) instead.
- Mark the bad release as a pre-release or yank it, and add a note saying why.
- Turn on **immutable releases** in the GitHub repo settings so assets can't be edited after publishing.
- Publish through a draft: the workflow uploads every asset, a verify job checks them, and only then does the release get published.
- Ask who installed during the bad window. Run `lumen --version` on a Linux runner against the old asset's download count to size it. Post a short notice if the broken binary only failed to start, which is a nuisance. Treat it as an incident if you can't prove that.

## 2. Add a smoke test per target, so the next bad binary never ships (high)

- Last time a bad Linux binary got all the way to a release. A test gate before publish closes that gap.
- Run `lumen --version` and one real command on each target, on a clean runner of that OS and architecture. Use a container for old glibc and for Alpine.
- Decide the Linux ABI deliberately. A `x86_64-unknown-linux-musl` static build avoids glibc-version breakage. If you stay on glibc, build on the oldest distro you support.
- Cover aarch64 for Linux and macOS, since the install script will detect it.

## 3. Move signing out of the matrix build job (high)

Today the `.p12` and `.pfx` are readable by the same job that compiles your code. Everything that runs there can read them: `build.rs` scripts, proc macros in dependencies, and third-party actions.

Target layout:

```yaml
jobs:
  build:            # no secrets, runs on tags and PRs
    strategy: { matrix: { target: [...] } }
    steps: [checkout, cargo build --locked, smoke test, upload-artifact]
  sign:             # needs: build
    environment: release     # required reviewers, tag-only
    if: startsWith(github.ref, 'refs/tags/v')
    strategy: { matrix: { os: [macos, windows] } }
    steps: [download-artifact, sign, notarize, upload-artifact]
  publish:          # needs: sign, creates draft, verifies, then publishes
```

- Put the secrets in a protected **environment** with required reviewers. Allow it only for tag refs.
- Pin every third-party action to a full commit SHA. Set `permissions:` explicitly and default to read-only.
- Use `cargo build --locked` and run `cargo audit` or `cargo deny`.
- Never expose the secrets to `pull_request` workflows.
- **Windows:** CA/Browser Forum rules since June 2023 require new code-signing private keys to live on hardware or in a managed HSM. A plain `.pfx` file therefore suggests an older certificate. Plan the move to cloud signing (Azure Trusted Signing or a CA's cloud HSM) for the renewal, so no key file sits in GitHub at all.
- **macOS:** Developer ID signing alone isn't enough. Notarize the signed binary with `notarytool`, using an App Store Connect API key stored as a secret. You can't staple a bare CLI binary, so ship it inside a zip or tarball and notarize that. Create the keychain per run with a random password and delete it afterwards.
- Calendar the certificate expiry dates, and write down how you would revoke and rotate each secret.

## 4. Harden the install script (high)

Since the script runs sudo, treat it like a package manager.

1. **Wrap everything in a `main` function** and call it on the last line, so a truncated download can't execute half a script.
2. **Download with `curl --proto '=https' --tlsv1.2 -fsSL`.**
3. **Verify before install.** A checksum file in the same release only proves the download wasn't corrupted. If the release is compromised, the checksum is too. Verify a signature against a public key embedded in the script, using minisign or cosign. Also publish GitHub artifact attestations and the Sigstore bundle, so security-conscious users can check provenance.
4. **Don't resolve "newest release" live from GitHub.** A compromised or broken release would reach every installer within minutes. Instead have the release workflow's final step update a small `latest.json` on your own host, with version, URLs and hashes. Update it only after the smoke tests pass. This also gives you a kill switch: point it back to the previous version.
5. **Avoid sudo by default.** Install to `~/.local/bin` (or `$LUMEN_INSTALL_DIR`) with no privileges. Offer `/usr/local/bin` only when the user asks, and only call sudo for the single `install -m 755` command. Print what you are about to do first.
6. **Handle platform detection explicitly.** Detect OS and architecture (including Rosetta on macOS and musl on Linux). Fail with a clear message on anything unsupported. Don't guess.
7. **Support `LUMEN_VERSION=1.4.1`** so users can pin, and so CI can use it.
8. **Secure `get.lumenwick.dev`.** Enable MFA on the DNS and hosting accounts, and set CAA records. Keep the script in a repo with branch protection and publish it as a release asset too, so it is inspectable. Monitor it for changes.

## 5. Windows is not covered by the install line (medium)

`curl … | sh` doesn't work in PowerShell or cmd. Only WSL and Git Bash users could run it. The docs need a Windows path, or the `.pfx` signing buys you nothing for the people who need it. Offer:

- `irm https://get.lumenwick.dev/install.ps1 | iex`, with the same pinned, signature-verified design, or better
- winget and scoop manifests, which also give you SmartScreen reputation sooner

Keep in mind that files fetched by `curl` don't get the quarantine flag. Gatekeeper on macOS and SmartScreen on Windows therefore don't check script-installed binaries. Signing still matters for users who download directly or install via brew or winget. The script's own signature check is what protects the `curl | sh` path.

## 6. Don't make it the only way in (medium)

"Install docs will say only `curl | sh`" shuts out people who can't run it: corporate machines, air-gapped hosts, and the security-conscious. Add short alternatives:

- `cargo binstall lumen` and `cargo install lumen --locked`
- Homebrew tap, winget and scoop
- A "download and verify manually" section with the checksum and signature commands

## 7. Smaller items

- Add a `lumen self-update` that applies the same verification, or tell users to re-run the installer.
- Publish an SBOM and `SECURITY.md` with a disclosure address.
- Write a one-page "release runbook" covering yank, rollback of `latest.json`, and secret rotation, so the next bad binary takes minutes rather than a rebuild.

## Suggested order

1. Immutable releases on; stop replacing assets (today).
2. Smoke-test gate and draft-then-publish flow.
3. Split the `sign` job with a protected environment.
4. Signature verification, `latest.json` and no-default-sudo in the installer.
5. Windows installer path, then alternative install methods.
6. Cloud signing for Windows at the next certificate renewal.

I can draft the workflow YAML or the installer script (`install.sh` and `install.ps1`) next if you want. Tell me the repo layout and whether you prefer minisign or cosign.