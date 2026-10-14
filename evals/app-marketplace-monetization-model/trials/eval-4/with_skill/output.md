# Sanity check: marketplace pricing-model menu (publish Monday)

**Verdict: ❌ don't publish as written.** Two of the four things you plan to promise can't be delivered, and two of the plan's rules go against the skill's guidance. All of it is fixable before Monday by changing the deck, with no new engineering.

I did not run the skill's one-question-at-a-time interview, because you asked for a sanity check. The open questions are at the end.

## 1. Metered usage can't ship ❌ (blocker)

- Your checkout does subscriptions and one-time purchases, plus coupons and trials.
- It has no usage-based billing. The skill says the rails cap the pricing menu, not the other way around (§5).
- The reference case is Salesforce AppExchange Checkout, which has the same capability set as yours. Its vendors simply can't offer consumption pricing.
- Per-seat is also unverified. It only works if seats are modelled as a quantity on a subscription. The checkout may or may not support that, so test it first.

**Fix, pick one before Monday:**
- **A. Cut metered from the deck** (recommended). Say "usage-based: roadmap". Ship what the checkout supports.
- **B. Keep metered, but on developer-billed rails.** The vendor bills usage itself. You then lose collection at source: you must audit self-reported revenue, and you need an anti-circumvention rule plus a delisting path. This is the weakest instrument in the skill's ranking.
- **C. Replace the checkout.** Not feasible by Monday.

## 2. Per-seat and flat: verify, then promise

- Flat subscription is supported.
- One-time add-ons are supported.
- Per-seat needs a 30-minute test of quantity-based subscriptions on your commerce vendor's checkout. Don't promise it until that passes.

## 3. Price variants under one product ❌ (change it)

- The skill's rule: model each pricing tier as its own product object, never as price variants of one product.
- Variants of one product look identical on customer invoices. A customer can't tell "Pro" from "Starter" on a bill, which causes disputes and support load.
- A tidy catalog is a display problem. Solve it with a catalog grouping layer, such as a parent listing that links the product objects. Don't solve it by collapsing the billing objects.
- Check before changing: if your commerce vendor's invoice shows the variant name, the risk is lower. The skill says to go with separate products regardless, because the cost of doing so is small.

## 4. Mandatory 14-day free trial ❌ (change it)

- The skill says to recommend defaults such as free trials or an entry plan, and never mandate them. That's how platforms shape pricing without owning vendors' pricing decisions.
- A forced trial doesn't fit one-time add-ons at all, since you can't trial a single purchase.
- It breaks metered and per-seat models, where a trial means unbilled consumption or seats.
- It would be a day-one partner complaint, because vendors lose control of their own pricing.

**Fix:** make it a recommended default. The checkout already supports trials, so you can pre-fill 14 days and let vendors change it or turn it off. Offer it as a one-click default, and tell the head of partnerships that you can still track adoption of it.

## 5. Gaps your plan doesn't mention

These are the skill's measurement gates. Any of them can undermine Monday's publication.

1. **Merchant of record.** Are you marketplace-billed or vendor-billed? Your commerce vendor's checkout implies marketplace-billed. Say so in the deck, and assign tax, chargebacks and payouts to a party explicitly. No transaction type should be left ambiguous.
2. **Take-rate.** Your deck is silent on the fee. If the rate isn't decided, stop and settle it first. This skill executes that decision, it doesn't make it. Publish the notice period for fee changes with the schedule. The usual pattern is six months.
3. **Payout timeline.** Publish the real sale-to-bank time, not "monthly". Holds typically add 30–60 days.
4. **Tax split.** Publish a jurisdiction-by-jurisdiction split, reviewed by counsel. Facilitator and VAT rules attach by law regardless of your billing posture.
5. **Entitlement and reporting.** A monetization stack is at least three systems: payment, entitlement (licences) and vendor revenue reporting. Does your commerce vendor cover the last two? If not, "vendors can sell" is only a third true.
6. **Anti-circumvention.** If vendors can route billing around you, the share erodes. Add the rule and the delisting path.

## Revised launch-deck promise

> **Available at launch:** flat subscriptions, one-time add-ons, and per-seat (once verified). Coupons are available. Free trials: a recommended 14-day default.
> **Roadmap:** usage-based pricing.

## Before Monday: checklist

1. Cut or reword the metered promise (§1).
2. Test per-seat as quantity on a subscription (§2).
3. Switch to one product object per plan, grouped in the catalog (§3).
4. Reword the trial rule from "required" to "recommended default" (§4).
5. Confirm merchant of record, take-rate, payout timeline and tax split before they go in the deck (§5).

## Questions I'd normally ask first

1. Is the take-rate already decided (level, tiers)?
2. Do you already bill these customers on an invoice cycle?
3. Is per-seat truly required at launch, or just promised in the deck?
4. Where do buyers sit (US, EU, elsewhere), and are any of them consumers?
5. Will you absorb chargebacks and fraud losses, or pass them to vendors?
6. Are any existing apps already billing customers directly?

Answers to questions 1, 5 and 6 would change the merchant-of-record advice above.