# Orrery Labs developer portal: gaps and placement

I read the skill and its three references. The skill wants one interview question at a time and section-by-section sign-off. You asked for the full answer in one go, so I made assumptions and listed them at the end for you to confirm or overrule.

## 1. Where you stand

- **You have a docs site and a dashboard on two subdomains, not a portal.** The skill's dividing line is self-service credentials. I assume the key dashboard already lets developers create, rotate and revoke keys without a ticket. If it doesn't, that is Priority 1.
- **The largest gap is the support workflow.** "Why did my send fail?" currently means an email and someone grepping logs. Integration logs need a first-class home in the portal. The skill lists this as a placement item, and its content belongs to `integration-error-observability`.
- **Your four items are the right core, but two are not yours to design here.** Quickstart content belongs to `developer-quickstart-guide`, and sandbox content belongs to `api-test-mode-design`. The portal decides where they sit and how a developer reaches them.
- **Decision-making content isn't on your list.** Pricing, use cases and comparisons need to be visible before login. The skill calls hiding them a sales-enablement failure.

## 2. What's missing

| # | Missing | Why it matters | Content owner |
|---|---|---|---|
| 1 | **Request logs and delivery status** (per-message events, search by ID/recipient/status) | Replaces the grep-via-support loop | `integration-error-observability` |
| 2 | **Error catalog** (public pages that `documentation_url` points at) | Failure explanations a developer can reach without support | `api-error-design` |
| 3 | **Usage and quota visibility** | Needs a deliberate home | Portal |
| 4 | **Billing and plan management** | Same | Portal |
| 5 | **Changelog and release notes** | Trust signal | Portal |
| 6 | **Status page link** | Trust signal | `api-status-communication` |
| 7 | **Support escalation path** | Should come after logs, search and the error catalog | Portal |
| 8 | **Pre-login evaluator layer:** landing page, product summary, use-case/solution pages, pricing | Business evaluators decide here | Portal |
| 9 | **Search plus an "Ask AI" assistant** | Expected component now; also feeds the docs backlog | Portal |
| 10 | **Team and tenancy:** Organization → Project, roles, test/live scoping | Keys, logs and usage scope to the project | Portal |
| 11 | **Try-it console** on each endpoint page, with the signed-in key injected | Removes the copy-key-between-sites step | `api-reference-quality` |
| 12 | **Agent readability** (clean markdown, `llms.txt`) | A third visitor class reads the portal for a human | Portal |

Items I added from email-API knowledge, not from the skill. Check them against your product:

- **Sending-domain verification** (SPF, DKIM, DMARC). This is probably your biggest TTFC stall. DNS propagation can't be made fast, so the sandbox must not depend on it.
- **Webhook documentation, testing and delivery log.** Bounce and complaint events are how senders learn about failures.
- **Suppression list and bounce/complaint view.**
- **SDKs and libraries index.**
- **Templates**, if you offer them.

## 3. IA candidates

1. **Single portal layered by depth. Recommended.** One host. The top layer is public marketing-rich pages, the solution layer is use cases, and the bottom layer is minimal technical pages plus the console. It fits one audience mix and one API backend, and it matches your "one place" goal.
2. **Split public and partner portals.** Only worth it if partners need approval-gated signup or SSO that the public tier shouldn't see. Revisit it if you have contracted partners.
3. **Docs-first minimal portal with embedded credentials.** This is the quickest route, since it keeps the current docs and drops the key dashboard into a nav shell. It is the likely first milestone of option 1, but on its own it leaves the evaluator layer empty.

## 4. Navigation tree

Layers: **Top** (marketing-rich), **Solution** (business problem → API), **Bottom** (minimal technical). Audiences: **E** evaluator, **I** integrating engineer.

```
/ (portal home)                                Top      E+I
├─ Products / What you can send                Top      E
│   └─ Use cases (onboarding mail, receipts,
│      password resets, alerts…)               Solution E  ← first-class layer
├─ Pricing and plans                           Top      E   (public, no login)
├─ Get started                                 Bottom   I
│   ├─ Quickstart (sandbox, one send)          Bottom   I
│   ├─ Verify your sending domain              Bottom   I   (email-specific)
│   └─ Go-live checklist                       Bottom   I
├─ Docs
│   ├─ Guides (webhooks, templates, suppression)  Bottom I
│   ├─ API reference + try-it console          Bottom   I   (generated from spec)
│   ├─ Errors catalog                          Bottom   I
│   ├─ SDKs and libraries                      Bottom   I
│   └─ Search + Ask AI (global, header)        —        E+I
├─ Console (login required)                    Bottom   I
│   ├─ Test/Live toggle (always visible)
│   ├─ API keys
│   ├─ Logs and delivery status                ← replaces support greps
│   ├─ Webhooks
│   ├─ Domains / suppression
│   ├─ Usage and quota
│   ├─ Billing and plan
│   └─ Team and projects (roles)
└─ Trust and help
    ├─ Changelog / release notes
    ├─ Status page (link)
    └─ Support (after logs and search)
```

Placement rules:

- Keep docs, pricing and the catalog public. Only the Console needs login.
- Keep the portal separate from the marketing site, linked both ways.
- Don't fold portal content into the marketing IA.
- 301-redirect both old subdomains so existing links and SEO survive.

## 5. Onboarding and TTFC

**Target: median under 15 minutes from landing to the first successful sandbox send.**

- The skill's guidance is under 15 minutes for a simple REST API with token auth.
- Track **first real delivered email** as a separate second milestone, since domain verification adds DNS wait time.

**Path:** landing → signup → verification → sandbox key → quickstart → first call.

**Friction order** (the skill's default, adjusted for you):

1. **Ungated exploration.** Docs, pricing and the reference readable with no signup. This is mostly a policy flip.
2. **Ready-to-run collection.** A forkable set of working send calls, such as a Postman collection.
3. **Auto-provisioned sandbox key injected into every snippet.** I would promote this one. Your docs and key dashboard live on different subdomains, so a developer has to switch sites, copy a key and come back. That is a likely stall point, and it disappears on one domain. Confirm it with the funnel data.
4. **Personalized onboarding.** Demote it. It is high effort, and you have a deadline and a likely single dominant use case.

**Instrument in increments:** landing → signup, then signup → first sandbox call, then first call → first delivered email. Let the data outrank this ordering.

## 6. Placement of each surface

| Surface | Portal decides | Content owner |
|---|---|---|
| Key dashboard | Console, first item, self-service lifecycle UX | `api-auth-key-management` |
| Logs/delivery status | Console, top-level, linked from every error | `integration-error-observability` |
| Sandbox | Default mode on signup, visible Test/Live toggle | `api-test-mode-design` |
| Reference | Generated from the spec, try-it on each endpoint page | `api-reference-quality` |
| Quickstart | Prominent "Get started" entry, TTFC measured around it | `developer-quickstart-guide` |
| Error catalog | Hosted under Docs, linked from log entries | `api-error-design` |
| Status | Link in the global footer or header | `api-status-communication` |
| Docs structure | Plugs into the portal container | `developer-docs-structure-audit` |

## 7. Search and Ask AI

- Put full-text or semantic search over the whole portal, with an Ask AI widget next to it.
- Every answer must cite a linkable source.
- The assistant must say "I don't know" when the docs don't cover the question.
- Send unanswered questions to the docs backlog.
- Treat any deflection claim as directional. Vendors report 20-40%, and you should measure against your own ticket baseline.
- The logs surface should come before Ask AI in sequencing. Failed-send questions can't be answered from docs alone.

## 8. Roles and tenancy

- Use Organization → Project, with keys, logs, usage and environments scoped to the project.
- Bundle permissions into roles, Owner/Admin/Member/Viewer style.
- Separate at minimum who manages keys, who sees billing and usage, and who invites teammates.
- Test vs Live is a first-class concept on every key and log screen.
- Add partner-style features (approval-gated signup, SSO/SCIM) only if you have a partner audience.

## 9. Build vs buy

- **Default: managed platform.** Mildly adjust that for two quarters.
- **Likely pick for you: assembled stack.** Compose a hosted docs/developer-hub product with the existing dashboard under one navigation and one host. Rebuilding the dashboard inside two quarters is not necessary.
- **Custom build** only if you hit one of the three promotion conditions: compliance/data-residency, a real CMS need for business authors, or a multi-gateway portfolio. Never without a named, ongoing owner.
- **Exclude** internal-portal frameworks. Their security model assumes no untrusted external users.
- **Watch the logs surface.** Credential-lifecycle and log depth varies across hosted platforms. It is the criterion most likely to push you off a pure docs product, so test it before choosing.

## 10. Two-quarter roadmap

**Priority 1: Q1**

- Name a **portal owner** with a backlog. The skill treats an unowned portal as one that decays.
- Stand up the **single host**, shared nav and auth, and 301s from both old subdomains.
- Ship **logs and delivery status MVP** (search by message ID/recipient, status, error with catalog link). This is the support-load win.
- Publish the **error catalog**.
- Make docs and pricing **public with no signup**.
- Set **sandbox key at signup**, injected into snippets.
- **Instrument TTFC**.

**Priority 2: Q2**

- Evaluator/solution layer: use-case pages, product summary.
- Search plus Ask AI.
- Usage/quota and billing in the Console.
- Changelog and status link.
- Team/project roles.
- Webhook testing and logs.
- Try-it console on endpoint pages.

**Priority 3: after Q2**

- SSO/SCIM and partner features, if relevant.
- Personalized onboarding, if the funnel shows no single quickstart serves everyone.
- Agent-readability polish.

**Maturity gate:** re-run the six-area diagnostic (Discovery, Decision-making, Onboarding, Go-live, Maintenance & troubleshooting, Community) after the redesign. Close every Priority 1 gap before calling it done.

## 11. Failure modes to avoid

- Pricing and use cases behind login.
- No owner.
- Missing solution layer.
- Mandatory signup before exploration.
- Marketing chrome on technical pages.
- A hand-maintained reference that drifts from the spec.
- An Ask AI that answers without citations.
- Key lifecycle actions that need a ticket.
- Treating TTFC as the only metric. Watch activation and retention as trends, not gates.

## 12. Assumptions I made, which you should confirm

1. Developers can already create, rotate and revoke keys without a ticket.
2. Your audience is mostly integrating engineers plus some evaluators, with no contracted partners.
3. Your API is token-auth REST, so the 15-minute class applies.
4. No compliance or data-residency requirement rules out a managed platform.
5. You have no named owner yet.
6. You have a hard deadline of two quarters.

If any of these is wrong, the build-vs-buy pick, the TTFC target or the Priority 1 list changes. Before writing the final design doc, I would validate the navigation tree section by section with you, as the skill's approval gate requires.