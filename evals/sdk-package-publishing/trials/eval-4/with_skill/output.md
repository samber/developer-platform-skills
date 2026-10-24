# Publishing `oak` to npm and Homebrew

Nothing here was run, because I have no access to the `oak` repo or to npm. Treat every file as a draft until you've approved the plan and run the preflight commands.

## 0. Your plan changes

Don't download the binary in `postinstall`. The skill rejects it for these reasons:

- **npm 12 skips install scripts by default.** It has been GA since 2026-07-08. `npx @oakridge/cli` and `npm i -g` have no project policy to approve a script, so the download would silently never run. Users would see `oak: command not found`.
- **Corporate registry proxies break it.** JS customers behind Artifactory or Nexus can't reach github.com at install time.
- **The download has no integrity check.** Nothing verifies it unless you write that check yourself.

The replacement needs no script. It is one npm package per platform, each holding the binary, plus a tiny `@oakridge/cli` launcher that lists them all as `optionalDependencies`. npm installs only the one matching the machine. `node_modules/.bin/oak` points at the launcher, which executes the binary.

Homebrew has one catch. `brew install oak` with no qualifier only works after `brew tap oakridge/tap` or once homebrew-core accepts the formula (section 4). Out of the box, users run `brew install oakridge/tap/oak`, which taps automatically.

## 1. Assumptions and inventory

I couldn't interview you, so I assumed the following. Correct anything that's wrong.

- The repo is `github.com/oakridge/oak`, public, on GitHub Actions with hosted runners.
- The `main` package is at `./cmd/oak`, and the binary has a `--version` flag.
- It's a standing process, GoReleaser OSS (not Pro), and a static binary (`CGO_ENABLED=0`).
- The tag `vX.Y.Z` is the version source. There is no manifest.
- Targets are linux, darwin and windows on amd64 and arm64.
- There are no private packages, so the dependency-confusion probe doesn't apply. Claiming the `@oakridge` scope is the defense.
- You have paying customers and the binary runs on their machines, so the approval-gate rung applies.

| Artifact | Channel | Publish path | Credential | Owners | Target model |
|---|---|---|---|---|---|
| `oak_*` archives, `checksums.txt`, cosign bundle, SBOMs | GitHub release | GoReleaser in CI, protected tag | built-in `GITHUB_TOKEN` | repo admins | draft, then publish; immutable releases on |
| `@oakridge/cli` and 6 `@oakridge/cli-<os>-<cpu>` packages | npm | CI, staged publish | trusted publishing (OIDC), no token after bootstrap | 2 owners, WebAuthn 2FA | `release` environment gate and `npm stage approve` |
| `oakridge/homebrew-tap` formula | Homebrew tap | CI job, last | token scoped to the tap repo only | repo admins | `release` environment only |

## 2. Per-registry decisions

**npm**
- **Credential:** trusted publishing bound to the `release` environment, plus staged publishing. A compromised workflow can then stage but not reach `latest`. Keep "allow direct publish" and "allow dist-tag" off.
- **Namespace:** claim the `@oakridge` org before anything else. It's the cheapest defense against lookalike scopes.
- **Linux packages omit `libc`.** The binary is static, so one package serves both glibc and musl. Add `libc` only if you ever ship cgo.
- **Publish order:** platform packages first, `@oakridge/cli` last, so the launcher never points at missing versions. Approve the stages in the same order.
- **Dist-tag policy:** pre-releases go to `next`, `beta` or `rc`, and a backport never moves `latest` backwards. The build job derives this.
- **Provenance:** automatic from trusted publishing on GitHub Actions.
- **Preflight:** `npm pack --dry-run` runs inside `build.mjs`, followed by the install smoke test in the workflow.

**GitHub release and GoReleaser**
- **Draft first:** attach every asset to a draft, then publish with `gh release edit <tag> --draft=false`. Enable immutable releases. Channels update after the release is public.
- **One job:** GoReleaser OSS builds, signs and releases in a single job. The environment gate, no caches and pinned tools stand in for the job split.
- **Pin versions:** use the exact GoReleaser, cosign and syft versions. Resolve action SHAs with `git ls-remote`, or let Renovate do it. I did not invent any.

**Homebrew**
- **Prebuilt-binary formula:** it pins the release asset URL and SHA-256. Formulae are not quarantined by Gatekeeper, and Go's linker ad-hoc signs darwin/arm64, so notarization isn't needed for brew or npm installs. It matters only for browser downloads.
- **Not a GoReleaser `brews` or `homebrew_casks` section:** `brews` has been deprecated since v2.10, and a cask is macOS-only. The formula is rendered from `checksums.txt` by a script after the release is public. That keeps the tap from ever pointing at draft assets.

## 3. Files

### `.goreleaser.yaml`

```yaml
version: 2
project_name: oak

before:
  hooks:
    - go mod verify

builds:
  - id: oak
    main: ./cmd/oak                     # assumption: adjust
    binary: oak
    env: [CGO_ENABLED=0]                # static: one linux package serves glibc and musl
    goos: [linux, darwin, windows]
    goarch: [amd64, arm64]
    flags: [-trimpath]
    ldflags:
      - -s -w -X main.version={{ .Version }} -X main.commit={{ .Commit }}
    mod_timestamp: "{{ .CommitTimestamp }}"

archives:
  - id: oak
    ids: [oak]
    formats: [tar.gz]
    format_overrides:
      - goos: windows
        formats: [zip]
    # build.mjs and the Homebrew renderer depend on this exact name
    name_template: "oak_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    files: [LICENSE, README.md]         # build.mjs copies LICENSE into every npm package

checksum:
  name_template: checksums.txt
  algorithm: sha256

signs:
  - id: checksums
    cmd: cosign
    artifacts: checksum
    signature: "${artifact}.sigstore.json"
    args: [sign-blob, "--bundle=${signature}", "${artifact}", --yes]   # keyless via CI identity

sboms:
  - artifacts: archive                  # needs syft installed in a prior step

release:
  draft: true                           # published by a later step, after every asset is attached
  prerelease: auto

# Optional: Developer ID signing and notarization. Matters for browser downloads only;
# brew and npm installs are not quarantined. Needs a paid Apple Developer account.
notarize:
  macos:
    - enabled: '{{ isEnvSet "MACOS_SIGN_P12" }}'
      ids: [oak]
      sign:
        certificate: "{{ .Env.MACOS_SIGN_P12 }}"
        password: "{{ .Env.MACOS_SIGN_PASSWORD }}"
      notarize:
        issuer_id: "{{ .Env.MACOS_NOTARY_ISSUER_ID }}"
        key_id: "{{ .Env.MACOS_NOTARY_KEY_ID }}"
        key: "{{ .Env.MACOS_NOTARY_KEY }}"
        wait: true
```

Preflight: run `goreleaser check`, then `goreleaser release --snapshot --clean`.

### `.github/workflows/release.yml`

```yaml
name: release
on:
  push:
    tags: ["v*"]                        # same pattern in the tag ruleset and the environment rule
permissions: {}

jobs:
  goreleaser:
    runs-on: ubuntu-latest
    environment: release                # reviewers approve here; holds MACOS_* secrets if used
    permissions:
      contents: write                   # draft release
      id-token: write                   # keyless cosign and attestation
      attestations: write
    steps:
      - uses: actions/checkout@<sha>    # v6
        with: { fetch-depth: 0, persist-credentials: false }
      - uses: actions/setup-go@<sha>    # v6
        with: { go-version-file: go.mod, cache: false }
      - uses: sigstore/cosign-installer@<sha>
      - uses: anchore/sbom-action/download-syft@<sha>
      - uses: goreleaser/goreleaser-action@<sha>
        with:
          distribution: goreleaser
          version: <pinned v2.x.y>
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # MACOS_SIGN_P12 / MACOS_SIGN_PASSWORD / MACOS_NOTARY_* from the release environment, if used
      - uses: actions/attest@<sha>
        with:
          subject-checksums: dist/checksums.txt   # attests every archive; subject-path would attest one file
      - name: Publish the release (assets are now immutable)
        run: gh release edit "$GITHUB_REF_NAME" --repo "$GITHUB_REPOSITORY" --draft=false
        env: { GH_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
      - uses: actions/upload-artifact@<sha>
        with:
          name: dist
          path: |
            dist/checksums.txt
            dist/*.tar.gz
            dist/*.zip

  npm-build:                            # unprivileged: no id-token, no secrets
    needs: goreleaser
    runs-on: ubuntu-latest
    permissions: { contents: read }
    outputs:
      version: ${{ steps.ver.outputs.version }}
      dist_tag: ${{ steps.ver.outputs.dist_tag }}
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: actions/download-artifact@<sha>
        with: { name: dist, path: dist }
      - uses: actions/setup-node@<sha>
        with: { node-version: "24", package-manager-cache: false }
      - name: Verify archives against checksums.txt
        run: cd dist && sha256sum --check --ignore-missing checksums.txt
      - name: Derive version and dist-tag
        id: ver
        run: |
          version="${GITHUB_REF_NAME#v}"
          [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]] || { echo "bad tag $GITHUB_REF_NAME"; exit 1; }
          case "$version" in
            *-*) channel="${version#*-}"; channel="${channel%%.*}"
                 case "$channel" in alpha|beta|rc|next) ;; *) echo "unknown channel $channel"; exit 1 ;; esac ;;
            *)   # default to 0.0.0 only on a genuine not-found; any other error stops the release
                 if out="$(npm view @oakridge/cli dist-tags.latest 2>err.log)"; then current="$out"
                 elif grep -q E404 err.log; then current=0.0.0
                 else cat err.log; exit 1; fi
                 highest="$(printf '%s\n%s\n' "$current" "$version" | sort -V | tail -n1)"
                 if [ "$highest" = "$version" ]; then channel=latest
                 else channel="latest-${version%%.*}"; fi ;;   # backport: never move latest backwards
          esac
          echo "version=$version" >> "$GITHUB_OUTPUT"
          echo "dist_tag=$channel" >> "$GITHUB_OUTPUT"
      - name: Build npm packages
        run: node scripts/npm/build.mjs dist "${{ steps.ver.outputs.version }}" npm-out
      - name: Smoke test the linux-x64 install
        run: |
          smoke="$RUNNER_TEMP/smoke"; mkdir -p "$smoke"
          v="${{ steps.ver.outputs.version }}"
          npm install --prefix "$smoke" --ignore-scripts --no-audit --no-fund \
            "./npm-out/oakridge-cli-$v.tgz" "./npm-out/oakridge-cli-linux-x64-$v.tgz"
          "$smoke/node_modules/.bin/oak" --version
      - uses: actions/upload-artifact@<sha>
        with: { name: npm-out, path: npm-out }

  npm-publish:
    needs: npm-build
    if: vars.NPM_BOOTSTRAPPED == 'true' # unset until the first manual bootstrap (section 6)
    runs-on: ubuntu-latest
    environment: release                # must equal the environment in every trusted-publisher config
    permissions:
      contents: read
      id-token: write                   # OIDC, this job only
    env:
      VERSION: ${{ needs.npm-build.outputs.version }}
      DIST_TAG: ${{ needs.npm-build.outputs.dist_tag }}
    steps:
      - uses: actions/download-artifact@<sha>
        with: { name: npm-out, path: npm-out }
      - uses: actions/setup-node@<sha>
        with: { node-version: "24", registry-url: "https://registry.npmjs.org", package-manager-cache: false }
      - run: npm install -g npm@<pinned 11.15+ version>     # staged publishing needs 11.15.0+
      - name: Stage every package, platforms first, launcher last
        run: |
          set -euo pipefail
          jq -r '.[] | [.name, .file] | @tsv' npm-out/order.json | while IFS=$'\t' read -r name file; do
            if npm view "$name@$VERSION" version >/dev/null 2>err.log; then
              echo "skip $name@$VERSION: already on the registry"; continue
            fi
            grep -q E404 err.log || { cat err.log; exit 1; }
            npm stage publish "npm-out/$file" --access public --tag "$DIST_TAG"
          done

  homebrew:                             # last: the release is public and its assets are immutable
    needs: goreleaser
    if: ${{ !contains(github.ref_name, '-') }}     # no formula for pre-releases
    runs-on: ubuntu-latest
    environment: release                # holds TAP_GITHUB_TOKEN
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: actions/download-artifact@<sha>
        with: { name: dist, path: dist }
      - run: scripts/render-formula.sh "${GITHUB_REF_NAME#v}" dist/checksums.txt > "$RUNNER_TEMP/oak.rb"
      - uses: actions/checkout@<sha>
        with:
          repository: oakridge/homebrew-tap
          token: ${{ secrets.TAP_GITHUB_TOKEN }}   # scoped to the tap repository only
          path: tap
      - run: |
          set -euo pipefail
          mkdir -p tap/Formula && cp "$RUNNER_TEMP/oak.rb" tap/Formula/oak.rb
          cd tap
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add Formula/oak.rb
          git diff --cached --quiet && { echo "formula unchanged"; exit 0; }
          git commit -m "oak ${GITHUB_REF_NAME#v}"
          git push
```

### `scripts/npm/launcher/bin/oak.js`

The only code users execute from the npm package. No install script runs.

```js
#!/usr/bin/env node
// Runs the oak binary from the platform package npm installed for this machine.
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";

const key = `${process.platform}-${process.arch}`;
const exe = process.platform === "win32" ? "oak.exe" : "oak";

let binary;
try {
  binary = createRequire(import.meta.url).resolve(`@oakridge/cli-${key}/bin/${exe}`);
} catch {
  console.error(
    `oak: no binary package for ${key}.\n` +
      `Either this platform is unsupported, or optional dependencies were skipped ` +
      `(--omit=optional, npm_config_optional=false). Reinstall without that flag, ` +
      `or download a release from https://github.com/oakridge/oak/releases.`,
  );
  process.exit(1);
}

const result = spawnSync(binary, process.argv.slice(2), { stdio: "inherit" });
if (result.error) {
  console.error(`oak: cannot execute ${binary}: ${result.error.message}`);
  process.exit(1);
}
if (result.signal) process.kill(process.pid, result.signal);
process.exit(result.status ?? 1);
```

### `scripts/npm/build.mjs`

Builds from the verified GoReleaser archives and uses only the Node standard library. It fails closed on a missing archive or a missing file inside one.

```js
// Builds the oak npm packages from GoReleaser archives: one package per platform holding
// the binary, plus the @oakridge/cli launcher that depends on all of them at the exact same version.
// Usage: node build.mjs <dist-dir> <version> <out-dir>
import { spawnSync } from "node:child_process";
import { chmodSync, copyFileSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SCOPE = "@oakridge";
const MAIN_NAME = `${SCOPE}/cli`;
const REPO_URL = "git+https://github.com/oakridge/oak.git";
const LICENSE_ID = "<SPDX-LICENSE>"; // placeholder: must equal the repo's LICENSE
// GoReleaser GOOS/GOARCH -> Node process.platform/process.arch.
const TARGETS = [
  { goos: "linux", goarch: "amd64", os: "linux", cpu: "x64" },
  { goos: "linux", goarch: "arm64", os: "linux", cpu: "arm64" },
  { goos: "darwin", goarch: "amd64", os: "darwin", cpu: "x64" },
  { goos: "darwin", goarch: "arm64", os: "darwin", cpu: "arm64" },
  { goos: "windows", goarch: "amd64", os: "win32", cpu: "x64" },
  { goos: "windows", goarch: "arm64", os: "win32", cpu: "arm64" },
];

const [distArg, version, outArg] = process.argv.slice(2);
if (!distArg || !version || !outArg) {
  console.error("usage: node build.mjs <dist-dir> <version> <out-dir>");
  process.exit(2);
}
const distDir = resolve(distArg);
const outDir = resolve(outArg);
const launcherDir = join(dirname(fileURLToPath(import.meta.url)), "launcher");

function run(cmd, args, cwd) {
  const r = spawnSync(cmd, args, { cwd, encoding: "utf8" });
  if (r.status !== 0) throw new Error(`${cmd} ${args.join(" ")} failed:\n${r.stderr}`);
  return r.stdout;
}

function pack(dir) {
  const out = run("npm", ["pack", "--json", "--ignore-scripts", "--pack-destination", outDir], dir);
  return JSON.parse(out)[0].filename;
}

function writeJson(path, value) {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

const common = {
  version,
  license: LICENSE_ID,
  repository: { type: "git", url: REPO_URL },
  homepage: "https://github.com/oakridge/oak",
  publishConfig: { access: "public" },
};

mkdirSync(outDir, { recursive: true });
const staging = mkdtempSync(join(tmpdir(), "oak-npm-"));
const order = [];
const optionalDependencies = {};
let licensePath;

for (const t of TARGETS) {
  const key = `${t.os}-${t.cpu}`;
  const name = `${SCOPE}/cli-${key}`;
  const isWindows = t.goos === "windows";
  const exe = isWindows ? "oak.exe" : "oak";
  const archive = join(distDir, `oak_${version}_${t.goos}_${t.goarch}.${isWindows ? "zip" : "tar.gz"}`);

  const extractDir = join(staging, `extract-${key}`);
  mkdirSync(extractDir);
  if (isWindows) run("unzip", ["-q", archive, "-d", extractDir]);
  else run("tar", ["-xzf", archive, "-C", extractDir]);

  const pkgDir = join(staging, `pkg-${key}`);
  mkdirSync(join(pkgDir, "bin"), { recursive: true });
  const binaryPath = join(pkgDir, "bin", exe);
  copyFileSync(join(extractDir, exe), binaryPath);
  chmodSync(binaryPath, 0o755); // the launcher executes it directly
  licensePath = join(extractDir, "LICENSE");
  copyFileSync(licensePath, join(pkgDir, "LICENSE"));

  writeJson(join(pkgDir, "package.json"), {
    name,
    ...common,
    description: `oak CLI binary for ${key}`,
    os: [t.os],
    cpu: [t.cpu],
    files: ["bin/"],
  });

  optionalDependencies[name] = version; // exact version, never a range
  order.push({ name, file: pack(pkgDir) });
}

const mainDir = join(staging, "pkg-main");
mkdirSync(join(mainDir, "bin"), { recursive: true });
copyFileSync(join(launcherDir, "bin", "oak.js"), join(mainDir, "bin", "oak.js"));
copyFileSync(licensePath, join(mainDir, "LICENSE"));
writeFileSync(
  join(mainDir, "README.md"),
  "# @oakridge/cli\n\nnpm distribution of the `oak` CLI. Docs: https://github.com/oakridge/oak\n",
);
writeJson(join(mainDir, "package.json"), {
  name: MAIN_NAME,
  ...common,
  description: "oak CLI",
  type: "module",
  bin: { oak: "bin/oak.js" },
  files: ["bin/oak.js"],
  engines: { node: ">=18" },
  optionalDependencies,
});
order.push({ name: MAIN_NAME, file: pack(mainDir) }); // launcher last

writeJson(join(outDir, "order.json"), order);
console.log(order.map((o) => `${o.name} -> ${o.file}`).join("\n"));
```

Local preflight: `goreleaser release --snapshot --clean`, then `node scripts/npm/build.mjs dist <snapshot-version> /tmp/npm-out`. Snapshot archives carry the snapshot version in their names, so pass that version, not `1.4.2`.

### `scripts/render-formula.sh`

Prints the tap formula. It fails if any checksum is missing.

```sh
#!/usr/bin/env bash
# Usage: render-formula.sh <version> <checksums.txt>   (prints Formula/oak.rb to stdout)
set -euo pipefail
version="$1"; sums="$2"
base="https://github.com/oakridge/oak/releases/download/v${version}"

sha() { # $1 = os_arch
  local f="oak_${version}_$1.tar.gz" s
  s="$(awk -v f="$f" '$2 == f { print $1 }' "$sums")"
  [ -n "$s" ] || { echo "no checksum for $f" >&2; exit 1; }
  printf '%s' "$s"
}

cat <<EOF
class Oak < Formula
  desc "Oakridge Telemetry CLI"
  homepage "https://github.com/oakridge/oak"
  version "${version}"
  license "<SPDX-LICENSE>"

  on_macos do
    on_arm do
      url "${base}/oak_${version}_darwin_arm64.tar.gz"
      sha256 "$(sha darwin_arm64)"
    end
    on_intel do
      url "${base}/oak_${version}_darwin_amd64.tar.gz"
      sha256 "$(sha darwin_amd64)"
    end
  end

  on_linux do
    on_arm do
      url "${base}/oak_${version}_linux_arm64.tar.gz"
      sha256 "$(sha linux_arm64)"
    end
    on_intel do
      url "${base}/oak_${version}_linux_amd64.tar.gz"
      sha256 "$(sha linux_amd64)"
    end
  end

  def install
    bin.install "oak"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/oak --version")
  end
end
EOF
```

Replace `<SPDX-LICENSE>` in both the script and `build.mjs`. `brew audit` fails until you do.

## 4. Homebrew formula

### Tap formula

This is what the script renders into `oakridge/homebrew-tap/Formula/oak.rb`, shown here for one version. Users run `brew install oakridge/tap/oak`, or `brew tap oakridge/tap` once and then `brew install oak`.

```ruby
class Oak < Formula
  desc "Oakridge Telemetry CLI"
  homepage "https://github.com/oakridge/oak"
  version "1.4.2"
  license "<SPDX-LICENSE>"

  on_macos do
    on_arm do
      url "https://github.com/oakridge/oak/releases/download/v1.4.2/oak_1.4.2_darwin_arm64.tar.gz"
      sha256 "<from checksums.txt>"
    end
    on_intel do
      url "https://github.com/oakridge/oak/releases/download/v1.4.2/oak_1.4.2_darwin_amd64.tar.gz"
      sha256 "<from checksums.txt>"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/oakridge/oak/releases/download/v1.4.2/oak_1.4.2_linux_arm64.tar.gz"
      sha256 "<from checksums.txt>"
    end
    on_intel do
      url "https://github.com/oakridge/oak/releases/download/v1.4.2/oak_1.4.2_linux_amd64.tar.gz"
      sha256 "<from checksums.txt>"
    end
  end

  def install
    bin.install "oak"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/oak --version")
  end
end
```

### homebrew-core variant (what makes plain `brew install oak` work)

homebrew-core builds from source, so it does not accept prebuilt-binary formulae. Submit this variant when `oak` meets Homebrew's notability bar. For self-submitted projects that is roughly 75 stars, 30 forks and 30 watchers. Check the current "Acceptable Formulae" page. Also run `brew search oak` first for a name clash.

```ruby
class Oak < Formula
  desc "Oakridge Telemetry CLI"
  homepage "https://github.com/oakridge/oak"
  url "https://github.com/oakridge/oak/archive/refs/tags/v1.4.2.tar.gz"
  sha256 "<sha256 of that source tarball>"
  license "<SPDX-LICENSE>"
  head "https://github.com/oakridge/oak.git", branch: "main"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args(ldflags: "-s -w -X main.version=#{version}"), "./cmd/oak"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/oak --version")
  end
end
```

Preflight (user runs): `brew audit --strict --online oakridge/tap/oak`, then `brew install --build-from-source` and `brew test oakridge/tap/oak` on a Mac.

## 5. Rollback runbook

Commands are for you to run. Nothing here is a dry run, and each one is public.

**npm.** Rehearse on a scratch scoped package first, never on `@oakridge/cli`.
1. Roll forward: tag the fix, for example `v1.4.4`. CI stages it, and you approve.
2. If `latest` points at the bad version, move it back: `npm dist-tag add @oakridge/cli@<last-good> latest`. Move it only if it points at the bad one.
3. Deprecate the bad version, naming the fix. Do the launcher first, because it pins the platform versions: `npm deprecate "@oakridge/cli@1.4.3" "Broken <thing>; use 1.4.4"`. Repeat for each `@oakridge/cli-<os>-<cpu>@1.4.3`.
4. Unpublish only for leaked secrets or malware, within 72 hours and with no public dependents. Otherwise contact npm security.
5. If compromise is suspected, isolate runners first. Then revoke and rotate everything the `release` job could reach: the tap token, the Apple keys and the trusted-publisher configs.

**GitHub release.** Never replace assets, since checksums and formulae pin the original bytes. Ship a new tag and note the bad version in the release body.

**Homebrew.** Roll forward by tagging the fix. The `homebrew` job re-renders the formula. Reverting the tap commit only helps users who haven't installed yet, because installed users see no downgrade.

**Announce** in the changelog and the security advisory channel.

## 6. Migration sequence

1. **Day 0, human setup:**
   - Create the `@oakridge` npm org, with two owners on WebAuthn 2FA.
   - Add a tag ruleset for `v*` limited to release managers.
   - Create the `release` environment: a team as reviewer, self-review blocked, deployments restricted to `v*` tags.
   - Create `oakridge/homebrew-tap`, plus a token scoped to that repo only, stored in the `release` environment.
   - Enable immutable releases.
   - Evidence: screenshots or settings exports.
2. **Day 0–1:**
   - Merge the files above, with action SHAs resolved.
   - Run `goreleaser check`, a snapshot release and `build.mjs`.
   - Rehearse the npm steps on a scratch scope.
3. **Tag the first release (`v1.x.0`).** `goreleaser`, `npm-build` and `homebrew` run. `npm-publish` is skipped, because `NPM_BOOTSTRAPPED` is unset. Evidence: the workflow run, the cosign bundle, and `gh attestation verify` on one archive.
4. **Bootstrap npm.** OIDC can't create a package.
   - Download the `npm-out` artifact. Run `npm login` locally and `npm stage publish <tgz> --access public --tag latest` for each file in `order.json` order.
   - Approve each stage with `npm stage approve`.
   - Add a trusted publisher to each of the 7 packages: owner `oakridge`, repo `oak`, workflow `release.yml`, environment `release`. Use the package settings page, or `npm trust` (check `npm trust --help` for its flags).
5. **Within 48 hours of step 4,** set repo variable `NPM_BOOTSTRAPPED=true` and tag a patch release. A configuration not validated by a publish in 48 hours expires. Approve the stages. Evidence: the provenance badge, and `npm audit signatures` on a fresh install.
6. **Lock down.** Set each package to "Require two-factor authentication and disallow tokens", then run `npm logout` and revoke any granular token used in step 4.
7. **Document the install paths:**
   - `npm install -g @oakridge/cli` or `npx @oakridge/cli`
   - `brew install oakridge/tap/oak`
   - `gh attestation verify <archive> --repo oakridge/oak`
   - Optionally add a verified `curl | sh` installer for Linux users who have neither.

## Gates to confirm

- **Tag equals version:** the dist-tag step enforces the semver shape of the tag. There's no manifest to compare it against.
- **Zero long-lived publish tokens:** true after step 6.
- **All publishes from CI on a protected tag:** true after step 5.
- **Rollback rehearsed:** still open until you run the scratch-scope rehearsal.

## Open items for you

- The package path `./cmd/oak`, the repo `oakridge/oak`, the `--version` flag and the SPDX license are assumed.
- Do you want Windows binaries on npm? I included win32 x64 and arm64. Drop those entries from `TARGETS` and the GoReleaser `goos` list if not.
- Do you accept seven stage approvals per release? If not, I'd drop staged publish and use direct OIDC publish behind the environment gate. That is a weaker gate.