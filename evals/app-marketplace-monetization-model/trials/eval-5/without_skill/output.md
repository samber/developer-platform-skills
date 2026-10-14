# Teardown: small-developer fee waiver

**Verdict:** ❌ Don't ship as drafted. The entity rule defeats the waiver, and the process delays and filters out the vendors it is meant to help. Both are fixable, and the fix makes the program simpler.

## 🔴 Blockers

**1. Per-entity allowance makes the threshold meaningless.**
- A vendor with $10M of marketplace revenue can pay 0% by spreading it across 25 shell companies at $399K each. Incorporation costs far less than the $1.5M/year in fees it saves.
- The legitimate case, separate entities that really are independent, is rare. The abuse case is rational for every large vendor.
- **Fix:** apply one allowance per controlled group, aggregated across all apps.
  - Define the group as common ownership above 50%, common control, or a shared payout account, tax ID, beneficial owner or bank account.
  - You already collect most of those fields at payout KYC, so detection can be automatic.
  - Add a contract clause: misrepresenting affiliation means fee recapture at 15% plus a penalty, and delisting.

**2. The cliff at $400K creates perverse incentives.**
- Define the rule as "under $400K pays 0%, over pays 15%." If that means all revenue, a vendor at $390K and a vendor at $410K differ by about $61K in fees on near-identical revenue.
- Vendors near the line will delay launches, discount, shift to off-platform billing, or split entities (see blocker 1).
- You will also get cliff behavior from honest vendors. They stop growing on your platform.
- **Fix:** make it marginal. The first $400K per year is at 0%, and everything above is at 15%. No cliff, no incentive to stay under, and the cost per vendor is capped at $60K/year.

**3. The process delays the benefit by up to six months, and only reaches vendors who apply.**
- Worst case: a vendor applies the day after a review, waits nearly a quarter for review, then waits for the next quarter to start. That is about 3 to 6 months at 15% with no retroactive credit.
- Opt-in forms select for sophisticated vendors. The solo developer earning $20K never finds the form.
- A $400K test is numeric. If the data is yours, nothing needs human review, and one person reviewing quarterly is a bottleneck and a single point of failure.
- **Fix:** compute eligibility automatically from your own ledger. Reserve partner-ops review for disputed affiliation cases only.

## 🟠 Serious gaps

**4. "Trailing 12 months" is undefined.**
- It is unclear whether it means gross or net, and whether it is before or after refunds, taxes, chargebacks, FX or promotional credits.
- It is also unclear whether it counts only your marketplace or all of the vendor's revenue.
- Pick net of refunds and taxes, in one reporting currency, on your marketplace only. Write it into the terms.

**5. New vendors fall into a hole.**
- A vendor with no history either trivially qualifies (reasonable) or has nothing to apply on (broken).
- The new vendors are the ones the waiver should most help. Say explicitly that zero history qualifies.

**6. No re-test or exit rule.**
- The draft is silent on what happens when a waived vendor grows past $400K, and the lag in the process helps them.
- A vendor can apply at $350K, take the waiver, and run at $3M for two quarters before anyone looks.
- With the marginal design this disappears. With a cliff, you need automatic quarterly re-testing and a glide path.

**7. Waiver start date opens a gaming window.**
- Eligibility is tested at application, but the benefit starts a quarter later.
- A vendor can time a launch or campaign to land after the test.
- Test at the start date, not only at application.

**8. App transfers reset the allowance.**
- A vendor can sell or transfer an app to a new entity, which has no trailing history and gets a fresh $400K.
- **Fix:** attach revenue history to the app lineage and aggregate it to whoever holds it.

**9. "Small developer" is not the same as "low marketplace revenue."**
- A large company's side app earning $50K qualifies, while a two-person studio with a $500K hit does not.
- That may be fine, since you are subsidizing apps, not companies. Decide it on purpose and write down the answer.

**10. "0%" is ambiguous.**
- It is unclear whether payment processing, VAT or tax remittance, fraud and support costs are covered by the waiver or still passed through.
- If you absorb processing costs, 0% is a loss on every sale. Spell out what it covers.

## 🟡 Strategy questions to answer before building

- **What is the goal?** Catalog growth, retention, goodwill, or competitive parity? Name one metric, such as apps live after 12 months or vendors crossing $100K.
- **Is fee the real barrier?** For a vendor at $50K, 15% is $7.5K. If discoverability or onboarding is the blocker, the money is wasted. Test with 5 to 10 vendor interviews.
- **What does it cost?** Compute it before launch.
  - Marginal design: 15% × Σ min(vendor revenue, $400K).
  - Cliff design: 15% × total revenue of all sub-$400K vendors.
  - Pull the revenue distribution first. If 90% of vendors are under $400K but hold 8% of revenue, the cost is small. If not, rethink the number.
- **Why $400K?** Its provenance is unstated. Check it against the revenue distribution and against what competing marketplaces offer.
- **Sunset or review date:** a waiver with no review date becomes permanent.

## ✅ Recommended redesign

1. **Marginal waiver, automatic.** First $400K of net marketplace revenue per controlled group per calendar year at 0%. 15% above that. Resets Jan 1.
2. **No application form.** Vendors see their status in the portal.
3. **Controlled-group aggregation** via payout KYC matching (tax ID, bank account, beneficial owner), plus an affiliation attestation at onboarding.
4. **Penalty clause** for misrepresentation: recapture plus surcharge plus delisting.
5. **Partner-ops handles only exceptions:** disputed groupings, acquisitions, app transfers.
6. **Written definitions:** net revenue, currency, what 0% covers.
7. **Review at 6 and 12 months** against the goal metric and the actual cost.

If you must keep the cliff, then evaluate eligibility monthly and automatically, apply it to the controlled group, and add a two-quarter glide before the 15% rate returns.

## Questions for you

1. What is the program's goal and success metric?
2. What does the vendor revenue distribution look like?
3. Do your payout records already hold tax IDs and beneficial owners?
4. Is a marginal 0% on the first $400K acceptable to finance?