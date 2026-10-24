# Release workflow for the four `ravelstone_pay` packages

I haven't run this workflow or checked it against your repo. Your directory layout, the native SDK coordinates, and the exact pub.dev OIDC behavior for Flutter packages are assumptions. The assumptions are marked `# ASSUMPTION` in the file and listed at the end.

## Blocker: the first release can't be a button

pub.dev only lets you enable "Publish from GitHub Actions" on a package that already exists. Nothing is on pub.dev yet, so an engineer has to publish `0.1.0` of all four packages by hand, once. After that, the button handles every later release.

### One-time bootstrap (engineer, about 20 min)

1. Make sure the committed pubspecs use hosted version constraints between your own packages. Publishing rejects `path:` deps. Use a gitignored `pubspec_overrides.yaml` for local development.
2. From a clean checkout, run `dart pub publish --dry-run` in `ravelstone_pay_platform_interface` and fix any warnings. The other three packages can't pass a dry run until `platform_interface` is live.
3. Publish in this order, waiting about a minute between packages so pub.dev indexes each one: `ravelstone_pay_platform_interface`, then `ravelstone_pay_ios`, then `ravelstone_pay_android`, then `ravelstone_pay`.
4. Move all four packages to a verified publisher. On each package page, go to Admin → Transfer to publisher.
5. For each package, go to Admin → Automated publishing → Enable publishing from GitHub Actions.
   - Set the repository to `<org>/<repo>`.
   - Tick "Require GitHub Actions environment" and enter `pub-dev`.
   - Leave the tag-pattern option off. `workflow_dispatch` publishing needs the environment instead.
6. In GitHub, go to Settings → Environments → New environment and name it `pub-dev`.
   - Under deployment branches, allow `main` only.
   - Add no required reviewers, because that would put an engineer back in the loop.
   - Add a branch ruleset so only engineers can push to `main`. This is the real control over what a PM can release.

## `.github/workflows/release-pub-dev.yml`

```yaml
name: Release to pub.dev

on:
  workflow_dispatch:
    inputs:
      confirm_version:
        description: "Type the ravelstone_pay version you are releasing (must match its pubspec.yaml)"
        required: true
        type: string
      dry_run:
        description: "Dry run: validate everything, publish nothing"
        required: true
        type: boolean
        default: true

# Two releases at once would race on pub.dev; never cancel one mid-publish.
concurrency:
  group: pub-dev-release
  cancel-in-progress: false

permissions:
  contents: read

env:
  # Dependency order: each package may only depend on those listed before it.
  PACKAGES: "ravelstone_pay_platform_interface ravelstone_pay_ios ravelstone_pay_android ravelstone_pay"
  PACKAGES_DIR: packages # ASSUMPTION: packages live in packages/<name>
  # 10 polls x 30 s: pub.dev indexing normally takes seconds, this is slack.
  POLL_ATTEMPTS: 10
  POLL_SLEEP_S: 30

jobs:
  verify:
    name: Verify
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          channel: stable
          cache: true

      - name: Versions must be consistent and confirmed
        run: |
          set -euo pipefail
          version_of() { awk '/^version:/ {print $2; exit}' "$PACKAGES_DIR/$1/pubspec.yaml"; }
          main_version=$(version_of ravelstone_pay)
          if [ -z "$main_version" ]; then echo "::error::no version in ravelstone_pay/pubspec.yaml"; exit 1; fi
          if [ "$main_version" != "${{ inputs.confirm_version }}" ]; then
            echo "::error::You typed '${{ inputs.confirm_version }}' but ravelstone_pay is at '$main_version'. Nothing was published."
            exit 1
          fi
          {
            echo "### Versions to release"
            for p in $PACKAGES; do echo "- \`$p\` $(version_of "$p")"; done
          } >> "$GITHUB_STEP_SUMMARY"

      - name: Committed pubspecs must not contain path deps or overrides
        run: |
          set -euo pipefail
          # pub publish rejects path deps; overrides would hide a broken constraint.
          if /usr/bin/grep -nE '^\s+path:|^dependency_overrides:' "$PACKAGES_DIR"/*/pubspec.yaml; then
            echo "::error::path dependency or dependency_overrides committed in a pubspec.yaml"
            exit 1
          fi

      - name: At least one package must be unpublished
        run: |
          set -euo pipefail
          todo=0
          for p in $PACKAGES; do
            v=$(awk '/^version:/ {print $2; exit}' "$PACKAGES_DIR/$p/pubspec.yaml")
            code=$(curl -s -o /dev/null -w '%{http_code}' "https://pub.dev/api/packages/$p/versions/$v")
            case "$code" in
              200) echo "$p $v already on pub.dev" ;;
              404) echo "$p $v to publish"; todo=$((todo + 1)) ;;
              *)   echo "::error::unexpected HTTP $code from pub.dev for $p $v"; exit 1 ;;
            esac
          done
          if [ "$todo" -eq 0 ]; then
            echo "::error::every version is already on pub.dev. Bump versions in a PR first."
            exit 1
          fi

      - name: Native SDK versions must exist upstream
        run: |
          set -euo pipefail
          # ASSUMPTION: exact pins, e.g. s.dependency 'RavelstonePay', '3.2.1'
          pod=$(grep -hoE "dependency\s+'RavelstonePay',\s*'[^']+'" "$PACKAGES_DIR"/ravelstone_pay_ios/ios/*.podspec | grep -oE "[0-9][0-9A-Za-z.+-]*" | tail -1)
          # ASSUMPTION: implementation 'com.ravelstone:pay:1.2.3' (replace group:artifact)
          aar=$(grep -hoE "com\.ravelstone:pay:[0-9][^'\"]*" "$PACKAGES_DIR"/ravelstone_pay_android/android/build.gradle* | head -1 | cut -d: -f3)
          [ -n "$pod" ] && [ -n "$aar" ] || { echo "::error::could not read native SDK pins (pod='$pod' aar='$aar')"; exit 1; }

          curl -sf https://trunk.cocoapods.org/api/v1/pods/RavelstonePay \
            | jq -e --arg v "$pod" '.versions[] | select(.name == $v)' > /dev/null \
            || { echo "::error::RavelstonePay $pod not on CocoaPods trunk"; exit 1; }

          code=$(curl -s -o /dev/null -w '%{http_code}' \
            "https://repo1.maven.org/maven2/com/ravelstone/pay/$aar/pay-$aar.pom")
          [ "$code" = "200" ] || { echo "::error::com.ravelstone:pay:$aar not on Maven Central (HTTP $code)"; exit 1; }
          echo "iOS SDK $pod and Android SDK $aar found upstream" >> "$GITHUB_STEP_SUMMARY"

      - name: Publish dry run (platform_interface has no in-repo deps)
        working-directory: packages/ravelstone_pay_platform_interface
        run: |
          flutter pub get
          dart pub publish --dry-run

      - name: Analyze and test all packages against local siblings
        run: |
          set -euo pipefail
          for p in $PACKAGES; do
            (
              cd "$PACKAGES_DIR/$p"
              # Dependents cannot resolve unpublished siblings from pub.dev, so point them at the checkout.
              {
                echo "dependency_overrides:"
                for q in $PACKAGES; do [ "$q" != "$p" ] && echo "  $q: {path: ../$q}"; done
              } > pubspec_overrides.yaml
              flutter pub get
              flutter analyze
              if [ -d test ]; then flutter test; fi
            )
          done

  publish:
    name: Publish
    needs: verify
    if: ${{ !inputs.dry_run }}
    runs-on: ubuntu-latest
    timeout-minutes: 60
    environment: pub-dev # must match the environment name set on pub.dev
    permissions:
      id-token: write # OIDC token pub.dev exchanges for upload rights
      contents: write # push release tags
    steps:
      - uses: actions/checkout@v4

      # setup-dart configures the OIDC token for pub; flutter-action then puts Flutter's Dart first on PATH.
      - uses: dart-lang/setup-dart@v1
      - uses: subosito/flutter-action@v2
        with:
          channel: stable
          cache: true

      - name: Publish in dependency order
        run: |
          set -euo pipefail
          api() { curl -s -o /dev/null -w '%{http_code}' "https://pub.dev/api/packages/$1/versions/$2"; }

          for p in $PACKAGES; do
            v=$(awk '/^version:/ {print $2; exit}' "$PACKAGES_DIR/$p/pubspec.yaml")
            case "$(api "$p" "$v")" in
              200) echo "skip $p $v (already published)"; continue ;;
              404) ;;
              *)   echo "::error::unexpected pub.dev response for $p $v"; exit 1 ;;
            esac

            echo "::group::publish $p $v"
            (
              cd "$PACKAGES_DIR/$p"
              # A just-published sibling may not be resolvable for a moment; retry.
              ok=0
              for i in $(seq "$POLL_ATTEMPTS"); do
                if flutter pub get; then ok=1; break; fi
                echo "pub get failed (attempt $i), sibling not indexed yet?"; sleep "$POLL_SLEEP_S"
              done
              [ "$ok" = 1 ] || { echo "::error::pub get never succeeded for $p"; exit 1; }
              flutter pub publish --force
            )
            echo "::endgroup::"

            # Dependents resolve against pub.dev, so wait until this version is visible.
            seen=0
            for i in $(seq "$POLL_ATTEMPTS"); do
              if [ "$(api "$p" "$v")" = "200" ]; then seen=1; break; fi
              sleep "$POLL_SLEEP_S"
            done
            [ "$seen" = 1 ] || { echo "::error::$p $v not visible on pub.dev after publish"; exit 1; }

            git tag "$p-v$v"
            git push origin "$p-v$v"
            echo "- published \`$p\` $v" >> "$GITHUB_STEP_SUMMARY"
          done
```

## How a product manager releases

1. An engineer merges a PR to `main` that bumps versions and updates the changelogs.
2. The PM opens Actions → Release to pub.dev → Run workflow on `main`.
3. The PM types the `ravelstone_pay` version and leaves **dry_run** ticked. The `verify` job runs and nothing is published.
4. If it's green, the PM runs it again with **dry_run** unticked.
5. If a run dies halfway, the PM re-runs it. Versions already on pub.dev are skipped, so the re-run resumes where it stopped.

## Why it's built this way

- **Dry run is the default.** A publish can't be undone. pub.dev only allows retracting a version within 7 days, and a retracted version is never deleted.
- **Branch and environment gate.** The `publish` job only runs from `main` through the `pub-dev` environment, so the PM can't ship an unmerged branch.
- **Confirmation input.** Typing the version stops a PM from releasing the wrong state of `main`.
- **Native SDK check.** It fails the run before publishing if the pinned iOS or Android SDK isn't on CocoaPods trunk or Maven Central. Otherwise the Flutter plugin would ship pointing at a native SDK that can't be resolved.
- **HTTP status checks.** The pub.dev checks accept only an exact `200` or `404`. Any other status fails the run, so a network error can't be read as "not published yet".
- **Resumable publishing.** It publishes in dependency order and waits for each package to appear on pub.dev before starting the next. The skip-if-published check makes partial failures safe to re-run.

## Assumptions to check against your repo

- **Layout and tags.** Packages live in `packages/<name>/`. The tag format `<package>-v<version>` is my choice.
- **Native pins.** The iOS and Android SDKs are pinned to exact versions in `ravelstone_pay_ios/ios/*.podspec` and `ravelstone_pay_android/android/build.gradle*`. The Maven coordinate `com.ravelstone:pay` is a placeholder, so replace it with the real group and artifact. If you use ranges such as `~> 3.2`, change the regex or pin exactly.
- **Federation.** `ravelstone_pay` endorses `_ios` and `_android` in its pubspec, and both depend on `_platform_interface`.
- **Flutter and OIDC.** I believe `dart-lang/setup-dart` followed by `flutter pub publish --force` picks up the OIDC token, but I couldn't confirm it. If the first real publish fails with an auth error, switch the publish step to `dart pub publish --force`. Flutter's Dart is already on `PATH` at that point.
- **`workflow_dispatch` publishing.** pub.dev supports it only when a GitHub environment is required on the package. I'm fairly sure of this, but check pub.dev's "Automated publishing" docs before relying on it.
- **Version drift.** The `confirm_version` check only covers `ravelstone_pay`. The other three versions are published as committed. Add a consistency check if you want all four versions identical.