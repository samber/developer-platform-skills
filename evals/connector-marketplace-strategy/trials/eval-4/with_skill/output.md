# Veriquil marketplace: quality bar and placement design

## Assumptions I made

The skill calls for an interview first. I didn't run it, so these answers are assumed. Tell me which are wrong, because each one moves a rung.

- **Q6 (data sensitivity): high.** Apps read patient records, site financials and protocol deviation logs. De-identified is not risk-free: small sites and rare-disease cohorts can be re-identified. Deviation logs and financials are also commercially and regulatorily sensitive (GCP inspection exposure, sponsor confidentiality).
- **Q3 (supply): the four launch partners are the only supply signal.** There is no evidence of unofficial third-party integrations.
- **Q2 (demand): not stated.** If the answer is 2d ("feels strategic"), the step 1 gate says "not yet, curated catalog first". I'm assuming 2a–c holds.
- **Q5 (purpose):** retention and distribution, not a revenue line.

## Verdict on the head of product's position

I recommend against both halves as stated.

**"Review nothing" fails on the skill's own logic.**
- Open admission is the right rung only when apps touch little sensitive data and supply is the binding constraint. Q6 = high flips that first condition.
- The skill says a high Q6 promotes the single hard review gate, because "an uncertified-but-listed tier is an incident waiting to be attributed to you."
- The efficiency objection to the hard gate is that review cost scales with every submission. At four partners, that cost is four reviews. Her argument is a mature-platform argument applied at the one moment it costs least.
- Over-curation kills supply when the gate is sized for a mature platform. Here the gate is sized for four known partners and grows with the pipeline.

**Selling the Featured slot is fine in principle, wrong at launch, and needs a disclosure rule.**
- The skill separates admission from discoverability. Paid placement that reads as an editorial pick spends the trust that curation bought.
- At launch the slot would sell to the four partners you are trying to seed. That taxes the hard side during the cold start.
- The revenue doesn't justify it. Four partners at $5,000 a quarter is at most $20,000 a quarter, which is not program funding. I'm inferring the four-buyer ceiling from the pool, not from her number.

## 1. Quality bar

**Position: single hard review gate for the Veriquil launch, with a planned move to a hybrid (open + certified) once Q6-style risk can be scoped by data tier.** The hybrid rung is gated on the promotion conditions below.

### Admission rules

Every listing needs all of the following before it exists in the catalog.

1. **Completeness check.** Named legal entity, data-flow diagram, subprocessor list, support contact.
2. **Compliance review.**
   - Data handling against Veriquil's own privacy and security requirements.
   - A written statement of the de-identification method relied on, and a contractual ban on re-identification attempts and on linking records to outside datasets.
   - Regulatory fit: HIPAA/GDPR posture, and Part 11-style audit-trail expectations where the app writes back.
3. **Security review.**
   - OWASP Top 10 testing.
   - **Scope minimization:** unused or excessive OAuth scopes are flagged for removal. Scopes are per data class, so an app never gets patient records, financials and deviation logs as one bundle.
   - Sandbox tenancy with synthetic data for all testing. No production data before approval.
4. **Post-approval monitoring.** Approval is not permanent, and Veriquil keeps removal authority (see below).

### Scope tiers (the lever that keeps the gate cheap)

| Tier | Data an app may read | Review depth |
|---|---|---|
| A | None of the three sensitive classes (UI widgets, scheduling, reporting on non-sensitive fields) | Steps 1–2 plus automated security checks |
| B | One sensitive class | Full steps 1–4 |
| C | Patient records, or two or more classes | Full steps 1–4 plus manual security test and reviewer sign-off by security and compliance |

Tier A is where a hybrid could later open. Tiers B and C stay gated.

### Governance (all three questions, each with an owner)

| Question | Rule | Owner |
|---|---|---|
| Admission | Review gate above. Decision in writing, with reasons on rejection. | Head of Platform, with Security and Compliance sign-off for Tier C |
| Value split | Zero take at launch (section 3). | Head of Product |
| Conflict resolution | See delisting below. | Head of Platform, appeal to a named exec |

**Delisting rules** (a rule without a removal path is a preference):
- Triggers: a security incident, scope creep beyond the approved data classes, re-identification attempts, failure to meet a retroactive security requirement, revenue-share circumvention if a take-rate is introduced later.
- Notice: immediate suspension of data access for an active incident. Otherwise 30 days' written notice with a remediation path. I picked the 30 days; adjust it.
- Decision: owner above. Appeal goes to a named exec, with a response SLA.

**Market-failure check:**

| Cause | Rule |
|---|---|
| Information asymmetry | Mandatory data-flow disclosure, shown on the listing |
| Externalities | One app's breach exposes a CRO's sponsors, hence per-class scopes and incident notification duty |
| Monopoly power | Pooled scale for small partners (below), no pay-to-rank |
| Risk | The review gate and monitoring |

**Partner concentration:** with four launch partners, a few will dominate. Write the pooled-scale mechanism in from day one: shared usage analytics and shared marketing slots for smaller partners.

**Review cadence:** schedule a governance review at 6 months. Platforms grow more open over time, so launch rules are not permanent.

### The openness counter-argument

Heavy gatekeeping inflates fees, hampers innovation and costs choice. That argument is live for generic consumer app stores. It is weak here, because the data is regulated and review is cheap at this scale.

### Promotion conditions (when to loosen)

Revisit the hybrid rung (open Tier A, certified Tier B/C) when all of these hold:
- Review queue time exceeds a target you set (suggest 4 weeks) for two consecutive quarters.
- Applications from non-launch partners are being turned away for capacity, not for quality.
- Tier A is at least half of submissions.

## 2. Placement design

**Principle: decouple admission, editorial endorsement and paid visibility.**

### Launch (first two quarters): no paid placement

- Homepage "Featured" is editorial only. Eligibility is review-approved status.
- Selection criteria are published: install-to-active rate, review score, maintenance freshness, and a Veriquil-side fit judgment.
- Reviews and organic ranking sit under it. Review-driven ranking is the counterweight to pay-to-play.
- The four launch partners get guaranteed launch placement as part of seeding. It is a subsidy, not a sale, and it is disclosed as "launch partner".
- Your head of product's funding goal is deferred, not rejected. Zero take plus no paid slot is the cheapest way to win the hard side.

### Later: a separate, labelled sponsored slot

Introduce it only when all of these hold:
- The catalog has enough approved apps that a slot is scarce (suggest 15 or more, my number).
- Install volume makes the slot worth buying.
- Seeding is done.

Rules:
1. **Separate slot, separate label.** "Sponsored" is shown in the slot itself. It never carries the name "Featured" or "Editor's pick".
2. **Eligibility:** approved apps only, and for Tier C apps only those with a clean monitoring record. Money never substitutes for review.
3. **No rank effect:** sponsorship cannot change organic ranking or the editorial slot.
4. **Fair access:** auction or fixed rotation, with small partners able to bid. Do not let the biggest partner buy every quarter.
5. **Pull right:** a sponsored app that is delisted or suspended loses the slot immediately, with prorated refund.
6. **Price:** $5,000 a quarter is a placeholder. Set it from measured install lift after launch, not before.
7. **Disclosure in the contract** and in the marketplace terms.

## 3. Economics (one line, so the above holds together)

Zero take-rate while seeding, with a committed notice period for any future rate (suggest six months, unfavorable changes deferred). Billing mechanics belong to `app-marketplace-monetization-model`.

## 4. What I'd say to the head of product

- Supply is not the binding constraint. You have four committed partners and a data-risk profile that makes one incident decisive.
- Reviewing four apps costs almost nothing, and it buys the claim that every Veriquil app was reviewed. That claim is what sponsors and CROs will want in procurement.
- The Featured slot is worth more as an earned signal. Sell a clearly labelled sponsored slot later, once there is something scarce to sell.

## Open items

- **Step 1 gate:** this answer assumes the build triggers hold. Confirm the demand evidence (Q2) and the procurement friction before committing, or fall back to a curated partner catalog.
- **Not run:** the seeding sequence and flywheel metrics (steps 6–7) are out of scope for this request.
- **Needs review:** I have not had security or compliance review the scope tiers or the de-identification clause. Treat both as drafts.