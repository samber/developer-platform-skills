# React Native libraries

## Contents

- Library vs app
- Package shape: JS, iOS, Android, codegen
- CI auto-publishing
- Native dependencies and prebuilt binaries
- Private publishing and consumption
- Dated changes

A React Native library is an npm package that carries JavaScript plus native iOS and Android sources. npm.md covers the registry mechanics; this file covers what the package must contain and how its native halves release.

## Library vs app

- **Library:** published to npm; the consuming app builds its native code.
- **App:** ships to the App Store and Google Play. Store submission is outside this skill.
- **Native SDK wrapped by the library:** released separately, as a SwiftPM package or pod (swift-cocoapods.md) and an Android artifact on Maven Central (maven-central.md, kotlin-gradle.md), then pinned by the library.

## Package shape

- Scaffold with `create-react-native-library` and build with `react-native-builder-bob` (`module`, `typescript`, `codegen` targets) in `prepare`.
- `files` must include `src`, `lib`, `android`, `ios`, `cpp` when used, the root `*.podspec`, `react-native.config.js` when used, and `app.plugin.js` for an Expo config plugin. Exclude `android/build`, `ios/build`, `example` and every `.gradle` cache. Check with `npm pack --dry-run`.
- **iOS autolinking** reads the podspec at the package root. A scoped npm name needs a podspec name without `/`.
- **Android autolinking** reads the library's Gradle module through the React Native Gradle plugin.
- **Swift Package Manager:** experimental in React Native 0.87, planned default in 0.89. Ship a `Package.swift` beside the podspec (`npx react-native spm scaffold` generates one) once you support 0.87+; it is experimental, so regenerate it on each React Native release.
- **New Architecture:** the only architecture since 0.82. Ship the Turbo Module or Fabric spec files and `codegenConfig` in `package.json` (`name`, `type`, `jsSrcsDir`, `android.javaPackageName`); the app build runs codegen. Shipping pre-generated code ties it to the React Native version that generated it: test it against every version you claim.
- Declare `react` and `react-native` as `peerDependencies` with the range you test in CI, never as dependencies.

## CI auto-publishing

- Publish the npm package with npm trusted publishing and staged approval, from the two-job skeleton in release-workflow.md. The scaffold's Release It setup uses tokens: replace its publish step with `npm stage publish`.
- Release order when the native SDK moves too: native SDK first (Maven Central, SwiftPM tag), wait until it resolves publicly, then the npm package pinning the exact native versions in its podspec, `Package.swift` and `build.gradle`.
- Build the example app on iOS and Android in the build job before publishing: a JS-only check misses broken autolinking.

## Native dependencies and prebuilt binaries

- Prebuilt iOS code: an XCFramework through `vendored_frameworks` in the podspec, and a `binaryTarget` in `Package.swift`.
- Prebuilt Android code: depend on the AAR from Maven Central (`implementation "com.corp:sdk-android:1.4.2"`) instead of committing binaries to the npm package.
- After 2026-12-02 CocoaPods trunk accepts no new versions. A pod dependency of your library freezes there; plan its move to SwiftPM or vendored XCFrameworks.
- **Expo:** the Expo Modules API is an alternative to Turbo Modules; it needs the `expo` package. Native setup the app needs (permissions, Info.plist keys) belongs in a config plugin, `app.plugin.js`.

## Private publishing and consumption

- The JS package uses a private npm scope (npm.md). Native halves use a private spec repo, a private SwiftPM git URL or registry scope, and a private Maven repository.
- Consumers' CI needs read credentials for all three ecosystems, each from the secret store.

## Dated changes

- 2024-10-23: React Native 0.76, New Architecture default.
- 2025-10-08: React Native 0.82, New Architecture only.
- 2026-08-11: React Native 0.87, experimental Swift Package Manager.
- 2026-10-19: React Native 0.88; 0.89 planned to make Swift Package Manager the default.
