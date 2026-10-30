**Fee: 3% of the transaction value, so about $11,400 per year on $380k.** AWS keeps it and pays you the rest. I'm giving this rate from memory. AWS has revised its fee schedule recently, so confirm it in the Seller Guide's fees page or in the Management Portal's offer preview. $380k is below any volume discount I know of.

**Step 1 (5 min).** Open the AWS Marketplace Management Portal. Start a draft private offer from your Limited listing. If the portal lets you pick Harrow's account, Limited does not block you. I believe private offers work on Limited listings, but I have not checked this against your portal. Do this before Monday so the AE doesn't promise a date you can't meet.

**Check before the AE sends anything:**

1. **Pricing model must be contract.** Quarterly billing uses flexible payment schedule, and that only works on SaaS contract pricing. If the listing is subscription or usage-only, you can't bill quarterly. Changing the pricing model on a listing this new may mean a new product.
2. **Dimensions.** A private offer reuses the listing's contract dimensions and changes only price and quantity. Make sure one fits a $380k annual contract.
3. **SaaS integration must work end to end.** This is the biggest risk for a first listing.
   - Your registration URL receives the buyer's token and calls `ResolveCustomer`.
   - You store the customer ID and read entitlements with `GetEntitlements`.
   - You subscribe to the Marketplace SNS topic for entitlement changes and cancellations.
   - You map the AWS customer to Harrow's existing tenant. Without this, they land on a blank signup instead of their live data.
   - Run a full test purchase from an allowlisted test account.
4. **Seller account is complete.** Tax interview and bank account must be done, or AWS can't disburse.
5. **Tax.** Confirm who calculates and collects tax on Harrow's invoices. It depends on where Harrow is. Ask your finance team.

**Offer settings:**

- **Buyer:** Harrow's AWS account ID. Ask which account holds their Marketplace purchases, since it is often a payer account.
- **Terms:** 12 months, agreement start 1 Feb. Future-dated start is supported, so Harrow can accept before Christmas and the term still starts 1 Feb.
- **Payment:** flexible payment schedule with 4 installments, one invoice date per quarter, $95k each. AWS invoices Harrow and pays you after it collects, so your cash arrives later than on direct invoices.
- **Offer expiry:** set it to a date in December that leaves Harrow time to accept, such as 15 Dec.
- **EULA:** upload your current renewal paper as a custom EULA, so the legal terms don't change.

**Harrow's side:**

- They need Marketplace procurement permissions in their AWS account.
- They must accept the offer in the console.
- They should check with their AWS rep that this purchase counts toward their spend commitment. Marketplace spend often counts only partly, or up to a cap, and that is the reason they asked for this. Have them confirm it before you invest the effort.

**Direct contract:** end it on 31 Jan, effective when the Marketplace term starts. Do not leave both contracts live. Get Harrow's acknowledgment in writing.

**Timeline:** Monday is 2 Nov. Sending the offer that day is realistic only if the integration test passes and the pricing model is contract. If either fails, tell the AE now, because fixing them can push the offer into mid-Nov.

**Next:** open the Management Portal and check whether the listing's pricing model is contract. Reply with what it says and I'll tell you whether Monday is still possible.

**Open questions:**

1. Where is Harrow based? (Tax.)
2. Is the integration already tested?