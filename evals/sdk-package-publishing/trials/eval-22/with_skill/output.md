# Ironvale release plan: `@ironvale/react-native-sdk` (draft, pending your approval before files land)

**Verdict.** The workflow can be one file on one tag push. It cannot publish everything in parallel. Three parts of the request change.

| You asked | Plan |
|---|---|
| Bump and publish on tag push | Bump happens before the tag, in Release It. CI checks that the tag equals every committed version and never edits the repo. |
| npm, Maven and iOS in parallel | Native first, in parallel: Maven, the iOS checks and the pod. npm goes last, only after Maven resolves publicly. |
| Release It with an npm token | Release It only bumps, commits and tags. npm publishes by trusted publishing plus staged approval. The token is deleted. |
| Ten minutes | Not guaranteed. Two human gates (Maven Portal, `npm stage approve`) and Central sync time are outside CI. Measure the first real run. |

Why npm goes last: the npm package pins exact native versions. If npm goes out first and Maven dies, the package points at a missing artifact. That is why you unpublished last time. The new order removes the cause. A Maven failure now happens before npm is staged, so there is nothing to unpublish.

## 1. Assumptions and inventory

Assumed because no one was available to ask. Correct any that are wrong.

- GitHub Actions, GitHub-hosted runners (OIDC for npm needs this).
- All three artifacts share one version `X.Y.Z` (lockstep).
- Maven coordinates are `com.ironvale:sdk-android`, built with Gradle. Replace with your real ones.
- The iOS SDK is a source SwiftPM package with `Package.swift` at the repo root. It is not a binary XCFramework. If it is binary, use the draft-release flow in `swift-cocoapods.md` instead.
- A pod `IronvaleSDK` exists on CocoaPods trunk and the wrapper podspec depends on it.
- Both example apps resolve the native SDK from local publication (`publishToMavenLocal`, a path pod) in the build jobs. Central does not have the new version yet, so they cannot resolve it from there.

| Artifact | Registry | Publish path today | Credential today | Target |
|---|---|---|---|---|
| JS package | npm | Release It on a laptop or CI | npm token | CI, trusted publishing + staged approval |
| Android SDK | Maven Central | Gradle job | Portal token | CI, Portal token, validate-then-publish gate |
| iOS SDK | SwiftPM | git tag | Tag rights | The protected tag is the release |
| iOS pod | CocoaPods trunk | `pod trunk push` | Trunk session | Temporary job, ends before the trunk cutoff |

## 2. Per-registry decisions

**npm**
- Credential: trusted publishing bound to the `release-npm` environment. Release It's token step is replaced by `npm stage publish`.
- First publish does not apply: the package already exists.
- A trusted-publisher configuration that no publish validates within 48 hours expires. Register it on release day.
- Settings to apply once one real release has worked:
  - Publishing access: "Require two-factor authentication and disallow tokens".
  - Direct publish: off.
  - OIDC dist-tag permission: off.
  - Revoke every write token, including the one Release It uses today.
- Dist-tag: `latest` for stable, the channel name for pre-releases. A backport gets `latest-N`, so a rerun of an old release can never move `latest` backwards.
- Preflight: `npm pack --dry-run`, `npx publint`, `npx @arethetypeswrong/cli --pack`.

**Maven Central**
- Cost first: the SDK is tied to your commercial product. Since 2026-10-01 that needs Publisher Pro, including the next version of an SDK already on Central. Check with procurement before anything else.
- No OIDC exists. Use a Portal token owned by a bot account, with an expiry, stored in the `release-maven` environment.
- The signing subkey (with an expiry) lives in the same environment. The Gradle publish job holds both. It runs no tests.
- Keep `autoPublish` off. Use `publishToMavenCentral`, not `publishAndReleaseToMavenCentral`. A human inspects the validated deployment and publishes or drops it.
- A published version is permanent. Roll forward.
- An old OSSRH token does not work. Generate a Portal token.

**SwiftPM**
- The tag is the release, and it is already public when the workflow starts. Restrict who can create `[0-9]*` tags as tightly as you would restrict a token.
- Never move or delete a tag.
- The iOS job in the workflow verifies. It cannot undo. A bad iOS tag means a new tag.

**CocoaPods**
- Trunk is read-only for a test run 2026-11-01 to 2026-11-07, and permanently from 2026-12-02.
- A wrapper podspec that depends on a trunk pod freezes at the last pushed version. Move the wrapper to SwiftPM or a vendored XCFramework (React Native 0.87+ supports an experimental SwiftPM path) before 2026-12-02.
- The `pod-publish` job below exists only for releases before the cutoff. Delete it, and its `needs` entry, once you stop pushing.

## 3. Files

### `.release-it.json` (bump, commit and tag only)

```json
{
  "git": {
    "requireBranch": "main",
    "requireCleanWorkingDir": true,
    "commitMessage": "chore: release ${version}",
    "tagName": "${version}",
    "push": true
  },
  "npm": { "publish": false },
  "github": { "release": false },
  "hooks": {
    "before:init": ["npm run lint", "npm run typecheck", "npm test"],
    "after:bump": "node scripts/release/sync-native-versions.mjs ${version}"
  },
  "plugins": {
    "@release-it/conventional-changelog": { "preset": { "name": "angular" } }
  }
}
```

- `tagName` changes from the scaffold's `v${version}` to plain SemVer. SwiftPM wants it, and the workflow trigger, tag ruleset and environment rule must all list the same pattern.
- `sync-native-versions.mjs` is a small script you write. It rewrites every committed native pin to `${version}`:
  - the wrapper's `build.gradle` pin on `sdk-android`
  - the wrapper podspec's dependency on `IronvaleSDK`
  - the native SDK's own version files
- `after:bump` runs before the commit, so the pins land in the release commit.
- Run `npx release-it --dry-run` first. Then run it for real from a clean `main` on a release manager's machine. The push of the commit and tag starts the workflow.
- If `main` is protected against direct pushes, tell me. The bump then needs a release PR, and the tag goes on the merge commit.

### `scripts/release/check-versions.sh` (runs in `js-build`)

```bash
#!/usr/bin/env bash
# Fails unless the tag equals every committed version. Emits version and dist_tag.
set -euo pipefail

version="${GITHUB_REF_NAME}"
name="$(node -p "require('./package.json').name")"

pkg="$(node -p "require('./package.json').version")"
[ "$pkg" = "$version" ] || { echo "tag $version != package.json $pkg" >&2; exit 1; }

# Native pins. Paths are placeholders: point them at your real files.
grep -qE "^IRONVALE_SDK_VERSION=${version}\$" android/gradle.properties \
  || { echo "android/gradle.properties pin != $version" >&2; exit 1; }
grep -qE "^VERSION_NAME=${version}\$" native/android/gradle.properties \
  || { echo "native android version != $version" >&2; exit 1; }
grep -qE "s\.dependency +['\"]IronvaleSDK['\"], *['\"]${version}['\"]" ./*.podspec \
  || { echo "podspec pin != $version" >&2; exit 1; }

case "$version" in
  *-*)
    channel="${version#*-}"; channel="${channel%%.*}"
    case "$channel" in alpha|beta|rc|next) ;; *) echo "unknown channel $channel" >&2; exit 1 ;; esac ;;
  *)
    # 0.0.0 only on a genuine not-found; any other npm error stops the release.
    if out="$(npm view "$name" dist-tags.latest 2>err.log)"; then current="$out"
    elif grep -q E404 err.log; then current=0.0.0
    else cat err.log >&2; exit 1; fi
    highest="$(printf '%s\n%s\n' "$current" "$version" | sort -V | tail -n1)"
    if [ "$highest" = "$version" ]; then channel=latest
    else channel="latest-${version%%.*}"; fi ;;
esac

echo "version=$version" >> "$GITHUB_OUTPUT"
echo "dist_tag=$channel" >> "$GITHUB_OUTPUT"
```

### `scripts/release/central-has.sh` (idempotence check with a positive control)

```bash
#!/usr/bin/env bash
# usage: central-has.sh <group/path> <artifact> <version>   prints yes | no
# Exits 1 when the check cannot see Central: an error is never read as "no".
set -euo pipefail
base="https://repo1.maven.org/maven2/$1/$2"
code() { curl -s -o /dev/null -w '%{http_code}' --proto '=https' --tlsv1.2 "$1"; }

# Control: the artifact has earlier releases, so its metadata must answer 200.
[ "$(code "$base/maven-metadata.xml")" = 200 ] \
  || { echo "control failed: cannot see $base" >&2; exit 1; }

case "$(code "$base/$3/$2-$3.pom")" in
  200) echo yes ;;
  404) echo no ;;
  *)   echo "inconclusive" >&2; exit 1 ;;
esac
```

### `.github/workflows/release.yml`

```yaml
name: release
on:
  push:
    tags: ["[0-9]*.[0-9]*.[0-9]*"]       # plain SemVer: the tag is also the SwiftPM release
permissions: {}                          # nothing by default
concurrency:
  group: release
  cancel-in-progress: false              # never cancel a half-done release

jobs:
  # ---------- unprivileged: no secrets, no id-token ----------
  js-build:
    runs-on: ubuntu-latest
    permissions: { contents: read }
    outputs:
      version: ${{ steps.guard.outputs.version }}
      dist_tag: ${{ steps.guard.outputs.dist_tag }}
    steps:
      - uses: actions/checkout@<sha>     # v6
        with: { persist-credentials: false }
      - uses: actions/setup-node@<sha>   # v6
        with: { node-version: "24", package-manager-cache: false }
      - id: guard
        run: scripts/release/check-versions.sh
      - run: npm ci && npm run typecheck && npm run lint && npm test
      - run: npm pack --dry-run && npx publint && npx @arethetypeswrong/cli --pack
      - run: npm pack
      - uses: actions/upload-artifact@<sha>   # v5
        with: { name: npm-tarball, path: "*.tgz" }

  android-build:
    runs-on: ubuntu-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>     # v6
        with: { persist-credentials: false }
      - uses: gradle/actions/wrapper-validation@<sha>
      - uses: actions/setup-java@<sha>   # v5
        with: { distribution: temurin, java-version: "17" }
      - uses: actions/setup-node@<sha>   # v6
        with: { node-version: "24", package-manager-cache: false }
      - run: npm ci
      # Example app must resolve the new native SDK before Central has it.
      - run: ./gradlew --no-daemon :sdk-android:testReleaseUnitTest :sdk-android:publishToMavenLocal
        working-directory: native/android
      - run: ./gradlew --no-daemon assembleDebug -PuseMavenLocal=true
        working-directory: example/android

  ios-verify:
    runs-on: macos-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>     # v6
        with: { persist-credentials: false }
      - uses: actions/setup-node@<sha>   # v6
        with: { node-version: "24", package-manager-cache: false }
      - run: npm ci
      - run: swift build
      - run: pod lib lint IronvaleSDK.podspec --allow-warnings
      # Build the example app against the tagged sources, not trunk.
      - run: xcodebuild -workspace Example.xcworkspace -scheme Example -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' build
        working-directory: example/ios

  # ---------- native first ----------
  android-publish:
    needs: [js-build, android-build]
    runs-on: ubuntu-latest
    environment: release-maven           # reviewers approve; deployments restricted to release tags
    permissions: { contents: read }
    env:
      VERSION: ${{ needs.js-build.outputs.version }}
    steps:
      - uses: actions/checkout@<sha>     # v6
        with: { persist-credentials: false }
      - uses: gradle/actions/wrapper-validation@<sha>
      - uses: actions/setup-java@<sha>   # v5
        with: { distribution: temurin, java-version: "17" }
      - id: exists
        run: echo "present=$(scripts/release/central-has.sh com/ironvale sdk-android "$VERSION")" >> "$GITHUB_OUTPUT"
      - name: Upload and validate (no automatic release)
        if: steps.exists.outputs.present == 'no'
        working-directory: native/android
        env:
          ORG_GRADLE_PROJECT_mavenCentralUsername: ${{ secrets.CENTRAL_TOKEN_USER }}
          ORG_GRADLE_PROJECT_mavenCentralPassword: ${{ secrets.CENTRAL_TOKEN_PASS }}
          ORG_GRADLE_PROJECT_signingInMemoryKey: ${{ secrets.SIGNING_KEY }}
          ORG_GRADLE_PROJECT_signingInMemoryKeyPassword: ${{ secrets.SIGNING_KEY_PASSWORD }}
        run: ./gradlew --no-daemon --no-configuration-cache -PVERSION_NAME="$VERSION" :sdk-android:publishToMavenCentral
      - name: Tell the approver what to do
        run: |
          if [ "${{ steps.exists.outputs.present }}" = yes ]; then
            echo "Version already on Central: nothing uploaded." >> "$GITHUB_STEP_SUMMARY"
          else
            echo "Open the Central Portal, inspect the VALIDATED deployment for $VERSION, then Publish (or Drop)." >> "$GITHUB_STEP_SUMMARY"
          fi

  wait-central:
    needs: [js-build, android-publish]
    runs-on: ubuntu-latest
    timeout-minutes: 120
    permissions: { contents: read }
    env:
      VERSION: ${{ needs.js-build.outputs.version }}
    steps:
      - uses: actions/checkout@<sha>     # v6
        with: { persist-credentials: false }
      - run: |
          for _ in $(seq 1 240); do
            [ "$(scripts/release/central-has.sh com/ironvale sdk-android "$VERSION" 2>/dev/null)" = yes ] && exit 0
            sleep 30
          done
          echo "sdk-android $VERSION not on Central after 120 min" >&2; exit 1

  # DELETE this job and its needs entry when you stop pushing to trunk (before 2026-12-02).
  pod-publish:
    needs: [js-build, ios-verify]
    runs-on: macos-latest
    environment: release-pod
    permissions: { contents: read }
    env:
      VERSION: ${{ needs.js-build.outputs.version }}
      COCOAPODS_TRUNK_TOKEN: ${{ secrets.COCOAPODS_TRUNK_TOKEN }}
    steps:
      - uses: actions/checkout@<sha>     # v6
        with: { persist-credentials: false }
      - run: |
          if pod trunk info IronvaleSDK | grep -q -- "- ${VERSION} "; then
            echo "pod $VERSION already on trunk"; exit 0
          fi
          pod trunk push IronvaleSDK.podspec

  # ---------- JS last ----------
  npm-publish:
    needs: [js-build, ios-verify, wait-central, pod-publish]
    runs-on: ubuntu-latest
    environment: release-npm             # name must match the trusted-publisher configuration exactly
    permissions:
      contents: read
      id-token: write                    # OIDC, this job only
    env:
      VERSION: ${{ needs.js-build.outputs.version }}
      DIST_TAG: ${{ needs.js-build.outputs.dist_tag }}
      PACKAGE: "@ironvale/react-native-sdk"
    steps:
      - uses: actions/download-artifact@<sha>   # v5
        with: { name: npm-tarball }
      - uses: actions/setup-node@<sha>    # v6
        with: { node-version: "24", registry-url: "https://registry.npmjs.org", package-manager-cache: false }
      - run: npm install -g npm@<pinned 11.15+ version>   # staged publishing needs 11.15.0+
      - name: Skip if this version is already published
        id: exists
        run: |
          if out="$(npm view "$PACKAGE@$VERSION" version 2>err.log)" && [ -n "$out" ]; then echo present=yes >> "$GITHUB_OUTPUT"
          elif grep -q E404 err.log; then echo present=no >> "$GITHUB_OUTPUT"
          else cat err.log; exit 1; fi
      - if: steps.exists.outputs.present == 'no'
        run: npm stage publish ./*.tgz --access public --tag "$DIST_TAG"
      - run: echo "Run 'npm stage list', inspect, then 'npm stage approve <stage-id>' (2FA)." >> "$GITHUB_STEP_SUMMARY"
```

Notes on the file:
- The workflow has no `workflow_dispatch` and no branch trigger. Adding either needs the same environment gate.
- The `npm-publish` job sets no `NODE_AUTH_TOKEN`.
- Pin every `<sha>` with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`, or let Dependabot pin them. Do not guess one.
- Tests run in the unprivileged jobs. The two privileged jobs only package and upload.

### Repository setup (hand-done in GitHub and the registries)

1. Tag ruleset: only release managers may create, move or delete `[0-9]*` tags.
2. Environments `release-maven`, `release-npm` and `release-pod`:
   - reviewers are a team, or at least two people besides whoever cuts releases
   - self-review blocked
   - deployments restricted to the `[0-9]*` tag pattern
   - Maven and pod secrets live in their own environment only; no repository-level publish secrets
3. npm trusted publisher: owner, repository, workflow file `release.yml`, environment `release-npm`.
4. Delete the repository `NPM_TOKEN` secret after the first OIDC release succeeds.

## 4. Rollback runbook (commands are yours to run)

Rules for all of it:
- Publish the fix first.
- Soft-remove second.
- Never unpublish.

**Why not unpublish:** a published `name@version` can never be reused, even after unpublish. Unpublish only works within 72 hours and only with no dependents. It would not have made last time's retry cleaner.

| Situation | Action |
|---|---|
| Maven failed before Publish, deployment VALIDATED or FAILED | In the Portal, **drop** the deployment. Then **re-run failed jobs** on the same tag. The check skips nothing because the version is absent. Always drop a stale deployment first: a rerun uploads a second one. |
| Maven published, a later job failed | Re-run failed jobs on the same tag. Both publish jobs skip versions that already exist. Finish the release. |
| npm staged, not approved, and wrong | **`npm stage reject <stage-id>`** |
| Bad npm version published | Ship `X.Y.Z+1` through this workflow. Then **`npm deprecate "@ironvale/react-native-sdk@<bad>" "Broken <what>, use <fixed>"`**. If `latest` points at the bad version: **`npm dist-tag add @ironvale/react-native-sdk@<fixed> latest`**. |
| Bad Maven version published | Release a fixed version and announce it in the changelog. Only Sonatype support removes a component, for malware or leaked secrets. |
| Bad iOS tag | Do not move or delete it. Cut the next tag and add a README notice. |
| Bad pod version (before cutoff) | **`pod trunk deprecate IronvaleSDK`**, with a README notice pointing to SwiftPM. Avoid `pod trunk delete`: it breaks every Podfile.lock pinning that version. |
| Suspected compromise | Isolate runners first. Then revoke and rotate the Portal token, the signing subkey, the trunk token and any npm token. Then follow the table above. |

Removal commands have no safe dry run. Do not add a dry-run flag to them.

Rehearse before the first real release, never on production packages:
- npm: a scratch scoped package, through stage, approve, deprecate and dist-tag.
- Maven: upload to a test namespace or the real one, check the VALIDATED deployment, then drop. Never click Publish to rehearse.
- SwiftPM: a scratch repository and tag.

## 5. Private consumption

Nothing in this plan is private: all three packages are public. If you also publish internal builds, say so and I will add a feed config and the canary probe.

## 6. Migration sequence

| When | Step | Evidence |
|---|---|---|
| Today, 2026-10-23 | Confirm Publisher Pro is in place for `com.ironvale`. Answer the open questions below. | Procurement ticket |
| Before the next release | Create environments and the tag ruleset. Create the Portal token and the signing subkey, both with expiries, owned by a bot account. | Settings screenshots, calendar entries for the rotations |
| Release day | Add the npm trusted publisher (48-hour validation window). Release with `release-it`. Approve the Maven deployment, then `npm stage approve`. | Workflow run, provenance on the package page |
| Right after the first good release | Set npm to disallow tokens. Revoke every write token. Delete `NPM_TOKEN`. | Package settings, revoked token list |
| Before 2026-11-01 | Last trunk push and, if the wrapper moves off the pod, **`pod trunk deprecate IronvaleSDK`**. | Trunk page |
| Before 2026-12-02 | Delete `pod-publish`. Move the wrapper to SwiftPM or a vendored XCFramework. | PR |
| Ongoing | Rotate the Portal token and the signing subkey on their expiry dates. | Calendar |

## Open questions (they change the files)

1. Is the iOS SDK source SwiftPM, or a binary XCFramework?
2. Does the wrapper podspec depend on the trunk pod today?
3. Is `main` protected against direct pushes by Release It?
4. Do all three artifacts really share one version?

**Next action (2 minutes):** confirm Maven Central Publisher Pro for `com.ironvale`. Then reply with answers to questions 1 and 2.