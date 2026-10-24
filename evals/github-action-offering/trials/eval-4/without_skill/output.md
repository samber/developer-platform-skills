# Teardown: OIDC for `ashgrove/deploy-action`

I wrote this from your description alone. I read no code, and I did not check the GitHub/GHES claim formats against current docs. Items marked **verify** need a check before they go in the spec.

## Verdict

Don't ship as designed. 🔴 Three blockers: the auth check proves nothing, the pattern match is bypassable and squattable, and your two biggest customers can't use it. The silent fallback is a fourth serious problem, because it makes failed deploys look green.

## 🔴 Blockers

### 1. "Valid signature + `iss` + `aud` present" authenticates nobody

- GitHub signs a token for any workflow in any repo on earth. Passing those checks only proves the caller is some GitHub Actions job somewhere.
- Authentication has to be the bound identity: this token maps to exactly one Ashgrove project through a trust policy. No match means no token. Never return a "valid but unlinked" state.
- "`aud` is present" is not an audience check. The default `aud` is the repo owner's URL (e.g. `https://github.com/<org>`), which the customer controls.
- Any third-party action in the same job can request an ID token with the default audience. Any service that receives one can replay it to you.
- Fix:
  - The action requests a fixed Ashgrove audience, preferably per tenant (e.g. `https://api.ashgrove.com` or `ashgrove:<tenant-id>`).
  - The server requires an exact `aud` match.
- Also required:
  - Allow `alg` RS256 only. Reject `none` and HS*.
  - Enforce `exp`, `nbf`, and `iat` with small clock skew.
  - Cap token size before parsing.
  - Keep a `jti` replay cache that lasts for the token's `exp` window.
  - Fail closed when the JWKS can't be fetched. Allow stale-cache use only within a bounded window.
  - On an unknown `kid`, refetch the JWKS with rate limiting, so a flood of forged `kid`s can't turn your endpoint into a JWKS-fetch amplifier.

### 2. Matching a typed pattern against `sub` is the weakest possible binding

- **`*` is too broad.** `repo:org/repo:*` matches `…:pull_request`, any branch, and any environment. Anyone with write access can push a branch with a modified workflow and deploy to the linked project. The default `sub` carries no event or workflow identity beyond `ref`/`environment`.
- **`pull_request_target`.** The `sub` looks like a base-branch ref run, but the job may check out fork code. Match on `event_name` too.
- **Names are mutable.** A repo rename, transfer, or delete-and-recreate means someone else can end up holding `repo:org/repo`. Bind on the immutable numeric claims `repository_id` and `repository_owner_id`, captured at link time. Keep `sub` as a secondary, human-readable constraint.
- **Glob semantics are undefined.**
  - Does `*` cross `:` and `/`?
  - Does `repo:org/repo*` match `repo:org/repo-evil`?
  - Is matching case-sensitive? GitHub names are case-insensitive.
  - Pick exact-match by default, a fully anchored match for anything else, and write test vectors for each case above.
- **Custom `sub` templates.** Orgs and repos can customize the `sub` claim, and GHES can too. A hand-typed `sub` pattern breaks silently when that changes, or matches something unintended.
- **Squatting.** Nothing proves the person typing `repo:bigorg/*` controls `bigorg`.
  - An attacker pre-links `repo:bigorg/*` to their own project. When BigOrg later adopts the action, its workflows exchange into the attacker's project, which leaks deploy artifacts and metadata.
  - Two projects that claim overlapping patterns are the same problem.
  - Fixes, pick one or more:
    - Require the action to name the project (`project: <id>`) and match only inside that project's policy.
    - Verify ownership of the org/repo, for example through a GitHub App install or an admin-confirmed handshake.
    - Make links unique per `(issuer, repository_id)`.
- **Typo-driven over-broadening.** Replace typed patterns with a "detected workflows" flow.
  - A failed exchange records the claims it saw.
  - An admin sees "repo X, ref main, env prod" in the UI and clicks to trust it.
  - Offer sensible narrow defaults: environment, or `ref` + `job_workflow_ref`. Warn on or block a bare `*`.
- Log every link, unlink, and edit in an audit trail, restricted to an admin role.

### 3. Hard-coded `iss` excludes your two biggest accounts

- GHES doesn't issue from `https://token.actions.githubusercontent.com`. I believe it uses `https://<ghes-host>/_services/token` with JWKS under `/.well-known/jwks` (**verify** for 3.15). GHEC enterprise-specific issuers and `*.ghe.com` data-residency tenants use other issuers too.
- Issuer must be a per-tenant allowlist: `{issuer, jwks source, audience}`. Every binding is keyed by `(issuer, repository_id, …)`.
  - Numeric repo and owner IDs collide across GHES instances and github.com.
  - Never accept an arbitrary issuer. Anyone can run their own OIDC provider and mint any claim.
- Reachability: a typical GHES sits behind a firewall, so your SaaS can't fetch its JWKS.
  - Options: the customer exposes the discovery and JWKS endpoints, uploads the JWKS manually (rotation burden), or you run a relay/agent.
  - If you fetch customer-supplied URLs, you have an SSRF surface. Allowlist per tenant, resolve and pin IPs, and block link-local and metadata ranges.
  - Ask these two accounts what is feasible now. It decides the architecture.
- Check the action itself on GHES 3.15:
  - How is the action resolved on GHES (GitHub Connect, or a mirrored copy)?
  - Which Node runtime does 3.15's runner support?
  - Can the runner reach the Ashgrove API from inside their network?
  - Are there custom CA or proxy requirements?
  - Does `ACTIONS_ID_TOKEN_REQUEST_URL` exist there? OIDC should be available on 3.15, but test it rather than assume.
- Put a real GHES 3.15 instance in the test matrix before the design is final.

## 🟠 Serious

### 4. Silent fallback to api-key, then to anonymous

- A deploy action that exits 0 without deploying is the worst failure mode. What does "read-only" mean for a deploy? If it does nothing, the pipeline is green and production is stale.
- The most common OIDC failure is a missing `permissions: id-token: write`. That produces silent success in anonymous mode instead of a one-line fix.
- It hides your own outages. A 5xx from `/v1/token/exchange` degrades quietly. You get no error signal, and customers get no signal that they are insecure or broken.
- It defeats the goal. Customers keep the pasted key "just in case", and you can't tell who has migrated.
- Downgrade: anything that forces exchange failure lands on the weaker credential.
- Fix:
  - Add an explicit `auth` input: `oidc | api-key | auto`.
  - Make `auto` choose by what is present (api-key given means key, otherwise OIDC), not by what succeeded.
  - On 4xx, fail with the specific reason (no `id-token` permission, no matching policy, wrong audience).
  - On 5xx or network errors, retry with backoff, then fail.
  - Make anonymous an opt-in (`mode: anonymous`), or choose it deliberately for fork PRs. That case is legitimate, since secrets are unavailable there.
  - Emit an `auth-method` output and a `::notice::` line saying which method was used.

### 5. "v3 because required input" is half the story

- Making `api-key` optional is not breaking by itself. It would be a minor release. Forcing a major means every customer edits their pin, which adds adoption friction for a feature meant to remove friction.
- The real break is behavioral. In v2 a missing or typo'd key fails loudly. In the current v3 design it passes silently in anonymous mode.
  - Either fix #4 and ship OIDC as v2.x with `api-key` optional, or
  - keep v3, state the break honestly, and ship a migration guide, a codemod or Dependabot note, a v2 security-fix window, and an api-key deprecation date.
- Needed in the docs and in error messages:
  - `permissions: id-token: write` must be set on the job (job-level, not workflow-level).
  - Adding it lets every action in that job mint tokens for any audience, so third-party actions get that power.
  - If a workflow sets `permissions:` explicitly and omits `id-token`, the action must detect the missing env vars and explain exactly that.
- Define precedence when both api-key and OIDC are available. The `auth` input in #4 solves it.

## 🟡 Gaps to specify

- **Exchange response.** The doc says "counts as authenticated" but not what the action gets back. Return a short-lived (10–15 min) Ashgrove token scoped to the project, `::add-mask::`ed immediately, never the ID token itself.
- **Policy claims beyond `sub`.** Consider `repository_id`, `repository_owner_id`, `ref`, `environment`, `event_name`, `job_workflow_ref` (reusable workflows), `runner_environment` (github-hosted vs self-hosted), and `actor`. Allow policy on `environment`, since protected environments carry the real approval controls.
- **Audit trail.** Record `repository`, `run_id`, `sha`, `ref`, `actor`, and `workflow_ref` on every exchange and deploy. This is a selling point for compliance buyers.
- **Endpoint hardening.** It is unauthenticated by nature. Add rate limits per IP and per issuer, body size limits, and bounded JWKS fetch concurrency.
- **Token lifetime.** Request the ID token right before the exchange. Long jobs can outlive `exp`.
- **Observability.** Add metrics for exchange success, failure by reason, auth method mix, and api-key vs OIDC share. They tell you when you can deprecate keys.

## Suggested revised design

1. The action requests an ID token with a fixed Ashgrove `aud` (per tenant, with an `audience` input override for GHES).
2. It posts the token plus `project` to `/v1/token/exchange`.
3. The server checks, in order: issuer is on the tenant allowlist, signature (RS256, `kid` lookup), `aud`/`exp`/`nbf`/`iat`, `jti` unused.
4. It looks up the project's trust policy keyed by `(issuer, repository_id, repository_owner_id)` and verifies the policy conditions: `sub` or `ref`/`environment`, plus `event_name` and `job_workflow_ref`.
5. On a match it returns a short-lived, project-scoped Ashgrove token. Otherwise it returns a specific 4xx and records the claims seen, so an admin can approve the workflow in the UI.
6. `auth: auto|oidc|api-key` is explicit. Anonymous mode is opt-in. The action logs which method it used.

## Questions to answer before the next draft

1. Can the two GHES accounts expose JWKS to the internet, or do you need an uploaded-JWKS or agent model?
2. Who may create a link in the UI, and how is repo ownership proven?
3. What does anonymous read-only actually do for a deploy action, and who asked for it?
4. Is the v3 major bump driven by a real break, or only by the input becoming optional?
5. What is the api-key deprecation timeline?

I can write this up as a proper design-doc diff or a test-vector list for the matcher if you want either.