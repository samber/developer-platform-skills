# Release workflow for `@keelharbor/sdk`

I'd skip the stored `NPM_TOKEN` and use npm trusted publishing (OIDC). The workflow below does that and has no secret in it. A token fallback is at the end.

## Why not the 2024 token

- **It may already be dead.** As I understand npm's late-2025 changes, classic tokens, including the old "automation" type, were revoked, and new write tokens are short-lived. Check the token's status on npmjs.com before building around it.
- **It would bypass 2FA.** A long-lived write-capable token sitting in repo secrets is a high-value target, and two paid enterprise customers build on this package.
- **OIDC has no standing credential.** GitHub mints a short-lived identity token per run, and npm accepts it only from the repo, workflow file and environment you register. It also attaches provenance, which the enterprise customers can verify.

## `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+*"

# Deny everything by default; the publish job opts in below.
permissions:
  contents: read

concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false

jobs:
  verify:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.meta.outputs.version }}
      dist_tag: ${{ steps.meta.outputs.dist_tag }}
    steps:
      # Pin third-party actions to full commit SHAs once you have chosen versions.
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - name: Tag must point at a commit on main
        run: |
          git fetch origin main
          git merge-base --is-ancestor "$GITHUB_SHA" origin/main \
            || { echo "::error::Tag ${GITHUB_REF_NAME} is not on main"; exit 1; }

      - name: Tag must match package.json version
        id: meta
        run: |
          pkg_version="$(node -p "require('./package.json').version")"
          tag_version="${GITHUB_REF_NAME#v}"
          if [ "$pkg_version" != "$tag_version" ]; then
            echo "::error::Tag $GITHUB_REF_NAME does not match package.json version $pkg_version"
            exit 1
          fi
          # Prereleases (1.2.0-rc.1) go to "next" so they never become "latest".
          if [[ "$pkg_version" == *-* ]]; then dist_tag=next; else dist_tag=latest; fi
          echo "version=$pkg_version" >> "$GITHUB_OUTPUT"
          echo "dist_tag=$dist_tag" >> "$GITHUB_OUTPUT"

      - run: npm ci
      - run: npm run build --if-present
      - run: npm test --if-present

  publish:
    needs: verify
    runs-on: ubuntu-latest
    # Environment with required reviewers = a human approves every publish.
    environment: npm-publish
    permissions:
      contents: read
      id-token: write # required for npm trusted publishing (OIDC) and provenance
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          registry-url: https://registry.npmjs.org
          cache: npm

      # Trusted publishing needs npm >= 11.5.1.
      - run: npm install -g npm@latest
      - run: npm ci
      - run: npm run build --if-present

      - name: Publish
        run: npm publish --access public --provenance --tag "${{ needs.verify.outputs.dist_tag }}"
```

`verify` runs tests with no publish rights. `publish` is a separate job, so only it gets `id-token: write` and the environment gate. The workflow doesn't set `NODE_AUTH_TOKEN`, so no token is involved.

## One-time setup

1. **npmjs.com** → `@keelharbor/sdk` → Settings → Trusted Publisher → GitHub Actions. Enter the org/repo, workflow filename `release.yml`, and environment `npm-publish`.
2. **GitHub** → Settings → Environments → create `npm-publish`. Add required reviewers, and restrict deployment to tags matching `v*`.
3. **GitHub** → Settings → Rules → add a tag ruleset for `v*` so only maintainers can create or delete release tags. Anyone who can push a tag can otherwise trigger a release attempt.
4. **npm** → after the first successful OIDC publish, set the package's publishing access to "Require 2FA and disallow tokens", then revoke the 2024 token and remove it from 1Password.
5. Confirm `package.json` has `repository.url` matching the GitHub repo exactly. Provenance fails otherwise.

## Release procedure

```bash
npm version minor        # bumps package.json, commits, creates tag vX.Y.Z
git push origin main --follow-tags
```

Approve the `npm-publish` deployment when GitHub prompts. A mismatched tag or version fails the run before anything ships.

## Assumptions to check

- Your repo uses npm with a `package-lock.json`. For pnpm or yarn, change the install and cache steps.
- `build` and `test` scripts exist. `--if-present` skips them silently if they don't, so remove it once you've confirmed they do.
- Trusted publishing requires GitHub-hosted runners, which you have.

## If you must use a token

Only do this if OIDC is blocked. Create a granular token scoped to `@keelharbor/sdk` with publish-only rights and the shortest expiry npm allows. Store it as an `NPM_TOKEN` secret on the `npm-publish` environment, not at repo level. In the `publish` job, add `env: NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}` to the publish step. Put a rotation reminder on the calendar. Don't reuse the 2024 token.