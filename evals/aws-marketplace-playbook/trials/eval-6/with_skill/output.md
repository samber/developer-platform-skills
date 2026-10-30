**Short answer: yes, both ideas have problems. Idea 1 breaks two ways, and idea 2 may not work as she expects.** Figures marked † come from the skill's AWS reference and can change. Check them against the current AWS Marketplace Seller Guide before you quote them. I didn't check them against live AWS docs.

## Idea 1a: raise the public price 3% to cover the fee

❌ **Don't do it.** The playbook says: "Never inflate the public price to recover the fee."

- **A price rise locks you in.** A public price increase freezes every further pricing update for at least 90 days†. It also reaches existing subscribers only after AWS notifies them. A 3% bump to cover fees uses up your one move for a small gain.
- **It's bad arithmetic.** The public fee is 3%†, charged on total contract value. To net the same cash you'd need roughly +3.1%, not +3%. That is a rounding error, and it makes Marketplace look dearer than your direct price.
- **Public price is the wrong place for it.** The listing is a procurement rail, not a demand channel. Revenue comes from private offers to buyers who already spend on AWS. Keep the public price at list and discount in the private offers. Almost nobody pays the public price, so inflating it doesn't recover the fee on the deals that matter.
- **The fee is smaller than she thinks on the deals that matter.** New private offers pay 3% under $1M, 2% up to $10M, and 1.5% above that†. Renewals pay 1.5%† at any size, if you flag them **Existing Customer Moving to AWS Marketplace**. So the real cost on most deals is 1.5–3%†, not a flat 3%.

**What to do instead:** treat the fee as a cost of sale in margin planning. If you must recover it, use a Marketplace-specific price in the private offer for that buyer, not the public list price.

## Idea 1b: deduct the Marketplace fee from the rep's commission

❌ **Don't do it.** The playbook says: "Pay reps the same commission and quota credit as direct, on acceptance. A fee deducted from commission routes deals around Marketplace."

- Reps will steer buyers to direct contracts and avoid Marketplace. That kills the deals where the buyer's procurement, AWS commit, or co-sell makes Marketplace the faster path.
- It works against ACE co-sell. You want AWS-referred and ACE-registered deals to close through Marketplace.
- The fee is a company cost of sale. Charging it to reps shifts a margin decision onto individuals.

**What to do instead:** pay full commission and quota credit on acceptance, and budget the fee at company level. If margin is the worry, set the discount floor for Marketplace private offers so it already includes the fee.

## Idea 2: raise prices on 1 March and update the AWS public price the same day for existing public subscribers

⚠️ **This won't work as stated.** Three problems:

1. **Subscribers aren't updated on your date.** Public price increases reach existing subscribers only after AWS notifies them. You don't control that timing. Your price change on 1 March does not mean subscribers pay the new price on 1 March.
2. **The 90-day freeze.** After the increase, every further pricing update is frozen for at least 90 days†. If the 1 March change has an error, or you need a correction, you can't fix it for a quarter. Her plan has no slack for that.
3. **"Across the board" is wrong for contract deals.** Signed contract terms are frozen on the accepted offer. A price rise doesn't reprice signed private-offer agreements. It only touches the public price and the subscribers on it. Those subscribers are likely few, because public listings draw little inbound. Check how many existing public subscribers you have before building a date around them.

Also note the ordering rule: **lower prices first, then raise.** If any dimension needs a cut as part of the new price book, do that before the raise, because after the raise you can't touch prices for 90 days†.

**What to do instead:**
- Set the new public price with at least 4–6 weeks of lead time before 1 March, so AWS's notification to subscribers can land before or near your direct-price date.
- Don't promise subscribers a 1 March effective date. Promise "after AWS notifies you."
- For contract customers, the new price takes effect at renewal. Use the renewal offer, with an uplift set in the auto-renewal terms. Finalize the uplift before the adjustment deadline, or the default applies.
- Check dimension names and the price book before submitting. Dimension API names never change, and custom dimensions added for offers cannot be removed.

## Questions to settle before you act

1. How many active public subscribers do you have, and how many deals are private offers? This sizes how much idea 2 matters.
2. Which Marketplace pricing model do you have (contract, contract with consumption, subscription)? It decides how price changes reach buyers.
3. Are any upcoming renewals due before 1 March? If so, flag them as renewals so they pay the 1.5%† fee, not 3%†.
4. Do you have ACE co-sell deals in flight? Those are the ones commission deductions would hurt most.

## Recommended answer to the CFO

- ❌ No public price inflation, and no commission deduction.
- ✅ Budget the 1.5–3%† fee as cost of sale, and build it into the discount floor for Marketplace private offers.
- ✅ Pay reps full commission and quota credit on acceptance.
- ⚠️ Submit the price rise early. Don't promise 1 March to existing subscribers, and don't plan another price change for 90 days† after it.
- ✅ Move contract customers to the new price at renewal, through the private-offer renewal terms.