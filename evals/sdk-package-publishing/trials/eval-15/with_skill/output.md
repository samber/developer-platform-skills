# Ravelstone: publishing `ravelstone_pay` (4 packages) to pub.dev from a button

## Read this first

1. **pub.dev refuses automated publishes from `workflow_dispatch`.** It accepts only a tag push. A button that runs `dart pub publish` cannot work.
2. **The button cuts the release instead of publishing it.** A PM runs `cut-release` on the Actions tab. It bumps the four packages, tags the commit and pushes. The tag starts `release`, which publishes all four packages. A PM approves that run in the `release` environment.
3. **The first version of each package must be published by hand.** pub.dev automation only covers packages that already exist. An engineer does this once, in dependency order (§4). After that, no engineer is needed.
4. **The iOS dependency has a deadline.** `RavelstonePay` is on CocoaPods trunk, which goes read-only on 2026-12-02. That is 40 days away, and a read-only test run starts 2026-11-01. Decision D1 below covers it.

## 1. Assumptions and inventory

No one was available to answer the interview, so I assumed the following. Correct any that are wrong.

- GitHub Actions on hosted runners, with the repo at `<org>/<repo>`. If the repo is private, check that your plan supports environment protection rules.
- The layout is `packages/<name>`, with a Dart pub workspace at the root. Members use `resolution: workspace` and sibling dependencies written as `name: ^x.y.z`. If you use melos with `dependency_overrides` instead, the bump and `pub get` steps need adapting.
- All four packages share one version (lockstep). One tag, one run and one approval then publish everything.
- The native SDKs are pinned exactly: `s.dependency 'RavelstonePay', '= X.Y.Z'` in the podspec, and `api 'GROUP:ARTIFACT:X.Y.Z'` in `android/build.gradle`.
- `GROUP` and `ARTIFACT` for the Android SDK are placeholders. You must fill them in.
- The SDK is a commercial product. Maven Central's Publisher Pro requirement applies to your Android SDK releases (from 2026-10-01), not to the pub.dev packages.

| Package | Registry | Publish path | Credential | Owner |
|---|---|---|---|---|
| `ravelstone_pay_platform_interface` | pub.dev | First version by hand, then CI tag | None after the first version (OIDC) | Verified publisher |
| `ravelstone_pay_ios` | pub.dev | Same | Same | Same |
| `ravelstone_pay_android` | pub.dev | Same | Same | Same |
| `ravelstone_pay` (app-facing) | pub.dev | Same | Same | Same |
| `RavelstonePay` (iOS SDK) | CocoaPods trunk | Native SDK team | Trunk token (no OIDC exists) | Native iOS team |
| Android SDK | Maven Central | Native SDK team | Portal token (no OIDC exists) | Native Android team |

The plugin never pushes anything to CocoaPods trunk or Maven Central. It only consumes the native SDKs.

## 2. Decisions

**Credentials**
- Use pub.dev automated publishing from GitHub Actions, bound to the protected environment `release`. Create no pub.dev secret in GitHub.
- The one new credential is a GitHub App that can push a tag, and it cannot publish anything. A tag pushed with the default `GITHUB_TOKEN` would not start the `release` workflow, so the App is required.
- Harden the jobs:
  - Pin every action to a full SHA.
  - Set `permissions: {}` by default.
  - Restore no caches.
  - Use no `pull_request_target` or `workflow_run` triggers.

**Namespace**
- Create a verified publisher for your company domain, using domain proof through Google Search Console.
- Transfer all four packages to it right after the manual first publish. The transfer is irreversible, and every publisher member gets upload rights, so keep the membership to release owners.

**Federated shape**
- Publish in this order: platform interface, `_ios`, `_android`, then the app-facing package.
- In `ravelstone_pay/pubspec.yaml`, endorse the implementations:

```yaml
name: ravelstone_pay
version: 1.0.0
repository: https://github.com/<org>/<repo>
resolution: workspace
flutter:
  plugin:
    platforms:
      ios:
        default_package: ravelstone_pay_ios
      android:
        default_package: ravelstone_pay_android
dependencies:
  ravelstone_pay_platform_interface: ^1.0.0
  ravelstone_pay_ios: ^1.0.0
  ravelstone_pay_android: ^1.0.0
```

- `ravelstone_pay_ios` and `ravelstone_pay_android` each declare `implements: ravelstone_pay` under `flutter.plugin.platforms`.
- Keep platform-interface changes additive, with default implementations.
- Leave `publish_to` unset on the public packages.
- Each package needs a `LICENSE`, a `CHANGELOG.md` and a `repository:` field. pana grades these.

**Native dependencies**
- Android: `build.gradle` points at the Maven Central coordinate, pinned exactly.
- iOS:
  - Ship `ios/ravelstone_pay_ios/Package.swift` and keep the podspec. Flutter 3.44 makes SwiftPM the default for plugins.
  - The podspec keeps resolving the pinned trunk version after 2026-12-02, because existing pods keep installing. But no new `RavelstonePay` version can reach trunk after that date.
- Add a public pub.dev package rule: no git or custom-hosted dependencies.

**Versions**
- SemVer, with pre-releases such as `1.4.0-beta.1`. Tags are `vX.Y.Z`.
- The tag, the four `version:` fields and the sibling constraints (`^X.Y.Z`) must all agree. The pipeline checks this.

**Decisions for you**
- **D1: iOS SDK on SwiftPM.** Does the native iOS SDK have a public SwiftPM package?
  - If yes, `Package.swift` can depend on it, and iOS native upgrades continue after 2026-12-02.
  - If no, the plugin's iOS side freezes at the last trunk version. Either vendor an XCFramework in the podspec or ship a SwiftPM package soon.
  - If the next plugin release needs a new native iOS version, push it to trunk before 2026-11-01.
- **D2: Who approves.** The `release-approvers` team should hold PMs only, and it needs at least two people besides whoever usually clicks the button. GitHub's "prevent self-review" cannot block the PM who clicked the button. The tag is pushed by the App, so the approval run's actor is the App, not that PM. If you want strict two-person control, make a different person from the clicker approve, by policy.
- **D3: Lockstep versions.** pub.dev documents the `<package>-v{{version}}` tag pattern for monorepos. The one-tag design depends on pub.dev accepting one OIDC token for all four packages configured with the same pattern. I could not confirm that from the docs, and it is validated by the first automated release. If pub.dev rejects it, fall back to four per-package tags. That means four approvals per release.

## 3. Pipeline files

Replace every `<sha>` with a full commit SHA, with the version kept as a comment:

```sh
git ls-remote https://github.com/<owner>/<action> refs/tags/<version>
```

Or let Dependabot or Renovate pin them.

### `.github/workflows/cut-release.yml` (the PM's button)

```yaml
name: cut-release
run-name: Cut release ${{ inputs.version }}

on:
  workflow_dispatch:
    inputs:
      version:
        description: "Version for all four packages, e.g. 1.4.0 or 1.4.0-beta.1"
        required: true
        type: string
      notes:
        description: "One-line changelog entry"
        required: true
        type: string

permissions: {}

concurrency:
  group: cut-release
  cancel-in-progress: false

jobs:
  cut:
    # The environment also restricts deployments to main, so a dispatch from any other branch gets no App secret.
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: cut-release
    permissions:
      contents: read
    env:
      VERSION: ${{ inputs.version }}
      NOTES: ${{ inputs.notes }}
      REQUESTED_BY: ${{ github.actor }}
    steps:
      - id: app
        uses: actions/create-github-app-token@<sha> # v2
        with:
          app-id: ${{ vars.RELEASE_APP_ID }}
          private-key: ${{ secrets.RELEASE_APP_PRIVATE_KEY }}

      - uses: actions/checkout@<sha> # v6
        with:
          token: ${{ steps.app.outputs.token }}

      - name: Validate inputs
        run: |
          set -euo pipefail
          [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-(alpha|beta|rc)\.[0-9]+)?$ ]] \
            || { echo "invalid version: $VERSION"; exit 1; }
          [ -n "$NOTES" ] || { echo "notes are required"; exit 1; }
          rc=0
          git ls-remote --exit-code --tags origin "refs/tags/v${VERSION}" >/dev/null || rc=$?
          # exit 2 = no matching ref; 0 = tag exists; anything else = could not ask
          [ "$rc" = 2 ] || { echo "tag v${VERSION} exists or the check failed (rc=$rc)"; exit 1; }

      - name: Bump the four packages
        run: |
          set -euo pipefail
          for pkg in ravelstone_pay_platform_interface ravelstone_pay_ios ravelstone_pay_android ravelstone_pay; do
            f="packages/${pkg}/pubspec.yaml"
            sed -i -E "s/^version: .*/version: ${VERSION}/" "$f"
            sed -i -E "s/^(  ravelstone_pay_(platform_interface|ios|android)): .*/\1: ^${VERSION}/" "$f"
            c="packages/${pkg}/CHANGELOG.md"
            { printf '## %s\n\n- %s\n\n' "$VERSION" "$NOTES"; cat "$c"; } > "${RUNNER_TEMP}/changelog"
            mv "${RUNNER_TEMP}/changelog" "$c"
          done
          git diff --stat

      - name: Commit, tag and push
        env:
          GH_TOKEN: ${{ steps.app.outputs.token }}
        run: |
          set -euo pipefail
          git config user.name "<app-slug>[bot]"
          git config user.email "<app-id>+<app-slug>[bot]@users.noreply.github.com"
          git switch -c "release/${VERSION}"
          git add packages/*/pubspec.yaml packages/*/CHANGELOG.md
          git commit -m "chore(release): ${VERSION}" -m "Requested by ${REQUESTED_BY}."
          git tag -a "v${VERSION}" -m "Release ${VERSION}, requested by ${REQUESTED_BY}"
          git push --atomic origin "release/${VERSION}" "refs/tags/v${VERSION}"
          gh pr create --base main --head "release/${VERSION}" \
            --title "chore(release): ${VERSION}" \
            --body "Version bump for ${VERSION}. Merge after the publish run succeeds."
          echo "Tag v${VERSION} pushed. Next: approve the release run in the Actions tab." >> "$GITHUB_STEP_SUMMARY"
```

The inputs reach the shell only through `env:`, never by inline `${{ }}` interpolation. That blocks script injection from the free-text `notes` field.

The button releases the current tip of `main`. The `release` run re-runs the tests on the tagged commit before anyone is asked to approve.

### `.github/workflows/release.yml` (tag-triggered publish)

```yaml
name: release

on:
  push:
    tags: ["v[0-9]*"] # same pattern in the tag ruleset, the environment rule and pub.dev ("v{{version}}")

permissions: {}

env:
  FLUTTER_VERSION: "<pinned stable version, 3.44 or newer>"
  IOS_POD: RavelstonePay
  ANDROID_GROUP: com.example     # placeholder: your Maven groupId
  ANDROID_ARTIFACT: pay-android  # placeholder: your Maven artifactId
  IOS_SPM_REPO: ""               # D1: https://github.com/<org>/<ios-sdk-repo>, empty = skip the check

jobs:
  build: # unprivileged: no id-token, no secrets, no caches
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<sha> # v6
        with:
          persist-credentials: false

      - uses: subosito/flutter-action@<sha> # v2
        with:
          flutter-version: ${{ env.FLUTTER_VERSION }}
          cache: false

      - name: Tag, versions and sibling constraints agree
        run: |
          set -euo pipefail
          version="${GITHUB_REF_NAME#v}"
          for p in ravelstone_pay_platform_interface ravelstone_pay_ios ravelstone_pay_android ravelstone_pay; do
            v="$(sed -n -E 's/^version: *([^ #]+).*/\1/p' "packages/${p}/pubspec.yaml" | head -n1)"
            [ "$v" = "$version" ] || { echo "${p} is ${v}, tag is ${version}"; exit 1; }
          done
          need() { grep -qxF "  $2: ^${version}" "packages/$1/pubspec.yaml" \
                   || { echo "$1 must depend on $2 ^${version}"; exit 1; }; }
          for impl in ravelstone_pay_ios ravelstone_pay_android; do
            need "$impl" ravelstone_pay_platform_interface
            need ravelstone_pay "$impl"
          done
          need ravelstone_pay ravelstone_pay_platform_interface

      - name: Analyze and test
        run: |
          set -euo pipefail
          flutter pub get
          flutter analyze
          for d in packages/*/; do
            [ -d "${d}test" ] && (cd "$d" && flutter test)
          done

      - name: Dry-run the leaf package
        # Dependents cannot dry-run until the new interface version is live on pub.dev;
        # their validation runs inside the publish step.
        run: cd packages/ravelstone_pay_platform_interface && flutter pub publish --dry-run

      - name: Native SDK versions are already public
        run: |
          set -euo pipefail
          podspec=packages/ravelstone_pay_ios/ios/ravelstone_pay_ios.podspec
          ios_ver="$(grep -E "dependency +['\"]${IOS_POD}['\"]" "$podspec" \
            | sed -nE "s/.*['\"]= *([0-9][^'\"]*)['\"].*/\1/p" | head -n1)"
          [ -n "$ios_ver" ] || { echo "pin exactly: s.dependency '${IOS_POD}', '= X.Y.Z'"; exit 1; }
          code="$(curl -s -o "${RUNNER_TEMP}/pod.json" -w '%{http_code}' "https://trunk.cocoapods.org/api/v1/pods/${IOS_POD}")"
          [ "$code" = 200 ] || { echo "trunk lookup returned ${code}"; exit 1; }
          jq -e --arg v "$ios_ver" '.versions[] | select(.name == $v)' "${RUNNER_TEMP}/pod.json" >/dev/null \
            || { echo "${IOS_POD} ${ios_ver} is not on trunk. Release the native iOS SDK first."; exit 1; }

          and_ver="$(sed -nE "s/.*['\"]${ANDROID_GROUP}:${ANDROID_ARTIFACT}:([0-9][^'\"]*)['\"].*/\1/p" \
            packages/ravelstone_pay_android/android/build.gradle | head -n1)"
          [ -n "$and_ver" ] || { echo "pin exactly: ${ANDROID_GROUP}:${ANDROID_ARTIFACT}:X.Y.Z"; exit 1; }
          pom="https://repo1.maven.org/maven2/${ANDROID_GROUP//.//}/${ANDROID_ARTIFACT}/${and_ver}/${ANDROID_ARTIFACT}-${and_ver}.pom"
          [ "$(curl -s -o /dev/null -w '%{http_code}' "$pom")" = 200 ] \
            || { echo "Android SDK ${and_ver} is not on Maven Central. Release it first."; exit 1; }

          if [ -n "$IOS_SPM_REPO" ]; then
            git ls-remote --exit-code --tags "$IOS_SPM_REPO" "refs/tags/${ios_ver}" >/dev/null \
              || { echo "SwiftPM tag ${ios_ver} missing in ${IOS_SPM_REPO}"; exit 1; }
          fi

  publish: # holds the only publish identity; installs no project dependencies
    needs: build
    runs-on: ubuntu-latest
    environment: release # reviewers approve here; name must match pub.dev's Admin tab
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@<sha> # v6
        with:
          persist-credentials: false

      - uses: subosito/flutter-action@<sha> # v2
        with:
          flutter-version: ${{ env.FLUTTER_VERSION }}
          cache: false

      - name: Write the idempotent publish helper
        run: |
          cat > "${RUNNER_TEMP}/publish_one.sh" <<'EOF'
          #!/usr/bin/env bash
          set -euo pipefail
          dir="$1"; name="$2"; version="$3"
          api="https://pub.dev/api/packages/${name}/versions/${version}"
          status() { curl -s -o /dev/null -w '%{http_code}' --retry 3 --retry-all-errors "$api"; }
          case "$(status)" in
            200) echo "${name} ${version} already on pub.dev, skipping"; exit 0 ;;
            404) ;;
            *)   echo "unexpected status checking ${name}"; exit 1 ;;
          esac
          (cd "$dir" && flutter pub publish --force)
          for _ in $(seq 1 30); do
            [ "$(status)" = 200 ] && { echo "${name} ${version} is live"; exit 0; }
            sleep 10
          done
          echo "${name} ${version} not visible after 5 minutes"; exit 1
          EOF
          chmod +x "${RUNNER_TEMP}/publish_one.sh"

      # Each package gets a fresh OIDC token: the wait for propagation could outlive one.
      - uses: dart-lang/setup-dart@<sha> # v1
      - run: ${RUNNER_TEMP}/publish_one.sh packages/ravelstone_pay_platform_interface ravelstone_pay_platform_interface "${GITHUB_REF_NAME#v}"

      - uses: dart-lang/setup-dart@<sha> # v1
      - run: ${RUNNER_TEMP}/publish_one.sh packages/ravelstone_pay_ios ravelstone_pay_ios "${GITHUB_REF_NAME#v}"

      - uses: dart-lang/setup-dart@<sha> # v1
      - run: ${RUNNER_TEMP}/publish_one.sh packages/ravelstone_pay_android ravelstone_pay_android "${GITHUB_REF_NAME#v}"

      - uses: dart-lang/setup-dart@<sha> # v1
      - run: ${RUNNER_TEMP}/publish_one.sh packages/ravelstone_pay ravelstone_pay "${GITHUB_REF_NAME#v}"
```

- The publish job re-checks out the tag's commit. The tag ruleset forbids moving tags, so build and publish see the same source.
- The helper skips any version pub.dev already holds. A rerun after a partial failure therefore finishes the release instead of failing on package one.
- Never delete the packages that made it. A partial release rolls forward.
- Flutter plugins need the Flutter SDK, and `dart-lang/setup-dart` only fetches the OIDC token. The `setup-dart` plus `flutter pub publish --force` combination is the documented route, but validate it on the first automated release.
- If `setup-dart` does not expose the token to Flutter's pub, check the `setup-dart` README for the current mechanism.

### Repository setup (one-time, owner)

1. **Tag ruleset** on `v[0-9]*`:
   - Block create, update and delete for everyone.
   - Bypass list: the release GitHub App and org owners.
2. **GitHub App** `ravelstone-release`, installed on this repo only:
   - Permissions: Contents write, Pull requests write, Metadata read.
   - Store `RELEASE_APP_ID` as a variable and the private key as a secret, both in the `cut-release` environment.
3. **Environment `cut-release`:**
   - Deployment branches: `main` only.
   - No reviewers.
4. **Environment `release`:**
   - Required reviewers: team `release-approvers`.
   - Deployment tags: `v[0-9]*`.
   - No secrets.
5. **Branch ruleset on `main`:** required review, so the release-bump PR needs a human approval.
6. **PM access:** PMs need permission to run workflows.
   - A write role does it.
   - Custom repository roles on Enterprise Cloud can narrow it.
   - Add `.github/workflows/**` and `**/pubspec.yaml` to CODEOWNERS. Otherwise write access lets someone rewrite the pipeline.
7. **pub.dev Admin tab, on each of the four packages:**
   - Enable publishing from GitHub Actions.
   - Repository `<org>/<repo>`.
   - Tag pattern `v{{version}}`.
   - Required environment `release`.

## 4. First release (manual, engineer, once)

Run these in your own terminal. They publish publicly and cannot be undone. Do them in order, and dry-run each package after the previous one is live, because dependents cannot resolve earlier.

```sh
cd packages/ravelstone_pay_platform_interface
flutter pub publish --dry-run
flutter pub publish        # publishes
```

Repeat for `ravelstone_pay_ios`, `ravelstone_pay_android`, then `ravelstone_pay`.

Then, on each package's Admin tab:
1. Transfer the package to the verified publisher. This is irreversible.
2. Configure the automated-publishing settings from §3.

Tag nothing for this first release. The first PM-driven release is the next version.

### PM runbook (every release after that)

1. Actions tab, then **cut-release**, then **Run workflow** on `main`.
2. Enter the version and a one-line note.
3. Wait for the **release** run on the new tag, and ask someone in `release-approvers` to approve it.
4. After the run succeeds, approve and merge the "chore(release)" PR.

To abort, ask a repo owner to delete the tag. Rejecting the approval leaves the tag in place.

## 5. Rollback runbook

pub.dev permits retraction only within 7 days of publishing, and you can undo a retraction within 7 days. Past 7 days, only a fix works. Run these yourself. Nothing here has a safe dry run.

1. **Publish the fix first.** Press the button with the next patch version, for example `1.4.1`, and put "fixes 1.4.0" in the note.
2. **Retract all four bad versions** on each package's Admin tab. Retract all four together.
   - If you retract only the interface, the app-facing `1.4.0` can no longer resolve its `^1.4.0` constraint.
   - Resolvers skip retracted versions unless they are already locked.
   - pub.dev has no message field, so name the safe version in the CHANGELOG and the GitHub release note.
3. **If compromise is suspected**, isolate the runners first.
   - Revoke and rotate the GitHub App private key.
   - Check that the `release` environment reviewers and the tag ruleset are unchanged.
   - Past 7 days, contact pub.dev support.
4. **A dead package** gets marked "discontinued" with its replacement named.
5. Announce in the changelog and your security advisory channel.

Rehearse the retract and republish steps on a private pub repository (Artifactory or a hosted pub service). pub.dev has no scratch registry. Until then, mark this runbook not rehearsed.

## 6. Private consumption

None. A public pub.dev package cannot depend on internal git or hosted packages, so there is nothing to map or probe. The dependency-confusion probe does not apply.

The native SDK coordinates (`RavelstonePay` on trunk and the Maven Central artifact) are checked read-only against their public registries in the `build` job.

## 7. Migration sequence

| When | Step | Evidence it leaves |
|---|---|---|
| By 2026-10-27 | Answer D1, D2 and D3. Fill in the Maven `GROUP` and `ARTIFACT`. | Decision note in the repo |
| Before 2026-11-01 | If the plugin needs a new native iOS SDK, push it to trunk and run `pod trunk deprecate RavelstonePay` with a README pointing at SwiftPM, once D1 is settled. | Trunk listing |
| Week of 2026-10-27 | Create the verified publisher. Manually publish the 4 packages (§4) and transfer them. Set up the repo and pub.dev (§3). | pub.dev versions page, ruleset and environment screenshots |
| Week of 2026-11-02 | Merge both workflows. The first PM-driven release is the first full pipeline test. | Green `release` run, four live versions |
| By 2026-12-02 | Ship the SwiftPM path for iOS if D1 was "yes". Do not push to trunk from CI. | `Package.swift` merged |

## 8. Measurement gates

| Gate | Status |
|---|---|
| Zero long-lived publish tokens | ✅ by design: no pub.dev secret, and the App key can only push a tag |
| Every publish runs from CI on a protected tag | ✅ after the manual first release |
| Written rollback primitive, rehearsed | ⚠️ written, not rehearsed (no private pub repository named) |
| Binary checksums and attestations | ℹ️ not applicable (source packages only) |
| Internal names resolve internally | ℹ️ not applicable |
| One-token-for-four-packages (D3) and the Flutter plus `setup-dart` OIDC combination | ⚠️ unverified until the first automated release |

I did not run any publish, push or registry command.