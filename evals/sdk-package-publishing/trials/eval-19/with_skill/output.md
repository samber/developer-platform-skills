# CocoaPods: what to do about the 2.4.0 re-upload

**Yes, act on CocoaPods, but not by repairing 2.4.0.** Ship 2.4.1 everywhere. The CocoaPods end date matters more than the re-upload: trunk goes read-only soon.

I took the mechanics from the `sdk-package-publishing` skill's SwiftPM and CocoaPods reference. I did not check your repo, podspec or trunk state.

## 1. The 2.4.0 re-upload

- **The asset is already burned.** A binary-target URL must keep the same bytes forever. Replacing the zip changed its checksum, so every consumer that pinned 2.4.0 now breaks.
- **SwiftPM is probably also broken, and it is the worse problem.** Your workflow tags first and commits the checksum to `main` afterwards. The 2.4.0 tag therefore carries a stale or placeholder checksum.
- **Don't move or delete the 2.4.0 tag.** `Package.resolved` pins its commit.
- **CocoaPods and the replaced zip.** Trunk keeps the 2.4.0 podspec immutably, but its source URL now serves the rebuilt zip.
  - If the podspec has no `:sha256` or `:sha1` on its http source, new installs get the good zip. Machines with the old zip in their pod cache keep the bad one.
  - If the podspec has a hash, every fresh install of 2.4.0 fails on a mismatch.
- **Don't run `pod trunk delete`.** It breaks every `Podfile.lock` that pins 2.4.0.
- **Roll forward.** Release 2.4.1 from a rebuild and leave 2.4.0 alone. Name 2.4.1 as the fix in the changelog and the release notes.

## 2. Two facts I need from you

1. Did 2.4.0 reach trunk before the rebuild, and was that before or after you replaced the asset?
2. Does `BirchwaterKit.podspec` pin a hash on its source?

Commands that only read:

```sh
pod trunk info BirchwaterKit
pod spec cat BirchwaterKit --version=2.4.0
curl -sL <2.4.0 asset URL> | shasum -a 256    # compare with the hash in the spec, if any
```

## 3. Trunk is ending, so "as long as it works" has a date

| Date | Event |
|---|---|
| 2026-11-01 to 11-07 | Read-only test run. Pushes may fail. Starts in 9 days. |
| 2026-12-02 | Trunk permanently stops accepting new pods and new versions. |

Existing versions keep installing from the CDN.

Plan:

1. **Release 2.4.1 to trunk and SwiftPM before 2026-11-01.** This is your last reliable trunk version.
2. **Deprecate the pod before 2026-11-01.** Add a README and release note that point CocoaPods users to the SwiftPM package. Assume no trunk write works after the cutoff, deprecate included. Hand this command to the person who owns the trunk account: `pod trunk deprecate BirchwaterKit`. `--in-favor-of` only accepts another pod name, so don't use it.
3. **Keep pushing until then.** Make the trunk step the last, separate job, so a failure there never blocks the SwiftPM release. Remove the job after 2026-12-02. Don't count on it working during the 11-01 to 11-07 window.
4. **Keep the podspec in the repo** only if a private spec repo or a React Native or Flutter plugin still reads it. Private spec repos are unaffected by the shutdown.

## 4. Fix the workflow so this can't recur

The SwiftPM binary-target flow in the skill is:

1. In a protected environment, build and sign the XCFramework and compute its checksum with `swift package compute-checksum`. Create a **draft** release `2.4.1` with the zip attached.
2. Commit `Package.swift` with the final asset URL and that checksum.
3. Tag that commit. Make the workflow trigger, the tag ruleset and the environment rule all list `[0-9]*` patterns.
4. In the tag job, download the draft's asset and verify its checksum against `Package.swift`. Publish the draft. **Never rebuild.**
5. After the release is published, run `pod trunk push BirchwaterKit.podspec` with a bot account's `COCOAPODS_TRUNK_TOKEN`, stored in the publish environment. Run `pod spec lint` first as a preflight.

Also:

- Turn on GitHub immutable releases so a published asset can't be replaced.
- Let the trunk push be the only step that holds the trunk token.
- Restrict who can create `[0-9]*` tags, because the tag is the SwiftPM release.

## 5. Order of operations

1. Answer the two questions in section 2. About 10 minutes.
2. Fix the workflow to the draft-first flow.
3. Release 2.4.1 and verify a fresh SwiftPM resolve and a `pod install`.
4. Run the `pod trunk deprecate` command, with the README and release note, before 2026-11-01.
5. Remove the trunk step after 2026-12-02.

I ran no publish, deprecate or delete command. Those are yours to run.