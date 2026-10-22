**Do first: pull the 15% waiver rule and the tax registration list, and check them against the numbers below. These two items can make launch day look fine while nothing works.**

## 1. Two blockers to settle this week

**1. The $1M exemption may zero out your take.**
- Gross is 40 × $600 = $24k/month, or $288k/year. Per vendor that is $7.2k/year, about 0.7% of the $1M threshold.
- If the tier means zero share below $1M, you collect $0 from all 40 vendors at launch. The 15% would only apply after a vendor grows about 140x.
- Without the exemption, take would be $3.6k/month ($43.2k/year).
- Confirm in writing what the tier does: waive fully or reduce the rate, and whether it resets each year or is lifetime.
- Also confirm what happens when a vendor crosses $1M mid-year, and whether related accounts are summed.
- Your ops dashboard will show take revenue near $0. Decide now whether that is intended.
- If it is intended, you are effectively zero-take at launch. The skill's default for that case is developer-billed, because collection machinery buys nothing. Marketplace-billed is still defensible if you sell tax, chargeback and billing handling as the product. Make that choice on purpose.

**2. "Automatic tax switched on for 50 states and the EU" is not the same as "registered."**
- Automatic tax calculation with no active registration in a jurisdiction collects $0 and returns no error.
- Past under-collection cannot be fixed afterward. Watching payouts and take revenue will never show it.
- Get the list of jurisdictions with an active registration. It should match where you have nexus, not "all 50." Five states have no state sales tax.
- Make a test charge in 3 to 5 jurisdictions and check that the tax line is non-zero. Include at least one registered state, one unregistered state, and one EU country.
- Check taxability: SaaS and app taxability varies by state.
- Check the EU buyer split:
  - B2C needs VAT collected and remitted. You are the deemed supplier, so file via OSS.
  - B2B is reverse-charged, so you must collect and validate buyer VAT IDs.
  - Do you have any consumer buyers at all?
- Have counsel review the published split. This is not tax advice.

## 2. Check the money mechanics

1. **Charge pattern.**
   - Monthly payouts with a hold window need separate charges and transfers. Destination charges pay the developer automatically on payment success, so they cannot hold funds.
   - Do not use `on_behalf_of`.
   - Confirm the platform carries the losses. Non-direct charges require it, and near-miss dial combinations shift liability to you silently.
2. **Fee base.**
   - Write down what the 15% applies to. It should be net of tax, and the rule should say whether processing is inside or outside it.
   - If processing (about 2.9% plus $0.30) is hidden inside the 15%, the real take is about 12%.
   - Show processing as its own labeled line.
3. **Refunds and disputes after payout.**
   - A refund or chargeback after a monthly payout can leave a negative vendor balance.
   - Define whether the 15% is clawed back on refunds, how a negative balance is recovered, and the hold window (30 to 60 days is the norm).
4. **Unit economics per vendor.**
   - Managed marketplace rails cost about £1.60/month per account, plus 0.25% and £0.20 per payout (Stripe UK pricing; check your region). That is roughly $4 to $5 per vendor per month, or about $2k/year across 40 vendors, before tax tooling and counsel.
   - With the exemption this is a pure cost. Without it, take is about $90 per vendor per month.
   - Also check cross-border payout currency conversion and fees.
5. **Payout timeline.** Publish the honest sale-to-bank number (billing cycle plus hold, likely 45 to 75 days), not "monthly."

## 3. Check the paper

- The published terms state, per vendor population, who owns tax, chargebacks and payouts. Check whether any apps still bill customers directly, and whether you can migrate them.
- The pricing models you promise are supported by your checkout. Verify usage-based pricing against the rails before you publish it.
- The anti-circumvention rule has a delisting path.
- The fee-change notice period (the sourced pattern is 6 months) is committed in writing.
- The tax split is published jurisdiction by jurisdiction.
- Eligible vendors are enrolled in the waiver automatically. A manual opt-in silently charges them the full rate.

## 4. Fix the dashboard

Payout volume and take revenue are the two numbers least likely to show a problem. Add:

1. Tax collected per jurisdiction, with an alert on $0 tax lines for taxable sales. Add registration coverage of transaction volume.
2. Net take minus billing-ops cost, not headline take.
3. Median sale-to-bank days against the published timeline.
4. Dispute and refund rate, with losses attributed to the owner the terms assign.
5. Waiver coverage among eligible vendors, plus circumvention incidents.

## 5. Order of work for the three weeks

- **Week 1:** confirm the waiver rule and the registration list, and run the test charges.
- **Week 2:** confirm the charge pattern and fee base, and settle the refund, hold and timeline rules. Send the tax split to counsel.
- **Week 3:** publish the terms and add the dashboard metrics. Run a dry-run payout cycle for 2 or 3 vendors.

## Assumptions to confirm

- Buyers: B2B only, or any consumers?
- Is the billing provider Stripe-like? Mechanics above follow Stripe Connect.
- Are there apps already billing customers directly that you cannot migrate in one cycle?

I did not ask the skill's 10 interview questions one at a time. Your recap covered take rate, tax, payouts, exemption and dashboard, so I assumed the rest. The answers above to buyer type, billing provider and legacy apps could change items 2, 3 and 5.

**Next: open the waiver rule and answer these two questions: "does the $1M tier zero the 15% for all 40 vendors?" and "which jurisdictions have an active tax registration?"**