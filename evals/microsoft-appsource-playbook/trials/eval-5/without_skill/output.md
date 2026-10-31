# Ledgerkite on Microsoft's commercial marketplace: fees and setup

I answered from memory and did not check Microsoft Learn or Partner Center, and I did not read anything under `skill-wip/`. Confirm the points marked ⚠️ against your current Partner Center fee and payout terms before you quote anyone.

## Summary

| Case | Fee you pay | Core setup |
|---|---|---|
| 1. January renewal, off-marketplace today | 0% if it stays off-marketplace. About 3% if you move it to the marketplace. | Decide whether to move it. If yes, create a private offer for their tenant before the renewal date. |
| 2. August 2024 private offer, auto-renews next month | About 3% on the renewal billing. | Check the plan's renewal setting and pricing, and confirm the fee in the payout report. |
| 3. German reseller via CSP, customer wants Azure commitment credit | About 3% marketplace fee, plus the reseller margin you set. | Resale-enabled plan, then a multiparty private offer. Verify first that the CSP route retires the commitment. |

## 1. Large customer, off-marketplace contract, renewal in January

**Fee**
- If you renew off-marketplace, Microsoft takes nothing, and the spend does not count against the customer's Azure commitment (MACC).
- If you move the renewal onto the marketplace as a private offer, you pay the 3% transactable fee for SaaS and Azure apps. The 20% rate that used to apply no longer does.
- The customer is paying a lot of money either way. The 3% buys you MACC burn-down for them, co-sell credit, and Microsoft seller incentives.

**Set up**
1. Ask the customer whether they have a MACC. If not, there is little reason to move.
2. Confirm the offer is transactable, not list-only, and is Azure IP co-sell eligible and Azure benefit eligible. Benefit eligibility is what lets the purchase retire the commitment.
3. Create a private offer in Partner Center. Use the customer's tenant ID and billing account, match the January start date and term, and price it at or below today's contract so the MACC story helps them.
4. Allow lead time. Customer acceptance and billing-account checks take weeks, so start in November, not January.
5. Terminate or let lapse the off-marketplace contract on the same date. Do not double-bill.
6. Bring in your Microsoft partner development manager or seller. Co-sell registration is what turns the move into incentive credit.

## 2. Customer on an August 2024 private offer, auto-renewing next month

**Fee**
- It is the same marketplace rate, about 3%, charged on each billing event.
- ⚠️ I believe the 3% rate applies to billing at the time it is invoiced, not at the date the offer was created. Confirm in the Partner Center payout and earnings report.

**Set up**
1. Open the plan in Partner Center and check the term and auto-renew setting. A renewal runs at the original private-offer price and terms.
2. If you want a different price, seat count or term, you need a new private offer before the renewal date. Do not rely on the auto-renew.
3. Tell the customer the renewal is coming. Their MACC retirement continues only while the offer stays active and benefit-eligible.
4. Check the next invoice and the payout line to confirm the fee rate.

## 3. German reseller via CSP, customer wants it to count against their Azure commitment

**Fee**
- You pay the same ~3% marketplace fee. ⚠️ Confirm whether it is calculated on the price the reseller pays you or on the customer price.
- The reseller's margin is a separate commercial cost. You set it in the offer, and Microsoft does not charge it.

**Set up**
1. Enable resale on the plan ("resale enabled"), and name the German reseller as an authorized CSP partner.
2. Create a multiparty private offer. You set the wholesale price and the reseller's margin. The reseller then completes the customer-facing offer.
3. Confirm the reseller holds the CSP indirect-provider and reseller relationship for that customer.
4. Handle VAT and invoicing. The reseller is the seller of record to the customer, and the marketplace handles your payout in EUR.
5. **Main risk, verify before promising:** I am not sure a CSP-resold purchase retires the customer's Azure commitment. The multiparty private offer route may allow it. A plain CSP resale generally does not. Get written confirmation from Microsoft, through your partner development manager or Partner Center support, before you promise the customer anything. If the CSP route does not retire the commitment, the customer must buy through a direct private offer and the reseller loses the margin. In that case, offer the reseller a referral or services arrangement instead.

## Next steps
1. Confirm which customers have a MACC. It decides whether cases 1 and 3 are worth doing.
2. Get Microsoft's written answer on commitment retirement through the CSP route.
3. Put the January customer's private offer in motion in November.
4. Check the renewal setting and the payout fee line for the August 2024 customer this week.