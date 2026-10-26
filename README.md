# Developer platform skills

Skills for building and running the **developer-facing surface of a SaaS product**: public APIs and their lifecycle, webhooks, SDKs, the developer portal, and the connector marketplace around it.

Written for **platform PMs, API and DX engineers, SDK authors, and partner engineering**: design and policy work, not code generation. Every skill is **tool-agnostic**: it teaches the decision, not one vendor's console.

<img width="1904" height="640" alt="image" src="https://github.com/user-attachments/assets/b8a9d183-8c93-4124-8ccc-8c7d9acd2807" />

## 📚 Related Collections

- [`developer-relations-skills`](https://github.com/samber/developer-relations-skills): DevRel strategy & execution: _for developer advocates, DevRel managers, community managers_
- [`dev-event-organizer-skills`](https://github.com/samber/dev-event-organizer-skills): Technical event operations: _for event organizers, conference producers, hackathon leads, community builders_

_Part of the [samber skills ecosystem](https://github.com/samber?tab=repositories&q=skills)_

## 🚀 Install

Install every skill in this repo, not just one. Skills here are atomic by design and reference each other freely: picking a single skill leaves its sibling skills uninstalled, so cross-references and routed handoffs go nowhere.

<details>
<summary><b>skills.sh</b> — universal, works with any Agent Skills-compatible tool</summary>

```bash
npx skills add samber/developer-platform-skills
```

</details>

<details>
<summary><b>Claude.ai</b></summary>

1. add as a plugin marketplace: open **Settings -> Capabilities -> Plugins**
2. click **Add -> Add marketplace -> Add from a repository**
3. enter `samber/developer-platform-skills`
4. then **Sync**

</details>

<details>
<summary><b>Claude Code</b></summary>

```bash
/plugin marketplace add samber/developer-platform-skills
/plugin install developer-platform-skills@developer-platform-skills
```

</details>

<details>
<summary><b>Codex (OpenAI)</b></summary>

```bash
codex plugin add github:samber/developer-platform-skills
```

</details>

<details>
<summary><b>Cursor</b></summary>

```bash
git clone https://github.com/samber/developer-platform-skills.git ~/.cursor/skills/developer-platform-skills
```

Cursor auto-discovers skills from `.agents/skills/` and `.cursor/skills/`.

</details>

<details>
<summary><b>Gemini CLI</b></summary>

```bash
gemini extensions install https://github.com/samber/developer-platform-skills
```

Update with `gemini extensions update developer-platform-skills`.

</details>

### First run

```
/developer-platform-kickoff We're about to publish our first public REST API and I'm not sure the design is ready to commit to.
```

## 📦 Skills

This collection covers the full developer-platform surface.

### Start here

[`developer-platform-kickoff`](./skills/developer-platform-kickoff): Routes any developer-platform task to the right skill in this collection, returning a ranked short-list, an ordered chain, and an honest gap list.

### Meta

- [`developer-platform-career`](./skills/developer-platform-career): Plans a developer-platform career from the candidate side: role track, company archetype, portfolio signals, interview prep, and offer benchmarking.
- [`developer-platform-hiring`](./skills/developer-platform-hiring): Builds the hiring side of a developer-platform role: scorecard, interview loop, sourcing channels, and compensation stance.

### API design

- [`api-error-design`](./skills/api-error-design): Designs a public API's error surface so integrators self-serve fixes: error-code taxonomy, RFC 9457 envelope, and retryability signals.
- [`api-idempotency-retry`](./skills/api-idempotency-retry): Designs idempotency-key support and client retry guidance, from key scoping and replay windows to backoff, retry budgets, and SDK defaults.
- [`api-rate-limit-policy`](./skills/api-rate-limit-policy): Defines the rate-limit policy a public API publishes: quota and burst numbers, response headers, the 429 contract, and override paths.
- [`public-api-design-review`](./skills/public-api-design-review): Audits a REST API surface against cited rules, buckets every finding as Must-change or Improvement, and designs the standing review program.
- [`public-graphql-api-design`](./skills/public-graphql-api-design): Designs a public GraphQL surface: the GraphQL-or-not gate, schema conventions, cursor pagination, complexity ceilings, and the federation trust boundary.
- [`graphql-federation-offering`](./skills/graphql-federation-offering): Decides how partners extend a public GraphQL graph, from app-owned fields to isolated partner subgraphs, with the trust contract each rung needs.
- [`public-grpc-api-design`](./skills/public-grpc-api-design): Decides whether to expose gRPC publicly, then designs the proto conventions, breaking-change gates, error model, and transcoding path.

### API authentication

- [`api-auth-key-management`](./skills/api-auth-key-management): Designs the API-key surface a platform issues: key format, hashed storage, least-privilege scoping, zero-downtime rotation, and lifecycle governance.
- [`oauth2-provider-design`](./skills/oauth2-provider-design): Designs the OAuth2 authorization server offered to third-party apps: an OAuth 2.1 baseline, scope taxonomy, consent, and app verification.

### API documentation

- [`api-reference-quality`](./skills/api-reference-quality): Audits a published API reference endpoint by endpoint, then drives remediation through a staged source-of-truth rollout with CI gates.

### API lifecycle

- [`api-versioning-policy`](./skills/api-versioning-policy): Defines an API's versioning and deprecation policy: version scheme, breaking-change definition, notice windows, sunset signalling, and enforcement.
- [`api-changelog-automation`](./skills/api-changelog-automation): Builds the pipeline from API contract diffs to a breaking-change CI gate and a traced, per-version changelog feed.
- [`public-roadmap-strategy`](./skills/public-roadmap-strategy): Decides whether and how to publish a product roadmap: posture, commitment vocabulary, exclusion gate, sales guardrails, and the slipped-item playbook.
- [`api-beta-program`](./skills/api-beta-program): Runs a preview, beta or design-partner program for a new API feature: stage guarantees, cohort, per-account access, and exit to GA or kill.

### Integration surfaces

- [`agent-integration-surfaces`](./skills/agent-integration-surfaces): Plans how a platform opens itself to AI agents, class by class: access policy per surface, agent identity and delegation, provision-then-claim signup, and agent usage measurement.
- [`agent-skill-offering`](./skills/agent-skill-offering): Ships an Agent Skill inside a library, CLI or SDK repo and keeps it versioned with the code: placement, version wiring, CI gates that fail a stale release, tag-pinned installs, and multi-harness manifests.
- [`api-integration-surface-strategy`](./skills/api-integration-surface-strategy): Decides which integration surfaces a platform offers external developers and AI agents, and in what build order, sequenced by reversal cost.
- [`bulk-data-sharing-design`](./skills/bulk-data-sharing-design): Designs bulk file and lake export as a product surface: delivery format, partitioning contract, cadence and freshness posture, credentials, and cost allocation.
- [`etl-connector-strategy`](./skills/etl-connector-strategy): Plans a vendor's presence as a source connector on customers' ETL platforms: demand gate, build path, certification target, and funded maintenance.
- [`cli-interface-design`](./skills/cli-interface-design): Designs the public CLI that wraps the platform's API: command layers and grammar, a frozen `--json` and exit-code contract, login flows, and safe non-interactive use by scripts and agents.
- [`github-action-offering`](./skills/github-action-offering): Ships a vendor's official GitHub Action and its CI ports: offering shape, action type, a frozen `action.yml` contract, immutable releases, OIDC auth, and hardening against injection and tag hijack.
- [`ide-extension-offering`](./skills/ide-extension-offering): Decides whether a platform ships an official VS Code or JetBrains extension, for which jobs, then runs it: thin shell over the CLI, publishing to three marketplaces, telemetry and deprecation.
- [`mcp-server-offering`](./skills/mcp-server-offering): Designs a product's MCP server for AI agents: a curated workflow-level tool set, write-safety patterns, hosting and auth posture, and versioning.
- [`sql-jdbc-access-design`](./skills/sql-jdbc-access-design): Designs customer-facing live SQL access: the architecture gate on scan economics, tenant isolation, schema-stability contract, BI connectivity, and pricing shape.
- [`terraform-provider-offering`](./skills/terraform-provider-offering): Decides whether a platform ships its own Terraform/OpenTofu provider, then designs, tests, signs, publishes and versions it on both registries.
- [`webhook-platform-design`](./skills/webhook-platform-design): Designs a provider-side outbound webhook platform: event taxonomy, signed payload envelope, retry and dead-letter policy, and the consumer debugging surface.

### Testing and sandbox

- [`api-test-mode-design`](./skills/api-test-mode-design): Designs the test/sandbox mode integrators build against: isolation model, test keys, magic values, deterministic events, reset, and the path to live.

### SDKs and client libraries

- [`sdk-portfolio-strategy`](./skills/sdk-portfolio-strategy): Decides which languages get official SDKs and in what order, with build model, support tiers, versioning, and end-of-life policy.
- [`sdk-package-publishing`](./skills/sdk-package-publishing): Plans and hardens SDK, library and CLI publishing across npm, PyPI, Maven Central, NuGet, Go, crates.io, pub.dev, RubyGems, Packagist, Hex, SwiftPM, CocoaPods and Docker Hub, plus dependency-confusion-safe private feeds.

### Developer portal

- [`developer-portal-design`](./skills/developer-portal-design): Designs an external developer portal: information architecture, the signup-to-first-call path, self-service surface placement, search, RBAC, and build-vs-buy.
- [`sample-app-strategy`](./skills/sample-app-strategy): Decides the sample-code portfolio: which quickstart repos, reference apps, templates and playgrounds exist, per developer job and language, with owners, CI-tested freshness, and archive rules.

### Status, incidents and integration health

- [`api-status-communication`](./skills/api-status-communication): Designs how an API platform tells consumers what is happening: status-page modeling, incident cadence, public postmortems, and SLA reporting.
- [`integration-error-observability`](./skills/integration-error-observability): Designs how a platform surfaces integration failures to external developers: delivery logs, correlation IDs, error-rate aggregation, and notification posture.
- [`integration-health-monitoring`](./skills/integration-health-monitoring): Finds deployed integrations that will break on a known date, reaches their owners, and gates the sunset on a per-integration readiness check.

### Integration partnerships

- [`integration-listing-optimization`](./skills/integration-listing-optimization): Optimizes a vendor's listing on a third-party app marketplace: funnel instrumentation, indexed keyword placement, media ordering, reviews, and badges.
- [`integration-partnership-strategy`](./skills/integration-partnership-strategy): Decides which technology partners to integrate with and how deep each goes, using a demand-data scorecard, depth ladder, and pipeline attribution.
- [`partner-app-onboarding`](./skills/partner-app-onboarding): Designs the partner-developer journey from signup to first submitted app: entry gate, sandbox provisioning, education, support ladder, and funnel checkpoints.
- [`salesforce-appexchange-playbook`](./skills/salesforce-appexchange-playbook): Takes a vendor's product onto Salesforce AppExchange as an ISV: listing type, irreversible 2GP choices, security review, PADA and payment path, and post-listing upkeep.
- [`slack-app-directory-playbook`](./skills/slack-app-directory-playbook): Gets a vendor's Slack app approved for the Slack Marketplace and keeps it listed: install gate, scope justifications, submission packet, review timeline, and post-listing rules.
- [`zapier-integration-playbook`](./skills/zapier-integration-playbook): Builds, publishes and maintains a vendor's Zapier integration: step design, Platform CLI code, review checks and beta, templates and embed, and versioning without breaking live Zaps.

### Publishing-platform playbooks

- [`github-engagement-playbook`](./skills/github-engagement-playbook): Plans a repository's engagement on GitHub after launch: flat-star diagnosis, releases as feed events, Discussions, topics, and the limits on star tactics.
- [`stackoverflow-playbook`](./skills/stackoverflow-playbook): Runs a vendor's Stack Overflow presence: product-tag ownership, disclosed staff answers, backlog triage by views, and canonical Q&A that ranks in search.

### Connector marketplace

- [`app-marketplace-launch-marketing`](./skills/app-marketplace-launch-marketing): Designs a marketplace launch and ongoing app co-marketing program: founding cohort size, reveal coordination, featuring menu, and budget split.
- [`app-marketplace-listing-standards`](./skills/app-marketplace-listing-standards): Writes the listing-content rulebook an operator enforces on submissions: required fields, media geometry, quality bar, taxonomy, badges, and staleness policy.
- [`app-marketplace-monetization-model`](./skills/app-marketplace-monetization-model): Designs how a marketplace earns on the operator side: merchant-of-record posture, billing rails, fee stack, waiver programs, payouts, and tax split.
- [`app-marketplace-review`](./skills/app-marketplace-review): Designs the operator-side review and approval process for third-party apps: pipeline shape, permission audits, re-review triggers, and the enforcement ladder.
- [`connector-certification-program`](./skills/connector-certification-program): Designs the certification label for partner-built connectors: go/no-go, measurable criteria, test kit, support routing, renewal, and decertification.
- [`connector-marketplace-strategy`](./skills/connector-marketplace-strategy): Decides whether to build a connector marketplace, join others', or buy embedded iPaaS, then designs governance, curation, take rate, and seeding.

## 👤 Contributors

![Contributors](https://contrib.rocks/image?repo=samber/developer-platform-skills)

## 💫 Show your support

Give a ⭐️ if this project helped you!

[![GitHub Sponsors](https://img.shields.io/github/sponsors/samber?style=for-the-badge)](https://github.com/sponsors/samber)

## 📝 License

Copyright © 2026 [Samuel Berthe](https://github.com/samber).

This project is under [MIT](./LICENSE) license.
