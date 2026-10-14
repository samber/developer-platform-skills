# Pre-launch review: marketplace as merchant of record

**Do first:** confirm tax registrations exist, because "auto tax is on" does not mean you are collecting or remitting. Registrations are the long-lead item and you have about 3 weeks.

## Your numbers, for sanity checks

- Gross is about $24,000/month ($288k/yr).
- Take is $3,600/month at 15% ($43.2k/yr).
- Payouts are $20,400/month before processor fees, refunds and tax.
- The $1M exemption tier is about 3.5x your annual volume, so no vendor and not the marketplace will reach it at launch.

## 🔴 Blockers (fix before the switch)

1. **Registrations vs calculation.**
   - Most billing providers calculate tax everywhere but collect only where you have entered a registration. An unregistered state silently yields $0 tax, and your dashboard will look fine.
   - Check which states and EU countries you are actually registered in.
   - Collecting tax without a permit is itself unlawful in many states.
   - Registrations take days to weeks, so start now.
2. **Who files and pays.** Calculation is not filing. Name the owner, the calendar and the cash for each return: state returns, EU OSS quarterly, and any UK, Canada or Australia filings.
3. **EU thresholds.**
   - A non-EU seller has no €10k threshold. VAT applies from the first euro, via non-Union OSS.
   - Where are you established? The answer changes the rules.
   - Also confirm the vendor→you VAT leg, because platforms are presumed to supply in their own name. Get an advisor's sign-off.
4. **The "$1M annual exemption tier."** I can't tell what it exempts, so tell me or document it.
   - If it is meant as a tax threshold, it is wrong. US economic-nexus thresholds are mostly $100k per state (CA and TX $500k), and the EU has none for non-EU sellers.
   - If it is a fee tier, nothing exercises it at launch. Test it with a synthetic vendor.
5. **Scope gap.** The plan says "50 states + EU", which leaves out DC, Puerto Rico, the UK, Canada, Australia and the rest of the world.
   - Decide whether to block those buyers or register there.
   - Some states also have local taxes (CO, AL, LA, AK).
6. **Tax-inclusive vs tax-exclusive math.**
   - The vendor share (85%) and your take must be computed on the pre-tax amount.
   - EU prices shown tax-inclusive can make you pay vendors on VAT. This is the likeliest silent overpayment.
7. **Product taxability.** Check the tax code per app (SaaS, digital good, B2B).
   - Taxability varies by state (TX, NY, WA, PA and others).
   - Who sets the code, you or the vendor?

## 🟠 Payout and vendor compliance

8. **Onboarding gate.** Block a vendor's first payout until they have completed KYC/KYB, sanctions screening, and a W-9 or W-8.
   - Missing TINs mean 24% backup withholding.
   - Foreign vendors may face 30% withholding on US-source royalties unless a treaty applies.
   - Confirm with a CPA whether 1099-K or 1099-NEC applies. Vendors at about $6.1k/yr net exceed the thresholds.
9. **Holding funds.** Collected tax is a liability, not revenue or payout money. Check that it is segregated and that you are not creating a money-transmitter problem. Using your provider's connected-account payouts usually avoids this.
10. **Refunds, disputes, clawbacks.**
    - Does a refund also refund the tax?
    - Who eats the chargeback fee?
    - What happens when a vendor's balance goes negative before payout?
    - Who pays processor fees: you out of the 15%, or the vendor? At roughly 3% fees, your real margin is about 11–12%.
11. **Vendor contract.** Cover the MoR relationship, payout timing, reserves, refund policy, and the ban on vendors also collecting tax.
12. **Existing customers.** Tax now appears on top of the price. Decide whether to absorb it or notify customers, and handle existing subscriptions and their notice terms.

## 🟠 Test matrix (staging, before the flip)

Run each case end to end through charge, ledger, payout and dashboard:

- US: a taxable state, a no-sales-tax state (OR), and a registered vs an unregistered state.
- EU: B2C (DE 19%), B2B with a valid VAT ID (reverse charge), and an invalid VAT ID.
- Missing or conflicting billing address.
- Full refund, partial refund, and dispute.
- Payout below the minimum, payout failure and retry, and vendor offboarding mid-month.
- A synthetic vendor that crosses the $1M tier.

## 🟠 Dashboard: payout volume + take is not enough

Both metrics come from the same flow and will happily agree with a wrong number. Add:

- **A reconciliation identity, checked daily:** gross charges = vendor payouts owed + take + tax collected + processor fees + refunds + reserves. Alert on any non-zero residual.
- **Payout/take ratio:** it must stay at exactly 85/15 on tax-exclusive amounts. Drift means a bug.
- **Tax liability by jurisdiction** against registrations, plus a "sales with $0 tax" alert.
- **Trailing-12-month sales by state and EU country**, to flag approaching nexus thresholds.
- **Tax-calc errors**, such as unrecognized locations.
- **Refunds, disputes, payout failures**, and **vendor concentration** (40 vendors on an average hides skew).
- **Take definition:** exclude tax, and decide principal vs agent for revenue recognition (MoR for tax is not automatically principal for accounting).

## ⏳ Timing trap

Payouts are monthly, so the first one lands about 5 weeks after launch. Errors would pile up unseen for 30 days. Run the daily reconciliation from day 1, and do a dry-run payout in staging before launch.

## Questions I need answered

1. Where are you established, and which registrations do you hold today?
2. Is the $1M tier a fee tier, a tax threshold, or something else?
3. Are prices shown tax-inclusive or tax-exclusive?
4. Which billing provider, and who files returns?
5. Are your vendors mostly US-based or international?

I did not read anything under `skill-wip/`. This is a checklist for your advisors, not legal or tax advice. Have a tax professional confirm items 1–3 and 8.