# AWS Marketplace: Kestrel Bank and Pinemoor

I answered from general knowledge of AWS Marketplace. I didn't check live docs, so confirm the exact Seller Portal labels and the fee treatment (marked ⚠️) with your AWS Marketplace Seller Operations contact before acting.

## Next actions, in order

1. Open the Kestrel offer in Seller Portal. Check its status, expiry, and the buyer account ID stored on it (**read-only**).
2. Ask Kestrel which AWS account they're signed into when they click the link.
3. Decide whether Pinemoor's two modules are one Marketplace listing or two.
4. Build one **replacement** private offer for Pinemoor instead of a new private offer. Details are in Problem 2.

## Problem 1: Kestrel Bank, "product not available in your private catalog"

**What it means.** A private offer is visible only to the AWS account ID it was extended to. If the viewer is signed into a different account, the offer doesn't exist for them. For a bank this is the most likely cause.

**Check in this order:**

1. **Account ID.** Compare the stored value with `441122907718`, which is 4411-2290-7718 without hyphens. Look for a typo or transposition.
2. **Which account Kestrel is using.**
   - Large banks run AWS Organizations. Procurement or the console user is often in a member account, a different account from the one you targeted (for example the payer or management account).
   - Ask them to look at the account ID in the console's top-right menu, and to open **AWS Marketplace → Private offers** in that account. Opening the offer from that page is more reliable than using the link.
3. **Offer state.** Look for an expired, withdrawn, or canceled offer, or an expired accept-by date. A published offer can take a short time to appear.
4. **Private Marketplace governance.** This is common at banks and matches the "private catalog" wording. If Kestrel's admins restrict which products users can subscribe to, the product may need approval in their private marketplace before anyone can see or accept it. Ask their cloud or procurement admin. This one is theirs to fix.
5. **Listing visibility and eligibility.** Check whether the listing is limited or public. Check for country or Region restrictions, and for buyer-entity constraints such as accounts billed through a regional AWS entity or GovCloud. ⚠️ I'm unsure how these interact with private offers, so confirm.

**Fix by cause:**

- **Wrong account:** you can't edit the recipient of a published offer. Create a new private offer to the correct account (copy the old one if the portal allows), then withdraw the old one. Do this before the old offer's expiry so two live offers don't cause confusion.
- **Expired offer:** create a new one.
- **Private Marketplace block:** Kestrel's admin approves the product, then the user retries.
- **Nothing above fits:** open an AWS Marketplace Seller Operations case. Include the offer ID, the account ID, the exact error text, and the time of the failed attempt.

## Problem 2: Pinemoor, "You already have an active contract"

**Cause.** A SaaS contract product allows one active agreement per buyer account. A brand-new private offer collides with the existing three-year agreement. You can't stack a second contract on top, so your offer type is wrong.

**What to use.** Use a **replacement (upgrade) private offer** that replaces the existing agreement. In Seller Portal this is the option to create a private offer against an existing agreement. ⚠️ I'm recalling the exact label from memory.

**How it behaves (verify before quoting to Pinemoor):**

- **It replaces the whole agreement.** The new offer must restate everything: all dimensions, seat counts, end date, payment schedule, and renewal terms. You can't amend one line.
- **Acceptance terminates the old agreement and creates a new one.** This can't be undone.
- **AWS doesn't carry paid amounts forward or prorate automatically.** You set the price. Design the new offer so Pinemoor isn't billed twice for periods already paid.
- **It must go to the same buyer account as the existing agreement.** A different account would create a parallel customer.

**Structure the new offer like this:**

- **End date:** keep the original three-year end date, unless the commercial deal changes it.
- **Seats:** current plan plus 50 on the module being expanded.
- **Payment schedule:** use a flexible schedule.
  - Payment 1 is a prorated charge for the +50 seats from today to the next anniversary, due on acceptance.
  - Future payments fall on the same dates as the old remaining installments, at the new seat totals.
  - Don't re-charge what Pinemoor has already paid for existing seats.
- **Renewal and auto-renew:** set them deliberately, matching the old contract.

**Your SaaS integration needs a test first.**

- Replacement changes the agreement ID and entitlements. Your fulfillment handler (customer resolution, entitlement lookups, and notifications) must not revoke access when the old agreement ends, and must not create a duplicate tenant when the new one starts.
- Run a test replacement in your staging or sandbox listing, or review the handler logic, before sending it to a real customer.

## The AE's request: 200 → 150 seats on another module

1. **Decide whether this is one product or two.**
   - **Same listing, two dimensions:** one replacement offer covers +50 on one dimension and −50 on the other.
   - **Two separate listings:** two separate agreements, so two replacement offers. Each is accepted on its own, so Pinemoor could accept one and not the other.
     - Mitigate this by sending both together.
     - Get a written order form or amendment that ties them together, and ask one named buyer to accept both the same day.
2. **Treat the reduction as a concession, not an admin change.**
   - Pinemoor signed a three-year commitment at 200 seats. They have no right to cut it mid-term.
   - The AE is trading −50 seats for +50 seats. Sales leadership and finance should approve the net effect on contract value, and it should be written down.
3. **If the current year is already paid at 200 seats**, a mid-year reduction creates a credit. Apply it to the next installment. Don't pay out a refund, because AWS won't do that for you.
4. **Fees** ⚠️. Ask Seller Operations how the AWS listing fee applies to a replacement offer: on the full new contract value, or only the increment. This could change your margin on a mid-term swap.

## Fallbacks

- If Seller Portal doesn't offer replacement for this agreement (for example a legacy contract), open a Seller Operations case. Include the agreement ID, the offer ID, and the error screenshot.
- If the +50 can't wait, invoice the extra seats directly outside Marketplace. Pinemoor then loses AWS commit drawdown on those seats, and you lose any co-sell credit. Use this only if they agree.
- If the listing has a consumption or pay-as-you-go dimension, extra usage may not need a new offer.

## Questions I need answered

1. For Kestrel: is the account the buyer signs into the same as `441122907718`, and does Kestrel use a private marketplace?
2. Are Pinemoor's two modules one listing or two?
3. When are the two remaining Pinemoor payments due, and has the current year been paid in full?
4. Who approves the downgrade on your side?