# AWS Marketplace: Kestrel Bank and Pinemoor

**Do first:** (1) email Kestrel's cloud team the Private Marketplace questions below. (2) Tell your AE the 200→150 cut cannot happen mid-term.

I can't see either offer, so each cause below is a ranked hypothesis, not a diagnosis. The playbook's buyer pre-check lists these as the usual causes.

## Problem 1: Kestrel Bank, "product not available in your private catalog"

**Most likely cause: Kestrel runs a Private Marketplace (PMP).** The message refers to a *private catalog*, which is how a PMP shows up. A bank is a typical PMP user. In a PMP, a private offer is not enough on its own. The product must also be approved by Kestrel's PMP administrator.

**Steps**

1. Ask Kestrel's cloud or procurement team, in writing:
   - Does your organization run a Private Marketplace?
   - Which account is the PMP administrator account?
   - Is `4411-2290-7718` the account that will own the subscription (a linked or management account)? Is it the same account whose catalog the buyer's user is browsing?
2. If a PMP exists:
   - Extend the offer to the buyer account **and** the PMP administrator account.
   - Ask the administrator to approve the product in the PMP.
   - Buyers and product cannot be changed on an existing offer. If you can't add the administrator account to the current offer, issue a new offer with both accounts. Check this in the seller console before promising a fix.
3. If no PMP exists, check the other causes in this order:
   - **Wrong account.** The ID must be the account that owns the subscription. A different account in the org, or a sandbox account, will not see the offer.
   - **Geo-targeting.** If you restricted countries, the buyer account's own location must be in the list, or the offer can't be accepted.
   - **Expiry.** Offers close at 23:59:59 UTC on the expiry date. You can extend an expired offer. If it has installments, update the schedule too, because only one invoice date may fall before acceptance.
4. Confirm two more things before resending:
   - Kestrel pays by invoice, not card.
   - If Kestrel expects this purchase to retire AWS commit, your product holds the Deployed on AWS badge and Kestrel's AWS account team has confirmed it. Never promise a percentage.

## Problem 2: Pinemoor, "You already have an active contract"

**This error is expected.** Pinemoor already holds an agreement for this product in that account. A second new offer is blocked. Use an agreement-based replacement offer instead.

### 2a. Add 50 seats: allowed

1. In the Agreements page, issue a **replacement offer** from Pinemoor's current agreement. It takes effect on acceptance and cannot be future-dated. The seller of record cannot change.
2. **Re-include both unbilled annual installments in the replacement.** Acceptance cancels the old agreement's pending payments. If you leave them out, you lose both payments.
3. Decide how the 50 extra seats are billed:
   - Fold them into the two remaining annual payments, or
   - add a charge on acceptance.
   
   Only one invoice date may fall before acceptance.
4. Set net terms again. The old terms were frozen on the accepted offer, and the new offer carries its own. They apply to every charge in the offer and are fixed once accepted.
5. Don't amend a *public* agreement for this. That turns it private and ends its auto-renewal.
6. After acceptance, check that your product processes the change event and raises seats from 200 to 250 on that license ID. Entitlements must be checked on every customer change.

### 2b. Drop the other module from 200 to 150 seats: not possible mid-term

- Contract buyers can upgrade but never downsize mid-term. They shrink at renewal.
- A replacement offer cannot carry a lower quantity. This holds whether the module is a dimension of the same product or a separate listing, because the rule is about the agreement.
- Cancelling the agreement instead is the wrong tool. A cancellation you request goes to the buyer, who has 7 days† before it auto-approves. It would also end the whole contract, not one module.

**What to tell the AE**

- Hold the module at 200 seats until renewal.
- At renewal, issue a **future-dated renewal offer** at 150 seats, starting the day after the current agreement ends.
- If the AE needs to give Pinemoor something now, make it a price concession on the 50 new seats or on the renewal. Don't offer a seat cut.
- Don't bundle the cut into the upsell offer. It will fail, and it signals to the buyer that the deal is negotiable.

**Questions I couldn't answer**

- Is the module a separate Marketplace product or a dimension of this one? This changes the paperwork, not the downsizing rule.
- Is the 3-year contract on a public listing or a private offer? Moving a public subscriber onto a private offer is not a renewal for the fee purpose.

## Assumptions

- Pinemoor's contract is a SaaS contract (annual installments, 3-year term), not subscription billing.
- Pinemoor pays by invoice.
- Kestrel's account ID was typed correctly. Verify this first, because it's the cheapest check.
- You are the ISV seller of record, with no reseller (CPPO) in either deal.

## Fees and cash

The playbook doesn't say which fee tier a replacement offer falls under. Don't quote a fee on the 50 seats until you've checked the Seller Guide. For reference:

- New private offers pay 3% under $1M†.
- Renewals pay 1.5%† when the renewal flag is set.
- The fee applies to total contract value whatever the payment schedule.

## Footnote

† Figures (net terms, 7-day cancellation window, fee tiers) come from the AWS Marketplace Seller Guide and change without notice. Verify against the current guide before quoting any of them to a customer or to your AE.