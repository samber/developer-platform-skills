# Ledgerkite fees and setup: three marketplace cases

Assumptions, since the request left gaps:
- Ledgerkite already has a live, transact SaaS offer on Microsoft Marketplace.
- Its Azure IP co-sell eligibility and MACC enrollment are in place.
- The standard marketplace fee is 3%†, and the renewal attestation halves it†, so 1.5%†. The playbook says "halves", not 1.5%, so I derived that figure.

† means verify in Partner Center before quoting. Microsoft moves fees and criteria often.

## Summary

| Case | Fee | Main action |
|---|---|---|
| 1. Off-marketplace renewal in January | 1.5%† for the whole term, if set up correctly | Create a new private offer with the renewal attestation ticked |
| 2. August 2024 private offer, auto-renews next month | 3%† if it auto-renews, 1.5%† if replaced | Have the customer stop auto-renew and accept a new attested private offer before the renewal date |
| 3. German reseller through CSP, counted against MACC | Not in the playbook, so I won't invent one | The CSP route can't count toward MACC, so use a different structure |

## 1. Big customer, off-marketplace contract, renewal in January

- **Fee:** 1.5%†, fixed for the whole offer term. Moving an off-marketplace contract onto the marketplace is a qualifying case.
- **Setup:**
  1. Create a private offer on the live transact SaaS offer.
  2. Tick the renewal attestation when you create it. It cannot be added later, so a forgotten tick means 3%† for the whole term and a rebuild.
  3. Send it early enough for the customer's procurement to accept before the January renewal.
  4. If they hold a Microsoft Azure Consumption Commitment (MACC), say so. Ledgerkite's eligibility lets the spend draw down, but only for usage running in Azure.
  5. Check that the offer shows MACC "Enrolled"†.

## 2. Customer on an August 2024 private offer, auto-renews next month

- **Fee:** 3%†. An offer created before October 2024 never qualifies for the reduced fee. The attestation can't be added to it, and auto-renew keeps the old terms.
- **Setup to get 1.5%†:**
  1. Ask the customer to stop auto-renew now, before next month's renewal date.
  2. Create a new private offer for the renewal with the renewal attestation ticked.
  3. The customer accepts the new offer.
- **If you do nothing,** it auto-renews at 3%†. Check the exact auto-renew cutoff in Partner Center today.

## 3. German reseller via CSP, customer wants it to count against their Azure commitment

- **Blocker:** CSP private offers never count toward MACC. The reseller's CSP route and the customer's goal can't both be met.
- **Fee:** The playbook gives no figure for channel or multiparty offers, and I won't guess. Get the fee and the reseller's margin from Partner Center before you quote anything†.
- **Options:**
  1. **Multiparty private offer.** The playbook's tool for when a reseller owns the relationship, with one channel partner per offer. It doesn't say whether these count toward MACC, so confirm with Partner Center support before promising it†.
  2. **Direct private offer to the customer.** This is the safe route for MACC drawdown, but the reseller loses its resale role on the marketplace. You would need to settle its compensation outside the marketplace.
- **Setup:**
  1. Tell the customer and the reseller now that CSP won't count toward MACC.
  2. Get written confirmation on multiparty versus MACC.
  3. Pick the structure.
  4. Create a private offer that matches it, ticking the renewal attestation only if it is a renewal or upsell to an existing customer.

## Open questions

1. Is the January customer already a Microsoft MACC holder?
2. What exact date does the August 2024 offer auto-renew?
3. Is the German deal a new sale or an upsell? That decides whether the attestation applies.