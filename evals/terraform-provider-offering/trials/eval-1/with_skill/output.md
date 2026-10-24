# Brightmoor Terraform provider: decision and plan

## Decision

**Build the provider, but don't rewrite it and don't publish under your lead engineer's account.** Take over the community provider through a dated outreach, then a fork, in a Brightmoor-owned namespace from the first release. Migrate it to the Plugin Framework one resource at a time.

| Your plan | Decision | Why |
|---|---|---|
| Rewrite from scratch | ❌ Reject | A rewrite strands the 1.4M-download user base. Every user would need a new address, new attribute names and new state, with no upgrade path. |
| Publish under the lead engineer's account, move after v1 | ❌ Reject | A namespace move is a breaking change for every user. Each one must edit `source` and run `terraform state replace-provider`. |
| Own attribute naming (`interval_seconds`) | ✅ Keep the goal, change the method | Add the new name beside the old one in a minor release, deprecate the old one, remove it in a major. |
| Ship because 70% of enterprise buyers require IaC | ⚠️ Drop the statistic | Public data doesn't quantify this. Your own evidence is enough: two deals asked for a Partner provider, and a community provider has 1.4M downloads. |

**Path: fork-adopt.** Transfer-adopt is only available if the maintainer answers, so it is the preferred outcome of the outreach below.

- **Why not rewrite:** a rewrite is justified only if the audit shows the community schema fails on names, sets and import together. One bad name (`check_frequency_secs`) is a deprecation, not a rewrite. The rewrite also costs the most effort and ships latest, and your deadline is this quarter.
- **Why fork over support-only:** supporting a volunteer's provider earns no Partner badge.
- **Licence:** MIT is an OSI licence, so the fork is legitimate. Keep the licence notice and attribution.
- **Why not fork today:** a two-week DM is not a stated time box. Fork-adopt needs an announced, dated reply window first.

**What moved the path:**
- Q1 (a community provider exists, with downloads and a silent maintainer) selects an adopt rung.
- Q2 (two deals asking for Partner) confirms real demand, so the answer is "ship".
- Q6 (Partner is the target, and the provider is on SDKv2) schedules the mux migration of the core resources before the badge request.
- Q7 (a deadline this quarter) keeps the default rungs and rules out the generated full-coverage path.

## Do now (this week)

1. **Outreach with a time box.** Open a public issue on `jhalvorsen/terraform-provider-brightmoor` and send an email. Both should say:
   - you want to transfer the repo to Brightmoor, or co-maintain it with the maintainer credited;
   - you will publish a vendor-maintained fork if there is no reply by **2026-11-07** (14 days).

   Keep the message free of internal detail.
2. **Set up the org namespace now.** Sign in to registry.terraform.io with GitHub, select the Brightmoor org, and create the signing key (below). That is hours of work, not a blocker. Your lead engineer can run it, but the key and namespace belong to the org.
3. **Ask the two buyers what the questionnaire line requires.** A "HashiCorp Partner provider" can mean the Partner badge or just a signed, vendor-maintained provider on both registries. The answer changes your date. Don't promise a badge date: I don't know HashiCorp's review time.
4. **Answer the open interview questions:**
   - Q3: which API objects customers configure and keep.
   - Q4: the API shape per object (see the gate matrix).
   - Q5: who owns the provider, who is on call for its issues, and whether you have a sandbox account.
   - Q6: the oldest Terraform and OpenTofu versions your customers run.

   Until Q4 is answered, the gate rows below stay UNKNOWN. UNKNOWN counts as FAIL.

## Community-provider audit

Run this during the time box. It decides between transfer or fork and a rewrite.

| # | Check | Status |
|---|---|---|
| 1 | OSI licence file in repo | ✅ MIT |
| 2 | Attribute names follow the API | ❌ `check_frequency_secs` vs `interval_seconds`. Count the others. |
| 3 | Sets where the API is unordered | UNKNOWN |
| 4 | Import works for every resource, with a documented ID grammar | UNKNOWN |
| 5 | Acceptance tests exist and pass against a sandbox | UNKNOWN |
| 6 | Open issues reporting a perpetual diff, "inconsistent result after apply" or a 404 after create | UNKNOWN. Triage the 60 issues. |
| 7 | Schema versions released, and whether state upgraders exist | UNKNOWN. You will owe upgraders from those versions. |
| 8 | SDK in use | SDKv2. This blocks the Partner badge until the core resources migrate. |
| 9 | Maintainer contact with a dated time box | In progress, deadline 2026-11-07 |

**Flip rule:** if checks 2, 3 and 4 all fail broadly, switch to the vendor-owned hand-written path. That means a Framework rewrite in the Brightmoor org with API-aligned names, plus a migration guide published from the community address. Even then the namespace rule holds.

## Gate matrix

Hypothesized objects. Replace them with your real list.

| Check | Monitor | Alert contact | Status page | Owner | Due |
|---|---|---|---|---|---|
| Stable server-assigned ID | UNKNOWN | UNKNOWN | UNKNOWN | API | wk 1 |
| GET returns writable non-secret fields | UNKNOWN | UNKNOWN | UNKNOWN | API | wk 1 |
| In-place update | UNKNOWN | UNKNOWN | UNKNOWN | API | wk 1 |
| Idempotent create | UNKNOWN | UNKNOWN | UNKNOWN | API | wk 2 |
| Bounded propagation (seconds) | UNKNOWN | UNKNOWN | UNKNOWN | API | wk 2 |
| Pollable async op, ID in 202 body | n/a? | n/a? | n/a? | API | wk 2 |
| Deterministic normalization and ordering | UNKNOWN | UNKNOWN | UNKNOWN | API | wk 2 |
| Secrets identified | UNKNOWN | UNKNOWN | UNKNOWN | API | wk 1 |
| Documented rate limits | UNKNOWN | UNKNOWN | UNKNOWN | API | wk 1 |

- A resource ships only when its column has no FAIL or UNKNOWN.
- A FAIL not fixed by the release cut moves to the next minor. Never ship a known perpetual diff.
- Leave check results and incidents out of the provider: they have no desired state.
- Route idempotency and rate-limit gaps to `api-idempotency-retry` and `api-rate-limit-policy`.

## Resource map (fill from the audit)

| API object | Construct | Import | Replace-only fields | Preserved fields | Secrets | Collections |
|---|---|---|---|---|---|---|
| Monitor | resource + singular/plural data source | plain ID | TBD | TBD | TBD | set unless the API orders them |
| Alert contact | resource + data source | plain ID | TBD | TBD | integration keys: API-generated once, `Sensitive`, null after import | TBD |
| Status page | resource + data source | plain ID | TBD | TBD | TBD | TBD |

- **Construct order after core resources:** write-only arguments for input secrets (need Terraform and OpenTofu 1.11+), then ephemeral resources, identity plus list resources, actions, functions.
- **Cut order if time runs out:** actions and functions first, then list resources, then the least-used data sources. Never cut import or upgrade tests.

## Plan-time rules to enforce on every resource

- **Read:**
  - Set every attribute the API returns.
  - Preserve from prior state any field the API never returns.
  - Remove the resource from state on 404.
  - Delete treats "already gone" as success.
- **Plan modifiers:** `RequiresReplace` only where the API can't update. `UseStateForUnknown` on stable computed values.
- **Validators** so bad input fails at plan, not mid-apply.
- **Consistency:** bounded waiters on typed errors after create, update and delete. Never retry broad error classes. Configurable timeouts.
- **Rate limits:** honour `Retry-After` and throttle client-side. Document a safe `-parallelism`.
- **Credentials:** Optional attributes with an environment fallback, and no write calls at configure time.
- **`ImportStateVerifyIgnore`:** list only the preserved fields and API-generated secrets. Document that these fields show a diff on the first plan after import.

## The rename (`check_frequency_secs` to `interval_seconds`)

Do this in **two steps**, so users face one migration at a time.

1. **First fork release:** schema-identical to the community provider. The only user change is `source` plus `terraform state replace-provider`.
2. **Next minor:**
   - Required attribute: make the old one Optional, add the new one, deprecate the old with `DeprecationMessage` ("Use `interval_seconds` instead. `check_frequency_secs` will be removed in vN"), and add `ExactlyOneOf`.
   - Optional attribute: add the new one, deprecate the old, and add `ConflictsWith`.
   - Computed attribute: populate both from Read until the major.

The removal waits for the next major. Majors ship at most once a year, staged behind an opt-in beta, with an upgrade guide. Apply the same recipe to every other oddly named attribute the audit finds.

## Build stack and Partner badge

- **Stack:** Plugin Framework, protocol 6, with `terraform-plugin-testing`, `tfplugindocs` and GoReleaser. Build on Brightmoor's Go SDK if you have one.
- **Mux migration:** mux the SDKv2 and Framework servers (`tf5to6server` plus `tf6muxserver`) and migrate one resource at a time, core resources first.
  - Keep every attribute name, type and `id`.
  - Blocks must stay blocks.
  - Prove each migrated resource with the old acceptance tests unchanged plus an upgrade test.
- **Partner requirements, which you must be able to meet:**
  - the Technology Partner Program;
  - the Plugin Framework;
  - nightly acceptance tests in GitHub Actions;
  - critical issues fixed in 48 hours, others in 5 business days.

  Size the on-call question (Q5) against that SLA before you apply.
- **Partner Premier** adds identity plus list resources, ephemeral resources or actions, and an SBOM. Treat it as a later target.

## Test plan

- **Per resource:**
  - `_basic` ending with an import step that uses `ImportStateVerify`;
  - `_disappears`;
  - one update test per mutable attribute;
  - one replacement test per replace-only attribute;
  - data-source tests: a singular source errors on zero or several matches, a plural source returns empty without error.
- **Never set `ExpectNonEmptyPlan`.** A PR that adds it must link the API bug.
- **Upgrade tests:**
  - apply with the last community release at the old address;
  - run `state replace-provider` in a pre-step;
  - plan with the new build and expect no changes;
  - repeat from every released schema version that needs an upgrader.
- **Import config generation:** run `-generate-config-out` and validate the HCL with `terraform validate`.
- **Sandbox and CI:**
  - A dedicated sandbox account with `tf-acc-test-` prefixed objects, and sweepers before and after each nightly.
  - Nightly runs the full suite plus the upgrade tests, with a `tofu` lane.
  - Fork PRs never get sandbox credentials.
  - Release only from a green nightly.

## Release checklist

1. Public repo `brightmoor/terraform-provider-brightmoor`, lowercase, in the final org. Keep the MIT licence and attribution, and continue the version line (next minor after the community's last release).
2. `terraform-registry-manifest.json` with protocol `6.0` once the provider is Framework-only, `5.0` while it is still SDKv2-only. A muxed provider serves protocol 6 through `tf5to6server`, so use `6.0`.
3. RSA 4096 signing key, since the Registry rejects GnuPG's default ECC key. Store it as CI secrets in a release environment restricted to maintainer tag pushes, with an expiry reminder, an offline backup and a revocation certificate.
4. GoReleaser config and workflow copied from `terraform-provider-scaffolding-framework`:
   - `CGO_ENABLED=0`;
   - zip archives with the exact asset names;
   - signed `_SHA256SUMS`;
   - the manifest renamed `_manifest.json`;
   - linux, darwin, windows and freebsd on amd64 and arm64;
   - actions pinned to commit SHAs;
   - `permissions: contents: write` only;
   - `release.draft` left unset.
5. Rehearse with a snapshot build, then a `v0.x.0-beta1` prerelease tag.
6. Register the provider and key on registry.terraform.io. Register both on OpenTofu through the `opentofu/registry` issue forms the same day, using the web forms. The submitter must be a public member of the org.
7. Tag `vX.Y.Z` from the default branch. Verify `terraform init` and `tofu init` on a clean machine, plus `OPENTOFU_ENFORCE_GPG_VALIDATION=true`.
8. Never delete, retag or re-upload a version. Ship the next patch instead.
9. Publish `docs/guides/` with the `source` edit and the `replace-provider` command. Open an issue on the old repo announcing the new address.

## Timeline (about 10 weeks, adjust after the audit)

| Week | Provider track | API and release track | Decision |
|---|---|---|---|
| 0–1 | Outreach, audit, triage the 60 issues | Org namespace, signing key, API gate asks filed for every UNKNOWN | D1 on 2026-11-07: transfer, fork or rewrite |
| 2–3 | Fork or transfer, CI green, first release at the new address | Both registries rehearsed with a snapshot build | |
| 4–6 | Mux-migrate core resources, add the `interval_seconds` alias | Sandbox, sweepers, nightly | D2: cut list, objects still FAIL move out |
| 7 | Upgrade tests from the community address, import config generation | Docs generated, upgrade guide drafted | |
| 8 | Prerelease tag, early-customer trial | OpenTofu provider and key submitted | D3: go or slip |
| 9–10 | Fixes from the trial | `1.0.0` or `0.x` tag, announcement | |

Pick `0.x` for the first release if the resource map is still moving, and promise compatibility from `1.0.0`.

## Success criteria and measures

The provider passes when:
- every resource's acceptance suite passes with no `ExpectNonEmptyPlan`;
- upgrade tests from the last release of each supported major pass;
- `terraform init` and `tofu init` (with GPG enforcement) install the latest version;
- no removal has shipped in a minor since `1.0.0`.

Track over time:
- Registry downloads per major, to see who is stranded;
- open perpetual-diff and "inconsistent result" issues, none older than a release cycle;
- nightly flake rate per resource;
- deals and security reviews where the provider tier came up.

## Risks to watch

- **Silent maintainer reappears after you fork.** Agree the hand-off in the announcement, and keep the schema compatible so users can move either way.
- **Users stuck on the old address.** The old address freezes at its last release. Announce on the old repo and in the docs, and track the share of downloads still on it.
- **Buyers want the badge, not just a provider.** The badge needs the Framework migration plus the SLA commitment. Say so to the buyers now.
- **API gate fails on a core object.** That object moves to a later minor. Fix the API before the release cut, not after.

I did not write to the memory file. When you're ready, I can record the path, gate matrix, resource map and deprecation schedule in `developer-platform-context.md`.