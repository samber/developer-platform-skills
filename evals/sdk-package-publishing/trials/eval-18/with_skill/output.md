**Time-critical.** `--revert` works only within 1 hour of publishing. You published 35 minutes ago, so about 25 minutes remain. Run step 3 below first.

I ran nothing, and I did not use the key.

## Two things I did not do

1. **No dry run of `--revert`.** `mix hex.publish --revert 1.4.3 --dry-run` is not a dry run on any released Hex. Hex ignores `--dry-run` on `--revert` and deletes the release immediately. Only the unreleased Hex 2.6 rejects the flag. I will not give you that command.
2. **No real revert from me.** Removal is public and permanent, so you run the command.

## 1. Revoke the pasted key now (2 min)

`hex_c9f2…` now sits in this chat. Treat it as leaked.

1. Run `mix hex.user key list`.
2. Run `mix hex.user key revoke <key-name>` for the key you pasted.
3. Run `mix hex.user key revoke --all` if you are unsure which one it was. Then generate a new key for CI.

## 2. Preview the revert without deleting anything (1 min)

Run these two commands. Both are read-only:

```sh
mix hex.info wrenfield_sdk 1.4.3
mix hex.package fetch wrenfield_sdk 1.4.3 --unpack --output /tmp/wrenfield_sdk-1.4.3
```

- The first confirms the version exists and shows its publish time. Check that the time is under 1 hour ago.
- The second lets you confirm the checksum file is missing from the tarball, so you know you are reverting the right release.

## 3. Real revert (you run it)

```sh
mix hex.publish --revert 1.4.3
```

What it does:

- It deletes `wrenfield_sdk` 1.4.3 from hex.pm and hexdocs.pm.
- It cannot be undone.
- Anyone who already resolved 1.4.3 will fail to fetch it. That is fine, because nobody can compile it anyway.

If the window has closed, do not retry. Retire the version instead:

```sh
mix hex.retire wrenfield_sdk 1.4.3 invalid --message "Broken NIF checksum file. Use 1.4.4"
```

Retired versions still resolve, but with a warning.

## 4. Roll forward with 1.4.4 (do not wait on the revert)

1. Regenerate the checksum file: `mix rustler_precompiled.download <Module> --all --print`.
2. Confirm the checksum file is listed in `files` in `mix.exs`. This is the likely root cause.
3. Run `mix hex.build`. Unpack the tarball and confirm the checksum file is inside.
4. Run `mix hex.publish --dry-run`. This is a safe preflight for a normal publish.
5. In a scratch project, compile with `{:wrenfield_sdk, path: "..."}` from the built tarball.
6. Bump to 1.4.4 and publish through CI, or hand me the command.

Add a CI guard that fails the release when the checksum file is absent from `mix hex.build` output.

## 5. Your CI credential is the real problem

You say CI uses your personal user key, stored with `mix hex.organization auth`. That setup has two problems:

- **It breaks soon.** Hex 2.6 stops accepting user-owned keys stored that way. Organization-owned keys are unaffected.
- **It is too broad.** A personal key carries all your permissions, and a leak means a full account takeover.

Replace it:

- **Organization package:**
  `mix hex.organization key wrenfield generate --key-name ci-publish --permission api:write`
- **Public package:** create a bot account with 2FA, and generate a key with the narrowest permission.
- **Storage:** put it in a protected `release` environment as `HEX_API_KEY`. Do not use a repository secret.
- **Pipeline:** build with `mix hex.build` in an unprivileged job. Publish with `mix hex.publish --yes` in a separate job behind the `release` environment, on a protected `v*` tag only. The skeleton is in `references/release-workflow.md`.
- **Rotation:** set a short expiry and rotate it on a schedule.

Also keep at least two owners with level `full` on the package.

## 6. OIDC like the PyPI team: not possible yet

Hex has no trusted publishing in any released version. Workload identity for GitHub Actions is in Hex 2.6 development only. PyPI has it. Hex does not.

- **Now:** do step 5 and make that key the only one.
- **When Hex 2.6 ships:** read the Hex changelog first. Then configure the trusted publisher on the package, give the publish job `id-token: write`, and revoke the key.
- **Reminder:** set a recurring check on the Hex release page. Tell me when it ships and I will write the workflow.

## Order of work

1. Revoke the leaked key (2 min).
2. Run `mix hex.info wrenfield_sdk 1.4.3` and check the publish time (1 min).
3. Run `mix hex.publish --revert 1.4.3` (1 min).
4. Fix and release 1.4.4 (about 30 min).
5. Rotate CI to a bot or organization key (about 15 min).

**Next:** run step 1 now. Then paste the output of `mix hex.info wrenfield_sdk 1.4.3` here, so I can confirm the window is still open.