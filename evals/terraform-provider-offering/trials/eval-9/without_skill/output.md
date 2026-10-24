# terraform-provider-ridgeway: plan to Partner Premier

I didn't inspect the provider repo, so everything below comes from your description. Items marked **verify** are assumptions to check first.

## Next action (30 min, before any planning meeting)

Find out what the manifest actually does. Run these in a scratch directory outside the repo.

1. Ask the released binary which protocol it speaks:
   `TF_PLUGIN_MAGIC_COOKIE=d602bf8f470bc67ca7faa0386276bbdd4330efaf76d1a219cb4d6991ca9872b2 ./terraform-provider-ridgeway_v1.8.0`
   The output looks like `1|5|unix|...|grpc`. The second field is the protocol. SDKv2 should print 5.
2. Ask the registry what it advertises: `curl -s https://registry.terraform.io/v1/providers/<ns>/ridgeway/versions`. Then check the OpenTofu registry the same way.
3. Compare the two results. If the binary says 5 and the registry says 6.0, you have a metadata bug in every release since the manifest was added.

## Recommendation: no big-bang v2.0.0

I recommend an incremental migration instead, for these reasons.

1. **Two sprints is not credible.** Moving 22 resources from SDKv2 to the Framework is a state-compatibility project. Null versus empty values, Set versus List, timeouts, import, state upgraders and `SchemaVersion` all change. A silent diff on existing state is the main risk. A rewrite plus new features in one release gives you no way to bisect a regression.
2. **"List resources and actions for every resource" is semantically wrong.**
   - List resources need a list API. Actions are for operations that are not CRUD, such as restart, rotate or invalidate.
   - Some resources will have neither. Shipping empty or fake ones adds maintenance cost and no user value.
3. **You don't need a rewrite to start.** `terraform-plugin-mux` runs SDKv2 and Framework resources in one provider. You can migrate one resource at a time with no state change.
4. **v2.0.0 is only for real breaking changes.** An internal rewrite is not one. Ship it as v1.x minors and keep v2 for a deliberate cleanup, if you ever need one.
5. **The pending Partner badge review is a reason to avoid churn.** Don't change what reviewers are looking at without asking.

## Assumptions to confirm with HashiCorp and leadership

- **What does Premier require?** I can't confirm the criteria from memory. Ask your HashiCorp partner contact for the written requirements. If "Terraform 1.14 parity" is not among them, that changes the whole scope.
- **What does leadership mean by "parity"?** Likely it is competitive pressure. Offer a concrete definition: Framework-based provider, list resources and actions where the API supports them, and tests on Terraform 1.14.
- **OpenTofu (30% of installs).**
  - **Verify** against the current OpenTofu release notes. As far as I know, OpenTofu does not implement list resources, `terraform query` or actions.
  - Those features give 30% of users nothing. The provider must keep working there, and the new RPCs must be inert.
  - Confirm the provider is published in the OpenTofu registry and its signing key is registered.

## Phases

Dates assume you start in late October 2026. Q2 2027 gives about 5 months, and each phase has an exit gate.

### Phase 0: facts and quick fixes (weeks 1–2)

1. Run the protocol check above and write down the result.
2. **If the manifest is wrong:**
   - Fix it in a patch release, 1.8.1.
   - Declare 5.0 while you are still on SDKv2, or 6.0 only once the binary really serves 6.
   - Add a CI check that fails when the manifest and the binary disagree.
   - Add a release-time step that runs the magic-cookie handshake and compares the protocol.
3. **Resource inventory.** One row per resource, with these columns:
   - list API available (yes or no)
   - non-CRUD operations
   - schema complexity (nested blocks, sets, computed-only fields)
   - install or usage weight, if you have telemetry
   - existing test coverage
   This table decides what gets a list resource, an action, or nothing.
4. **Questions to settle:**
   - Premier criteria.
   - Support policy for Terraform and OpenTofu versions.
   - The Partner badge review status. Ask whether releases during review are fine.

Exit gate: the manifest is true, the inventory is done, and the Premier requirements are in writing.

### Phase 1: mux foundation, no behavior change (weeks 3–6)

1. Add `terraform-plugin-framework` and `terraform-plugin-mux`. Serve one protocol version consistently.
   - Choose 6 if you want the manifest to be true as it stands.
   - Serve the SDKv2 side through `tf5to6server`, then combine with `tf6muxserver`.
2. Move zero resources in this phase. Ship the empty Framework provider alongside the SDKv2 one.
3. Test on every supported version of Terraform and OpenTofu, using the real binaries in CI.
4. Release as v1.9.0.

Exit gate: all acceptance tests are unchanged and green on the Terraform and OpenTofu matrix, and no state diff appears on a real upgrade.

### Phase 2: migrate resources in waves (weeks 7–16)

1. Migrate in waves of 3 to 5 resources, simplest first, with the highest-risk resources last. One wave per minor release.
2. **Per-resource gate.**
   - Run an upgrade test: create state with the previous release, then plan with the new one. It must show an empty plan.
   - Cover import, null and empty values, and every sensitive and computed attribute.
   - Keep the existing tests unchanged. If a legacy test has to change, treat that as a regression in the migration.
3. Treat `SchemaVersion` and state upgraders explicitly. Test the upgrade path from several old provider versions, not only 1.8.0.
4. Keep the SDKv2 and Framework implementations of a resource from coexisting. Remove the SDKv2 version in the same PR.

Exit gate: all 22 resources are on the Framework and upgrade tests are green.

### Phase 3: list resources and actions (weeks 12–20, overlapping Phase 2)

1. Start once the first migrated resources are stable. Only resources that are already on the Framework can get them.
2. Build list resources only where the inventory shows a list API. Build actions only for real non-CRUD operations.
3. Document every new feature as "requires Terraform 1.14 or later, not available on OpenTofu".
4. Test with Terraform 1.14 acceptance tests. Make sure Terraform below 1.14 and OpenTofu still plan and apply normally.

Exit gate: each shipped list resource or action has an acceptance test and documentation.

### Phase 4: Premier submission (weeks 18–22)

1. Close the remaining Premier requirements once you have them in writing.
2. Check docs, examples and the changelog. Make sure the registry listing is correct.
3. Submit, then handle review feedback.

## OpenTofu strategy

- Keep a CI matrix with the real OpenTofu binary and the same acceptance suite.
- Never make a basic resource require a Terraform 1.14 feature.
- State clearly in the docs and changelog which features are Terraform-only.
- Watch OpenTofu's roadmap. If it adds support later, enabling it should be a small change.

## Risks

| Risk | Mitigation |
|---|---|
| Silent state diffs after migration | Upgrade tests from old versions, empty-plan assertion per resource |
| Manifest and binary disagree | CI check, plus the Phase 0 fix |
| Premier criteria differ from leadership's belief | Get them in writing in Phase 0 |
| Feature work with no user value | Inventory-driven scope, with no list or action where there is no API |
| Regression hits the OpenTofu 30% | Tofu in the CI matrix from Phase 1 |
| Badge review disrupted | Ask the partner contact, keep changes incremental |
| Schedule slip | Hard gates per phase, with Premier-critical work first |

## What to tell leadership

> We can reach Premier by Q2, but not through a two-sprint rewrite. A big-bang v2.0.0 risks corrupting customer state and breaks 30% of our installs' expectations, because OpenTofu doesn't support the new features. We'll migrate incrementally with no breaking releases, ship the Terraform 1.14 features where the API supports them, and confirm the exact Premier requirements this week.

## Open questions for you

1. Do you have telemetry on installs per resource, to order the migration waves?
2. Which Terraform and OpenTofu versions must you support?
3. Does the badge review have a deadline, or can it run in parallel?
4. Do you want me to turn this into tickets once Phase 0 is done?