# Kestrel Compute: Go SDK and CLI publishing plan

Everything below is a **draft pending your approval**. I ran nothing. Each command that publishes, pushes, tags or changes a setting is marked `# **SIDE EFFECT**` and left for you to run.

## 0. Assumptions

Correct any of these before applying the files.

- Hosting and CI: the repo is on GitHub and CI is GitHub Actions on hosted runners. The module path is `go.kestrel.dev/sdk`, served through a vanity domain.
- Layout: the CLI lives in the same module at `./cmd/kestrel`.
- Binaries: the CLI has no signed binary releases today. Customers use `go install`.
- Organization names (placeholders): GitHub org `kestrel-dev`, tap repo `kestrel-dev/homebrew-tap`.
- Branches: `main` is the release branch. Whether `main` already holds v2 work is unknown, so section 2 covers both cases.
- macOS signing: no Apple Developer ID is assumed. The `notarize` block below is optional, and without it Homebrew casks trip Gatekeeper.
- Scope: Windows channels (Scoop, winget) and container images are out of scope.

| Artifact | Registry or channel | Publish path today | Credential | Target |
|---|---|---|---|---|
| Go module `go.kestrel.dev/sdk` | proxy.golang.org, sum.golang.org | Pushed tag, plus a `publish` job that only runs `go build` | None. The tag is the release. | Tag ruleset, tests, proxy warm-up |
| `kestrel` CLI | GitHub release assets, Homebrew tap | `go install` only | None yet | GoReleaser in the `release` environment |
| Homebrew tap | `kestrel-dev/homebrew-tap` | Does not exist | Needs a tap-scoped credential | GitHub App token, short-lived, tap repo only |

## 1. Why `go get go.kestrel.dev/sdk@v1.6.0` fails

**Cause.** proxy.golang.org caches a version the first time anyone requests it. sum.golang.org then records that content's hash permanently. Moving the tag after that point creates two versions of "v1.6.0":

- One has the original CHANGELOG date and is what the proxy and checksum database hold.
- The other has the corrected date and is what git now serves.

Anyone who fetches the other one gets `SECURITY ERROR ... checksum mismatch`. That includes people using `GOPROXY=direct`, a corporate Artifactory or Athens proxy that cached the other copy, or a `go.sum` written during the window between your two pushes.

**This cannot be repaired.** Re-pushing the tag again will not help. The proxy and sumdb never forget, and the Go tool correctly refuses to trust the new bytes. A hash in `go.sum` that disagrees with the sumdb is the security feature working.

**Read-only diagnosis (safe to run):**

```sh
# scratch dir, outside any repo
mkdir /tmp/kestrel-probe && cd /tmp/kestrel-probe
curl -s https://proxy.golang.org/go.kestrel.dev/sdk/@v/v1.6.0.info      # Origin.Hash = commit the proxy holds
git -C <your clone> rev-parse 'v1.6.0^{commit}'                          # commit git serves now
git -C <your clone> reflog show --tags 2>/dev/null | head                # your original commit, if still local
```

Ask the customer for the full error text and the output of `go env GOPROXY GOSUMDB GOFLAGS GONOSUMDB`.

- If `Origin.Hash` is not the commit git serves now, this explanation is confirmed.
- If the proxy returns 404 for v1.6.0, nobody cached it. In that case the mismatch is local to the customer's `go.sum`.

**Fix: roll forward and retract.** Do not touch the tag again. Details are in section 2.

**Reply for the customer:**

> v1.6.0 was re-tagged after it was first fetched, so the checksum database and git disagree. Use v1.6.1, which retracts v1.6.0. Run `go get go.kestrel.dev/sdk@v1.6.1`. If a stale `go.sum` blocks you, delete the `go.kestrel.dev/sdk v1.6.0` lines and run `go mod tidy` with default `GOPROXY` and `GOSUMDB`. Do **not** set `GONOSUMDB`, `GOFLAGS=-insecure` or `GOSUMDB=off`. That disables verification for every module.

## 2. Rollback runbook: Go

1. **Roll forward first.** Ship v1.6.1 on the v1 line. Its only change is the retract directive; the CHANGELOG fix is already in the commit the v1.6.0 tag now points to.
   - If `main` has no v2 work yet, release from `main`.
   - If `main` already has v2 work, branch from the current v1.6.0 commit.

   ```sh
   git fetch origin
   git switch -c release-v1 v1.6.0          # skip if main has no v2 work; use main instead
   ```

   Add the following to `go.mod`:

   ```
   // Deprecated notice is added later, once v2 exists (section 6).
   retract v1.6.0 // Tag re-pushed after publication; checksum mismatch. Use v1.6.1.
   ```

   ```sh
   go mod tidy && go test ./...
   git commit -am "fix: retract v1.6.0 after tag re-push"
   git push origin release-v1                 # **SIDE EFFECT**
   git tag -s v1.6.1 && git push origin v1.6.1   # **SIDE EFFECT: this is the release**
   ```

2. **Soft-remove v1.6.0.** The retract directive does this. Retracted versions are skipped by `@latest` and upgrades, hidden from `go list -m -versions`, and flagged on pkg.go.dev. Pinned builds keep working. Do not move or delete the v1.6.0 tag.
3. **Warm the proxy** from a clean machine, after confirming the tag's commit with `git ls-remote --tags origin v1.6.1`:

   ```sh
   GOPROXY=https://proxy.golang.org go list -m go.kestrel.dev/sdk@v1.6.1   # **SIDE EFFECT**: fixes v1.6.1 in sumdb forever
   ```

4. **Verify:**

   ```sh
   GOPROXY=https://proxy.golang.org go list -m -retracted -versions go.kestrel.dev/sdk
   GOPROXY=https://proxy.golang.org go list -m -u go.kestrel.dev/sdk@latest
   ```

   Expect v1.6.0 labelled retracted and `@latest` resolving to v1.6.1.
5. **Carry the directive forward.** Every later v1.x tag must keep the `retract` line, because Go reads retractions from the highest version.
6. **Announce** in the CHANGELOG and the security or advisory channel. Record the v1.6.0 CHANGELOG date discrepancy in the v1.6.1 notes.
7. **Rehearse** on a scratch module and scratch repo first (tag, retract, `go list -m -retracted`). Every public rehearsal burns a version forever.

⚠️ v1.6.1 is cut from an old commit, so the tag-triggered workflow that runs is the old one (the `go build` job). That is harmless. The new pipeline starts with the v2 pre-release.

## 3. Prevent a repeat: tag protection

Tag control is the Go publish credential. This is a repo setting change; you apply it. In Settings → Rules → Rulesets, create a **tag** ruleset:

- Target: `v*`. Add `*/v*` if you ever tag submodules.
- Enforcement: Active.
- Rules: restrict creation, restrict updates, restrict deletions, block force pushes.
- Bypass: none. Release managers get permission to create tags, not to update or delete them. A force-push of an existing tag then fails for everyone, including you.

Create the **`release` environment** (Settings → Environments):

- Required reviewers: a team, or at least two people besides whoever cuts releases (any one approves).
- Self-review blocked.
- Deployment tags restricted to `v*`.
- It holds the macOS signing secrets (if you use them) and the GitHub App secrets.

Also enable **immutable releases** on the repo, so a published release's tag and assets cannot change.

## 4. The "publish" job: there is no upload to proxy.golang.org

⚠️ **No upload step exists.** The proxy pulls from git when asked, and the tag is the release. A job that "uploads the module" cannot be built, and there is no credential for it.

What the job should do:

- gate the tag: tests, tag on a release branch, module path matches the major version;
- build and publish the CLI (GoReleaser, next section);
- warm the proxy with `go list -m`.

**Draft `.github/workflows/release.yml`.** Replace `<sha>` with the commit SHA for the stated version; resolve it with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`. Never guess one.

```yaml
name: release
on:
  push:
    tags: ["v*"]            # must match the tag ruleset and the release environment's tag rule
permissions: {}

jobs:
  verify:                   # unprivileged: no secrets, no id-token
    runs-on: ubuntu-latest
    permissions: { contents: read }
    outputs:
      module: ${{ steps.guard.outputs.module }}
    steps:
      - uses: actions/checkout@<sha>        # v6
        with: { fetch-depth: 0, persist-credentials: false }
      - uses: actions/setup-go@<sha>        # v6
        with: { go-version-file: go.mod, cache: false }
      - name: Tag must sit on a release branch and match the module major
        id: guard
        run: |
          set -euo pipefail
          tag="$GITHUB_REF_NAME"
          on_branch=0
          for b in main release-v1; do     # release-v1 exists only while v1 patches ship
            if git rev-parse --verify -q "origin/$b" >/dev/null \
               && git merge-base --is-ancestor "$GITHUB_SHA" "origin/$b"; then on_branch=1; fi
          done
          [ "$on_branch" = 1 ] || { echo "tag commit is on no release branch"; exit 1; }
          major="${tag%%.*}"; major="${major#v}"
          module="$(go list -m)"
          suffix="${module##*/}"
          if [ "$major" -ge 2 ]; then
            [ "$suffix" = "v$major" ] || { echo "tag $tag needs module path ending /v$major, got $module"; exit 1; }
          else
            if [[ "$suffix" =~ ^v[0-9]+$ ]]; then echo "v0/v1 tag but module path is $module"; exit 1; fi
          fi
          echo "module=$module" >> "$GITHUB_OUTPUT"
      - run: go mod tidy && git diff --exit-code go.mod go.sum
      - run: go vet ./... && go test -race ./...
      - uses: goreleaser/goreleaser-action@<sha>   # v6/v7: match your pinned major
        with:
          version: "<pinned v2.x.y>"        # exact version, not "latest"
          args: check
      - uses: goreleaser/goreleaser-action@<sha>
        with:
          version: "<pinned v2.x.y>"
          args: release --snapshot --clean --skip=sign,sbom,notarize   # trim to what `release --help` lists for your pinned version

  release:
    needs: verify
    runs-on: ubuntu-latest
    environment: release                    # reviewers approve here
    permissions:
      contents: write                       # release assets
      id-token: write                       # keyless cosign + attestation
      attestations: write
    steps:
      - uses: actions/checkout@<sha>        # v6
        with: { fetch-depth: 0, persist-credentials: false }
      - uses: actions/setup-go@<sha>        # v6
        with: { go-version-file: go.mod, cache: false }   # no restored caches in a privileged job
      - uses: sigstore/cosign-installer@<sha>              # the goreleaser action installs neither
      - uses: anchore/sbom-action/download-syft@<sha>
      - uses: goreleaser/goreleaser-action@<sha>
        with:
          version: "<pinned v2.x.y>"
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # Drop these five if you skip notarization (and the notarize block in .goreleaser.yaml)
          MACOS_SIGN_P12: ${{ secrets.MACOS_SIGN_P12 }}
          MACOS_SIGN_PASSWORD: ${{ secrets.MACOS_SIGN_PASSWORD }}
          MACOS_NOTARY_KEY: ${{ secrets.MACOS_NOTARY_KEY }}
          MACOS_NOTARY_KEY_ID: ${{ secrets.MACOS_NOTARY_KEY_ID }}
          MACOS_NOTARY_ISSUER_ID: ${{ secrets.MACOS_NOTARY_ISSUER_ID }}
      - uses: actions/attest@<sha>
        with:
          subject-checksums: dist/checksums.txt    # not subject-path: that attests only the checksum file
      - name: Publish the draft release (assets are final from here)
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh release edit "$GITHUB_REF_NAME" --repo "$GITHUB_REPOSITORY" --draft=false
      # Channels update last, after the release is public. Skipped for pre-releases.
      - name: Mint a tap-scoped token (GitHub App, expires in an hour)
        if: ${{ !contains(github.ref_name, '-') }}
        id: tap
        uses: actions/create-github-app-token@<sha>
        with:
          app-id: ${{ vars.TAP_APP_ID }}
          private-key: ${{ secrets.TAP_APP_PRIVATE_KEY }}
          owner: kestrel-dev
          repositories: homebrew-tap
      - name: Push the cask to the tap
        if: ${{ !contains(github.ref_name, '-') }}
        env:
          GH_TOKEN: ${{ steps.tap.outputs.token }}
        run: |
          set -euo pipefail
          cask="$(find dist -name 'kestrel.rb' -path '*Casks*' | head -n1)"
          [ -n "$cask" ] || { echo "cask not generated"; exit 1; }
          gh auth setup-git
          gh repo clone kestrel-dev/homebrew-tap "$RUNNER_TEMP/tap"
          mkdir -p "$RUNNER_TEMP/tap/Casks"
          cp "$cask" "$RUNNER_TEMP/tap/Casks/kestrel.rb"
          cd "$RUNNER_TEMP/tap"
          git config user.name "kestrel-release-bot"
          git config user.email "release-bot@kestrel.dev"
          git add Casks/kestrel.rb
          git commit -m "kestrel ${GITHUB_REF_NAME}"
          git push

  warm-proxy:               # no credentials: it only asks the proxy to fetch the tag
    needs: [verify, release]
    runs-on: ubuntu-latest
    permissions: {}
    env:
      MODULE: ${{ needs.verify.outputs.module }}
    steps:
      - uses: actions/setup-go@<sha>        # v6
        with: { go-version: stable, cache: false }
      - name: Warm proxy.golang.org and record the checksum
        run: |
          set -euo pipefail
          mkdir "$RUNNER_TEMP/warm" && cd "$RUNNER_TEMP/warm"
          for i in 1 2 3 4 5; do
            GOPROXY=https://proxy.golang.org GOSUMDB=sum.golang.org \
              go list -m "${MODULE}@${GITHUB_REF_NAME}" && exit 0
            sleep 30
          done
          echo "proxy did not serve ${MODULE}@${GITHUB_REF_NAME}"; exit 1
```

Notes on the draft:

- The workflow has no `workflow_dispatch` and no branch trigger. Adding either needs the same environment gate.
- The verify job only detects a bad tag after the fact, since the tag already exists. The tag ruleset is the real control.
- GoReleaser OSS builds and publishes in one job, so the job split does not apply to it. The environment gate, no caches and pinned versions replace it.
- The tap token is minted after GoReleaser has compiled, so the compile step never sees it.

## 5. GoReleaser for the CLI, with Homebrew

**Draft `.goreleaser.yaml`**, using the v2.10+ `homebrew_casks` (the `brews` key is deprecated). It uses the `/v2` import path that the next release needs:

```yaml
version: 2
project_name: kestrel

builds:
  - id: kestrel
    main: ./cmd/kestrel
    binary: kestrel
    env: [CGO_ENABLED=0]
    flags: [-trimpath]
    ldflags:
      - -s -w -X go.kestrel.dev/sdk/v2/internal/version.Version={{ .Version }}
      - -X go.kestrel.dev/sdk/v2/internal/version.Commit={{ .Commit }}
    goos: [linux, darwin, windows]
    goarch: [amd64, arm64]
    mod_timestamp: "{{ .CommitTimestamp }}"

archives:
  - formats: [tar.gz]
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    format_overrides:
      - { goos: windows, formats: [zip] }

checksum:
  name_template: checksums.txt
  algorithm: sha256

signs:                      # keyless: the CI identity signs the checksum file
  - cmd: cosign
    artifacts: checksum
    signature: "${artifact}.sigstore.json"
    args: ["sign-blob", "--bundle=${signature}", "${artifact}", "--yes"]

sboms:
  - artifacts: archive

# Optional: needs an Apple Developer ID. Without it, delete this block and the five MACOS_* env lines
# in the workflow, and accept that the cask triggers Gatekeeper.
notarize:
  macos:
    - enabled: '{{ isEnvSet "MACOS_SIGN_P12" }}'
      ids: [kestrel]
      sign:
        certificate: "{{ .Env.MACOS_SIGN_P12 }}"
        password: "{{ .Env.MACOS_SIGN_PASSWORD }}"
      notarize:
        issuer_id: "{{ .Env.MACOS_NOTARY_ISSUER_ID }}"
        key_id: "{{ .Env.MACOS_NOTARY_KEY_ID }}"
        key: "{{ .Env.MACOS_NOTARY_KEY }}"

nfpms:                      # casks are macOS-only; this serves Linux users
  - id: kestrel
    package_name: kestrel
    formats: [deb, rpm, apk]
    vendor: Kestrel Compute
    homepage: https://kestrel.dev
    license: <SPDX id>
    maintainer: <release contact>

release:
  draft: true               # assets attach to a draft; the workflow publishes it before channels update
  prerelease: auto          # tags with a hyphen (v2.0.0-rc.1) become pre-releases

homebrew_casks:
  - name: kestrel
    homepage: https://kestrel.dev
    description: Kestrel Compute CLI
    repository:
      owner: kestrel-dev
      name: homebrew-tap
    skip_upload: true       # cask is generated into dist/; the workflow pushes it after the release is public
```

- `skip_upload` on `homebrew_casks` is from memory. Confirm the key with `goreleaser check` on your pinned version.
- The cask URL points at the release asset. Pushing the cask while the release is still a draft would break `brew install` during that window, which is why the workflow pushes it last.
- I did not verify the `notarize` and `--skip` flag names against your pinned GoReleaser version. `goreleaser check` and the snapshot run in `verify` will catch a wrong name.
- No GoReleaser Pro features are used.

**Credentials.** No long-lived credential is needed:

| Credential | Where | Lifetime |
|---|---|---|
| `GITHUB_TOKEN` | Job-scoped, built in | One run |
| GitHub App for the tap (`TAP_APP_ID` variable, `TAP_APP_PRIVATE_KEY` secret) | `release` environment | Token lasts an hour and covers `homebrew-tap` only; the key lives until rotated, so list a rotation date |
| `MACOS_*` secrets (optional) | `release` environment | Per Apple certificate expiry |

Set up the App yourself: contents write on `kestrel-dev/homebrew-tap` only, installed only on that repo. A fine-grained PAT scoped to the tap repo also works, but it expires within 90 days and needs manual rotation, so I chose the App.

**User install paths:**

- `brew install --cask kestrel-dev/tap/kestrel` (macOS)
- `.deb`, `.rpm` or `.apk` from the release (Linux)
- `go install go.kestrel.dev/sdk/v2/cmd/kestrel@v2.0.0` (source)

Verification:

- `gh attestation verify <archive> --repo <owner>/<repo>`
- `cosign verify-blob` against `checksums.txt.sigstore.json`

## 6. v2.0.0: what the breaking release requires

Go ties the major version to the import path, so this is a checklist, not just a tag.

1. **Module path.** Change `go.mod` to `module go.kestrel.dev/sdk/v2` and rewrite every internal import. A v2.x tag on a module without `/v2` is rejected by `go get`. This rewrite is mechanical:

   ```sh
   # in the working tree
   perl -pi -e 's#"go\.kestrel\.dev/sdk(?!/v2)#"go.kestrel.dev/sdk/v2#g' $(git ls-files '*.go')
   go mod tidy && go build ./... && go test ./...
   ```

   Then grep docs, examples, `go:generate` lines, the `ldflags` above and CI for the old path. `ugrep` honours `.gitignore`; use `/usr/bin/grep -rE` for a repo-wide sweep.
2. **Vanity domain.** The `go-import` handler at `go.kestrel.dev` must answer `go.kestrel.dev/sdk/v2?go-get=1` with the same prefix mapping as the root path. A handler that only matches `/sdk` exactly breaks every v2 fetch. Test it before the tag.
3. **Branch strategy.** Keep v1 patches on `release-v1`, cut at the last v1 commit. Put v2 on `main`. Both branches are in the verify job's allowed list.
4. **After v2.0.0 is public**, publish one more v1 tag (v1.6.2 or later) that adds `// Deprecated: use go.kestrel.dev/sdk/v2` above the `module` line and keeps the v1.6.0 retract. Do not deprecate v1 before v2 exists.
5. **Migration guide.** Write one for the breaking changes. `samber/developer-relations-skills@version-migration-guide` covers it.
6. **Pre-release first.** Tags are immutable, so burn a pre-release rather than a real version: cut `v2.0.0-rc.1` through the full pipeline. Pre-releases skip the cask push.

## 7. Migration sequence

| When | Step | Evidence it leaves |
|---|---|---|
| Today, 2026-10-23 | Run the section 1 diagnosis. Apply the tag ruleset (section 3). Do not touch the v1.6.0 tag. | `.info` output saved; ruleset screenshot |
| Today or tomorrow | Cut and push v1.6.1 with the retract; warm the proxy; verify (section 2); reply to the customer. | `go list -m -retracted` output |
| Within the week | Create the `release` environment, the tap repo and the GitHub App. Open a PR with `release.yml` and `.goreleaser.yaml`, replacing the old `publish` job. | PR with `goreleaser check` and the snapshot green |
| Before v2 | Rehearse the pipeline on a scratch repo with a scratch tap. Rehearse the retraction on a scratch module. | Scratch release and `brew install` log |
| Then | Rewrite the module path and imports, then test the vanity handler. | Green build and tests on `/v2` |
| Then | Tag `v2.0.0-rc.1`, approve the `release` environment, and verify the release (`gh attestation verify`, cosign, `go get ...@v2.0.0-rc.1` from a clean machine). | Verified rc release |
| Last | Tag `v2.0.0`, approve, verify. Publish the deprecated v1 tag. | Release page with checksums, bundle, attestation |

## 8. Gates for "done"

- No publish credential exists for the Go module. Release tags are creatable only by release managers, and updates and deletions are blocked.
- The only standing secrets are the optional `MACOS_*` ones and the GitHub App key, all inside the `release` environment.
- Every binary release carries `checksums.txt`, a cosign bundle and an attestation.
- A rollback primitive (`retract`) is written and has been rehearsed on a scratch module.
- Not applicable: the dependency-confusion probe. Go has no flat namespace to squat. Keep `go.kestrel.dev` renewed, and have CI use `GOPRIVATE` for any internal Kestrel module paths.

## 9. Open decisions for you

1. Release v1.6.1 from `main` or from a `release-v1` branch. This depends on whether `main` has v2 work.
2. Whether you have an Apple Developer ID. If not, ship the cask un-notarized (with the Gatekeeper warning) or get one first.
3. GitHub App (recommended) or a fine-grained PAT for the tap.
4. Whether to restore the git tag v1.6.0 to the original commit so git, the proxy and sumdb agree. I recommend against it. It is a second tag move, and anyone who fetched the amended content directly would break the other way. Retraction already handles both populations.