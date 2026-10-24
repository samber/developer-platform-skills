# Marrowfield `mfd` CI integrations: priority and corrections

I read `github-action-offering/SKILL.md` and its `ci-ports.md` and `contract-and-release.md` references. I didn't open the live Action or the drafts, so everything below is based on your descriptions.

## Verdict

Build two native ports (GitLab first, Azure DevOps second) and ship tested CLI snippets for the other four. All four drafts have a defect that would have shipped. The "each integration owns its own logic" plan should be dropped.

## Priority

Rank by your paying customers' CI share, not by market popularity (step 8).

| Rank | CI | Share | Share of non-GitHub customers | Deliverable |
| --- | --- | --- | --- | --- |
| 0 | GitHub | 68% | n/a | Live. Audit it against the contract rules once, since every port copies it. |
| 1 | GitLab | 19% | 59% | Native component |
| 2 | Azure DevOps | 7% | 22% | Native task, in the second half of the quarter |
| 3 | CircleCI | 3% | 9% | Tested snippet only |
| 4 | Bitbucket | 2% | 6% | Tested snippet only |
| 5 | Jenkins | 1% | 3% | Tested snippet only; the plugin comes last |

- GitHub plus GitLab covers 87% of customers. Adding Azure DevOps brings it to 94%.
- CircleCI, Bitbucket and Jenkins together are 6%. That is too few customers to repay a second release pipeline each, and one engineer can't maintain five.
- "Huge in the market" is not a ranking input. The ranking input is the survey. The one thing that could change it is revenue weighting: the survey counts customers, and 1% on Jenkins could be large enterprise contracts. Ask for the ARR split before locking the plan. If Jenkins holds real revenue, promote it, but it is still the last native port.

## Correct the PM's premise: no per-port logic

"Each integration owns its own logic so teams can iterate independently" is the failure the skill warns about. A port that reimplements logic drifts within a few releases.

- The `mfd` CLI is the product, and every port is thin packaging over it.
- Keep one input schema (names, types, defaults) and check each manifest against it: `action.yml`, component `spec:inputs`, `task.json`, snippet variables.
- Teams still iterate independently, because each port gets its own semver bumped by its own contract.
- Publish one compatibility table mapping each port version to the CLI version range it installs.
- Send the same versioned `User-Agent` from every port, with the CI name. This gives you usage by CI and version, and it is how you decide next quarter whether CircleCI or Jenkins earns a native port.
- Drift concentrates in auth, output passing and secret masking. Test those three per port.

## Corrections to the four drafts

| Draft | Problem | Fix |
| --- | --- | --- |
| GitLab component with `spec: inputs: {}` | An empty `inputs:` key fails release creation. | Declare real inputs now, with defaults, mirroring `action.yml` names (parity rule). If a component truly has none, omit `inputs:`. Document `@1` or `@1.2` pinning for consumers. `~latest` can include breaking changes. |
| CircleCI orb as `mfd/mfd@dev:latest` for in-place hotfix | `dev:` versions are mutable and expire after 90 days, so customers' pipelines would break silently. Production orb versions are immutable and can't be deleted, so a hotfix in place is impossible by design. | Publish semver (`mfd/mfd@1.0.1`) for fixes. Use `dev:` only for pre-release tests. Choose the namespace once, because renaming needs CircleCI support. Document the "allow uncertified orbs" setting. All of this is deferred anyway, since CircleCI gets a snippet this quarter. |
| Azure DevOps task declaring `Node20` | That handler key doesn't exist. Valid keys are `Node`, `Node10`, `Node16`, `Node20_1` and `Node24`. | Declare `Node20_1` and `Node24` during the transition. `Node24` needs `minimumAgentVersion` 4.265.1. Test on the oldest Windows Server you support, because adding `Node24` alone broke at least one task there. Check current removal dates in the Azure Pipelines task docs. |
| Bitbucket pipe re-pushing the `1.0.0` image tag | Registry tags are mutable. Customers pinned to `1.0.0` get changed code with no notice, which is a supply-chain risk. | Publish each version once and never re-push a tag. A fix is `1.0.1`. Pin the base image by digest. Validate required variables first and add a debug toggle. Deferred anyway, since Bitbucket gets a snippet this quarter. |

## The glibc constraint (not in your drafts)

`mfd` is glibc-linked on Linux. Anything that runs it on musl, such as Alpine, fails.

- **GitLab:** set the component's default `image` input to a glibc image (Debian or Ubuntu based), pinned by digest. Don't default to Alpine.
- **CircleCI, Bitbucket and Jenkins snippets:** use a glibc base image in every example. The Bitbucket pipe image, if built later, must be glibc too.
- **Azure DevOps:** the task must pick the right binary per agent OS, because agents run Windows, macOS and Linux. A container-based design would cover Linux only, so don't use one.
- **All snippets:** download a pinned CLI version and verify it against a digest committed to your repo or a signature checked against a pinned signer. Don't use a checksum file from the same download origin. Set full Git history when `mfd` needs it (`GIT_DEPTH: 0` on GitLab).

## Quarter plan (one engineer, about 12 weeks)

1. **Week 1: shared foundation.**
   - Write the canonical input schema and the compatibility table.
   - Write one install script: pinned version, digest-verified, glibc-aware, with mirror URL and proxy support.
   - Add the `User-Agent` convention.
   - Start the Azure DevOps publisher verification now. It has lead time and blocks the Azure release.
2. **Weeks 1-2: snippets for all six CIs.**
   - Cover CircleCI, Bitbucket, Jenkins, GitLab and Azure DevOps, plus the existing GitHub example.
   - Each snippet uses the shared install script, that CI's OIDC token where the backend supports it (else a masked variable), and a glibc image.
   - This ships coverage for the 6% right away.
3. **Weeks 3-7: GitLab component.**
   - Inputs mirror `action.yml`.
   - Release with a semantic version to the CI/CD Catalog.
   - Test auth, outputs and secret masking.
   - Start with GitLab ID tokens (OIDC) if the backend supports them.
4. **Weeks 8-11: Azure DevOps task.**
   - Handlers are `Node20_1` and `Node24`.
   - Ship a Marketplace extension under the verified publisher.
   - Use a workload identity federation service connection for customers on Azure.
   - Test on Linux, Windows and macOS agents, including the oldest supported Windows Server.
5. **Week 12: buffer and measurement.**
   - Read `User-Agent` telemetry by CI and version.
   - If Azure slips, cut it to the snippet. Don't cut the parity tests.

## Next-quarter decision rule

Promote a snippet to a native port only when telemetry shows real weekly active repositories on it, or the ARR split justifies it. Order the candidates by that evidence, not by market buzz. The Jenkins plugin (Maven release, minimum core version) is the last candidate.

## Assumptions to confirm

I had no answers to the interview questions, so this plan is provisional on these.

| Assumption | Step it drives |
| --- | --- |
| The survey counts customers, not revenue. | Priority ranking |
| The `mfd` backend can't yet validate external OIDC tokens. | Auth wiring. Key input now, with `auth: auto|oidc|key` so OIDC lands as a minor. |
| GitLab customers are mostly gitlab.com or a recent self-managed release with the CI/CD Catalog. | GitLab component viability |
| Azure DevOps customers include Windows and macOS agents. | Task platform handling |
| The live GitHub Action already satisfies the six contract rules (SHA-pinned nested `uses:`, digest-verified binaries, no input in shell as code). | Port parity. Verify this first, since the ports copy its schema and auth shape. |