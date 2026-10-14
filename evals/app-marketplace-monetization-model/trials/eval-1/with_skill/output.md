**Next action:** before any billing build, get leadership to sign off on the take-rate architecture. The skill's step 1 says to stop without it. "20%, maybe 25%, we'll land on it later" is a range, not a decision.

Everything below builds on one assumption. The billing code treats the rate as a configuration value, so the number can change later without a rebuild. The rate itself is still a strategy decision.

I could not run the 10-question interview in a single response. Where an answer was missing, I used a default and marked it **[ASSUMED]**. Confirm each one.

---

# Calvetta paid-apps monetization design (draft v1, 2026-10-03)

## 0. Decisions needed before build

| # | Decision | Owner | Why it blocks |
|---|---|---|---|
| D1 | Take-rate level, tiers, zero-take-or-not. Run `connector-marketplace-strategy`. | Leadership | The fee stack, waiver and enforcement all hang on it. |
| D2 | Scope: what counts as a "paid app". See §4. | You and legal | It decides which revenue the take applies to. |
| D3 | Buyer geography and consumer exposure (interview Q5). | Finance and legal | It sets the tax map in §8. |
| D4 | Hard date: is Q2 2027 (about 26 weeks from today) fixed, or a target? | Leadership | A fixed date forces managed rails and the simplest posture. |

**D1 caveat.** Your 20-25% sits above the sourced B2B benchmarks:
- Salesforce charges 15% (25% only for OEM).
- Shopify charges 15% above $1M.
- Atlassian charges 15-17% on Forge and 20-25% on its legacy Connect framework.
- Apple and Google charge 30%, with 15% small-developer tiers.

Both 15% and 30% are used as developer-acquisition levers. Calvetta is introducing a take on 310 developers who have paid nothing so far, so it will run into more circumvention pressure than a marketplace that charged from day one. Put that point to leadership as part of D1.

## 1. Take-rate architecture

Not decided. The design treats the rate as one config value, with room for tiers and a waiver threshold. The notice commitment in §9 covers later changes.

## 2. Merchant-of-record posture

**Marketplace-billed (Calvetta is merchant of record) for all paid apps.**

- Leadership's "take a percentage" rules out developer-billed. Under developer-billed, the only way to collect a percentage is self-reported revenue. That is the weakest instrument and the easiest to circumvent.
- Collection at source is the only mechanism that does not depend on developers reporting honestly.
- **[ASSUMED]** Calvetta already invoices its ~900 customers on a recurring cycle for the core product (interview Q2). If so, **consolidate app charges onto the existing Calvetta invoice.** This is the cheapest build. Shopify works this way.
- **[ASSUMED]** No developer is currently billing customers off-directory (Q7). The 310 connectors are free, so there is no legacy population. **Delete the "configurable per app" posture.** If Q7 turns out to be yes, see D2.

| Item | Owner |
|---|---|
| Customer invoice and dunning | Calvetta |
| Chargebacks, refunds, disputes | Calvetta (absorbed, then managed) |
| Sales tax and VAT | Calvetta, split per §8 |
| Entitlement and licensing | Calvetta |
| Developer net payout | Calvetta pays out after hold |
| Product support and refund eligibility rules | Developer (Calvetta decides refunds) |

This table gives each transaction type one owner for tax, chargebacks and payout, which is what measurement gate 1 requires.

**Loss appetite (Q6) is not answered.** Marketplace-billed means Calvetta carries chargebacks and fraud losses. If leadership will not accept that, this posture is wrong. Ask them.

## 3. Billing rails

- **Customer charge:** Calvetta's existing billing stack, as a line item on the existing invoice. **[ASSUMED]** it can add third-party line items and per-app tax lines. Check this first. It is the largest unknown in the Q2 plan.
- **Developer payouts:** a managed payout rail. If you use Stripe Connect, take the **marketplace-shaped bundle**:
  - express dashboard
  - platform collects fees
  - platform carries losses
  - separate charges and transfers, because a hold window rules out destination charges
- **Do not mix dials.** Combinations outside the two bundles are either blocked or silently move liability onto Calvetta.
- **Do not use `on_behalf_of`.** It makes the developer merchant of record, which contradicts §2.
- **Three systems, not one.** Payment is the visible one. Entitlement (who is licensed) and developer revenue reporting are the other two. Scope all three for Q2, or the first paid install has no license record and no statement.

**Unit economics.** Using Stripe UK figures from the reference (re-verify; they vary by region): about £1.60 per active developer per month, plus 0.25% and £0.20 per payout. At a 20% take, the flat fees (about £1.80) are covered once a developer grosses roughly **£9 a month**. That is easy to clear, but only for developers who actually sell. Model it per active developer: 310 listings will not all become paid apps.

## 4. Fee stack

Instruments, in order of priority:

1. **Revenue share netted at source.** Calvetta deducts its cut before payout. This is the primary instrument. The rate comes from D1.
2. **Processing pass-through, shown as a separate labeled line.** This keeps the headline take comparable with competitors. Do not fold card or ACH cost into the percentage.
3. **Flat program fees, optional.** Possibly a per-app security-review fee, if you decide to charge one. Keep it small: it should cover review cost and filter spam, not deter developers. Skip it if you have no review cost to recover.
4. **Audited self-reported share: deleted.** It only exists under developer-billed.

**D2, scope of "paid app".** The risk to close is the free-connector-plus-paid-upgrade pattern, where a free directory listing sells upgrades on the developer's own site. Decide one rule and publish it:

- **(a)** The take applies only to purchases made through the marketplace. Simple, but easy to route around.
- **(b)** Free listings may not sell in-product upgrades that unlock Calvetta-connected functionality outside marketplace billing. Stronger, but it needs review and enforcement effort.

I recommend (a) at launch with (b) as a published terms clause, backed by §9 enforcement.

## 5. Developer pricing-model menu

**[ASSUMED]**, pending Q3. Launch with:

- flat subscription
- per-seat, as a quantity on a subscription
- free with paid tiers

**Defer one-time and usage-based.** First confirm Calvetta's invoice and entitlement stack supports each. Rails cap this menu, not the other way round. Usage-based needs metering, which is a maturity ladder with several rungs. Scope only the rung developers actually ask for.

Two rules to adopt:
- Model each tier as its own product object, never as price variants of one product.
- Recommend defaults (a trial, an entry plan) without mandating them.

## 6. Waivers and incentives

**Default shape: a revenue-exemption tier, but do not copy the $1M anchor.**

Sourced programs use $1M. At Calvetta's scale that would waive the take for essentially everyone. The reach is about 900 customers, so a strong app might look like this (illustrative, not data): $100/month × 30% adoption × 900 customers ≈ $324k a year. Under a $1M exemption, no developer would pay a take at 20-25% for years, and the revenue you are building billing for would not exist.

Decide the threshold deliberately, as part of D1. Options:
- scale it to your own ceiling
- use a shorter annual-reset window instead of lifetime
- skip a revenue exemption and use a behavior-based discount, such as a lower rate for subscriptions over one-time

**Default eligible developers in automatically.** Do not require manual enrollment. Apple and Google both require it, and developers who miss it silently pay full rate.

**Delete migration incentives** unless Q7 turns out to be yes.

## 7. Payout design

- **Default: monthly cycle plus an explicit hold window**, 30-60 days sized to your refund exposure.
- **Preferred if Q2 is yes:** payouts ride the existing invoice and settlement cycle. This is near-zero marginal build.
- **Annual contracts matter.** If customers pay annually, define when a developer is paid: on collection, not on invoice.
- **Publish the honest end-to-end sale-to-bank timeline.** The sourced lags run to roughly twice the "monthly" headline once holds and escrows stack. Plan cash flow on that number.
- **Do not offer rolling or instant payouts at launch.** Layer them on later only if small developers cite cash flow as the blocker.
- **Minimum payout threshold:** set it small. It is not the lever developers feel; the hold window is.
- **Cross-border:** if any developer is outside your payout currency, Calvetta owns FX and rail choice. Budget for it.

## 8. Tax layer (not tax advice; route through counsel before publishing)

Merchant-of-record status and tax-collector status are legally distinct. Marketplace-facilitator law can make Calvetta liable for tax regardless of §2.

The split below is a draft to publish, pending D3:

| Jurisdiction | Who collects and remits |
|---|---|
| US states with facilitator laws | Calvetta collects, calculates and remits. Whether SaaS is taxable varies by state, so counsel must confirm each state. |
| EU B2B | Reverse-charged to the business buyer. Light version of the deemed-supplier rule. |
| EU or other consumer buyers, if any | Deemed-supplier VAT. Calvetta owns it. This is a heavier build; confirm none exist. |
| Rest of world | Decide per country. Do not publish a single "we handle tax" toggle. |

**Silent-failure trap.** Automatic tax calculation with no active registration in a jurisdiction collects $0 and returns no error. It cannot be corrected retroactively. Monitor tax collection as its own system, and do not infer it from payouts.

## 9. Enforcement and notice

- **Anti-circumvention rule with a delisting path.** Routing billing around the marketplace to avoid the share violates the terms, and the penalty is removal. This is more necessary here than elsewhere, because you are adding a take to developers who paid none before.
- **Notice commitment: six months for standard-rate changes**, with unfavorable changes deferred and favorable ones accelerated. Publish it with the fee schedule, before the first paid listing goes live.
- The 310 existing free connectors are unaffected. State in writing that free apps pay no share.

## 10. Measurement gates

Pass criteria:
1. Merchant-of-record posture is stated per app population, with tax, chargeback and payout ownership assigned. §2 does this.
2. Every fee instrument names its collection mechanism, enforcement pair and notice commitment. This depends on D1 and §9.
3. Developer docs publish the sale-to-bank timeline and the tax split. Blocked on §7 hold sizing and §8 counsel review.

Post-launch, track against your own first quarter:
- net take revenue against billing-ops cost
- median sale-to-bank days against the published number
- dispute rate, with losses attributed to the owner in §2
- waiver coverage among eligible developers
- tax-registration coverage of volume
- circumvention incidents

## Risks to the Q2 date

1. D1 is still open. The build can start on rate-agnostic parts (invoice line items, entitlement, payout rail), but not the fee schedule or waiver.
2. Counsel review of §8 has a lead time. Start it now.
3. If Calvetta's billing stack cannot add third-party line items, the build is much larger than the invoice-consolidation path assumes.

## Open questions, ranked

1. Does leadership accept chargeback and fraud losses (Q6)?
2. Can your invoice stack carry third-party line items with per-app tax (Q4)?
3. Where do buyers sit, and are any consumers (Q5)?
4. Which pricing models must developers offer (Q3)?
5. Are any of the 310 developers already selling paid upgrades off-directory (Q7)?

**Next:** send D1 to leadership today, and answer questions 1 and 2 above. Both change the design the most.