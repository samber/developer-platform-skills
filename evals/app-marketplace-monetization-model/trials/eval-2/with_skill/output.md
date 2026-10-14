**Short answer: no, not entirely.** A developer-billed model makes the vendor the merchant of record. It doesn't make tax theirs by law. A contract clause only allocates tax between you and the vendor. It doesn't bind a state or an EU tax authority, and a one-line "vendors are responsible for all taxes" clause hides the parts that matter.

I skipped the full interview and assumed the 12% take-rate is already decided. I'm not re-opening your developer-billed choice. A hard launch date next month favors the simplest posture, which is yours. The consequences of that choice are below.

## Where "tax is entirely theirs" breaks

1. **Facilitator and deemed-supplier rules attach by law, not by billing posture.**
   - US marketplace-facilitator statutes exist in most sales-tax states (since *Wayfair*) and can put collection and remittance on the platform.
   - Whether they reach you when the vendor charges on its own processor depends on each state's definition of "facilitator". Some key on payment processing, some on listing plus other criteria. I can't tell you the answer for your 22 states, and counsel has to check each one.
   - Tax law and card-network merchant-of-record status are legally distinct and don't always coincide.
2. **The 12% of seats bought by individuals changes the EU picture.**
   - The EU deemed-supplier rule targets B2C supplies. B2B cross-border VAT is normally reverse-charged to a business buyer.
   - A consultant buying as an individual, with no VAT ID, is treated as a consumer. That's the case where the platform is most likely to be exposed, and where reverse charge doesn't help.
   - Whether the rule reaches your app category and vendor locations is a counsel question. Scope is also widening under the 2025 ViDA package.
3. **Someone has to collect the VAT ID and buyer type at checkout.** That's the vendor, so your agreement has to require it. Otherwise you can't prove which sales were B2B.
4. **Vendors may not be registered anywhere.**
   - Automatic tax calculation with no active registration silently collects $0 and returns no error.
   - Under-collected past transactions can't be fixed retroactively.
   - A one-person vendor selling into 22 states and 5 countries is the most likely case. Monitor tax collection as its own system.
5. **Your own 12% fee is a taxable supply.** You may owe VAT or sales tax on what you invoice vendors. Your fee has to be defined on the net price, excluding tax. Otherwise you take 12% of the tax too.

## What your model also needs

You collect the 12% from vendor self-reports, which is the only way to collect a percentage under developer-billed. That makes these three items mandatory:

- An **audit right** over vendor sales records.
- An **anti-circumvention rule with a delisting path.** Without the delisting path it's only a preference.
- A written **notice period for fee changes.** The sourced pattern is six months.

## Deliverable: replacement clause

**One-line version (replaces yours):**

> Vendor is the seller and merchant of record for every app sale and, as between Vendor and Platform, is solely responsible for determining, registering for, collecting, reporting, and remitting all taxes on those sales, and shall indemnify Platform for any such tax Platform is legally required to collect or pay; Platform's fee is calculated on the net price excluding taxes, and Platform may collect and remit tax where law requires and recover it from Vendor.

**Companion clauses (three short ones, same section):**

1. **Reporting.** Each quarterly report states, per sale: buyer jurisdiction, business or individual status, VAT ID where provided, and tax collected.
2. **Evidence.** Vendor keeps those records for the retention period counsel sets, and Platform may audit them.
3. **Registration.** Vendor warrants it holds, or will obtain before its first sale, the tax registrations its sales require.

## Tax split to publish

The skill's rule is a published jurisdiction-by-jurisdiction split, never a single toggle. This is the skeleton. The "Platform exposure" column is deliberately open until counsel fills it.

| Jurisdiction / buyer | Collect and remit | Platform exposure |
|---|---|---|
| 22 US states, business buyer | Vendor | Counsel to check each state's facilitator definition |
| 22 US states, individual buyer | Vendor | Same |
| 5 EU countries, business buyer with valid VAT ID | Vendor, reverse charge | Lighter |
| 5 EU countries, individual buyer | Vendor (OSS or local registration) | Deemed-supplier question to confirm |
| Platform's 12% fee, vendor to Platform | Platform | Your own VAT and sales-tax registration |

## Before you ship

- ⚠️ Have counsel review the split. I can't confirm any state's or country's rule, and this is not tax advice.
- ⚠️ Ask counsel two specific questions: do facilitator statutes in your 22 states reach a developer-billed listing, and does EU deemed-supplier treatment reach your individual buyers.
- ℹ️ Start tax-collection monitoring at launch: vendors with no registration, and sales with no buyer-type data.
- ℹ️ Re-check this when volume grows. A take-rate with self-reported collection is the weakest collection mechanism, and the skill's promotion condition is to move to marketplace-billed once you charge a cut. Your launch date justifies deferring that, not dropping it.