# Developer platform skills

Skills for building and running the **developer-facing surface of a SaaS product**: public APIs and their lifecycle, webhooks, SDKs, the developer portal, and the connector marketplace around it.

Written for **platform PMs, API and DX engineers, SDK authors, and partner engineering**: design and policy work, not code generation. Every skill is **tool-agnostic**: it teaches the decision, not one vendor's console.

## 📚 Related Collections

- [`developer-relations-skills`](https://github.com/samber/developer-relations-skills): DevRel strategy & execution: _for developer advocates, DevRel managers, community managers_
- [`dev-event-organizer-skills`](https://github.com/samber/dev-event-organizer-skills): Technical event operations: _for event organizers, conference producers, hackathon leads, community builders_

_Part of the [samber skills ecosystem](https://github.com/samber?tab=repositories&q=skills)_

## 🚀 Install

Install every skill in this repo, not just one. Skills here are atomic by design and reference each other freely: picking a single skill leaves its sibling skills uninstalled, so cross-references and routed handoffs go nowhere.

**skills.sh (universal)**: works with any Agent Skills-compatible tool:

```bash
npx skills add samber/developer-platform-skills
```

**Claude.ai**:

1. add as a plugin marketplace: open **Settings -> Capabilities -> Plugins**
2. click **Add -> Add marketplace -> Add from a repository**
3. enter `samber/developer-platform-skills`
4. then **Sync**

**Claude Code**: install the plugin:

```bash
/plugin marketplace add samber/cc
/plugin install developer-platform-skills@samber
```

**Codex (OpenAI)**: install via the Codex CLI:

```bash
codex plugin add github:samber/developer-platform-skills
```

**Cursor**: copy into Cursor's skills directory:

```bash
git clone https://github.com/samber/developer-platform-skills.git ~/.cursor/skills/developer-platform-skills
```

Cursor auto-discovers skills from `.agents/skills/` and `.cursor/skills/`.

**Gemini CLI**: install as a Gemini extension:

```bash
gemini extensions install https://github.com/samber/developer-platform-skills
```

Update with `gemini extensions update developer-platform-skills`.

## 📦 Skills

This collection covers the full developer-platform surface.

### Start here

[`developer-platform-kickoff`](./skills/developer-platform-kickoff): Routes any developer-platform task to the right skill in this collection, returning a ranked short-list, an ordered chain, and an honest gap list.

### Meta

- [`developer-platform-career`](./skills/developer-platform-career): Plans a developer-platform career from the candidate side: role track, company archetype, portfolio signals, interview prep, and offer benchmarking.
- [`developer-platform-hiring`](./skills/developer-platform-hiring): Builds the hiring side of a developer-platform role: scorecard, interview loop, sourcing channels, and compensation stance.

### API design

| Skill                                                             | Description                                                                                                                                               |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`api-error-design`](./skills/api-error-design)                   | Designs a public API's error surface so integrators self-serve fixes: error-code taxonomy, RFC 9457 envelope, and retryability signals.                   |
| [`api-idempotency-retry`](./skills/api-idempotency-retry)         | Designs idempotency-key support and client retry guidance, from key scoping and replay windows to backoff, retry budgets, and SDK defaults.               |
| [`api-rate-limit-policy`](./skills/api-rate-limit-policy)         | Defines the rate-limit policy a public API publishes: quota and burst numbers, response headers, the 429 contract, and override paths.                    |
| [`public-api-design-review`](./skills/public-api-design-review)   | Audits a REST API surface against cited rules, buckets every finding as Must-change or Improvement, and designs the standing review program.              |
| [`public-graphql-api-design`](./skills/public-graphql-api-design) | Designs a public GraphQL surface: the GraphQL-or-not gate, schema conventions, cursor pagination, complexity ceilings, and the federation trust boundary. |
| [`public-grpc-api-design`](./skills/public-grpc-api-design)       | Decides whether to expose gRPC publicly, then designs the proto conventions, breaking-change gates, error model, and transcoding path.                    |

### API authentication

| Skill                                                         | Description                                                                                                                                           |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`api-auth-key-management`](./skills/api-auth-key-management) | Designs the API-key surface a platform issues: key format, hashed storage, least-privilege scoping, zero-downtime rotation, and lifecycle governance. |
| [`oauth2-provider-design`](./skills/oauth2-provider-design)   | Designs the OAuth2 authorization server offered to third-party apps: an OAuth 2.1 baseline, scope taxonomy, consent, and app verification.            |

### API documentation

| Skill                                                     | Description                                                                                                                            |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| [`api-reference-quality`](./skills/api-reference-quality) | Audits a published API reference endpoint by endpoint, then drives remediation through a staged source-of-truth rollout with CI gates. |

### API lifecycle

| Skill                                                     | Description                                                                                                                                         |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`api-versioning-policy`](./skills/api-versioning-policy) | Defines an API's versioning and deprecation policy: version scheme, breaking-change definition, notice windows, sunset signalling, and enforcement. |

### Integration surfaces

| Skill                                                                           | Description                                                                                                                                                        |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`api-integration-surface-strategy`](./skills/api-integration-surface-strategy) | Decides which integration surfaces a platform offers external developers and AI agents, and in what build order, sequenced by reversal cost.                       |
| [`bulk-data-sharing-design`](./skills/bulk-data-sharing-design)                 | Designs bulk file and lake export as a product surface: delivery format, partitioning contract, cadence and freshness posture, credentials, and cost allocation.   |
| [`etl-connector-strategy`](./skills/etl-connector-strategy)                     | Plans a vendor's presence as a source connector on customers' ETL platforms: demand gate, build path, certification target, and funded maintenance.                |
| [`mcp-server-offering`](./skills/mcp-server-offering)                           | Designs a product's MCP server for AI agents: a curated workflow-level tool set, write-safety patterns, hosting and auth posture, and versioning.                  |
| [`sql-jdbc-access-design`](./skills/sql-jdbc-access-design)                     | Designs customer-facing live SQL access: the architecture gate on scan economics, tenant isolation, schema-stability contract, BI connectivity, and pricing shape. |
| [`webhook-platform-design`](./skills/webhook-platform-design)                   | Designs a provider-side outbound webhook platform: event taxonomy, signed payload envelope, retry and dead-letter policy, and the consumer debugging surface.      |

### Testing and sandbox

| Skill                                                   | Description                                                                                                                                           |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`api-test-mode-design`](./skills/api-test-mode-design) | Designs the test/sandbox mode integrators build against: isolation model, test keys, magic values, deterministic events, reset, and the path to live. |

### SDKs and client libraries

| Skill                                                       | Description                                                                                                                       |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [`sdk-portfolio-strategy`](./skills/sdk-portfolio-strategy) | Decides which languages get official SDKs and in what order, with build model, support tiers, versioning, and end-of-life policy. |

### Developer portal

| Skill                                                         | Description                                                                                                                                                    |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`developer-portal-design`](./skills/developer-portal-design) | Designs an external developer portal: information architecture, the signup-to-first-call path, self-service surface placement, search, RBAC, and build-vs-buy. |

### Status and incident communication

| Skill                                                                         | Description                                                                                                                                                    |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`api-status-communication`](./skills/api-status-communication)               | Designs how an API platform tells consumers what is happening: status-page modeling, incident cadence, public postmortems, and SLA reporting.                  |
| [`integration-error-observability`](./skills/integration-error-observability) | Designs how a platform surfaces integration failures to external developers: delivery logs, correlation IDs, error-rate aggregation, and notification posture. |

### Integration partnerships

| Skill                                                                           | Description                                                                                                                                                    |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`integration-listing-optimization`](./skills/integration-listing-optimization) | Optimizes a vendor's listing on a third-party app marketplace: funnel instrumentation, indexed keyword placement, media ordering, reviews, and badges.         |
| [`integration-partnership-strategy`](./skills/integration-partnership-strategy) | Decides which technology partners to integrate with and how deep each goes, using a demand-data scorecard, depth ladder, and pipeline attribution.             |
| [`partner-app-onboarding`](./skills/partner-app-onboarding)                     | Designs the partner-developer journey from signup to first submitted app: entry gate, sandbox provisioning, education, support ladder, and funnel checkpoints. |

### Connector marketplace

| Skill                                                                               | Description                                                                                                                                                    |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`app-marketplace-launch-marketing`](./skills/app-marketplace-launch-marketing)     | Designs a marketplace launch and ongoing app co-marketing program: founding cohort size, reveal coordination, featuring menu, and budget split.                |
| [`app-marketplace-listing-standards`](./skills/app-marketplace-listing-standards)   | Writes the listing-content rulebook an operator enforces on submissions: required fields, media geometry, quality bar, taxonomy, badges, and staleness policy. |
| [`app-marketplace-monetization-model`](./skills/app-marketplace-monetization-model) | Designs how a marketplace earns on the operator side: merchant-of-record posture, billing rails, fee stack, waiver programs, payouts, and tax split.           |
| [`app-marketplace-review`](./skills/app-marketplace-review)                         | Designs the operator-side review and approval process for third-party apps: pipeline shape, permission audits, re-review triggers, and the enforcement ladder. |
| [`connector-marketplace-strategy`](./skills/connector-marketplace-strategy)         | Decides whether to build a connector marketplace, join others', or buy embedded iPaaS, then designs governance, curation, take rate, and seeding.              |

## 👤 Contributors

![Contributors](https://contrib.rocks/image?repo=samber/developer-platform-skills)

## 💫 Show your support

Give a ⭐️ if this project helped you!

[![GitHub Sponsors](https://img.shields.io/github/sponsors/samber?style=for-the-badge)](https://github.com/sponsors/samber)

## 📝 License

Copyright © 2026 [Samuel Berthe](https://github.com/samber).

This project is under [MIT](./LICENSE) license.
