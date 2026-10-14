**No, not entirely. Developer-billed shifts most of the tax work to vendors, but it doesn't make tax "entirely theirs."** A contract clause allocates cost between you and the vendor. It doesn't bind tax authorities, and it doesn't remove a legal duty the law puts on you. I'm not a tax adviser, so have tax counsel confirm this before launch next month.

## Where you can still be on the hook

1. **US marketplace facilitator laws (22 states).**
   - Most sales-tax states make the platform collect and remit on sales it "facilitates."
   - The definitions differ. Some require that you collect or process payment, which developer-billed mostly avoids.
   - Others turn on listing, setting terms, or controlling the buyer relationship. Under those you could be caught even though you never touch the money.
   - Whether SaaS or data tools are taxable at all also varies by state.
   - Check each of your 22 states individually. Don't assume developer-billed puts you outside them.

2. **EU VAT deemed-supplier rule (five countries).**
   - Under Article 9a of the VAT Implementing Regulation, a platform facilitating electronically supplied services can be treated as the supplier in its own name.
   - You can rebut that only if you don't authorise the charge, don't authorise delivery, and don't set the general terms of sale.
   - A mandatory developer agreement and marketplace terms can count as setting terms. Have counsel review exactly what your agreement controls.
   - The vendor must also be clearly named as the supplier on invoices and in the checkout.

3. **The 12% of seats going to individuals.**
   - In the EU, a buyer without a valid VAT ID is a consumer. The vendor must charge VAT at the buyer's country rate, usually through the OSS scheme.
   - A buyer with a valid VAT ID gets B2B reverse charge instead.
   - Vendors can only do this correctly if someone captures buyer country and VAT ID. You hold that data at checkout or install, so expect vendors to push it back onto you.
   - In the US, individual versus business status affects exemptions and which states tax the sale.

4. **Tax on your own fee.**
   - Your 12% is your revenue. Depending on the vendor's location, it may carry VAT or reverse charge, or US sales tax in some states.
   - Vendors outside the US or EU may add withholding questions.

5. **The fee base.** "Based on what they report" is ambiguous. State that the 12% applies to the net price, excluding taxes, and give yourself audit rights over the vendor's reports.

## Questions that decide your actual exposure

- Does the buyer purchase through your flow, or is the vendor's checkout fully separate?
- Do you set or constrain vendor pricing, terms, or refunds?
- Do you hold buyer location and VAT ID data that you could pass to vendors?

## The one line

> Vendor is solely responsible for determining, collecting, reporting and remitting all sales, use, VAT, GST and similar transaction taxes on its sales through the Marketplace, and all income and withholding taxes on its own earnings, and will indemnify Company for any such taxes, penalties and interest assessed against Company in connection with Vendor's sales; Company's fees are calculated on prices excluding such taxes, and Company is responsible only for taxes on its own income and on the fees it charges.

If you want it shorter, use this version:

> Vendor is solely responsible for all taxes on its sales through the Marketplace (including sales, use, VAT and income taxes) and will indemnify Company against any such taxes assessed against Company; fees are calculated on prices excluding taxes.

I wouldn't ship the bare "vendors are responsible for all taxes." It reads as covering your own fee tax too, and it has no indemnity or net-of-tax language, so it protects you less than it appears to.

## Before launch

- Run the 22-state facilitator check.
- Have counsel apply Article 9a to the five EU countries.
- Add buyer-location and VAT-ID capture to the install flow.
- Add a tax-excluded revenue field to the vendor report.