# Release workflow for `@ironvale/react-native-sdk`

This is one workflow on tag push. I haven't run it, and I haven't read your repo. Paths and Gradle task names are assumptions, marked below.

## Parallel publishing is the wrong fix

Last time's failure came from parallel jobs that can't be undone, not from the Maven job dying. Maven Central can never be unpublished. An npm unpublish is limited and breaks anyone who already installed the version. If you publish all three at once, any one failure leaves the other two live and you can't roll back.

So this design runs the checks in parallel, then publishes in sequence, riskiest step first. Every publish step skips itself if its artifact already exists, so a retry reruns only the failed job. You never unpublish.

```
tag push vX.Y.Z
   │
   ├─ preflight (parallel, publishes nothing)
   │     ├─ versions-match   tag == package.json == gradle == podspec
   │     ├─ npm-dry-run      build + npm pack
   │     ├─ android-build    gradle build + signing check
   │     └─ ios-build        swift build + pod lib lint
   │
   ▼ all green
 maven   (immutable, slowest, most likely to fail → first)
   │
   ▼
   ├─ npm   (parallel, idempotent)
   └─ ios   (parallel, idempotent: tag/pod)
   │
   ▼
 github-release
```

npm goes after Maven because the RN package pulls the native Android SDK from Maven Central. If npm shipped first, installs would fail until Maven synced.

## 1. `.release-it.json` (maintainer machine does the bump)

Release It bumps, commits, tags and pushes locally. The push triggers the workflow, and CI no longer bumps anything. That removes the usual problem where CI tries to push a bump commit back after the tag already exists.

```json
{
  "git": {
    "commitMessage": "chore: release ${version}",
    "tagName": "v${version}",
    "requireBranch": "main"
  },
  "npm": { "publish": false },
  "github": { "release": false },
  "hooks": {
    "after:bump": "scripts/sync-native-versions.sh ${version}"
  }
}
```

`npm.publish` and `github.release` are off because the workflow owns both. Without that, Release It would publish npm from your laptop and race CI.

## 2. `scripts/sync-native-versions.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
version="${1:?usage: sync-native-versions.sh <version>}"

# Paths are assumptions: adjust to the monorepo layout.
sed -i.bak "s/^VERSION_NAME=.*/VERSION_NAME=${version}/" android-sdk/gradle.properties
sed -i.bak "s/^\(\s*s.version\s*=\s*\).*/\1\"${version}\"/" IronvaleSDK.podspec
find . -name '*.bak' -not -path './node_modules/*' -delete
```

## 3. `.github/workflows/release.yml`

```yaml
name: release

on:
  push:
    tags: ["v[0-9]+.[0-9]+.[0-9]+*"]

# One release at a time; never cancel one that is mid-publish.
concurrency:
  group: release
  cancel-in-progress: false

permissions:
  contents: read

env:
  VERSION: ${{ github.ref_name }}   # vX.Y.Z; stripped to X.Y.Z in each job

jobs:
  # ---------- preflight: publishes nothing, runs in parallel ----------
  versions-match:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Tag must equal every manifest version
        run: |
          v="${VERSION#v}"
          pkg=$(jq -r .version package.json)
          gradle=$(grep '^VERSION_NAME=' android-sdk/gradle.properties | cut -d= -f2)
          pod=$(grep -E '^\s*s\.version' IronvaleSDK.podspec | sed -E 's/.*"([^"]+)".*/\1/')
          echo "tag=$v npm=$pkg gradle=$gradle pod=$pod"
          [ "$v" = "$pkg" ] && [ "$v" = "$gradle" ] && [ "$v" = "$pod" ]

  npm-dry-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: yarn }
      - run: yarn install --immutable
      - run: yarn typecheck && yarn lint && yarn test
      - run: yarn prepare            # builds lib/ via bob
      - run: npm pack --dry-run

  android-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - uses: gradle/actions/setup-gradle@v4
      - name: Build and verify signing material is present
        working-directory: android-sdk
        env:
          ORG_GRADLE_PROJECT_signingInMemoryKey: ${{ secrets.MAVEN_SIGNING_KEY }}
          ORG_GRADLE_PROJECT_signingInMemoryKeyPassword: ${{ secrets.MAVEN_SIGNING_PASSWORD }}
        run: ./gradlew build publishToMavenLocal   # exercises signing without uploading

  ios-build:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - run: swift build
        working-directory: ios-sdk
      - run: pod lib lint IronvaleSDK.podspec --allow-warnings

  # ---------- Maven Central: immutable, slowest, so it goes first ----------
  maven:
    needs: [versions-match, npm-dry-run, android-build, ios-build]
    runs-on: ubuntu-latest
    environment: release            # optional: add required reviewers here
    steps:
      - uses: actions/checkout@v4
      - name: Skip if already on Maven Central
        id: exists
        run: |
          v="${VERSION#v}"
          url="https://repo1.maven.org/maven2/com/ironvale/sdk/${v}/sdk-${v}.pom"   # group/artifact are assumptions
          code=$(curl -s -o /dev/null -w '%{http_code}' "$url")
          case "$code" in
            200) echo "published=true"  >> "$GITHUB_OUTPUT" ;;
            404) echo "published=false" >> "$GITHUB_OUTPUT" ;;
            *)   echo "unexpected HTTP $code from Maven Central"; exit 1 ;;   # never fail open
          esac
      - uses: actions/setup-java@v4
        if: steps.exists.outputs.published == 'false'
        with: { distribution: temurin, java-version: 17 }
      - uses: gradle/actions/setup-gradle@v4
        if: steps.exists.outputs.published == 'false'
      - name: Publish and release (Portal validates before release; invalid bundles are never published)
        if: steps.exists.outputs.published == 'false'
        working-directory: android-sdk
        env:
          ORG_GRADLE_PROJECT_mavenCentralUsername: ${{ secrets.MAVEN_CENTRAL_USERNAME }}
          ORG_GRADLE_PROJECT_mavenCentralPassword: ${{ secrets.MAVEN_CENTRAL_PASSWORD }}
          ORG_GRADLE_PROJECT_signingInMemoryKey: ${{ secrets.MAVEN_SIGNING_KEY }}
          ORG_GRADLE_PROJECT_signingInMemoryKeyPassword: ${{ secrets.MAVEN_SIGNING_PASSWORD }}
        run: ./gradlew publishAndReleaseToMavenCentral --no-configuration-cache   # assumes the vanniktech maven-publish plugin
      - name: Wait until the artifact resolves
        run: |
          v="${VERSION#v}"
          url="https://repo1.maven.org/maven2/com/ironvale/sdk/${v}/sdk-${v}.pom"
          for i in $(seq 1 60); do
            [ "$(curl -s -o /dev/null -w '%{http_code}' "$url")" = 200 ] && exit 0
            sleep 30
          done
          echo "not visible on Central after 30 min"; exit 1

  # ---------- npm and iOS: cheap, idempotent, parallel ----------
  npm:
    needs: maven
    runs-on: ubuntu-latest
    environment: release
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: yarn
          registry-url: https://registry.npmjs.org
      - name: Skip if already on npm
        id: exists
        run: |
          v="${VERSION#v}"
          if npm view "@ironvale/react-native-sdk@${v}" version >/tmp/npm-view.out 2>/tmp/npm-view.err; then
            echo "published=true" >> "$GITHUB_OUTPUT"
          elif grep -q E404 /tmp/npm-view.err; then
            echo "published=false" >> "$GITHUB_OUTPUT"
          else
            cat /tmp/npm-view.err; exit 1     # registry/network error is not "not published"
          fi
        env: { NODE_AUTH_TOKEN: "${{ secrets.NPM_TOKEN }}" }
      - if: steps.exists.outputs.published == 'false'
        run: yarn install --immutable && yarn prepare
      - if: steps.exists.outputs.published == 'false'
        run: |
          tag=latest
          case "$VERSION" in *-*) tag=next ;; esac   # prereleases must not move "latest"
          npm publish --access public --tag "$tag" --provenance
        env: { NODE_AUTH_TOKEN: "${{ secrets.NPM_TOKEN }}" }

  ios:
    needs: maven
    runs-on: macos-15
    environment: release
    steps:
      - uses: actions/checkout@v4
      # The pushed vX.Y.Z tag is already the SwiftPM version if Package.swift is at the repo root.
      # If iOS uses a separate tag (e.g. ios-vX.Y.Z), create it here, skipping when it exists.
      - name: Verify SwiftPM resolves the tag
        run: swift package resolve
      - name: Push podspec (skip if version exists)
        env: { COCOAPODS_TRUNK_TOKEN: "${{ secrets.COCOAPODS_TRUNK_TOKEN }}" }
        run: |
          v="${VERSION#v}"
          if pod trunk info IronvaleSDK | grep -q "^\s*- ${v} "; then
            echo "pod ${v} already on trunk"
          else
            pod trunk push IronvaleSDK.podspec --allow-warnings
          fi

  github-release:
    needs: [npm, ios]
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps:
      - uses: actions/checkout@v4
      - run: gh release create "$VERSION" --generate-notes --verify-tag || gh release view "$VERSION"
        env: { GH_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
```

## 4. Recovery runbook

| Failure | What to do |
|---|---|
| Preflight fails | Nothing is published. Fix on `main`, delete the tag (`git push --delete origin vX.Y.Z`), rerun `release-it`. |
| `maven` fails before upload or at Portal validation | Nothing is published. Use "Re-run failed jobs". |
| `maven` succeeds, `npm` fails | Use "Re-run failed jobs". Maven and the pod are skipped by their existence checks. |
| `ios` fails | Rerun it alone. |
| A bad version already shipped | Roll forward with a patch release. Use `npm deprecate` for npm. Don't unpublish. |

## Caveats

- **Ten minutes isn't guaranteed.** Maven Central Portal validation and sync often takes 10–30 minutes, and that wait now sits on the critical path. Preflight, npm and iOS together take about 5 minutes. If Maven is slow, the release is slow, and that's the price of not publishing blind.
- **Assumed names:** the `android-sdk/` and `ios-sdk/` paths, the `com.ironvale:sdk` coordinates, the `IronvaleSDK` pod name and the vanniktech `publishAndReleaseToMavenCentral` task. Replace them with yours.
- **Secrets:**
  - `NPM_TOKEN`
  - `MAVEN_CENTRAL_USERNAME`
  - `MAVEN_CENTRAL_PASSWORD`
  - `MAVEN_SIGNING_KEY`
  - `MAVEN_SIGNING_PASSWORD`
  - `COCOAPODS_TRUNK_TOKEN`

  Scope them to the `release` environment, not the repo.
- **npm token:** `--provenance` needs `id-token: write` on the npm job (add it under `permissions`). npm trusted publishing (OIDC) would let you drop `NPM_TOKEN` entirely, if you want to move off the token later.

## Questions for you

1. Is the iOS "tag" the same `vX.Y.Z` as the repo tag, or a separate `ios-vX.Y.Z`?
2. Does the pod wrap the native iOS SDK, or is it the native SDK itself?
3. Which Gradle publishing plugin do you use for Maven Central?