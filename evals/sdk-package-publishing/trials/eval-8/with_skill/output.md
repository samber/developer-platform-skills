# Ashgrove Robotics: publishing plan for `com.ashgrove:robotics-sdk` and the Gradle plugin

Nothing here has been run. I read `sdk-package-publishing` and its `kotlin-gradle.md`, `maven-central.md`, `swift-cocoapods.md` and `release-workflow.md` references. I prepared the commands and left every publish, release and drop for you to run.

## Answer for the iOS team

They consume the SDK as a Swift package. A Swift package is a prebuilt `AshgroveRobotics.xcframework` attached to a GitHub release and referenced from a `Package.swift`. They never see Gradle or Kotlin.

1. In Xcode, choose File ▸ Add Package Dependencies and enter `https://github.com/ashgrove/robotics-sdk`.
2. Pick "Exact Version" `1.0.0`.
3. Add `import AshgroveRobotics` to their Swift files.

If they use a `Package.swift`, they add this dependency:

```swift
.package(url: "https://github.com/ashgrove/robotics-sdk", exact: "1.0.0")
```

Do not ship CocoaPods. CocoaPods trunk has a read-only test run from 2026-11-01 to 2026-11-07 and stops accepting new pods on 2026-12-02. A pod published now would be dead within six weeks.

The `com.ashgrove:robotics-sdk-iosarm64` artifacts on Maven Central are Kotlin klibs. They are useless to a Swift-only team, which is why the XCFramework exists.

## Five things in your plan that need to change

| # | Your plan | Problem | Fix |
|---|---|---|---|
| 1 | Plugin ID `com.github.ashgrove.robotics` | The Plugin Portal rejects `com.github.*` IDs. Changing the ID later restarts the human review. | Use `com.ashgrove.robotics`, proved with a DNS TXT record on the domain. The alternative is `io.github.<user>.<plugin>`. The plugin's Gradle group must be `com.ashgrove`. |
| 2 | Ubuntu publishes jvm/android/js and macOS publishes iOS, both on tag | Two hosts each publish the root KMP publication, and Central rejects duplicates. Apple targets only build on macOS. | One macOS runner publishes every target. Ubuntu only runs tests. |
| 3 | `publishAndReleaseToMavenCentral` | Central releases are immutable and there is no undo. Auto-release removes the only inspection point. | Run `publishToMavenCentral` and leave auto-release off. A maintainer inspects the validated deployment in the Portal, then publishes or drops it. |
| 4 | Plugin Portal listing, launch in five days | The first version gets a human review that takes days. | Submit the plugin version this weekend. Do not make the launch depend on it (see the fallback below). |
| 5 | Nothing about cost | Since 2026-10-01, Maven Central requires the paid Publisher Pro tier for commercial-nature artifacts. That includes service-dependent SDKs, drivers and integrations, open source or not. | If the SDK talks to an Ashgrove service or robot fleet, procurement must act today. |

## 1. Assumptions and inventory

Nobody was available to answer the interview, so these are my assumptions. Correct any that are wrong.

- CI is GitHub Actions on hosted runners.
- The repo is `github.com/ashgrove/robotics-sdk` and is public. If it is private, the SwiftPM binary-target download needs auth. Tell me and I will change the approach.
- Ashgrove owns `ashgrove.com`, so DNS TXT proof is possible.
- The SDK is tied to a commercial product, so Publisher Pro applies.
- No private feed is involved, so there is no private-consumption work.
- This is a standing release process, not a one-off.
- Launch is 2026-10-28, five days from today (2026-10-23).
- Nothing is published yet. Every credential is new and must be created.

| Artifact | Registry or channel | Publish path | Credential | Expiry | Owners | Target model |
|---|---|---|---|---|---|---|
| `com.ashgrove:robotics-sdk` (root plus `-jvm`, `-android`, `-iosarm64`, `-iossimulatorarm64`, `-js`) | Maven Central, via the Central Portal | CI on tag `X.Y.Z`, macOS job | Portal user token pair plus a PGP signing subkey | Token: set one, calendar the rotation. Subkey: set one. | Sonatype namespace `com.ashgrove`, 2 owners | Static token in a protected environment, manual Portal release |
| `AshgroveRobotics.xcframework.zip` | GitHub release asset plus SwiftPM binary target | Signing job, then the tag job publishes the draft release | Apple Distribution identity, `GITHUB_TOKEN` with `contents: write` | Certificate expiry | GitHub org owners | Tag is the release |
| `com.ashgrove.robotics` Gradle plugin | Gradle Plugin Portal | CI on tag `gradle-plugin/vX.Y.Z` | `GRADLE_PUBLISH_KEY` and `GRADLE_PUBLISH_SECRET` from a bot profile | Rotate on a schedule | Portal profile, 2 owners | Static key, no OIDC exists |

Neither Maven Central nor the Plugin Portal offers OIDC. Both use the narrowest token available, owned by a bot account, stored in a protected environment and rotated on a schedule.

## 2. Per-registry decisions

**Maven Central**
- **Namespace:** `com.ashgrove`, proved with a DNS TXT record on `ashgrove.com`. Do this today. The Portal is not instant.
- **Plugin:** `com.vanniktech.maven.publish` with `publishToMavenCentral()` and `signAllPublications()`. Do not enable automatic release.
- **Signing:** use a dedicated PGP subkey with an expiry. Keep its passphrase separate and publish the public key to a keyserver.
- **Publisher Pro:** confirm the tier and its per-namespace terms with procurement before anything else.
- **Preflight:** a real upload to the Portal that stays VALIDATED and is then dropped.

**Library versus binary.** Library: Maven Central, one root publication plus per-target artifacts. Binary: the XCFramework, which is an Apple binary rather than a Kotlin library. The Android AAR and jar need no extra channel.

**Version and channel policy**
- Use SemVer.
- Tag the SDK as plain `1.0.0`, the form SwiftPM requires. The `v`-prefixed `v*` pattern in the reference skeleton cannot be used here.
- Tag the plugin as `gradle-plugin/v0.1.0`. This is the monorepo `<package>/vX.Y.Z` form from the reference.
- A CI guard fails the run if the tag differs from `version=` in `gradle.properties` (or the plugin's version).
- Pre-releases use SemVer suffixes such as `1.0.0-rc.1`.
- Every published version is permanent.

**Tag ruleset.** Only release managers may create tags matching `[0-9]*` or `gradle-plugin/v*`. For SwiftPM, this rule is the publish credential. The workflow triggers, the ruleset and the environment rule must list the same patterns.

**Swift distribution**
- A code-signed XCFramework zip, declared as a `.binaryTarget(url:checksum:)` in a root `Package.swift`.
- Keep the Gradle repo as the Swift package repo. A thin separate repo is cleaner but adds a cross-repo handoff you do not have time for before launch.
- You list only `iosArm64` and `iosSimulatorArm64`. The XCFramework therefore has no Intel-simulator slice, and iOS app developers on Intel Macs cannot run it in the simulator. Say so in the README, or add `iosX64`.
- Never move or delete a tag. Never replace an uploaded asset.
- Submit the repo to the Swift Package Index after the first tag.
- Skip CocoaPods entirely.

**Gradle Plugin Portal**
- Apply `com.gradle.plugin-publish`.
- Run `publishPlugins --validate-only` in the build job.
- Declare configuration-cache compatibility.
- The first version gets human review. Submit it now.
- **Fallback if review has not finished by launch:** launch the SDK without the plugin and document the plugin as "coming soon". If the plugin must ship, publishing it to Maven Central and resolving it through `pluginManagement` repositories is a possible workaround. That is outside the skill's references, so check Gradle's docs before relying on it.
- If the plugin depends on the SDK, wait until the SDK resolves publicly on Central before publishing the plugin.

**Hardening, all workflows**
- Pin every action to a full commit SHA.
- Set `permissions: {}` by default.
- Restore no caches in the test or publish jobs. This costs minutes. The saving is to run macOS only for iOS tests and publish. If the repo is private, macOS minutes bill at a higher multiple than Linux.
- Use no `pull_request_target` or `workflow_run` triggers.
- The `release` environment needs a reviewer team, or at least two people besides whoever cuts releases. Any one approves, and self-review is blocked.

## 3. Pipeline files (drafts pending your approval)

`<sha>` marks an action to pin. Resolve it with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`. Do not invent SHAs.

### `build.gradle.kts` (relevant parts)

```kotlin
kotlin {
    jvm(); androidTarget(); js(IR) { browser(); nodejs() }
    val xcf = XCFramework("AshgroveRobotics")
    listOf(iosArm64(), iosSimulatorArm64()).forEach { target ->
        target.binaries.framework {
            baseName = "AshgroveRobotics"
            isStatic = true
            xcf.add(this)
        }
    }
}

mavenPublishing {
    publishToMavenCentral()   // no automaticRelease: a maintainer publishes in the Portal
    signAllPublications()
    coordinates("com.ashgrove", "robotics-sdk", version.toString())
    pom { /* name, description, url, licenses, developers, scm are mandatory */ }
}
```

Check the XCFramework assemble task name with `./gradlew tasks --all`. I expect `assembleAshgroveRoboticsReleaseXCFramework`, but I did not verify it.

### `.github/workflows/xcframework-draft.yml`

This builds, signs and drafts the release. It runs from the release branch before you tag.

```yaml
name: xcframework-draft
on:
  workflow_dispatch:
    inputs: { version: { required: true } }
permissions: {}
jobs:
  draft:
    runs-on: macos-latest
    environment: apple-signing        # own environment: signing identity plus contents:write
    permissions: { contents: write }
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - uses: actions/setup-java@<sha>
        with: { distribution: temurin, java-version: "21" }
      - run: ./gradlew --no-daemon assembleAshgroveRoboticsReleaseXCFramework
      - name: Sign, zip, checksum, draft release
        env:
          GH_TOKEN: ${{ github.token }}
          VERSION: ${{ inputs.version }}
          # APPLE_SIGNING_IDENTITY and keychain import: from the apple-signing environment
        run: |
          # TODO(draft): import cert into a temp keychain, then
          # codesign --timestamp -s "$APPLE_SIGNING_IDENTITY" build/XCFrameworks/release/AshgroveRobotics.xcframework
          ditto -c -k --sequesterRsrc --keepParent \
            build/XCFrameworks/release/AshgroveRobotics.xcframework AshgroveRobotics.xcframework.zip
          swift package compute-checksum AshgroveRobotics.xcframework.zip | tee checksum.txt
          gh release create "$VERSION" --draft --title "$VERSION" \
            --repo "$GITHUB_REPOSITORY" AshgroveRobotics.xcframework.zip
```

A maintainer then commits `Package.swift` with this checksum and the final asset URL, and tags that commit as `1.0.0`:

```swift
// swift-tools-version:5.9
import PackageDescription
let package = Package(
    name: "AshgroveRobotics",
    platforms: [.iOS(.v15)],   // placeholder: set your real minimum
    products: [.library(name: "AshgroveRobotics", targets: ["AshgroveRobotics"])],
    targets: [.binaryTarget(
        name: "AshgroveRobotics",
        url: "https://github.com/ashgrove/robotics-sdk/releases/download/1.0.0/AshgroveRobotics.xcframework.zip",
        checksum: "<output of swift package compute-checksum>")]
)
```

### `.github/workflows/release.yml` (SDK, tag `X.Y.Z`)

```yaml
name: release
on:
  push:
    tags: ["[0-9]*"]
permissions: {}
jobs:
  test-linux:                          # cheap: jvm, android unit, js
    runs-on: ubuntu-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>   # v6
        with: { persist-credentials: false }
      - name: Tag must equal gradle.properties version
        run: |
          version="$(sed -n 's/^version=//p' gradle.properties)"
          [ "$GITHUB_REF_NAME" = "$version" ] || { echo "tag $GITHUB_REF_NAME != version $version"; exit 1; }
      - uses: actions/setup-java@<sha> # v5
        with: { distribution: temurin, java-version: "21" }
      - run: ./gradlew --no-daemon jvmTest jsTest testDebugUnitTest

  test-apple:
    runs-on: macos-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: actions/setup-java@<sha>
        with: { distribution: temurin, java-version: "21" }
      - run: ./gradlew --no-daemon iosSimulatorArm64Test

  publish-maven:                       # the ONLY job that publishes any KMP target
    needs: [test-linux, test-apple]
    runs-on: macos-latest              # Apple targets build only here
    environment: release               # reviewers approve here
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: actions/setup-java@<sha>
        with: { distribution: temurin, java-version: "21" }
      - name: Upload to Central Portal (validated, NOT released)
        env:
          ORG_GRADLE_PROJECT_mavenCentralUsername: ${{ secrets.CENTRAL_TOKEN_USER }}
          ORG_GRADLE_PROJECT_mavenCentralPassword: ${{ secrets.CENTRAL_TOKEN_PASS }}
          ORG_GRADLE_PROJECT_signingInMemoryKey: ${{ secrets.SIGNING_SUBKEY }}
          ORG_GRADLE_PROJECT_signingInMemoryKeyPassword: ${{ secrets.SIGNING_SUBKEY_PASSPHRASE }}
        run: ./gradlew --no-daemon --no-configuration-cache publishToMavenCentral

  publish-swift:                       # tag is the release; publish the draft prepared earlier
    needs: [test-linux, test-apple]
    runs-on: ubuntu-latest
    environment: release
    permissions: { contents: write }
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - name: Draft asset must match Package.swift, then publish; never rebuild
        env: { GH_TOKEN: "${{ github.token }}" }
        run: |
          gh release download "$GITHUB_REF_NAME" -p AshgroveRobotics.xcframework.zip
          got="$(shasum -a 256 AshgroveRobotics.xcframework.zip | cut -d' ' -f1)"
          grep -q "checksum: \"$got\"" Package.swift || { echo "checksum mismatch"; exit 1; }
          gh release edit "$GITHUB_REF_NAME" --draft=false
```

Between the tag push and the draft being published, the asset URL returns 404 and SwiftPM resolution of that version fails. The approval gate keeps that window short.

### `.github/workflows/release-plugin.yml` (tag `gradle-plugin/vX.Y.Z`)

```yaml
name: release-plugin
on:
  push:
    tags: ["gradle-plugin/v*"]
permissions: {}
jobs:
  validate:
    runs-on: ubuntu-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: actions/setup-java@<sha>
        with: { distribution: temurin, java-version: "21" }
      - run: ./gradlew --no-daemon :gradle-plugin:check :gradle-plugin:publishPlugins --validate-only
  publish:
    needs: validate
    runs-on: ubuntu-latest
    environment: release-plugin        # separate environment: different secret set
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: actions/setup-java@<sha>
        with: { distribution: temurin, java-version: "21" }
      - env:
          GRADLE_PUBLISH_KEY: ${{ secrets.GRADLE_PUBLISH_KEY }}
          GRADLE_PUBLISH_SECRET: ${{ secrets.GRADLE_PUBLISH_SECRET }}
        run: ./gradlew --no-daemon :gradle-plugin:publishPlugins
```

The Gradle publish jobs rebuild while publishing. Treat them as privileged build code behind the environment gate, and run no tests in them. The publish jobs install nothing beyond the Gradle toolchain.

## 4. Rollback runbook

All commands below are for you to run. Nothing in them has a safe dry-run form, so do not append `--dry-run` to any removal.

**Maven Central**
1. Publish a fixed version as a new tag. Do not wait on any removal.
2. A bad released version cannot be removed. Announce the fix in the changelog and release notes.
3. A bad deployment that has not been published can be dropped in the Portal only while it is VALIDATED or FAILED.
4. If a secret leaked or malware shipped, contact Sonatype support, the only party who can remove a component.
5. If compromise is suspected, first isolate the build hosts, then revoke and rotate the Portal token pair and the signing subkey.

**SwiftPM**
1. Tag a fixed release.
2. Never move or delete a tag, and never replace an asset. `Package.resolved` pins the commit, and a replaced zip changes the checksum and breaks every consumer of that version.
3. Add a README and release-notes notice pointing users to the fixed version.

**Gradle Plugin Portal**
1. Treat every published version as permanent.
2. Roll forward with a new version.
3. Rotate `GRADLE_PUBLISH_KEY` and `GRADLE_PUBLISH_SECRET` if the release job might have exposed them.

**Rehearsal, before 2026-10-28**
- **Maven Central:** do one real upload that you inspect and then drop in the Portal. Never rehearse by releasing.
- **SwiftPM:** use a scratch repository with a throwaway binary target.
- **Plugin Portal:** run `publishPlugins --validate-only`. A public rehearsal would burn a version forever.

## 5. Private consumption

Not applicable. You named no private feed, so there are no internal names to protect from dependency confusion. If you add one later, I will extend the plan.

## 6. Migration sequence

Launch is Wednesday 2026-10-28. The plugin's first-release human review and Publisher Pro are the two long poles.

| When | Action | Evidence it leaves |
|---|---|---|
| **Fri 10-23 (today)** | Raise Publisher Pro with procurement. Add the DNS TXT records for the Maven namespace and the Plugin Portal ID. Create bot accounts for Sonatype and the Plugin Portal. Make sure there are 2 owners with phishing-resistant 2FA on each. | Purchase confirmation, DNS records, owner list |
| **Fri-Sat 10-23/24** | Generate the PGP signing subkey, set an expiry, and publish the public key to a keyserver. Create the Portal token pair with an expiry. Create the Plugin Portal key and secret. Put all of them in the protected environments, never in repository secrets. | Secret-store entries (names only), rotation dates on the calendar |
| **Sat 10-24** | Set the plugin ID to `com.ashgrove.robotics` and the group to `com.ashgrove`. Merge the Gradle changes. Add the tag ruleset and environments. Pin the action SHAs. | Merged PR, ruleset screenshot |
| **Sat-Sun 10-24/25** | Tag `gradle-plugin/v0.1.0` and approve the release so the Plugin Portal review starts. The version is permanent. | Review submitted, timestamp recorded |
| **Mon 10-26** | Rehearse Maven Central: upload, inspect, drop. Rehearse the XCFramework draft flow on a scratch repo. Have a real iOS developer add the package to a sample app. | Dropped deployment, resolved sample app |
| **Tue 10-27** | Dry run of the full SDK flow up to, but not including, the release click. Decide go or no-go on the plugin. If review is incomplete, use the fallback. | Go/no-go note |
| **Wed 10-28 (launch)** | Run the draft workflow, commit `Package.swift`, tag `1.0.0`, approve the `release` environment. A maintainer clicks Publish in the Portal. Publish the GitHub draft release. Submit the repo to the Swift Package Index. | Central coordinates resolving, SwiftPM resolving, release notes |
| **After launch** | Calendar token rotation and subkey expiry. Remove any CocoaPods mention from docs. | Rotation dates |

When tokens are ready, send them to the secret store only. If you paste one into chat, I will ask you to revoke it.

**Open questions that change this plan**
1. Is the SDK tied to an Ashgrove service or product? This decides Publisher Pro.
2. Do you own `ashgrove.com`, so DNS proof works?
3. Is the repository public?
4. Do you need an Intel-simulator slice (`iosX64`)?
5. Does the plugin depend on the SDK artifact?