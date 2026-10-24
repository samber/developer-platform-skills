## Decision needed first: the "no exceptions" rule blocks trusted publishing

Trusted publishing needs the publish job to mint a GitHub OIDC token and exchange it with the registry. As far as I know, **npm only supports this from GitHub-hosted runners**, and PyPI gives no support guarantee for self-hosted ones. I couldn't fetch the vendor docs in this session (web access was denied), so this comes from memory. Check both docs pages before you take it to Security.

You have three options:

1. **Recommended: ask Security for a narrow exception covering the publish jobs only.**
   - Everything else, including all compiling and wheel building, stays on self-hosted runners.
   - The publish jobs have no checkout and no secrets. They only download artifacts built earlier and hand them to the registry.
   - They run in a protected environment with required reviewers.
   - Security gets a smaller attack surface than the shared release VM, which holds long-lived tokens.
2. Keep self-hosted for everything and use short-lived registry tokens instead. This is not trusted publishing, so it fails your stated goal.
3. Wait for registry support on self-hosted runners. I can't promise a date.

The workflow below implements option 1. The publish runner is an input, so if support lands later you change one default.

## Reusable workflow: `.github/workflows/publish.yml`

This lives in a central repo, for example `veldtstream/.github-workflows`. Action SHAs are placeholders (`<sha>`). Pin them to full commit SHAs before merging.

```yaml
name: publish

on:
  workflow_call:
    inputs:
      npm-package-dir:
        description: Directory of the npm package; empty to skip npm
        type: string
        default: ""
      pypi:
        description: Build and publish the PyPI package with cibuildwheel
        type: boolean
        default: false
      runner-linux:
        description: JSON array of self-hosted labels for Linux build jobs
        type: string
        required: true
      runner-macos:
        type: string
        required: true
      runner-windows:
        type: string
        required: true
      runner-publish:
        description: >-
          JSON array of labels for the publish jobs. Defaults to GitHub-hosted
          because registries issue trusted-publishing credentials only for
          those runners (approved security exception).
        type: string
        default: '["ubuntu-latest"]'

permissions: {}

jobs:
  build-npm:
    if: inputs.npm-package-dir != ''
    runs-on: ${{ fromJSON(inputs.runner-linux) }}
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<sha>
        with:
          persist-credentials: false
      - uses: actions/setup-node@<sha>
        with:
          node-version: "22"
      - run: npm ci
        working-directory: ${{ inputs.npm-package-dir }}
      - run: npm test --if-present
        working-directory: ${{ inputs.npm-package-dir }}
      - run: npm pack --pack-destination "$RUNNER_TEMP/npm-dist"
        working-directory: ${{ inputs.npm-package-dir }}
      - uses: actions/upload-artifact@<sha>
        with:
          name: npm-dist
          path: ${{ runner.temp }}/npm-dist/*.tgz
          if-no-files-found: error

  build-sdist:
    if: inputs.pypi
    runs-on: ${{ fromJSON(inputs.runner-linux) }}
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<sha>
        with:
          persist-credentials: false
      - run: pipx run build --sdist
      - uses: actions/upload-artifact@<sha>
        with:
          name: pypi-sdist
          path: dist/*.tar.gz
          if-no-files-found: error

  build-wheels:
    if: inputs.pypi
    strategy:
      fail-fast: true
      matrix:
        os: [linux, macos, windows]
    runs-on: ${{ fromJSON(matrix.os == 'linux' && inputs.runner-linux || matrix.os == 'macos' && inputs.runner-macos || inputs.runner-windows) }}
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<sha>
        with:
          persist-credentials: false
      - uses: pypa/cibuildwheel@<sha>
      - uses: actions/upload-artifact@<sha>
        with:
          name: pypi-wheels-${{ matrix.os }}
          path: wheelhouse/*.whl
          if-no-files-found: error

  publish-npm:
    needs: build-npm
    runs-on: ${{ fromJSON(inputs.runner-publish) }}
    environment: release
    permissions:
      id-token: write # OIDC exchange with npm; nothing else
    steps:
      - uses: actions/setup-node@<sha>
        with:
          node-version: "22"
      - run: npm install -g npm@^11.5.1 # trusted publishing needs npm >= 11.5.1
      - uses: actions/download-artifact@<sha>
        with:
          name: npm-dist
          path: dist
      - name: Publish
        env:
          # The repo is private, so npm cannot attach provenance.
          NPM_CONFIG_PROVENANCE: "false"
        run: npm publish ./dist/*.tgz --access public

  publish-pypi:
    needs: [build-sdist, build-wheels]
    runs-on: ${{ fromJSON(inputs.runner-publish) }}
    environment: release
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@<sha>
        with:
          pattern: pypi-*
          path: dist
          merge-multiple: true
      - uses: pypa/gh-action-pypi-publish@<sha>
        with:
          packages-dir: dist
          attestations: false # private repo: no public Sigstore attestation
```

## Caller, in each repo: `.github/workflows/release.yml`

```yaml
name: release
on:
  push:
    tags: ["v*"]

permissions: {}

jobs:
  publish:
    uses: veldtstream/.github-workflows/.github/workflows/publish.yml@<sha-or-v1-tag>
    permissions:
      contents: read
      id-token: write # a reusable workflow cannot exceed the caller's permissions
    with:
      npm-package-dir: packages/sdk   # or omit; set `pypi: true` in the C-extension repo
      runner-linux: '["self-hosted","linux","x64"]'
      runner-macos: '["self-hosted","macos","arm64"]'
      runner-windows: '["self-hosted","windows","x64"]'
```

## One-time setup

1. **Central repo access.** In the central repo, go to Settings → Actions → Access and allow repositories in the organization to use the workflow. Pin callers to a SHA or an immutable tag.
2. **`release` environment, in every calling repo.**
   - Add required reviewers.
   - Restrict deployment to `v*` tags.
   - Add a tag ruleset so only maintainers can create `v*` tags.
3. **npm.** In the `@veldtstream/sdk` package settings, add a Trusted Publisher: org, repo, workflow filename, environment `release`.
4. **PyPI.** In the `veldtstream` project settings, add a GitHub trusted publisher with the same four fields.
5. **Workflow filename.** Use the caller's file name, `release.yml`, not `publish.yml`.
   - I believe both registries validate the top-level calling workflow, not the reusable one.
   - Confirm this in each registry's docs. A mismatch shows up as a "no matching publisher" error on the first run.
6. **Cutover.**
   - Do a dry run with a prerelease tag, such as a `-rc.1` version on npm or a PyPI pre-release.
   - Then revoke the npm and PyPI tokens on the release VM and decommission it.
   - Optionally enable "Require trusted publishing" on the npm package.

## Gotchas

- **Wheels on self-hosted runners.**
  - Linux `manylinux` builds need Docker on the runner.
  - Windows and macOS runners need the C toolchains.
  - Use ephemeral runners so build state doesn't persist between jobs.
  - Mind the macOS architecture. For universal2 or x86_64 wheels, either set `CIBW_ARCHS_MACOS` or add an Intel runner to the matrix.
- **`pypa/gh-action-pypi-publish` is a Docker container action.** It needs Docker if you ever move the publish job to a self-hosted Linux runner.
- **No provenance or attestations while the repo is private.** The packages work fine without them. If you open-source the repos later, remove `NPM_CONFIG_PROVENANCE` and `attestations: false`.
- **One npm trusted publisher per package.** That is fine for one SDK per repo, but not for a shared multi-package release flow.
- **The publish jobs run no repo code.** There is no checkout and no install step beyond `npm`. Keep it that way, because those jobs are the only ones holding OIDC capability.

## Unverified claims to check

- npm trusted publishing doesn't work on self-hosted runners.
- PyPI offers no guarantee on self-hosted runners.
- Both registries match the caller's workflow filename.
- The npm CLI minimum is 11.5.1.

I have not run this workflow. Dry-run it with a prerelease tag before cutover.