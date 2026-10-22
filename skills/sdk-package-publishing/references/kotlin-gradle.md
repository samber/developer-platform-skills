# Kotlin and Gradle (Maven Central, Kotlin Multiplatform, Gradle Plugin Portal)

## Contents

- Library vs binary
- CI auto-publishing to Maven Central from Gradle
- Kotlin Multiplatform
- Gradle Plugin Portal
- Dated changes

Gradle builds publish libraries to Maven Central; Java projects built with Gradle use this file too. Namespace proof, signing, POM rules, cost tiers and immutability come from maven-central.md; load both files.

## Library vs binary

- **Library:** jar or AAR (Android) on Maven Central; Kotlin Multiplatform adds one artifact per target.
- **JVM application:** jlink runtime images, jpackage installers (`deb`, `rpm`, `msi`, `dmg`, `pkg`) or GraalVM native images. None cross-compiles: build on a runner per OS. JReleaser assembles and publishes them to GitHub releases, Homebrew, SDKMAN, Scoop, winget and JBang catalogs.
- **Kotlin/Native executable:** built per host OS, shipped as release assets.
- **Gradle plugin:** the Gradle Plugin Portal, below.

## CI auto-publishing to Maven Central from Gradle

- **Trigger:** a protected `v*` tag. Pipeline shape: release-workflow.md.
- Sonatype ships no official Gradle plugin. Use a community plugin, which Sonatype does not support:
  - `com.vanniktech.maven.publish`: `publishToMavenCentral()` plus `signAllPublications()`; handles KMP and Android.
  - `nmcp` (GradleUp): uploads existing Gradle publications through the Portal API.
  - JReleaser: deploys a staged repository and also releases applications.
- Keep the validate-then-publish gate: upload without automatic release, then a maintainer publishes in the Portal. With vanniktech, run `publishToMavenCentral` (not `publishAndReleaseToMavenCentral`) and leave automatic release off.
- **Signing runs in-build:** `signAllPublications()` signs inside the Gradle run, which executes every plugin. Run tests in the unprivileged build job and give only the publish job the signing subkey, with an expiry and a rotation date.
- **No OIDC.** Secrets in the protected `release` environment: `ORG_GRADLE_PROJECT_mavenCentralUsername` and `ORG_GRADLE_PROJECT_mavenCentralPassword` (the Portal token pair), and `ORG_GRADLE_PROJECT_signingInMemoryKey` with `ORG_GRADLE_PROJECT_signingInMemoryKeyPassword`. Plain Gradle `signing` uses `useInMemoryPgpKeys()`.
- Run publish with `--no-configuration-cache` when the plugin requires it, and with no restored Gradle caches in the publish job.

## Kotlin Multiplatform

- One release produces a root publication (`com.corp:sdk`, Gradle module metadata pointing at every target) plus per-target artifacts (`sdk-jvm`, `sdk-android`, `sdk-iosarm64`, `sdk-js`).
- Apple targets build only on macOS. Publish every target from one macOS runner: Central rejects duplicates, and two hosts each publish the root publication.
- iOS apps that do not use Kotlin consume an XCFramework through Swift Package Manager (swift-cocoapods.md), released alongside the Central artifacts.

## Gradle Plugin Portal

- **Plugin ID:** `io.github.<user>.<plugin>`, or `com.<domain>.<plugin>` with domain ownership proved by a DNS TXT record. `com.github.*` IDs are rejected. Plugin ID and group must share the top-level namespace.
- **First release:** a human reviews the first version, which takes days. Submit well before launch; changing the ID or group restarts the review. SNAPSHOT versions are refused.
- **Publish:** apply `com.gradle.plugin-publish`, run `./gradlew publishPlugins --validate-only` in the build job, then `publishPlugins` in the publish job.
- **Credential:** no OIDC. `GRADLE_PUBLISH_KEY` and `GRADLE_PUBLISH_SECRET` from the profile's API keys, stored in the `release` environment, owned by a bot account. Rotate them on a schedule.
- Treat every published version as permanent and roll forward with a new one.
- Declare configuration-cache compatibility; the Portal surfaces it to users.

## Dated changes

- 2025-06-30: OSSRH shut down; Gradle builds must target the Central Portal.
