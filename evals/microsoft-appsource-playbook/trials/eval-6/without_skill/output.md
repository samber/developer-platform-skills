Do this first: open Partner Center, confirm Brightmoor's commercial marketplace account is verified, and start the payout and tax profile. Legal verification can take days, and it blocks everything else. Time: 30 minutes to start.

⚠️ I wrote this from memory and did not check live Microsoft docs. Items marked **verify** may have changed since your 2024 notes.

## What changed from your 2024 notes

- **Order is wrong.** Listing comes first, not last. Marketplace Rewards and co-sell benefits need a live listing. Rewards benefits also depend on marketplace activity (**verify** current terms).
- **AppSource is now part of Microsoft Marketplace.** Azure Marketplace and AppSource were merged (**verify** current naming and Partner Center menus).
- **ISV Success credits are for dev/test, not production.** They fund the build. They do not produce a transaction.
- **Qualified Referral Program (**verify**).** I can't confirm it still exists in its 2024 form. Drop it from this quarter either way. It is lead generation, it needs a live listing, and it cannot produce a January transaction.
- **A listing alone does not transact.** You need a transactable SaaS offer plus a customer who buys it. The fastest path is a private offer to one named customer.

## Plan: Nov 2 to Jan 30

Target: first Marketplace transaction by Jan 30. I define "transaction" as the customer accepting a private offer and a live subscription, not cash received. Payouts come weeks later.

1. **Week of Nov 2: decisions and accounts (about 1 week)**
   - Finish Partner Center verification, payout profile, and tax forms.
   - Apply to ISV Success. Use the credits for Brightmoor's Marketplace integration testing.
   - Name one pilot customer. Pick one that already runs on Azure, ideally with a Microsoft commitment (MACC) to burn down. Ask them now whether their procurement allows Marketplace purchases.
   - Decide the pricing model. A private offer needs a transactable public plan to build on, even if the plan is hidden.
2. **Nov 9 to Dec 4: build (about 4 weeks of engineering)**
   - Build the SaaS fulfillment: landing page with Entra sign-in, webhook, and subscription lifecycle (SaaS Fulfillment API v2). Add metering only if your pricing needs it.
   - Write the listing content, terms, and privacy links.
   - Test in preview with your own tenant.
3. **Gate on Dec 4.** The listing must be submitted by then. If it is not, a January transaction is unlikely. Tell the pilot customer early.
4. **Dec 7 to Dec 18: certification and publish (about 2 weeks)**
   - Submit, fix review findings, and go live before Dec 18.
   - Then request co-sell status and Azure benefit/MACC eligibility. Check Microsoft's current requirements (**verify**). They typically include technical validation and reference customers, so start collecting references now.
5. **Dec 19 to Jan 2: holiday freeze**
   - Draft the private offer: price, term, and customer tenant ID and billing account. Expect customer procurement to pause.
6. **Jan 5 to Jan 16: private offer**
   - Send the offer to the customer's tenant and help their admin accept it. Keep Jan 19 to 30 as buffer.
7. **After first transaction**
   - Check what Marketplace Rewards offers you at that point (**verify**).
   - Revisit lead-generation programs.

## Risks, ranked

1. 🔴 **No named buyer by mid-November.** Without one, nothing transacts. Customer procurement often needs 2 to 4 weeks.
2. 🟠 **Certification rejection.** Each review round can add days to a week. The Dec 4 submission date is your buffer.
3. 🟠 **Customer cannot buy through Marketplace.** Some customers lack a billing account or tenant setup for it. Confirm in week 1.
4. 🟢 **ISV Success approval delay.** Low impact, because the credits are optional for the timeline.

Next: tell me whether a pilot customer exists and whether they run Azure with a commitment. That decides whether January is realistic.