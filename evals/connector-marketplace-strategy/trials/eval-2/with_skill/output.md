# Cadence Ops: Marketplace Operating Model (draft for Thursday board)

**Do first:** confirm or correct the 6 assumptions in the table below. The skill's interview was skipped because you asked for the full document today. Every assumption could change a recommendation. About 10 minutes.

## 0. Decision summary

- **Recommendation:** do not launch a paid marketplace now. Launch a **Certified Partner Catalog** (stage 1) with zero take-rate. Set written promotion criteria for a **volume-tiered paid marketplace** (stage 2).
- **Why:** supply evidence is strong, but customer pull, procurement friction and partner-lifecycle capacity are not yet evidenced. Without them, a paid marketplace becomes "little more than an expensive partner directory."
- **Business case that carries the decision:** retention and expansion. At 1,100 customers, an ecosystem-distribution flywheel is not yet the justification.
- **Kill test:** if accounts with 4+ installed integrations do not churn measurably less than the rest, the case fails and we stay at "join and buy."
- **Urgent item:** 3 unofficial integrations reverse-engineer the web app today. They are a security and support exposure, and the strongest supply signal we have.

## 1. Assumptions to confirm

| # | Interview item | Assumed | Changes if wrong |
|---|---|---|---|
| Q1 | Ecosystem today | (c) partner directory with 40 integrations | None |
| Q2 | Demand evidence | **Unknown.** No lost deals or support requests cited | If (a)-(c) exist, trigger 1 passes and stage 2 moves earlier |
| Q3 | Supply evidence | (a) and (b): 6 partners want to charge, 3 unofficial integrations | None |
| Q4 | Staff the partner lifecycle | **Partial.** Public API and 2 partner engineers. Sandbox tenancy, review and partner support not confirmed | If not a standing commitment, stage 1 shrinks to a better directory |
| Q6 | Data sensitivity | Medium. Customer addresses, contacts, work orders, technician locations | If high, move to a single hard review gate |
| Q7-9 | Deadline, one-off vs compounding, effort ceiling | Board Thursday, no hard launch date. Compounding asset. Effort ceiling = 2 engineers, no subsidy budget | A funded budget promotes subsidies. A hard date promotes first-party connectors |

Q5 (purpose) is set by this document: retention first, revenue later.

## 2. Gate: build, join or buy

| Trigger | Status | Evidence |
|---|---|---|
| 1. Clear customer pull | ❌ Unevidenced | None provided |
| 2. Ecosystem fit and supply | ✅ Pass | 6 partners asking to charge. 3 unofficial integrations already shipped |
| 3. Repeated procurement friction | ❌ Unevidenced | None provided |
| 4. Readiness for the full partner lifecycle | ⚠️ Partial | Documented public API and 2 partner engineers. Nothing on sandbox, review or support |

- **Verdict:** two of four triggers lack evidence, so build is not justified yet. Join and buy do not fit either, because supply already exists and the problem is governance and trust, not integration volume.
- **Intermediate step (recommended):** the Certified Partner Catalog.
- **Promotion criteria to stage 2**, all of which must hold:
  1. Trigger 1 and trigger 3 each cite 3 or more concrete cases (lost deals, stalled deals, support requests or procurement requests tied to integrations).
  2. The 2 partner engineers' time shows a standing partner-lifecycle load that fits current headcount, or headcount is approved.
  3. After one full quarter, the retention check in section 7 shows lower churn for accounts with 4+ installed integrations.
  4. At least 3 partners have a paid app live and ask for platform billing.

Pull items 1 and 3 from CRM loss reasons and support tickets before Thursday if possible. That is the cheapest way to strengthen the board case.

## 3. Operating-model candidates

| | A. Certified Partner Catalog (recommended) | B. Paid marketplace with platform billing | C. Buy embedded iPaaS |
|---|---|---|---|
| Archetype | HubSpot: listed/certified ladder, zero take | Shopify: 0% under a threshold, then a percentage | Embedded iPaaS (one case built 100+ integrations in a year) |
| Optimizes for | Retention, trust, low effort | Revenue and partner monetization | Integration count fast |
| Costs | 2 engineers on review, sandbox, support | Billing, payouts, tax, disputes on top of A | Vendor fees. Cadence does not own the ecosystem |
| Failure mode | Stays a directory if nobody promotes it | Expensive directory with a billing layer, no distribution to justify a take | Does not answer the 6 partners or the unofficial integrations |

- **Recommendation: A now, B as the promoted state.** It matches the effort ceiling, answers the six partners without building billing, and keeps B open once the criteria in section 2 hold.
- **How A serves the six partners:** partners may charge their own customers through their own billing. Cadence lists the price model on the listing (see disclosure rule below). Cadence takes nothing and builds no billing.
- Billing and payout mechanics for stage 2 belong to `app-marketplace-monetization-model`, not this document.

## 4. Governance (stage 1)

Governance answers three questions in writing. Each has an owner. Owners are role placeholders; name individuals before Thursday.

### 4.1 Admission (owner: Head of Partnerships)

- Any partner signing the Partner Terms and passing the automated bar gets **Listed**.
- **Automated bar (Listed):**
  1. Uses only the public API with OAuth, with minimal scopes.
  2. Publishes a privacy policy and a security contact.
  3. Passes a smoke test in a sandbox tenant.
  4. Declares price model, if any.
- **Certified tier (separate, quantitative):**
  1. Security questionnaire completed.
  2. API success rate above a floor set from the first-quarter baseline. HubSpot's 95% is context, not a target.
  3. Maintenance evidence: updated within the last 2 quarters.
  4. Review of the app by a minimum number of customers.
  5. Re-review every 6 months.
- **Losing Certified removes the badge, not the listing.** "Allowed to exist" and "endorsed" stay separate.
- **Escalation:** if Q6 is "high", move to a single hard review gate for every listing.

### 4.2 Value split (owner: Head of Product, with Finance)

- **Stage 1:** 0% take, no listing fee, no review fee. Partners keep 100% of what they bill.
- **Stage 2:** see section 6.
- **Paid placement:** if sold, it carries a visible "Sponsored" label. Organic ranking stays review-driven. Undisclosed paid placement spends the trust that curation buys.
- **Rate-change commitment:** 6 months' notice for any unfavorable change. Favorable changes may take effect early.

### 4.3 Conflict resolution and removal (owner: Head of Security for security, Head of Partnerships for policy)

| Trigger | Action | Notice | Decider |
|---|---|---|---|
| Active security incident or data misuse | Immediate suspension | Same day, partner informed | Head of Security |
| Failed re-review or lapsed maintenance | Certified badge removed, stays listed | 30 days to cure | Partnerships |
| Policy breach (scraping, scope abuse, misleading listing) | Delisted | 30 days to cure, shorter if repeated | Partnerships |
| Retroactive security requirement | Delisted if not met by the deadline | At least 90 days | Head of Security |

- Partners get one written appeal to a second reviewer within 14 days.
- Delisting is the lever. A rule without a removal path is a preference.
- Review governance every 6 months. Platforms grow more open over time, so criteria are not permanent.

### 4.4 Check against the four market-failure causes

- **Information asymmetry:** partner declares scopes, price model and data use on the listing. Customers see them before install.
- **Externalities:** one unsafe app harms the Cadence brand. Mitigation: scope limits, rate limits, suspension right.
- **Monopoly power:** one big partner dominating. Mitigation: pooled analytics and shared marketing for smaller partners, set up now. Trigger to review: top 3 partners above 50% of installs or revenue (proposal, not a benchmark).
- **Risk:** residual data-breach risk. Mitigation: uninstall deletes tokens and requires partner data deletion, plus a customer-visible audit of granted scopes.

No cause is left without a rule.

### 4.5 The 3 unofficial integrations

- They scrape the web app. We cannot see their security posture, and they break when the UI changes.
- **Recommended path:** invite in, then enforce.
  1. Identify them (access logs, support tickets).
  2. Close the API gaps they exploit. Their reason to scrape is a missing endpoint. List these gaps.
  3. Offer a time-boxed amnesty (suggest 90 days) to migrate to the public API and be listed.
  4. After the window, update the Terms of Service to prohibit scraping and add technical blocks. Legal review before any notice.
- **Why not block first:** it wastes the supply signal and turns builders into adversaries. Legal action remains available but is not the opening move.

## 5. Quality bar (curation position)

- **Rung: hybrid** (open listing with a minimal automated bar, plus Certified). It scores best on efficiency, and the effort ceiling of 2 engineers rules out per-listing manual review.
- **Moved by:** Q6 = medium keeps hybrid. Q6 = high would promote the single hard review gate. Supply is the binding constraint, so open admission as the only gate is rejected as too weak for field and customer data.
- **Partnership-gated listing** is not needed yet. It becomes relevant if resellers or enterprise co-selling partners join.

## 6. Economics

| Stage | Take-rate | Rung |
|---|---|---|
| 1 (now) | 0%, no fees | Zero take while seeding |
| 2 (after promotion criteria) | Volume-tiered: 0% under a partner-revenue threshold, a moderate percentage above | Volume-tiered |
| Never planned | Flat 15-25% plus fee stack | Needs distribution Cadence does not have |

- **Why zero now:** taxing the hard side before it has reasons to build selects against the supply we depend on. HubSpot shows 0% is a durable architecture, not a transitional one.
- **Stage 2 sizing:** Shopify's 0% under $1M a year is not transferable. At 1,100 customers, few partners would ever cross that figure. **Set the threshold and percentage from the 6 partners' actual marketplace revenue, collected before stage 2.** I give no number because I have no data. Placeholder range to test, not a recommendation: threshold in the low hundreds of thousands of dollars a year per partner, rate at or below 15%.
- **Anti-circumvention:** takes effect only when billing runs through Cadence. Then partners must bill through the platform for Cadence-originated customers, and breach leads to the delisting path in section 4.3.
- **Notice:** 6 months for any unfavorable rate change, written into the partner terms at stage 1.

## 7. Seeding plan

- **Hard side:** the partners and developers who build integrations, not customers.
- **Atomic network:** one use case, dense. **Hypothesis only:** pick the single use case where the most existing installs and the 6 paying-intent partners overlap. Confirm from install data across the 40 integrations. I do not know which use case that is.
- **Rung: first-party complements, plus the existing partners as anchors.**
  1. Make the 6 charging partners the anchor ISVs, because they are already built and motivated.
  2. Ship at most 1-2 first-party connectors in the atomic use case if the 6 do not cover it. Skip if they do.
  3. Run the amnesty path for the 3 unofficial builders.
- **Promotion condition for other rungs:**
  - Subsidies (build funds, guaranteed floors): promoted only if a hard deadline and a budget appear. The zero-take window already acts as a light subsidy.
  - Trojan-horse tooling: not needed, because supply already exists.
  - Hackathons: promoted only once the compounding mandate gets a partner-community budget. Layer on top, never in place.

### Timeline (estimates, not commitments)

| Window | Work |
|---|---|
| Days 0-30 | Partner Terms and API terms updated. Listed bar and sandbox tenant defined. Gap list from the 3 unofficial integrations. Partner revenue data collected from the 6 |
| Days 30-90 | Open the catalog. First Certified cohort from the 40. Amnesty window running |
| Days 90-180 | First-quarter baselines complete. Promotion review against section 2 criteria |

## 8. Flywheel measurement

Gates for this document:
1. Every build trigger cites evidence. Triggers 1 and 3 currently do not, which is why the answer is "not yet."
2. All three governance questions have written answers and a removal path (section 4).
3. The seeding plan names the hard side, atomic network and rung. The atomic network is a hypothesis to confirm.

**Supply side (lead with these, it fails first):**
- Active partners with a live listing.
- Time from partner signup to first live listing.
- Share of catalog updated in the last 2 quarters.
- Partner revenue concentration.

**Demand side:**
- Share of customers (of 1,100) with at least 1 installed connector.
- Installed integrations per account, watching the 4+ cluster.
- Churn and expansion delta between accounts above and below 4 integrations. This is the direct test of the retention case.

**Flywheel coupling:** marketplace-attributed influence on new deals and churn saves. Attribution is soft; direction matters more than precision.

No industry thresholds exist at this scale. Baseline against the first quarter. Salesforce's 91% usage is a mature-platform anchor, not a target.

## 9. Risks

- **Building too early:** mitigated by the promotion criteria in section 2.
- **Over-curation:** mitigated by hybrid curation and an automated bar.
- **Capacity:** 2 engineers cover review, sandbox, support and gap-closing. If the plan slips, cut Certified re-reviews to annual before cutting the sandbox.
- **Partner frustration:** the 6 want to charge. Stage 1 allows it via their own billing. Tell them the stage 2 criteria and dates openly.
- **Security exposure from scraping:** ongoing until the amnesty ends.

## 10. Decisions requested from the board Thursday

1. Approve stage 1 (Certified Partner Catalog, 0% take) and the 6-month notice commitment.
2. Approve the stage 2 promotion criteria in section 2.
3. Confirm owners for admission, value split, and security removal.
4. Approve the unofficial-integration amnesty approach, pending Legal review.
5. Confirm the 2 partner engineers as a standing commitment, or approve headcount.

## 11. Not verified

- Customer-pull and procurement-friction evidence (Q2).
- Sandbox, review and support capacity (Q4).
- Data sensitivity classification (Q6).
- Atomic use case, partner revenue, and the stage 2 threshold and rate.
- All benchmark figures (HubSpot, Shopify, Salesforce) come from the skill's reference files, dated 2026. Re-verify before quoting in the board deck.

**Next:** reply with corrections to the Section 1 table, starting with Q2 and Q4. After that, I can fill in the evidence for triggers 1 and 3 and tighten sections 5-7.