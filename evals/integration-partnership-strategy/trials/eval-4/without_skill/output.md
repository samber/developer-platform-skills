# Partnership depth: Kitewell, Norsefield, Orbit Freight, AWS Marketplace

## Recommendation

| Partner | Depth | Why |
|---|---|---|
| **Kitewell** | 🟢 Deepest: build the productized integration, referral co-sell | Customer pull is real and the structure fits finance's rule. |
| **Norsefield** | 🟠 Explore only: blocked by finance until they rule | White-label puts them on our revenue, and the strategic risks are large. |
| **Orbit Freight** | ⚪ Shallowest: no engineering, one cheap demand test | No evidence of demand yet. |
| **AWS Marketplace** | ℹ️ A payment channel, not a partnership tier | Decide it on procurement demand, separately from the three above. |

A depth ladder helps here. Each rung adds cost and obligation:

0. Listing or mention.
1. Referral.
2. Productized integration plus co-sell.
3. Embedded or OEM.
4. Exclusivity or equity.

## Kitewell: go to rung 2

**Evidence for.** Their largest customers are asking for a real integration. That is customer pull, not partner enthusiasm. Their reps also sent us 6 opportunities and 2 closed.

**Caveat.** 6 opportunities is too small to call 33% a rate. Compare it with your direct close rate and ACV before you cite it. Also check whether the 2 wins came from reps or from customers who would have found you anyway.

**Structure.**
- Kitewell refers. We contract directly with the customer, so every contract stays signed by us and finance's rule holds.
- Pay a referral fee on closed-won deals, paid by us. Do not let them invoice or resell.
- Build the integration as a supported product, not another CSV workaround. Start with one workflow (inventory sync with robot task status), then expand.
- Ask for co-investment in return:
  - a named partner manager,
  - a listing in their app directory,
  - one joint case study,
  - a quarterly pipeline review.
- No exclusivity in either direction.

**Gate before committing engineering.** Get 3 or more named Kitewell customers to confirm they'd adopt the integration. Get a scoped build estimate. Define the metric you'll check at 2 quarters, such as joint-sourced pipeline or integration attach rate.

## Norsefield: hold at "explore"

**The blocker.** In a white-label deal, Norsefield sells forecasting to their customers under their brand. That is another company transacting on revenue tied to our product, which is the thing finance refuses. You could argue that Norsefield is simply our customer in a supply contract. Finance may not read it that way, and I can't tell from here.

**Step 1.** Ask finance and the CFO one question this week: "Is an OEM supply contract where Norsefield is our customer acceptable, or does your rule cover it?" Don't spend engineering time until they answer.

**Why caution even if finance agrees:**
- **Minimum commitments are attractive but not free.** Compare the number to $22M ARR. A small minimum buys little. A large one makes you dependent on a single counterparty.
- **Brand and customer ownership.** You lose the relationship with end users and the pricing power that comes with it.
- **Learning risk.** A large ERP vendor gets deep exposure to your forecasting logic. That can end in an in-house rebuild.
- **Cannibalization.** Customers in Norsefield's base who might buy forecasting from you directly will get it from them instead.

**Counter-offer that fits the constraint:** "Powered by Cassava" co-branded embedding or a deep integration, with Cassava contracting directly with the end customer and Norsefield earning a referral fee.

**If finance approves OEM, protect these terms:**
- a firm minimum annual commitment with a shortfall true-up,
- no exclusivity,
- a defined term with termination rights,
- a price floor,
- data and IP boundaries,
- a non-compete or non-replication clause,
- tiered support responsibilities.

## Orbit Freight: rung 0 to 1

You have zero overlap and no customer has asked. Warehouse and TMS are adjacent, so the pairing is plausible but unproven.

**Cheap test, about a day of work:**
1. Ask your top 20 pipeline accounts and 10 existing customers which TMS they run.
2. Count how many use Orbit.
3. Check whether any asked for yard, dock or shipment-status data.

**Trigger to move up:** 3 or more shared accounts or 2 customer requests. Until then, do an API-docs cross-link and a mutual mention, nothing more. Keep the relationship warm, since the people are good, but spend no engineering.

## AWS Marketplace: not a partnership tier

Your VP Sales is mixing up two things. Marketplace is a way for customers to buy: it uses their AWS commit and procurement. It does not add co-development, shared roadmap or joint selling, so it doesn't make you deeper with anyone.

**Finance fit (verify before listing):**
- In a direct SaaS listing, you should remain seller of record and AWS acts as billing facilitator.
- Resale through channel partners (a channel-partner private offer) would put another company in the transaction, so decline or disable that route.
- Confirm current fees, tax treatment and payment terms with finance. I believe the fee is a few percent, but check.

**Decision test.** Ask sales how many deals in the last 4 quarters stalled or were lost because the buyer wanted to pay through AWS commit. If the answer is a handful or more, list it. It is a modest lift, not a strategy. If the answer is zero, defer it. Do not let it displace the Kitewell build.

## Sequence, next 30 days

1. **This week:** send finance the Norsefield OEM question and the AWS seller-of-record question.
2. **Weeks 1-2:** get Kitewell customer confirmations and an engineering estimate.
3. **Weeks 1-2:** run the Orbit TMS overlap check.
4. **Week 3:** reply to Norsefield with the co-branded, direct-contract counter-offer, or the OEM terms if finance says yes.
5. **Week 4:** go or no-go on the Kitewell build, and on the AWS listing based on the stalled-deal count.

## What I assumed

- Norsefield's minimums are still informal, with no numbers.
- You run SaaS, so a Marketplace listing is technically feasible.
- Finance's rule is firm and not negotiable on an OEM exception.

If any of these is wrong, the Norsefield and AWS answers change most.