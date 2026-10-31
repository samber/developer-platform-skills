# Auditwave for Jira: pricing plan

I wrote this from my own knowledge of the Atlassian Marketplace, with no live lookups. Items marked **VERIFY** are fast-moving Atlassian policy or numbers that I'm not certain are current as of Oct 2026. Check them before you commit.

## 1. Decisions needed

1. **You can't charge for 40 users on a Cloud Marketplace listing.** Per-user app pricing follows the site's total licensed user tier, not who uses the app. The bank's 2,000-user site lands in the 1,001–2,000 tier and pays that tier's price. (VERIFY the current tier boundaries in Partner Portal.)
2. **Data Center: no, don't build it.** Details in section 4.
3. **Atlassian's cut: model 25% as the base case**, and test 15% as an upside scenario (section 5). VERIFY the current rate in the Partner Portal.

## 2. The 40-user problem

Marketplace apps in "paid via Atlassian" mode are billed by tier. Atlassian doesn't count active or assigned app users. A 2,000-user site pays the tier price whether 40 or 2,000 people use the app.

| Path | Result for the bank | Trade-off |
|---|---|---|
| **A. Tiered per-user list price (recommended)** | Pays the 1,001–2,000 tier price | One public price list. Everyone at that tier pays the same, so tune the tier to the bank's value. |
| **B. Private offer / custom quote** (VERIFY availability for Cloud apps) | Negotiated annual price, such as an explicit "40 compliance seats" deal | Handled through Atlassian billing. Works only if Atlassian supports it for your listing type. |
| **C. Paid via vendor** (you invoice) | Any structure you want, including 40 seats | The payment model is hard to change later, and you lose Atlassian billing and the Marketplace procurement path. Banks often prefer Atlassian billing. Check the lock rules before choosing. |
| **D. Enforce 40 seats in-app** | Your own entitlement check | Atlassian's price is still tier-based, so you'd be limiting the customer below what they've paid for. This is confusing and invites disputes. Skip it. |

**Recommendation:** use path A for the public listing. Use path B for the bank if it's available. Fall back to C only if the bank insists on seat-based terms.

## 3. What to charge

$5 × 40 users is $2,400 a year. That is too low for compliance software sold to a bank. Support, security questionnaires, and vendor due diligence will cost more than that.

Price on value instead. Evidence collection replaces audit-prep labor for a regulated team.

| Scenario | Annual price at the bank | Effective per compliance user per month | Notes |
|---|---|---|---|
| Floor | $6,000 | $12.50 | Barely covers bank-grade support. |
| **Target** | **$12,000–$18,000** | **$25–$38** | Sensible for a compliance tool. |
| Stretch | $24,000 | $50 | Needs the evidence-quality and audit features to justify it. |

**Public price list:** a smaller-site tier ladder with per-user prices that taper downward. Set the 1,001–2,000 tier so its total lands in the Target band, about $1,000–$1,500 a month. Check this against what comparable GRC and compliance apps charge at that tier before you lock it. I have no current comparables, so gather them first.

Test the target against the bank's own numbers: roughly what one audit cycle costs them in internal hours.

## 4. Data Center

**Recommendation: don't ship a Data Center version.**

- **Forge is Cloud-only.** A DC edition means a separate Java (P2) app, with its own build, QA, and support. It's a second product, not a flag.
- **Atlassian is winding down Data Center.** My understanding: new DC sales to new customers ended in March 2026, and end of life is March 2029. VERIFY the exact dates. A new DC app would have about two years of selling life.
- **A bank still on DC is a bank that will migrate.** Their infra team's question is really "will you support us until we move?"

**What to offer instead:**
1. A written answer: Cloud-only, with a roadmap tied to their Cloud migration timeline.
2. If the bank's on-prem need is data residency or isolation, ask them which Forge options they need. Forge's "Runs on Atlassian" model and data residency may answer it. VERIFY current residency coverage.
3. If they truly must have DC, price it as a bespoke project: a fixed engineering fee up front plus annual support. Don't list it publicly.

## 5. How much Atlassian keeps (for finance)

Model these layers separately.

| Layer | Treatment | Confidence |
|---|---|---|
| **Marketplace revenue share** | Base case 25% of gross. Upside scenario 15%. | VERIFY the current rate and any threshold or program discounts. |
| **Taxes (VAT/sales tax)** | Collected and remitted by Atlassian on Marketplace sales. Your payout is net of those taxes. | Reasonably sure, but confirm for your seller country. |
| **Forge platform charges** | Forge usage beyond the free allowance (compute, storage, egress) is billed to you as the vendor. | VERIFY the current consumption pricing and free allowances. Model it per active tenant. |
| **Customer discounts and partner commissions** | Atlassian-run promotions or Solution Partner discounts may reduce the gross. | VERIFY who funds them. |
| **Payout timing** | Monthly payouts, in arrears. Plan cash flow for a lag. | VERIFY. |

**Worked example, bank at $15,000 gross a year:**

| Item | 25% share | 15% share |
|---|---|---|
| Gross | $15,000 | $15,000 |
| Atlassian share | −$3,750 | −$2,250 |
| **Net before Forge costs** | **$11,250** | **$12,750** |
| Forge usage (assumption: $300/yr, replace with real figure) | −$300 | −$300 |
| **Contribution** | **≈$10,950** | **≈$12,450** |

For the $5 × 40 version, gross is $2,400 and net at 25% is $1,800, before support.

## 6. Pre-commitment checklist (about 1 hour)

1. Confirm the revenue share and any payout terms in Partner Portal.
2. Confirm the payment-model lock rules before choosing paid-via-Atlassian vs. paid-via-vendor.
3. Check whether private offers are available for your Cloud listing.
4. Confirm the DC wind-down dates.
5. Estimate real Forge cost per tenant from your usage logs.
6. Check comparable apps' prices at the 1,001–2,000 tier.

## 7. Next step

Tell me which path you want for the bank (A, B, or C) and your target ACV. I'll turn this into a tier ladder with the exact monthly totals per tier.