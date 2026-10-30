# Docuvane: commercial launch plan for the AppExchange package

I haven't configured anything. I can't reach your Partner Console, LMA, or Checkout enrollment, so this is the design and checklist for you to execute. I also didn't verify Checkout's current capabilities. The points marked ⚠️ rest on my knowledge of Checkout, so confirm them with your Salesforce partner manager before you build on them.

## 1. Selling everything through Checkout won't work

Two parts of the brief conflict with how Checkout works.

1. ⚠️ **Checkout doesn't meter usage.** It sells fixed products: per-user or flat subscriptions and one-time items, with quantities you set. It doesn't ingest "documents processed" and bill $0.02 per unit in arrears. Your pricing is a flat fee plus metered usage.
2. ⚠️ **Three-year contracts with custom discounts don't fit Checkout's standard catalog.** Checkout expects list-price products with terms and discounts defined in advance. Bespoke enterprise paper normally runs outside it.

There is also a customer-side problem. Procurement teams at the companies who sign three-year contracts don't avoid invoices. They usually require POs, invoices, MSAs, and security paperwork. A card on file for a six- or seven-figure commitment will stall those deals. Card-on-file is right for small and mid-market buyers, but it is probably the wrong default for your biggest deals.

**Recommendation: two lanes.**

| | Lane A: Self-serve | Lane B: Enterprise |
|---|---|---|
| Buyer | SMB and mid-market, no negotiation | Large orgs, 3-year deals, custom discount |
| Channel | AppExchange Checkout, card on file | Direct paper (MSA, order form, invoice/PO) |
| Provisioning | Automatic through LMA | You create or extend the license in LMA by hand |
| Pricing | Fixed tiers with prepaid document bundles | Committed annual spend, tiered per-document rate |

## 2. Lane A: Checkout catalog (metered pricing converted to fixed products)

Your $300 platform fee is a clean fit as a flat monthly Checkout product. The $0.02 per document has to become prepaid bundles.

**Products (USD, monthly, per org):**

| Product | Price | Effective rate |
|---|---|---|
| Platform | $300/mo | n/a |
| Document bundle S, 10,000 docs/mo | $200/mo | $0.020 |
| Document bundle M, 50,000 docs/mo | $900/mo | $0.018 |
| Document bundle L, 250,000 docs/mo | $4,000/mo | $0.016 |

- Bundle prices are my placeholders. Your list price is $0.02, so S matches it exactly. M and L are volume breaks you should check against margin.
- A customer can buy one bundle at a time. Bundles don't stack.
- Anything above 250,000 docs/mo goes to Lane B.

**Overage handling.** Checkout can't bill for it, so choose one:

1. **Hard cap (recommended for launch).** The package stops processing at the bundle limit and shows an in-app upgrade prompt. It's predictable and needs no billing integration. The risk is a customer outage at month-end, so alert at 80% and 100%.
2. **Soft overage billed by you.** You report usage and invoice overage outside Checkout. This brings back the invoicing you wanted to avoid, and it may cut across your Salesforce revenue-share terms.

**Package work this requires:**
- Count documents per org per billing period, keyed to the LMA license.
- Read the bundle entitlement from the license, using custom license fields or a feature parameter.
- Add cap enforcement and the 80%/100% notifications.
- Reset the counter at the license billing anniversary, not the calendar month.

## 3. Lane B: enterprise terms

- **Structure:** a committed annual platform fee plus a prepaid document commitment, with a lower per-document rate at higher commits. Keep the $300 platform fee per org, but cap it or discount it by org count for large estates.
- **Rate card (draft):**

| Annual committed spend | Per-document rate |
|---|---|
| Under $25k | $0.020 |
| $25k to $100k | $0.016 |
| $100k to $500k | $0.013 |
| Over $500k | Negotiated, with approval |

- **Discount governance:** reps may discount up to 15% on their own authority. Up to 30% needs the CEO or CFO. Anything beyond that needs a written business case. Never discount the per-document rate below your floor. Set the floor from your cost to process a document.
- **Contract mechanics for 3-year deals:**
  - Annual billing in advance, with a fixed price or a capped uplift (for example CPI or 5%, whichever is lower) in years 2 and 3.
  - Unused documents roll over for at most one year, or expire. Decide this explicitly.
  - Overage at the contracted rate, billed quarterly in arrears.
  - Termination for convenience is not allowed in the committed term.
  - Auto-renewal with a 90-day notice window.
- **Provisioning:** after signature, create or extend the license in LMA with the right seats, expiry date, and entitlement. Record the contract ID against the license.

## 4. Open items to settle before launch

These affect the numbers above:

1. **Checkout eligibility and terms.** Is a Toronto entity enrolled? Which currencies and countries are supported? Who is merchant of record, and who collects and remits tax (Canadian HST/GST, US sales tax, EU VAT)? What are the fees and revenue share?
2. **Revenue share on direct deals.** Does your Salesforce partner agreement apply a share to Lane B sales made outside Checkout? Get this answer in writing.
3. **Whether Checkout now supports usage-based or custom-quote products.** If it does, Lane A could be metered and Lane B could partly move into Checkout. Ask your partner manager directly.
4. **Currency.** Decide whether to list in USD only or also CAD, and how your accounting handles FX.
5. **Cost per document.** The rate card and discount floor are guesses until you know your processing cost, including any third-party OCR or LLM spend.
6. **Free trial.** Decide whether to offer one, for how long, and with what document cap. The AppExchange trial mechanism is separate from Checkout.
7. **Support and SLA tiers.** Decide whether these are bundled or sold as an add-on, and what you promise in the order form.

## 5. Launch checklist

1. Confirm Checkout enrollment, tax, and merchant-of-record details (item 1 above).
2. Answer the revenue-share question for direct deals (item 2).
3. Build metering and cap enforcement in the package, and ship it as a new package version.
4. Create the Checkout products and price points in the Partner Console. Test a purchase end to end in a sandbox org, including cancellation and upgrade from bundle S to M.
5. Draft the MSA, order form, and rate card for Lane B. Have counsel review them, including Canadian and US law and data-processing terms.
6. Set up the enterprise path: a quote template, discount approval flow, and an LMA provisioning runbook.
7. Publish the pricing on your listing and website. The listing should show Lane A prices and say "Contact us" for volume above 250,000 docs/mo.
8. Test the cap, the notifications, and the license-renewal reset with real licenses.
9. Brief sales and support on the two lanes and how to route a buyer who starts in the wrong one.

## 6. Decisions I need from you

- Do you accept two lanes, or is Checkout-only a hard business requirement? If it is, enterprise deals need Salesforce's help, and I'd ask them about that first.
- Hard cap or soft overage for Lane A?
- What's your cost per document, so we can check the rate card and the discount floor?
- Does the Toronto entity transact in USD or CAD?