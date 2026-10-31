**Short answer: yes, several things are wrong.** The plan as written can't be built on Microsoft Marketplace. It also has two costly mistakes: a flat plan locks Teams out, and testing on the live offer gets you invoiced.

## What breaks

1. **Flat monthly now, per-seat later, in one offer: not possible.** The pricing model (flat rate or per user) is fixed per offer. It is the same for every plan in that offer and can't change after publish.
2. **Teams selling "the same offer" needs per-user pricing.** A Teams-linked offer must be per user. A flat monthly offer can never be linked to the Teams app. Switching later means a second offer, a new review and MACC re-enrollment.
3. **A per-seat plan plus a usage meter in one offer: not possible.** Metering exists only on flat-rate plans. Per-user and metered plans can't live in the same offer.
4. **Contact Me now, transactable in Q2, may not work.** Microsoft's pages disagree on whether a published listing-only offer can switch to transact. Don't rely on it. Either build transact from day one, or get Partner Center support to confirm in writing before you publish.
5. **Contact Me doesn't get you "in the catalog" in any useful way.** It unlocks no MACC, no IP co-sell and no private offers. It gives you leads you chase yourself.
6. **Testing on the live offer with the corporate card will cost you.** Test purchases are invoiced. They are refunded only if cancelled within 72 hours†. Your own purchases would also pollute the live offer. Use a separate DEV offer in preview at a nominal price, and never press Go live on it. Publish the real offer to a preview audience first, then Go live.
7. **Teams apps never earn co-sell.** The linked SaaS offer stays eligible, so co-sell and MACC run on the offer, not the app.

## Assumptions (I couldn't ask)

- **Hosting:** Pingwell is not primarily on Azure. A non-Azure SaaS offer must integrate with or extend a Microsoft product, say how in the description, and accept Entra SSO. A linked Teams app usually meets that test, so confirm it in the certification notes. Without a Teams app or another Microsoft integration, the SaaS offer itself may be rejected.
- **Stage:** no live offer yet.
- **Date:** no hard target date.
- **Owner:** no one owns Microsoft seller outreach.

Tell me if any of these is wrong, since they change the path.

## Recommended path

Transact SaaS with private offers, plus a linked Teams app. Skip Contact Me. Skip Azure IP co-sell, since you're not on Azure. At most, stop at co-sell ready.

**Decide the Teams question first. It sets the pricing model.** Choose one:

- **Option A (recommended):** one per-user offer, Teams-linked. Plans are seat tiers, for example Team and Business. The offer goes live before the Teams app links to it.
  - The usage meter can't go in this offer. If you want API-call metering, handle overage in your own billing or build Option B.
- **Option B:** two offers.
  - Offer 1 is per-user and Teams-linked.
  - Offer 2 is flat-rate with the API-call meter, not Teams-linked.
  - Customers then buy through two SKUs and you run two certifications. Do this only if you really need metered billing on Marketplace.
- **Not recommended:** a flat offer first. It permanently excludes Teams selling on that offer.

## Locked-choice register

Fill every row before the first publish:

| Choice | Proposed | Owner | Decision date |
|---|---|---|---|
| Pricing model | per user (Option A) | unassigned | unassigned |
| Plan IDs | unassigned | unassigned | unassigned |
| Seat min and max per plan | unassigned | unassigned | unassigned |
| Metered dimensions and IDs | none in Option A | unassigned | unassigned |
| Public vs private plans | public, plus private offers for deals | unassigned | unassigned |
| Contract terms | Microsoft standard contract, or your own | unassigned | unassigned |

Plan ID, seat limits, dimension IDs and values, a public plan going private, and standard vs custom contract terms are all locked once published.

## Submission plan

- **SaaS offer:**
  - Build the landing page and Fulfillment API v2, and validate webhooks through the Get Operation API.
  - Register a multitenant Entra app and request only `User.Read` at activation.
  - Write certification notes with test accounts that have no MFA.
  - Test on the DEV offer first.
- **Teams app:**
  - Complete Publisher Verification first.
  - Submit in parallel with the offer build. Budget three to six weeks†, including one failed cycle.
  - After the offer is live, add `subscriptionOffer` as `publisherId.offerId` with "Additional purchases" set to Yes. That update goes through validation again.
- **Publisher Attestation:** complete it the day the Teams app goes live, and renew yearly.
- **Pre-flight checks:**
  - App name, description and URLs are identical in the manifest and Partner Center.
  - Admin and non-admin users can buy.
  - License assignment counts are correct in your app.

## Co-sell plan

- **Status:** target co-sell ready only, with no IP co-sell and no MACC.
- **Gap:** Azure IP co-sell needs primarily-Azure platforming and $100K† Azure consumed or billed. Not applicable until an Azure migration is decided.
- **Collateral:** one-pager, pitch deck, and a sales contact per geography. Owner: unassigned. Raise this as a question.
- **First deals:** run them as private offers. Tick the renewal attestation for any renewal or upsell, because it halves the fee† and can't be added later.

## Timeline

No target date was given, so this runs forward from today, with a one-validation-cycle buffer:

1. Weeks 0–2: decide the pricing model and fill the register. Create the Partner Center account. The tax profile takes up to 48 hours before the payout profile.
2. Weeks 2–6: build the SaaS offer and test it on the DEV offer. Start the Teams app submission in parallel.
3. Weeks 6–9: certify and go live with the offer, to preview first. Teams review runs three to six weeks† and is likely still open.
4. Weeks 9–12: link the Teams app to the live offer, re-validate, attest, and run the first private offer.

Expect roughly three months, so a Q2 flip is realistic only if you start now.

† Verify every Microsoft figure (fees, thresholds, durations, refund windows) in Partner Center before quoting it. Microsoft renames programs and moves criteria yearly.