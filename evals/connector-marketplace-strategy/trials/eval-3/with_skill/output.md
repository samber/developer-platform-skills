# Lumen Freight marketplace: rate structure and partner announcement

**Verdict:** Don't adopt the CFO's 25% + $2,500 + $400. Launch at 0% take with no fees. Publish a dated tier schedule and a notice commitment.

I skipped the skill's interview, so the assumptions below are mine. Correct any that are wrong. The recommendation changes if answers 2, 6 or 9 differ.

## Assumptions

- **Supply:** the 12 lined-up partners count as confirmed supply. I don't know their commitment level.
- **Demand:** I have no evidence yet, which is the open gate risk (see "Gate check").
- **Data sensitivity:** medium to high. Shipment and customer data is exposed, so a certified tier matters.
- **Deadline:** five months to launch.
- **Billing:** Lumen's own platform collects, so the anti-circumvention rule can be enforced.

## Gate check

The build trigger conditions must hold with evidence:

1. Customer pull.
2. Supply.
3. Repeated procurement friction from one-off integration requests.
4. Staffed partner lifecycle.

I can only evidence supply. If deals aren't being lost over missing integrations, the skill's answer is a curated partner catalog first. The rate question assumes the gate passes. Please confirm items 1, 3 and 4.

## Why the CFO's package fails

| Item | CFO | Closest benchmark | Gap |
|---|---|---|---|
| Revenue share | 25% flat | AppExchange: 15% standard, 25% only for OEM | Top of range, applied to everyone |
| Security review | $2,500 once | AppExchange: $999, paid apps only | 2.5x |
| Listing | $400/year | AppExchange: $150 | 2.7x |

- **Different leverage.** AppExchange earns its fees because 91% of its 150,000+ customers use an app, so it is the procurement gate. Lumen has 12 unproven partners and zero distribution evidence.
- **The Apple analogy fails.** Apple holds the only route to its users. Your logistics partners can sell direct. Shopify markets its 15% ceiling as better than Apple and Google's 30%, which shows partners compare rates.
- **Nothing to take yet.** None of the 12 charges, so 25% of $0 is $0. The only real revenue is fees: at most 12 × $2,900 = **$34,800** in year one, taken from apps with no revenue. That is small money, and it spends the goodwill that gets partners to build.
- **Circumvention pressure.** Pressure rises with the rate. Enterprise B2B partners can close customers on direct contracts and skip your billing.
- **Wrong direction to start.** Favorable changes can be accelerated at will. Unfavorable ones need six months' notice. Starting high and cutting is easy, but starting low and raising costs trust.

## Recommended structure

**Rung:** zero take while seeding, then volume-tiered. Flat percentage plus fees is the starved option and must be earned.

1. **Launch to month 12: 0% on all partner app revenue.** There is no review fee and no listing fee. If Lumen incurs payment-processing costs, pass them through at cost, disclosed separately (Shopify does this at 2.9%).
2. **From month 12: volume-tiered.** Each partner pays 0% under a yearly revenue threshold **T** and a rate **r** above it.
   - Calibrate T from your first-quarter data, since no benchmark transfers to your scale.
   - Cap **r** at 15% unless the promotion condition below is met. Shopify and AppExchange standard are the 15% references.
   - Publish the schedule at launch, so the change comes with about 12 months of notice.
3. **Promotion to flat percentage plus fee stack.** Require evidence of distribution partners can't replicate:
   - Marketplace-sourced deals are a material share of partner pipeline.
   - Most customers have at least one app installed.
   - The marketplace has become a buying gate for your customers.
   - This gives the CFO a defined path upward.
4. **Anti-circumvention.** Paid apps must bill through Lumen. Violation leads to delisting, with written notice and a named decision owner. Billing mechanics belong to the monetization sibling skill.
5. **Notice commitment.** Write six months' notice for any unfavorable rate change into the terms. Favorable changes take effect immediately.

**Quality bar (hybrid):** open admission with a minimal automated check, plus a certified tier (security questionnaire, API success-rate floor, maintenance evidence, scheduled re-review). Losing certification drops the badge, not the listing. If apps get write or PII scopes, raise those apps to a hard review gate.

**Cost recovery without fees:** the review cost is the price of the certified tier. If the CFO needs cost recovery, add a certification fee later, after the promotion evidence above.

## What to announce to partners

Send privately to the 12 partners now, then publish at launch.

1. **Launch terms.**
   - 0% revenue share through month 12.
   - No review or listing fees.
   - Processing at cost, if any.
2. **The published schedule.**
   - The month-12 tier structure (T and r).
   - The 15% ceiling, unless promotion conditions are met.
   - The notice commitment.
3. **Billing rule.** Paid apps bill through Lumen, with the delisting path and notice period.
4. **Governance, each with a named owner:**
   - **Admission:** who decides and by what criteria.
   - **Value split:** the schedule above.
   - **Disputes and removal:** what gets an app delisted, with what notice, decided by whom.
5. **Tiers.** What listed and certified mean, and what certification requires.
6. **Discoverability.** Featured placement is labelled as paid. Organic ranking is review-driven.
7. **Shared services.** Shared analytics and marketing for smaller partners.
8. **Review cadence.** Governance is reviewed on a schedule, not set once.

**Do not announce** numbers nobody has signed off, or a rate you might raise before month 12.

### Draft message

> Lumen Freight opens its marketplace on [date]. As a founding partner, you pay no revenue share and no listing or review fees through [launch + 12 months]. From then, any revenue share applies only above [T] in yearly app revenue, capped at 15%. We commit to six months' written notice of any unfavorable change. Paid apps bill through Lumen; routing billing around the marketplace leads to delisting after written notice. Certification is optional and affects the badge, not your listing.

## Decisions needed before sending

1. Does the gate pass? Is there evidence of deals lost over missing integrations, and is the partner lifecycle staffed?
2. Will you publish the 15% ceiling? It is an irreversible public commitment, and the CFO must sign off.
3. What is T? I recommend deciding it after Q1 data. For the announcement, say "set before month 12".
4. Who are the named owners for admission, value split and disputes?

## Measure from day one

Lead with supply-side metrics:

- Active partners with a live listing.
- Time to first listing.
- Share of the catalog updated recently.
- Partner revenue concentration.

On the demand side, track the share of customers with at least one connector installed, and integrations per account, watching the 4+ cluster. Also track marketplace-attributed deal influence, which is inherently soft. Baseline against your own first quarter, because the AppExchange 91% is context, not a target.