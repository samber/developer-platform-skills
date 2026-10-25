# Routing detail - developer-platform-skills collection

Route only from the declared scopes below. Every "do not route here" line comes from the skill's own description, not from inference. The kickoff's own routing table states what each skill covers; this file states where each one _stops_, which is what a two-way keyword collision actually needs.

Nothing here is ranked, and nothing in it should be. Scope is a match test, not a ratio. Ranking lives in the kickoff's short-list and routine set, where several skills compete for one session (see `samber/developer-platform-skills@developer-platform-kickoff` § 4 and § 7).

Nine skills sit at macro altitude:

- `api-integration-surface-strategy`
- `api-versioning-policy`
- `public-roadmap-strategy`
- `sdk-portfolio-strategy`
- `developer-portal-design`
- `sample-app-strategy`
- `etl-connector-strategy`
- `integration-partnership-strategy`
- `connector-marketplace-strategy`

Each shares subject keywords with a tactical sibling and is separated from it by altitude, not by topic.

Three further pairs split by _side of the table_, where the keywords are identical and the advice inverts:

- Operator vs submitter.
- Issuer vs consumer.
- Provider vs client.

Both kinds are collected under Boundary pairs below.

## Table of Contents

- [Per-skill signals](#per-skill-signals)
- [Boundary pairs](#boundary-pairs)
- [Ordered chains](#ordered-chains)
- [Sibling-repo recommendations](#sibling-repo-recommendations)

## Per-skill signals

### `samber/developer-platform-skills@api-integration-surface-strategy`

- Route here: "which API should we build first", "should we add GraphQL or MCP", "a deal is blocked on a surface we don't have", API-first vs embedded-first sequencing.
- Do not route here: designing any chosen surface - it hands off to the per-surface sibling once the surface is picked.

### `samber/developer-platform-skills@public-api-design-review`

- Route here:
  - Audit a REST surface against design rules, bucketing findings Must-change or Improvement.
  - Stand up the review program (lifecycle triggers, reviewer authority, linting, federation).
  - "Review this API before we publish it."
- Do not route here: generating a spec or server code; error taxonomy, versioning, idempotency, auth, rate limits and docs depth each belong to a named sibling.

### `samber/developer-platform-skills@api-error-design`

- Route here: "our errors just say 400", designing the code taxonomy and the RFC 9457 envelope, making messages actionable, signalling retryability.
- Do not route here: client-side retry mechanics, whole-surface consistency review, incident or status-page communication.

### `samber/developer-platform-skills@api-idempotency-retry`

- Route here: "make POST safe to retry", "customers are double-charged", adding an `Idempotency-Key` header, writing retry guidance, setting SDK backoff defaults.
- Do not route here: what the error response signals (`api-error-design`); webhook delivery retries (`webhook-platform-design`).

### `samber/developer-platform-skills@api-rate-limit-policy`

- Route here: setting and publishing quota and burst numbers, the header family, the 429 and `Retry-After` contract, noisy-neighbour fairness, enterprise limit-increase paths.
- Do not route here: throttling infrastructure or gateway configuration; the 429 envelope shape, client backoff mechanics and deprecation machinery belong to siblings.

### `samber/developer-platform-skills@public-graphql-api-design`

- Route here: "should this be GraphQL", designing or reviewing a public schema, Relay cursor connections, error result types, depth and complexity ceilings, the federation trust boundary, persisted queries.
- Do not route here: published cost/quota policy (`api-rate-limit-policy`), deprecation and versioning policy, push-event architecture, partners or third-party apps contributing fields or subgraphs (`graphql-federation-offering`).

### `samber/developer-platform-skills@graphql-federation-offering`

- Route here: "can partners ship subgraphs into our supergraph", letting partner apps add fields or data to platform types in the public graph, stitching partner APIs into the graph the platform publishes, reviewing a partner subgraph's SDL or the router config toward partners, offboarding a partner from the graph.
- Do not route here: single-owner schema design or internal team federation (`public-graphql-api-design`), whether GraphQL is the right surface, consuming third-party APIs in your own client, the partner's signup and sandbox journey (`partner-app-onboarding`).

### `samber/developer-platform-skills@public-grpc-api-design`

- Route here: "should we expose gRPC at all", proto governance and AIP conventions, buf breaking-change gates, the `google.rpc.Status` error model, transcoding and gateway architecture, the pre-exposure audit.
- Do not route here: language-specific server implementation; internal-only gRPC, which this skill's own gate usually sends back to REST.

### `samber/developer-platform-skills@api-auth-key-management`

- Route here: key format and storage, least-privilege scoping, rotation UX, the key dashboard, offboarding, compliance lifecycle governance - and the unresolved "keys or OAuth?" question, which this skill owns.
- Do not route here:
  - Consuming another vendor's API.
  - OAuth flow design.
  - Webhook signing schemes.

### `samber/developer-platform-skills@oauth2-provider-design`

- Route here: "let third-party apps act on our users' behalf", "add Sign in with X plus delegated access", defining scopes, designing consent, setting token lifetimes, gating app publishing behind verification.
- Do not route here: integrating against someone else's OAuth; API-key design.

### `samber/developer-platform-skills@api-versioning-policy`

- Route here: picking a version scheme, writing the breaking-change definition, setting notice windows, sunset signalling and enforcement, breaking-change governance. Asks the API paradigm first - REST's version-and-sunset and GraphQL's continuous evolution are different policies.
- Do not route here: client SDK versioning, which is plain SemVer; auditing whether one surface is well-designed.

### `samber/developer-platform-skills@public-roadmap-strategy`

- Route here: "should we publish a roadmap", "our sales team keeps promising features", a GitHub roadmap repo or roadmap page, now/next/later vs dated quarters, roadmap disclaimers, a feature voting board on the roadmap, announcing a slipped or cancelled roadmap item.
- Do not route here: internal roadmap planning or prioritization; triaging individual feature requests (`samber/developer-relations-skills@developer-feedback-loop`); deprecation notices (`api-versioning-policy`); joint roadmaps with a partner (`integration-partnership-strategy`); what a preview or beta stage promises (`api-beta-program`).

### `samber/developer-platform-skills@api-beta-program`

- Route here: "let a few customers try the new endpoint before it's final", design partners for an API feature, defining what beta or preview means for our API, a beta allowlist, sales asking for early access to an unreleased API, a beta that never ended, customers running production on our own beta endpoints, deciding when a preview goes GA or gets killed.
- Do not route here: whole-app or consumer beta testing; evaluating a vendor's beta you consume; percentage or canary rollouts of a GA change; deprecating a GA version (`api-versioning-policy`); routine feature-request triage (`samber/developer-relations-skills@developer-feedback-loop`); the design review itself (`public-api-design-review`).

### `samber/developer-platform-skills@api-changelog-automation`

- Route here: oasdiff, openapi-diff, graphql-inspector, buf breaking or AsyncAPI diff in CI; "fail the PR on breaking changes"; generating the API changelog or a change feed from spec diffs; cleaning up a breaking-change ignore file; approval records for accepted breaks; capturing behavior changes the spec cannot express.
- Do not route here: writing the breaking-change definition or notice windows (`api-versioning-policy`); release-note prose and CHANGELOG.md wording (`samber/developer-relations-skills@changelog-writing`); upgrade guides (`samber/developer-relations-skills@version-migration-guide`); finding who still calls a deprecated endpoint (`integration-health-monitoring`); consumer-side upgrades to another vendor's API.

### `samber/developer-platform-skills@api-reference-quality`

- Route here: "find our undocumented endpoints", measuring docs completeness against a spec, missing examples or snippet parity, broken try-it, "stop our reference drifting" via CI lint and contract-test gates.
- Do not route here: site-wide docs information architecture, the quickstart page, sample-corpus policy, agent-facing docs - all `samber/developer-relations-skills`.

### `samber/developer-platform-skills@webhook-platform-design`

- Route here: "add webhooks to our API", event taxonomy, payload envelope and schema versioning, HMAC signing, delivery guarantees and dead-letter policy, subscription lifecycle, the consumer debugging surface.
- Do not route here: consumer-side retry mechanics, signing-key storage lifecycle, sandbox mechanics.

### `samber/developer-platform-skills@sdk-portfolio-strategy`

- Route here: "which SDK languages first", generated vs handwritten, tiering and promoting community SDKs, sunsetting a low-usage SDK, release cadence, decoupling SDK SemVer from API versioning.
- Do not route here: single-SDK ergonomics, registry publishing mechanics (`samber/developer-platform-skills@sdk-package-publishing`), whether to offer SDKs as a surface at all.

### `samber/developer-platform-skills@sdk-package-publishing`

- Route here: npm, PyPI, Maven Central (Java, Kotlin, Scala, Gradle plugins), NuGet, Go module, crates.io, pub.dev (Dart, Flutter), RubyGems, Packagist, Hex, SwiftPM, CocoaPods, React Native library or Docker Hub publishing; shipping CLI and other binaries (GoReleaser, cargo-dist, Homebrew tap, winget, Scoop, deb/rpm, `curl | sh` installers, signing and notarization); tag-triggered CI auto-publishing; Artifactory or another private feed for any ecosystem; moving CI off long-lived registry tokens to trusted publishing; dist-tags and pre-releases; rolling back a bad package version; publishing to a private feed; `.npmrc`, `pip.conf`, `settings.xml`, `nuget.config`, `GOPRIVATE` or `.cargo/config.toml` for private packages; dependency confusion.
- Do not route here: which SDK languages to build (`sdk-portfolio-strategy`), API version numbering (`api-versioning-policy`), deploying the platform's own service images, app-store or extension-marketplace submission, MCP registry listing (`mcp-server-offering`), CLI command, flag and output design (`cli-interface-design`), the agent skill bundled in the package (`agent-skill-offering`), registry discoverability and README codes (`samber/developer-relations-skills@oss-distribution-strategy`), the vendor's GitHub Action or CI integration that customers run (`github-action-offering`).

### `samber/developer-platform-skills@agent-integration-surfaces`

- Route here: "are we agent-ready", which AI agent classes may reach marketing site, docs, signup, app and API; a CDN "block AI bots" preset or CAPTCHA stopping agents; robots.txt versus edge enforcement per agent class; how agents prove identity (Web Bot Auth, signed or verified agents) and act for a user (delegated tokens, device grant, per-agent credentials, out-of-band approval); agents provisioning resources a human claims later; Context7 claim and api-catalog; counting agent-originated usage and signups.
- Do not route here: which surfaces to build and in what order (`api-integration-surface-strategy`); MCP tool design (`mcp-server-offering`); the CLI's commands and `--json` contract (`cli-interface-design`); shipping the skill beside the code (`agent-skill-offering`); key formats and OAuth grant mechanics (`api-auth-key-management`, `oauth2-provider-design`); llms.txt, docs markdown endpoints and docs cold runs (`samber/developer-relations-skills@coding-agent-docs-optimization`); an agent the user builds that calls other vendors' APIs.

### `samber/developer-platform-skills@mcp-server-offering`

- Route here: "should we ship an MCP server", choosing which tools to expose, securing write-capable tools, versioning the tool surface, judging MCP ROI.
- Do not route here: code-generation MCP builder skills, which scaffold what this skill specifies; documenting an existing SDK for agent consumption (`samber/developer-relations-skills@coding-agent-docs-optimization`).

### `samber/developer-platform-skills@cli-interface-design`

- Route here: designing or reviewing the CLI that wraps the platform's API, "mirror every endpoint as a command", command naming and grammar, `--json` output and exit codes, CLI login and CI tokens, `--wait` and pagination flags, deprecating CLI flags, CLI telemetry, a CLI that hangs in CI or confuses coding agents.
- Do not route here: whether to offer a CLI at all (`api-integration-surface-strategy`), API-less tools, argument-parser code, an Agent Skill shipped with the CLI (`agent-skill-offering`), shipping the CLI's binaries or packages - Homebrew tap, deb/rpm, release binaries, registries (`sdk-package-publishing`), the GitHub Action or CI integration wrapping the CLI (`github-action-offering`).

### `samber/developer-platform-skills@agent-skill-offering`

- Route here: shipping a SKILL.md with a library, CLI or SDK; keeping a skill's version in sync with releases; CI that fails a release on a stale skill; tag-pinned skill installs; plugin.json, marketplace.json, Codex, Cursor or Gemini manifests for a skill beside code; every Claude plugin manifest field and Claude plugin directory submission checks for that plugin; OpenClaw `metadata.openclaw` gating and ClawHub publishing of a tool's skill; skill vs MCP vs CLI for a coding-agent audience.
- Do not route here: designing the MCP server itself (`mcp-server-offering`); the CLI's commands, `--json` or exit codes (`cli-interface-design`); docs written for coding agents (`samber/developer-relations-skills@coding-agent-docs-optimization`); standalone skill collections with no code version.

### `samber/developer-platform-skills@github-action-offering`

- Route here: "customers want to run us in CI", an official or `setup-<tool>` GitHub Action, `action.yml` inputs and outputs, moving the `v1` tag, immutable releases, a node24 major for the vendor's action, GitHub OIDC token exchange into the vendor API, script injection or tag hijack in the vendor's action, adopting a community-written action, Marketplace listing of an action, GitLab CI/CD components, CircleCI orbs, Bitbucket Pipes or Azure DevOps tasks for the product.
- Do not route here: a team's own workflows or pinning third-party actions; the CLI the action wraps (`cli-interface-design`); publishing the CLI's binaries or packages (`sdk-package-publishing`); API key formats and rotation (`api-auth-key-management`); GitHub Apps and Marketplace app listings.

### `samber/developer-platform-skills@ide-extension-offering`

- Route here: "developers want us in the editor", should we build an official VS Code extension or JetBrains plugin, which jobs it serves, a stale community extension using our API, Cursor or VSCodium users missing our extension, Open VSX namespace or `ovsx`, `vsce` publishing auth, the verified publisher badge, JetBrains Marketplace review or `until-build`, extension telemetry and the IDE telemetry setting, extension login and secret storage, keeping the extension in sync with the CLI, deprecating an extension.
- Do not route here: the CLI's commands, `--json` or exit codes (`cli-interface-design`); MCP server design, even when the extension bundles it (`mcp-server-offering`); npm or other package registries (`sdk-package-publishing`); internal-only extensions, themes, or writing extension and language-server code.

### `samber/developer-platform-skills@terraform-provider-offering`

- Route here: "customers want to manage us with Terraform", should we build or take over a Terraform/OpenTofu provider, terraform-plugin-framework resource design, a perpetual diff or "inconsistent result after apply" in our provider, import blocks and state upgrades, provider acceptance tests, GPG signing and publishing on the Terraform Registry or OpenTofu Registry, Partner or Partner Premier badge, deprecating or renaming provider resources and attributes.
- Do not route here: writing Terraform modules or HCL for the platform's own infrastructure; Pulumi, Crossplane or CDK offerings; which surfaces to offer at all (`api-integration-surface-strategy`); SDK and CLI package registries (`sdk-package-publishing`); the API's own versioning policy (`api-versioning-policy`).

### `samber/developer-platform-skills@sql-jdbc-access-design`

- Route here: "offer SQL access to customers", a JDBC/ODBC endpoint, connecting customer BI tools to product data, tenant isolation, the schema-stability contract, pricing a SQL add-on.
- Do not route here: bulk file delivery (`bulk-data-sharing-design`); ETL-platform connectors (`etl-connector-strategy`).

### `samber/developer-platform-skills@bulk-data-sharing-design`

- Route here: "ship customer data as Parquet", offering a warehouse or lake share, setting an export freshness posture, partitioning and schema-evolution contracts, egress cost allocation, cross-border residency.
- Do not route here: live SQL endpoints, ETL-platform connectors, surface selection.

### `samber/developer-platform-skills@etl-connector-strategy`

- Route here: "get us listed in an ETL platform catalog", build vs partner-built for a source connector, adding CDC to a SaaS product (honestly: API sources ship pseudo-CDC, never log-based), justifying connector engineering spend.
- Do not route here: pipeline-building for data teams; the vendor's own inbound connector marketplace.

### `samber/developer-platform-skills@developer-portal-design`

- Route here: designing or restructuring a portal, console or API dashboard, cutting time to first call, deciding where each self-service surface sits, portal search, RBAC and tenancy, build vs buy.
- Do not route here: internal service catalogs; designing any individual surface the portal hosts - each has its own sibling.

### `samber/developer-platform-skills@sample-app-strategy`

- Route here: which sample apps, quickstart repos, reference apps, starter or deploy templates and playgrounds to keep; too many or broken sample repos; who owns samples; CI and dependency cadence for sample repos; archiving or redirecting samples; a sample gallery or `samples create` CLI.
- Do not route here: quality and CI tier of snippets inside docs pages (`samber/developer-relations-skills@docs-code-sample-standards`), which SDK languages exist (`sdk-portfolio-strategy`), writing one quickstart page (`samber/developer-relations-skills@developer-quickstart-guide`), the sandbox itself (`api-test-mode-design`).

### `samber/developer-platform-skills@api-test-mode-design`

- Route here: designing a sandbox or test mode, choosing the isolation model, magic test values and simulated personas, on-demand test events, reset and seeding, graduation to live.
- Do not route here: code-execution sandboxing, unit-test mocking, a marketing try-it playground, partner sandbox _provisioning timing_ (`partner-app-onboarding`).

### `samber/developer-platform-skills@integration-error-observability`

- Route here: "build a developer-facing error dashboard", exposing request logs to integrators, correlation IDs that survive into a support ticket, alerting partners when their integration breaks, "cut integration support tickets".
- Do not route here: platform-wide incident comms (`api-status-communication`), webhook delivery mechanics, the shape of a single error response.

### `samber/developer-platform-skills@integration-health-monitoring`

- Route here: version drift across deployed integrations, who still calls a deprecated endpoint or auth method, partners on old API or SDK versions, webhook endpoints on a retiring payload version, expiring or dormant integration credentials, chasing owners before a sunset, brownout scheduling, "is it safe to turn v1 off".
- Do not route here: live error dashboards and error-rate alerts (`integration-error-observability`), writing the deprecation policy, notice windows or headers (`api-versioning-policy`), key expiry and rotation design (`api-auth-key-management`), migrating your own code off another vendor's deprecated API.

### `samber/developer-platform-skills@api-status-communication`

- Route here: designing or auditing a status page, writing incident updates or a public postmortem, uptime and SLA reporting, announcing planned maintenance.
- Do not route here: deprecation and breaking-change notices (`api-versioning-policy`), per-integration error surfacing, webhook delivery status.

### `samber/developer-platform-skills@integration-partnership-strategy`

- Route here: picking integration partners from demand data rather than relationships, tiering partnership depth on the referral-to-OEM ladder, evaluating a certification-program join, fixing sourced-vs-influenced partner attribution, where the function reports.
- Do not route here: your own marketplace, ETL-platform listings, integration-surface choice.

### `samber/developer-platform-skills@partner-app-onboarding`

- Route here: designing or auditing the partner-developer entry flow, self-service vs application-gated registration, when sandbox tenancy is provisioned, whether certification gates submission, cutting time-to-first-submitted-app.
- Do not route here: review-gate mechanics, sandbox isolation architecture, post-launch partner tier ladders, listing content, reseller sales enablement.

### `samber/developer-platform-skills@integration-listing-optimization`

- Route here: improving your own listing's conversion or search rank on someone else's marketplace, winning installs and compliant reviews, badge pursuit, defending rank against decay.
- Do not route here: anything the marketplace _operator_ decides - standards, review, monetization, promotion.

### `samber/developer-platform-skills@zapier-integration-playbook`

- Route here: building or auditing your integration on Zapier, writing it with the zapier-platform CLI or Platform UI, converting UI to CLI, an inherited private Zapier integration, polling vs instant triggers, a Zapier trigger that misses or duplicates records, submitting to Zapier's app directory, the 90-day beta, Partner Program tier, publishing Zap templates, the Workflow Element embed, promoting, migrating or deprecating integration versions.
- Do not route here: building Zaps as an end user; Make, n8n or Power Automate connectors; whether to embed an iPaaS in your own product (`connector-marketplace-strategy`); listing copy and ranking on marketplaces generally (`integration-listing-optimization`); the webhook subscription API a REST hook trigger calls (`webhook-platform-design`).

### `samber/developer-platform-skills@salesforce-appexchange-playbook`

- Route here: getting a SaaS product listed and selling on Salesforce AppExchange or AgentExchange as an ISV, API listing vs managed 2GP package, namespace and global Apex decisions, passing or resubmitting the security review, PADA and PNR, Checkout vs GTM app private offers vs Channel Order App, LMA licenses and trials, periodic re-reviews, push upgrades, the Connected App/ECA OAuth mandates.
- Do not route here: listing copy, search rank and reviews (`integration-listing-optimization`); Salesforce consulting listings; packages for your own Salesforce org; writing Apex or LWC; designing the review process for your own marketplace (`app-marketplace-review`); whether Salesforce deserves the investment at all (`integration-partnership-strategy`).

### `samber/developer-platform-skills@slack-app-directory-playbook`

- Route here: submitting or resubmitting a Slack app to the Slack Marketplace (formerly Slack App Directory), the active-workspace install gate, a returned submission, scope rejections and per-scope justifications, bot vs user token choice, enhanced review for history or search scopes, the Security & Compliance and AI disclosures, landing, support and privacy pages, review timelines, updating a listed app (staging app, new scopes, reinstalls), delisting warnings, listed vs unlisted distribution and the rate limits on unlisted apps.
- Do not route here: listing copy, media order and install conversion (`integration-listing-optimization`); designing the review process for your own marketplace (`app-marketplace-review`); designing scopes for your own API's OAuth (`oauth2-provider-design`); building the MCP server itself (`mcp-server-offering`); writing Bolt code; running a community Slack workspace.

### `samber/developer-platform-skills@connector-marketplace-strategy`

- Route here: "should we build an app store", "is our ecosystem ready", setting the take-rate _level_ and curation posture, governing third-party apps at the policy level, seeding a two-sided ecosystem from zero, build vs join vs embedded iPaaS.
- Do not route here: partner onboarding, app review, listing standards, monetization _mechanics_ - all execution siblings; being a connector on others' data platforms is `etl-connector-strategy`.

### `samber/developer-platform-skills@app-marketplace-review`

- Route here: designing the review pipeline, setting approval criteria, what re-triggers review after an update, auditing app permissions, hardening the publish channel, appeal paths, delisting and revocation policy.
- Do not route here: submitter onboarding, listing-content standards, marketplace strategy; the certified or verified label on partner-built connectors above admission (`connector-certification-program`).

### `samber/developer-platform-skills@connector-certification-program`

- Route here: whether to run a certification program for partner-built connectors at all, certified-vs-community labels, measurable certification criteria, the conformance test kit partners run, telemetry gates, who supports a certified connector, recertification after platform releases, decertifying or transitioning existing badges.
- Do not route here: the admission security review (`app-marketplace-review`); where a badge renders on a listing (`app-marketplace-listing-standards`); a vendor earning a badge on someone else's catalog (`etl-connector-strategy`, `integration-listing-optimization`); certifying people (`samber/developer-relations-skills@developer-certification-program`).

### `samber/developer-platform-skills@app-marketplace-listing-standards`

- Route here: defining what every listing must contain, screenshot and media requirements, the description quality bar, category taxonomy design, rejection criteria, when stale listings get downgraded or delisted.
- Do not route here: optimizing your own listing on someone else's marketplace; the security review behind admission.

### `samber/developer-platform-skills@app-marketplace-monetization-model`

- Route here: merchant-of-record posture, billing rails, the fee stack and its anti-circumvention rule, fee waivers, payout cadence and hold windows, the facilitator/VAT tax layer.
- Do not route here: the take-rate _level_ and tier structure (`connector-marketplace-strategy`); this skill designs the collection mechanics under whatever level that skill set.

### `samber/developer-platform-skills@app-marketplace-launch-marketing`

- Route here: launching a marketplace, sizing the founding cohort, coordinating the reveal and partner embargoes, featured-app and spotlight rotations, allocating MDF and per-partner co-marketing budget.
- Do not route here: a vendor optimizing its own listing on someone else's marketplace.

### `samber/developer-platform-skills@github-engagement-playbook`

- Route here: "our GitHub stars are flat", whether and how to run Discussions on an SDK repository, getting releases noticed by watchers, which topics to set, a label scheme for issues, PRs and discussions, keeping the repository visibly active in the feed, archiving traffic and tracking mentions, PR and tracking-issue templates, a board deck that reports stars, a request to buy, trade or reward stars.
- Do not route here: the launch itself (`samber/developer-relations-skills@oss-launch`), README text and sidebar copy (`samber/developer-relations-skills@readme-optimization`), a profile page (`samber/developer-relations-skills@github-profile-optimization`), the cross-channel distribution mix (`samber/developer-relations-skills@oss-distribution-strategy`), publishing the package behind a release (`sdk-package-publishing`), choosing a license (`samber/developer-relations-skills@oss-license-strategy`).

### `samber/developer-platform-skills@stackoverflow-playbook`

- Route here: "our Stack Overflow tag is full of unanswered questions", staff or engineers answering on Stack Overflow, answers flagged as spam or self-promotion, the tag excerpt and wiki, ChatGPT-drafted answers, whether Stack Overflow is still worth the hours.
- Do not route here: the error pages on your own docs (`samber/developer-relations-skills@developer-troubleshooting-docs`), getting your own docs cited by AI assistants (`samber/developer-relations-skills@developer-docs-ai-visibility`), measuring several community channels together (`samber/developer-relations-skills@developer-community-health`), an internal Stack Internal (Teams) instance.

### `samber/developer-platform-skills@developer-platform-career`

- Route here: breaking into an API Product Manager, Platform Engineer/Architect, or Partner/Integration Engineer role, prepping a platform-engineering or API-PM interview, evaluating an offer against this track's own ladder and comp benchmark.
- Do not route here: hiring for these roles (`developer-platform-hiring`), or a developer advocate, community manager, developer educator, or DevRel-flavored DX engineer target - `samber/developer-relations-skills@devrel-career`.

### `samber/developer-platform-skills@developer-platform-hiring`

- Route here: writing a posting, building a scorecard or interview loop, sourcing candidates, or setting a compensation stance for an API Product Manager, Platform Engineer/Architect, or Partner/Integration Engineer role.
- Do not route here: candidate-side prep (`developer-platform-career`), or hiring a developer advocate, community manager, developer educator, or DevRel-flavored DX engineer - `samber/developer-relations-skills@devrel-hiring`.

### `samber/developer-platform-skills@developer-platform-kickoff`

- Route here: project start, periodic check-in, "which skill do I need", re-routing mid-project. This skill routes; it never performs a sibling's job itself.

## Boundary pairs

Where two or more siblings collide on keywords, decide from these declared-scope boundaries.

**Split by altitude.** The kickoff's altitude rule names each macro/tactical pair; these are the questions that decide them at the boundary:

- **api-integration-surface-strategy vs every per-surface skill** - "Should we add GraphQL?" → strategy. "Design our GraphQL schema" → the surface skill. A surface question arriving with no audience attached is always the strategy question in disguise.
- **api-versioning-policy vs public-api-design-review** - "What are we allowed to change?" → policy. "Is this surface well-designed?" → review. A review that finds no agreed breaking-change definition escalates up to the policy.
- **sdk-portfolio-strategy vs api-idempotency-retry** - "Which SDKs first?" → portfolio. "What should the SDK do on a 503?" → idempotency-retry.
- **cli-interface-design vs mcp-server-offering** - "What commands, flags and `--json` contract does our CLI expose?" → CLI. "Which tools does our MCP server expose?" → MCP. Both may serve agents; which surface to build first is `api-integration-surface-strategy`.
- **cli-interface-design vs sdk-package-publishing** - "What does the CLI do and promise?" → CLI design. "How do we ship its binaries and packages?" → publishing.
- **github-action-offering vs cli-interface-design / sdk-package-publishing** - "What does our action take, output and promise, and how do we tag and secure it?" → action. "What do the CLI's commands and exit codes promise?" → CLI. "How do we publish the CLI binary to registries and Homebrew?" → publishing. A new action usually needs all three, in that reverse order: CLI contract, then binaries, then the action.
- **ide-extension-offering vs cli-interface-design / mcp-server-offering** - "Should we ship a VS Code or JetBrains extension, and how do we publish, measure and retire it?" → extension. "What does the CLI the extension wraps promise?" → CLI. "Which tools do agents in the editor call?" → MCP; the extension may only distribute that server. A new extension usually needs the CLI contract first.
- **agent-integration-surfaces vs api-integration-surface-strategy / mcp-server-offering** - "Should we add MCP or a CLI next to REST and SDKs?" → surface strategy. "Which agents get in where, how do they authenticate and act for users, sign up, and get counted?" → agent integration surfaces, which picks the execution path per agent class and hands each surface's design to its skill. "Which tools does the MCP server expose?" → MCP.
- **agent-skill-offering vs mcp-server-offering / cli-interface-design** - "Ship instructions that teach agents to drive our CLI or SDK, versioned with it" → agent skill. "Expose our product as remote tools an agent without a shell can call" → MCP. "Design the CLI's commands and `--json` contract" → CLI design. The skill's step 1 hands the other two over.
- **terraform-provider-offering vs sdk-package-publishing / api-integration-surface-strategy** - "Should we have an IaC surface at all, next to SDKs and a CLI?" → surface strategy. "Design, sign and publish our Terraform/OpenTofu provider" → provider offering. "Ship our Go SDK or CLI binary to a registry" → publishing; the provider's own GoReleaser and Registry flow stays with the provider skill.
- **sdk-portfolio-strategy vs sdk-package-publishing** - "Which SDKs should exist and at what tier?" → portfolio. "How do we ship them to npm and PyPI without long-lived tokens?" → publishing.
- **sdk-package-publishing vs github-engagement-playbook** - "How does the package reach the registry?" → publishing. "How does the GitHub Release reach watchers, and what do we post in Discussions?" → playbook. One release usually needs both, publishing first.
- **stackoverflow-playbook vs api-error-design** - "What does the error response say?" → error design. "Where does the fix live when a developer pastes that error into a search engine?" → the playbook's canonical Q&A, mirrored by `samber/developer-relations-skills@developer-troubleshooting-docs` on your own docs.
- **sample-app-strategy vs sdk-portfolio-strategy / api-test-mode-design** - "Which sample repos do we keep, and in which languages?" → samples. "Which SDK languages exist?" → SDK portfolio. "What do the samples run against?" → test mode. SDK tiers feed sample coverage; never the reverse.
- **developer-portal-design vs api-auth-key-management / api-test-mode-design / integration-error-observability / api-reference-quality** - "Where does the key dashboard live and what else belongs on that page?" → portal. "What does a key look like and how does rotation work?" → key management. The portal decides which self-service surfaces exist and where; each sibling designs one of them.
- **connector-marketplace-strategy vs the four app-marketplace skills** - "Should we build one?" and "what take-rate?" → strategy. "How do we collect it?" → monetization-model. "What must a listing contain?" → listing-standards. "What gets rejected?" → review. "How do we launch it?" → launch-marketing.
- **integration-partnership-strategy vs partner-app-onboarding / etl-connector-strategy / integration-listing-optimization** - "Which partners matter?" → strategy. "How does a partner get from signup to first app?" → onboarding. "How do we get listed on their ETL catalog?" → etl-connector-strategy. "Why is our listing not converting?" → listing-optimization.

- **zapier-integration-playbook vs integration-listing-optimization / webhook-platform-design** - one platform's mechanics vs the generic method. "How do we build, review, launch and version our Zapier app?" → the playbook. "Why does our listing not convert across marketplaces?" → listing-optimization. "How does our API let anyone subscribe to events?" → webhook-platform-design, which the playbook's REST hook triggers then call.
- **salesforce-appexchange-playbook vs integration-listing-optimization / app-marketplace-review** - one marketplace's admission and money path vs the generic listing method vs the operator's chair. "How do we pass Salesforce's security review, package and get paid?" → the playbook. "Why does our AppExchange listing not convert or rank?" → listing-optimization. "How should our own marketplace review third-party apps?" → app-marketplace-review.
- **slack-app-directory-playbook vs integration-listing-optimization / app-marketplace-review / oauth2-provider-design** - one marketplace's admission rules vs the generic listing method vs the operator's chair vs the issuer's chair. "Why did Slack return our app and which scopes will pass?" → the playbook. "Why does our Slack listing not convert?" → listing-optimization. "How should our own marketplace review apps?" → app-marketplace-review. "How should our API's scopes be designed?" → oauth2-provider-design.

**Split by side of the table:**

- **integration-listing-optimization vs app-marketplace-listing-standards / app-marketplace-launch-marketing** - same words, opposite chairs. You are the submitter optimizing a listing you own on a marketplace you don't → listing-optimization. You are the operator writing the rules and promoting the catalog → standards and launch-marketing. Ask which side of the review gate the user sits on before routing any "marketplace listing" question.
- **api-auth-key-management vs oauth2-provider-design** - both are credentials you issue, split by whose data the caller acts on. The customer's own backend calling your API on its own behalf → API keys. A third-party app acting on your _users'_ behalf, needing consent → OAuth. Key management owns the decision boundary itself, so an unresolved "keys or OAuth?" starts there.
- **webhook-platform-design vs api-idempotency-retry** - both concern retries, split by direction. You delivering events to a consumer, with your retry schedule and dead-letter policy → webhook-platform-design. A client retrying its call into you, with idempotency keys and backoff → idempotency-retry.

**Split by scope of the audience:**

- **api-error-design vs integration-error-observability vs api-status-communication** - three altitudes of "something failed":
  - One response body an integrator receives → api-error-design. "Our error messages are useless" routes here.
  - One integration's history, aggregated and replayable, visible to the integrator who built it → integration-error-observability. "Partners don't know their integration is broken" routes here.
  - The whole platform's health, visible to everyone at once → api-status-communication. "Customers didn't know we were down" routes here.
- **integration-error-observability vs integration-health-monitoring** - split by tense. An integration failing now, seen in errors, logs and alerts → error-observability. An integration working today that a dated change will break - a sunset, an SDK end of life, a credential expiry → health-monitoring. "Partners don't know their integration is broken" routes to the first; "partners don't know their integration will break on March 31" routes to the second.
- **api-versioning-policy vs integration-health-monitoring** - the policy sets notice windows, headers and enforcement style once; health-monitoring runs that policy integration by integration - census, outreach, brownouts, readiness gate. Pulling a published date earlier is a policy change and goes back to the policy.
- **sql-jdbc-access-design vs bulk-data-sharing-design vs etl-connector-strategy** - three ways to give customers the data, split by who runs the pipe:
  - You expose a live queryable endpoint or share → SQL/JDBC.
  - You deliver files or a lake share on a cadence → bulk sharing.
  - A third-party ETL platform pulls from your API on the customer's behalf → etl-connector-strategy.

  Scan frequency and freshness expectations decide between the first two; who the customer already pays decides the third.

- **public-roadmap-strategy vs api-versioning-policy vs api-status-communication** - three horizons of telling consumers about change:
  - What is coming, and how firmly → public-roadmap-strategy. "Customers keep asking what's next" routes here.
  - What is going away, on what notice → api-versioning-policy. "We need to retire /v1" routes here.
  - What is broken right now → api-status-communication.

- **api-versioning-policy vs api-changelog-automation** - "What counts as breaking, and how much notice?" → policy. "Make CI enforce that definition and write the change record" → automation. An automation request with no written definition escalates to the policy first; the gate may ship meanwhile with a severity map marked provisional.
- **api-reference-quality vs api-changelog-automation** - both put a spec in CI. Is the published reference complete against the spec → reference quality. What changed between two versions of the spec, and did it break callers → automation.

- **api-beta-program vs api-versioning-policy** - the GA line splits them. Before GA, including retiring one preview version for the next and rescuing a beta that never ended → api-beta-program. After GA, including the deprecation window a graduated beta surface gets → api-versioning-policy. A beta program uses the versioning policy's breaking-change definition rather than writing its own.

- **public-graphql-api-design vs graphql-federation-offering** - "Design our public schema" or "split it across our teams" → public-graphql-api-design. "Let partners add their own fields or subgraphs" → graphql-federation-offering. The test is who authors the contributed schema: your own teams, or an outside party.
- **api-rate-limit-policy vs public-graphql-api-design** - GraphQL's depth and complexity ceilings are schema design decisions and live with the schema; the published quota, tier numbers, headers and 429 contract are policy and live with rate-limit-policy. A GraphQL cost model needs both, in that order.
- **partner-app-onboarding vs app-marketplace-review vs api-test-mode-design** - three stages of the same partner's path:
  - Getting to a first submission → onboarding.
  - What happens to that submission → review.
  - How the sandbox they build in is actually isolated → test-mode-design.
- **app-marketplace-review vs connector-certification-program vs app-marketplace-listing-standards** - three questions about the same badge:
  - Is the app safe to admit at all → review.
  - What earns, keeps and loses the certified label → certification program.
  - Where the earned badge shows and how its currency renders → listing standards.

## Ordered chains

Propose a chain only when the task genuinely decomposes this way; never fabricate a sequence. Each chain is listed in dependency order, not efficiency order - a later link consumes what the earlier one produces, so there is no ratio to rank.

- `api-integration-surface-strategy` → the chosen surface skill → `api-versioning-policy` - decide which surface, design it, then commit to what you will and won't break in it. Publish before the promise exists and every later change is negotiated case by case.
- `api-versioning-policy` → `api-changelog-automation` - write the breaking-change definition, then encode it as the severity map the gate enforces. Automating first makes the diff tool's defaults the policy nobody chose.
- `public-api-design-review` → `api-error-design` → `api-idempotency-retry` → `api-reference-quality` - audit, fix the error contract the audit exposed, make failing calls safe to retry, then document. Documenting first just freezes the flaws in prose.
- `api-auth-key-management` → `api-rate-limit-policy` → `integration-error-observability` - you cannot meter or attribute what you cannot identify; the identity issued first is what limits key on and what error rates split by.
- `oauth2-provider-design` → `partner-app-onboarding` → `app-marketplace-review` - apps need delegated auth before a partner journey means anything, and a journey before there are submissions to review.
- `connector-marketplace-strategy` → `app-marketplace-listing-standards` → `app-marketplace-review` → `app-marketplace-monetization-model` → `app-marketplace-launch-marketing` - settle whether and at what curation level, write what a listing must contain, define what gets rejected, wire up collection, then launch. Launching first means grandfathering every early listing.
- `developer-portal-design` → `api-test-mode-design` → `api-reference-quality` - the portal decides which self-service surfaces exist and where; the sandbox and the reference each land in a slot it already reserved.
- `integration-partnership-strategy` → `etl-connector-strategy` or `integration-listing-optimization` - the prioritization decides which platform is worth the connector or listing. Building either first pays a maintenance tax for a platform nobody's customers use.
- `public-api-design-review` → `api-idempotency-retry` → `terraform-provider-offering` - the provider's readiness gate fails on non-idempotent creates and fields never read back; fix the contract before mapping it to resources, or every gap ships as a perpetual diff.
- `webhook-platform-design` → `integration-error-observability` - delivery logs and replay are the debugging surface for the deliveries the first link creates.
- `api-versioning-policy` → `integration-health-monitoring` → `integration-error-observability` - set the notice and enforcement rules, run them per integration until the gate passes, then catch the callers the census missed as errors after cutoff.
- `public-api-design-review` → `api-beta-program` → `api-versioning-policy` - review the new surface at beta level, run the preview that freezes its shape, then put the GA surface under the compatibility promise. Enrolling partners before the review freezes an unreviewed shape.

## Sibling-repo recommendations

`developer-platform-skills` owns the _platform surface_: the API and its lifecycle, the integration surfaces around it, the portal, and the partner and marketplace ecosystem. Two sibling `samber` collections cover adjacent ground this collection intentionally excludes. Recommend installing the sibling instead of stretching a task onto a skill above that doesn't cover it; never frame it as a dependency - this collection stays fully usable standalone.

### `samber/developer-relations-skills` - DevRel practice

Recommend the sibling repo, not a skill above, when the task is:

- Site-wide docs information architecture, rather than endpoint-level reference completeness → `samber/developer-relations-skills@developer-docs-structure-audit`.
- The quickstart page and its first-run narrative → `samber/developer-relations-skills@developer-quickstart-guide`.
- Making an existing SDK, API or protocol consumable by a coding agent unattended → `samber/developer-relations-skills@coding-agent-docs-optimization`. Distinct from `mcp-server-offering`, which builds a _new_ agent-facing tool surface rather than documenting an existing one.
- Whether to evolve from product to platform at all, and how far up the openness ladder → `samber/developer-relations-skills@developer-ecosystem-strategy`. Upstream of `connector-marketplace-strategy`: the ecosystem question is "should we be a platform", the marketplace question is "should we run a catalog".
- The devtools revenue model, or what to open-source → `samber/developer-relations-skills@devtools-business-model`, `samber/developer-relations-skills@oss-distribution-strategy`.
- A launch, relaunch or ongoing presence on Product Hunt - self-hunting, account eligibility, featuring vs points, maker comment, vote-solicitation and AI-comment rules, relaunch gaps → `samber/developer-relations-skills@producthunt-playbook`. Distinct from `app-marketplace-launch-marketing`, which runs a marketplace operator's own launch program.
- A certification or badge that vouches for a developer or partner engineer, rather than for an app → `samber/developer-relations-skills@developer-certification-program`. Distinct from `partner-app-onboarding`, which decides whether education gates a partner's first submission, from `app-marketplace-review`, which admits the app, and from `connector-certification-program`, which certifies partner-built connectors.
- Feature requests scattered across community, support and sales channels, and closing the loop with requesters → `samber/developer-relations-skills@developer-feedback-loop`. Distinct from `public-roadmap-strategy`, which publishes what those decisions add up to.
- A vulnerability report against an open-source SDK, SECURITY.md, CVE and advisory, the disclosure embargo → `samber/developer-relations-skills@oss-security-disclosure`. `sdk-package-publishing` still ships the patched version.
- The release contract of an open-source SDK or library - SemVer vs CalVer, when to ship 1.0, supported versions and LTS, backports, cadence, deprecation windows → `samber/developer-relations-skills@oss-release-policy`. `sdk-package-publishing` ships each version under that policy; `api-versioning-policy` versions the hosted API.
- A maintainer burning out on an open-source SDK, wanting to step back, hand it over or archive it → `samber/developer-relations-skills@oss-maintainer-sustainability`. `sdk-package-publishing` still owns the registry deprecation and ownership mechanics it triggers.
- A maintainer wanting an open-source SDK or library to pay them - a paid add-on, support, a commercial license on the next major → `samber/developer-relations-skills@oss-monetization`. `sdk-package-publishing` still owns publishing the paid package to a private feed.
- Whether and how to translate the docs, and keeping translations current → `samber/developer-relations-skills@docs-localization-strategy`.
- Which docs versions stay live, a docs version switcher, archived old-version docs, doc-fix backports → `samber/developer-relations-skills@docs-versioning-strategy`. The hosted API's version scheme stays with `api-versioning-policy`.
- AI assistants answering with deprecated APIs or old-version docs, and measuring AI-answer correctness → `samber/developer-relations-skills@developer-docs-ai-visibility`. The deprecation policy itself stays with `api-versioning-policy`.
- A Show HN, a Hacker News thread about the product, staff commenting there, or a Who is hiring post → `samber/developer-relations-skills@hackernews-playbook`. Distinct from `stackoverflow-playbook`, which covers the Q&A archive, not a discussion site.
- A repository about to go public, or a launch-day Trending push → `samber/developer-relations-skills@oss-launch`; the README page itself → `samber/developer-relations-skills@readme-optimization`. Distinct from `github-engagement-playbook`, which tends the repository's GitHub surfaces after launch.
- The troubleshooting pages on your own docs that a Stack Overflow canonical mirrors → `samber/developer-relations-skills@developer-troubleshooting-docs`. `stackoverflow-playbook` runs the product tag itself.
- A vendor's or maintainer's presence on dev.to - organization account, canonical cross-posting, tag rules, AI disclosure → `samber/developer-relations-skills@devto-playbook`. `stackoverflow-playbook` and `github-engagement-playbook` stay here.
- Anything else in the DevRel practice - developer content and SEO, community, events, open-source program operations. Start at `samber/developer-relations-skills@developer-relations-kickoff` when the boundary is unclear.

Distinguish from this collection: `developer-platform-skills` owns what the platform _is_ and what integrating with it costs; `developer-relations-skills` owns how developers hear about it, learn it, and stay. "Design our webhook platform" stays here; "write the tutorial that teaches it" goes to the sibling.

**Career and hiring split by what the role is screened on, not by the word "platform" in a title.** `developer-platform-career`/`-hiring` cover API Product Manager, Platform Engineer/Architect, and Partner/Integration Engineer - roles screened on API and system design judgment as a primary skill. `samber/developer-relations-skills@devrel-career`/`devrel-hiring` cover developer advocate, community manager, developer educator, and DevRel's own DX-engineer flavor - roles screened on communication and community craft. A "platform engineer" title is doubly ambiguous on top of this split: it can also mean internal developer platforms (Kubernetes, Backstage, golden paths), a population neither pair of skills covers - see `developer-platform-career`'s own disambiguation step before routing any "platform engineer" hiring or career task.

### `samber/dev-event-organizer-skills` - technical event operations

Recommend the sibling repo when the task is running a conference, hackathon, meetup or developer event as an _event_ - venue, sponsorship, CFP, speakers, budget, logistics - rather than as a DevRel program. A marketplace launch keynote is `app-marketplace-launch-marketing` here; producing the conference the keynote happens at is the sibling repo.

Coverage gaps this collection does not fill at all - per-marketplace submission playbooks, publishing-platform playbooks beyond GitHub and Stack Overflow, federated-graph offerings, API monetization, connector certification programs, and deployed-integration health monitoring - are listed with their boundaries in `samber/developer-platform-skills@developer-platform-kickoff` § 8. Name the gap from there; never promise a skill exists.
