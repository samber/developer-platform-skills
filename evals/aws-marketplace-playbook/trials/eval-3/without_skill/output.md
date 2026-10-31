**Next action:** confirm with Corbel and your finance lead what "15% margin" is measured against (see the math below). Then ask your ops lead to hold off on the loose authorization.

## 1. Who pays the AWS fees?

**You do.** In an AWS Marketplace channel-partner private offer:

- **Northvale** pays Corbel's price and no AWS fee.
- **Corbel** keeps its margin. It is the difference between your wholesale price and what it charges Northvale.
- **You (the ISV)** pay the AWS Marketplace seller fee. It comes out of your disbursement. You also fund Corbel's margin, because it is carved out of your price.

I have not checked the current fee schedule. The fee percentage and its basis (your wholesale price or the buyer's total) have changed over the years. Confirm both in the AWS Marketplace Management Portal or with your AWS partner rep before you quote anyone. The rate has been about 3% on private offers, so the figures below use that as an assumption.

**Illustrative math** (3-year, $500k list, 15% margin, 3% fee):

| Reading | Corbel margin | Your wholesale price | AWS fee (3%) | Your net |
|---|---|---|---|---|
| Northvale pays $500k, Corbel keeps 15% | $75k | $425k | $12.75k if on wholesale; $15k if on $500k | about $410k to $412k |
| Northvale pays $500k × 0.85, Corbel adds 15% on top | depends on Corbel's markup | $425k | same as above | same as above |

The second row shows the ambiguity. "15% margin" could mean 15% of the customer price or 15% off your list. Get the definition and the dollar amount into writing. Then check that the offer's payment schedule (annual or upfront) matches your cash plan, because the fee applies to each disbursement.

Other points to check:
- **Seller of record, tax and contract terms.** Check who is seller of record, who handles tax and who owns the EULA and support. Corbel's reseller agreement sits outside AWS and has to cover these.
- **Corbel's AWS status.** Corbel must be an eligible AWS Marketplace channel partner. Confirm that before anything else.
- **Fee clawback.** Confirm how the fee is treated if the deal is cancelled or the amount changes.

## 2. Loose authorization now, tighten later: don't

I recommend against it, for four reasons.

1. **The authorization defines what Corbel can quote.** That covers product, pricing floor or discount, term and expiry. Anything you leave open is a decision you have handed to Corbel.
2. **You can't tighten after the buyer accepts.** Once Northvale accepts the offer, the contract is fixed. Closing a gap afterward means renegotiating with a partner who now holds the leverage.
3. **Loose terms can leak.** If Corbel isn't scoped to one buyer, it can use the authorization for other deals. That exposes you to channel conflict, margin leakage and discount precedent.
4. **You already know the deal shape.** It is one buyer, one reseller, one product, 36 months, $500k. There is nothing left to learn that justifies being loose.

**Set the authorization tight now:**

- Scope it to the one product, to Corbel only, and to Northvale's AWS account if the portal supports buyer scoping.
- Cap the discount so Corbel's margin can't exceed 15%. Set a price floor of $425k, or whatever you settle on.
- Limit the term to 36 months, with no auto-renewal and a fixed payment schedule.
- Set a short expiry, for example 60 to 90 days, so it lapses if the deal stalls.
- Keep ISV approval on for the resulting offer, and review the final terms before Northvale sees them.
- Put the commercial terms in a signed reseller agreement before you create the authorization. These cover margin definition, renewal margin, support responsibility, and who owns the customer relationship at renewal.

**Where loose is fine:** an expiry you can extend or a margin you can raise later. Both can safely start tighter than final, because extending or raising is the easy direction. Starting loose and tightening is the hard direction.

I couldn't verify the AWS portal specifics (buyer scoping, whether an authorization can be edited after creation, current fees) from here. Have your AWS partner rep confirm them before you build it.