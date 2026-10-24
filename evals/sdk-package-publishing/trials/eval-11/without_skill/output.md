# Fix: `nuget.config`

## Root causes

1. **Source order does nothing.** NuGet queries every source and picks the best version match across all of them. It does not stop at the first source that has the package. A public `Pellucid.Core.Common` 9.0.0 on nuget.org (a dependency-confusion package) beats your internal version if it is higher.
2. **`$FEED_TOKEN` is never expanded.** NuGet only expands `%FEED_TOKEN%`. It sent the literal string `$FEED_TOKEN` as the password, so Linux gets a 401. Windows probably passes because of cached credentials or the credential provider, so it never uses the token in the file.
3. **Encrypted passwords are Windows-only** (DPAPI). On Linux you must use `ClearTextPassword`, filled from an environment variable. Never commit the real token.

## `nuget.config` (repo root)

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="pellucid-artifacts"
         value="https://pkgs.dev.azure.com/<ORG>/<PROJECT>/_packaging/<FEED>/nuget/v3/index.json" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
  </packageSources>

  <!-- Each package ID comes from exactly one source. The longest matching pattern wins. -->
  <packageSourceMapping>
    <packageSource key="pellucid-artifacts">
      <package pattern="Pellucid.Core.*" />
    </packageSource>
    <packageSource key="nuget.org">
      <package pattern="*" />
    </packageSource>
  </packageSourceMapping>

  <packageSourceCredentials>
    <pellucid-artifacts>
      <add key="Username" value="az" />
      <add key="ClearTextPassword" value="%FEED_TOKEN%" />
    </pellucid-artifacts>
  </packageSourceCredentials>
</configuration>
```

Notes:
- `<clear />` drops machine-level and user-level sources that could re-add nuget.org unmapped.
- The `key` values in `packageSourceMapping` and `packageSourceCredentials` must match the `packageSources` key exactly. The credentials element name is the source key, so keep it free of spaces.
- `Pellucid.Core.*` resolves only from Azure Artifacts, so a public `Pellucid.Core.Common` is never considered. If Azure Artifacts lacks a version, restore fails instead of silently falling back to nuget.org.
- Source mapping needs NuGet 6.0+ (.NET SDK 6+). Check the Linux agents' SDK version, because older clients ignore the section.

## Linux agent auth

**Azure Pipelines (preferred):** drop the credentials block entirely and add this before restore:

```yaml
- task: NuGetAuthenticate@1
- script: dotnet restore --locked-mode
```

**Other CI:** export `FEED_TOKEN` (a PAT with Packaging → Read) as a secret env var for the restore step. Check that it is non-empty before restoring.

## Harden further

- Enable lock files (`<RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>`), commit `packages.lock.json`, and restore with `--locked-mode` in CI. Content hashes will catch a swapped package.
- Reserve the `Pellucid.Core.` prefix on nuget.org. If the 9.0.0 package exists publicly and is not yours, report it to nuget.org as malicious.
- Treat the developer's restore as an incident, since that package could have run code:
  - Find out which machine and which project restored it.
  - Check whether any build artifact shipped with it.
  - Delete the poisoned package from the global packages cache (`dotnet nuget locals all --clear`).
  - Rotate any secrets reachable from that machine or pipeline.
  - Rebuild after the fix.
- Verify: `dotnet nuget list source` and `dotnet restore --force --no-cache` on a Linux agent. Then bump a test reference to `Pellucid.Core.Common 9.0.0` and confirm restore fails with "not found in pellucid-artifacts".

I did not run or edit anything in your repo. The file above is a drop-in, with `<ORG>`, `<PROJECT>` and `<FEED>` as placeholders.