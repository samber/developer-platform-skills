# Threadline marketplace strategy

## Recommendation

1. **Ship a Threadline Marketplace in Q2, but as a first-party integration catalog on top of a public API beta.** Don't ship an open third-party platform.
2. **Treat "open to outside builders" as a gated Phase 3**, opened only if demand signals appear. Today none exist.
3. **Fix the actual revenue leak first.** Six lost enterprise deals came from missing integrations, not from a lack of third-party developers.

The CEO's all-hands promise ("marketplace live by Q2") can still be met. The word "marketplace" stays. The scope is what changes.

## Why not an open marketplace in Q2

- **A marketplace needs two sides.** You have neither a supply side (no API, docs, sandbox or partner manager) nor any evidence of one (no outside builder has ever built on you or asked to).
- **Your pain is demand-side.** Buyers want specific integrations, such as Workday and certain ATSs. A third-party ecosystem would not deliver those on your timeline, and Workday-class integrations are rarely built by hobbyist partners.
- **Capacity doesn't fit.** 14 engineers, fully committed, means a platform build (API, auth, review, docs, support) would displace the core roadmap.
- **The economics are weak at this scale.** At $4.1M ARR and 320 customers, a marketplace won't produce direct revenue for years. Its value is win rate and retention.

## What "live in Q2" means

**Scope (the v1 contract with the CEO):**

- A public **Marketplace page** and an in-app **Integrations tab**.
- All 9 existing integrations listed, each with a setup guide.
- 3–5 new integrations, chosen by revenue at stake (see Phase 0).
- A **Zapier connector** (and Make, if cheap) to cover the long tail of requests.
- A **public API v1 (beta)** with docs, OAuth or API keys, webhooks and a sandbox tenant.
- A **"Build on Threadline" waitlist**, which doubles as the demand test for Phase 3.

**Explicitly out of Q2:**

- Open third-party submissions.
- Revenue share.
- Embedded app UI.
- A partner certification program.

## Phases

### Phase 0: Evidence (now to end of November, about 3 weeks)

1. Pull the six lost deals. For each, record the named integration, deal size, competitor that won, and whether a connector or iPaaS would have saved it.
2. Tag the last 12 months of support requests by integration and by customer ARR.
3. Rank integrations by revenue at stake and effort, then pick the 3–5 for Q2.
4. **Evaluate buy vs build** for the long tail:
   - Unified HRIS/ATS APIs.
   - Embedded iPaaS.
   - Zapier.
   One vendor contract may replace dozens of hand-built connectors. Price and coverage need verifying before you commit.
5. Check the prerequisites that could block enterprise buyers anyway: SOC 2 status, data-processing terms, and whether your multi-tenant architecture can safely expose an API.

### Phase 1: API foundation (December to February)

- Scope: employees, onboarding plans and tasks, templates and webhooks. Read-heavy at first, with writes only where integrations need them.
- Scoped OAuth. Employee PII is the sensitive part, so least-privilege scopes and audit logs are mandatory.
- Docs site, quickstart and sandbox tenant. Build these for your own integration team first, since they are the first users.
- Versioning and deprecation policy, written before launch. Once published, an API is a commitment.

### Phase 2: Marketplace v1 (March to Q2 launch)

- Listings with a consistent template: what syncs, setup time, permissions requested, support contact.
- Admin install flow with permission review and a connection health status.
- Launch the new integrations in a staggered way, so the marketplace has news every few weeks after launch.
- Sales enablement. Give sales a one-page integration matrix and a script for the "do you integrate with X?" objection.
- Re-engage the six lost accounts and any open deals that named a now-shipped integration.

### Phase 3: Partner pilot (H2, only if gates pass)

- Hand-recruit 3–5 design partners, such as ATS/HRIS vendors your customers already use, or implementation consultancies. Don't run an open call.
- Add a part-time partner owner and a lightweight listing review (security questionnaire, scope review, support SLA).
- Co-market each partner listing.

### Phase 4: Open platform (2027, optional)

Open self-serve submission only if Phase 3 shows repeatable partner-led value.

## Gates to advance

| Gate | Evidence required |
|---|---|
| Phase 1 to 2 | API beta used internally by ≥2 shipped integrations; security review passed |
| Phase 2 to 3 | ≥10 unprompted waitlist or inbound requests from outside builders or vendors; ≥3 named design partners willing to commit engineering time |
| Phase 3 to 4 | ≥2 partner integrations live with measurable customer adoption; support load per listing sustainable |

**Kill or pause rule:** if the Phase 3 gate isn't met by end of Q3, keep the catalog as a first-party integration hub and stop investing in the platform.

## Metrics

**Primary (business outcome):**

- Win rate in deals where an integration was required (baseline: the six losses).
- Pipeline and ARR influenced by integration availability.
- Retention and expansion of customers with ≥1 active integration vs those with none.

**Secondary (health):**

- % of customers with ≥1 integration connected.
- Integration request backlog, and time from request to ship.
- API: active keys, calls, error rate.
- Support tickets per integration.

**Don't report:** raw listing counts or "partners signed" as success. At your stage they're vanity metrics.

## Pricing and packaging

- No revenue share or listing fees.
- Gate premium or enterprise-grade integrations (Workday-class) to higher tiers, or include them as a differentiator in enterprise contracts. Decide in Phase 0 once you see the lost-deal tier.
- API access: free for paying customers in beta, with rate limits. Revisit at GA.

## Resourcing

Honest trade-off: this needs roughly **2–3 of 14 engineers** for two quarters, plus:

- A part-time technical writer or contractor for docs.
- A designer for part of the time.
- A PM owner, which could be you or a delegate.
- Security review time.

Buying the long tail from a vendor (Phase 0 step 4) is the main lever to cut engineering. Leadership must decide which core roadmap items slip, and say so now. Otherwise Q2 slips silently.

## Risks

| Risk | Mitigation |
|---|---|
| Scope creep into a full platform | Written v1 contract (above), signed off by CEO |
| Security and PII exposure | Scoped OAuth, audit logs, security review before beta, no third-party code in Q2 |
| API becomes a permanent commitment | Version it, label it beta, publish a deprecation policy |
| Support burden from each integration | Health monitoring, setup docs, and one owner per integration |
| Core roadmap starvation | Fixed capacity allocation; weekly check against the Phase gates |
| Expectation gap from the all-hands | Reframe now (below), before Q2 |
| Marketplace launches but doesn't win deals | Phase 0 attribution baseline, so the effect is measurable |

## Reframing for the CEO

Suggested message:

> "We'll have the marketplace live in Q2. It launches as our integration hub, with our existing integrations plus the new ones that cost us six enterprise deals, and an API in beta. We'll open it to outside builders later, once we see demand. That order fixes the revenue problem first and avoids building a platform nobody is using yet."

## Decisions needed from you this week

1. Approve the Q2 scope contract (first-party catalog plus API beta, no open submissions).
2. Name the owner and approve the engineering allocation, including what slips.
3. Approve the 3-week Phase 0 evidence sprint.
4. Approve a conversation with the CEO using the reframing above.

## Assumptions to check

- The 6 lost deals are enterprise-sized. If their average value is well above your ~$12.8K blended ARR per customer, the integration investment is easy to justify. If not, rethink the size.
- A single unified-API or iPaaS vendor can cover a meaningful share of the requests. Verify coverage and pricing in Phase 0.
- Your architecture can expose a safe public API without a major refactor. Ask engineering for a 1-week spike.