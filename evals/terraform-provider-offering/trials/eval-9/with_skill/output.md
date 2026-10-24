# Terraform provider plan: `terraform-provider-ridgeway`

**Next action (today):** send the 8 questions in §2 to the API owner and the provider team. Every gate cell below is UNKNOWN until they answer, and UNKNOWN counts as FAIL.

## 1. Verdict

| Leadership ask | Verdict | What we do instead |
| --- | --- | --- |
| Partner Premier by Q2 | ✅ Feasible if Partner lands first | Migrate to the Plugin Framework by mux, then Partner, then Premier constructs. |
| "Full parity with Terraform 1.14" | ❌ Wrong target | Ship list resources and actions only where an API object fits. Premier needs one of identity plus list, ephemeral resources or actions, and an SBOM. |
| List resources and actions for every resource | ❌ | List needs a list endpoint plus identity. Actions are for imperative day-2 operations. Neither exists for most config objects. |
| Big-bang v2.0.0 rewrite on the Framework | ❌ | Incremental mux migration in minors. A major ships only for a real breaking change, and only after a deprecating minor. |
| Two sprints | ⚠️ Not credible | About 4.5 months of work, with the Premier submission around mid-March 2027. This is an estimate until Q5 (team size) and the gate matrix are answered. |

**Path (step 1):** vendor-owned, hand-written, on the Plugin Framework, migrated resource by resource behind a mux.

- It ranks first on durability and second on value.
- I rejected a generated full rewrite. It is the starved rung, worth promoting only past about a hundred resource types, and we have 22.
- Interview Q6 (target tier) moved the path. A Partner target plus an SDKv2 base means the mux migration of the core resources comes before the badge request.

**Why the big-bang fails the contract:**

- *Rule 3:* removals, renames and type changes ship only in a major, after a minor that deprecated them. A "rewrite" with no deprecating minor behind it breaks this.
- *Failure mode:* a full-coverage rewrite shipped as a major means broken resources for months.
- *Parity:* a Framework migration with identical schemas produces no diff, so it is a minor. "v2.0.0" gains nothing toward the badge.
- *Cadence:* majors come at most once a year, staged behind a beta.

## 2. Open questions

Each unanswered question stays UNKNOWN, so the dependent gate rows stay FAIL.

1. **"Inherited" from whom?** Who owns the GitHub org and namespace today, and is it the final one? Rule 6: an address change is a migration for every user. Who holds the signing key?
2. **Registry state.** Is the signing key RSA, and is it registered on both the Terraform and OpenTofu registries? OpenTofu is 30% of installs. Without a registered key, users who set `OPENTOFU_ENFORCE_GPG_VALIDATION=true` cannot install.
3. **Partner application.** What exactly is pending, since SDKv2 blocks Partner? Who is the program contact, and can the application stay open while we migrate? Also confirm the Premier requirements in writing.
4. **Team (Q5).** Who owns the provider, what is their Go experience, and who is on call for the issue queue? Partner means fixing critical issues in 48 hours and others in 5 business days. Do nightly acceptance tests already run in GitHub Actions, against a sandbox account?
5. **Version floor (Q6).** What is the oldest Terraform and OpenTofu version customers run?
6. **API shape (Q4), for each of the 22 resources:**
   - stable ID;
   - GET returns every writable field;
   - idempotent create;
   - propagation delay;
   - async operations and whether the 202 body carries the object ID;
   - list endpoint, and whether it is ordered;
   - rate limits.
7. **Demand and usage.** Downloads per resource, open issues reporting a perpetual diff or "inconsistent result after apply", and any deals asking for Premier.
8. **Q2.** Does it mean calendar April to June 2027? Is the date fixed, or is "Partner Premier" the real goal?

I am assuming Q2 = April to June 2027 and that the team is small. I am also assuming the manifest and the code disagree today (see §3).

## 3. The manifest says protocol 6.0 on SDKv2

SDKv2 serves protocol 5 (`["5.0"]`). The manifest claims 6.0, so the metadata and the binary disagree.

1. **Verify before fixing:**
   - Download the 1.8.0 `_manifest.json` release asset.
   - Run `terraform init` and `tofu init` on a clean machine.
   - Record what the Registry shows.
2. **Preferred fix:** make the claim true by shipping the mux skeleton as **1.9.0** first.
   - All 22 resources stay on SDKv2 behind `tf5to6server` plus `tf6muxserver`.
   - No schema changes.
   - The binary then serves protocol 6 and the manifest is correct.
   - Docs and NOTES state the Terraform 1.0+ floor, since protocol 6 needs it. Record this as a decision.
3. **Fallback:** if the skeleton cannot ship within about 2 weeks of discovery, ship **1.8.1** with `5.0`, then flip to `6.0` at the skeleton.
4. Never edit or retag 1.8.0. Fix forward.

## 4. Step 2: API readiness gate

Make 22 columns, one per resource, and fill the nine rows below per object. Cell values are PASS, FAIL, UNKNOWN or COMP.

```
| Check                              | <resource 1..22>       | Owner | Due |
| Stable server-assigned ID          | UNKNOWN                |       |     |
| GET returns writable fields        | UNKNOWN                |       |     |
| In-place update                    | UNKNOWN                |       |     |
| Idempotent create                  | UNKNOWN                |       |     |
| Bounded propagation (seconds)      | UNKNOWN                |       |     |
| Pollable async op, ID in 202 body  | UNKNOWN                |       |     |
| Deterministic normalization/order  | UNKNOWN                |       |     |
| Secrets identified                 | UNKNOWN                |       |     |
| Documented rate limits             | UNKNOWN                |       |     |
```

- **Shortcut for 20 of the 22:** the resources already exist in v1.8.0, so existing acceptance tests and the open-issue list are evidence. A resource with open perpetual-diff issues is not PASS on "GET returns writable fields".
- **Cut rule:** a resource with a FAIL not fixed by its batch date moves to the next minor. It never ships a Framework version with a known perpetual diff.
- **Identity and list rows:** add `list endpoint exists and is paginated` and `list order stable`. They decide §7.
- **Routing:**
  - idempotency: `api-idempotency-retry`;
  - rate limits: `api-rate-limit-policy`;
  - sandbox: `api-test-mode-design`;
  - API fixes: `public-api-design-review`.

## 5. Step 3 and 4: resource map and migration rules

Fill the resource map per resource. The columns are: construct, type name, ID and import grammar, mutable fields, replace-only fields, preserved fields, secrets kind, set or list, consistency class, and timeouts.

The preserved-fields column feeds `ImportStateVerifyIgnore`.

**Migration is behaviour-preserving.** Every improvement lands as an additive minor or goes on the v2 backlog.

- Keep every attribute name, type and `id`.
- Keep blocks as blocks. Nested attributes change the HCL syntax.
- Decide null explicitly. SDKv2 collapsed unset values into zero values.
- Do not switch List to Set, add a default that differs from the API, or tighten validation. Each of those is a major.
- Do not turn an existing secret into a write-only argument. Add the `<name>_wo_version` form beside it with `ConflictsWith` and `PreferWriteOnlyAttribute`. Write-only needs 1.11+ on both Terraform and OpenTofu.
- Keep the `Sensitive` attribute for anything below 1.11.
- Add `RequiresReplace` only where the API cannot update.
- Apply `UseStateForUnknown` to stable computed values.
- Add validators only if they reject values the API already rejects.
- Add bounded waiters on typed errors after create, update and delete.
- Import by plain ID stays on every resource.

**Per migrated resource, all four are required:**

1. The old acceptance tests pass unchanged.
2. An upgrade test: apply with the last released version, plan with the new build, expect an empty plan.
3. Import-config generation (`-generate-config-out`), then `terraform validate` on the result.
4. `_disappears`, plus an update test per mutable attribute.

Never set `ExpectNonEmptyPlan`.

## 6. Schedule

Week 1 is the week of 2026-10-26. All dates are proposals, to be replaced once Q4 and the gate are answered.

| Weeks | Track A: provider | Track B: release, registry, API | Decision |
| --- | --- | --- | --- |
| 1-2 | Answer §2. Verify the manifest. Audit the open-issue queue. | File API asks for every FAIL. Confirm key and namespace on both registries. Contact the Partner program. | D1: path confirmed, namespace final |
| 3-4 | Fill the gate matrix and resource map. Ship the mux skeleton as **1.9.0**. | Add a `tofu` lane and nightly CI. Set up sweepers. Verify `terraform init` and `tofu init` with GPG enforcement. | D2: batch assignment and cut list |
| 5-7 | Batch 1: the most-used resources, about 5-6, as **1.10.0**. | Partner program update with migration evidence. | D3: submit or update the Partner request |
| 8-11 | Batch 2 as **1.11.0**. | Docs generation. Upgrade guide stubs. | |
| 12-15 | Batch 3 as **1.12.0**. Identity and list resources for the eligible long-lived objects. | SBOM through a GoReleaser `sboms` section (Syft). Confirm the layout with the program. | D4: Premier constructs chosen |
| 16-19 | Batch 4 as **1.13.0**. All 22 on the Framework, mux removed. | Premier package. | D5: Premier submission, about mid-March 2027 |
| 20+ | Fixes and review turnaround. | April to June slack for program review. | |

- A winter-holiday gap is built in around weeks 8-9.
- **Release rule:** tag only from a green nightly, with a `moved`-safe changelog and regenerated docs. Never delete or retag a version.
- **Cut order if time runs out:** actions, then functions, then list resources, then the least-used data sources. Never cut import support or upgrade tests.
- **Two sprints, if leadership insists:** the skeleton plus Batch 1 fits. That gives the mux, protocol-6 truth, and the most-used resources on the Framework, plus a stronger Partner application. It is not Premier.

## 7. Partner Premier constructs

Premier needs at least one of identity plus list resources, ephemeral resources or actions, plus an SBOM. Pick by API fit, in this order.

1. **Identity plus list resources** for long-lived configured objects that have a paginated list endpoint and a stable order. This is the best candidate, because it gives bulk import and `terraform query`. Start with the 3-5 most-used objects that pass the gate, then expand by demand.
2. **Ephemeral resource** if the API mints short-lived tokens that another resource consumes.
3. **Actions** only for imperative operations that leave no object, such as rotate, restart or invalidate. Expect a handful, not 22. Cut them first when time runs out.
4. **Provider functions** are lowest priority.

**Parity table** (fill after the gate):

```
| Resource | Identity | List resource | Action | Reason if none |
```

For each cell, write a construct or a reason. "No list endpoint" and "no imperative operation" are valid answers. "Left out" is the correct outcome for transactional records.

**Compatibility:**

| Construct | Terraform | OpenTofu |
| --- | --- | --- |
| Identity | 1.12+ | 1.12+ |
| List resources | 1.14+ | not implemented |
| Actions | 1.14+ | not implemented |
| Write-only arguments | 1.11+ | 1.11+ |

- List resources and actions do nothing for OpenTofu's 30%. Nothing breaks for them, since every resource still imports by plain ID. Re-check OpenTofu's changelog before each major, because parity moves.
- Tests for list resources and actions skip below Terraform 1.14. The `tofu` lane skips both.
- Actions are tested through `lifecycle.action_trigger`, with API-side assertions afterwards.

## 8. OpenTofu (30% of installs)

- **Submit the provider and the key** through the `opentofu/registry` web issue forms. API, CLI and PR submissions are closed unprocessed.
- **Key rules:** the submitter must be a public member of the GitHub org, and OpenTofu checks key expiry on submission.
- Without the key, strict users cannot install the provider.
- Add `tofu` as a second CI lane via `TF_ACC_TERRAFORM_PATH`.
- Announce the Terraform 1.0+ floor and the 1.11+ requirement for the new write-only arguments in the same NOTES entry.

## 9. Versioning and deprecation

- **No v2.0.0 now.** Every release above is a minor.
- **v2 backlog:** add to it any finding that is a real break, such as List to Set fixes, attribute renames, validation tightening or default corrections. Deprecate each item in a minor first, with an actionable `DeprecationMessage`.
- **When to cut v2.0.0:** only when the backlog justifies it, no sooner than 12 months after the previous major, and not before the Premier decision.

Before any major:

1. Ship a final minor of 1.x that deprecates everything the major removes.
2. Run betas (`v2.0.0-beta1`) with the upgrade guide published at the first beta.
3. Run upgrade tests from the last release of every supported 1.x.
4. Keep security and critical fixes on 1.x for a stated window, and track the share of downloads still on it.

**If leadership needs a "2.0" story:** the story is the Framework, protocol 6 and Premier, and none of that requires a major.

## 10. Measure

The provider passes when all hold:

- Every resource's acceptance suite passes with no `ExpectNonEmptyPlan`.
- Upgrade tests pass from the last 1.x release.
- `terraform init` and `tofu init` with `OPENTOFU_ENFORCE_GPG_VALIDATION=true` both install the latest version.
- No removal has shipped in a minor.

Also track:

- downloads by version;
- open perpetual-diff and "inconsistent result" issues (none older than one release cycle);
- nightly flake rate per resource;
- deals or reviews where the tier came up.

## 11. Failure modes to watch

- A resource migrated while its gate row is UNKNOWN. This produces a perpetual diff under a new label.
- A "harmless" improvement that is a major: type change, new default, or stricter validation.
- A missing state upgrader. Every released schema version needs one.
- Unsigned or retagged releases.
- Acceptance tests in a production org, or on fork PRs with secrets.

## 12. Memory block

Record this in `developer-platform-context.md`, or in the memory system in use.

- Chosen path and the manifest decision.
- Gate matrix location.
- Resource map.
- Namespace and signing key owner.
- Minimum Terraform (1.0) and OpenTofu versions.
- Deprecation schedule and the v2 backlog.

## Rejected

- Generated full rewrite.
- v2.0.0 as the migration vehicle.
- List resources and actions for all 22 resources.
- Withdrawing the pending Partner application before talking to the program.
- Changing the manifest by editing the existing 1.8.0 release.