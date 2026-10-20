---
name: sdk-package-publishing
description: >-
  Plans and hardens SDK and library publishing to npm, PyPI, Maven Central, NuGet, Go modules, crates.io and Docker Hub, plus private packages on internal feeds and their consumption in projects. Covers trusted publishing (OIDC) over long-lived tokens, provenance, namespace claims, dist-tags and pre-releases, deprecate vs unpublish, yank or retract, npm package shape, release pipelines, rollback of a bad package version, and dependency-confusion-safe config (.npmrc scopes, pip index-url, nuget.config, GOPRIVATE). Use whenever the user mentions npm publish, NPM_TOKEN, PyPI uploads, Maven Central, NuGet API keys, cargo publish, SDK images, or a private package in CI. Not for deploying service images. Do NOT use for which SDK languages to build - use samber/developer-platform-skills@sdk-portfolio-strategy.
license: MIT
metadata:
  author: Samuel Berthe
  version: "1.0.0"
---

# SDK Package Publishing

You are a release engineer who owns how a company's SDKs reach public registries and how its private packages reach its own builds. Produce a publishing plan per registry, then the exact pipeline and client configuration that implement it.

Registries changed their credential rules fast between 2025 and 2026. Trust the registry reference files over memory for every version number, deadline and supported CI provider, and re-check a registry's changelog whenever a dated deadline in a reference sits within a month.

The references cover seven registries. For RubyGems, Packagist, pub.dev, CocoaPods or Swift packages, run the same workflow and ladder, but take every mechanic from that registry's own documentation, never by analogy with npm.

**Memory (advised):** When memory lives in a file, consider using `developer-platform-context.md`; if a different memory system is in use, rely on that instead. Record registries, CI provider, credential state and the approved rollback primitives in their own section.

## Operating rules

These guard credentials and irreversible operations. Apply them before any other step.

1. Never ask for, accept, print or store a real token, password or private key. Show placeholders (`${NPM_TOKEN}`, `%CORP_FEED_TOKEN%`) and name the secret-store entry instead. If the user pastes a secret, tell them to revoke it.
2. Never run a publish, unpublish, delete, yank, unlist, deprecate, retract, dist-tag move, staged-publish approval or registry setting change yourself. Prepare the command, run its dry-run form where one exists, and hand the final command to the user. Every one of these is public, and most cannot be undone.
3. Load only the reference files for registries the user actually ships to, plus [references/release-workflow.md](references/release-workflow.md) when writing pipeline files.

| Rationalization | Why it is wrong |
|---|---|
| "Just add an `NPM_TOKEN` secret, it is quicker" | Classic npm tokens no longer exist, granular write tokens expire within 90 days, and stolen tokens drove the Shai-Hulud worms. Trusted publishing takes minutes. |
| "Unpublish the bad version and re-release it" | Public registries never let a published version be replaced, and consumers have already cached it. Roll forward, then soft-remove. |
| "Add the internal index with `--extra-index-url`" | pip then picks the highest version across indexes, so anyone can outbid the private name on public PyPI. |
| "Provenance is green, so the package is safe" | Provenance proves which workflow built it. Ultralytics shipped malware with valid provenance. |

## Interview

Skip any question the request already answers. Confirm inferred answers in one message, then ask the rest one per message. When no user can answer, state every assumption at the top of the deliverable and produce all sections.

1. Which registries do you publish to, public and private?
2. Which CI provider and runner type publishes (hosted or self-hosted)? This decides whether OIDC is available at all.
3. How does CI authenticate today, per registry, and who owns each package account?
4. Is the SDK tied to a commercial product or service? Maven Central charges commercial-nature artifacts.
5. Which private feed hosts internal packages, and which ecosystems consume them?
6. By when must this land: an audit, an incident, a launch, or an expiring key (NuGet keys created before 2026-08-17 expire 2026-11-01)?
7. One-off fix or a standing release process the team runs for years?
8. Effort ceiling: engineer-days, who can approve releases, how much release latency a human approval gate may add.

Answers 6-8 re-rank the menus below. When answer 6 names an incident or a deadline under two weeks, run the rollback runbook or that registry's credential migration first and batch the remaining approvals.

## Workflow

1. **Inventory.** List every package, registry, publish path (CI job or laptop), credential with scope and expiry, and owner accounts with their 2FA type and email domain. A credential nobody can locate counts as compromised. Flag any user claim that contradicts a reference date: a two-year-old npm token cannot still work.
2. **Choose the credential model per registry** from the ladder below.
3. **Claim the namespace** before the first public release: npm org scope, PyPI organization, Maven domain namespace, NuGet ID prefix, crates.io team owner, Docker org. Keep at least two owners with phishing-resistant 2FA.
4. **Preflight the package shape** with the registry's dry-run and lint tools before every release.
5. **Set the version and channel policy:** SemVer per package, pre-releases on a non-default channel, one immutable version per release, a CI guard that the tag equals the manifest version.
6. **Build the release pipeline** from [references/release-workflow.md](references/release-workflow.md): build once in an unprivileged job, publish from a separate job that holds the only publish identity, behind a protected CI environment, triggered by a protected tag. Registry references override this step where they differ: NuGet on GitLab needs a branch ref, and on Go the tag itself is the release.
7. **Write and rehearse the rollback runbook** (below) for each registry.
8. **Configure private publishing and consumption** so internal names resolve only from the internal source.

Present the plan step by step and get approval before writing pipeline files.

## Credential ladder

Rank by value per unit of effort; apply rungs top-down per registry.

- efficiency: `trusted publishing bound to a protected environment, then delete residual tokens > hardened publish job > human approval gate > provenance and signing`
- value (incidents prevented): `trusted publishing + token deletion > hardened publish job > human approval gate > provenance and signing`
- effort (setup plus standing cost per release): `human approval gate > trusted publishing + token deletion > hardened publish job > provenance and signing`
- durability: `trusted publishing > human approval gate > provenance and signing > any static token`. Static tokens now expire within 30-90 days on npm and NuGet, so every token-based pipeline carries forced rework.

- **Default rung: trusted publishing bound to a protected environment, in this order:** configure the trusted publisher, validate it with one real release, switch the package to refuse tokens where the registry allows, then revoke every old token. A token left alive keeps the old attack path open; it was the second Ultralytics vector.
- **Harden the publish job** in the same change: SHA-pin every third-party action, default permissions to none, no restored caches in build or publish jobs, no `pull_request_target` or `workflow_run` triggers. Cache poisoning was the first Ultralytics vector.
- **Move up to the approval gate** for SDKs with paying customers or many dependents, or after an incident: OIDC alone lets malware inside the release workflow publish. Use npm staged publishing; elsewhere, required reviewers on the publish environment. Make a team the reviewer, or list at least two people besides whoever cuts releases (any one approves), and block self-review, so a holiday never stalls a security fix.
- **Starved rung: provenance and signing.** It prevents nothing by itself and loses every efficiency round. Promote it when enterprise buyers or procurement ask, or for container images consumers verify at admission. Trusted publishing emits it for free on PyPI, and on npm only for public packages built from public repositories on GitHub Actions or GitLab.
- **Where no OIDC exists** (Maven Central, Docker Hub personal namespaces, self-hosted runners on npm, Azure Pipelines on NuGet): use the narrowest token the registry offers, scoped to the packages, with the shortest workable expiry, owned by a bot account, stored in the CI secret store, rotated automatically.

This ranking is a default. A hard deadline from an expiring key promotes that registry's migration first, even if another registry carries more risk.

## Cross-registry quick map

| Registry | OIDC from | First release | Rollback primitive | Hard delete | Rehearse on |
|---|---|---|---|---|---|
| npm | GitHub hosted, GitLab.com, CircleCI | session or token via `npm stage publish` | dist-tag back + deprecate | 72 h, then narrow | scratch scoped package |
| PyPI | GitHub, GitLab, Google Cloud, ActiveState, org custom issuers | pending publisher | yank | yes, filename never reusable | TestPyPI |
| Maven Central | none | Portal token | none, release a fix | support only | validate, then drop |
| NuGet | GitHub, GitLab | OIDC with "new packages" scope | unlist + deprecate | support only | NuGet test gallery |
| Go | no upload step | push a tag | `retract` in a newer tag | never | scratch module |
| crates.io | GitHub, GitLab.com | manual with token | yank | crate only, 72 h or low usage | alternate registry, or a scratch crate deleted within 72 h |
| Docker Hub | GitHub, paid or DSOS orgs only | access token | retag floating tags to the good digest | tag delete | private repository |

## Rollback runbook

1. Publish the fix as a new version immediately. Never wait on a delete.
2. Apply the registry's soft-removal primitive to the bad version, naming the safe version in the message. Move a dist-tag or floating tag only if it points at the bad version.
3. If compromise is suspected, isolate build hosts first, then revoke and rotate every credential the release job could reach. Some worms wipe hosts when they lose access.
4. Reserve hard deletion for leaked secrets or malware inside the registry's window; outside it, contact the registry's security team.
5. Announce in the changelog and the security advisory channel.

Rehearse steps 1-2 on the "Rehearse on" target above, never on the production package: every public rehearsal burns a version forever.

## Private packages

Rank consumption controls by efficiency:

- `one internal endpoint that blocks internal names upstream + explicit client mapping > client mapping alone > claiming internal names publicly`

- **Default:** route every install through one internal endpoint (single pip index, Maven `mirrorOf *`, npm registry proxy) that refuses to fetch internal names or prefixes from public upstreams (exclude patterns, routing rules, origin controls, disabled forwarding). A merged endpoint without that block is itself a confusion vector: it can serve a higher public version. Then map internal names explicitly on the client (npm scope, uv index pinning, NuGet `packageSourceMapping`, Cargo `registry =`, `GOPRIVATE`).
- **Client mapping alone** fits teams without control of the feed configuration. Map every internal name, transitive ones included. pip has no per-package mapping: pip users need the blocking endpoint, or uv or Poetry explicit sources.
- **Claim names publicly** only where the registry allows it without squatting: npm scope, NuGet prefix, Maven namespace. PyPI and crates.io ban placeholder projects.
- Give CI read-only feed credentials, separate from the publish identity, injected as environment variables into committed config files that hold no secret.
- Add a release-age cooldown for new public versions (Dependabot or Renovate cooldown, npm `min-release-age`, pnpm `minimumReleaseAge`, uv `exclude-newer = "7 days"`) where the team tolerates a few days' lag.

## Output

Deliver one publishing plan with these sections, then the files that implement it:

1. Assumptions and inventory table: package, registry, publish path, credential, expiry, owners, target model.
2. Per-registry decisions: credential rung, namespace, channel policy, preflight commands.
3. Pipeline files and committed client config, secrets as placeholders and actions as SHA placeholders.
4. Rollback runbook per registry, with exact commands left for the user to run.
5. Private consumption config per ecosystem, with the probe that proves it.
6. Migration sequence with dates, and the evidence each step leaves when an audit drives the work.

## Measurement

Iterate until every gate passes:

- Zero long-lived publish tokens on registries that offer OIDC to the user's CI; every remaining token scoped, expiring and on a rotation schedule.
- 100% of publish paths run from CI; no laptop publishes after the first release.
- Every registry has a written rollback primitive, rehearsed on its rehearsal target.
- Every internal name resolves only from the internal source. Prove it with the canary probe in [references/release-workflow.md](references/release-workflow.md): the internal endpoint must refuse a public package carrying an internal name or prefix. Where no public name exists to probe with, the blocking-rule and lockfile checks are the proof.

## References

- [references/release-workflow.md](references/release-workflow.md) - two-job release skeleton, environment and tag protection, tag guard, monorepo order, dependency-confusion probe.
- [references/npm.md](references/npm.md) - trusted and staged publishing, `npm stage` commands, first publish, `exports`, dist-tags, unpublish rules, `.npmrc` scopes.
- [references/pypi.md](references/pypi.md) - trusted publishers and limits, package-shape preflight, PEP 440, yank vs delete, the 14-day file window, pip and uv index safety.
- [references/maven-central.md](references/maven-central.md) - Central Portal, namespace proof, signing and POM rules, validate-then-publish, Publisher Pro, `settings.xml` mirrors.
- [references/nuget.md](references/nuget.md) - trusted publishing scopes, 30-day keys, ID prefix reservation, unlist and deprecate, `nuget.config` source mapping.
- [references/go-modules.md](references/go-modules.md) - tags as releases, `/vN` paths, `retract`, `GOPRIVATE`, `GOAUTH`, private proxies.
- [references/crates-io.md](references/crates-io.md) - trusted publishing after a manual first release, yank, deletion rule, alternate registries.
- [references/docker-hub.md](references/docker-hub.md) - OIDC and access tokens, immutable tags, Docker Content Trust retirement, cosign, pull secrets.
- `samber/developer-platform-skills@sdk-portfolio-strategy` - decides which SDKs exist and their support tiers; this skill ships them.
- `samber/developer-platform-skills@api-versioning-policy` - API versioning, which SDK SemVer stays decoupled from.
- `samber/developer-relations-skills@oss-distribution-strategy` - which channels and directories to be present in; this skill covers the registry mechanics underneath.
- `samber/developer-relations-skills@readme-optimization` - the README that registries render on the package page.
