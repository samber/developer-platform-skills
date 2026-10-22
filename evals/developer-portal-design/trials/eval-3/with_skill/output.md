# Kestrel Freight developer section: page structure

I didn't run the skill's one-question-at-a-time interview or the section-by-section approval gate. You asked for the full deliverable in one response. The IA below is a proposal to validate, and the assumptions it rests on are at the end.

## Decision: one portal, layered by depth

| Option | Verdict |
|---|---|
| **A. One portal, layered by depth** (marketing-rich top, minimal technical bottom) | **Recommended.** It serves the three audiences below with one API backend, one auth model, and one owner. |
| B. Split public and partner portals | Not needed at launch. Revisit if system integrators (SIs) need approval-gated partner status. |
| C. Docs-first minimal portal with embedded keys | Fails the ops director, who compares you against two competitors before any engineer opens the docs. |

Host it separately from the marketing site (for example `developers.kestrelfreight.com`) and link the two both ways. Add "Developers" to the main site nav, and send marketing-site API pages to the Solutions layer.

## Audiences

1. **Ops director (evaluator).** Compares you with two competitors and has no code in mind. Needs use cases, pricing, limits, data freshness, reliability, and a plain-language answer to "what will integration cost us?". Leaves if any of this is behind a login.
2. **In-house developer.** Needs a working sandbox key and a first tracking call quickly, with no marketing chrome on technical pages.
3. **Outside systems integrator.** Needs a spec file they can scope from, a sandbox they can use before the client signs, and a way to work in the client's account without holding the client's billing or owner rights.

## Navigation tree

Layer key: **T** is the top layer (marketing-rich), **S** the solution layer, **B** the bottom layer (minimal chrome). Audience key: **E** evaluator, **D** developer, **I** integrator.

```
developers.kestrelfreight.com
│
├─ Home                                   [T · E D I]
│    One-line promise with a time ("track your first shipment in 15 minutes").
│    Two doors: "Evaluating Kestrel?" and "Ready to build?"
│    Status light, latest changelog entry, search + Ask AI.
│
├─ Solutions                              [S · E, D]   ← first-class layer
│    ├─ Proactive delay alerts to your customers
│    ├─ Embed tracking in your customer portal or app
│    ├─ Feed tracking into your TMS/WMS/ERP
│    └─ Exception handling and ETA workflows
│    Each page: the business problem, which endpoints/webhooks solve it,
│    an example payload, and the integration effort in plain terms.
│
├─ Platform overview                      [T · E]
│    ├─ What the API covers (shipment types, events, coverage)
│    ├─ Data freshness and latency, reliability and SLA
│    ├─ Security and compliance
│    └─ Push vs polling: how updates reach you
│
├─ Pricing & limits                       [T · E]   ← pre-login, always
│    Plans, rate limits, quotas, overage, sandbox vs live terms.
│
├─ Evaluate                               [S · E]
│    ├─ "What it takes to integrate" (effort, skills, typical timeline)
│    ├─ Evaluation checklist to hand to IT
│    └─ Try it without signup (read-only demo against sample shipments)
│
├─ For integrators                        [S · I]
│    ├─ Scoping guide and effort template
│    ├─ Working in a client's account (invite flow, roles)
│    ├─ Downloadable OpenAPI spec (stable URL)
│    └─ Integrator listing / contact (if a partner program exists)
│
├─ Docs                                   [B · D I]   ← no marketing chrome
│    ├─ Quickstart (zero to first tracking call)
│    ├─ Guides
│    │    ├─ Authentication and keys
│    │    ├─ Tracking shipments (lookup, status model, event types)
│    │    ├─ Webhooks (setup, signature check, retries)
│    │    ├─ Errors and troubleshooting
│    │    ├─ Testing in the sandbox
│    │    └─ Go-live checklist
│    ├─ API reference (generated from the spec, try-it console on each endpoint)
│    ├─ Error catalog (target of every `documentation_url`)
│    ├─ SDKs and Postman collection
│    └─ Changelog and deprecations
│
├─ Console (signed in)                    [B · D I, plus E as Viewer]
│    ├─ Overview (setup progress, first-call status)
│    ├─ API keys (create, scope, rotate, revoke; last-used)
│    ├─ Sandbox / Live toggle (visible on every page)
│    ├─ Logs (requests + webhook deliveries)
│    ├─ Usage and quota
│    ├─ Billing and plan
│    ├─ Team and roles
│    └─ Support
│
└─ Footer on every page: Status · Changelog · Support · Last updated · Main site
```

Search and an "Ask AI" widget sit in the header of every page.

## Onboarding path

**TTFC target: 15 minutes** from landing to the first successful tracking lookup in the sandbox. That fits a simple REST API with token auth. If you add OAuth, move the target to under an hour. Treat the first received webhook event as a second milestone, because tracking is useful only once updates are pushed.

Path: `Docs (no signup) → sign up → sandbox key → quickstart → first lookup → first webhook event`

Friction removal, in order:

1. **Ungated exploration (default).** Docs, reference, pricing, and Evaluate need no login.
2. **Postman collection and runnable snippets.** They are forkable, with sample tracking numbers.
3. **Auto-provisioned sandbox key, injected into quickstart snippets and try-it.** Promote this to step 1 priority if the funnel shows drop-off between signup and first call. Auth is the usual stall point.
4. **Personalized onboarding: not promoted.** The one exception is a single field at signup, "building for your own company or a client?". It drives the integrator role and invite flow, not the quickstart.

**Sandbox needs simulated shipments.** A developer integrating tracking has no real shipment IDs before go-live. Ship fixed test tracking numbers that replay a full lifecycle (in transit, delayed, exception, delivered) and fire real webhooks. Without these, TTFC will be slow no matter how good the docs are. Content belongs to `api-test-mode-design`.

Instrument two increments: landing → signup, and signup → first call.

## Placement of every surface

| Surface | Home | Notes |
|---|---|---|
| Keys | Console → API keys | Self-service create, scope, rotate (overlap window), revoke. No tickets. |
| Request logs and webhook deliveries | Console → Logs | First-class. Webhook failures are the top support driver for tracking APIs. |
| Sandbox | Console toggle + Quickstart step 1 | The toggle shows on every Console page, key row, and log row. |
| API reference | Docs → API reference | Generated from the spec, never hand-maintained. Replaces the PDF. |
| Status | Footer and Home | Trust signal. |
| Error catalog | Docs → Error catalog | |
| Quickstart | Docs, one click from Home | |
| Usage and quota | Console → Usage | Alerts before limits are hit. |
| Billing | Console → Billing | Visible to Owner and Billing roles only. |
| Changelog | Docs and footer | Include deprecation dates. |
| Support | Console and footer | Escalation path with expected response times. |

## Search and AI assistant

- Search covers all of Home, Solutions, Docs, and the error catalog.
- Ask AI sits beside search and gives answers grounded in the portal, each with a source link.
- It says "I don't know" instead of guessing. Unanswered questions go to the docs backlog.
- Measure ticket deflection against your own baseline before claiming a number.

## Roles and tenancy

- Hierarchy: **Organization → Project**. Keys, usage, and environments scope to the project.
- Roles: **Owner**, **Admin**, **Developer**, **Viewer**, plus **Billing** (or fold it into Owner).
- Ops director: Owner or Viewer. They see usage and logs without touching keys.
- Integrator: invited as Developer into the client's org. They get no billing access, and their access can be revoked cleanly at project end.
- Test and live are separate credentials, visible on every surface.

## Build vs buy

**Default: buy a managed developer-hub platform**, composed with your gateway's credential management if the hub's key lifecycle is shallow. It's the efficient path for a Q3 launch. Two conditions would promote a custom build:

- Compliance or data-residency requirements that no managed platform meets.
- Business authors who need a real CMS for the Solutions and Evaluate pages. Check this early, because those pages hold the content your buyers read first.

A custom build also needs a funded, named owner. Whichever route you take, **name the portal owner now**. An unowned portal decays.

## Roadmap

Priorities use Pronovix's six focus areas.

| Priority | Item | Focus area |
|---|---|---|
| **P1: launch gate** | Ungated Platform overview, Pricing & limits, and 3-4 Solutions pages | Discovery, Decision-making |
| | Downloadable OpenAPI spec, plus generated reference with try-it | Onboarding |
| | Sandbox with simulated shipments, plus Quickstart | Onboarding |
| | Self-service keys, sandbox/live toggle, Logs | Onboarding, Troubleshooting |
| | Webhook guide, error catalog, go-live checklist | Go-live |
| | Status, changelog, last-updated stamps, named owner | Maintenance |
| **P2: first quarter after launch** | Evaluate and For integrators pages, client invite flow | Decision-making, Go-live |
| | Ask AI assistant with citations | Discovery, Troubleshooting |
| | Postman collection and SDKs | Onboarding |
| | Usage alerts, role refinement | Maintenance |
| **P3** | Integrator directory, community or office hours | Community |

**Gates:** median TTFC meets the 15-minute target, and every P1 gap is closed before you call the work done. Watch ticket deflection and integration activation and retention as trends only. A fast first call doesn't prove a retained integrator.

## Failure modes to avoid

- Pricing, limits, or use cases behind a login.
- Thin or missing Solutions pages.
- Marketing chrome on reference pages.
- A hand-maintained reference that drifts from the spec.
- Mandatory signup before docs.
- An AI assistant without citations.
- Key rotation that needs a support ticket.

## Assumptions to confirm

I'd have asked these in the interview. Each could change the design:

1. **Greenfield.** Today there is only the emailed PDF, so this is not a redesign.
2. **Pricing exists and can go public.** If not, Pricing & limits becomes "plans and limits at launch", and that decision is the first thing to unblock.
3. **Live access.** I assumed self-serve sandbox and self-serve live keys. If live keys need a signed contract, add an approval gate and say so on Pricing & limits.
4. **Gateway and compliance.** I don't know your API gateway or any data-residency requirements. Both re-rank build vs buy.
5. **One owner exists or can be named** before launch.
6. **Q3 date.** Today is 2026-10-08, so I assumed Q3 means a future quarter. The date sets how much of P2 can ship at launch.
7. **No separate partner program.** If SIs will be formal partners with approval, that triggers the split-portal option.

Next step: validate the tree above section by section (Home, Solutions, Docs, Console) before any build starts.