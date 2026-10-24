Start with blocker 1: create a dedicated test org. Everything else depends on it.

I couldn't check HashiCorp's current Partner checklist from here, so the partner-portal items are from memory. Confirm them in the portal before you apply.

## Blockers, ranked

**1. Separate test org (about 1 day)**
- Create a dedicated org that holds no sales demo data.
- Acceptance tests today can create, change, or delete demo data. That alone fails review.
- Use a scoped, rate-limited, quota-capped API key for that org. Make it rotatable and cheap to throw away.
- Name every test object `tf-acc-test-<random>`. Sweepers need that prefix.

**2. Cleanup: sweepers instead of the monthly manual delete (about 1 day)**
- Register one sweeper per resource with `resource.AddTestSweepers`. Delete only objects with the `tf-acc-test-` prefix.
- Add `TestMain` with `resource.TestMain(m)`.
- Run `go test ./... -sweep=<region>` in a nightly CI job. Run it again after every acceptance run, even a failed one (`if: always()`).
- Add `CheckDestroy` to every test case. It must call the API and confirm the object is gone.

**3. Remove `ExpectNonEmptyPlan: true` on the 3 resources (about 0.5 to 1 day each)**
- This is a real provider bug, not a test problem. Users see a perpetual diff on every `terraform plan`.
- Reviewers look for this.
- Fix by data model, in order of preference:
  1. Change tags to a set (`TypeSet` in SDKv2, `SetAttribute` in the Framework) if order carries no meaning.
  2. If order matters to users, sort in the read path or add a plan modifier or `DiffSuppressFunc`.
  3. Fix it in the API only if you own it and can do it soon.
- After the fix, every step should end with `PlanOnly` and an empty plan.

**4. Fork PR policy: "green before review" cannot run live acceptance tests (about 0.5 day)**
- Secrets are not exposed to `pull_request` runs from forks, so acceptance tests cannot run there.
- Do not switch to `pull_request_target` and check out the PR head with secrets. That is the classic pwn-request hole, and it hands your key to any contributor.
- Run these automatically on every PR, with no secrets:
  - `go build`, `go vet`, `golangci-lint`
  - unit tests
  - `tfplugindocs` diff check
  - `terraform fmt` on the examples
  - `goreleaser check`
- Run acceptance tests only after a maintainer approves:
  - Trigger on a label such as `ok-to-test`, or on `workflow_dispatch`.
  - Put the secrets in a GitHub Environment with required reviewers.
  - Pin the checked-out SHA to the one the reviewer approved.
  - Gate your own PRs the same way, with a concurrency group so only one run hits the org at a time.
- Tell contributors: "unit and lint green means ready for review. Acceptance runs after review starts."

**5. Test depth: `_basic` alone is not enough (about 3 to 5 days for 9 resources)**
- For each resource, add these tests:
  - update in place (step 2 changes a field)
  - import with `ImportState` and `ImportStateVerify` (plus `ImportStateVerifyIgnore` only where justified)
  - disappears: delete out-of-band, then expect a plan that recreates it
  - one invalid-config test using `ExpectError`
  - the optional and nested attributes
- Cover the API edge cases:
  - 404 on read removes the object from state
  - 429 and 5xx retry
  - pagination
  - timeouts
- Add acceptance tests for every data source.
- Add unit tests for the client, for the expand and flatten helpers, and for the tags ordering.
- After you write the tests, break the code on purpose. Make sure the tests fail.

**6. Terraform version matrix (about 0.5 day)**
- Test on latest only today.
- Add a CI matrix over `TF_ACC_TERRAFORM_VERSION`: latest, plus the oldest version you claim to support. Add the prior minors if you want them.
- Match the protocol version in `terraform-registry-manifest.json` to your framework (5 or 6).
- Optionally add an OpenTofu job.

## Likely needed on the registry side (confirm each in the partner portal)

- GPG-signed releases built by GoReleaser, with SemVer tags.
- `terraform-registry-manifest.json`.
- Generated docs and an `examples/` folder for every resource and data source.
- `CHANGELOG.md`.
- `LICENSE` and `SECURITY.md`.
- A named support contact.
- An agreed process for breaking changes.

## Order of work

1. Test org plus scoped key. Then sweepers and `CheckDestroy`.
2. Fix the 3 tag-order bugs.
3. Rework the CI split (blocker 4) and add the version matrix.
4. Add the tests from blocker 5, one resource per PR.
5. Apply for the badge.

Total is about 2 weeks for one person.

**Next, in under 2 minutes:** list the 3 resources that carry `ExpectNonEmptyPlan: true`. Tell me whether tag order carries meaning for users. That decides the set-versus-sort fix.