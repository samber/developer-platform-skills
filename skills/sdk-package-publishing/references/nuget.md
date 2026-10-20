# NuGet

## Contents

- Public publishing: credentials, namespace, signing, versions, removal
- Private publishing
- Private consumption
- Dated changes

## Public publishing

**Credentials**

- Trusted publishing on nuget.org from GitHub Actions and GitLab CI. The CI token is exchanged for a single-use API key valid one hour. Azure Pipelines is not supported.
- GitHub setup: nuget.org account > Trusted Publishing > policy with repository owner, repository, workflow file name only, optional environment. Job: `permissions: id-token: write`, `NuGet/login@<sha>  # v1` with `user:` set to the nuget.org profile name (not email), then `dotnet nuget push <pkg> --api-key ${{ steps.login.outputs.NUGET_API_KEY }} --source https://api.nuget.org/v3/index.json`.
- GitLab: `id_tokens` with audience `https://www.nuget.org`; the policy matches namespace and project path. The token's `ref` must name a branch: publish from a protected release-branch pipeline, not a tag pipeline.
- Set Policy Scopes on every policy: a package glob (`Corp.Sdk.*`) and "publish new versions". By default a policy covers every package the owner holds. Enable "publish new packages" only on the policy that creates a new ID, then remove it.
- Policies for private repositories stay temporary for 7 days, then lock to immutable repository IDs after the first publish. An org-owned policy goes inactive if its creator leaves the org: recreate it under an active owner.
- API keys (fallback, e.g. Azure Pipelines): 30 days maximum. Scope to "push new versions" plus a package glob (`Corp.Sdk.*`); never account-wide push. Automate rotation before expiry; nuget.org emails a warning 10 days ahead. On shared or self-hosted agents pass the key through the `NUGET_API_KEY` environment variable (NuGet 7.6+), not the command line.

**Namespace**

- Apply for ID prefix reservation (`Corp.`) by emailing nuget.org support. Reserved prefixes reject pushes from anyone else and show a verified mark. Do it before the first public package: it is also the publisher-side dependency-confusion defense.

**Signing**

- nuget.org repository-signs every package. Author signing needs a CA-issued code-signing certificate (self-issued rejected) registered on the account and an RFC 3161 timestamp; most SDK publishers rely on repository signing plus trusted publishing.

**Versions**

- A dot-separated pre-release (`2.0.0-beta.1`) or build metadata makes the package SemVer 2, invisible to clients older than NuGet 4.3. Fine for modern SDKs; state the minimum client in the README.
- SemVer 1 style suffixes sort as strings: zero-pad counters (`beta01`, `beta02`).

**Removal**

- Owners cannot delete from nuget.org; only support removes packages, for malware or leaked secrets. Unlist hides a version from search, but exact-version restores still work and floating ranges can still pick it. Pair unlist with deprecation (reason, optional alternate package) and publish a fixed version.

## Private publishing

- Feeds with NuGet support: GitHub Packages, GitLab Package Registry, AWS CodeArtifact, Azure Artifacts (views `@prerelease`/`@release` promote without republishing), Artifactory, Nexus.
- Push with `dotnet nuget push --source <feed-name>` using a feed defined in `nuget.config`; credentials from environment variables.

## Private consumption

Source order in `nuget.config` is ignored during restore, so any listed source can serve any ID. Package Source Mapping (NuGet 6.0+) fixes that.

```xml
<configuration>
  <packageSources>
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="corp" value="https://nuget.internal.example.com/v3/index.json" />
  </packageSources>
  <packageSourceMapping>
    <packageSource key="nuget.org"><package pattern="*" /></packageSource>
    <packageSource key="corp"><package pattern="Corp.*" /></packageSource>
  </packageSourceMapping>
  <packageSourceCredentials>
    <corp>
      <add key="Username" value="ci" />
      <add key="ClearTextPassword" value="%CORP_FEED_TOKEN%" />
    </corp>
  </packageSourceCredentials>
</configuration>
```

- `<clear />` stops machine-level sources leaking in. The most specific pattern wins, so `Corp.*` beats `*`.
- Environment variables use `%VAR%` syntax on every OS; `$VAR` never resolves.
- Two documented leaks remain: a package already in the global packages folder skips mapping (set a per-repo `globalPackagesFolder` in CI), and metadata commands (`dotnet package add`, `dotnet list package --outdated`) still query every source.
- Commit lock files (`RestorePackagesWithLockFile`) and restore with `--locked-mode` in CI.

## Dated changes

- 2025-09: trusted publishing launched.
- 2026-08-17: new API keys capped at 30 days.
- 2026-11-01: every API key created before 2026-08-17 expires.
