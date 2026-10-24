# Fix `nuget.config` for Pellucid Health: source mapping and `%FEED_TOKEN%`

I followed `sdk-package-publishing` and `references/nuget.md` (Private consumption) plus the probe in `references/release-workflow.md`. I did not run any commands against your feed or nuget.org.

## Root causes

1. **"First source wins" is false.** NuGet ignores source order during restore. Any listed source can serve any package ID, and NuGet picks the best version match across sources. A public `Pellucid.Core.Common` 9.0.0 on nuget.org beats your internal 8.x, so one developer restored it. This is dependency confusion.
2. **`$FEED_TOKEN` never resolves.** NuGet expands only `%VAR%`, on every OS. On Linux the literal string `$FEED_TOKEN` goes out as the password, so you get a 401. Windows builds probably pass because a credential provider or cached credential covers for the broken value. That is my inference, so check the Windows agent. It is not proof of a working config.

## Fixed `nuget.config` (commit this; it holds no secret)

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <!-- Drop machine-level sources so nothing else can serve a Pellucid.* ID -->
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="pellucid" value="https://pkgs.dev.azure.com/<ORG>/<PROJECT>/_packaging/<FEED>/nuget/v3/index.json" />
  </packageSources>

  <packageSourceMapping>
    <!-- Most specific pattern wins: Pellucid.Core.* beats * -->
    <packageSource key="pellucid">
      <package pattern="Pellucid.Core.*" />
    </packageSource>
    <packageSource key="nuget.org">
      <package pattern="*" />
    </packageSource>
  </packageSourceMapping>

  <packageSourceCredentials>
    <pellucid>
      <add key="Username" value="ci" />
      <!-- %VAR% syntax resolves on every OS; $VAR never does -->
      <add key="ClearTextPassword" value="%FEED_TOKEN%" />
    </pellucid>
  </packageSourceCredentials>
</configuration>
```

- **Mapping scope:**
  - `*` on nuget.org also covers other `Pellucid.*` names such as `Pellucid.Foo`.
  - If any internal package falls outside `Pellucid.Core.*`, add its own pattern under `pellucid`. Map transitive internal names too.
  - Broaden to `Pellucid.*` if every `Pellucid.*` ID is internal.
- **`ClearTextPassword`:** Linux has no DPAPI, so the encrypted `Password` form is not usable there.
- **Username:** Azure Artifacts accepts any non-empty value with a PAT, so `ci` is fine.
- **Local developers:** keep the interactive Azure Artifacts Credential Provider. Do not give them a shared token.

## Linux agent token

- Create a read-only PAT, scope Packaging (Read), owned by a bot account with the shortest workable expiry.
- Store it as a secret named `FEED_TOKEN`, only for jobs that restore.
- Never paste the token into chat or commit it. If it has been pasted anywhere, revoke it.
- On Azure Pipelines you can skip the PAT and run the `NuGetAuthenticate@1` task before restore. It injects the job's identity credentials.
- Keep the read-only credential separate from any publish identity.

## The rogue public `Pellucid.Core.Common` 9.0.0

Do these four steps, in order:

1. **Don't trust anything built from it.**
   - Find the developer's build outputs and any artifact built from it.
   - Check whether it reached a shared branch, CI cache or release.
   - Treat the package as untrusted. Do not unpack or run it.
2. **Find out who owns it on nuget.org.**
   - Look at the package page owner and publish date, metadata only.
   - If it isn't yours, report it to nuget.org support as a squat or malware.
   - Owners cannot delete packages, so only support can remove it.
3. **Reserve the prefix** `Pellucid.Core.` by emailing nuget.org support. Do it before you publish anything public, and ideally cover `Pellucid.` as a whole. Reserved prefixes reject pushes from anyone else.
4. **Check the Azure Artifacts feed.**
   - Confirm the upstream setting does not let nuget.org versions of `Pellucid.Core.*` leak through.
   - Block upstream for these names, or disable the nuget.org upstream.
   - The skill's default is one internal endpoint that refuses internal names upstream, plus client mapping.
   - I don't have an Azure Artifacts reference, so take the exact upstream controls from Microsoft's current docs.

## Clear caches and lock files

A package already in the global packages folder skips source mapping.

- **Developer who got 9.0.0:** delete `Pellucid.Core.Common/9.0.0` from `~/.nuget/packages` (or run `dotnet nuget locals all --clear`). Delete `obj/` and re-restore.
- **CI:** set a per-repo `globalPackagesFolder`, for example via `NUGET_PACKAGES=$(Build.SourcesDirectory)/.nuget`. Restore with no restored package cache.
- **Lock files:** set `<RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>` and commit `packages.lock.json`. Run `dotnet restore --locked-mode` in CI. Then review the lock file: every `Pellucid.Core.*` entry must point at the Azure Artifacts source, and none may be 9.0.0 unless you published it.
- **Metadata commands:** `dotnet list package --outdated` and `dotnet package add` still query every source. Don't trust their output for internal names.

## Verification probe

Check the metadata only. Never download or install the package.

```sh
# credentials via netrc, never argv
code() { curl -s -o /dev/null -w '%{http_code}' --netrc-file "$FEED_NETRC" "$1"; }
FEED="https://pkgs.dev.azure.com/<ORG>/<PROJECT>/_packaging/<FEED>/nuget/v3/flat2"

# 1. Positive control: the public squat exists upstream
[ "$(curl -s -o /dev/null -w '%{http_code}' \
  https://api.nuget.org/v3-flatcontainer/pellucid.core.common/index.json)" = 200 ] \
  || { echo "control failed: no public package to probe with"; exit 1; }

# 2. The probe can see the feed (a known internal package)
[ "$(code "$FEED/pellucid.core.<known-internal>/index.json")" = 200 ] \
  || { echo "probe cannot see the feed"; exit 1; }

# 3. The feed must not serve the public 9.0.0
curl -s --netrc-file "$FEED_NETRC" "$FEED/pellucid.core.common/index.json" \
  | grep -q '"9.0.0"' && { echo "FAILED: feed serves public 9.0.0"; exit 1; } || echo ok
```

- A 401, 403, 5xx or DNS error is inconclusive, never a pass.
- Step 3 only proves anything if the endpoint answers 200 or a clean 404.
- Repeat the probe after any feed reconfiguration.
- Also confirm the restore on a Linux agent, with `--locked-mode`, resolves `Pellucid.Core.*` from the `pellucid` source only. Check the restore log or `project.assets.json`.

## Order of work

1. Merge the `nuget.config` fix and set `FEED_TOKEN` on the Linux agents. This clears the 401.
2. Identify and contain the 9.0.0 exposure.
3. Clear caches, then commit lock files and switch CI to `--locked-mode`.
4. Close the feed upstream hole and run the probe.
5. Request the prefix reservation and report the squat.

## Assumptions to confirm

- The CI is Azure Pipelines or similar, with Linux agents reading `FEED_TOKEN` from a secret.
- The feed is an Azure Artifacts NuGet feed, and `<ORG>/<PROJECT>/<FEED>` are placeholders.
- NuGet is 6.0 or newer, which source mapping requires.
- The Windows pass comes from a credential provider or cache, not from a correct token.