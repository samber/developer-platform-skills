**Next action:** remove `"version": "3.2.0"` from `composer.json`. It is the likely reason fixes don't reach Packagist.

There are 4 problems. Fix them in this order. I didn't run anything against your repos or Packagist, so verify the two flagged claims below.

## 1. Moved tag, stale Packagist (🔴)

- Packagist keeps the first commit it saw for a tag. A moved `v3.2.0` is not re-imported.
- Moved tags also break users. Their `composer.lock` pins the old commit hash, and a fresh install gets different code under the same version.
- Do not move tags again. Ship the hotfix as `v3.2.1`.

**Remove the hard-coded `version` first.**

- Composer and Packagist read the version from the tag. A hard-coded `version` overrides it.
- ⚠️ I recall Packagist skipping tags whose name differs from the `version` field. The message reads like "Skipped tag v3.2.1, tag (3.2.1) does not match version (3.2.0) in composer.json". Check the package's update log to confirm.
- If that is true, the v3.2.1 tag would be silently skipped while `version` is still there.
- Also, `3.2.0` in the field is the same stale value, so it hides every real version.

Steps:

1. Delete the `version` line from `composer.json`, commit, and push.
2. Make sure the hotfix commit includes that removal.
3. Run `git tag v3.2.1 <hotfix-sha> && git push origin v3.2.1`.
4. Trigger the sync, or press "Update" on the Packagist package page.
5. Check the new tag:
   - Run `git rev-parse v3.2.1^{commit}`.
   - Run `composer show -a thornfield/sdk` in a clean temp dir and compare the source reference.
6. Tell consumers to run `composer update thornfield/sdk`.

If you must fix `3.2.0` itself, a maintainer can delete that version on the Packagist package page and trigger an update to re-import it. ⚠️ Anyone who locked the old `3.2.0` still has the old hash. I advise against this.

## 2. CI uses your main API token (🔐)

- The main token acts as you on every package you maintain.
- If the sync passes it as `?apiToken=` in the URL, it probably sits in CI logs and proxy logs.
- ⚠️ Treat the main token as leaked.

Steps:

1. Rotate the main token in your Packagist profile. This kills the old one.
2. Create the "safe" API token. Packagist offers a limited token that can only call update-package.
3. Store the safe token as a CI secret, masked.
4. Send it in a header, not the URL. Check the current Packagist docs for the exact `Authorization` format.
5. Better: drop the CI step. Install the Packagist GitHub hook or webhook so a tag push triggers the update itself.

## 3. Satis `canonical: false` (🟠)

- With `canonical: false`, Composer also searches packagist.org for `thornfield/internal-auth`.
- It then picks the highest version across both repos. If anyone publishes that name or a higher version on Packagist, installs pull attacker code. This is dependency confusion.
- The contractor hid the symptom. Installs were failing for a different reason, most likely missing auth for Satis, a missing version in the Satis build, or Satis listed after Packagist.

Steps:

1. Remove `canonical: false`. The default is `true`.
2. Use repository filters (Composer 2.6 or later) so each package has one source:

```json
{
  "repositories": [
    {
      "type": "composer",
      "url": "https://satis.thornfield.example",
      "only": ["thornfield/internal-*"]
    },
    {
      "type": "composer",
      "url": "https://repo.packagist.org",
      "exclude": ["thornfield/internal-*"]
    }
  ]
}
```

   If your Composer is older, remove the filter keys and rely on `canonical: true` with Satis listed first.

3. Find why installs failed. Run `composer update thornfield/internal-auth -vvv` and read the repository lines.
   - If you see 401 or 403, add credentials to `auth.json` (`http-basic`).
   - If you see "no matching version", rebuild Satis so it contains the needed tags.
4. Reserve or claim `thornfield/internal-auth` on Packagist if the name is free. This stops anyone else squatting it.
5. Check `composer.lock` files that were generated while `canonical` was `false`. Run `composer show -s thornfield/internal-auth` and confirm the dist URL points at Satis, not packagist.org.

## 4. After the fixes

- No `version` key in any `composer.json` that is tagged from VCS.
- Run `composer validate --strict` in CI. It warns about the `version` field.
- Releases come only from new tags. Never move or force-push a tag.
- Add a CI guard: fail if the tag already exists on origin with a different commit.

**Time:** about 20 minutes for steps 1 and 2 (the `version` removal, `v3.2.1` tag, and token rotation). About 30 to 60 minutes for the Satis root cause.

**Next:** do the `version` removal and the token rotation first. Both are quick, and the token is the live security risk.