# Release workflow

## Contents

- Repository protection setup
- Two-job skeleton (GitHub Actions)
- Publish steps per registry
- Binary releases and distribution channels (Homebrew, Scoop, winget, `curl | sh`)
- GitLab CI differences
- Monorepos and multi-package releases
- Dependency-confusion probe

## Repository protection setup

1. Tag ruleset: only release managers may create, move or delete release tags (`v*`, monorepo `*/v*`, plain `[0-9]*` for SwiftPM). On Go, SwiftPM and Packagist this rule is the publish credential.
2. Publish environment (`release`, or any name, as long as the job and the registry's trusted-publisher configuration match): reviewers listed as a team, or at least two people besides whoever usually cuts releases; any one approves; self-review blocked; deployments restricted to release tags. The workflow trigger, the tag ruleset and the environment rule must list the same tag patterns, or a tag triggers a run that the gate then blocks. Environment protection on private repositories needs a plan that supports it; check before designing around it.
3. The environment name in the job must match the environment named in the registry's trusted-publisher configuration exactly.
4. Repository and organization secrets: none for publishing once trusted publishing works. Read-only feed credentials live in the environment of the jobs that install private dependencies.

## Two-job skeleton (GitHub Actions)

Pin every action to a full commit SHA with the version as a comment. Resolve a SHA with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>` or let Dependabot or Renovate pin and bump it; never invent one.

```yaml
name: release
on:
  push:
    tags: ["v*", "*/v*"]               # second pattern: monorepo <package>/vX.Y.Z
permissions: {}                      # nothing by default

jobs:
  build:                             # unprivileged: no secrets, no id-token
    runs-on: ubuntu-latest
    permissions: { contents: read }
    outputs:
      dist_tag: ${{ steps.ver.outputs.dist_tag }}
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - name: Tag must equal manifest version; derive the dist-tag
        id: ver
        run: |
          tag="${GITHUB_REF_NAME##*/}"; tag="${tag#v}"
          pkg="${GITHUB_REF_NAME%/*}"                          # monorepo tags: <package>/vX.Y.Z
          if [ "$pkg" = "$GITHUB_REF_NAME" ]; then dir=.; else dir="packages/$pkg"; fi
          version="$(node -p "require('./$dir/package.json').version")"
          name="$(node -p "require('./$dir/package.json').name")"
          [ "$tag" = "$version" ] || { echo "tag $tag != version $version"; exit 1; }
          case "$version" in
            *-*) channel="${version#*-}"; channel="${channel%%.*}"
                 case "$channel" in alpha|beta|rc|next) ;; *) echo "unknown channel $channel"; exit 1 ;; esac ;;
            *)   # default to 0.0.0 only on a genuine not-found; any other error stops the release
                 if out="$(npm view "$name" dist-tags.latest 2>err.log)"; then current="$out"
                 elif grep -q E404 err.log; then current=0.0.0
                 else cat err.log; exit 1; fi
                 highest="$(printf '%s\n%s\n' "$current" "$version" | sort -V | tail -n1)"
                 if [ "$highest" = "$version" ]; then channel=latest
                 else channel="latest-${version%%.*}"; fi ;;      # backport: never move latest backwards
          esac
          echo "dist_tag=$channel" >> "$GITHUB_OUTPUT"
          echo "DIR=$dir" >> "$GITHUB_ENV"                      # same job only
      - run: npm ci && npm run build && npm test && npm pack "./${DIR:-.}"   # build once; no restored caches
      - uses: actions/upload-artifact@<sha>  # v5
        with: { name: dist, path: "*.tgz" }

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release              # reviewers approve here
    permissions:
      contents: read
      id-token: write                 # OIDC, this job only
    env:
      DIST_TAG: ${{ needs.build.outputs.dist_tag }}
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: dist }
      - uses: actions/setup-node@<sha>  # v6
        with: { node-version: "24", registry-url: "https://registry.npmjs.org", package-manager-cache: false }
      - run: npm install -g npm@<pinned 11.15+ version>   # staged publishing needs 11.15.0+
      - run: npm stage publish ./*.tgz --access public --tag "$DIST_TAG"
```

- The guard step reads `package.json`; elsewhere compare the tag with the manifest's version field: `pyproject.toml` `version`, `pom.xml` `<version>`, `gradle.properties` `version`, `*.gemspec` `version`, `pubspec.yaml` `version`, `mix.exs` `version`, `Cargo.toml` `version` (or root `[workspace.package]` with `version.workspace = true`), `build.gradle.kts` `version`, `.csproj` or `Directory.Build.props` `<Version>`, `*.podspec` `s.version`. sbt-dynver, Go, SwiftPM and Packagist derive the version from the tag itself.
- A restricted npmjs package returns 404 to an anonymous `npm view`: give that step a read-only token, or the guard treats every release as the first.
- The publish job installs nothing from the network except the registry client, and runs no project scripts.
- Never add `workflow_dispatch` or a branch trigger to the publish job without the same environment gate.

## Publish steps per registry

The publish job uploads an artifact the build job produced. Where a registry client rebuilds during publish, move that build out or treat the publish job as privileged build code behind the environment gate.

| Registry | Build job | Publish job |
|---|---|---|
| npm | `npm pack` | `npm stage publish <tarball> --access public --tag <channel>`; a maintainer runs `npm stage approve <stage-id>` with 2FA |
| PyPI | `python -m build`, `twine check --strict` | `pypa/gh-action-pypi-publish@<sha>` with `dist/`; no token input |
| crates.io | `cargo publish --dry-run` | `rust-lang/crates-io-auth-action@<sha>`, then `cargo publish --no-verify` from the same commit (skips re-running `build.rs` with the token present) |
| NuGet | `dotnet pack` | `NuGet/login@<sha>`, then `dotnet nuget push` with its output key |
| Maven Central | `mvn verify` (tests, no key) | `mvn deploy` signs in-build and uploads with `autoPublish=false`; a maintainer publishes or drops the validated deployment |
| Docker Hub | build to an OCI layout, no push | push the prebuilt layout (`crane push <layout-dir> <ref>`, `oras cp --from-oci-layout`, or `buildx imagetools create` from buildx 0.33+), then `cosign sign <image>@<digest>` |
| Go | tests only | no publish job: the protected tag is the release; a follow-up job only warms the proxy with `go list -m` |
| pub.dev | `dart pub publish --dry-run` | `dart-lang/setup-dart@<sha>`, then `dart pub publish --force` (OIDC, tag trigger only) |
| RubyGems | `gem build` per platform | `rubygems/configure-rubygems-credentials@<sha>`, then `gem push` each `.gem` |
| Packagist, SwiftPM | tests, `composer validate` or `swift build` | no publish job: the protected tag is the release |
| Hex | `mix hex.build` | `mix hex.publish --yes` with `HEX_API_KEY` from the environment |
| CocoaPods | `pod lib lint` | `pod trunk push` with `COCOAPODS_TRUNK_TOKEN` (trunk writes may fail from 2026-11-01) |
| sbt | `+test` (no key) | `+publishSigned` to local staging (signs in-build), then `sonaUpload`; a maintainer publishes the deployment |
| Gradle Plugin Portal | `publishPlugins --validate-only` | `publishPlugins` with the key and secret from the environment |

Sign in a dedicated job that downloads the unsigned artifact, holds only the signing key in its own protected environment, and runs no project code. Never put a long-lived signing key in the build job (it runs every dependency and test) or in the job holding the upload token. JVM build tools (Maven, Gradle, sbt) sign in-build: there the publish job holds both, so give it a signing subkey with an expiry and run no tests in it.

## Binary releases

CLIs, agents and standalone executables ship as release assets, beside or instead of a registry package. GoReleaser (Go, go-modules.md) and dist (Rust, crates-io.md) generate most of this; other stacks follow the same shape.

1. Build each OS and architecture on its own runner in unprivileged matrix jobs, unsigned; upload them as workflow artifacts.
2. Sign per OS in a signing job that downloads the unsigned binary, holds only the signing credentials in its own protected environment, and runs no project code: macOS Developer ID signing plus notarization (`notarytool` with an App Store Connect API key), Windows Authenticode through a cloud signing service or HSM rather than a key file.
3. Collect the signed binaries in one job, package archives and write `checksums.txt` (SHA-256).
4. Sign the checksum file keylessly (`cosign sign-blob --bundle checksums.txt.sigstore.json checksums.txt --yes`) and attest every archive (`actions/attest@<sha>` with `subject-checksums: checksums.txt`, `id-token: write` and `attestations: write`). Attestations on private repositories need GitHub Enterprise Cloud.
5. Create the release from the protected tag as a draft, with `contents: write`, in the `release` environment; upload archives, checksums and signature bundle; then publish it.
6. Update distribution channels last (Distribution channels, below; npm platform packages in npm.md), each with the narrowest credential that channel allows.

- Never replace an asset on a published release: checksums, SwiftPM binary targets and installers all pin the original bytes. Enable GitHub immutable releases where available: once published, the release's tag and assets can no longer change, which is why step 5 attaches everything to the draft first. Configure GoReleaser's release as a draft for the same reason, then publish it in a final step (`gh release edit <tag> --draft=false`) before channels update.
- GoReleaser OSS builds, signs and publishes in one job, so the job split does not apply; the environment gate, cache ban and pinned tools stand in for it. Its `notarize` section signs and notarizes macOS binaries from Linux, which puts the Apple identity in the job that compiles every dependency: accept that for low-dependency CLIs, or sign `dist/` output in a separate job.
- Users verify with `gh attestation verify <archive> --repo <owner>/<repo>` or `cosign verify-blob` against the bundle, the workflow identity and the CI issuer.

### Distribution channels

Rank by trust per unit of effort: `package-manager channel you control (Homebrew tap, Scoop bucket) > community-reviewed index (winget, homebrew-core) > curl | sh script`. Offer the script as a fallback, never as the only path.

- **Homebrew tap** (`corp/homebrew-tap`): a cask or formula pinning the asset URL and SHA-256. Push with a token scoped to the tap repository only. Casks for unsigned or unnotarized macOS binaries trip Gatekeeper.
- **Scoop bucket** (`corp/scoop-bucket`): a JSON manifest pinning `url` and `hash` per architecture, plus `checkver` and `autoupdate`; users run `scoop bucket add corp https://github.com/corp/scoop-bucket`. GoReleaser `scoops` and dist write it; push with a token scoped to the bucket repository.
- **winget:** manifests submitted by pull request to `microsoft/winget-pkgs`, validated automatically and approved by moderators, so a release reaches users hours to days later. Generate them with `wingetcreate`, `komac` or GoReleaser `winget`. The pull request comes from a fork, so the bot needs a token with public-repository scope that cannot be narrowed to one repository: keep it on a dedicated bot account, in the `release` environment only, and keep the fork in sync.
- **`curl | sh` installer:**
  - Trade-offs: the user runs unreviewed remote code; whoever controls the host or the script serves every installer at once; a dropped connection can execute a truncated script; a checksum fetched from the same host proves integrity, not authenticity.
  - Build it so that it: wraps the body in a function called on the last line (a truncated download runs nothing); downloads over HTTPS only (`curl --proto '=https' --tlsv1.2 -fsSL`); installs a pinned version (overridable by an environment variable) into a user directory, never with `sudo` by default; verifies the archive against `checksums.txt` and, when cosign is present, verifies the checksum bundle against the release workflow identity (`cosign verify-blob --bundle ... --certificate-identity <workflow ref> --certificate-oidc-issuer https://token.actions.githubusercontent.com`), failing closed on mismatch.
  - Serve the script from the release itself or a host you control with a pinned path, and document the "download, read, then run" form beside the one-liner.
  - dist generates shell and PowerShell installers; check what yours verifies and add the signature check yourself.

## GitLab CI differences

- OIDC tokens come from `id_tokens` with a registry-specific `aud`. Every job in the pipeline can mint one, so put publishing in a protected pipeline that runs only for protected tags or branches.
- NuGet requires a branch `ref`: publish from a protected release branch pipeline, not a tag pipeline.
- Use protected environments with approval rules as the review gate.

## Monorepos and multi-package releases

- Publish in dependency order, leaves first. Across registries (native SDK, then the wrapper that pins it), wait until the dependency resolves publicly before publishing the dependent.
- Make the job idempotent: skip any `name@version` the registry already holds, so a rerun after a partial failure completes the release instead of failing on the first package.
- Treat a partial release as roll-forward: finish publishing, never unpublish the packages that made it.
- Release tools that wrap the registry client (changesets, semantic-release, release-please, pnpm or yarn publish) may not support staged publishing or OIDC yet. Let the tool version and pack, then run the registry's own publish command per tarball, or keep direct publish enabled only for that configuration behind the environment gate.

## Dependency-confusion probe

A probe only proves something if a public package with an internal-looking name actually exists upstream. Removing the internal source and watching installs fail proves nothing: everything fails.

1. **Canary.** npm: publish one harmless canary in your own public scope (`@corp/confusion-canary`), never internally. Other registries: use an existing public package whose name matches an internal prefix rule. Never publish a canary to Maven Central or nuget.org (permanent), and PyPI and crates.io ban placeholders.
2. **Query the internal endpoint's metadata only.** Never download or install the probe target: a misconfigured endpoint would serve squatter code, and building an sdist runs it.

Authenticate with the read-only credential CI uses, prove the request can see the feed, then assert the exact status. A 401, 403, 5xx or DNS error is inconclusive, never a pass.

```sh
# credentials from a netrc file, never argv
code() { curl -s -o /dev/null -w '%{http_code}' --netrc-file "$FEED_NETRC" "$1"; }
[ "$(code "$INTERNAL_INDEX/corp-sdk/")" = 200 ] || { echo "probe cannot see the feed"; exit 1; }
[ "$(code "$INTERNAL_INDEX/<public corp-* name>/")" = 404 ] || { echo "probe FAILED or inconclusive"; exit 1; }
# npm: `npm view "@corp/confusion-canary" --registry "$INTERNAL_NPM"` must fail with E404, not E401/E403
```

3. **Check the blocking rule itself** on the feed: the exclude pattern, routing rule, origin control or disabled forwarding covers every internal prefix. Use the feed's rule-test feature where it has one.
4. **Check client resolution:** every internal entry in the lockfile points at the internal host (`uv.lock` source, `package-lock.json` resolved URL, `packages.lock.json` source).
5. When no public name exists to probe with, steps 3 and 4 are the proof; record that step 2 did not apply.
6. Repeat after any feed reconfiguration: deleting a private package while public forwarding is on reopens the hole.
