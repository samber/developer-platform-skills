# Kestrel Compute: v1.6.0 checksum fix, real publish job, GoReleaser + Homebrew, v2.0.0

I haven't seen your repo, so I assumed the following. Adjust any that are wrong:
- The module is at the repo root.
- The CLI entrypoint is `./cmd/kestrel`.
- The GitHub org is `kestrel`.

If the SDK module lives in a subdirectory such as `sdk/`, its tags must be `sdk/v1.6.0`, not `v1.6.0`. Check this first.

## Order of work

1. Restore the v1.6.0 tag to its original commit.
2. Lock release tags so this can't happen again.
3. Replace the CI publish job and add GoReleaser.
4. Prepare v2.0.0.

## 1. Why the checksum fails, and the fix

**Cause.** Go module versions are immutable by design, in two places:
- `proxy.golang.org` cached the zip for the first v1.6.0 and never refetches it.
- `sum.golang.org` (the checksum DB) permanently recorded that zip's hash.

The force-pushed tag now points at different bytes. Any client that fetches from the repo instead of the proxy cache gets a zip whose hash doesn't match the sumdb. That includes `GOPROXY=direct`, a corporate proxy such as Artifactory or Athens that cached the new tag, and a stale `go.sum`. Go then reports `checksum mismatch` / `SECURITY ERROR`.

You can't purge or overwrite a version on the public proxy. The fix is to make the tag match what the proxy already has.

**Steps**

```bash
# 1. Find the commit the proxy cached (Origin.Hash).
curl -s https://proxy.golang.org/go.kestrel.dev/sdk/@v/v1.6.0.info
# Fallbacks if Origin is missing: the first release workflow run's SHA,
# `git reflog`, or the GitHub Release page.

# 2. Confirm the commit is still fetchable, then point the tag back at it.
git fetch origin
git cat-file -t <ORIG_SHA>
git tag -f v1.6.0 <ORIG_SHA>                  # **rewrites a local tag**
git push --force origin refs/tags/v1.6.0      # **force-pushes a tag**

# 3. Verify: tag commit must equal the proxy's Origin.Hash.
git rev-parse 'v1.6.0^{commit}'
```

The wrong CHANGELOG date isn't worth a second tag move. Keep the corrected CHANGELOG on `main`, and it ships in v2.0.0. If you want a v1 fix release, tag v1.6.1 from `release/v1` (see section 4). Use `retract` only if the original v1.6.0 content is actually bad. It isn't here.

**Message for the customer**

> We moved the v1.6.0 tag by mistake and have restored it to the original commit. Run `go clean -modcache` (or delete `$(go env GOMODCACHE)/cache/download/go.kestrel.dev/sdk/@v/v1.6.0.*`), remove the `go.kestrel.dev/sdk v1.6.0` lines from `go.sum`, then `go get go.kestrel.dev/sdk@v1.6.0`. If you use an internal proxy, purge its cached copy of this version. Don't set `GONOSUMDB`, `GONOSUMCHECK` or `GOFLAGS=-insecure` to work around it.

## 2. Make tags immutable

This **creates a repo ruleset**. It blocks updating or deleting `v*` tags and still allows creating them.

```bash
gh api -X POST repos/kestrel/<repo>/rulesets --input - <<'EOF'
{
  "name": "immutable-release-tags",
  "target": "tag",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/tags/v*"], "exclude": [] } },
  "rules": [ { "type": "update" }, { "type": "deletion" } ]
}
EOF
```

Run this after step 1, because the ruleset would also block your restore. The release workflow below also refuses tags that aren't on `main` or `release/v*`.

## 3. Publish job and GoReleaser

### What "publish to proxy.golang.org" means

You can't upload to the Go proxy. It pulls from your VCS on demand, so **pushing the tag is the publish**. A real publish job does four things:
1. Gate the tag with checks.
2. Force the proxy to fetch it right away.
3. Prove the proxy has the same commit you tagged.
4. Run the CLI release only after that.

### `.github/workflows/release.yml`

Replace the old `publish` job with this file.

```yaml
name: release

on:
  push:
    tags: ["v*"]

permissions:
  contents: read

concurrency:
  group: release-${{ github.ref_name }}
  cancel-in-progress: false

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod

      - name: Validate tag, module path and branch
        env:
          TAG: ${{ github.ref_name }}
          SHA: ${{ github.sha }}
        run: |
          set -euo pipefail
          re='^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?$'
          [[ "$TAG" =~ $re ]] || { echo "::error::$TAG is not a valid semver tag"; exit 1; }
          major="${BASH_REMATCH[1]}"
          path="$(go list -m)"
          # Go requires a /vN suffix on the module path for N >= 2, and forbids it below.
          if [ "$major" -ge 2 ]; then
            [[ "$path" == */v"$major" ]] || { echo "::error::module path $path must end in /v$major"; exit 1; }
          else
            [[ ! "$path" =~ /v[0-9]+$ ]] || { echo "::error::module path $path must not carry a major suffix for $TAG"; exit 1; }
          fi
          # Releases come from main or a maintenance branch only.
          git branch -r --contains "$SHA" | grep -Eq 'origin/(main|release/v[0-9]+)$' \
            || { echo "::error::$TAG is not on main or release/v*"; exit 1; }
          # CHANGELOG must already describe this version.
          grep -Eq "^## \[?${TAG#v}\]?( |$)" CHANGELOG.md \
            || { echo "::error::CHANGELOG.md has no section for ${TAG#v}"; exit 1; }

      - name: Build and test
        run: |
          set -euo pipefail
          go mod verify
          go mod tidy
          git diff --exit-code go.mod go.sum
          go vet ./...
          go test -race ./...

      - uses: goreleaser/goreleaser-action@v6
        with:
          distribution: goreleaser
          version: "~> v2"
          args: check

  publish-module:
    needs: verify
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod

      - name: Warm proxy.golang.org and verify it serves this commit
        env:
          TAG: ${{ github.ref_name }}
          SHA: ${{ github.sha }}
        run: |
          set -euo pipefail
          mod="$(go list -m)"
          url="https://proxy.golang.org/${mod}/@v/${TAG}.info"
          # The proxy can 404 for a short while right after a tag push.
          ok=0
          for i in $(seq 1 12); do
            if curl -fsS "$url" -o /tmp/info.json; then ok=1; break; fi
            echo "attempt $i: not available yet, retrying in 30s"
            sleep 30
          done
          [ "$ok" = 1 ] || { echo "::error::proxy never served $mod@$TAG"; exit 1; }

          # Origin.Hash is the commit the proxy cached. It must be the tagged commit.
          got="$(jq -r '.Origin.Hash // empty' /tmp/info.json)"
          if [ -z "$got" ]; then
            echo "::warning::proxy response has no Origin.Hash; commit not verified"
          elif [ "$got" != "$SHA" ]; then
            echo "::error::proxy cached $got but tag points at $SHA"; exit 1
          fi

          # Resolve through proxy + checksum DB the way a customer would.
          tmp="$(mktemp -d)"
          cd "$tmp"
          go mod init example.invalid/probe
          GOPROXY=https://proxy.golang.org GOFLAGS=-mod=mod go get "${mod}@${TAG}"

  release-cli:
    # Chained after publish-module so the Homebrew formula never points at a
    # version the Go proxy doesn't serve.
    needs: publish-module
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - uses: goreleaser/goreleaser-action@v6
        with:
          distribution: goreleaser
          version: "~> v2"
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # Fine-grained PAT, contents:write on the tap repo only.
          # GITHUB_TOKEN can't push to another repository.
          HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

Pin the third-party actions by SHA before merging.

Add this to your PR workflow so config errors show up before a tag exists:

```yaml
      - uses: goreleaser/goreleaser-action@v6
        with:
          distribution: goreleaser
          version: "~> v2"
          args: release --snapshot --clean --skip=publish
```

### `.goreleaser.yaml`

```yaml
version: 2
project_name: kestrel

builds:
  - id: kestrel
    main: ./cmd/kestrel
    binary: kestrel
    env:
      - CGO_ENABLED=0
    goos: [linux, darwin, windows]
    goarch: [amd64, arm64]
    flags:
      - -trimpath
    mod_timestamp: "{{ .CommitTimestamp }}"
    ldflags:
      # Adjust the package path. Include /v2 once the module path changes.
      - -s -w
      - -X go.kestrel.dev/sdk/v2/internal/version.Version={{ .Version }}
      - -X go.kestrel.dev/sdk/v2/internal/version.Commit={{ .Commit }}
      - -X go.kestrel.dev/sdk/v2/internal/version.Date={{ .CommitDate }}

archives:
  - id: kestrel
    formats: [tar.gz]
    format_overrides:
      - goos: windows
        formats: [zip]
    name_template: "kestrel_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    files: [LICENSE*, README*]

checksum:
  name_template: checksums.txt

changelog:
  use: github
  filters:
    exclude: ["^docs:", "^test:", "^chore:"]

release:
  # Review the notes before they go public.
  draft: false
  prerelease: auto

brews:
  - name: kestrel
    repository:
      owner: kestrel
      name: homebrew-tap
      token: "{{ .Env.HOMEBREW_TAP_TOKEN }}"
    directory: Formula
    homepage: https://kestrel.dev
    description: Kestrel Compute CLI
    license: <SPDX id>
    commit_author:
      name: kestrel-release-bot
      email: <bot email>
    test: |
      system "#{bin}/kestrel", "version"
    install: |
      bin.install "kestrel"
```

**Homebrew notes**
- Create the `kestrel/homebrew-tap` repo first. Users then run `brew install kestrel/tap/kestrel`.
- GoReleaser 2.10+ marks `brews` (formulae) as deprecated in favor of `homebrew_casks`. Formulae still work and cover both macOS and Linux.
- If `goreleaser check` warns about this, `homebrew_casks` is the migration target. Casks are macOS-only, so macOS binaries need signing and notarization or a quarantine-removal hook. I haven't verified current Linux cask support.
- Adjust `ldflags` to match how your CLI exposes its version. The `kestrel version` test needs it.

**Coupling to know about:** one tag now releases both the SDK and the CLI. An SDK-only v2.1.0 also ships a CLI binary. That is fine for one repo and one version line. If you want independent versions later, split the CLI into its own module.

## 4. v2.0.0 (breaking change)

Go treats v2 as a different module. Skipping these steps makes `go get …@v2.0.0` fail with `+incompatible` or "module path must match".

1. **Create the maintenance branch first.** Run `git branch release/v1 <last v1 commit>` and push it. v1.x patches are tagged from there, and the workflow above already allows it.
2. **Change the module path on `main`:**
   ```bash
   go mod edit -module go.kestrel.dev/sdk/v2
   # **rewrites every import in place**
   grep -rl 'go.kestrel.dev/sdk' --include='*.go' . \
     | xargs sed -i '' -E 's#go\.kestrel\.dev/sdk(/|")#go.kestrel.dev/sdk/v2\1#g'
   gofmt -l . ; go mod tidy ; go build ./... && go test ./...
   ```
   On Linux, use `sed -i` without `''`. Review `git diff` afterward. The sed also hits strings in docs and examples, and it must skip a path that already ends in `/v2`.
3. **Fix every literal path.** That means README and doc import snippets, the `ldflags` paths above, `go install go.kestrel.dev/sdk/v2/cmd/kestrel@latest`, and examples.
4. **Check your vanity-import server.** `go.kestrel.dev/sdk/v2` must return the same `<meta name="go-import">` as `go.kestrel.dev/sdk`, pointing at the same repo. Test it with `curl 'https://go.kestrel.dev/sdk/v2?go-get=1'`.
5. **Write the migration guide** before the tag: what breaks, in order of blast radius, with before/after code and a deprecation timeline for v1.
6. **Dry-run with a release candidate.** Tag `v2.0.0-rc.1` and let the workflow run end to end. Remember that rc tags are immutable too. If the rc is wrong, burn it and tag `rc.2`.
7. **Tag v2.0.0.** Ship it with `git tag -a v2.0.0 -m "v2.0.0"` and `git push origin v2.0.0` (**publishes the release**). Check afterward that `go get go.kestrel.dev/sdk/v2@v2.0.0` works from a clean module and `brew install kestrel/tap/kestrel` gives 2.0.0.

## Rule going forward

Never move or delete a pushed tag. If a release is wrong, ship the next patch version. If a published version is harmful, add `retract v1.6.0 // reason` to `go.mod` and release a higher version containing it.

I answered from Go and GoReleaser knowledge and did not run any of this against your repo, so none of it is tested. Run `goreleaser check` and a snapshot build before trusting the config.