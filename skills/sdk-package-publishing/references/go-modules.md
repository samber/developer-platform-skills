# Go modules

## Contents

- Library vs binary
- CI auto-publishing: library tags, GoReleaser for binaries
- Public publishing: major versions, retraction
- Private publishing
- Private consumption
- Dated changes

## Library vs binary

- **Library (SDK module):** a pushed semver tag is the whole release. No build artifact, no GoReleaser.
- **Binary (CLI, agent, server):** build with GoReleaser from the same tag: archives per OS and architecture on the GitHub release, `checksums.txt`, a cosign signature bundle, SBOMs, a Homebrew tap, container images and deb/rpm/apk packages. Users who prefer source can still `go install example.com/sdk/cmd/corp@v1.4.2`.
- A repository that holds both cuts one tag: the tag releases the module, and GoReleaser builds the binaries from it.

## CI auto-publishing

**Library tags**

- No upload step and no publish credential: the module path is the repository URL, and a pushed semver tag (`v1.4.2`) is the release. `proxy.golang.org` caches it on first request and `sum.golang.org` records its checksum forever.
- Release flow: `go mod tidy`, `go test ./...` as a required status check on the release branch (a test job triggered by the tag only detects, since the tag already is the release), tag only commits already on the protected branch (a tag job running `git merge-base --is-ancestor "$GITHUB_SHA" origin/main` detects violations), push the tag, then warm the proxy with `GOPROXY=proxy.golang.org go list -m example.com/sdk@v1.4.2`.
- Never move or re-push a tag. The checksum database already holds the first content; every consumer then gets a security error.
- Protect release tags in the forge (tag protection rules, restricted pushers): tag control is the publish credential for Go.
- Submodules in a monorepo tag with the directory prefix: `sdk/go/v1.4.2`.
- Provenance: the checksum database is the integrity record; there is nothing to sign for a library.

**GoReleaser for binaries**

- Config `version: 2` in `.goreleaser.yaml`; preflight with `goreleaser check` and `goreleaser release --snapshot --clean` in the build job.
- Trigger on the protected tag. The job needs `fetch-depth: 0`, `contents: write` (release), `packages: write` (ghcr.io images), `id-token: write` (keyless cosign), and `attestations: write` when attesting.
- GoReleaser builds and publishes in one job, so that job holds the release token while it compiles. Run it in the `release` environment, with no restored caches and pinned tool versions.
- `notarize` (open-source edition) signs and notarizes macOS binaries from Linux with `MACOS_SIGN_P12`, `MACOS_SIGN_PASSWORD`, `MACOS_NOTARY_KEY`, `MACOS_NOTARY_KEY_ID` and `MACOS_NOTARY_ISSUER_ID` in the `release` environment. Casks for unnotarized binaries trip Gatekeeper.
- Sections to configure:
  - `archives` and `checksum` (`checksums.txt`);
  - `signs`: `cosign sign-blob --bundle=${signature} ${artifact} --yes` on the checksum file, keyless through the CI identity;
  - `sboms`: syft, installed in a prior step (the action installs neither syft nor cosign);
  - `homebrew_casks`: `brews` formulas are deprecated since v2.10; casks target macOS, so serve Linux users with `nfpms`;
  - `nfpms`: deb, rpm, apk;
  - `scoops` and `winget`: Windows channels, with the credential limits in release-workflow.md;
  - `dockers_v2` (v2.12+, marked provisional) or `dockers` with `docker_manifests`.
- The Homebrew tap lives in another repository, so the built-in token cannot push to it. Use a token scoped to the tap repository only, stored in the `release` environment.
- Attest every archive with `actions/attest@<sha>` and `subject-checksums: dist/checksums.txt`; `subject-path` on the checksum file attests only that file, and `gh attestation verify <archive>` then fails.
- GoReleaser OSS cannot split build from publish. There, the environment gate, the cache ban and pinned tools replace the unprivileged build job of release-workflow.md.
- GoReleaser Pro features (npm publishing, DMG/MSI installers, split builds, apt/yum repositories) are not in the open-source edition; confirm the edition before designing around them.

## Public publishing

**Major versions**

- From v2, the module path needs the `/v2` suffix (`module example.com/sdk/v2`) and every internal import changes with it. A v2+ tag on a module whose `go.mod` lacks the suffix is unusable: `go get` rejects it. (`+incompatible` exists only for repositories with no `go.mod`.)
- Mark an old major deprecated with a `// Deprecated: use example.com/sdk/v2` comment above the `module` line, published in a new tag.

**Retraction (rollback)**

- Versions can never be deleted from the proxy or the checksum database.
- Retract by publishing a newer tag whose `go.mod` holds the directive, with a rationale comment users will see:

```
retract (
    v1.4.3 // Breaks token refresh; use v1.4.4.
)
```

- A version can retract itself; if the highest version retracts itself, `@latest` falls back to the previous one. Retracted versions are skipped by `@latest` and upgrades, hidden from `go list -m -versions`, labelled retracted on pkg.go.dev, and flagged to users who depend on them; pinned builds keep working.

## Private publishing

- A private module is a private repository plus tags; nothing is uploaded.
- Optional private proxy for caching and access control: Google Artifact Registry (Go format), Artifactory, Nexus, or a self-hosted GOPROXY server. GitHub Packages and AWS CodeArtifact have no Go registry; GitLab's Go proxy is experimental.

## Private consumption

```sh
# CI environment for a company module tree
export GOPRIVATE=corp.example.com        # prefix match; also sets GONOPROXY and GONOSUMDB
export GOPROXY=https://proxy.golang.org,direct
```

- `GOPRIVATE` keeps private paths away from the public proxy and checksum database; without it, every private path is sent to both.
- Never set `GOSUMDB=off` or a broad `GONOSUMDB` to make a private fetch pass: that drops checksum verification for public modules too. Scope `GONOSUMDB` to private prefixes, and keep `GOINSECURE` (plain HTTP) out of CI.
- Credentials: `GOAUTH` (Go 1.24+, default `netrc`). In CI write `.netrc` from a secret, or rewrite to SSH:

```
# ~/.netrc rendered at job start from the secret store (netrc expands nothing);
# mode 600, removed by an always-run cleanup step on self-hosted runners
machine github.com login ci-bot password <GO_READ_TOKEN value>
# or: git config --global url."ssh://git@github.com/".insteadOf "https://github.com/"
```

- With a private proxy serving everything, set `GOPROXY=https://goproxy.internal.example.com` and `GONOSUMDB=corp.example.com`. A comma between proxies falls back only on 404/410; a pipe falls back on any error, which can leak private paths during an outage.
- Import paths are URLs, so Go has no flat namespace to squat; dependency confusion here means a leaked path or a vanity domain you no longer control. Keep vanity domains renewed.

## Dated changes

- 2024-05: GoReleaser v2 (`--clean` replaces `--rm-dist`).
- GoReleaser v2.10: `homebrew_casks` added, `brews` deprecated (harder deprecation in v2.16).
- GoReleaser v2.12: `dockers_v2`, planned to replace `dockers` and `docker_manifests` in v3.
