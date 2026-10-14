# Kestrel Freight developer section: page structure

## Design premise

Three audiences visit this section, in this order:

1. **Ops director.** They arrive before anyone technical does. They compare Kestrel with two competitors. They are asking "can my team or my integrator connect this to our TMS/WMS without a project that eats the quarter?" They won't read code. They will notice whether a real developer section exists, whether it is public, and whether it looks maintained.
2. **In-house dev or systems integrator (SI).** They receive a link from the director. They want to know if they can start in minutes and what the full scope looks like. The SI is also quoting the build, so they need scope facts: endpoints, auth, limits, webhooks, sandbox.
3. **Both, again.** The director comes back to check reliability, support and cost before signing.

Every page therefore has two layers. The top layer is plain language that the director can forward. The layer underneath is technical detail for the builder.

The PDF-by-email model fails on both counts. It gates the evidence the director needs for the comparison, and it goes stale. The section replaces it with public, versioned, linkable pages. Make everything public with no signup wall, apart from sandbox keys.

## Hierarchy

```
Developers (/developers)
├── Overview / "What you can build"        /developers
├── Use cases (by ops outcome)             /developers/use-cases
│   ├── Shipment status in your TMS        /developers/use-cases/shipment-visibility
│   ├── Automated ETA & delay alerts       /developers/use-cases/eta-and-delay-alerts
│   ├── Proof of delivery into ERP/billing /developers/use-cases/proof-of-delivery
│   ├── Customer-facing tracking page      /developers/use-cases/customer-tracking
│   └── (one page per validated use case)
├── For your integrator                    /developers/integration-partners
│   ├── Scoping checklist & effort guide   /developers/integration-partners/scoping
│   ├── Certified integrator directory     /developers/integration-partners/directory
│   └── Partner sandbox & support path     /developers/integration-partners/program
├── Quickstart                             /developers/quickstart
├── Guides                                 /developers/guides
│   ├── Authentication                     /developers/guides/authentication
│   ├── Tracking a shipment end to end     /developers/guides/track-a-shipment
│   ├── Webhooks & event handling          /developers/guides/webhooks
│   ├── Pagination, rate limits, retries   /developers/guides/limits-and-retries
│   ├── Error handling                     /developers/guides/errors
│   ├── Going to production checklist      /developers/guides/go-live
│   └── Migrating from the PDF spec        /developers/guides/migrating-from-pdf
├── API reference                          /developers/api
│   ├── Shipments                          /developers/api/shipments
│   ├── Tracking events                    /developers/api/tracking-events
│   ├── Webhooks                           /developers/api/webhooks
│   ├── (one page per resource)
│   ├── OpenAPI spec (download)            /developers/api/openapi.json
│   └── Postman collection (download)      /developers/api/postman
├── Sandbox & API keys                     /developers/sandbox
├── SDKs & tools                           /developers/sdks
├── Reliability & trust                    /developers/reliability
│   ├── Status page (live)                 status.kestrelfreight.com
│   ├── Uptime & latency history           /developers/reliability/history
│   ├── SLA & support tiers                /developers/reliability/support
│   └── Security & data handling           /developers/reliability/security
├── Changelog & versioning                 /developers/changelog
│   └── Deprecation policy                 /developers/changelog/deprecation-policy
├── Support                                /developers/support
└── Get access / Talk to us                /developers/access
```

## What each page does

| Page | Primary reader | Job | Must contain |
|---|---|---|---|
| **Overview** | Ops director first | Prove the API is real and usable. Route each audience. | A one-paragraph business promise. Three or four outcome cards linking to use cases. A "forward this to your team" block. Live status badge. Latest changelog entry (shows it's maintained). Two CTAs: "Start in sandbox" (dev) and "Talk to us about integration" (director). |
| **Use cases** | Director | Connect the API to ops outcomes. This is the comparison page. | Per page: the problem, what data flows where, which systems it typically connects to, rough effort ("typically X days for an integrator"), and a short code snippet. Include a plain-language "what you need from your side". |
| **For your integrator** | Director and SI | Cover the buyer who isn't building it themselves. | Scoping checklist: endpoints needed, auth model, webhook vs polling, test plan. An effort estimate by scenario. The directory of integrators who have built against Kestrel. How an SI gets a partner sandbox and escalation contact. |
| **Quickstart** | Dev | First successful call in under 10 minutes. | Get a sandbox key, make one request, see a shipment, receive one webhook. Copy-paste in curl plus two or three languages. Ends by linking to the guides. |
| **Guides** | Dev, SI | Task-based depth. | Authentication, end-to-end tracking, webhooks, limits, errors, go-live checklist. The migration guide covers current PDF-spec users. |
| **API reference** | Dev, SI | Complete, accurate, scannable. | Generated from OpenAPI so it never drifts. Per endpoint: request, response, error codes, examples. Downloadable OpenAPI and Postman collection. Interactive "try it" against the sandbox. |
| **Sandbox & keys** | Dev, SI | Remove the access barrier. | Self-serve sandbox key. Realistic test shipments, including delayed, exception and delivered states. Clear sandbox-vs-production differences. Production access request flow. |
| **SDKs & tools** | Dev | Reduce build effort. | Official libraries (state which languages and their maintenance status). Webhook testing tool. Link to OpenAPI so integrators can generate their own clients. |
| **Reliability & trust** | Director, SI | Settle risk during the comparison. | Live status page. Historical uptime and latency. SLA terms. Support hours and response times. Security overview and data handling. Commit to numbers only if you can honor them. |
| **Changelog & versioning** | Dev, SI | Prove stability. | Dated entries. Versioning scheme. Deprecation policy with a minimum notice period. Subscribe via email or RSS. |
| **Support** | All | Make it clear where help comes from. | Channels, hours, escalation path, and who answers (developer support vs account manager). |
| **Get access / Talk to us** | Director | Convert the non-technical buyer. | A short form for the ops director ("we want to integrate with X system"). It routes to a solutions contact, not the dev queue. |

## Navigation

**Developer section header (sticky sub-nav):** Overview · Use cases · Quickstart · Guides · API reference · Reliability · Changelog · **[Get sandbox key]**

- "For your integrator" and "Support" sit in the sub-nav overflow and in the footer. They are important but secondary.
- The main kestrelfreight.com nav gets one item, **Developers**, placed beside Solutions and Pricing so a director comparing vendors finds it without hunting.
- Breadcrumbs on every page. API reference and guides get a left sidebar tree plus on-page search.
- Search spans the whole section and is the main way builders navigate.

## Internal linking

- Overview links to every use case, the quickstart, reliability and the integrator page.
- Each use case links to its guides, the relevant API reference pages, and the sandbox.
- Each guide and API page links back to its use case, so a technical reader can see the business context.
- The integrator page links to scoping, the directory, the sandbox and reliability.
- The changelog, status badge and "last updated" dates appear site-wide in the developer section footer. They signal that it is maintained.
- Link from product and solutions pages on the main site into the matching use case pages. This is where the ops director is already reading.

## Build order

1. **Launch-critical (before Q3):** Overview, Quickstart, API reference (from OpenAPI), Sandbox, Authentication and Webhooks guides, Changelog, Support, Get access, Reliability (status page plus support/SLA).
2. **At launch if possible:** Use cases (two or three that match your real first customers), the integrator scoping page, the migration-from-PDF guide.
3. **After launch, driven by usage:** SDKs, integrator directory and partner program, additional use cases, uptime history.

## Open questions

These decide the details above, so answer them before design starts:

1. **Which two or three use cases are real?** Use case pages must reflect what customers actually do. If they are guesses, publish fewer.
2. **What can you promise on reliability?** The reliability page is only as strong as your SLA and uptime. Don't publish claims you can't back.
3. **Sandbox self-serve or gated?** Self-serve is recommended. If legal or abuse concerns require approval, keep the review fast and state the turnaround.
4. **Do you have integrators in the loop yet?** The directory and partner program need at least a few named references. Until then, ship the scoping page alone.
5. **Who owns the section after launch?** The changelog, status and docs only build trust if someone updates them. Name an owner.