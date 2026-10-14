# Threadline marketplace strategy

**Decision: do not build a marketplace for Q2. Ship a curated Integrations Hub by Q2 and set written criteria for promoting it to a marketplace later.**

**Next action (10 minutes):** send your CEO the reframe in section 9, before Q2 planning locks.

I could not interview you one question at a time, so section 0 lists my assumptions. Correct any wrong one and the affected sections change.

## 0. Interview answers and assumptions

| # | Question | Answer used | Source |
|---|---|---|---|
| 1 | Ecosystem today | (b) nine bilateral in-house integrations | You |
| 2 | Demand evidence | (a) six enterprise deals lost, (b) weekly support requests | You |
| 3 | Supply evidence | (c) none. No partner has asked, and nobody has built on you. | You |
| 4 | Can staff the partner lifecycle | No. No API, docs, sandbox or partner manager, and 14 engineers are fully committed. | You |
| 5 | Marketplace purpose | (b) retention and sales lever. Not a revenue line. | **Assumed** |
| 6 | Data sensitivity | High. HR onboarding handles identity, tax, bank and I-9 data. | **Assumed** |
| 7 | Deadline | Soft-hard. The CEO said Q2 at an all-hands. Today is 2026-10-08, so about 6–8 months. | You, inferred |
| 8 | One-off or compounding | One-off win now, compounding option later | **Assumed** |
| 9 | Effort ceiling | About 1–1.5 engineers plus 1 product owner. No new headcount in year 1. | **Assumed** |

Questions to confirm, most important first:
1. Q6: confirm data sensitivity is high.
2. Q9: confirm the effort ceiling.
3. What is the average contract value (ACV) of the six lost deals, and which integrations did buyers name? Both drive the sizing and the build order.

## 1. Gate: build, join or buy

Result: **join and buy, and keep building your own, the key integrations. Do not build a marketplace.**

| Build trigger | Evidence | Pass? |
|---|---|---|
| 1. Clear customer pull | Six deals lost to named integration gaps, plus weekly support requests | ✅ |
| 2. Supply signal | No partner has asked, and nobody has built anything on you | ❌ |
| 3. Procurement friction from one-off requests | Lost deals show integration demand. They do not show friction from repeated one-off builds. Support requests are weekly but not yet counted by integration. | ⚠️ unproven |
| 4. Readiness for the full partner lifecycle | No API, docs, sandbox or partner manager, and engineering is full | ❌ |

All four must hold, and only one does. A marketplace now would be, in the skill's words, "little more than an expensive partner directory."

**Which business case carries the decision:** retention and sales conversion only. The ecosystem flywheel case does not apply at 320 customers with no external builders. The plan is falsifiable on that basis (section 8).

**Sanity check on size.** $4.1M ARR over 320 customers is about $12.8K per customer. If the six lost deals were average-sized, they total about $77K. Enterprise deals are likely larger, but the dollars may be modest next to what a real marketplace costs. Plug in the real ACV. A modest figure strengthens the cheap path.

**Why not build later with the same plan.** High data sensitivity means every third-party app would need a hard security review. That review is a standing cost you cannot staff.

## 2. Operating-model candidates

| | A. Curated Hub (recommended) | B. Invite-only partner program | C. Open marketplace |
|---|---|---|---|
| What | Threadline-owned catalog. Own 9 integrations, plus integrations bought through an embedded iPaaS, plus listings on others' marketplaces. No third-party submissions. | Public API, docs and sandbox. 3–5 anchor vendors (ATS and HRIS) build under a signed agreement. | Self-serve submissions, a hybrid listed/certified tier, 0% take |
| Archetype | No close match in the references. It is the skill's intermediate step, "curated partner catalog," with Zoom-style hard review applied to a few listings. | Closest to Zoom's gated pipeline, plus partnership-gated listing | HubSpot's listed/certified ladder at 0% take |
| Optimizes for | Closing the lost-deal gap by Q2 at near-zero platform cost | Scalable supply of integrations from vendors who benefit | Long-tail breadth |
| Cost | About 1–1.5 engineers, plus iPaaS fees (unpriced) | Public API, docs, sandbox, partner manager and security reviewer, all new | All of B, plus review at volume |
| Failure mode | Looks like "not a real marketplace." Catalog goes stale. | Nobody shows up, because there is no demand-side pull from partners yet | Empty catalog and an unreviewed app touching HR data |
| Fits interview | ✅ | Later (Phase 2) | ❌ |

I recommend A. Sections 3–7 detail A. If you pick B or C instead, tell me and I will redo them.

## 3. Governance

**Admission.**
- Owner: the Hub product owner (a named person, not "product"), with sign-off from your security lead.
- Rule: a listing needs documented demand (at least 3 customer or lost-deal requests) and a security check on the connecting vendor (SOC 2 report or equivalent).
- No third-party self-submission.

**Value split.**
- No money flows through the Hub, so there is nothing to split yet.
- Rule: the Hub never charges partners.
- Open question: whether integrations are bundled in plans or sold as an add-on. That is a pricing decision. It does not belong in this strategy.

**Conflict resolution and removal.**
- Delist if the vendor loses its security attestation, deprecates the API with no replacement, or fails a health check.
- A health check is 30 days of connector error rate above a threshold you set.
- Notice: 30 days to the vendor and affected customers, except for security incidents (immediate).
- Owner: the Hub product owner decides, security lead can override.

**Check against the four market-failure causes.**
- Information asymmetry: every listing shows what data it reads and writes, and who maintains it.
- Externalities: a bad connector hurts every customer's HR data, so the delisting path above applies.
- Monopoly power: not a risk yet, because no partner has scale. Write the pooled-scale mechanism (shared analytics, shared marketing) into the Phase 2 plan.
- Risk: the security check plus the removal path.

**Review cadence.** Governance review every quarter. Curation rules should loosen only as evidence supports it.

## 4. Quality bar

**Rung: single hard review gate, applied to every listing.** The skill's default for efficiency is hybrid, but high data sensitivity (Q6) promotes the hard gate. Review cost scales with submissions, and here the count is 9–15 listings, all invited by you. So the cost stays small.

- Review stages: completeness, data-handling and compliance, security and scope minimization, then ongoing monitoring with removal authority.
- Revisit hybrid (open plus certified tier) only after the Phase 2 promotion criteria are met.
- Discoverability: rank by customer demand and review score. No paid or featured placement. If you ever sell placement, you need a disclosure rule first.

## 5. Economics

**Rung: zero take-rate.** HubSpot funds its marketplace as a retention asset at 0%, so 0% is a legitimate architecture, not a stopgap.

- No revenue share, no listing fee, no review fee.
- Promote to volume-tiered only when (a) billing flows through your platform and (b) some partners clearly earn from it. Neither is close.
- Commit now to 6 months' notice for any future rate change.
- Anti-circumvention rule: not needed at 0%. Add it with the first rate above 0%.

## 6. Seeding

- **Hard side.** Today it is you. There is no external supply, so your first-party engineers and the iPaaS vendor are the supply. In Phase 2 the hard side becomes the HRIS and ATS vendors (and their integration engineers).
- **Atomic network.** One dense use case: *new hire created in ATS → onboarding triggered in Threadline → employee record synced to HRIS.* Pick the two or three ATS and HRIS products that appear most in the six lost deals. Do not build a broad, thin catalog.
- **Rung: first-party complements.** Your 9 existing integrations are the seed. Add the lost-deal integrations next.
- **Buy the long tail.** An embedded iPaaS or unified API for HRIS/ATS is the middle path when the need is "many integrations fast." Candidates to evaluate: Merge, Paragon, Workato Embedded, Prismatic. I have not verified their pricing or HR-data coverage.
- **Join others' marketplaces.** Ask your customers which ones they trust. HRIS and ATS vendors run their own directories. Their eligibility rules are unverified. Check them.
- **Promotion condition to Trojan-horse (public API as a standalone tool):** leave until Phase 2 criteria are met (section 8).
- **Starved options.** Subsidies need budget you lack. Hackathons need a developer community you lack. Do not start either.

## 7. Plan to Q2

Dates assume calendar quarters, so Q2 2027 is April–June. Estimates are rough.

1. **Now–Oct (about 1 week).** Tag every lost deal and last 12 months of support requests by integration name. Count them. This ranks the build order and tests trigger 3.
2. **Nov (2–3 weeks).** Shortlist 2–3 iPaaS vendors. Run a security and coverage check against your top-ranked integrations. Ask each for pricing in writing.
3. **Nov–Jan.** Build or buy the top 3 missing integrations. Start with the one named most in lost deals.
4. **Jan–Feb.** Ship the Hub page, listing the 9 existing integrations plus new ones, with a request form. Add a "request an integration" counter.
5. **Mar–Apr.** Apply to 1–2 third-party marketplaces that your customers already use. Do the listing work in the skill `integration-listing-optimization`.
6. **Q2.** Launch the Hub publicly. Use the skill `app-marketplace-launch-marketing` for launch planning.

Effort cap: stop and re-plan if the Hub work needs more than about 1.5 engineers for two consecutive months.

## 8. Measurement and promotion criteria

**Baseline in the first quarter. Trend against yourself.** The mature-platform anchors (for example, 91% of Salesforce customers use at least one AppExchange app) are context, not targets.

Supply side (leads, because it fails first):
- Integrations live and healthy.
- Days from request to shipped integration.
- Share of integrations updated in the last two quarters.
- Inbound partner requests per quarter. This is your missing supply signal.

Demand side:
- Share of customers with at least 1 active integration.
- Integrations per account. Watch the 4+ cluster, the cited switching-cost threshold.
- Retention difference between accounts above and below 4 integrations. This tests the retention case directly.

Coupling (soft attribution; say so in reports):
- Deals won and lost citing integrations.
- Integration support requests per month.

**Kill criteria (the plan is falsified if):**
- Two quarters after launch, lost-deal count citing integrations does not fall, or
- accounts with 4+ integrations show no retention advantage.

**Promote to Candidate B (invite-only program) when all of these hold.** These thresholds are self-set starting values, not industry standards:
1. At least 3 unsolicited partner build requests in 2 quarters.
2. A public API exists with at least 1 external production consumer.
3. Funded headcount: 1 partner manager plus 2 engineers on platform work, outside the core roadmap.
4. Security review capacity for external code is staffed.

Candidate C is not on the roadmap. Revisit only after B runs for at least a year.

## 9. Handling the CEO's all-hands commitment

The CEO's real goal is to close the integration gap publicly by Q2. A Hub meets that goal. A marketplace does not, because no one outside the company builds on you.

Say this to the CEO:
- "We will launch Threadline Integrations in Q2. It lists our integrations and new ones we add, and we join partner marketplaces. We open to outside builders when 4 criteria are met. Building the marketplace now would take engineering off the roadmap and produce an empty catalog holding HR data."
- Ask whether "marketplace" in the all-hands was a goal or a label. If it is the label, rename the Hub "marketplace" in marketing only after you add third-party apps. Otherwise you pay for a reputation gap.

## 10. Self-check against the skill's gates

| Gate | Pass |
|---|---|
| Every build trigger cites interview evidence | ✅ section 1 (the build recommendation is "no," so unevidenced triggers are correctly flagged) |
| Admission, value split and conflict resolution have owners, including a removal path | ✅ section 3 |
| Seeding names hard side, atomic network, rung and promotion condition | ✅ section 6, with promotion criteria in section 8 |

Not yet done: the skill requires approval section by section. This is a one-shot draft, so approve or correct sections 0–9 and I will finalize.

**Next action:** answer the three questions in section 0 (data sensitivity, effort ceiling, ACV and named integrations of the six lost deals).