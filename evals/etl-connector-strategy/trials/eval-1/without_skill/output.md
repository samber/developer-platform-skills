# Business case: ELT source connector for Cadenza

**Ask:** Fund about 9 weeks of engineering (about $135K all-in) plus about $60K/yr to maintain it.
**Recommendation:** Fund it as a gated build, not a revenue bet. Spend 2 weeks first on demand evidence (see Gate). The numbers below are my assumptions, so replace them with your actuals.

## Why this isn't like the reseller and referral deals

Those deals had a counterparty, a commission, and a trackable deal. A connector is a product feature with no contract and no revenue line of its own. Its revenue shows up in three indirect places:

1. **Retention.** Customers who pipe schedules and labor data into their warehouse switch away less often.
2. **New logos.** Buyers whose shortlist requires "works with our data stack" start considering us.
3. **Expansion.** An optional paid analytics or data-sync tier.

None of these is tracked today. Without tagging, the CFO would be approving a revenue line nobody can later verify.

## Cost

| Item | Estimate | Basis |
|---|---|---|
| Build | $108K | 3 engineers × 9 weeks × about $4K/week loaded |
| PM, QA, docs, launch | $27K | Assumption |
| **Build total** | **$135K** | Spent by about month 3 |
| Maintenance | $60K/yr | About 0.3 FTE for API drift and support |
| **Year-1 cash cost** | **about $180K** | Build plus 9 months of maintenance |

## Revenue line and payback

Starting points from your numbers: $18M ARR over 1,400 customers is about **$12.9K ACV**, and **1 point of churn is $180K ARR**.

Assumptions: revenue starts at month 4 and ramps linearly to its month-12 level, with 80% gross margin on new-logo ARR. Payback is measured from kickoff.

| Scenario | Churn avoided | New logos | Incremental ARR at month 12 | Payback |
|---|---|---|---|---|
| Low | 0.25 pt ($45K) | 2 ($26K) | about $70K | Never (maintenance exceeds margin) |
| Base | 0.5 pt ($90K) | 6 ($77K) | about $170K | About 32 months |
| High | 1.0 pt ($180K) | 12 ($155K) | about $335K | About 16 months |

**Break-even:** The connector needs about **$290K of attributable ARR by month 12 (1.6% of ARR)** to pay back in 18 months. It needs about $210K for 24 months. That is roughly 22 new logos, or 1.6 points of churn avoided, or a mix.

On the CFO's partnership yardstick, the base case does not pass. I would not present it as a standalone revenue play.

## What supports funding anyway

- **Cheap relative to the downside protected.** About $135K buys exposure to $180K of ARR per churn point.
- **Distribution.** A listing in an ELT platform's connector catalog puts us in front of buyers already shopping for data integrations.
- **Optionality.** A working connector is the base for a paid data tier. The unmodeled upside is a priced add-on, which could lift the base case.

## Gate (2 weeks, before committing the 9)

1. Count the customers and open deals that have asked for warehouse or ELT access in the last 12 months. Check support tickets, CRM notes and lost-deal reasons.
2. Ask the top 20 accounts by ARR whether they would use it, and whether they would pay.
3. Pick one platform for the first build, not all of them. Scope the 9 weeks to that platform.
4. Tag every deal and renewal that mentions the connector, so the revenue line can be measured at 6 and 12 months.

**Proceed if** the gate finds either:
- 15 or more named accounts or deals with a stated need, or
- evidence it blocks renewals among the top 50 accounts.

If neither is true, the base case says this should be a roadmap item, not funded work.

## Risks

- **Attribution.** Retention gains are hard to separate from other factors. The tagging above mitigates this only partly.
- **Third-party dependency.** The ELT platforms control the catalog, certification and API changes. The $60K/yr maintenance figure is the part most likely to be wrong.
- **First-build scope.** Nine weeks is a quote for a first build. Certification and review by the platform may add time that isn't in the number.

## Inputs for finance to replace

- Loaded engineering cost per week
- Gross margin on new-logo ARR
- Actual annual churn and the share of customers on a modern data stack
- Win-rate data on deals where integrations were raised