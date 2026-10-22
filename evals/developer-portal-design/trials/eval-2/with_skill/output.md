# Partner developer portal: recommendation, architecture, navigation

## Verdict: don't open Backstage to partners

Build a separate external partner portal. Keep Backstage internal, and feed the new portal from it one way.

- **Threat model.** Backstage and similar internal-portal frameworks assume untrusted external actors have no access. An auth layer in front doesn't change what sits behind it: the whole catalog, ownership data, service topology, and every installed plugin's endpoints.
- **Community guidance.** The consensus is not to build an external portal on an internal framework.
- **Missing portal functions.** What makes a portal a portal is self-service credentials: partners create, rotate, and revoke keys without a ticket. Add logs, usage, a sandbox toggle, and a try-it console with injected keys. You would build all of that as custom plugins, on a base that was never meant to be exposed.
- **Your team's expertise still carries over.** The platform team's Backstage knowledge applies to the spec pipeline (below), not to the portal itself.

⚠️ I couldn't run the skill's one-question-at-a-time interview or its section-by-section approval gate, so the assumptions below are mine. Treat this as a draft for your review, not a signed-off design.

## Assumptions to confirm

| # | Assumption | Changes if wrong |
|---|---|---|
| 1 | Partners are contracted, so signup is invite or approval-gated. Audience is mostly integrating engineers, plus some business and ops staff. | A public audience too would mean a second portal off the same API backend. |
| 2 | Only a handful of the 90 services are partner-facing. | A large partner API surface raises the cost of the spec pipeline. |
| 3 | There is an API gateway, and key issuance can be driven from it or from an auth service. | No gateway pushes you toward an assembled stack. |
| 4 | No residency or regulatory rule rules out a managed platform. | A compliance blocker is the main condition that promotes a custom build. |
| 5 | Auth is simple token or key auth. | OAuth plus webhooks moves the TTFC target from 15 minutes to under an hour. |
| 6 | Deadline and effort ceiling are unknown. | A hard deadline pushes harder toward buying. |

## IA options considered

| Option | Trade-off | Verdict |
|---|---|---|
| **A. One partner portal, layered by depth** | One backend and one auth model. 40 partners don't justify more. | ✅ Recommended |
| B. Split public and partner portals | Right only if you also want a public developer audience. Two auth models. | Defer |
| C. Docs-first minimal portal with embedded credentials | Fastest. Weak on the solution layer and on evaluators. | Fallback if the deadline is brutal |

## Build vs buy

Default to a **managed platform**: a gateway-bundled portal or a hosted developer hub. At 40 partners, owning a custom portal is hard to justify. Re-rank on two conditions:

- If you already run one gateway, its bundled portal is nearly free.
- Only compliance or residency limits, business authors who need a CMS, or a multi-gateway estate promote a custom build. A custom build also needs a named, funded, permanent owner.

Backstage is ruled out as the foundation. It isn't demoted, it's excluded.

## Architecture: components, not Backstage plugins

```
INTERNAL (unchanged)                         EXTERNAL (new)
┌────────────────────┐   CI publish job     ┌──────────────────────────────┐
│ Backstage catalog  │  (one-way, no        │ Partner portal platform      │
│ ~90 services      ─┼─ network path back)─▶│ (managed / gateway-bundled)  │
│ API entities +     │  OpenAPI specs +     │  ├ Docs + generated reference│
│ "partner-facing"   │  changelog entries   │  ├ Try-it console            │
│ annotation         │                      │  ├ Search + Ask AI           │
└────────────────────┘                      │  └ Console (post-login)      │
                                            └──────────┬───────────────────┘
                                                       │
                      Partner IdP/SSO ─▶ Org → Project │
                                                       ▼
                                      API gateway / auth service
                                      (keys, quotas, logs, usage)
```

**1. Spec pipeline: the only link to Backstage.**
- Tag partner-facing API entities in the catalog with an annotation.
- A CI job exports only those specs and changelog entries to the portal's docs source.
- The portal never calls Backstage, and there is no network path from the portal back into it.
- The reference is generated from the spec, never hand-copied, so it can't drift.
- Review the annotated list with the platform team before first publish. A wrongly tagged service becomes publicly documented.

**2. Identity and tenancy.**
- Invites are seeded from your contract list, so "approval-gated" doesn't add waiting time to TTFC.
- The hierarchy is Organization (partner company) → Project (an integration). Keys, usage, and environments scope to the project.
- Roles:
  - Owner.
  - Developer (manages credentials).
  - Billing/Viewer.
  - A separate right to invite teammates.
- Add SSO/SCIM only if partners ask for it.
- Add page-level visibility so some APIs are visible only to partners under contract for them.

**3. Self-service surfaces.** This skill places each surface. Sibling skills own the content.

| Surface | Placement | Content owner |
|---|---|---|
| API keys | Console → Applications & Keys | `api-auth-key-management` |
| Sandbox / test-live toggle | Persistent in the console header | `api-test-mode-design` |
| Request logs and delivery status | Console → Logs | `integration-error-observability` |
| API reference + try-it | Endpoint page, console targets the sandbox by default | `api-reference-quality` |
| Error catalog | Reference section; `documentation_url` points here | `api-error-design` |
| Status | Header and footer link | `api-status-communication` |
| Quickstart | Linked from Home and from the empty console state | `developer-quickstart-guide` |
| Docs internals | Plugged into the portal container | `developer-docs-structure-audit` |
| Usage and quota | Console → Usage, with overage alerts | This design |
| Billing/plan | Console, only if usage-based; skip if contracts are flat | This design |
| Changelog | Top-level nav, fed by the pipeline | This design |
| Support escalation | Header, plus a contextual link from error and log pages | This design |

**4. Key lifecycle UX.**
- Scope keys at creation.
- Show test and live as a pair.
- Support rotation with an overlap window.
- Choose expiry at creation.
- Show last-used timestamps.
- No lifecycle action may require a ticket.

**5. Search and Ask AI.**
- Index portal content only. Never index Backstage.
- Every answer cites a linkable source.
- The assistant says "I don't know" instead of guessing.
- Unanswered and low-confidence questions feed the docs backlog.
- Measure ticket deflection against your own pre-assistant baseline. Vendor figures of 20–40% are directional only.

## Partner-facing navigation

Layers: **Top** is marketing-rich, **Solution** connects business problems to APIs, **Bottom** is minimal technical pages. Audience: **E** is the business evaluator, **I** is the integrating engineer.

```
Header: Logo | Solutions | APIs | Guides | Changelog | Status | Support | [Search + Ask AI] | Sign in / Console

Home                                  Top      E, I
 ├─ Value props, "first call in N minutes" CTA, status badge, latest changelog

Solutions                             Solution E, I   ← treat as first-class; most portals fail here
 ├─ By use case (e.g. order sync, event ingestion) → which APIs, flow diagram
 └─ Partner onboarding overview (contract → keys → go-live)

APIs                                  Top → Bottom
 ├─ Catalog (filter by product, visible per partner entitlement)
 └─ <API> product page                Top      E, I
     ├─ Overview, auth model, limits, versioning
     ├─ Reference (generated from spec + try-it)   Bottom  I
     └─ Webhooks / events (if any)                 Bottom  I

Guides                                Bottom   I
 ├─ Quickstart (zero → first call)
 ├─ Authentication
 ├─ Sandbox and going live
 ├─ Error catalog and troubleshooting
 └─ SDKs and Postman collection

Changelog and deprecations            Bottom   I   (+ last-updated timestamps)
Status                                link out
Support                               escalation path, contact, SLA

Console (signed in)                   Bottom   I, ops
 ├─ Overview: setup checklist, TTFC progress
 ├─ Applications & Keys   (test/live pair, rotate, revoke)
 ├─ Logs                  (per-request, filter by key/env/status)
 ├─ Usage and Quotas
 ├─ Webhooks
 ├─ Team and Roles
 └─ Organization settings (SSO if enabled)

Footer: Terms/contract, Security, Changelog RSS
```

Technical pages carry no marketing chrome. Visual richness drops with each step deeper.

**Open decision: ungated or partner-gated docs?**
- Ungated exploration is the default and removes a top friction point.
- Gate only if your contracts make the API surface itself confidential.
- Keep Solutions and Home readable pre-login either way.
- If you gate, say so before the TTFC target is set.

## Onboarding path and TTFC

- **Target:** under 15 minutes for simple token auth, under an hour for OAuth plus webhooks. Pick one by confirming assumption 5, and write the rationale into the design doc.
- **Path:** invite → verify → auto-provisioned sandbox key → quickstart with the key injected → first call.
- **Rung order:**
  1. Ungated exploration (if you choose it).
  2. Ready-to-run Postman collection.
  3. Auto-provisioned sandbox key with injected credentials. Promote it first if the funnel shows partners stalling between signup and first call.
  4. Personalized onboarding. Skip it; at 40 partners, a partner manager does this better.
- **Instrument two increments:** landing → signup, and signup → first call.

## Roadmap

| Priority | Item |
|---|---|
| **P1** | Named product owner and backlog for the portal |
| **P1** | Spec pipeline from the catalog, with the annotation review |
| **P1** | Self-service key lifecycle with test and live modes |
| **P1** | Quickstart, TTFC instrumentation, and the sandbox |
| **P1** | Solutions pages and the nav above |
| **P2** | Logs, usage and quotas, changelog, status link |
| **P2** | Search plus Ask AI with citations |
| **P3** | SSO/SCIM, page-level entitlements, webhook lifecycle events |
| **P3** | Community channel for partners |

Re-score Pronovix's three dimensions after launch. Close every P1 gap before calling the work done.

## Failure modes to avoid

- Decision-making content gated behind login.
- A portal with no owner that decays.
- Solutions layer missing, so endpoints appear with no business context.
- Any key action that needs a ticket.
- Judging success by TTFC alone. Also watch activation and retention.

## What I need from you

1. Which gateway or auth service issues partner keys today?
2. Any compliance or residency limits?
3. Auth style: simple key, or OAuth plus webhooks?
4. How many of the 90 services are partner-facing?
5. Deadline and effort ceiling, and who will own the portal.
6. Docs ungated or partner-gated?

Answers to 1, 2, and 5 are the ones most likely to change the build-vs-buy ranking.