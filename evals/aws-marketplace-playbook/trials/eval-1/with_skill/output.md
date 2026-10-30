# Ledgerline on AWS Marketplace: sanity check and plan

**Verdict: list, but change three of the four planned decisions.** The CRO's pitch is wrong for your architecture. Engineering's account choice and pricing model are both irreversible mistakes.

## 1. Assumptions

I couldn't ask questions, so each gap below is an assumption. Correct any that are wrong.

- **A1.** "This quarter" means the calendar quarter ending 2026-12-31. Today is 2026-10-31.
- **A2.** The application and control plane run on GCP. Only the API edge and backups are on AWS.
- **A3.** The AWS Organization may contain accounts under more than one legal entity. I haven't verified this.
- **A4.** No named deal has asked for Marketplace yet.
- **A5.** Your price book is seats or tiers with no metered overage. Tell me if that's wrong.
- **A6.** No reseller is required, and buyers are mostly US or EU banks.

## 2. Fit verdict: Transact, no commit

"Customers can burn 100% of their EDP with us" fails on two counts.

- **The badge.** Only products with the Deployed on AWS badge may still retire EDP or PPA commitments.† The badge requires the application plane and control plane on AWS. It also requires every third-party service that touches customer data to be on AWS, with only CDN, DNS and corporate identity exempt. Your edge and backups on AWS don't offset a GCP application plane.
- **The percentage.** Even with the badge, the share of a commitment that Marketplace can retire is set in each buyer's private AWS contract. AWS publishes no figure. Practitioners commonly cite 25%, not 100%.

**What to do differently**
- Ban "burn your EDP" language in decks, emails and offers.
- Pitch what is true:
  - one AWS invoice
  - pre-approved procurement terms
  - faster vendor onboarding at banks that already buy through AWS
- Ask each buyer's AWS account team what Marketplace spend counts toward their commitment. Don't promise a figure.
- Treat a fully-on-AWS edition as a separate strategic decision. It is a re-platform, so don't commit to it for this quarter. Revisit it only if named bank deals explicitly depend on commit drawdown.

**Tell the CRO now.** If a bank signs expecting commit burn and doesn't get it, you lose trust and possibly the deal. The framing is wrong, but the channel can still be worth using for procurement speed.

## 3. Irreversible-choice register

| Choice | Engineering's plan | Recommendation | Owner / date |
|---|---|---|---|
| **Seller account** | Prod AWS account inside the Organization | **Don't.** It becomes seller of record forever and mixes Marketplace finance with infrastructure billing. A member account also inherits the management account's legal entity for tax. Create a fresh standalone account under the Ledgerline legal entity, or use an org whose accounts all share one entity. Check A3 before choosing. | Finance + eng lead, before registration (target 2026-11-04) |
| **SaaS pricing model** | Pay-as-you-go (subscription), switch later | **Don't.** The model is fixed once the product is published to Limited, so switching later means a new product. You sell 2-3 year contracts at $150-400k, so use **SaaS contract**. Move to contract with consumption only if overage is in your price book (A5). | CRO + eng, before Limited |
| **Dimension API names** | Not discussed | Names never change, and custom dimensions added for offers can't be removed. Design them from your price book before building. | Eng lead, before build |
| **Reseller authorizations** | Not discussed | None planned. Published authorizations can't be edited or extended, only deactivated. | n/a |
| **Auto-renewal opt-out** | Not discussed | Seller opt-out is irreversible, and the buyer then needs a new offer. Decide per deal. | Offer owner |

**Why not pay-as-you-go:** subscription is for pure metered usage and needs hourly metering per customer. It also can't support installments or auto-renewal. It doesn't fit your deal shape.

## 4. Timeline to first deal (counted from 2026-10-31)

I haven't verified the durations below.† The plan is 3-6 weeks from registration to Public, and registration and engineering run in parallel.

| Step | Target | Note |
|---|---|---|
| Pick the account and legal entity, open the standalone seller account | By 2026-11-04 | Gated on the A3 check |
| Register: tax interview, bank, USD disbursement method, verification, KYC | 2026-11-04 to about 2026-11-18 | KYC can take up to 2 weeks. Editing details after approval restarts it. |
| Build the integration (fulfillment, entitlement checks, EventBridge events) | In parallel, 2026-11-04 onward | Needs engineering weeks. I don't know your availability. |
| Publish to Limited at a reduced test price, allowlist test accounts, cancel every test subscription | About 2026-11-25 | |
| Request Public at the real price | About 2026-11-30 | Review takes 7-10 business days† from the request. |
| Public approved | Best case about mid-December | Realistic range is 2026-12-05 to early January. |
| First private offer | Mid-December at the earliest | No private offer is possible before one paid public listing exists. |

**Say this plainly to the CRO.** A first Marketplace signature before 2026-12-31 is possible only if everything goes right, so don't promise it. The first offer is more likely in Q1 2027. Never promise a signature date earlier than review allows.

**If a renewal date falls before Public can pass:** extend the customer briefly on your own paper. At the next renewal, set the renewal flag (see section 5).

## 5. First-offer plan

**Pick the right first deal.** Choose a deal already late-stage outside Marketplace, with a buyer who wants AWS billing. Ideally it's an existing customer renewing, which earns the lower renewal fee.

**Buyer pre-check.** Get each item in writing from the bank's cloud or procurement team.
1. The 12-digit AWS account that will own the subscription.
2. Whether they run a Private Marketplace. If yes, extend the offer to the buyer account and the Private Marketplace administrator account, and ask the administrator to approve the product.
3. Payment by invoice, not card.
4. Any active agreement for the same product in that account.
5. What they expect the purchase to retire against their commitment. Tell them you don't have the badge.
6. Currency. Private offers support USD, EUR, GBP, AUD and JPY.† Public offers are USD only.
7. Country, if you geo-target the offer.

**Fees.**† Fees are charged on total contract value, pre-tax.
- A new private offer pays 3% under $1M and 2% from $1M to $10M. Your 2-3 year terms put TCV at roughly $300k-$1.2M, so most offers land at 3%, and 36-month deals at the high end of your range fall into 2%.
- A renewal pays 1.5% at any size. Flag existing customers moving onto Marketplace as **Existing Customer Moving to AWS Marketplace**. Moving a public Marketplace subscriber onto a private offer is not a renewal.
- Don't raise the public price to recover the fee. Keep the public price at list and discount in private offers.

**Payment terms and settings**
- Invoice by installments, for example annual, which needs the contract model. Only one invoice date may fall before acceptance.
- Net terms run Net 15 to Net 120† and are fixed after acceptance. They move your cash by the same number of days.
- Set the expiry to about 30 days, aligned to the buyer's quarter-end, and extend rather than issuing long-dated offers.
- Decide auto-renewal before acceptance. Once turned off, it can't come back.
- Use the Standard Contract for AWS Marketplace as the EULA to shorten legal review. Banks will probably want their own paper, and a custom EULA accepts up to five documents.

**Sales team.** Pay reps the same commission and quota credit as direct deals, on acceptance. Deducting the fee from commission routes deals around Marketplace.

## 6. Co-sell rung for this quarter

**This quarter:** ACE, but with a caveat. Submit your own opportunities with real AWS consumption, and answer AWS-referred opportunities within 5 business days. The caveat is that ACE wants net-new AWS usage, and your app runs on GCP. Entries "for visibility only" count toward no threshold, so don't expect much AWS-side pull. AWS sellers rarely prospect for an unknown ISV, so expect field engagement 6-12 months after listing.

**Next rung up, when to climb:**
- **FTR (Foundational Technical Review)** is a 2-4 week architecture and security review. Do it once a real deal is in flight.
- **ISV Accelerate** requires all of these:
  - a GA listing
  - Validated status
  - a Payee Central account
  - 5 launched and 15 qualified opportunities in 12 months
  - one trained seller
  - $2,000† of AWS revenue

  AWS invites you once you qualify. With a GCP app, hitting these thresholds is unlikely soon, so don't plan around it.

**Skip the badge submission for now.** Your architecture doesn't qualify.

## Do these next, in order

1. Tell the CRO the EDP claim is not true for Ledgerline, and agree the replacement pitch (one invoice, procurement speed).
2. Stop engineering from registering with the prod account. Confirm the legal-entity situation across your AWS Organization (A3).
3. Choose a standalone seller account under the Ledgerline legal entity and start registration in parallel with the build.
4. Switch the listing plan to **SaaS contract**, and design dimensions from your price book.
5. Name one late-stage bank deal as the first offer, and run the buyer pre-check with them.

All AWS fees, durations and thresholds marked † come from the AWS Marketplace Seller Guide and change without notice. Verify them against the current guide before quoting them to anyone. The Deployed on AWS commit-drawdown reading is practitioner interpretation of AWS's wording.