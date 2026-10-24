**Next action, 5 minutes:** open nuget.org → Account → API Keys. Write down the scope, glob pattern and expiry of the March key.

I checked one page, the Microsoft Learn Trusted Publishing doc (updated 2026-09-01). Web search was denied, so I checked nothing else. The doc lists **GitHub Actions and GitLab only**. It never mentions Azure Pipelines.

## Big picture

- GitLab half: supported now. Do it.
- Azure half: nuget.org doc lists no Azure Pipelines support. "OIDC everywhere" may not be possible for it by December. See Phase 3.
- Prefix reservation: independent of OIDC, cheap, and it protects the `Pellucid.*` namespace. Do it first.
- The one account-wide key is the main risk. Anyone with a pipeline secret can push any package under the account.

## Phase 0: baseline (week 1, about 1 hour)

1. Inventory: list every pipeline that pushes to nuget.org, with platform, project path and the package IDs it pushes.
2. Record the March key's scope, glob and expiry. nuget.org keys expire after at most 365 days. If yours has no earlier expiry, it dies around March 2027, so rotate it before then anyway.
3. Find every place the key is stored: Azure variable groups, GitLab CI/CD variables, developer machines, wikis.
4. Confirm who owns the packages on nuget.org: a personal account or an organization. Trusted Publishing policies belong to an owner. Use an **organization** owner, not an individual. If a policy creator leaves the org, the policy goes inactive.

## Phase 1: reserve the prefix (week 1, request about 30 minutes)

1. Choose prefixes. Start with `Pellucid.`. Add `Pellucid.Fhir.` only if you want a narrower one. The broad one covers it.
2. Submit the ID prefix reservation request through the nuget.org support form. I could not verify the current form or criteria, so read them on the NuGet docs "ID prefix reservation" page first.
3. Check that all existing `Pellucid.*` IDs belong to your org. Unknown owners will block the request.
4. Once approved, only the owners can push IDs under that prefix. The packages also get a reserved-prefix badge.
5. Do this before OIDC. A reserved prefix limits the damage if any credential leaks.

## Phase 2: GitLab to Trusted Publishing (weeks 2–3)

1. On nuget.org, add a policy owned by the org. Use the "Federated credentials" page, per the doc.
2. Set the GitLab `namespace_path` and `project_path` claims. Both are required. Optionally add `environment`. `ref` must be a branch name, so tags do not work.
3. Scope the policy to the package glob and to the actions it needs, for example new versions only.
4. Pilot on one low-risk repo. Use the doc's `id_tokens` job with `aud: "https://www.nuget.org"`. Then call `POST /api/v2/token` and push.
5. Request the API key **right before** `dotnet nuget push`. It lives 1 hour. Each OIDC token works once.
6. Pass the nuget.org profile name, not an email. Keep it as a CI variable.
7. If you publish from release tags, add a branch-based publish job or protected-environment job. Tags are not a valid `ref`. Test this in the pilot.
8. Roll out to the remaining GitLab pipelines. Remove the key variable from each one after its first green OIDC publish.

## Phase 3: Azure Pipelines (weeks 3–6)

Check first whether nuget.org now trusts Azure DevOps as an issuer. The doc says nothing. Ask on NuGet/Home. Decide at the end of week 3, then pick one option:

| Option | Gets you | Costs |
|---|---|---|
| A. Native OIDC, if nuget.org supports Azure | True keyless | Only if support exists |
| B. Move the publish step to GitLab | Keyless. Azure still builds. | Hand-off needed, such as artifacts or a repo mirror. Needs a trusted trigger. |
| C. Keep a key, but only for Azure | Works now | Not "OIDC everywhere". The key must be narrow. |

My recommendation is B if the Azure packages can move cheaply, otherwise C. For C:

1. Create one key per pipeline. Give each a glob limited to its own IDs and push-only scope.
2. Set a short expiry, 90 days or less. Put a reminder on the calendar.
3. Store it as a secret variable in Azure Key Vault or a protected variable group. Allow only the release pipeline to read it.
4. Add an approval check on the publish stage.

Tell leadership plainly that option C is an exception, with a name, an owner and a review date.

## Phase 4: retire the old key (week 7–8)

1. Confirm that every package published since cutover used a new credential. Use nuget.org package history.
2. **Revoke** the March account-wide key. Do this only after all pipelines are green on the new paths.
3. Wait 7 days for hidden users such as local scripts. Then delete the key from every secret store in the Phase 0 inventory.
4. Turn on 2FA for every account that can manage policies. Confirm that at least two people can manage the org.

## Timeline

| Phase | When | Effort |
|---|---|---|
| 0 Baseline | Oct 26–30 | 1 hour |
| 1 Prefix | Oct 26–Nov 6 | 30 minutes, then wait for approval |
| 2 GitLab | Nov 2–13 | 1–2 days |
| 3 Azure | Nov 9–Dec 4 | 1 day (B) to 3 days (C) |
| 4 Retire | Dec 7–18 | 2 hours |

This leaves roughly 2 weeks of buffer before the end of December. I did not account for any freeze window or holidays. Check yours.

## Open questions

1. Are the packages owned by a personal account or an org on nuget.org?
2. Do the Azure pipelines publish from branches or tags?
3. Can Azure-built packages be published from a GitLab job without moving the source?
4. Is leadership fine with one scoped, short-lived key for Azure if B is not feasible?

**Next:** do the 5-minute check above and paste the key's scope and expiry. I can then tighten Phase 1 and the Phase 3 decision.