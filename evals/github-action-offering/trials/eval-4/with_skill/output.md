# Teardown: OIDC for `ashgrove/deploy-action`

**Verdict: don't ship this design.** It has two security holes and one broken-by-design requirement. It also misses both of your biggest accounts, and the v3 premise is wrong. Everything below is a change to the design doc. This is a design review only, so I haven't run anything.

I followed the `github-action-offering` skill and its four references. Your answers to the skill's interview aren't in the brief, so the assumptions I made are in the last table. Treat the plan as provisional on them.

## Blockers

### 1. Any GitHub workflow can authenticate (contract rule 6; step 4; `vendor-oidc.md` § Backend validation)

- **Default audience.** The token is minted with the default audience, and you only check that `aud` is present. The default is just the repo owner's URL.
- **Replay from other services.** Any token minted for AWS, Vault or any other service passes that check, so it can be replayed at `/v1/token/exchange`.
- **Shared issuer.** `token.actions.githubusercontent.com` is shared by every GitHub customer. Valid signature plus valid issuer proves "some GitHub workflow somewhere", not "your customer's workflow".
- **Fix.**
  - Request a vendor-specific audience, for example `https://api.ashgrove.example`.
  - Require `aud` to equal it exactly.
  - Treat "authenticated" as "a trust binding matched". Issuer, signature and audience are only preconditions.

### 2. Trust binding on a typed `sub` pattern (step 4; § Trust binding; § Claim formats)

The `repo:their-org/their-repo:*` pattern fails in six ways.

| Problem | Consequence |
| --- | --- |
| Name-only `sub` | A customer renames or transfers an org, an attacker takes the freed name and recreates the repo, and the old binding matches. The attacker gets a deploy token. |
| Immutable `sub` | Repos created, renamed or transferred after 2026-07-15 get `repo:org@123456/repo@456789:…`, so the typed pattern never matches new repos. Expect "works in our test org, fails for the new customer repo". This is the AWS README failure in the skill's precedents table. |
| Org `sub` templates | Orgs can customize `sub`, so string-matching it is fragile either way. |
| Trailing `:*` | It matches every ref, every environment and `pull_request`. A deploy action then accepts any branch. |
| `pull_request_target` | A customer's workflow using it runs with base-repo identity, and a public-repo attacker can reach a binding meant for `main`. |
| Free-text field | One typo (`repo:org/*`) silently widens the grant. |

**Fix.** Replace the pattern box with a structured binding keyed on individual claims:

- `repository_owner_id` is required.
- `repository_id` is strongly recommended. Make it required for deploy.
- One of `ref`, `environment` or `job_workflow_ref` is required. A bare wildcard is not allowed.
- `event_name` is an allow-list. Default it to `push`, `workflow_dispatch` and `release`, and refuse `pull_request_target`.
- The UI shows the exact claim values a sample token would carry. Add a "test with a real run" button that displays the last rejected token's claims.

### 3. Silent fallback: OIDC, then key, then anonymous (rule 6; step 3)

The skill states this directly: an OIDC failure MUST fail the step with a named error. Your design has three separate faults.

- **Hidden failures.**
  - A broken trust setup becomes invisible. The customer thinks OIDC works while keys are still in use, so the secrets you wanted gone never leave.
  - You can't tell a trust bug from an outage.
- **Fail-open downgrade.** Anything that breaks the exchange (a 5xx, a JWKS fetch error, a misconfigured binding) moves the run to a weaker auth path or a no-op.
- **Green pipelines that did nothing.** For a *deploy* action, "anonymous read-only" means the deploy didn't happen and the job is green. That is the Trivy incident pattern in `security-hardening.md`: the pipeline stays green while the real work never runs.

**Fix.** Add an `auth` input with values `auto`, `oidc` and `key`, defaulting to `auto`.

- `auto` with a non-empty `api-key` uses the key. Behaviour for existing v2 users is unchanged.
- `auto` with an empty key selects OIDC.
- If `ACTIONS_ID_TOKEN_REQUEST_URL` is absent, fail with: `api-key is empty and the job lacks "permissions: id-token: write"`. A missing secret also arrives as an empty string, so the message must name both causes.
- Log the chosen mode on every run.
- Retry transient exchange errors (429, 5xx, network) with backoff, then **fail**. Never fall back.
- Return distinct error classes: `no-token`, `untrusted-issuer`, `bad-audience`, `no-matching-binding`, `expired`, `service-unavailable`. Each message tells the customer which claim to fix.
- Auth, config and service errors always fail the step.

### 4. v3 is not required for OIDC (rule 2; § Breaking-change table)

- **Relaxing is a minor.** Making `api-key` optional relaxes the contract. `required:` isn't enforced by the runner anyway, so only your in-code validation changes. Adding the `auth` input with a default that preserves behaviour is also a minor. Per step 3 of the skill, OIDC should land as a minor.
- **Cost of v3.** Customers pinned to `@v2`, to a SHA, or to a lockfile entry would never get OIDC. Dependabot only proposes a major bump after the customer acts, and you'd carry two majors.
- **Plan.** Ship it as `v2.N.0`, an immutable GitHub release.
  - Release notes carry the full commit SHA and `uses: ashgrove/deploy-action@<sha> # v2.N.0`.
  - A job in a protected environment moves the plain Git tag `v2`, pushed as `refs/tags/v2`, never `--tags`.
  - Add a CI contract check that diffs `action.yml` against the last release.
- **When v3 is justified.** Cut a major only if you also change something that actually breaks pinned workflows: `runs.using`, a raised runner floor, a changed default, or removal of a deprecated input. Don't bundle node24 into this release (see item 5).

### 5. GHES 3.15 breaks the design twice (§ 7; `vendor-oidc.md`)

Your two largest accounts are on GHES 3.15, and they fail against the design as written.

- **Issuer.** GHES signs tokens as `https://<host>/_services/token`, so your `iss == token.actions.githubusercontent.com` check rejects every GHES run.
- **JWKS.** The JWKS usually sits on the customer's private network, out of reach of your SaaS backend.
- **Immutable `sub`.** It isn't available on GHES, so the claim shape differs from github.com.
- **Numeric ID collisions.** Owner and repo IDs are instance-local. `repository_owner_id=1234` on a GHES instance is unrelated to github.com's `1234`. Bindings must key on **(issuer, owner ID, repo ID)**, not on IDs alone. Otherwise one tenant's binding can match another instance's token.
- **Runtime.** I haven't verified which runner and Node version GHES 3.15 bundles. Check before any `runs.using` change, because a node24 bump would lock them out.
- **Support lifecycle.** I haven't verified whether 3.15 is still in GitHub's support window. Check; if it isn't, say so to those accounts.
- **Distribution.** They get the action through GitHub Connect or `actions-sync`. Any nested `uses:` must be synced too, so keep nested dependencies few.

**Pick one of three options with the account owners before building.**

1. **Customer-registered issuer.** The customer registers their GHES issuer in Ashgrove and either exposes the JWKS through an IP allowlist or uploads it, with a documented rotation procedure.
2. **Declare GHES key-only for now.** `auth: auto` with a key still works. Say so in the README and give those accounts a dated roadmap. Honest, but it defeats the "stop pasting keys" goal for your two biggest customers.
3. **Delay launch** until options 1 or 2 are agreed.

If you choose option 1, add these safeguards:

- A registered issuer is valid **only for the customer that registered it**. It can never satisfy a binding owned by another tenant.
- SSRF-guard every discovery and JWKS fetch you make from a customer-supplied URL. Allow only https, block private and link-local ranges, cap response size and set timeouts.
- Fetch the JWKS only from the issuer you've pinned.
- Test audience support and the claim set on a real 3.15 sandbox before committing.

## Other findings

### Backend validation checklist for `/v1/token/exchange`

Your doc lists signature, issuer and `aud`. Add:

- An algorithm allow-list (RS256 or whatever GitHub uses). Reject `none` and HMAC.
- `exp`, `nbf` and `iat` within a small clock skew.
- JWKS caching, with a refetch on an unknown `kid` that is **rate-limited** so random `kid`s can't be used to hammer GitHub or you.
- Rate limiting on the endpoint and on failed-binding attempts.
- Optional `jti` replay cache on very sensitive scopes.
- **Output token:** lives minutes, carries only the matched binding's scopes, and has the matched claims logged next to it.

### Action-side hardening

- **Mask first.** Mask the exchanged vendor token before anything else (`core.setSecret`, or `::add-mask::` in a composite). Composite steps that fetch the GitHub token with `curl` get no automatic masking, so also mask the raw GitHub JWT.
- **No shell injection.** Pass every input through `env:` and quote `"$VAR"` (rule 4). `${{ inputs.x }}` inside `run:` is never safe in a composite.
- **Document the permissions.** The README and docs quickstart must show the minimum block: `permissions: { id-token: write, contents: read }`.
- **Log the mode.** State which auth mode was chosen, and never print a token.

### Fork PRs and Dependabot

Fork `pull_request` runs get no secrets and no `id-token: write`. Today your "anonymous read-only" mode probably covers them. Keep that case, but make it explicit:

- Detect the fork case (head repo is not the base repo) and enter tokenless read-only mode **only then**, with a visible notice and a job-summary line.
- If the product can't do anything useful tokenless, exit with a message naming the limitation.
- Never tell customers to switch to `pull_request_target`.
- Verify how Dependabot-triggered runs behave in a sandbox before documenting them.

### Anonymous mode

Keep it only if the product genuinely supports it. If so, it's opt-in (`auth: none`) or fork-only, never a failure fallback. For a deploy action I'd drop it entirely.

### Exit-code mapping (step 3)

- Config, auth and service errors always fail.
- The primary verdict (deploy failed) fails by default.
- Advisory findings warn.

### Telemetry and retirement (step 9)

- Send a versioned `User-Agent` from the action, for example `ashgrove-deploy-action/2.N.0 (github-actions; Linux-X64)`.
- Add a header flag when the deprecated or key path is used.
- Count OIDC runs from **server-validated** claims at the exchange, deduplicated by `run_id`. Don't trust self-reported data.
- Track key-auth share by version. Use it to decide when to deprecate the key path in a later major, never before.

### Tests and gates before release

- **Contract diff.** Must be clean against the last release.
- **Integration matrix.** Run against a real sandbox account with OIDC on, covering the runner OSes the README claims, the oldest supported self-hosted runner, and GHES 3.15.
- **Negative OIDC cases.**
  - Wrong audience
  - Another org's token
  - Expired token
  - Wildcard-less binding mismatch
  - Renamed repo (bound by ID still works, name-only squatter rejected)
  - `pull_request_target` event
  - Missing `id-token: write`
  - Exchange 5xx (must fail, not fall back)
- **Tooling.** zizmor at medium and above on the action repo and the README example, plus actionlint.
- **Pinning.** Every nested `uses:` pinned by full SHA, every image by digest, every downloaded binary verified against a committed digest or a pinned signature.

## Corrected design

1. The customer's job grants `id-token: write`.
2. The action requests a token for the Ashgrove audience and masks it.
3. It posts the token to `/v1/token/exchange`.
4. The backend validates algorithm, signature, issuer, audience and time claims, then resolves the issuer to a registered trust domain (github.com, or a customer-registered GHES issuer).
5. The backend matches a structured binding on (issuer, `repository_owner_id`, `repository_id`, ref or environment or `job_workflow_ref`, allowed `event_name`).
6. It returns a minutes-long token scoped to the binding.
7. The action masks it and runs.
8. Any failure at any step fails the step with a named error class. No fallback.

## Assumptions I made (answer these to firm the plan up)

| Assumption | Drives |
| --- | --- |
| v2 fails with a named error today when `api-key` is empty | The "minor, not major" call in item 4 |
| The action is composite, or can stay composite | No `runs.using` change, so GHES-safe |
| Ashgrove already runs an HTTP service where the exchange can live, with a per-project token model | Binding and token design |
| "Deploy" cannot be read-only | Dropping anonymous mode |
| Fork PRs are a real use case for some customers | Tokenless mode and the fork split |
| GHES 3.15 customers' Actions can reach `actions-sync`/GitHub Connect for the action | Distribution plan |
| The backend team can build issuer registration, SSRF guards and per-tenant issuers | Option 1 vs option 2 in item 5 |

Questions I can't answer from the brief:

- Which GHES runner and Node version do those accounts actually run?
- Is there a date for the OIDC rollout, and who owns the action after launch?
- What does v2 do on an empty key today?
- Is the GHES issuer reachable from your backend, or do you need uploaded-JWKS?

## Order of work

1. Settle the GHES option with the two account owners.
2. Backend: validation, issuer registry, structured bindings, error classes, rate limits.
3. Binding UI with a claims preview and a "last rejected token" view.
4. Action: `auth` input, mode logging, named errors, masking, README and quickstart.
5. Negative-case test matrix on a sandbox plus GHES 3.15.
6. Release `v2.N.0`, then move the `v2` tag.