# Bellwright: partner revenue rebuild for the Q3 headcount ask

**Caveat.** The skill calls for a one-question-at-a-time interview. This task needs a single complete answer, so I assumed the answers below. Correct any that are wrong, because each one changes a recommendation.

| Interview item | Assumed answer | What it changes |
|---|---|---|
| Q1: program today | A handful of integrations, no tiers | Co-sell is the default rung. |
| Q2: demand data | Only the spreadsheet, so (d) | Attribution becomes a prerequisite, not a follow-up. |
| Q3: reporting line | Partner manager (Dana) reports into Sales | Keep the function under Sales for now. |
| Q4: sponsor | None with budget | The ask needs a named sponsor. |
| Q5: deadline | The Q3 headcount review | Fast rungs only. |
| Q6: goal | Compounding asset | Few-and-deep portfolio. |
| Q7: effort ceiling | Unknown | The ask is staged so it fits a low ceiling. |

## 1. Why finance rejected the $31M

- **The number is more than 77% of the company.** $31M against about $40M ARR is 77.5%. A CFO cannot accept that, and the skill says this is the result that "ends the conversation immediately".
- **The tag measures logo presence, not partner effect.** A partner logo anywhere in the opportunity notes counts as a touch. That conflates "sourced" (the deal wouldn't exist without the partner) with "influenced" (the partner advanced a deal that already existed). It also counts mentions that did nothing.
- **There is no cap and no split.** Credit is not capped and not divided between sourced and influenced.
- **Claims are made after the outcome.** Dana tags in the last week of the quarter, after the deals closed. Nothing predates the result.
- **The record is a Google Sheet.** It sits outside the CRM, and the person maintaining it is the person whose function is being justified. That is the structural weakness the skill names.
- **The units may not match.** I don't know whether $31M is closed-won ACV, bookings, or total contract value. If it is cumulative bookings against current ARR, it is a different comparison and part of the "three quarters" shock may be units alone. Check this first.

The old number is retired. Do not defend it, adjust it, or reuse it as a baseline.

## 2. The rebuilt measurement

### Definitions

Three buckets that must sum to total closed-won new ARR, to the dollar:

| Bucket | Definition | Credit |
|---|---|---|
| **Partner-sourced** | The partner originated the deal through deal registration or a referral. The deal would not exist without them. | 100% to one partner. Only one sourced partner per deal. |
| **Partner-influenced** | The deal already existed and the partner materially advanced it. Qualifying evidence is a co-sell call, technical validation or POC, procurement access, or a documented integration requirement. A logo mention does not qualify. | Split by role, within a cap set before the quarter. |
| **Direct** | Neither of the above. | None. |

Sourced and influenced are always reported as **two separate, capped numbers**, never one blend.

### Rules

1. **Add a partner-source field to the CRM opportunity.** It carries the partner, the claim type (sourced or influenced), and the evidence type. The spreadsheet stops being a system of record.
2. **Claim at deal creation with a dated ID.** The claim must predate the outcome. Anything added at close is flagged "retroactive" and excluded from the headline.
3. **Use a short window.** The claim must be made within about 14 days of opportunity creation. Later claims are labeled and not counted.
4. **Set credit caps before the quarter starts.** Finance and the partnerships lead agree them in writing.
5. **Have someone other than Dana audit.** Rev ops or finance samples claims each quarter and checks the evidence.
6. **Reconcile to the booking report finance already uses.** Sourced + Influenced + Direct must equal total closed-won new ARR. If it doesn't, the report is not published.

### Backfill for the current ask

Dated claims don't exist for past quarters, so the history cannot be repaired. Rebuild the last four quarters in tiers instead:

- **Tier A (the headline floor).** Deals where verifiable evidence predates opportunity creation. Examples are a partner referral email, a deal registration, or a dated CRM activity from the partner.
- **Tier B (a labeled range).** Deals with evidence from after creation but before close. Report as "influenced, unaudited".
- **Excluded.** Logo-only tags. They count for nothing.

Present the result as a floor and a ceiling, with Tier A as the number you stand behind. A modest audited figure beats a large one that gets challenged. I can't compute it here because I have no access to the CRM or the sheet, so no figure appears in this document.

### The set to report

These go inside the dashboards leadership already checks, not in a separate partner report:

- Sourced revenue and influenced revenue, as two numbers.
- Activation rate: the share of signed partners that ever produced a lead or revenue.
- Time to first deal.
- Partner CAC against direct CAC. A common working benchmark is under about 1.5x (vendor-published, directional).

## 3. Making it credible beyond the number

- **Demand evidence per partner.** Every partner you ask to invest in carries a written line with named deals, request counts, or retention data. No partner stays on the list because of a relationship.
- **Comp alignment.** If AEs earn less on partner deals, they deprioritize them. Settle this before you scale or the data will stay thin.
- **Unified forecast.** Partner pipeline joins the same forecast review as direct pipeline, with the same exit criteria.
- **Retention lift.** Measure it from your own cohorts: customers with partner integrations against those without. Do not cite industry stats to the CFO. The Crossbeam figures are vendor-published ceilings, and the "83% of buyers cite integrations" figure is unverified and must not be shown to finance.

## 4. Portfolio recommendation

I considered three portfolio shapes:

- **Few-and-deep:** 3-5 partners chosen on demand evidence, each on a co-sell rung.
- **Category breadth:** one integration per adjacent category. It is the cheapest to start and has the weakest per-partner economics.
- **Platform anchor:** one dominant platform partnership plus a thin tail. It concentrates risk as well as gravity.

**Recommendation: few-and-deep.** After the Q3 audit, evidence will exist for only a few partners, and the Okta case (company-reported) argues against spreading thin. Hold every partner at co-sell or lower until it shows repeatable sourced deals and passes the product, commercial, and operational fit test.

## 5. The ask: three heads, staged

The skill says attribution must exist before the plan asks for headcount. So the ask is structured around gates rather than one request for three people.

| Tranche | Headcount | Role | Release gate |
|---|---|---|---|
| Now | 1 | Partner operations / integration analyst, covering CRM field, audit, and dashboard | Approved with the attribution design. It pays for itself by making the other two defensible. |
| After one clean quarter | 1 | Partner / integration engineer, owning builds and certification maintenance | CRM-level sourced and influenced numbers reconcile to bookings, and Tier A is non-trivial. |
| After two quarters | 1 | Alliance manager for the top 3-5 partners | Activation rate and partner CAC against direct CAC are at or under the agreed threshold. |

Notes for the proposal:

- **Placement.** Keep the function under Sales at first, as the skill's default for an unproven function. Revisit around 100 employees, when the split roles become justified.
- **Certification.** Join no certification program unless the proposal names a renewal owner and a standing annual cost. Count that cost against the integration engineer's time.
- **Sponsor.** Name an executive sponsor. The CFO's own team should co-own the audit step so the number is theirs as well.

## 6. Self-set gates before the Q3 meeting

1. Every partner in the plan has a demand-evidence line.
2. Sourced and influenced are defined as two capped CRM-level numbers, with dated claim IDs and a stated window, before headcount is requested.
3. Every certification names a renewal owner and a budgeted cost.

Add a fourth for this case: the three buckets reconcile exactly to the closed-won total finance uses.

## What I need from you

- Is the $31M closed-won ACV, bookings, or TCV, and over what period?
- Does the CRM record when each opportunity was created and who created it? That determines how much of the backfill reaches Tier A.
- Does the CFO's team have a bookings report I should reconcile to?
- Who is the executive sponsor?

Once I have the first two answers, I can draft the exact CRM field spec and the audit sampling method.