# Governance reset for the Halvard Analytics alliance

I used `integration-partnership-strategy`, mainly step 2 (depth ladder) and step 3 (governance of deep rungs), plus the JDA-vs-JV detail from its references. The skill asks one interview question at a time. You asked for the finished deliverable, so I filled the gaps with the assumptions below. Correct me if any are wrong, because they change the recommendation.

## Assumptions

| # | Assumption | What it changes |
|---|---|---|
| A1 | The "strategic alliance" is a signed business agreement with no joint development agreement (JDA) and no joint business plan. | Step 3 sets up the missing paper. |
| A2 | No demand evidence has been written down: no named joint customers, no deal-attached revenue, no retention data. | The partnership is unproven, so the 90-day gate below tests it. |
| A3 | Budget and a named executive sponsor are unknown. | I assume interest without a decision-maker, which is why the sponsor is Fix 1. |
| A4 | There is no hard deadline and the goal is a compounding asset. | This favors fixing co-build over retreating to a shallow rung. |

## Diagnosis

You signed a co-build alliance, but you are running it as a referral alliance with no accountability.

- **Two slide swaps are not QBRs.** A QBR reviews last quarter against dated commitments and sets the next quarter's. There were no prior commitments to review. These were status updates.
- **No shared plan.** Nobody owns a target, a date, or an unblock obligation. When Halvard's engineering went quiet in month three, nothing was breached because nothing was promised.
- **No engineering channel and no change-notice duty.** You learned about their API re-platform from a mutual customer. This is the sharpest failure, because a re-platform may have invalidated the integration design.
- **No decision-makers in the room.** Both calls were quarterly-numbers presentations. Nobody could approve resources on either side.
- **No demand evidence (A2).** The skill requires a written demand-evidence line before a partner is on the shortlist. Without one, "deep joint integration" is a hope, not a plan.

## Legal's question: joint venture?

**No. Do not restructure as a joint venture.**

- A JV creates a new jointly owned legal entity with shared management, profits, and liabilities. The skill reserves it for a genuinely shared new entity or product.
- Your problem is missing cadence, owners, and obligations. A JV would not create engagement. It would add entity formation, shared liability, and a harder unwind.
- The default shape is a **JDA scoped to the specific integration**. Both parties stay independent, no new entity is formed, and IP, support, and roadmap terms are explicit.
- Revisit a JV only if the joint work later becomes a separate product with its own revenue, customers, and P&L. Use contractual escalation, as in the Vast Renewables/EDF example: a JDA first, then a JV per project once it reaches a defined stage.

I am not your counsel. Give legal this framing and let them confirm the JDA terms.

## The fix: six moves

### 1. Name a sponsor on each side this week

- Each side needs one executive who can approve engineering hours and budget.
- Add an operating committee: one alliance manager, one integration engineer, and one product owner per side.
- If Halvard will not name a sponsor and an engineer within 2 weeks, treat that as your answer. Skip to the 90-day gate.

### 2. Write the joint business plan in 30 days

It is a short document both sides work from. It contains:

- **Customer evidence.** Named joint customers, deal counts, and any retention data. The mutual customer who told you about the re-platform is a candidate, so interview them.
- **Scope.** The specific integration use cases and a definition of done.
- **Phased targets with dates.** Shared pipeline and adoption targets.
- **Lift per phase.** Which side carries the heavier load in each phase. A stall on one side obligates the other to unblock, not to wait.
- **Quality bar and security review.** The standard the integration must meet before launch.

### 3. Replace the slide swaps with real QBRs

- **Cadence.** Quarterly, with a monthly operating-committee sync until the first launch.
- **Attendance.** The alliance managers plus someone on each side who can approve resources.
- **Fixed agenda.** Four blocks:
  1. Last quarter against the previous commitments.
  2. Pipeline by name.
  3. Blockers.
  4. Next quarter's plan.
- **Exit rule.** The meeting is not finished until it produces dated commitments with owners. Otherwise it was a status update.
- **First QBR.** Hold it within 45 days. Its first agenda item is the re-platform fallout.

### 4. Install the engineering channel and a change-notice clause

- **Shared channel.** A shared Slack or Teams channel, plus a named integration engineer on each side.
- **Roadmap visibility.** Each side shares its roadmap and upcoming platform changes at every sync, not only at launch.
- **Contract clause.** Add to the JDA or an amendment: advance written notice of breaking API or platform changes, a deprecation window, and a named technical contact. Pick the notice period with your engineers. The skill gives no number.
- **Immediate task.** Get Halvard's re-platform documentation and assess impact on your integration work this sprint.

### 5. Treat the integration as a product

- It gets its own roadmap, backlog, quality bar, security review, and definition of done.
- Name an integration product manager on your side. Without one, the likely outcome is decay after launch.
- Add a shared scorecard (joint plan, shared KPIs, QBR-ready dashboard) visible to both sides.

### 6. Set up two-tier governance if the alliance is large

| Tier | Members | Decides | Cadence |
|---|---|---|---|
| Joint steering committee | Executive sponsors | Strategy, budget, major pivots, escalations | Quarterly or twice yearly |
| Operating committee | Alliance manager, integration engineer, product owner on each side | Resource allocation, roadmap sequencing | Monthly, QBR quarterly |

For a smaller alliance, the operating committee alone is enough, with the sponsors as the escalation path.

## 90-day gate

Re-test the depth rung at day 90 against the three-fit test: product fit, commercial fit, and operational fit must all line up.

| By day | Pass signal |
|---|---|
| 14 | Halvard names a sponsor and an integration engineer. |
| 30 | Joint business plan signed by both sponsors, with customer evidence attached. |
| 45 | First real QBR held, with dated commitments recorded. |
| 60 | Re-platform impact assessed, and the change-notice clause agreed or in legal review. |
| 90 | Halvard has delivered at least one dated commitment, and the integration scope is re-confirmed against their new API. |

- **If the gate passes:** keep co-build and report sourced and influenced pipeline as two separate capped numbers (step 5 of the skill).
- **If it fails:** step down to the default rung, co-sell/integration alliance. Build and maintain one integration on their public API, with a joint pipeline motion and no joint roadmap commitment. If there is still no demand evidence, drop to referral.
- **If it fails on the Halvard side:** ending the deep alliance is a legitimate outcome. Do not keep funding a co-build they will not staff.

## Open questions

1. Is there a named sponsor with budget on your side (A3)?
2. Does any demand evidence exist: named joint customers, blocked deals, retention data (A2)?
3. Is there a hard deadline for a first result (A4)?

Answers to these could move the recommendation toward a shallower rung.

## Sourcing and caveats

- The JDA-vs-JV rule, QBR definition, and two-tier governance come from the skill's references (PartnerStandard, Umbrex, the Vast Renewables/EDF filing). They are practitioner guidance, not legal advice.
- The change-notice clause is my addition. The skill does not specify one, and the notice period is for your engineers and counsel to set.
- The 90-day gates are my proposal, not from the skill's sources.