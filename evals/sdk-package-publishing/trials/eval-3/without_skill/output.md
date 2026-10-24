# Fix `@fennel/client` `latest` tag and prevent a repeat

**Cause:** `--tag latest` is hard-coded in the publish step, so every version, including prereleases, is published as `latest`.

## Part 1: Repair the registry (run from your terminal)

These commands change the registry, so I haven't run them.

1. **Repoint `latest` to stable.** This is instant and fixes plain `npm install`. Do it before anything else.

   ```bash
   npm dist-tag add @fennel/client@2.9.4 latest
   npm view @fennel/client dist-tags --json
   ```

   Expected: `"latest": "2.9.4"`. The beta tag may still show `3.0.0-beta.1` under `latest` until the first command lands. Re-run the view to confirm.

2. **Unpublish the beta.** You published it last night, so you're inside npm's 72-hour unpublish window. It only works if nothing public depends on it.

   ```bash
   npm unpublish @fennel/client@3.0.0-beta.1
   ```

   - The version number is burned forever. The next beta must be `3.0.0-beta.2`.
   - Anyone who locked `3.0.0-beta.1` overnight gets a 404 on fresh installs. If that matters, run `npm deprecate @fennel/client@3.0.0-beta.1 "Published by mistake, use 2.9.4"` instead. It hides the beta from default resolution and breaks nobody.
   - If the unpublish is refused (dependents, or window expired), fall back to `deprecate`.

3. **Verify from a clean directory.**

   ```bash
   cd "$(mktemp -d)" && npm init -y >/dev/null && npm install @fennel/client && npm ls @fennel/client
   ```

   Expected: `2.9.4`.

4. **Clean up the repo.** Delete the `v3.0.0-beta.1` git tag and GitHub release, or mark the release as a pre-release. Otherwise the next run may re-trigger on it.

## Part 2: Make the workflow choose the tag

Rules the script enforces:

- Prerelease versions get their prerelease id as the tag (`beta`, `rc`), never `latest`.
- A stable version gets `latest` only if it's higher than the current `latest`.
- A lower stable version, such as a 2.x backport after 3.0.0 ships, gets `latest-<major>`. Backports never move `latest`.
- The script fails closed. If `npm view` errors or returns nothing, the job stops. It never defaults to a value, because a default would reopen this bug.

### `scripts/resolve-npm-tag.sh`

```bash
#!/usr/bin/env bash
# Prints the npm dist-tag for the version in package.json. Exits non-zero on any doubt.
set -euo pipefail

PKG=$(node -p "require('./package.json').name")
VERSION=$(node -p "require('./package.json').version")

if [[ "$VERSION" == *-* ]]; then
  # 3.0.0-beta.1 -> beta. A numeric id (1.0.0-0) is not a usable tag name.
  PRE=${VERSION#*-}
  TAG=${PRE%%.*}
  if [[ ! "$TAG" =~ ^[A-Za-z][A-Za-z0-9-]*$ || "$TAG" == "latest" ]]; then
    echo "::error::Cannot derive a safe dist-tag from prerelease '$VERSION'" >&2
    exit 1
  fi
else
  # No fallback value: an npm failure must stop the release, not publish to latest.
  LATEST=$(npm view "$PKG" dist-tags.latest)
  if [[ -z "$LATEST" || "$LATEST" == *-* ]]; then
    echo "::error::Current latest '$LATEST' is empty or a prerelease; repair it by hand first" >&2
    exit 1
  fi
  if [[ "$VERSION" == "$LATEST" ]]; then
    echo "::error::$VERSION is already latest" >&2
    exit 1
  fi
  HIGHEST=$(printf '%s\n%s\n' "$LATEST" "$VERSION" | sort -V | tail -n1)
  if [[ "$HIGHEST" == "$VERSION" ]]; then
    TAG=latest
  else
    TAG="latest-${VERSION%%.*}"   # backport: 2.9.5 while latest is 3.x -> latest-2
  fi
fi

echo "tag=$TAG"
```

`sort -V` is safe here because only stable versions are compared.

### Workflow steps

```yaml
      - name: Resolve dist-tag
        id: tag
        run: bash scripts/resolve-npm-tag.sh >> "$GITHUB_OUTPUT"

      - name: Publish
        env:
          NPM_DIST_TAG: ${{ steps.tag.outputs.tag }}
        run: npm publish --access public --tag "$NPM_DIST_TAG"

      - name: Assert latest is stable
        run: |
          LATEST=$(npm view @fennel/client dist-tags.latest)
          if [[ -z "$LATEST" || "$LATEST" == *-* ]]; then
            echo "::error::latest is '$LATEST' after publish"; exit 1
          fi
```

The last step catches any future regression, even one that bypasses the script.

For backports, run the same workflow from a `2.x` branch by adding it to the trigger's `branches`. No other change is needed, because the script picks the tag from the version.

## Part 3: Test the script before trusting it

Stub `npm` with a function and check each case:

| `package.json` version | current `latest` | expected |
|---|---|---|
| `3.0.0-beta.2` | 2.9.4 | `beta` |
| `3.0.0-rc.1` | 2.9.4 | `rc` |
| `2.9.5` | 2.9.4 | `latest` |
| `3.0.0` | 2.9.4 | `latest` |
| `2.9.5` | 3.0.0 | `latest-2` |
| `1.0.0-0` | any | fail (numeric id) |
| `2.9.5` | `npm view` errors | fail |
| `2.9.5` | empty output | fail |
| `2.9.5` | `3.0.0-beta.1` | fail |

The failing rows matter most. A check that has only been seen passing hasn't been shown to catch anything. Confirm the "`npm view` errors" row exits non-zero.

Then run `npm publish --dry-run --tag "$TAG"` in CI on a PR before the first real release.

## Optional hardening

- Trigger releases only from tags matching `v*`, and fail if the tag doesn't match the `package.json` version.
- Require a manual approval environment on the publish job for any `latest` or `latest-*` tag.