**Short answer:** it depends on one thing. Does your podspec pin a hash, and was 2.4.0 already pushed to trunk before the re-upload? I can't see your workflow or podspec, so this comes from how CocoaPods behaves, not from your repo.

## What CocoaPods does

- Trunk podspecs are immutable. Pushing an existing version again is rejected.
- A binary pod's podspec points at your GitHub release URL, for example `s.source = { :http => ".../2.4.0/BirchwaterKit.xcframework.zip" }`. CocoaPods downloads the zip from there at install time. Trunk never stores it.
- Re-uploading over the same asset therefore changes what every future `pod install` of 2.4.0 downloads.

## Three cases

| Situation | What happens | Action |
|---|---|---|
| **A. 2.4.0 not yet pushed to trunk** (push is a later step, or you hadn't run it) | Nothing is broken. | Push now. If the podspec has a `:sha256` or `:sha1`, make sure it holds the **new** zip's hash. |
| **B. Already pushed, podspec has no hash** | Installs fetch the rebuilt zip and work. Machines that cached the bad zip keep it. | Nothing on trunk. Tell affected users to run `pod cache clean BirchwaterKit --all`, or to delete the pod cache entry, then reinstall. |
| **C. Already pushed, podspec pins a hash of the old zip** | Every fresh install of 2.4.0 fails with a checksum mismatch. You can't fix this in place. | Ship **2.4.1** with the correct zip and hash. Optionally run `pod trunk deprecate` on 2.4.0 only if your trunk version supports it. Don't use `pod trunk delete`, because it removes the whole pod. |

## What to do now

1. Hash the current release asset: `shasum -a 256 BirchwaterKit.xcframework.zip`.
2. Compare it with what trunk serves: `pod spec cat BirchwaterKit --version=2.4.0`. Check the `source` URL and any `:sha256` or `:sha1`.
3. Pick case A, B or C from that comparison.
4. In every case, run a clean `pod install` in a throwaway project to confirm 2.4.0 resolves. Use `pod cache clean --all` first so you don't test against a cached copy.

## SwiftPM has the same problem, and your workflow makes it worse

- Your workflow commits the checksum to `Package.swift` on main after tagging. The `2.4.0` tag therefore points at a commit with a stale or placeholder checksum, unless the tag is moved.
- The re-upload changed the zip, so any checksum recorded earlier no longer matches it.
- Clients that already resolved 2.4.0 hold the old checksum in `Package.resolved` and SwiftPM's cache. They will see checksum errors.
- The clean fix is also **2.4.1**. It is safer than moving the tag or re-uploading assets.

## Prevention

- Never overwrite a release asset. Always bump the version, because trunk and SwiftPM both treat versions as immutable.
- Reorder the workflow to: build, compute the checksum, commit it and tag that commit, upload the asset, then push to trunk. This way no consumer can see a version whose hash doesn't match.
- Add a CI step that downloads the published asset and checks its hash against both the podspec and `Package.swift` before `pod trunk push`.

If you tell me whether the podspec has a hash and whether the trunk push already ran, I can say which case you're in.