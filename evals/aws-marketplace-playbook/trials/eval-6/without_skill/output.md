# Review of the CFO's two AWS Marketplace ideas

Yes, there are problems with both. I haven't checked these against AWS's current seller terms, so the figures marked "verify" need confirming in the Seller Guide before anyone acts.

## Idea 1a: "+3% so the fee is covered"

1. **The math is off.** To net the same amount after a fee `f`, the price must rise by `1/(1-f) - 1`.
   - A 3% fee needs about +3.1%.
   - A 10% fee needs +11.1%.
   - A 20% fee needs +25%.
   - So +3% only works if the fee on that listing type is exactly 3%. Verify which rate applies to each offer type (public vs private, SaaS vs AMI or container). AWS has changed these rates.
2. **Public price is rarely the price paid.** Most Marketplace revenue closes through private offers, usually at a lower fee. Raising the public price by 3% over-recovers on those deals, or does nothing, because the negotiated price is what the buyer pays.
3. **It's a real price increase for public buyers.** Buyers burning down AWS commitments (EDP/PPA) are less price-sensitive, but they compare against your direct price. Decide on purpose whether Marketplace carries a premium over direct.

## Idea 1b: "fee comes out of the rep's commission"

1. **It's a comp plan change.** Applying it to deals already in flight or already closed is a retroactive pay cut. That creates legal exposure (employment law and plan terms), and in France it needs formal notice and often consultation. Get HR and legal review. Make any change prospective only, with written notice.
2. **It double-recovers the fee** if combined with 1a. The price bump and the commission cut both claim to cover the same cost.
3. **It steers reps away from Marketplace.** Reps will push deals off-channel, or hold back on Marketplace deals that buyers want because they burn down AWS commitments. The fee is a channel cost, so it belongs in channel margin, not in individual pay.
4. **A cleaner option:** pay commission on net revenue after the fee, consistently for every channel. Or keep commission on gross and account for the fee in the channel P&L. Either way, write it into the plan, apply it from a future date, and state the rule once.

**Recommendation:** pick one mechanism. Either raise the price (with the correct gross-up per offer type) or change the commission basis, not both.

## Idea 2: "Update the AWS public price on 1 March for existing subscribers"

1. **You probably can't do it on the same day.** As I recall, AWS requires advance notice of a price increase to existing subscribers, about 90 days, taking effect on the first of a month. Verify the exact rule.
   - Counting back from 1 March 2026-10-31 (today) gives a notice deadline of about **1 December 2026**. That's roughly a month away, so it's feasible but tight.
   - New subscribers can usually be moved to the new price sooner than existing ones.
2. **Contract-based SaaS subscribers are locked until term end.** A public price change doesn't reprice a running annual contract. It applies at renewal or to new contracts. Only usage-based or hourly subscriptions reprice mid-term.
3. **Check your own EULA and contract terms.** Price-protection or price-lock clauses may block an increase even where AWS allows it.
4. **Private offers are unaffected.** Existing private-offer customers keep their negotiated price until the offer ends. Plan renewals separately.
5. **Two increases is worse than one.** If the 3% fee gross-up and the across-the-board increase ship separately, existing customers get two notices. Fold both into one change and one communication.
6. **Align direct and Marketplace.** If direct customers move on 1 March but Marketplace customers move later, you create a temporary price gap that buyers will notice.

## What I'd do

1. Confirm the current fee rate for each offer type and the exact price-change notice rule.
2. Decide the Marketplace-versus-direct price policy: parity or an explicit premium.
3. Fold the fee gross-up into the 1 March increase, calculated per offer type.
4. Send the AWS price-change notice by about 1 December, and plan customer communications.
5. Handle commission separately, prospectively, after HR and legal review.
6. List the existing contract and private-offer cohorts with their renewal dates, because those are who actually gets repriced.

To tighten this, I need three facts from you: which listing types you use (SaaS contract, subscription, AMI), what share of Marketplace revenue closes via private offers, and whether your EULA has price-lock language.