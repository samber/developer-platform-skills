Do first: stop replacing assets on published releases. The next fix ships as a new patch tag, and nobody edits assets after that. Files below are drafts pending your approval, so don't commit them yet.

## 0. Assumptions

I couldn't ask questions, so I assumed the following. Correct any that are wrong.

1. CI is GitHub Actions on hosted runners. The repo is `lumenwick/lumen`, a placeholder name.
2. The crate is not on crates.io. No Homebrew tap, Scoop bucket or winget entry exists. The `curl | sh` script is the only install path.
3. The Apple `.p12` and Windows `.pfx` are repo-level secrets. Expiry is unknown. Apple notarization is probably done with an Apple ID password, which I'll replace with an API key.
4. The cause of the bad Linux binary is unknown, and I have no evidence of compromise.
5. At least 3 people can approve releases. Release latency from a human gate is fine.
6. No deadline is set, and this is a standing process. Effort is about 5 engineer-days.
7. Private packages: none.
8. GitHub immutable releases are available to the org.

Three answers change the plan:
- **Why was the Linux binary bad?** If you can't explain it, treat it as suspected compromise and rotate every credential (see §4).
- **How does the `.pfx` exist?** CAs have had to issue code-signing keys on hardware (HSM or token) since 2023, so an exportable `.pfx` suggests an older certificate. Check when it expires and whether the CA can renew it as a file.
- **Who can approve releases?** This sets the reviewer team on the `release` environment.

## 1. Inventory

| Artifact | Channel | Publish path | Credential | Expiry | Owner | Target |
|---|---|---|---|---|---|---|
| `lumen` macOS (arm64, x64) | GitHub release asset | matrix build job | Apple `.p12` in a repo secret, plus notarization credential | unknown | unknown | separate signing job, `signing-macos` environment, App Store Connect API key |
| `lumen` Windows x64 | GitHub release asset | matrix build job | `.pfx` in a repo secret | unknown | unknown | separate signing job, cloud signing or HSM |
| `lumen` Linux (x64, arm64) | GitHub release asset | matrix build job | none | n/a | n/a | checksums, cosign signature, attestation |
| `install.sh` | `get.lumenwick.dev` | unknown | host credentials | unknown | unknown | rendered per release, pinned version |
| Homebrew, Scoop, winget | none yet | none | none | n/a | n/a | new channels |
| crates.io | none | none | none | n/a | n/a | optional, later |

## 2. Findings

1. **Replacing an asset on a published release is the worst problem.**
   - Anyone who downloaded the first Linux binary has bad bytes under the same version.
   - The script serves different bytes for the same tag. Any checksum or pin made from the first bytes now fails.
   - No `--version` output tells the two apart.
   - Fix: roll forward and never edit a published asset again. Turn on immutable releases, and attach everything to a draft before publishing.
2. **Signing happens in the matrix build job.**
   - That job compiles every dependency and runs tests.
   - The Linux and Windows legs can read the Apple `.p12` too, because the secrets are repo-level.
   - Fix: build unsigned with no secrets, then sign in one dedicated job per OS. Each signing job runs no project code and holds only its own credentials, in its own protected environment.
3. **The install script has several weaknesses.**
   - It runs `sudo` by default.
   - It fetches "newest", so the version isn't pinned.
   - It does no verification.
   - It can't work natively on Windows. Windows users need Scoop or winget.
4. **A `.pfx` file is the wrong Windows credential.** Move to a cloud signing service or HSM. Use the `.pfx` only as an interim, inside the `signing-windows` environment.
5. **There is no smoke test.** Nothing ran the built binary before release, and that is how the bad Linux binary shipped.

## 3. Per-registry decisions

**Credential rung.** The default is trusted publishing bound to a protected environment. GitHub Releases take no registry credential. The only rungs that apply are a hardened publish job, a human approval gate, and signing plus provenance.

- **Gate:** promoted, because this is an incident and users download the binaries directly.
- **Reviewers:** a team, or 2+ people besides whoever cuts releases. Any one approves, and self-review is blocked.
- **Signing and provenance:** promoted for the same reason. Add checksums, a cosign signature and an attestation.

**Namespace.** Not applicable on GitHub. Restrict who can create `v*` tags, because the tag triggers the release.

**Library vs binary.** `lumen` is a binary. It ships as signed release assets plus channel packages. The `curl | sh` script stays as a fallback only.

**Channel policy.**
- SemVer.
- Pre-releases use `-rc.N` or `-beta.N` and are flagged as pre-release on GitHub.
- One immutable version per release.
- CI checks that the tag equals the `Cargo.toml` version.

**crates.io.** Skip for now. At 2,000 downloads a week, the tap, bucket, winget and script cover the audience. Add the crate if Rust users ask for `cargo install --locked`.
- Crate names are flat and permanent. Check that the name is free first.
- The first release is manual with a scoped token. Then add a trusted publisher, enable "Trusted Publishing only", and revoke the token.

**Preflight commands.** Run these before tagging:
```sh
cargo build --release --locked
cargo test --locked
cargo package --list      # only if publishing to crates.io
```

## 4. Pipeline files (drafts pending approval)

### 4.1 One-time repository setup (done by you in GitHub settings)

1. Add a tag ruleset on `v*`: only release managers may create, move or delete tags.
2. Turn on immutable releases.
3. Create these environments, all restricted to `v*` tags:
   - `release`: reviewers = team, self-review blocked.
   - `signing-macos`: Apple secrets.
   - `signing-windows`: Windows secrets.
   - `channel-homebrew` and `channel-winget`: one narrow token each.
4. Move the Apple and Windows secrets from repo level into their environments. Delete the repo-level copies after the first good release.

### 4.2 `.github/workflows/release.yml`

```yaml
name: release
on:
  push:
    tags: ["v[0-9]*"]
permissions: {}

env:
  # Pinned so a rebuild of the same commit uses the same compiler.
  RUST_TOOLCHAIN: "<pinned stable version>"

jobs:
  plan:
    runs-on: ubuntu-latest
    permissions: { contents: read }
    outputs:
      version: ${{ steps.ver.outputs.version }}
      prerelease: ${{ steps.ver.outputs.prerelease }}
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - name: Tag must equal Cargo.toml version
        id: ver
        run: |
          set -euo pipefail
          tag="${GITHUB_REF_NAME#v}"
          version="$(cargo metadata --no-deps --format-version 1 | jq -r '.packages[] | select(.name=="lumen") | .version')"
          [ "$tag" = "$version" ] || { echo "tag $tag != version $version"; exit 1; }
          case "$version" in
            *-*) echo "prerelease=true" >> "$GITHUB_OUTPUT" ;;
            *)   echo "prerelease=false" >> "$GITHUB_OUTPUT" ;;
          esac
          echo "version=$version" >> "$GITHUB_OUTPUT"

  test:
    needs: plan
    runs-on: ubuntu-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - run: rustup toolchain install "$RUST_TOOLCHAIN" --profile minimal && cargo +"$RUST_TOOLCHAIN" test --locked   # no restored caches

  build:                                  # unprivileged: no secrets, no id-token
    needs: plan
    runs-on: ${{ matrix.runner }}
    permissions: { contents: read }
    strategy:
      fail-fast: true
      matrix:
        include:
          - { runner: ubuntu-latest,   target: x86_64-unknown-linux-musl }     # static: no glibc surprises
          - { runner: ubuntu-24.04-arm, target: aarch64-unknown-linux-musl }
          - { runner: macos-14,        target: aarch64-apple-darwin }
          - { runner: macos-14,        target: x86_64-apple-darwin }           # cross-built on arm runner
          - { runner: windows-latest,  target: x86_64-pc-windows-msvc }
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - name: Build unsigned
        shell: bash
        env:
          LUMEN_BUILD_SHA: ${{ github.sha }}     # surfaced in `lumen --version` so support can tell builds apart
        run: |
          rustup toolchain install "$RUST_TOOLCHAIN" --profile minimal --target "${{ matrix.target }}"
          cargo +"$RUST_TOOLCHAIN" build --release --locked --target "${{ matrix.target }}" -p lumen
          mkdir -p out
          cp "target/${{ matrix.target }}/release/lumen"* out/ 2>/dev/null || true
      - uses: actions/upload-artifact@<sha>  # v5
        with: { name: "unsigned-${{ matrix.target }}", path: out/lumen* }

  sign-macos:                             # runs no project code; no checkout
    needs: build
    runs-on: macos-14
    environment: signing-macos
    permissions: {}
    strategy:
      matrix: { target: [aarch64-apple-darwin, x86_64-apple-darwin] }
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: "unsigned-${{ matrix.target }}", path: in }
      - name: Sign and notarize
        env:
          APPLE_P12_BASE64: ${{ secrets.APPLE_P12_BASE64 }}
          APPLE_P12_PASSWORD: ${{ secrets.APPLE_P12_PASSWORD }}
          ASC_KEY_BASE64: ${{ secrets.ASC_KEY_BASE64 }}      # App Store Connect API key (.p8)
          ASC_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          ASC_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
        run: |
          set -euo pipefail
          # Hosted runners are ephemeral; add keychain cleanup if this ever runs self-hosted.
          keychain="$RUNNER_TEMP/sign.keychain-db"; kcpw="$(uuidgen)"
          security create-keychain -p "$kcpw" "$keychain"
          security set-keychain-settings -lut 900 "$keychain"
          security unlock-keychain -p "$kcpw" "$keychain"
          echo "$APPLE_P12_BASE64" | base64 --decode > "$RUNNER_TEMP/cert.p12"
          security import "$RUNNER_TEMP/cert.p12" -P "$APPLE_P12_PASSWORD" -T /usr/bin/codesign -f pkcs12 -k "$keychain"
          security set-key-partition-list -S apple-tool:,apple: -s -k "$kcpw" "$keychain" >/dev/null
          security list-keychains -d user -s "$keychain"
          identity="$(security find-identity -v -p codesigning "$keychain" | awk -F'"' '/Developer ID Application/ {print $2; exit}')"
          [ -n "$identity" ] || { echo "no Developer ID Application identity"; exit 1; }
          codesign --force --options runtime --timestamp --sign "$identity" --keychain "$keychain" in/lumen
          codesign --verify --strict --verbose=2 in/lumen
          ditto -c -k --keepParent in/lumen "$RUNNER_TEMP/lumen.zip"
          echo "$ASC_KEY_BASE64" | base64 --decode > "$RUNNER_TEMP/AuthKey.p8"
          xcrun notarytool submit "$RUNNER_TEMP/lumen.zip" --key "$RUNNER_TEMP/AuthKey.p8" \
            --key-id "$ASC_KEY_ID" --issuer "$ASC_ISSUER_ID" --wait --output-format json > "$RUNNER_TEMP/notary.json"
          # Exit 0 means nothing: assert the status.
          [ "$(jq -r .status "$RUNNER_TEMP/notary.json")" = "Accepted" ] || { cat "$RUNNER_TEMP/notary.json"; exit 1; }
      - uses: actions/upload-artifact@<sha>  # v5
        with: { name: "signed-${{ matrix.target }}", path: in/lumen }

  sign-windows:
    needs: build
    runs-on: windows-latest
    environment: signing-windows
    permissions: {}                       # add id-token: write only if the cloud signer uses OIDC
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: unsigned-x86_64-pc-windows-msvc, path: in }
      # Preferred: cloud signing service or HSM. Take the action and its pinned SHA from the vendor's docs.
      - name: Sign with cloud signer
        uses: <vendor signing action>@<sha>
        with: { files: in/lumen.exe }
      # Interim only, while the .pfx still exists (lives in the signing-windows environment):
      #   signtool sign /f cert.pfx /p $env:PFX_PASSWORD /fd SHA256 /tr <CA RFC3161 URL> /td SHA256 in\lumen.exe
      - name: Assert signature
        shell: pwsh
        run: |
          $s = Get-AuthenticodeSignature in\lumen.exe
          if ($s.Status -ne 'Valid') { throw "signature status: $($s.Status)" }
      - uses: actions/upload-artifact@<sha>  # v5
        with: { name: signed-x86_64-pc-windows-msvc, path: in/lumen.exe }

  package:
    needs: [plan, test, build, sign-macos, sign-windows]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write                     # keyless cosign + attestation
      attestations: write
    env:
      VERSION: ${{ needs.plan.outputs.version }}
    steps:
      - uses: actions/checkout@<sha>  # v6  (only to copy LICENSE and README; runs nothing from the repo)
        with: { persist-credentials: false }
      - uses: actions/download-artifact@<sha>  # v5
        with: { pattern: "{signed-*,unsigned-*-linux-musl}", path: bins }
      - name: Archive and checksum
        run: |
          set -euo pipefail
          mkdir dist
          for d in bins/*/; do
            n="$(basename "$d")"; target="${n#*-}"
            case "$target" in
              *windows*) (cd "$d" && zip -q "../../dist/lumen-${VERSION}-${target}.zip" lumen.exe) ;;
              *) chmod 0755 "$d/lumen"; tar -czf "dist/lumen-${VERSION}-${target}.tar.gz" -C "$d" lumen ;;
            esac
          done
          (cd dist && sha256sum lumen-* > checksums.txt)
          sed "s/@VERSION@/${VERSION}/" scripts/install.sh > dist/install.sh
      - uses: sigstore/cosign-installer@<sha>  # v3
      - run: cosign sign-blob --bundle dist/checksums.txt.sigstore.json dist/checksums.txt --yes
      - uses: actions/attest@<sha>  # v3
        with: { subject-checksums: dist/checksums.txt }
      - uses: actions/upload-artifact@<sha>  # v5
        with: { name: dist, path: dist/* }

  verify:                                 # smoke test: the gate that was missing
    needs: [plan, package]
    runs-on: ${{ matrix.runner }}
    permissions: {}
    strategy:
      matrix:
        include:
          - { runner: ubuntu-latest,    target: x86_64-unknown-linux-musl }
          - { runner: ubuntu-24.04-arm, target: aarch64-unknown-linux-musl }
          - { runner: macos-14,         target: aarch64-apple-darwin }
          - { runner: windows-latest,   target: x86_64-pc-windows-msvc }
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: dist, path: dist }
      - name: Run the shipped archive
        shell: bash
        env: { VERSION: "${{ needs.plan.outputs.version }}", TARGET: "${{ matrix.target }}" }
        run: |
          set -euo pipefail
          cd dist
          sha256sum -c --ignore-missing checksums.txt 2>/dev/null || shasum -a 256 -c --ignore-missing checksums.txt
          mkdir x; case "$TARGET" in *windows*) unzip -q "lumen-${VERSION}-${TARGET}.zip" -d x ;; *) tar -xzf "lumen-${VERSION}-${TARGET}.tar.gz" -C x ;; esac
          ./x/lumen --version | grep -F "$VERSION"
          ./x/lumen --help >/dev/null
          # Add one real subcommand run that touches the network-free core path.

  release:
    needs: [plan, package, verify]
    runs-on: ubuntu-latest
    environment: release                  # reviewers approve here, with the draft visible
    permissions: { contents: write }
    env:
      GH_TOKEN: ${{ github.token }}
      PRERELEASE: ${{ needs.plan.outputs.prerelease }}
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: dist, path: dist }
      - name: Draft, attach everything, then publish
        run: |
          set -euo pipefail
          gh release create "$GITHUB_REF_NAME" --repo "$GITHUB_REPOSITORY" --draft --verify-tag --generate-notes
          gh release upload "$GITHUB_REF_NAME" --repo "$GITHUB_REPOSITORY" dist/*
          if [ "$PRERELEASE" = true ]; then flag=--prerelease; else flag=; fi
          gh release edit "$GITHUB_REF_NAME" --repo "$GITHUB_REPOSITORY" --draft=false $flag

  channel-homebrew:                       # channels update last, one narrow token each
    needs: [plan, release]
    if: needs.plan.outputs.prerelease == 'false'
    runs-on: ubuntu-latest
    environment: channel-homebrew         # holds a token scoped to lumenwick/homebrew-tap only
    permissions: {}
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: dist, path: dist }
      - name: Render formula and push to the tap
        env:
          TAP_TOKEN: ${{ secrets.TAP_TOKEN }}
          VERSION: ${{ needs.plan.outputs.version }}
        run: |
          # Fill Formula/lumen.rb from the template with VERSION and the four SHA-256 values in dist/checksums.txt,
          # commit "lumen ${VERSION}", push to the tap's default branch. The tap owns its own formula template.

  channel-winget:
    needs: [plan, release]
    if: needs.plan.outputs.prerelease == 'false'
    runs-on: windows-latest
    environment: channel-winget           # public-repo-scope token on a dedicated bot account
    permissions: {}
    steps:
      - name: Open the winget-pkgs PR
        env: { WINGET_TOKEN: "${{ secrets.WINGET_TOKEN }}" }
        run: |
          # wingetcreate update Lumenwick.Lumen --version <v> --urls <zip URL>|x64 --submit
```

### 4.3 `scripts/install.sh`

The release job renders it with the version baked in. It is served from `get.lumenwick.dev`, either by redirecting to the release's `install.sh` asset or by uploading a copy.

```sh
#!/bin/sh
# Installs lumen @VERSION@. Whole body sits in main(), called on the last line,
# so a truncated download runs nothing.
set -eu

die() { echo "lumen install: $*" >&2; exit 1; }

main() {
  version="${LUMEN_VERSION:-@VERSION@}"
  install_dir="${LUMEN_INSTALL_DIR:-$HOME/.local/bin}"   # never sudo; a system dir is the caller's choice
  repo="lumenwick/lumen"
  base="https://github.com/${repo}/releases/download/v${version}"

  case "$(uname -s)" in
    Linux)  os="unknown-linux-musl" ;;
    Darwin) os="apple-darwin" ;;
    *) die "unsupported OS $(uname -s). On Windows use: scoop install lumen, or: winget install Lumenwick.Lumen" ;;
  esac
  case "$(uname -m)" in
    x86_64|amd64)  arch="x86_64" ;;
    arm64|aarch64) arch="aarch64" ;;
    *) die "unsupported CPU $(uname -m)" ;;
  esac
  archive="lumen-${version}-${arch}-${os}.tar.gz"

  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  fetch() { curl --proto '=https' --tlsv1.2 -fsSL -o "$2" "$1"; }

  fetch "$base/$archive" "$tmp/$archive"
  fetch "$base/checksums.txt" "$tmp/checksums.txt"

  expected="$(awk -v f="$archive" '$2 == f { print $1 }' "$tmp/checksums.txt")"
  [ -n "$expected" ] || die "no checksum for $archive"
  if command -v sha256sum >/dev/null 2>&1; then actual="$(sha256sum "$tmp/$archive" | awk '{print $1}')"
  else actual="$(shasum -a 256 "$tmp/$archive" | awk '{print $1}')"; fi
  [ "$expected" = "$actual" ] || die "checksum mismatch for $archive"

  # The checksum comes from the same host: it proves integrity, not authenticity.
  # The cosign check ties checksums.txt to the release workflow, and fails closed.
  if command -v cosign >/dev/null 2>&1; then
    fetch "$base/checksums.txt.sigstore.json" "$tmp/checksums.txt.sigstore.json"
    cosign verify-blob --bundle "$tmp/checksums.txt.sigstore.json" \
      --certificate-identity "https://github.com/${repo}/.github/workflows/release.yml@refs/tags/v${version}" \
      --certificate-oidc-issuer https://token.actions.githubusercontent.com \
      "$tmp/checksums.txt" || die "signature verification failed"
  else
    echo "note: cosign not found; checksum verified, signature not verified" >&2
  fi

  mkdir -p "$install_dir"
  tar -xzf "$tmp/$archive" -C "$tmp"
  install -m 0755 "$tmp/lumen" "$install_dir/lumen"
  echo "installed lumen ${version} to ${install_dir}"
  case ":$PATH:" in *":$install_dir:"*) ;; *) echo "add ${install_dir} to PATH" ;; esac
}

main "$@"
```

### 4.4 Install docs

Put the package managers first, then the script, then the read-before-run form:

```sh
brew install lumenwick/tap/lumen                     # macOS, Linux
scoop bucket add lumenwick https://github.com/lumenwick/scoop-bucket && scoop install lumen
winget install Lumenwick.Lumen
curl --proto '=https' --tlsv1.2 -fsSL https://get.lumenwick.dev | sh   # fallback
# Download, read, then run:
curl --proto '=https' --tlsv1.2 -fsSL -o install.sh https://get.lumenwick.dev && less install.sh && sh install.sh
```

Users who want `/usr/local/bin` run `LUMEN_INSTALL_DIR=/usr/local/bin sudo -E sh install.sh` themselves. The script never calls `sudo`.

The Scoop manifest goes in the bucket repo. Its `checkver` and `autoupdate` fields let the bucket update itself, with no cross-repo token:

```json
{ "version": "<v>", "architecture": { "64bit": { "url": "…/lumen-<v>-x86_64-pc-windows-msvc.zip", "hash": "<sha256>" } },
  "bin": "lumen.exe",
  "checkver": { "github": "https://github.com/lumenwick/lumen" },
  "autoupdate": { "architecture": { "64bit": { "url": "…/lumen-$version-x86_64-pc-windows-msvc.zip",
                  "hash": { "url": "…/checksums.txt" } } } } }
```

## 5. Rollback runbook

Rule: never edit a published asset. None of these commands has a safe dry run, so I haven't run any of them. Run them yourself.

**For the bad Linux release (now):**

1. Find the cause. Compare the replaced asset with the first one if you kept a copy. If you can't explain it, run step 3 as well.
2. Cut `vX.Y.(Z+1)` from the fixed commit, using the new pipeline once it exists. Until then, tag it as a draft and attach all assets before publishing.
3. Soft-remove the bad version and name the safe one. Don't touch its assets, because they can't change:
   - **`gh release edit vX.Y.Z --prerelease --notes-file superseded.md`**. The note says: "Do not use. Linux build was replaced after publish. Use vX.Y.(Z+1)."
   - Repoint `get.lumenwick.dev` at the safe version's `install.sh`.
4. Homebrew: **revert the bump commit in the tap**. Scoop: **revert the bucket commit**. winget: submit a PR with the fixed version.
5. Announce in the changelog and release notes, with the window between the first publish and the replacement. Download counts alone won't identify who is affected.
6. Hard deletion (**`gh release delete`**) is for leaked secrets or malware only.

**If compromise is suspected:**
1. Isolate the runners and repo first.
2. Revoke the App Store Connect API key.
3. Ask the CA to revoke the Windows certificate.
4. Decide with Apple's docs whether to revoke the Developer ID certificate. Revoking it can break installed signed binaries.
5. Rotate the tap and winget bot tokens.

**Rehearsal.** Use a scratch repo, `lumenwick/lumen-release-rehearsal`, with a hello-world binary. Run steps 2–3 on it: the prerelease edit, the installer repoint, and the formula revert. Don't rehearse on `lumen`. Each public rehearsal burns a version.

## 6. Private consumption

Not applicable, since there are no private packages. When you add some, use `publish = ["lumenwick"]` in the crate's `Cargo.toml`. Name the registry on each internal dependency.

CI should build with `cargo build --locked`. Set Dependabot to use a 7-day cooldown on new releases.

## 7. Migration sequence

Dates assume work starts Mon 2026-10-26. The roughly 5 engineer-days are spread across the weeks below.

| Step | By | Evidence it leaves |
|---|---|---|
| 1. Freeze asset replacement. Add the tag ruleset and immutable releases. Create the environments. Move the secrets into them. | 10-27 | Settings screenshots. A run log showing a secret read only in a signing job. |
| 2. Confirm the cause of the bad binary. Check Apple and Windows certificate expiry. Rotate if the cause is unexplained. | 10-28 | Written root cause. Expiry dates in the inventory. |
| 3. Dry-run the workflow on the scratch repo. Include the smoke test and the rollback rehearsal. | 10-30 | Green run. Rehearsal log. |
| 4. Cut the next patch release through the new pipeline. | 11-02 | Draft, then published release with checksums, cosign bundle and attestation. `gh attestation verify` passes. |
| 5. Launch the tap, bucket and winget. Serve the new `install.sh`. Update the docs. | 11-06 | Channel install tested on a clean macOS, Linux and Windows machine. |
| 6. Delete the repo-level secrets. Move Windows signing to the cloud signer and delete the `.pfx`. | 11-13, or when the vendor is ready | Secrets list empty at repo level. |

## 8. Done when

- No signing credential is reachable from the build or test jobs, and none is a repo-level secret.
- Every release comes from a protected tag, behind the `release` approval, as a draft that is published after upload.
- Every release carries `checksums.txt`, a cosign bundle and an attestation. `gh attestation verify` passes.
- The smoke test runs the shipped archive on four platforms before publish.
- `install.sh` runs no `sudo`, pins the version, and fails closed on a checksum or signature mismatch.
- The rollback has been rehearsed on the scratch repo.

**Next:** answer the three questions in §0. Start with how the bad Linux binary came to be bad.