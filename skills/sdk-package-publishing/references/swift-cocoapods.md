# Swift Package Manager and CocoaPods

## Contents

- Library vs binary
- CI auto-publishing
- Swift Package Manager: releases, binary targets, registries
- CocoaPods: the trunk read-only plan, until then, private spec repos
- Private consumption
- Dated changes

Default to Swift Package Manager (SwiftPM) for every new Apple SDK. CocoaPods trunk stops accepting new pods and versions on 2026-12-02.

## Library vs binary

- **Source library:** a git repository with a root `Package.swift`; a SemVer tag is the release.
- **Closed-source or prebuilt SDK:** a code-signed XCFramework, zipped, attached to the release, declared as `.binaryTarget(name:url:checksum:)`. Compute the checksum with `swift package compute-checksum CorpSDK.xcframework.zip`.
- **Command-line tool:** an `executable` product, built per architecture (`swift build -c release --arch arm64 --arch x86_64` for a universal macOS binary), signed and notarized, shipped as release assets or through a Homebrew tap. See the binary section of release-workflow.md.

## CI auto-publishing

- **Public SwiftPM:** no upload and no publish credential. The protected tag is the release, as on Go: restrict who may create `[0-9]*` tags.
- **Binary target:** the tagged commit must already carry the final `url` and `checksum`, and XCFramework zips are not byte-reproducible. Hand the zip between runs through a draft release:
  1. On the release branch, in its own protected environment with `contents: write` and the signing identity: build, sign, compute the checksum, and create a draft release `1.4.2` with the zip attached.
  2. Commit `Package.swift` with that checksum and the final asset URL (`.../releases/download/1.4.2/CorpSDK.xcframework.zip`).
  3. Tag that commit. Add `[0-9]*` to the workflow trigger, the tag ruleset and the environment rule, or plain SemVer tags never start the tag job.
  4. In the tag job: download the draft's asset, verify its checksum against `Package.swift`, then publish the draft. Never rebuild.
- **Provenance:** attest the XCFramework zip (`actions/attest`) and code-sign it with the Apple Distribution identity; Xcode checks the signature of signed XCFrameworks.
- **Registry publish** (private registries): `swift package-registry publish corp.sdk 1.4.2 --signing-identity "<identity>"` with a registry token from the secret store.
- **CocoaPods trunk** (until 2026-12-02): no OIDC. `pod trunk push CorpSDK.podspec` with `COCOAPODS_TRUNK_TOKEN` from a bot account's trunk session, stored in the publish environment.

## Swift Package Manager

**Releases**

- Tag plain SemVer (`1.4.2`). Never move or delete a tag: `Package.resolved` pins the commit for each version, and a moved tag breaks every resolved checkout.
- List the package on the Swift Package Index: submit the repository URL through its add-a-package form. The index builds DocC documentation when the repository carries a `.spi.yml`.
- A binary-target URL must stay valid forever. Never replace an uploaded asset: a new zip changes the checksum and breaks every consumer of that version.

**Registries (SE-0292)**

- Registry publishing and package signing (SE-0391) are implemented by private registries such as AWS CodeArtifact and Artifactory. Public discovery still goes through git URLs.
- Configure clients per scope: `swift package-registry set --scope corp https://swift.internal.example.com`, stored in `.swiftpm/configuration/registries.json`.

## CocoaPods

**The trunk read-only plan**

- 2026-11-01 to 2026-11-07: a temporary read-only test run, to expose automation that still pushes to trunk.
- 2026-12-02: trunk permanently stops accepting new pods and new versions.
- Existing pods keep installing from the CDN. Private spec repos and vendored pods are unaffected.

**What to do**

1. Ship a SwiftPM package for every pod-distributed SDK now.
2. Publish the last trunk version and run `pod trunk deprecate CorpSDK` before the 2026-11-01 test run, with a README and release note pointing CocoaPods users to the SwiftPM package. `--in-favor-of` only accepts another pod name. Assume no trunk write works after the cutoff, deprecate included.
3. Delete trunk push steps from CI after the cutoff; they fail from then on.
4. Keep the podspec in the repository only for private spec repos or React Native and Flutter plugin consumers that read it locally.

**Until the cutoff**

- Preflight with `pod lib lint` (working tree) and `pod spec lint` (the podspec as published). `pod trunk push` lints again and aborts on errors.
- `prepare_command` is disallowed in trunk podspecs since 2025-05.
- Removal before the cutoff: deprecate. `pod trunk delete` exists but breaks every Podfile.lock pinning that version. After it, roll back through a SwiftPM tag and a README notice.

## Private consumption

- SwiftPM over git: private repositories with SSH keys or a `.netrc` rendered from the secret store in CI. A git URL names one host, so there is no cross-registry confusion for declared dependencies.
- SwiftPM over a registry: one scope per internal namespace (`corp.*`) mapped to the internal registry.
- CocoaPods: CocoaPods takes a pod from the first `source` that contains it. List the private spec repo first, then the CDN explicitly, and prefix internal pod names:

```ruby
source 'https://github.com/corp/private-specs.git'
source 'https://cdn.cocoapods.org/'
```

- Push internal pods with `pod repo push corp-specs CorpAuth.podspec`; the read-only plan never affects private spec repos.

## Dated changes

- 2025-05: `prepare_command` disallowed on trunk.
- 2026-11-01 to 2026-11-07: trunk read-only test run.
- 2026-12-02: trunk permanently read-only.
