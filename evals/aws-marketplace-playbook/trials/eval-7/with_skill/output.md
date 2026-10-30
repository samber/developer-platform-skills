# AWS Marketplace: should you list?

**Verdict: skip for now.** Revisit when a named customer deal asks for it.

## Assumptions

I couldn't ask follow-ups, so these are my assumptions. Correct any that are wrong.

- ℹ️ **Hosting:** Vercel and Fly.io mean the app and control plane run off AWS. Your database host and any model API are probably off AWS too.
- ℹ️ **Buyers:** individual devs and small teams paying by card. None of them hold an AWS commitment.
- ℹ️ **Sales:** you have no sales team, so no one owns offers. The skill says an AWS-sourced deal needs someone to run it.
- ℹ️ **Stage:** you aren't registered with AWS Marketplace and have no other public paid product there.

## Why skip

1. **A listing is a procurement rail, not a demand channel.** The playbook says public listings draw little inbound, and revenue comes from private offers to buyers who already spend on AWS. "Millions of AWS customers browse it" doesn't describe how this channel earns money. Your $29/mo card buyers don't buy through procurement.
2. **The commit-drawdown pitch is closed to you.** "Burn your AWS commit" only works for products with the Deployed on AWS badge. That badge needs the application plane, the control plane, and every third-party service touching customer data to run on AWS. Vercel and Fly.io fail that test, so you'd be in the "transact, no commit" bucket. That bucket only makes sense for buyers who want one AWS invoice or pre-approved terms.
3. **Billing becomes a second system.**
   - You must bill through listed dimensions, with no card capture.
   - You'd integrate entitlement checks, hourly metering and EventBridge subscription events, and pass AWS's pre-Public review.
   - Your signups are card-based, so you'd run a parallel enterprise path next to your existing one.
4. **The fee buys you nothing yet.** The public SaaS fee is 3%†, and 1.5%† on renewals. That only pays off if Marketplace closes deals you couldn't otherwise close.
5. **AWS field help is slow.** AWS sellers don't prospect for an unknown ISV, and the playbook expects field engagement 6-12 months† after listing. ISV Accelerate is by invitation, after you already meet its pipeline thresholds.

## Irreversible choices you'd make by listing

These are the reason not to list casually.

- The AWS account you register becomes seller of record and can't change once a product is listed. Use a fresh standalone account, never your main one.
- The SaaS pricing model, such as subscription or contract, is fixed once the product is published to Limited. The wrong choice means a new product.
- Dimension API names never change, and custom dimensions can't be removed.

## What would change the verdict

List when **a named prospect asks to buy through AWS Marketplace.** Typically that's a mid-size or larger team whose procurement wants AWS billing. Then:

1. Ask them for the buyer pre-check items: the 12-digit AWS account, whether they run a Private Marketplace, invoice rather than card payment, and whether they expect to retire a commit.
2. Pick one owner for offers. Pay them the same commission as for direct deals.
3. Register a fresh standalone seller account.
4. Choose the pricing model. Contract is the playbook's default, because it maps to team and annual deals. Per-seat monthly at $29 is a poor fit for a contract listing, so decide this with the buyer's deal size in view. Don't switch later.
5. Publish to Limited, then request Public.
   - The playbook counts 3-6 weeks† from registration to Public. The review itself takes 7-10 business days†.
   - No private offer can go out before Public passes, so don't promise that buyer a signature date.
6. Send the first private offer to that deal. Use ACE (AWS's co-sell program) from this first deal.

If that deal is on a renewal date before Public can pass, extend them on your own paper first.

## What to do instead

- Check how often your signups ask about invoicing, annual billing or team plans. That's the real signal for an enterprise tier.
- If many ask, add direct annual invoicing first. It's cheaper and reversible.
- Moving to AWS would also let the commit pitch work, but that's a big infrastructure decision. Don't make it for a listing.

† Fees, durations and thresholds come from the playbook, not a live check. Verify them against the current AWS Marketplace Seller Guide before quoting them.