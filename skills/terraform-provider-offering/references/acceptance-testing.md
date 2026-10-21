# Acceptance testing

Load at workflow step 6. Acceptance tests run real plan, apply, refresh, import and destroy cycles against a live account through `terraform-plugin-testing`, gated by `TF_ACC=1`.

## Contents

- Required tests per resource
- Checks that catch user-visible bugs
- Upgrade tests
- Sandbox and sweepers
- Cadence and CI
- Flakiness
- Testing newer constructs

## Required tests per resource

| Test | Proves |
| --- | --- |
| `_basic` | create, read back, destroy; ends with an import step using `ImportStateVerify`, ignoring only the resource map's preserved fields and API-generated secrets |
| `_disappears` | object deleted out of band is removed from state and recreated on the next plan |
| update per mutable attribute | in-place update works and does not force replacement |
| replacement per `RequiresReplace` attribute | plan shows replace, not update |
| `_upgrade` (step 8) | the last released version's state plans clean with the new build |
| data source `_basic` | singular errors on zero and on several matches; plural returns empty without error |

Name objects with a random suffix and a fixed prefix (`tf-acc-test-<random>`) so parallel runs never collide and sweepers can find leftovers.

Fix regressions in two commits: the failing test first, then the fix. Break a passing test deliberately once (flip an expected value) to prove it can fail.

## Checks that catch user-visible bugs

- The harness already re-plans after every apply step and fails when the plan is not empty. That default catches perpetual diffs, the most reported provider bug class. Never set `ExpectNonEmptyPlan: true` to make a test pass; a PR that adds it must link the API bug it works around.
- Use typed state checks (`statecheck.ExpectKnownValue` with `knownvalue` matchers) over legacy string checks.
- Assert the planned action (`plancheck.ExpectResourceAction`) on steps that should update in place.
- Assert sensitive and write-only values never appear in state.

## Upgrade tests

Run before every release and for every migrated resource:

1. Step one: apply with the last released provider from the Registry (`ExternalProviders` with a version constraint).
2. Step two: plan with the new build (`ProtoV6ProviderFactories`) and expect an empty plan.
3. Repeat from the last release of every major you still support, and from each schema version that has a state upgrader.
4. After an adoption, start from the last release at the old address: apply with the old `source`, run `terraform state replace-provider` in a pre-step, then plan with the new build and expect no changes. Script it outside the harness if the harness cannot run the replace step.

Import config generation: for each resource, apply, then run an `import` block with `terraform plan -generate-config-out` against the created object, and validate the generated HCL with `terraform validate`. Customers adopting existing objects in bulk depend on it.

## Sandbox and sweepers

- Run tests in a dedicated account or organization per CI lane, never a customer or production org, with credentials scoped to that sandbox.
- Raise the sandbox's quotas and rate limits to what the parallel suite needs, or run fewer tests in parallel.
- Register sweepers (`resource.AddTestSweepers` with dependencies; `TestMain` calling `resource.TestMain`) that delete every object matching the test prefix, and run them before and after each nightly. Leaks come from API errors mid-test and from destroy steps that report success too early.
- Feed sandbox misbehaviour back to the API team: a test that needs a retry usually exposes the same race a customer will hit.

## Cadence and CI

| Trigger | Runs |
| --- | --- |
| every pull request | build, lint (`go vet`, a linter config, provider-specific linters), unit tests, docs regeneration check, no new `ExpectNonEmptyPlan` |
| PR label or maintainer comment | acceptance tests for the resources the PR touches |
| nightly | full acceptance suite, sweepers, upgrade tests |
| release | only from a commit with a green nightly |

- Test against the oldest Terraform version you claim and the latest; add the `tofu` binary as a second lane (point the harness at it with `TF_ACC_TERRAFORM_PATH`) to catch OpenTofu divergence.
- Never run acceptance tests on pull requests from forks with sandbox credentials: a malicious PR can exfiltrate them. Require a maintainer to approve the run.

## Flakiness

- Fix flaky tests with waiters and bounded typed retries in the provider (see `references/resource-design-rules.md`, eventual consistency), never with test-level retries: users run the same code path.
- Track flake rate per resource; a resource that flakes in CI produces "inconsistent result after apply" in production.
- Cost driver: hyperscaler providers pay for real infrastructure across thousands of tests; a SaaS API with tens of resources mostly spends API quota and sandbox seats.

## Testing newer constructs

- Ephemeral resources: assert through a test-only echo provider, since values never reach state.
- List resources: query-mode steps (`Query: true`) with query checks on result count and identity.
- Actions: trigger through `lifecycle.action_trigger`, skip below Terraform 1.14, and assert against the API afterwards, since actions write nothing to state.
- Write-only arguments: assert the value reached the API and is absent from state; bump `<name>_wo_version` and assert an update.
