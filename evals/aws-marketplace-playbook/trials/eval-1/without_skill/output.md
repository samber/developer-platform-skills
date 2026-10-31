**Verdict:** two of three plan pieces are wrong, and the CRO's headline claim is unverified. Don't register the prod account. Don't start with pay-as-you-go (PAYG).

**Next action (15 min):** email your 3 largest bank prospects' procurement. Ask: "Does your AWS commitment (EDP/PPA) count Marketplace purchases, at what cap, and do you buy software through Marketplace today?" Everything below depends on those answers.

## Problem 1: the account (engineering plan)

- The AWS account you register becomes the permanent seller account. Its legal entity, tax, bank and KYC data attach to it. Changing it later needs AWS Support and is painful.
- Prod account means the seller identity, Marketplace IAM roles and finance data sit next to customer-facing infrastructure. Your bank customers' security reviews will ask about that.
- Do not use the Organization management account either.
- **Do:** create a dedicated member account in your Organization, for example `marketplace-seller`. Register that one.
- Metering and entitlement calls must use credentials from the seller account. Your app runs on GCP, so use a cross-account role with workload identity federation. Do not use long-lived keys.

## Problem 2: PAYG first, contracts later

- Your deals are 2-3 year commitments of $150k-400k ACV. Banks buy fixed commits, not monthly metered usage. PAYG fits a self-serve product, not your sales motion.
- A SaaS pricing model can't be switched in place. Subscription (usage) and contract are different products with different integrations: metering with `BatchMeterUsage` versus entitlements with `GetEntitlements`. "Switch later" means a new listing, a second integration and customers re-subscribing. Confirm this with your AWS Marketplace seller contact before you build.
- **Do:** build one SaaS contract listing. Sell real deals through private offers. Private offers carry custom price, multi-year terms (up to 5 years) and flexible payment schedules, such as annual invoices. The public listing can be a minimal anchor.

## Problem 3: "customers burn 100% of their EDP"

- This is not guaranteed. Marketplace spend counting toward EDP depends on each customer's own contract. Historically many contracts capped it, often around 25%.
- AWS has a "Deployed on AWS" designation that, as far as I know, gets better drawdown treatment. Your core app runs on GCP, and an edge plus backups on AWS probably doesn't qualify. Verify this with AWS before the CRO repeats it.
- **Do:** stop saying "100%" in sales material. Ask AWS for your eligibility. Ask each bank for its actual cap. If Ledgerline's drawdown is partial, the pitch weakens, and you should know that before you invest.

## Also check (not in your plan)

- **Fees:** AWS takes a percentage, roughly 3% on SaaS private offers last I knew. Verify the current schedule. At $150k-400k ACV that is about $4.5k-12k per year per deal. Price it in, or accept the margin hit.
- **Cash timing:** AWS pays you after the customer pays AWS, with disbursement lag. Model it against your invoicing.
- **Seller onboarding:** tax interview, bank details and identity checks. Budget 1-3 weeks, mostly waiting.
- **Value check:** Marketplace removes procurement friction. It does not shorten bank security reviews or vendor risk reviews.

## Plan

1. **Today, 15 min:** send the bank procurement question above. Ask your AWS account rep or ISV contact about "Deployed on AWS" eligibility for a GCP-hosted app.
2. **Week 1, about 1 hour of setup plus waiting:** create the `marketplace-seller` member account. Register as a seller there. Start the tax and bank steps.
3. **Weeks 1-4, about 2-4 engineer-weeks:** build the SaaS contract integration. It covers customer resolution (`ResolveCustomer`), entitlement checks, subscription notifications and a test in the AWS sandbox. Add the cross-account role from GCP.
4. **Weeks 4-6:** submit the listing and wait for AWS review. The wait is typically weeks and out of your hands.
5. **After approval:** cut the first private offer for the bank that said yes in step 1.

**Timeline:** "this quarter" is about 2 months. Registration, integration and review fit only if nothing slips. A first live private offer by year-end is possible but tight. Tell the CRO the realistic target is "listed and first offer sent", not "revenue booked".

**If step 1 shows weak demand or a low cap:** pause at step 2. Registration is cheap and reversible while the account choice is right. The integration is the real cost.

**Next:** run step 1 and paste me the bank answers. I'll turn them into a go/no-go for the CRO.