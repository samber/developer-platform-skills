**Do this today (about 20 minutes): your nuget.org key expires 2026-11-01, nine days from now.** It was created in March 2026, before the 2026-08-17 cutoff, so "no rush, December" is wrong. Both pipeline halves fail at the next publish after that date unless a replacement is in place.

1. Open nuget.org, sign in as the account that owns the key, and check its expiry date under API Keys.
2. Create a replacement key scoped to "push new versions" and glob `Pellucid.Fhir.Sdk*`, with a 30-day expiry. Store it in the Azure variable group. Do not delete the old key yet.
3. Email nuget.org support to reserve the prefix `Pellucid.` (see section 2).

## 1. Assumptions and inventory

Assumptions (correct me if wrong):
- The package ID is `Pellucid.Fhir.Sdk`. It is a class library, not a .NET tool.
- It is tied to a commercial product, so it gets the approval gate.
- The key lives as a CI secret in both Azure Pipelines and GitLab.com.
- The key belongs to one engineer's personal nuget.org account.
- Azure runs hosted agents. GitLab runs shared runners on GitLab.com.
- No private NuGet feed was mentioned, so this plan has no private-consumption config. Tell me if you have one.

| Item | Registry | Publish path | Credential | Expiry | Owner | Target model |
|---|---|---|---|---|---|---|
| `Pellucid.Fhir.Sdk`, GitLab half | nuget.org | GitLab CI | account-wide key, March 2026 | 2026-11-01 | unknown | trusted publishing (OIDC) |
| `Pellucid.Fhir.Sdk`, Azure half | nuget.org | Azure Pipelines | same key | 2026-11-01 | unknown | scoped 30-day key, automated rotation |
| Prefix `Pellucid.` | nuget.org | none | none | none | none | reserved |

A key nobody can locate counts as compromised. Check where else the key is stored, such as laptops, wikis, and old variable groups.

## 2. Decisions

**"OIDC everywhere" is not possible for the Azure half.**
- nuget.org supports trusted publishing only from GitHub Actions and GitLab CI. Azure Pipelines is not supported.
- Reframe the leadership goal as "zero long-lived, account-wide tokens". Then:
  - GitLab becomes fully OIDC.
  - Azure keeps one narrow, 30-day key, owned by a bot account.
- Plan C below is the only route to true OIDC for the Azure half.

**Credential rung per half**
- **GitLab:** trusted publishing, then revoke the old key.
- **Azure:** the narrowest key nuget.org offers, with these properties:
  - Scope is "push new versions" plus the glob `Pellucid.Fhir.Sdk*`.
  - Expiry is 30 days.
  - It sits in a protected environment with required approvers.
  - The agent receives it through the `NUGET_API_KEY` environment variable (NuGet 7.6+), not the command line.
  - A scheduled rotation job runs before expiry. nuget.org emails a warning 10 days ahead.
- **Rotation caveat:** my references do not say how to create keys programmatically. Confirm that against nuget.org docs before promising "automated". Otherwise use a calendar reminder with two named people.

**Azure options after the emergency (decide in November)**
- **A (default):** keep the scoped key on Azure.
- **B:** move the Azure half to a GitLab or GitHub publish job. Azure builds the `.nupkg`, and a separate pipeline publishes it. This needs the source or artifact reachable from that CI.
- **C:** wait for nuget.org to support Azure. Do not plan on it.

**Namespace**
- Email nuget.org support to reserve ID prefix `Pellucid.` before any new package.
- Reserved prefixes reject pushes from anyone else and show a verified mark. This is also your dependency-confusion defense.
- First check nuget.org search for `Pellucid.*` packages owned by others. Those would complicate the reservation.
- Move ownership of `Pellucid.Fhir.Sdk` to an organization account with at least two owners using phishing-resistant 2FA.
- An org-owned trusted-publishing policy goes inactive if its creator leaves the org. Create policies under a long-lived owner.

**Channel policy**
- SemVer per release, one immutable version each.
- Pre-releases use the `-beta.1` form on a non-default channel. Zero-pad SemVer 1 counters (`beta01`).
- A CI guard fails the release if the tag does not equal `<Version>` in `.csproj` or `Directory.Build.props`.

**Approval gate**
- Use required reviewers on the publish environment: a team, or at least two people besides whoever cuts releases. Any one approves. Self-review is blocked.
- This applies to both GitLab (protected environment) and Azure (environment approvals).

**Preflight** (before every release)
- `dotnet pack -c Release`
- Inspect the `.nupkg` and `.snupkg`.
- Do a trial push to the NuGet test gallery.

**Policy scopes** (GitLab trusted publishing)
- Set the package glob `Pellucid.Fhir.Sdk*` and "publish new versions" only.
- Without scopes, a policy covers every package the owner holds.
- Enable "publish new packages" only on a temporary policy for a brand-new ID, then remove it.

## 3. Pipeline files (drafts pending your approval)

**GitLab: `.gitlab-ci.yml` (publish pipeline)**

Constraints:
- NuGet requires a branch ref in the OIDC token, not a tag. Publish from a protected `release` branch pipeline.
- Every job in a pipeline can mint an OIDC token, so keep the build job free of `id_tokens`.

```yaml
stages: [build, publish]

build:
  stage: build
  image: mcr.microsoft.com/dotnet/sdk:<pinned-version>@sha256:<digest>
  rules:
    - if: '$CI_COMMIT_BRANCH == "release" && $CI_COMMIT_REF_PROTECTED == "true"'
  script:
    - ./ci/check-version.sh            # tag-equals-manifest guard
    - dotnet test -c Release
    - dotnet pack -c Release -o out
  artifacts:
    paths: [out/]                      # no cache: restores are banned in build and publish jobs

publish:
  stage: publish
  image: mcr.microsoft.com/dotnet/sdk:<pinned-version>@sha256:<digest>
  needs: [build]
  environment: release                 # protected environment with approval rules
  rules:
    - if: '$CI_COMMIT_BRANCH == "release" && $CI_COMMIT_REF_PROTECTED == "true"'
  id_tokens:
    NUGET_ID_TOKEN:
      aud: https://www.nuget.org
  script:
    # PLACEHOLDER: exchange $NUGET_ID_TOKEN for a one-hour API key per the nuget.org
    # trusted-publishing docs. My reference only documents the GitHub action, not the
    # GitLab exchange call. Fill this in from the docs, not from memory.
    - export NUGET_API_KEY="<exchange-output>"
    - dotnet nuget push "out/*.nupkg" --source https://api.nuget.org/v3/index.json --skip-duplicate
```

`--skip-duplicate` makes a rerun after a partial failure complete the release.

**Azure Pipelines: `azure-pipelines-release.yml`**

```yaml
trigger: none                          # tag/branch triggers set in the UI; protected

stages:
- stage: build
  jobs:
  - job: pack
    pool: { vmImage: ubuntu-latest }
    steps:
    - script: ./ci/check-version.sh && dotnet test -c Release && dotnet pack -c Release -o $(Build.ArtifactStagingDirectory)
    - publish: $(Build.ArtifactStagingDirectory)
      artifact: dist
- stage: publish
  dependsOn: build
  jobs:
  - deployment: push
    environment: nuget-release         # approvals and checks configured on this environment
    pool: { vmImage: ubuntu-latest }
    strategy:
      runOnce:
        deploy:
          steps:
          - download: current
            artifact: dist
          - script: dotnet nuget push "$(Pipeline.Workspace)/dist/*.nupkg" --source https://api.nuget.org/v3/index.json --skip-duplicate
            env:
              NUGET_API_KEY: $(NuGetApiKey)   # variable group, scoped to this environment only; never account-wide
```

Hardening that applies to both files:
- Pin all images and tasks by digest or SHA. I did not resolve any, so none are invented.
- Default permissions to none.
- Add no triggers other than the protected release path.
- Add no manual-run trigger to the publish job without the same approval gate.

## 4. Rollback runbook (commands are yours to run)

nuget.org owners cannot delete packages. Only nuget.org support removes them, and only for malware or leaked secrets.

1. Publish the fixed version first, immediately.
2. Unlist the bad version. Unlist hides it from search, but exact-version restores still work and floating ranges can still pick it. Deprecate it with a reason and name the safe version. Do not append a dry-run flag to removal commands.
3. If compromise is suspected, isolate build hosts first. Then revoke and rotate every credential the release job could reach. That includes the Azure key and any GitLab policy.
4. For malware or leaked secrets, contact nuget.org support for hard removal.
5. Announce in the changelog and your security advisory channel.

Rehearse steps 1-2 on the NuGet test gallery, never on `Pellucid.Fhir.Sdk`. Every public rehearsal burns a version forever.

## 5. Private consumption

No private feed is named. If you have one, add `packageSourceMapping` to `nuget.config` with `<clear />` and `Pellucid.*` mapped to the internal source. Add `--locked-mode` restores in CI. The probe in release-workflow.md applies: never publish a canary to nuget.org.

## 6. Migration sequence

| Date | Step | Evidence it leaves |
|---|---|---|
| 2026-10-23 | Scoped replacement key into the Azure environment. Prefix-reservation email sent. Locate every copy of the old key. | Key scope screenshot, sent email |
| 2026-10-26 | GitLab: create the policy (scope `Pellucid.Fhir.Sdk*`, new versions). Rehearse on the test gallery. | Test-gallery push log |
| 2026-10-28 | GitLab: one real release via the OIDC path. | Pipeline run, nuget.org version |
| 2026-10-29 | Revoke the old account-wide key everywhere, before 2026-11-01. Confirm Azure still publishes. | Revocation record, Azure run |
| by 2026-11-20 | First scheduled Azure key rotation, before the 30-day expiry. | Rotation log |
| 2026-11 | Decide Azure option A, B or C. Write the rollback rehearsal result. | Decision note |
| by 2026-12-31 | Prefix reserved. Org ownership with 2 owners confirmed. | Verified mark on nuget.org |

Success gates:
- Zero account-wide tokens.
- One short-lived scoped key remains, on Azure only.
- 100% of publishes come from CI on a protected path.
- The rollback is rehearsed on the test gallery.

## Questions for you

1. Which nuget.org account owns the key, and is it a personal or org account?
2. Are the Azure repos on Azure Repos or GitHub? That decides whether option B is cheap.

**Next, within 2 minutes:** open nuget.org API Keys and send me the expiry date, scope and owner (not the key itself). If you paste a secret anywhere, revoke it.