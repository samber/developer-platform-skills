# Harrow Insurance: AWS Marketplace renewal

## Short answer

- **Fee:** 1.5%† of pre-tax total contract value, if the offer carries the renewal flag. Without the flag it is 3%†.
- **Monday:** don't send the offer. A first product can't carry a private offer while it is Limited. The listing has to pass Public review first.
- **Signed before Christmas:** possible, but not guaranteed. The 1 Feb start is not at risk.

## 1. Why Monday doesn't work

Your seller account needs at least one public listing priced above zero before any private offer can go out. This is your first and only product, so it can't have one while it is Limited.

To get there, request **Public** with the real price. Seller Operations reviews in 7-10 business days† from the request, and longer if they find errors.

Counting from today (Sat 31 Oct):

| Event | Date |
|---|---|
| Request Public (earliest, Mon 2 Nov) | 2 Nov |
| Review passes (7-10 business days, if no errors) | about 11-16 Nov |
| Private offer can go out | mid-Nov at the earliest, realistically late Nov or early Dec |

Signature before Christmas is realistic if the integration already passes the review list in section 3. I don't know whether it does, so treat that as an assumption.

Don't promise Harrow a signature date earlier than the review allows.

**Fallback:** if Public hasn't passed by about mid-December, extend Harrow briefly on your own paper. Put the Marketplace move at the following renewal.

The AE can tell Harrow now that the offer follows listing approval and targets the 1 Feb start.

## 2. Fee

AWS charges its fee on pre-tax total contract value. The quarterly payment schedule does not change it.

| Case | Rate† | On a 12-month, $380k term |
|---|---|---|
| Existing customer moving from your paper, flagged **Existing Customer Moving to AWS Marketplace** | 1.5% (renewals pay this at any size) | about $5,700 |
| Same offer, flag not set (treated as a new private offer under $1M) | 3% | about $11,400 |

- **Flag:** Harrow is a paying off-Marketplace customer renewing, so it qualifies. The AE must set the flag when drafting the offer, because forgetting it doubles the fee.
- **Multi-year:** the fee scales with total contract value. A 3-year offer is about $1.14M, which is about $17.1k at 1.5%.
- **Reseller:** no reseller is involved, so there is no CPPO surcharge. A reseller would add +0.5%† and become seller of record.
- **Payment timing:** AWS invoices Harrow and pays you only after it collects. Net terms shift your cash by the same number of days.
- **Sales comp:** pay the AE full commission and quota credit on acceptance. Don't deduct the fee from commission.
- **Public price:** don't inflate it to recover the fee. Keep the public price at list and discount in the private offer.

## 3. What to set up

### Today and Monday

1. **Check the pricing model.** It is fixed once published to Limited. Quarterly installments and auto-renewal need a **SaaS contract** model (or contract with consumption). If you picked subscription (pay-as-you-go) or free, you need a new product, and that restarts the timeline. Confirm this first.
2. **Check the integration.** Run it against the review list below, then run AWS's full SaaS integration checklist.
   - The fulfillment page accepts an HTTPS POST with the registration token, resolves it at once, and never stores it in a cookie.
   - Records are keyed on the license ID.
   - Registration accepts any email domain and has an English view.
   - Subscription events arrive on EventBridge and go to a queue. Handle subscribe, change, cancel and expiry.
   - Entitlements are checked on every customer change. If you use consumption, meter hourly.
   - Support contacts, EULA and refund policy are in place.
3. **Cancel every test subscription,** then **request Public** at the real price.

### In parallel

4. **Deployed on AWS badge.** Harrow wants this to count against their AWS spend, and only badged products may still retire a commitment. "Fully hosted on AWS" is not enough on its own.
   - The application plane, the control plane and every third-party service that touches customer data must be on AWS. Only CDN, DNS and corporate identity providers are exempt. A database host or model API outside AWS disqualifies you.
   - Submit the architecture diagram in Partner Central.
   - Invoice date, not signature date, decides eligibility. The badge therefore has to be in place by the first invoice around 1 Feb.
5. **Don't promise a percentage.** The share of Harrow's commitment that Marketplace can retire sits in their private AWS contract. Ask Harrow's AWS account team to confirm it. A figure of 25% circulates, but AWS publishes none.
6. **Link accounts and register the deal.** Link your Partner Central and Marketplace seller accounts. Submit the deal to ACE as an opportunity.

### Buyer pre-check (get each answer from Harrow's cloud or procurement team, in writing)

1. The 12-digit AWS account that will own the subscription.
2. Whether they run a Private Marketplace. If so, extend the offer to their account and to the administrator account, and ask the administrator to approve the product.
3. Payment by invoice, not card. Card buyers are charged immediately, so installments and net terms do nothing for them.
4. Any active agreement for your product in that account. If one exists, you need a replacement offer instead.
5. Confirmation that they expect the purchase to retire commitment, and that they know whether you hold the badge.
6. Currency: USD, EUR, GBP, AUD or JPY† are supported, with a matching disbursement method.
7. Country, if you geo-target the offer. Their account's own location must be in the selected countries or they can't accept.

### Offer settings

| Setting | Value |
|---|---|
| Purpose | **Existing Customer Moving to AWS Marketplace** (renewal flag) |
| Start | Future-dated to 1 Feb, the day after the current agreement ends (up to 3 years ahead†) |
| Payments | Quarterly installments; only one invoice date may fall before acceptance. Check the schedule against the 1 Feb start. |
| Net terms | Ask Harrow's accounts payable; Net 15 to 120†. Fixed after acceptance. |
| Auto-renewal | Must be off before acceptance on a future-dated agreement, and it can't be turned back on. The next renewal needs a new offer. |
| Expiry | About 30 days, aligned to Harrow's quarter-end. Extend rather than issue a long-dated offer. |
| EULA | Your normal paper, up to five documents. The Standard Contract for AWS Marketplace shortens legal review if Harrow's lawyers will accept it. |
| Dimensions | Custom dimensions added for the offer can never be removed, so keep them minimal. |

Signed payment schedules and net terms are frozen on acceptance. Changing them takes a replacement offer that Harrow must accept, and it cancels unbilled payments unless you re-include them.

### Direct contract

Check your current contract's auto-renew and notice window. It must end cleanly on 31 Jan so Harrow is not billed on both your paper and Marketplace.

## Open questions

- Which pricing model did you publish? It decides whether this plan works at all.
- Does the integration already pass the review list?
- Are all third-party services that touch Harrow's data on AWS?
- How long is the term, 12 months or longer? It sets the fee.

† AWS figures (fees, durations, limits, thresholds): verify against the current AWS Marketplace Seller Guide before quoting them to Harrow or finance.