**Verdict: do not ship "all 180, single cutover, no exceptions" on Jan 1.** It fails the skill's own gates, and your team size makes it unsafe. Keep Jan 1 as the date the marketplace-billed model goes live. Cut over new apps and volunteers then, and migrate the rest as their contracts end.

**Next action:** answer the 4 questions in "Unknowns" below. Two of them (take-rate decided? existing invoice cycle?) can flip the design.

## What I know and assume

- Today is 2026-10-03, so Jan 1 is about 90 days away.
- Question 7 is yes: 180 apps already bill directly, some on 3-year contracts signed in 2025 that run to about 2028.
- Question 8 is a hard date.
- Question 10 is a very low effort ceiling: 2 billing engineers and no compliance.
- Assumed, not stated: you charge a non-zero take-rate. If it is zero, the skill says do not build collection at all.

## Contradiction in the brief

The skill gives two opposing rules here:
- A legacy population that can't migrate in one cycle promotes the "configurable per app" posture.
- A low effort ceiling deletes that same posture.

Your brief demands the one outcome neither rule allows: no legacy branch and no capacity to build it. Something has to give. The fix is to shrink scope, not to add a second billing branch. See "Recommended design".

## Blockers (each one alone breaks Jan 1)

1. **Three-year contracts.**
   - Those contracts are between the developer and their customer. You are not a party.
   - Moving the payee, invoicing entity, tax treatment and payment instructions mid-term needs customer consent and often a contract amendment.
   - Customers' accounts-payable teams treat "new bank details, new vendor" as an invoice-fraud signal. Expect holds and vendor re-onboarding.
   - The fixed price also bites. The developer can't reprice, but now loses your share plus processing out of a locked price.
   - Customers with annual or PO invoicing will not pay by card on your rails.
2. **Notice.**
   - The skill's pattern is 6 months' written notice for fee changes. Going from 100% kept to a take is the largest fee change possible.
   - Announce today and the pattern-compliant date is about 2027-04-03, not Jan 1.
   - "No exceptions" with 90 days' notice is the unannounced-increase failure mode.
   - Check your developer agreement: can you change the billing model unilaterally?
3. **Tax with zero compliance headcount.**
   - Marketplace-billed makes you collect and remit. US marketplace-facilitator laws apply in most sales-tax states. EU deemed-supplier VAT applies to B2C. Neither depends on your billing posture, and both attach now.
   - Silent trap: automatic tax with no active registration collects $0, raises no error, and can't be corrected later. Registrations must be live before Jan 1, with their own monitoring.
   - Nobody owns the published jurisdiction-by-jurisdiction split, and counsel must sign it off.
   - 90 days is tight for registrations plus a counsel review.
4. **Developer cash-flow cliff.**
   - On Jan 1, 180 developers stop receiving cash directly. Under monthly payout plus hold, the first money arrives about 30-60+ days later. Sourced lags run up to about 68 days.
   - All 180 hit that gap in the same month. Some will be unable to cover payroll and will leave or reroute billing.
   - Only rolling payouts with reserves avoid it, and those need more engineering.
5. **Two engineers cannot build the system.**
   - The marketplace-billed system has at least 7 parts: checkout, entitlements and licensing, netting at source, payout and holds, refunds and disputes, tax monitoring, and developer reporting.
   - Salesforce runs payment, license and reporting as three separate systems.
   - Migrating 180 live subscriptions is a separate project from the build. Card tokens sit in each developer's own processor, so you need processor-to-processor transfers or customer re-entry. Prorations, trials, usage history and credits all move too. (This is general payments knowledge, not in the skill; verify.)
   - Add dispute and billing support, and the 2 people are underwater before launch.

## Serious holes

1. **Rails cap the pricing menu.**
   - Existing apps likely use per-seat, usage-based and negotiated enterprise pricing. Some checkouts support only one-time and subscription.
   - Verify every pricing model across the 180 apps against the rails before promising migration.
   - The skill also asks that each pricing tier be a separate product object.
2. **You absorb the losses.**
   - The marketplace bundle forces the platform to carry disputes, refunds and fraud. You haven't said whether you accept that (question 6).
   - Large B2B tickets mean large chargebacks.
3. **Pre-cutover money.** Prepaid years from 2025-26 sit with the developer.
   - Define the boundary by invoice date. Pre-cutover refunds stay with the developer.
   - Otherwise you inherit service and refund liability on revenue you never collected.
4. **Enforcement has no credible threat.**
   - The skill's enforcement pair is a delisting path plus an anti-circumvention rule.
   - Delisting 180 apps, some critical, harms your own customers. Rerouting pressure peaks right at cutover.
5. **Gate failures.** The skill's gate 1 needs posture stated per app population with tax, chargeback and payout ownership assigned. "One posture, no exceptions" hides at least 4 populations: new apps, volunteers, legacy short contracts, and legacy 3-year contracts. Gate 3 needs the published payout timeline and tax split before launch.

## The $4M off-marketplace revenue

This is the skill's "back-book," so it promotes the migration incentive. It is also the weakest assumption in the plan.

- **Wrong incentive direction.** Partners closed these deals outside the directory, probably to avoid the share. Pulling them in means offering better terms than today. At a 15% share the gross prize is about $600K per year (rate assumed; use yours). Waiving fees for year one, as the sourced programs do, makes year-one net near zero.
- **You don't control the contracts.** These are partner-customer agreements. Re-papering needs the same consents as blocker 1, and many are probably multi-year too.
- **Unverified base.** $4M is probably self-reported. The incentive needs attestation and eligibility checks. Microsoft uses self-attestation with a 50% fee cut on renewals. Build that check or you pay for deals that were never off-platform.
- **Overlap.** Check whether any of the $4M sits in the 180 apps already. Count each deal once.
- **Heavier exposure.** Large private deals bring custom pricing, POs and invoicing, big tax amounts and big disputes. The rails need private-offer support, which many checkouts lack.
- **Timing.** Plan on renewals as deals come up, not a Jan 1 lump. Treat a small fraction in year one as realistic until you have signed intent.

## Not in the skill (verify with counsel and finance)

- **Money handling:** KYC and KYB on 180 developers, sanctions screening, and money-transmitter exposure when you hold and pay out third-party funds. Managed rails may cover this; confirm.
- **Year-end reporting:** a Jan 1 cutover lands payout and tax reporting on you. Developers will expect tax forms and, in the EU, platform-reporting rules (DAC7) may apply.
- **Accounting:** principal versus agent revenue treatment changes your reported revenue.
- **Calendar:** Jan 1 sits in year-end close, a holiday freeze and a quarter boundary.

## Unknowns that change the design (answer one at a time)

1. Is the take-rate decided (level, tiers, any zero-take)? If not, stop and run `connector-marketplace-strategy` first.
2. Do you already bill these customers on an invoice cycle? If yes, consolidating onto that invoice is the cheapest variant and removes most of blocker 5.
3. Which pricing models do the 180 apps use today? This sets what the rails must support.
4. Will you absorb chargebacks and refunds? A no on question 6 kills marketplace-billed.

## Recommended design

1. **Rails:** managed marketplace bundle (platform owns charge and losses, express dashboard). Use destination or separate charges. Do not use `on_behalf_of`.
2. **Jan 1 scope:**
   - All new paid apps go marketplace-billed.
   - Existing apps opt in with a migration incentive.
   - Apps whose contracts roll off migrate at renewal.
3. **Legacy branch (the skill's closing legacy path):**
   - Announce an end date and the 6-month notice now.
   - Legacy apps stay developer-billed until their contract ends. The share on them is either zero until then, or audited self-reported share (the starved fallback, built only if you accept the audit cost).
4. **Cohorts:** cap each wave at roughly what 2 engineers can migrate and support. Start with about 10-20 apps. Waves 2 and up follow once wave 1 reconciles cleanly.
5. **Payout:** monthly plus hold sized to refund exposure as the default. Rolling payouts with reserves only if cash-flow churn shows up in wave 1. Publish the real sale-to-bank timeline.
6. **Waiver:** revenue-exemption tier at the $1M anchor, default-enrolled. Decide annual versus lifetime up front.
7. **Tax:** counsel signs off the split first. Registrations go live before the first collected dollar. Add a separate monitor that alerts on $0 tax lines.
8. **Back-book:** sequence migration incentives behind wave 1, tied to verified attestation, and forecast it by renewal date.

## Pre-launch checklist

- Fee-change notice published, 6 months out.
- Developer agreement amended and signed.
- Tax split signed off by counsel.
- Registrations active in every jurisdiction where you collect.
- $0-tax monitor running.
- Sale-to-bank timeline published in the developer docs.
- Pricing models verified against the rails.
- Pre-cutover refund boundary defined.
- Wave-1 apps picked.

Each item maps to the three measurement gates from the skill; none is optional.

**Next:** reply with your answer to unknown 1 (is the take-rate decided?).