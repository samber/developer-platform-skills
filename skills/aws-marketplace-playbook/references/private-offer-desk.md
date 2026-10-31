# Private offer desk and integration review

Figures marked † come from the AWS Marketplace Seller Guide and change without notice: verify before quoting.

## Contents

- Buyer pre-check before any offer
- Offer settings
- Changing a signed deal
- Resellers (CPPO)
- Commitment drawdown
- Integration items reviewed before Public

## Buyer pre-check before any offer

Confirm each line with the buyer's cloud or procurement team, in writing:

1. The 12-digit AWS account that will own the subscription (linked or management account).
2. Whether the organization runs a Private Marketplace. If yes, extend the offer to the buyer account and the Private Marketplace administrator account, and ask the administrator to approve the product.
3. Payment by invoice, not card. Card buyers are charged at once, so net terms and a spread schedule do nothing for them.
4. Any active agreement for the same product in that account. Products using one agreement per account need a replacement offer, not a new one.
5. Whether the buyer expects the purchase to retire an AWS commitment, and whether your product carries the Deployed on AWS badge.
6. Currency: private offers support USD, EUR, GBP, AUD and JPY† (INR for sellers in India) with a matching disbursement method; public offers are USD only.
7. Country: if you geo-target the offer, the buyer account's own location must be in the selected countries, or it cannot accept.

## Offer settings

- **Expiry**: date of your choice, closes at 23:59:59 UTC, extendable. Practitioners set 30 days aligned to the buyer's quarter-end and extend rather than issuing long-dated offers.
- **Buyers**: up to 24† account IDs per offer. Product and product type cannot change after creation.
- **Installments**: monthly, quarterly, annual or custom; only one invoice date may fall before acceptance. Extending an expired installment offer can fail on that rule: update the schedule too.
- **Net terms**: Net 15 to Net 120†, applied to every charge in the offer, fixed after acceptance.
- **Future-dated agreement**: starts up to 3 years† ahead. For a renewal, start the day after the current agreement ends. Auto-renewal must be off before acceptance and cannot come back.
- **Auto-renewal**: set renewal price (same or uplift), maximum renewals, decision deadline; finalize any uplift before the adjustment deadline or the default applies.
- **Purpose**: mark renewals of existing paid customers, including those moving from an off-Marketplace contract, so the 1.5%† renewal fee applies. Moving a public Marketplace subscriber onto a private offer is not a renewal.
- **EULA**: Standard Contract for AWS Marketplace shortens legal review; custom EULA accepts up to five documents.
- **Express private offers**: rate cards that let buyers get standard-deal offers without your sales team.

## Changing a signed deal

- Upgrades, extra units, new payment schedules and EULA swaps go through an agreement-based (replacement) offer from the Agreements page. It takes effect on acceptance and cancels the old agreement's unbilled payments: carry them over.
- A replacement cannot be future-dated and cannot change the seller of record. Amending a public agreement turns it private and ends its auto-renewal.
- Contract buyers can upgrade but never downsize mid-term; they shrink at renewal.
- Cancellation you request goes to the buyer, who has 7 days† before it auto-approves. AWS refunds non-private purchases cancelled within 48 hours† without asking you. Every paid product needs a published refund policy.

## Resellers (CPPO)

- The reseller must be a registered paid seller. You issue a selling authorization: product, wholesale price or recurring discount, optional buyer IDs, renewal flag for an existing paid customer, currency, maximum net terms, latest service start date, and availability (single use, until a date, or open-ended).
- The reseller is seller of record for the agreement: refunds and cancellations go through it.
- The reseller marks up the wholesale price; its margin is the spread.
- Your fee is the normal tier plus 0.5%†, computed on the wholesale price and taken from your payout.
- Published authorizations cannot be edited or extended. Issue single-buyer authorizations for negotiated deals and recurring ones only for trusted partners.
- Distributors can pass authorizations down to resellers. Designated Seller of Record (DSOR) partners, by invitation, list and sell on your behalf.

## Commitment drawdown

- AWS states that products with the Deployed on AWS badge "may qualify" for customer commitment benefits. Practitioners read it as: since May 2025, SaaS hosted partly or fully off AWS no longer retires EDP or Private Pricing Agreement commitments.
- The badge needs application and control plane on AWS, and every third-party service that transmits, stores or processes customer data on AWS too; only CDN, DNS and corporate identity providers are exempt. A database host or model API outside AWS disqualifies the product. Agents on buyer premises are allowed when they send data only to AWS.
- AWS reviews a non-public architecture diagram submitted in Partner Central before granting it.
- The share of a commitment Marketplace can retire sits in each buyer's private contract. Practitioners commonly cite 25%; AWS publishes no figure. Never promise a percentage: ask the buyer's AWS account team.
- Invoice date, not signature date, decides eligibility. Professional services do not count.

## Integration items reviewed before Public

Seller Operations exercises the integration before approving Public. Each item below sends listings back when missing:

- Fulfillment page accepts an HTTPS POST with the registration token, resolves it at once, and never stores it in a cookie.
- Resolve the token to the buyer account and license; key every record on the license ID, since one account can hold several agreements for the same product.
- Registration accepts any email domain, incomplete and repeated attempts, has an English view, and lets existing users log in.
- Subscription events arrive on Amazon EventBridge routed to a queue; handle subscribe, change, cancel and expiry.
- Contracts check entitlements; usage and overage are metered hourly with retries. After cancellation or expiry you have one hour† to send final usage.
- Test buyer accounts listed in the product notes; every test subscription cancelled before you request Public.
- Support contacts on the landing page; subscription status visible in the product; EULA and refund policy attached.

This list covers what most often sends a listing back; run AWS's full SaaS product integration checklist (test bills, invalid-customer cases, account security) before requesting Public. For metering pipeline code, use AWS's own Marketplace integration samples or documentation rather than writing it from this list.
