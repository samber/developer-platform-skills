# CI ports

Contents: parity rule, GitLab, CircleCI, Bitbucket, Azure DevOps, Jenkins, documented snippets.

## Parity rule

- One CLI is the product; every port is packaging. Codecov moved its GitHub Action, CircleCI orb and Bitrise step to the same major on top of one CLI; Snyk's Bitbucket Pipe defaults to the same image as its CLI.
- Keep one input schema (names, types, defaults) and generate or check each manifest against it: `action.yml`, component `spec:inputs`, orb parameters, `pipe.yml` variables, `task.json` inputs.
- Give each port its own semver, bumped by its own contract, and publish one compatibility table mapping each port version to the CLI version range it installs. Moving every port to the same major together (as Codecov did) is simpler when you control all of them from day one.
- Send the same versioned `User-Agent` from each port, with the CI name.
- Drift concentrates in auth (different OIDC claims), output passing and secret masking: test those three per port.

## GitLab CI/CD components

- A component project needs `README.md` and a top-level `templates/` directory (`<name>.yml` or `<name>/template.yml`); up to 100 components versioned together.
- Inputs: `spec: inputs:` header, referenced as `$[[ inputs.name ]]`. When a component has no inputs, omit `inputs:` under `spec:`; an empty `inputs:` key fails release creation.
- Publishing to the CI/CD Catalog requires a release with a semantic version. Consumers may use partial versions (`@1`, `@1.2`) or `~latest`, only for published versions; `~latest` skips pre-releases and can include breaking changes.
- Turning off the catalog toggle destroys catalog metadata; republishing needs a new release.
- Badges: GitLab Partner (namespace verified through the partner program) and verified creator. Premium and Ultimate show 30-day unique-project usage per catalog resource.

## CircleCI orbs

- Production orb versions (`<namespace>/<orb>@1.2.3`) are immutable and cannot be deleted: a bad release is fixed only by a newer one.
- `dev:<label>` versions are mutable and expire after 90 days; use them for pre-release tests.
- URL orbs (hosted at a URL the customer controls, mutable, cached a few minutes) serve customers who block the public registry; they carry no registry immutability.
- One namespace per organization by default; renaming needs CircleCI support, so choose it once.
- Public registry orbs are open source under MIT.
- Partner orbs need customers to allow uncertified orbs in their organization settings; document that step.

## Bitbucket Pipes

- A pipe is a public Docker image plus `pipe.yml` metadata and a README; consumers write `pipe: <account>/<pipe>:<version>`.
- Pin the base image tag, validate required variables first, provide a debug toggle, and push a semver-tagged image from CI.
- Image tags are mutable on the registry; publish each version once and never re-push a tag.

## Azure DevOps tasks

- Ship a task inside a Marketplace extension (`task.json`, published with `tfx`) under a verified publisher.
- Node handler keys: `Node`, `Node10`, `Node16`, `Node20_1`, `Node24`; a `Node20` key does not exist. `Node24` needs `minimumAgentVersion` 4.265.1. Microsoft has put the Node 6, 10, 16 and 20 handlers on the end-of-life path; check the current removal dates in the Azure Pipelines task docs before planning a release.
- Declare both `Node20_1` and `Node24` during a transition, and test on the oldest Windows Server you support: adding `Node24` alone broke at least one task on older Windows agents.
- Authenticate through a workload identity federation service connection when the customer runs on Azure.

## Jenkins

- A plugin is a Maven-versioned release on the Jenkins update center with a minimum Jenkins core version; budget it last unless enterprise customers on Jenkins hold real revenue.

## Documented snippets

For every CI without a native package, publish a tested snippet that:

- downloads a pinned CLI version and verifies its checksum;
- authenticates with that CI's OIDC token where the backend supports it, else a masked variable;
- sets the full Git history when the CLI needs it (`fetch-depth: 0` on GitHub, `GIT_DEPTH: 0` on GitLab);
- uses a glibc base image when the CLI binary is not built for musl.
