I couldn't run anything. This machine has no `mix`/Elixir, and there is no `wrenfield_sdk` checkout under the current directory. I used the key nowhere. Below is what to run from the SDK repo, and one trap to check first.

## 1. The revert has a time limit

Hex only allows `--revert` for about 60 minutes after publish. You are 35 minutes in, so you have roughly 25 minutes left. If you miss it, use `mix hex.retire` (step 4).

## 2. Check `--dry-run` before relying on it

`mix help hex.publish` documents `--dry-run` as "builds the package and runs local checks without publishing". I'm not sure the revert path honors it, and I couldn't check here. If it ignores the flag, the "dry run" is the real revert.

Read the help text first:

```bash
mix help hex.publish | grep -iE -A2 'revert|dry-run'
```

For a dry run that is safe either way, read the release state:

```bash
export HEX_API_KEY=...   # your key
mix hex.info wrenfield_sdk 1.4.3
mix hex.info wrenfield_sdk
```

This shows whether 1.4.3 is the latest release. If it is the only release, a revert removes the whole package. It should show 1.4.3 and the publish time, which lets you confirm you're inside the window.

## 3. The real revert

```bash
export HEX_API_KEY=...   # your key
mix hex.publish --revert 1.4.3   # **deletes the release from hex.pm**
```

- The revert **deletes the release** and is not reversible.
- Don't pass the key on the command line. Keep it in the environment variable.
- Fix the NIF checksum file, then publish as **1.4.4**. Don't assume 1.4.3 can be reused.
- Before publishing, run `mix hex.build --unpack` and confirm the checksum file is in the tarball. Add that check to CI.

## 4. If the window has closed

Retire the release instead. This doesn't delete it, but it shows a warning and discourages new resolution:

```bash
mix hex.retire wrenfield_sdk 1.4.3 other --message "Broken NIF checksum file, use 1.4.4"
```

## 5. Rotate the key you pasted

The key is now in this conversation and the transcript. Treat it as exposed and revoke it after the revert:

```bash
mix hex.user key list
mix hex.user key revoke <key-name>
```

Also, `mix hex.organization auth` stores an organization key, not a personal user key. If CI uses a personal key for `HEX_API_KEY`, that key carries your full publish rights.

## 6. OIDC like PyPI

I can't confirm that Hex supports OIDC trusted publishing. I know of no equivalent to PyPI's feature as of my knowledge. Check hex.pm's docs and the `hexpm/hexpm` GitHub issues before planning around it.

If it isn't available, the closest setup is:

1. Generate a dedicated CI key with the minimum permission and a clear name:
   `mix hex.user key generate --key-name wrenfield-ci --permission api:write`
2. Store it as a GitHub Actions secret in a protected environment with required reviewers.
3. Publish only from tag pushes on protected branches.
4. Rotate the key on a schedule, and immediately after any exposure like this one.

If OIDC does exist, I can help wire up the workflow once you point me at the CI repo.