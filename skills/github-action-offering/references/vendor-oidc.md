# Vendor-side OIDC

Contents: flow, backend validation, trust binding, claim formats, precedents, fork pull requests, PR comments, other CI systems.

## Flow

1. The customer's job grants `permissions: id-token: write`.
2. The action requests a token for the vendor audience: `core.getIDToken('<vendor-aud>')` in JavaScript, or from a composite step `curl -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=<vendor-aud>"`.
3. The action posts the JWT to the vendor token-exchange endpoint.
4. The backend validates it, matches a customer trust binding and returns a short-lived vendor token scoped to that binding.
5. The action masks the vendor token (`core.setSecret` or `::add-mask::`) before anything else and uses it for the run.

## Backend validation

- Issuer is exactly `https://token.actions.githubusercontent.com`. GHES issues tokens from `https://<host>/_services/token`, usually unreachable from a SaaS backend: accept a customer-registered issuer whose JWKS the customer exposes through an allowlist, or an uploaded JWKS with a rotation procedure, or declare GHES key-only.
- Signature verifies against the issuer's JWKS; cache keys, refetch on unknown `kid`.
- `exp`, `nbf`, `iat` within a small clock skew.
- `aud` equals the vendor audience. A blank or default audience accepts tokens minted for other services.
- At least one trust binding matches. Issuer plus audience alone is never enough: the issuer is shared by every GitHub customer, so it accepts any org's workflow.
- Exchanged vendor token lives minutes, carries the binding's scopes only, and is logged with the claims that matched.

## Trust binding

Let the customer bind a vendor project to:

- `repository_owner_id` (required) and `repository_id` (recommended): numeric, never reassigned.
- One of: `ref` (e.g. `refs/heads/main`), `environment` (e.g. `production`), or `job_workflow_ref` for a reusable-workflow-only policy.
- Optionally `event_name` to refuse `pull_request_target`.

Show the binding in the vendor UI with the exact claim values a sample token would need, and a "test with a real run" button that logs the last rejected token's claims.

## Claim formats

- Old `sub`: `repo:octo-org/octo-repo:ref:refs/heads/main`.
- Immutable `sub`: `repo:octo-org@123456/octo-repo@456789:ref:refs/heads/main`. Default for repositories created, renamed or transferred after 2026-07-15 on github.com; older repositories opt in; not on GHES. An earlier hyphen-delimited draft allowed name squatting and was replaced by `@`.
- Organizations can customize the `sub` template, so string-matching `sub` is fragile. Match individual claims instead.

## Precedents

| Vendor | Entry point | Scoping |
| --- | --- | --- |
| AWS | `configure-aws-credentials`, `role-to-assume` | `aud: sts.amazonaws.com`; IAM conditions on `sub`. Its README trust policies broke for new repos on the immutable `sub` change. |
| Google Cloud | `google-github-actions/auth`, direct workload identity federation | Pool provider attribute conditions. |
| JFrog | `setup-jfrog-cli` `oidc-provider-name`, `oidc-audience` | Configured audience plus identity mappings on claims; warns a blank audience accepts any. |
| Pulumi Cloud | OIDC token exchange | Registered issuer, audience, trust policy; warns that issuer plus audience accepts other orgs. |
| Codecov | `codecov-action` `use_oidc: true` | Vendor-fixed audience. Shipped separate fixes for forks and for OIDC leaking into tokenless mode. |

## Fork pull requests

- `pull_request` runs from forks get a read-only `GITHUB_TOKEN`, no secrets and no `id-token: write`.
- Pick one behaviour and document it: tokenless read-only mode where the product allows it for public repositories, or exit with a message that names the limitation.
- Never recommend `pull_request_target` to get credentials on fork PRs: it runs with base-repository secrets, and GitHub blocks it by default in public repositories from 2026-12-02.
- When results must reach a fork PR, document a two-workflow split in the customer's repo:
  1. A `pull_request` workflow runs the action without credentials (or in tokenless mode) and uploads the result as an artifact.
  2. A `workflow_run` workflow names the first workflow in `workflows:`, runs only on `conclusion == 'success'`, and has `actions: read` plus `pull-requests: write`. It downloads the artifact by run ID and validates it as data (schema, size).
  3. It resolves the PR from `workflow_run.head_sha` through the API (`GET /repos/{owner}/{repo}/commits/{sha}/pulls`) and requires that PR's head SHA to equal it: `workflow_run.pull_requests` is empty for fork PRs, and a PR number inside the artifact is attacker-controlled.
  4. It never checks out or executes fork code.

## PR comments

- Permissions: `pull-requests: write` (and `issues: write` for issue-style comments), nothing else.
- Upsert one comment per action and job, found by a hidden marker (`<!-- vendor-action:scan -->`) authored by the token's own identity, instead of a new comment per push; anyone can post the marker.
- GitHub caps a comment body at 65,536 characters: truncate, and link to the job summary for the full result.
- In public repositories, assume the comment is public: never echo secrets, internal hostnames or full infrastructure diffs; show counts and identifiers, link the details behind vendor login.
- Escape any text taken from the PR (titles, file names) before it goes into Markdown.

## Other CI systems

Each port reuses the same token-exchange endpoint with its own issuer and claims:

- GitLab: `id_tokens:` keyword with a custom `aud`; claims include `project_id`, `namespace_id`, `ref`, `environment`.
- CircleCI: OIDC token in the job environment; claims carry organization and project IDs.
- Bitbucket Pipelines: OIDC per step when enabled; claims carry workspace and repository UUIDs.
- Azure DevOps: workload identity federation through a service connection.

Normalize all of them into one trust model in the backend: owner ID, repository or project ID, ref or environment. Customers then read one binding screen whatever CI they use.
