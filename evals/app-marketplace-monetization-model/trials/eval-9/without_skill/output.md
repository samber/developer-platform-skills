# Poking holes: Jan 1 merchant-of-record cutover and $4M off-marketplace pull

**Verdict:** ❌ Don't commit to this as written. There are about 90 days to Jan 1 (as of 2026-10-03). The plan stacks three irreversible bets on two engineers and no compliance owner. The "$4M" is the weakest piece and should come out of the forecast.

This is based only on what you told me. I don't know your jurisdictions, processor, take rate, or contract wording, so I've flagged where the answer depends on those.

---

## 1. Legal and compliance (the biggest gap)

Becoming merchant of record (MoR) makes you the legal seller of 180 apps' products. That is a different business from a directory.

- **Tax is yours.** You must register, calculate, collect, and remit sales tax, VAT, and GST wherever you have a liability.
  - US marketplace-facilitator laws apply per state.
  - EU/UK VAT applies (OSS, B2B reverse charge, VAT-ID validation).
  - Some countries require e-invoicing in a mandated format.
  - A tax-calculation tool (Stripe Tax, Avalara, Anrok) computes the amount. It does not register you, file returns, or take on liability.
- **Money handling may be regulated.** If you collect funds and pay out to apps, check whether you are a money transmitter, payment facilitator, or "commercial agent" under PSD2-style rules. The answer depends on your funds-flow design and jurisdictions, and it needs counsel. Getting it wrong is a licensing problem, not a bug.
- **KYB, AML, and sanctions on 180 payees.** You need onboarding checks, ongoing screening, and tax forms (W-9/W-8, 1099s). EU platform reporting (DAC7) likely applies.
- **Customers' claims now run against you.** The customer's seller of record is you. Your terms must allocate warranty, SLA credits, refunds, indemnity, and IP between you and each app. Today, 180 separate app contracts do that.
- **Accounting.** Gross vs net revenue (principal vs agent) is an audit question, and the answer changes your reported revenue.
- **Card network and acquirer rules.** Underwriting, restricted categories, and your acquirer's willingness to onboard some apps (crypto, health, adult, and so on). "No exceptions" will break on the first app your acquirer refuses.
- **No compliance headcount.** Someone must own filings, notices, audits, and regulator contact. Outside tax counsel and a payments lawyer are the minimum, and they should be in place before December. Budget for them in the plan.

## 2. Existing contracts and the "no exceptions" rule

- **Three-year contracts signed last year.** I can read this two ways, and both are problems.
  - If these are app-to-customer contracts with their own pricing and payee, you can't unilaterally reroute them. Customers must agree to a new payee, invoice entity, and terms (novation or amendment).
  - If these are your own agreements with apps that let them bill directly, forcing migration is a breach. That means damages exposure, plus leverage for those apps in negotiation.
  - Check change-of-terms, assignment, MFN, and termination clauses now. Read the real wording rather than relying on the summary.
- **Customer-side friction.**
  - New payee means new vendor onboarding, new bank details, and new PO matching.
  - Finance teams will reject invoices from an unfamiliar entity.
  - A payee-change email looks exactly like invoice fraud, and customers are trained to distrust it.
- **Apps' own side effects.** Their processor contracts may carry minimums or termination fees. Their revenue recognition, CRM, investor reporting, and tax treatment change (they now sell wholesale to you). Some will refuse, or leave the marketplace.
- **"No exceptions" is a promise you can't keep.** Sanctioned jurisdictions, restricted categories, and signed contracts will force exceptions. Design them deliberately (a defined exception policy and end date) instead of discovering them in January.

## 3. Single cutover on Jan 1

- **Card tokens don't move for free.** Moving saved cards between processors needs a PCI-compliant token migration with the old processor's cooperation, often weeks per processor.
  - Direct debit mandates (ACH, SEPA) need re-authorization.
  - Without migration, customers re-enter payment details, which means involuntary churn.
- **Double billing and gaps.** Whenever app-side billing and yours overlap, customers get charged twice. If the app stops billing before you start, nobody bills.
- **Mid-term money.** For annual prepaid plans, who owes the unused balance, and how is deferred revenue handed over? Usage-based plans need metering continuity. Proration, credits, and refunds need a rule per app.
- **The date is bad.**
  - Jan 1 sits on year-end close and the holiday freeze, when staff are absent.
  - Annual renewals cluster in January.
  - Many tax rates change on Jan 1.
  - Customer budgets reset.
  - You'd have roughly 60 working days to build, test, and migrate, and no rollback on a big-bang move.
- **No rollback means no safety.** If the cutover fails for 30 apps, you are failing for everyone at once, in your highest-traffic month.

## 4. Capacity: two engineers

Rough math: 180 apps over ~60 working days is 90 apps per engineer. That leaves less than one working day per app for plan mapping, tax categories, currencies, testing, and partner communication. It also leaves nothing for building the platform itself.

- **Ongoing load after cutover.** Refunds, disputes, chargebacks, invoice requests, payout reconciliation, dunning, and tax filing support all land on the same two people. There's no on-call depth and a bus factor of one per domain.
- **Reconciliation.** Daily settlement-to-ledger-to-payout matching for 180 payees is full-time work on its own.
- **Payout risk.** If an app goes insolvent after you've paid it, refunds and chargebacks on its sales come back to you. You need reserves, holdbacks, and clawback terms.
- **Buy, don't build.** A true MoR provider (Paddle, FastSpring, or a similar white-label arrangement) takes on tax and compliance liability for a fee. Check that fee against your take rate. It may still beat hiring.

## 5. The $4M off-marketplace revenue

- **Why would partners move?** They'd pay your take rate on deals they closed themselves. At an illustrative 10–20%, that's $400K–$800K of margin transferred from partners to you. They'll read this as a tax on their own sales.
- **Custom terms don't fit a marketplace.** Private deals often have negotiated pricing, net-60 payment terms, wire payment, bespoke SLAs, and the customer's own paper. As MoR, you inherit obligations you didn't negotiate.
- **Contract and relationship risk.** Check whether your partner agreements restrict or allow charging fees on deals you didn't source. Forcing it risks breach claims, and it will push partners to move off the directory.
- **The number is soft.** Where does $4M come from? If it's partner self-reported, it's unverified and may have been shared in confidence. It probably isn't all recurring, and some of it likely sits in the same three-year contracts.
- **It adds liability.** Every extra dollar of volume adds tax exposure and chargeback risk for deals you can't see into.

**Recommendation:** forecast $0 of it. Treat it as an opt-in upside with a partner-facing incentive (lower take rate on migrated deals, co-selling, faster payouts). Never make it mandatory.

---

## What I'd do instead

1. **Weeks 1–2: stop and verify.**
   - Pull all 180 contracts and flag the three-year ones.
   - Hire payments and tax counsel.
   - Confirm whether your funds flow needs licensing.
2. **Decide build vs buy for tax and compliance** (true MoR provider, or Connect-style platform plus tax tool). Decide this before writing code.
3. **Replace the single cutover with waves.**
   - Wave 0: 5 friendly apps, with no contract conflicts.
   - Wave 1: about 25 apps.
   - Wave 2: the rest.
   - Wave 3: the three-year-contract apps, on negotiated terms, with an explicit exception policy.
   - Keep "everything is MoR" as the destination and a stated date for the last wave. Pick a mid-quarter start date, not Jan 1.
4. **Set go/no-go gates before each wave:** tax registrations live, token migration tested, dispute and refund runbooks written, payout reconciliation passing for 30 days, and customer comms sent.
5. **Staff it.** At minimum, add a compliance/finance-ops owner and a third billing engineer, or contract them out for the migration.
6. **Take the $4M out of the plan.** Run it as a separate, voluntary program after the core migration is stable.

## Questions only you can answer

- What are the three-year contracts, exactly (who signed with whom, and what do they say about payee and termination)?
- Which jurisdictions do your customers and apps sit in?
- What take rate are you planning, and what do apps pay today?
- Where does the $4M figure come from?
- Is Jan 1 fixed by something external (investor commitment, contract, announcement)? If so, what is it?
- What does "billing on their own processors" involve per app (Stripe, Adyen, invoices, or a mix)?

I did not read anything under `skill-wip/`, as you asked.