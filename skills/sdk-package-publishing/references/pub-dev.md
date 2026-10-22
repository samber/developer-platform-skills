# pub.dev (Dart and Flutter)

## Contents

- Library vs binary
- CI auto-publishing
- Public publishing: namespace, package shape, versions, removal
- Flutter plugins
- Private publishing and consumption
- Dated changes

## Library vs binary

- **Library:** a source package on pub.dev. Pub builds nothing at publish time.
- **Dart CLI tool:** the same package plus `executables:` in `pubspec.yaml`, mapping each command to `bin/<script>.dart`. Users install it with `dart install <package>` (Dart 3.10+; `dart pub global activate` is the legacy path); both need the Dart SDK.
- **Standalone binary:** `dart compile exe` on a runner per OS. Cross-compilation targets Linux only (Dart 3.8+), so macOS and Windows binaries need their own runners. Ship them as release assets (see the binary section of release-workflow.md), never as a pub.dev package.
- **Flutter apps** ship to app stores. Store submission is outside this skill.

## CI auto-publishing

- **Trigger:** a tag push only; pipeline shape in release-workflow.md. pub.dev refuses automated publishes from `workflow_dispatch`, branch pushes or any other event.
- **First version:** publish it manually with `dart pub publish` from a maintainer session. Automated publishing only covers packages that already exist.
- **Setup (GitHub Actions, OIDC):**
  1. On the package's Admin tab, enable publishing from GitHub Actions: repository `org/repo` and a tag pattern containing `{{version}}` (`v{{version}}`, or `<package>-v{{version}}` in a monorepo; add that pattern to the workflow's tag filter and the tag ruleset).
  2. Require a GitHub environment there and give it required reviewers. Any name works (`release` keeps it consistent with release-workflow.md) as long as pub.dev and the job match.
  3. Call the reusable workflow `dart-lang/setup-dart/.github/workflows/publish.yml@<sha>` with `permissions: id-token: write` and the environment name as input.
- `dart pub publish` always archives the checked-out source, so no build artifact passes from build to publish. Run tests in the build job, and keep the publish job free of project scripts: `dart-lang/setup-dart@<sha>` (it fetches the OIDC token), then `dart pub publish --force`.
- Flutter packages and plugins need the Flutter SDK: add `subosito/flutter-action@<sha>` after `setup-dart` and run `flutter pub publish --force`. Validate it on the first automated release.
- **No GitHub:** enable publishing with a Google Cloud service account on the Admin tab and publish from Google Cloud Build. Other CI can impersonate that service account through Workload Identity Federation, never an exported key; pub.dev does not document that route, so validate it on a non-critical package first. Anyone who can impersonate the service account is a publisher.
- **Provenance:** pub.dev accepts no attestation upload. Attest compiled CLI binaries on the GitHub release instead.

## Public publishing

**Namespace**

- Names are flat and first-come. Create a verified publisher for the company domain (domain proof through Google Search Console) and transfer packages to it before the first release.
- A transfer to a publisher is irreversible, and every member of the publisher gets upload rights. Keep membership to release owners.

**Package shape**

- Preflight with `dart pub publish --dry-run` (or `flutter pub publish --dry-run`). Recommended maximums: 100 MB gzipped, 256 MB uncompressed.
- Everything not hidden and not matched by `.gitignore` or `.pubignore` ships. A `.pubignore` replaces `.gitignore` for that directory, so repeat its secret patterns.
- pub.dev rejects packages that depend on git or custom-hosted packages: a public SDK cannot pull an internal package.
- Check the pana score before release; it grades documentation, platform support, static analysis, dependency freshness and Swift Package Manager support for iOS and macOS plugins.

**Versions**

- SemVer with pre-release suffixes (`2.0.0-beta.1`). Consumers reach a pre-release only through a constraint that names one (`^2.0.0-beta.1`).

**Removal**

- Retract a version within 7 days of publishing; a retraction can itself be undone within 7 days. Resolvers skip retracted versions unless already locked.
- Past 7 days nothing removes a version: publish a fix. Mark a dead package "discontinued" and name its replacement.

## Flutter plugins

- A federated plugin splits into an app-facing package (`corp_sdk`), a platform interface (`corp_sdk_platform_interface`) and one implementation per platform (`corp_sdk_android`, `corp_sdk_ios`, `corp_sdk_web`).
- Endorse an implementation with `default_package` under `flutter.plugin.platforms.<os>` in the app-facing pubspec, plus a normal dependency on it. Non-endorsed implementations need the user to add them.
- Publish in dependency order: platform interface, then implementations, then the app-facing package.
- Change the platform interface additively, with default implementations. A breaking interface change breaks every implementation at once, including third-party ones.
- iOS and macOS: ship a `Package.swift` under `ios/<name>/` (Swift Package Manager is the default from Flutter 3.44) and keep the podspec until Flutter drops CocoaPods. The podspec is consumed from the pub package, never pushed to CocoaPods trunk, so the trunk read-only date does not block plugin releases.
- Native dependencies of the plugin itself (a vendor iOS or Android SDK) follow swift-cocoapods.md and maven-central.md. A podspec `dependency` on a trunk pod freezes at that pod's last trunk version after 2026-12-02: vendor the XCFramework in the podspec, or serve the pod from a private spec repo, and depend on the SwiftPM package in `Package.swift`.

## Private publishing and consumption

- Hosts implementing the pub repository spec include Artifactory and several hosted pub services. Set `publish_to: https://pub.internal.example.com` in every private package, so a stray `dart pub publish` cannot reach pub.dev; set `publish_to: none` on apps.
- Authenticate with `dart pub token add https://pub.internal.example.com --env-var PUB_INTERNAL_TOKEN`; the token stays in the CI secret store.
- Each internal dependency names its host, and pub fetches it only from there:

```yaml
dependencies:
  corp_auth:
    hosted: https://pub.internal.example.com
    version: ^1.4.0
```

- A dependency without `hosted:` resolves from pub.dev, or from `PUB_HOSTED_URL` when set. Declare the host on every internal package, transitive ones included, or point `PUB_HOSTED_URL` at a virtual repository that blocks internal names upstream.

## Dated changes

- Dart 3.8: `dart compile exe` cross-compiles to Linux.
- Dart 3.10: `dart install`; `dart pub global` labelled legacy.
- Flutter 3.44: Swift Package Manager default for iOS and macOS plugins; CocoaPods in maintenance mode.
