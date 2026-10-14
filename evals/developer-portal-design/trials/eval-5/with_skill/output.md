# Halcyon Payroll: API developer site, build or buy

## Recommendation

**Buy the credentials and docs layer, and own the front door. Don't build the portal.** Use an assembled stack with the gateway or a hosted docs platform as its core:

- **Gateway-bundled portal or hosted docs platform:** keys, reference, try-it console, usage and logs.
- **Your existing CMS:** the marketing layer, which means integration guides and customer stories, published by content marketing.
- **One shared design-token set:** applied to both, with one navigation across them.

This is not a custom build. A custom build is the one option that fails on your two constraints and one of your assets:

- **10 weeks and two contractors.** The skill says never to promote a custom build without a named, ongoing owner. Contractors leave at week 10, and an unowned portal decays rapidly.
- **One gateway across all four products.** This is the strongest signal for buying. The skill says an org standardized on one gateway gets that gateway's bundled portal nearly free. The multi-gateway condition that would promote a custom build is not met.

## Build-vs-buy scoring

The skill's default ranking is: efficiency `managed platform > assembled stack > custom build`, and value `custom build > assembled stack > managed platform`. I re-ranked it against your answers.

| Promotion condition for a custom build | Your situation | Met? |
|---|---|---|
| Compliance or data residency no managed platform meets | Not stated. A payroll vendor may have hosting requirements. | ❓ See open question 1. |
| Business authors need a real CMS beside spec-driven docs | Yes. Content marketing lives in your CMS. | ✅ |
| Multi-gateway portfolio no vendor portal unifies | No. One gateway serves all four products. | ❌ |
| Named, ongoing owner | None named yet. | ❌ |

One condition is met, and that is not enough to promote a custom build. The CMS need is served by the assembled stack, which keeps the CMS for marketing content only. Technical docs stay generated from the spec in CI, so they never live in the CMS.

Backstage-class frameworks are ruled out. They are internal-portal frameworks and unsafe as an external foundation.

## Resolving the pixel-control demand

The skill's own IA gives a way through. Visual richness should decrease with depth:

- **Top layer** (landing, product summaries, use cases, pricing signals). Brand matters most here, and design can own every pixel. Build it in your CMS or a custom front end.
- **Solution layer** (integration guides, customer stories, "payroll sync for X" pages). Marketing authors it in the CMS, in design's templates.
- **Bottom layer** (reference, guides, console, key dashboard). This should be clean and minimal, so a themed standard component is correct here. Marketing chrome on technical pages is friction.

So design controls the pixels where pixels matter. The bottom layer gets a themed product, not a templated-looking one.

**Hard selection criterion for design:** only shortlist platforms that allow all of these:

- design-token theming
- custom CSS and components
- custom domain
- ideally a headless or API mode

Reject any platform that locks the shell. Do a one-day theming spike per finalist before you commit.

The cost of full pixel control over the entire surface is real. It means a funded platform team and permanent ownership, which you don't have. If design still insists after seeing the layered split, that is a decision for your leadership, not a technical one.

## Content marketing without engineering tickets

- **Guides and customer stories:** authored in your CMS, published under the portal domain. Use path-level routing or a reverse proxy, such as `/integrations` and `/customers`. Both link to and from the portal navigation.
- **Technical reference and quickstarts:** generated from the OpenAPI spec through CI. Engineers own these, never the CMS.
- **Operational check:** each authoring persona needs a working workflow. Engineers push specs via CI, and marketing publishes via the CMS. That is the Pronovix Operational Excellence test.
- 🟠 Do not move technical docs into the CMS. A hand-maintained copy drifts from the spec.

## Proposed IA (needs your approval before it is final)

Single portal, layered by depth, with the four products as sections of one catalog.

| Node | Contents | Audience | Layer |
|---|---|---|---|
| Home | Value proposition, product cards, "Get a sandbox key" CTA | Both | Top |
| Products (×4) | Summary, pricing signals, endpoints overview | Evaluators | Top |
| Solutions | Use cases linking business problems to APIs, plus integration guides and customer stories | Both | Solution |
| Docs | Quickstart, guides, API reference with try-it, error catalog, changelog | Engineers | Bottom |
| Console | Keys, sandbox/live toggle, request logs, usage, team | Engineers | Bottom |
| Support and trust | Status link, release notes, escalation path | Both | Cross-cutting |

- Pricing, use cases and comparisons stay readable without login. Hiding them is the most common portal failure.
- Docs, pricing and the catalog are open with no signup.
- One catalog across four products is easy because there is one gateway.

## Onboarding and TTFC

- **Target:** a median TTFC under 60 minutes at launch, tightened to 30 after the baseline. I'm assuming OAuth plus webhooks, which puts a payroll API in the complex class. Confirm this (open question 5).
- **Path:** signup, verification, sandbox key, quickstart, first call.
- **Rung 1:** ungated exploration. This is a policy flip and costs almost nothing.
- **Rung 2:** a ready-to-run Postman collection per product.
- **Rung 3, if the funnel shows a stall between signup and first call:** auto-provisioned sandbox key injected into quickstart snippets. Promote it if auth is where people stall, which is common.
- **Rung 4:** personalized onboarding. Four products with different roles could justify it, but a hard 10-week deadline demotes it. Defer.
- **Payroll-specific rule:** the sandbox must use synthetic employee data only. Never expose real PII in test mode.

## Tenancy

- Organization, then Project, with keys, usage and environments scoped to the project.
- Roles: Owner, Admin, Member, Viewer. Separate who manages credentials, who sees billing and usage, and who invites teammates.
- Test and live are first-class on every key and log surface.
- Scope keys per product. Add SSO/SCIM only if partners or enterprise customers are in scope.

## 10-week plan (two contractors)

| Weeks | Work |
|---|---|
| 1 | Name the owner, pick the platform finalists, run theming spikes, get IA sign-off, audit the spec |
| 2–3 | Stand up the platform on the gateway, publish the generated reference, set up the TTFC instrumentation |
| 3–5 | Apply design tokens, build the top-layer templates, set up CMS-to-portal routing |
| 5–7 | Quickstart, Postman collections, key dashboard, sandbox, logs and status entry points |
| 7–8 | Content marketing publishes the first guides and stories, to prove the no-ticket workflow |
| 9 | Test the funnel with real integrators and fix the stall points |
| 10 | Launch, handover to the owner, runbook |

Search and the AI assistant are not on the critical path. Buy a widget after launch, with citations and an "I don't know" fallback. Measure deflection against your own ticket baseline, because vendor figures of 20–40% are directional only.

## Maturity roadmap

- **Priority 1 (before launch):** a named owner, self-service key lifecycle, ungated pricing and docs, spec-generated reference, a working quickstart, TTFC instrumentation.
- **Priority 2 (next 1–2 quarters):** solution-layer depth, changelog and trust signals, usage and quota visibility, the AI assistant.
- **Priority 3:** community, partner-portal features, personalized onboarding.

## Gates and metrics

- **TTFC gate:** instrument landing to signup and signup to first call. Iterate until the median meets the target.
- **Maturity gate:** re-run the benchmark after launch and close every Priority 1 gap.
- **Watch, don't gate:** ticket deflection, activation and retention.

## Open questions (they could change the answer)

1. **Compliance or data residency:** any hosting requirement a managed platform can't meet? This is the main condition that would promote a custom build.
2. **Greenfield or existing:** is there a docs site today, and can developers create and rotate keys without a ticket?
3. **Audience:** integrating engineers, business evaluators, or both? Public developers, contracted partners, or both?
4. **Gateway:** which one is it? That decides whether its bundled portal is enough.
5. **API complexity:** is auth OAuth plus webhooks, or simple token auth?
6. **Owner:** who owns this after week 10, with what hours?
7. **Deadline:** is the 10 weeks hard, and is the portal one-off or a compounding asset?

## Risks

- ⚠️ Design rejects the layered split and wants full custom control. That reopens the build decision and needs a funded permanent team.
- ⚠️ No owner after week 10. Without one, any option decays.
- ⚠️ Third-party pricing for these platforms is mostly from competing vendors. Re-verify all contract numbers with the vendor.
- ⚠️ I didn't interview you one question at a time, as the skill prescribes. I worked from your stated facts and flagged assumptions. The IA still needs your section-by-section approval.