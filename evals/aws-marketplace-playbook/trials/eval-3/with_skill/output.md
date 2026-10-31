# Northvale Health via Corbel Systems: AWS fees and reseller authorization

**Short answer:** you pay the AWS fee, not Northvale and not Corbel, and it is 3.5%† of the wholesale price. Don't publish the authorization with loose terms. A published authorization can't be edited or extended, so "tighten later" isn't possible.

## Assumptions

- **Margin definition.** I read "15% margin" as Corbel keeping 15% of the $500k resale price. That makes the wholesale price $425,000.
  - If Corbel means a 15% markup on wholesale, wholesale is about $434,783 and the figures below shift by about 2%.
  - Fix this definition in writing with Corbel before you price the authorization.
- **New customer.** I assumed Northvale is a new customer for this product. If they already pay you off-Marketplace and this is a renewal, the fee drops (see the fee table).
- **Country and listing.** I assumed Northvale isn't a South Korea buyer and that your listing is already Public. If either is wrong, see the checks at the end.

## Who pays the AWS fees

This is a CPPO (channel partner private offer) deal. You issue Corbel a selling authorization with a wholesale price. Corbel marks it up and sells to Northvale, so Corbel is the seller of record.

| Item | Amount |
| --- | --- |
| Resale price to Northvale (3-year total) | $500,000 |
| Corbel's margin (15%) | $75,000, kept by Corbel as the spread |
| Wholesale price you set | $425,000 |
| Your AWS fee, 3% new private offer under $1M† + 0.5% CPPO†, on wholesale | 3.5% × $425,000 = **$14,875** |
| **Your net, before tax** | **$410,125**, about 82% of list |

- **You:** AWS deducts the fee from your payout. The 0.5% CPPO surcharge is computed on the wholesale price, so it is also yours to absorb.
- **Northvale:** AWS invoices Northvale. Where marketplace-facilitator law applies, AWS collects and remits the tax. Northvale pays no AWS fee.
- **Corbel:** the skill doesn't cover Corbel's own fees or terms with AWS. Treat that as unverified and ask Corbel. Don't quote a number to anyone.
- **Payment schedule:** fees are charged on the total contract value, whatever the schedule. A 3-year deal paid yearly doesn't defer the fee.

How the fee changes under other assumptions:

| Case | Fee rate | Fee on $425k wholesale |
| --- | --- | --- |
| New customer (assumed) | 3.5%† | $14,875 |
| Existing paying customer moving onto Marketplace, with the renewal flag set on the authorization | 1.5% + 0.5% = 2%† | $8,500 |
| South Korea buyer | +1%† | add $4,250 |

Price the 0.5% into the 15% discussion. Your fee is roughly the same as a direct private offer (3% × $500k = $15,000†), but your net is $75k lower because of Corbel's margin.

Also note that Corbel handles refunds and cancellations for this agreement. The skill doesn't say whether Northvale can downsize mid-term; confirm that before promising Corbel anything.

## The "loose terms now, tighten later" plan

Don't do it. Four reasons:

1. **Published authorizations can't be edited or extended**, only deactivated. Any mistake costs a new authorization.
2. **Loose terms are risky.** Examples are open-ended availability, a recurring discount instead of a fixed wholesale price, no buyer ID, and generous net terms. They let Corbel sell your product to anyone at your wholesale terms. The skill says to use recurring authorizations only for trusted partners.
3. **Wrong inputs can't be fixed.** Wrong currency, wholesale price, renewal flag or service start date are all fixed once published.
4. **There is no deal shape to wait for.** Product, term, price and margin are already known. The remaining unknowns are paperwork and can be collected now.

**Do now, without publishing:**

1. Confirm Corbel is a registered paid AWS Marketplace seller. The authorization can't be issued otherwise.
2. Get Northvale's 12-digit AWS account ID, the one that will own the subscription, in writing.
3. Run the buyer pre-check with Northvale's cloud or procurement team, in writing:
   - Private Marketplace: if they use one, extend to the administrator account too and ask them to approve the product.
   - Invoice payment, not card.
   - Any active agreement for your product in that account.
   - Currency. USD, EUR, GBP, AUD and JPY† are supported.
   - Country, if you geo-target.
   - Whether the buyer expects to retire an AWS commitment. That requires your Deployed on AWS badge, and you must never promise a percentage.
4. Agree in writing with Corbel: margin definition, wholesale price, currency, maximum net terms, service start date, and who handles refunds and cancellations.
5. Decide the renewal flag: set only if Northvale is an existing paying customer.

**Then publish a tight authorization:**

- Single buyer: Northvale's account ID.
- Single use.
- A wholesale price, not a recurring discount.
- A near-term latest service start date.
- Maximum net terms you can live with, noting AWS pays you only after it collects.

If the deal changes after publication, deactivate and reissue. That is cheap with a single-buyer, single-use authorization. It would be costly with an open one.

## Checks before you quote any of this

- **Public listing.** A first private offer requires a Public listing priced above zero. If you're still Limited, plan 3–6 weeks† and don't promise Northvale a signature date earlier than review allows.
- **Account status.** Your seller account must be registered and you must be able to receive disbursement.
- **Co-sell.** Submit the deal to ACE with real AWS consumption, and link your Partner Central and Marketplace seller accounts.
- **Rep commission.** Pay reps the same commission and quota credit as a direct deal, on acceptance. The skill doesn't say which amount the credit is based on, so decide that now. Don't deduct the fee from commission.

† Fees, durations and thresholds come from the AWS Marketplace Seller Guide and change without notice. Verify them against the current guide before quoting any figure to Northvale or Corbel.