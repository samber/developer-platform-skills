# terraform-provider-silverbeck: gaps before the Partner badge request

**Verdict: not ready.** Three problems block the badge: the shared staging org, the three `ExpectNonEmptyPlan` flags, and acceptance tests running on external PRs. Three more are cheap to close. I used the `terraform-provider-offering` skill and its testing, design and release references. Several answers are missing and are listed at the end. I treated each as an assumption and marked the dependent gate row UNKNOWN.

## Gaps, ranked by severity

| # | Gap | Rule it breaks | Fix |
| --- | --- | --- | --- |
| 1 | External-contributor PRs run acceptance tests with sandbox credentials | Never run acceptance tests on fork PRs with credentials (a malicious PR can exfiltrate them) | Split CI into a credential-free lane and an approval-gated lane (below) |
| 2 | Tests run in the staging org that also hosts the sales demo data | Tests need a dedicated sandbox, never a shared org | New dedicated org per CI lane, with credentials scoped to it |
| 3 | `ExpectNonEmptyPlan: true` on 3 resources (tags order) | Never set it to turn CI green. The harness's empty-plan check is what catches perpetual diffs. | Fix the cause (below), then delete the flags |
| 4 | No sweepers, monthly manual deletion | Sweepers must run before and after each nightly | Add sweepers and a test prefix |
| 5 | Only `_basic` for 9 resources | Each resource needs `_disappears`, update, replace, `_upgrade` and data-source tests | Fill the coverage matrix below |
| 6 | Terraform latest only | Test the oldest claimed version, the latest, and a `tofu` lane | Matrix lane, plus `TF_ACC_TERRAFORM_PATH` for tofu |
| 7 | No nightly suite | Partner requires nightly acceptance tests in GitHub Actions. Releases must come from a green nightly. | Add a `schedule:` workflow |

### 1. Fork PRs and credentials

Your goal is "community PRs green before review", but that goal conflicts with the credential rule. Only the credential-free lane can be green before review.

- **Lane A, every PR, no secrets.** Run `build`, `go vet`, the linter, unit tests, a docs-regeneration dirty-tree check, and a check that fails if a PR adds `ExpectNonEmptyPlan`. Add API-mocked unit tests (`httptest`) so contributors get real signal. Contributors see green or red here before anyone reviews.
- **Lane B, acceptance tests, gated.** Run it on a maintainer label or comment, for the resources the PR touches. Put the sandbox secrets in a GitHub Environment with required reviewers. The reviewer reads the diff before approving, because the PR code runs with the credentials.
- Use the `pull_request` trigger for Lane A. Never check out PR head code under `pull_request_target` with secrets.
- Tell contributors that "acceptance pending maintainer approval" is expected, and add it to `CONTRIBUTING.md`.
- **Ask how fork PRs get secrets today.** GitHub does not pass secrets to fork PRs under `pull_request`. If they currently get secrets, you are probably on `pull_request_target`. In that case, treat the staging credentials as exposed and rotate them. Check the past workflow runs.

### 2. Shared staging and demo data

- Create a dedicated sandbox org used only by CI, with its own scoped token.
- Name every test object `tf-acc-test-<random>`.
- Do not write sweepers against the current org. A prefix sweeper in a demo org is a data-loss risk, and the monthly hand-deletion already is one.
- Raise the sandbox's quotas and rate limits to what the parallel suite needs, or run fewer tests in parallel.
- Design the sandbox with `samber/developer-platform-skills@api-test-mode-design`.

### 3. The three `ExpectNonEmptyPlan` resources

The gate row "Deterministic normalization and ordering" reads **FAIL for those 3 resources** until the choice below is made. A resource ships only when its row reads PASS or COMP.

1. Ask the API team how `tags` should behave.
   - If tags are unordered, the provider uses a **set**.
   - If order means something and the API keeps it, the API needs a position field and the provider uses a **list sorted by it**.
   - The choice is permanent, so settle it with the API team first.
2. Check whether the provider is at 1.0 or later.
   - If tags are a list today, switching to a set is **breaking**. It needs a schema version bump, a state upgrader from every released version, and a major release, preceded by a minor that deprecates the old shape.
   - A non-breaking alternative is a semantic-equality custom type or plan modifier that normalizes order. Document it.
3. Delete the three flags.
4. Add the CI check that rejects any new `ExpectNonEmptyPlan`. A PR that must add one has to link an API bug.
5. Re-run the 3 `_basic` tests. The flag also hides any other diff in those steps, so more may surface.

### 4. Sweepers

- Register sweepers with `resource.AddTestSweepers`, declare dependencies, and call `resource.TestMain` in `TestMain`.
- Each sweeper deletes every object with the test prefix.
- Run sweepers before and after each nightly.
- This replaces the monthly manual deletion. Leaks come from API errors mid-test and from destroy steps that report success too early. Feed any leak you find back to the API team.

### 5. Coverage matrix (9 resources)

You have `_basic` for each resource. Confirm its import step uses `ImportStateVerify` and ignores only the preserved fields and API-generated secrets from the resource map. Missing for each resource:

| Test | Count |
| --- | --- |
| `_disappears` | 9 |
| update per mutable attribute (assert in-place with `plancheck.ExpectResourceAction`) | 1 per mutable attribute |
| replacement per `RequiresReplace` attribute | 1 per replace-only attribute |
| `_upgrade`: apply the last released version via `ExternalProviders`, plan with the new build, expect an empty plan | 9 once you have a prior release |
| data source `_basic`: singular errors on zero and on several matches, plural returns empty without error | per data source |
| import config generation: an `import` block with `-generate-config-out`, then `terraform validate` | 9 |

Also add the following:

- Use typed `statecheck` and `knownvalue` checks.
- Assert that secrets are absent from state (write-only) or marked sensitive.
- Break one passing test on purpose to prove it can fail.

If any resource has no state upgrader yet, there is nothing to upgrade from. Record the first release as the baseline.

### 6. Version matrix

- Run the oldest Terraform you claim, plus latest. If you have no stated minimum, default to the oldest upstream-supported minor. Write-only arguments need 1.11 or later on both Terraform and OpenTofu.
- Add a `tofu` lane by pointing `TF_ACC_TERRAFORM_PATH` at the binary.
- Publish the minimums in the docs.

### 7. Cadence target

| Trigger | Runs |
| --- | --- |
| every PR (Lane A) | build, lint, unit tests, docs check, no new `ExpectNonEmptyPlan` |
| label or maintainer comment (Lane B) | acceptance tests for the resources touched |
| nightly | full acceptance suite, sweepers, upgrade tests, on the matrix (oldest Terraform, latest Terraform, tofu) |
| release | only from a commit with a green nightly |

Track the flake rate per resource. Fix flakes with bounded typed waiters in the provider, never with test-level retries. A resource that flakes in CI produces "inconsistent result after apply" in production.

## Partner items outside the CI you described

I cannot tell from your description whether these pass, so they stay open:

- **Technology Partner Program membership.** Required.
- **Plugin Framework.** Required. If any resource is on SDKv2, schedule the mux migration before the badge request, core resources first. Prove each migrated resource with its old tests unchanged plus an upgrade test.
- **Support commitment.** Critical issues within 48 hours and others within 5 business days. Confirm you have the staffing and on-call.
- **Release hygiene.**
  - Published under your final GitHub organization.
  - RSA key registered on both the Terraform Registry and OpenTofu (the OpenTofu key submission is easy to forget).
  - Never retag a release.
  - Verify `terraform init` and `tofu init` on a clean machine.
- **API gate.** Fill the full gate matrix for the 9 objects. Only the ordering row is known to FAIL. The other rows are UNKNOWN until answered, and UNKNOWN counts as FAIL: stable ID, GET returns every field, in-place update, idempotent create, propagation, async, secrets, rate limits.

## Order of work

1. Today: rotate the staging credentials if fork PRs ever ran with them, and move acceptance tests behind the approval gate.
2. Week 1: create the dedicated sandbox, add sweepers and the prefix, and add Lane A.
3. Week 1 to 2: settle the tags decision with the API team, fix the 3 resources, and remove the flags.
4. Week 2 to 3: add the nightly, the oldest-Terraform lane and the tofu lane, then fill the coverage matrix.
5. Before applying: the nightly is green on every resource for a release cycle, the release is verified on both registries, and the Partner items above are confirmed.

**Definition of ready:**
- No `ExpectNonEmptyPlan` anywhere.
- Every resource's suite passes.
- Upgrade tests pass from the last release.
- `terraform init` and `tofu init` with `OPENTOFU_ENFORCE_GPG_VALIDATION=true` both install the latest version.

## Questions I need answered

1. Is the provider on the Plugin Framework or SDKv2?
2. Is it at 1.0 or later, and is `tags` a list today?
3. Which are the 3 resources, and are their tags unordered?
4. How do fork PRs get credentials today?
5. What is the minimum Terraform and OpenTofu version you support?
6. Are you in the Technology Partner Program, and who is on call for the issue queue?
7. Is there a stable ID, a GET that returns every field, and a documented rate limit for the other gate rows?