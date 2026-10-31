# Verifying Kestrelgate partner integrations without a 9-week queue

## Verdict

**Don't certify on the self-assessment alone.** Leadership has the right problem (9 weeks, partners threatening to leave) and the wrong fix. Cut the manual reading, not the verification. Replace it with automated, behavior-based checks and spend human time only where risk is high.

## Why the form alone fails

- **A form records what partners believe, not what their code does.** The 40 questions are only useful because the code reading currently checks them. Without it, nothing tests a "yes".
- **Identity integrations fail badly.** An SSO bug such as a skipped signature check, a loose `redirect_uri` match or a missing `aud` check is an auth bypass in your customers' tenants. A provisioning bug can leave a fired employee's account active, or delete the wrong users.
- **The failure lands on you.** The certification badge is your claim to customers. A breach through a "certified" integration is your incident, with an unverified attestation as your only evidence.
- **Incentives push the wrong way.** Partners are frustrated and want the badge. A form with no check behind it rewards answering "yes".
- **Dropping review is the wrong lever.** The cost is 2 humans reading every line of every release. Most of that reading is repeatable, so a machine can do it. Some of it is low-value, because most releases don't touch auth or provisioning.

## The plan

### Step 1: Measure the current review (week 0–1)

Before building anything, answer these from the last 6–12 months of reviews:

1. What share of releases changed anything security-relevant (auth flow, token handling, scopes, provisioning logic, dependencies)? I expect most did not.
2. What did the reviewers actually find? Classify every finding (e.g. "signature not validated", "token logged", "deprovision doesn't disable"). I expect a short list of recurring classes to cover most findings.
3. Where does reviewer time go: understanding the code, writing up findings, or waiting on partner fixes?

This gives you the design input and the baseline for the new process. It also gives you the test set for step 3.

### Step 2: Triage the backlog now (weeks 0–2)

1. Sort the queue by risk (step 4) and by diff size.
2. Open a fast lane. Releases that don't touch auth, provisioning, scopes or dependencies get an automated check plus a short attestation. This should clear a large share of the queue.
3. Bring in temporary capacity, such as a contracted security firm or other internal engineers, for 4–6 weeks. Their only job is the Tier 1 backlog. This is cheaper than losing partners.
4. Publish a review SLA to partners and report queue age weekly. Silence is what drives the threats to stop updating.
5. Do not grant blanket "provisional" certification. If you need interim relief, limit it to low-risk integrations (Tier 3 below), with an expiry date.

### Step 3: Build a conformance harness (weeks 2–12)

Test behavior against a sandbox tenant instead of reading code. Start with SSO, since it has the highest impact and the most standardized tests. Do SCIM second.

**SSO (SAML and OIDC):**
- Tampered, unsigned and wrongly signed assertions must be rejected.
- XML signature wrapping variants must be rejected.
- Wrong audience, issuer, recipient or `InResponseTo` must be rejected.
- Expired assertions and replayed assertions must be rejected.
- OIDC: `alg: none`, wrong `iss`/`aud`, missing or reused `nonce`, `state` validation, PKCE enforced, exact `redirect_uri` matching.
- Tokens must not appear in logs or URLs.

**Provisioning (SCIM or your API):**
- Conformance to the protocol: create, PATCH semantics, filters, pagination.
- Idempotency: a retried create must not make a duplicate.
- **Deprovision actually disables access**, and deprovisioning one user touches no other.
- Behavior on `429` and `5xx` (backoff, no data loss).
- The integration only touches users and groups it owns.

**Static and supply-chain checks, run by the partner in CI with your rule pack:**
- SAST with identity-specific rules (for example Semgrep).
- Secret scanning, dependency scanning for known CVEs, and an SBOM.
- The partner uploads signed results. You re-run a sample yourself. If the source is closed, they run your container or action.

**Validate the harness before trusting it.** Replay your historical findings from step 1 against it. Seed deliberately broken integrations (a "known-bad" corpus) and measure how many it catches. Do not retire manual review for any tier until the harness catches all past findings of that class. A check that cannot fail proves nothing.

### Step 4: Tier by risk (weeks 4–10)

| Tier | Typical profile | Verification |
|---|---|---|
| 1 (high) | Admin or write scopes, deprovisioning, large install base, new or poor-history partner | Harness + SAST + **human review of security-critical paths only** |
| 2 (medium) | Provisioning with limited scopes, or SSO with custom code | Harness + SAST; human review of **diffs** that touch security-relevant code |
| 3 (low) | Read-only, or SSO via a standard library, small install base, clean history | Harness + SAST + evidence-backed self-assessment; random sampling |

Inputs for tiering: requested scopes, data sensitivity, install count, partner history, and past findings. Tier moves are rule-based and reviewed quarterly. A serious finding moves a partner up a tier.

### Step 5: Review by diff, not by integration (weeks 6–12)

Classify each release automatically:
- **No change to auth, provisioning, scopes or dependencies, and clean scans:** automatic pass.
- **Dependency bump with no known CVEs:** automatic pass.
- **Scope increase:** always needs approval, enforced by the platform, not by the form.
- **Security-relevant diff:** human review of the diff only, not the whole code base.

### Step 6: Keep the self-assessment, demote it

- Pre-fill answers the harness already proves. Partners only answer what cannot be tested.
- Require evidence links for "yes" answers (a test run, a config, a policy).
- Add a contractual consequence for false attestation, such as certification revoked and a re-review fee.
- Audit a random sample against reality (step 8).

### Step 7: Reduce what a bad integration can do (weeks 4–16)

Don't rely on partner code being right. Contain it on your side:
- Least-privilege scopes, with re-consent on any increase.
- Per-integration credentials, short-lived tokens, easy revocation.
- Rate limits and anomaly detection (mass provisioning, mass deletion, unusual token use).
- A kill switch to suspend one integration across all tenants.
- Runtime telemetry that feeds back into tier and re-certification.

This is the check that remains when a harness test or a review misses something.

### Step 8: Audit and re-certify (from week 12)

- Each quarter, deep-review a random sample of certified integrations, weighted toward Tier 1. Compare findings with the self-assessments and the harness results.
- Re-certify automatically when a CVE lands in a listed dependency, or when a partner's incident history changes.
- Run a disclosure or bug-bounty channel for integrations, with remediation SLAs for partners.

## Roles for the two senior engineers

They become the owners of the harness rules and the Tier 1 reviewers, not the readers of every release. Their past findings are the specification for what to automate. Add one platform engineer for the harness and CI tooling if you can. Without that, the rollout will stall behind the same two people.

## Metrics

- **Queue age:** p50 and p90 time from submission to decision. Target days, not weeks.
- **Reviewer hours per release,** by tier.
- **Harness recall:** share of historical and seeded flaws it catches. This gates every move away from manual review.
- **Escapes:** security issues found after certification, by tier. This is the number leadership should care about most.
- **Audit disagreement rate:** how often sampled audits contradict the self-assessment or the harness.

## Rough timeline

| When | What |
|---|---|
| Weeks 0–2 | Measure, triage the queue, fast lane, temporary reviewers, SLA published |
| Weeks 2–8 | SSO conformance tests MVP, SAST rule pack, tiering rules |
| Weeks 8–12 | SCIM tests, diff classifier, harness validation against past findings |
| Weeks 12–16 | Tier 3 moves to automated gates, runtime controls, sampling audits start |
| Quarterly after | Tier review, audit sample, harness updates |

These durations assume a small dedicated team. Adjust them once step 1 shows how much repeatable work there is.

## What to tell leadership

1. Form-only certification trades the backlog for a security liability. It makes the badge meaningless, and the first incident through a certified integration is yours.
2. The backlog is a throughput problem, and it has a fix: automate the repeatable checks, tier by risk, and review diffs.
3. Most of the queue can clear in 2–4 weeks through the fast lane and temporary reviewers, while the harness is built.
4. Success is measured by queue age and post-certification escapes, not by badges issued.

## Questions that would change the plan

- Are partner sources visible to you, or only built artifacts? That decides whether SAST runs on your side or in partner CI.
- Are integrations mostly SAML/OIDC and SCIM, or custom API clients? Custom APIs need more manual review.
- Do you have a sandbox tenant partners can test against today?
- What do your contracts say about revoking certification and liability for false attestation?
- How many of the 260 are Tier 1 by scope? If it is under about 20%, the human load drops sharply.