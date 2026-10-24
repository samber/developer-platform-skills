Ship three things: the npm package, the `.goreleaser.yaml` sections, and the Homebrew formula. Estimate: about 45 minutes to wire up and test with a `v0.0.1-rc.1` tag.

I assumed the code is in `github.com/oakridge/oak`, the entrypoint is `./cmd/oak`, and `main.version` exists. Change any that are wrong.

## 1. `.goreleaser.yaml`

```yaml
version: 2
project_name: oak

before:
  hooks:
    - go mod tidy

builds:
  - id: oak
    main: ./cmd/oak
    binary: oak
    env:
      - CGO_ENABLED=0
    flags:
      - -trimpath
    ldflags:
      - -s -w -X main.version={{.Version}} -X main.commit={{.Commit}} -X main.date={{.Date}}
    goos: [linux, darwin, windows]
    goarch: [amd64, arm64]

archives:
  - id: oak
    formats: [tar.gz]
    format_overrides:
      - goos: windows
        formats: [zip]
    # The npm postinstall builds this exact name. Change both together.
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    files:
      - LICENSE
      - README.md

# The npm postinstall verifies downloads against this file.
checksum:
  name_template: checksums.txt
  algorithm: sha256

release:
  github:
    owner: oakridge
    name: oak

brews:
  - name: oak
    repository:
      owner: oakridge
      name: homebrew-tap
      token: "{{ .Env.HOMEBREW_TAP_TOKEN }}"
    directory: Formula
    homepage: https://github.com/oakridge/oak
    description: Oakridge Telemetry CLI
    license: Apache-2.0
    install: |
      bin.install "oak"
    test: |
      assert_match version.to_s, shell_output("#{bin}/oak --version")
```

- **`brews` deprecation:** Recent GoReleaser versions flag `brews` as deprecated in favor of `homebrew_casks`. It still works. Run `goreleaser check` and follow its warning when you upgrade.
- **Tap repo:** Create the empty repo `oakridge/homebrew-tap` first.
- **Token:** `HOMEBREW_TAP_TOKEN` is a fine-grained PAT with contents write on the tap repo.

## 2. Homebrew

**`brew install oak` will not work from a tap.** A tap gives `brew install oakridge/tap/oak`, or `brew tap oakridge/tap && brew install oak`.

The bare name needs a homebrew-core PR. Core requires a source build and a notable project. The bar is roughly 75+ stars, 30+ forks or watchers, and a project older than 30 days. It also needs a stable tagged release.

The GoReleaser `brews` section above generates a tap formula that installs prebuilt binaries. For core, submit this source-build formula instead. It also works in the tap if you prefer building from source:

```ruby
class Oak < Formula
  desc "Oakridge Telemetry CLI"
  homepage "https://github.com/oakridge/oak"
  url "https://github.com/oakridge/oak/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_SHA256_OF_TARBALL"
  license "Apache-2.0"
  head "https://github.com/oakridge/oak.git", branch: "main"

  depends_on "go" => :build

  def install
    ldflags = "-s -w -X main.version=#{version}"
    system "go", "build", *std_go_args(ldflags:, output: bin/"oak"), "./cmd/oak"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/oak --version")
  end
end
```

Get the sha with `curl -sL <url> | shasum -a 256`.

## 3. npm package `@oakridge/cli`

Layout:

```
npm/
  package.json
  install.js
  bin/oak.js
```

**Deviation from your plan:** the postinstall does not link into `node_modules/.bin`. npm does that itself from the `bin` field, and a `bin` target that does not exist at link time causes errors. So `bin` points to a small JS shim, and the postinstall downloads the real binary into `vendor/`. The shim runs it. This also works on Windows, where `.bin` entries are `.cmd` wrappers.

`package.json`:

```json
{
  "name": "@oakridge/cli",
  "version": "0.0.0",
  "description": "Oakridge Telemetry CLI",
  "license": "Apache-2.0",
  "repository": "github:oakridge/oak",
  "bin": { "oak": "bin/oak.js" },
  "scripts": { "postinstall": "node install.js" },
  "files": ["bin/oak.js", "install.js"],
  "engines": { "node": ">=18" },
  "os": ["darwin", "linux", "win32"],
  "cpu": ["x64", "arm64"],
  "publishConfig": { "access": "public", "provenance": true }
}
```

The version stays `0.0.0` in git. CI sets it from the tag (step 4).

`install.js`:

```js
#!/usr/bin/env node
"use strict";

const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { version } = require("./package.json");

// Release tag is "v<package version>". CI keeps the two equal.
const REPO = process.env.OAK_RELEASE_REPO || "oakridge/oak";
const OS_MAP = { darwin: "darwin", linux: "linux", win32: "windows" };
const ARCH_MAP = { x64: "amd64", arm64: "arm64" };

async function download(url) {
  const res = await fetch(url, { redirect: "follow" });
  if (!res.ok) throw new Error(`GET ${url} failed: HTTP ${res.status}`);
  return Buffer.from(await res.arrayBuffer());
}

async function main() {
  if (process.env.OAK_SKIP_DOWNLOAD) {
    console.log("OAK_SKIP_DOWNLOAD set, skipping binary download.");
    return;
  }

  const goos = OS_MAP[process.platform];
  const goarch = ARCH_MAP[process.arch];
  if (!goos || !goarch) {
    throw new Error(`Unsupported platform ${process.platform}/${process.arch}`);
  }

  const ext = goos === "windows" ? "zip" : "tar.gz";
  const exe = goos === "windows" ? "oak.exe" : "oak";
  const asset = `oak_${version}_${goos}_${goarch}.${ext}`;
  const base = `https://github.com/${REPO}/releases/download/v${version}`;

  const archive = await download(`${base}/${asset}`);

  // Verify before extracting: refuse any archive not listed in checksums.txt.
  const sums = (await download(`${base}/checksums.txt`)).toString("utf8");
  const line = sums.split("\n").find((l) => l.trim().endsWith(` ${asset}`));
  if (!line) throw new Error(`${asset} not listed in checksums.txt`);
  const expected = line.trim().split(/\s+/)[0].toLowerCase();
  const actual = crypto.createHash("sha256").update(archive).digest("hex");
  if (actual !== expected) {
    throw new Error(`Checksum mismatch for ${asset}: expected ${expected}, got ${actual}`);
  }

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "oak-"));
  try {
    const archivePath = path.join(tmp, asset);
    fs.writeFileSync(archivePath, archive);
    // tar ships with macOS, Linux and Windows 10+ (bsdtar reads zip).
    execFileSync("tar", ["-xf", archivePath, "-C", tmp], { stdio: "inherit" });

    const vendor = path.join(__dirname, "vendor");
    fs.mkdirSync(vendor, { recursive: true });
    const dest = path.join(vendor, exe);
    fs.copyFileSync(path.join(tmp, exe), dest);
    fs.chmodSync(dest, 0o755);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
  console.log(`oak ${version} installed (${goos}/${goarch}).`);
}

main().catch((err) => {
  console.error(`@oakridge/cli postinstall failed: ${err.message}`);
  process.exit(1);
});
```

`bin/oak.js`:

```js
#!/usr/bin/env node
"use strict";

const { spawnSync } = require("node:child_process");
const path = require("node:path");

const exe = process.platform === "win32" ? "oak.exe" : "oak";
const binary = path.join(__dirname, "..", "vendor", exe);

const result = spawnSync(binary, process.argv.slice(2), { stdio: "inherit" });

if (result.error) {
  if (result.error.code === "ENOENT") {
    console.error(
      "oak binary missing. The postinstall script did not run (--ignore-scripts?). " +
        "Run: npm rebuild @oakridge/cli"
    );
  } else {
    console.error(result.error.message);
  }
  process.exit(1);
}
process.exit(result.status ?? 1);
```

## 4. CI: publish npm after GoReleaser

Order matters: the npm package must not appear before its release assets exist.

```yaml
# .github/workflows/release.yml
name: release
on:
  push:
    tags: ["v*"]

permissions:
  contents: write
  id-token: write # npm provenance

jobs:
  goreleaser:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-go@v5
        with: { go-version-file: go.mod }
      - uses: goreleaser/goreleaser-action@v6
        with:
          version: "~> v2"
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}

  npm:
    needs: goreleaser
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          registry-url: https://registry.npmjs.org
      - name: Set version from tag
        working-directory: npm
        run: npm version "${GITHUB_REF_NAME#v}" --no-git-tag-version
      - name: Publish
        working-directory: npm
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

A prerelease tag such as `v0.0.1-rc.1` publishes to npm's `latest` tag unless you add `--tag next` for prereleases.

## 5. Weak points of the postinstall design

1. **`--ignore-scripts`:** Many corporate and CI setups, and pnpm 10+ by default, skip postinstall scripts. Users get the "binary missing" message from the shim. They need `npm rebuild @oakridge/cli`, or pnpm's `onlyBuiltDependencies`.
2. **Proxies and air-gapped networks:** Node's `fetch` ignores `HTTPS_PROXY` unless you run Node 24+ with `NODE_USE_ENV_PROXY=1`. Offline installs from an npm mirror fail, because the binary is not in the tarball.
3. **Private or rate-limited GitHub:** The download breaks if release assets ever move or the repo goes private.

**The sturdier alternative is the esbuild/Biome pattern.** Publish `@oakridge/cli-darwin-arm64`, `-darwin-x64`, `-linux-x64`, `-linux-arm64` and `-win32-x64`, each carrying the binary with `os` and `cpu` fields. The main package lists them as `optionalDependencies`, and npm installs only the matching one. There is no network call in a script, and it works with `--ignore-scripts`, proxies and mirrors. The cost is publishing 5+ packages per release, which a CI loop handles.

I'd start with your postinstall plan for speed. Move to per-platform packages if the first enterprise customer hits point 1 or 2.

## Next step

1. Create `oakridge/homebrew-tap` and add the `HOMEBREW_TAP_TOKEN` and `NPM_TOKEN` secrets.
2. Run `goreleaser release --snapshot --clean` locally. Confirm the archive names match `oak_<version>_<os>_<arch>`.

I did not run any of this. Test the full path with a `v0.0.1-rc.1` tag before announcing.