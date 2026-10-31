# Auditwave for Jira: Atlassian Marketplace pricing plan

The plan follows the `atlassian-marketplace-playbook` skill, "Not built" route, plus its `references/submission-and-upkeep.md`. Figures marked † come from that playbook, not from live Atlassian docs. Verify each one before it goes into a model or a contract.

## Answers to your three questions

| Question | Answer |
|---|---|
| Charge $5 for only the 40 compliance users? | **No.** A Paid via Atlassian (PvA) license matches the host site's licensed user count, so customers cannot license a subset of users. The bank pays for the 2,000-user tier. |
| Ship a Data Center version for the bank's on-prem Jira? | **No.** New Data Center app submissions have been closed since 16 Dec 2025†. Offer Forge with data residency, Atlassian Government Cloud or Isolated Cloud instead. |
| How much does Atlassian keep? | **17%†** of PvA revenue for a Forge-only app, from 1 Oct 2026. It keeps **0%** until $1M of lifetime Forge revenue†. If the app has any Connect module or scope, Atlassian keeps 25%†. |

## 1. Assumptions

I could not ask the interview questions, so each gap below carries one assumption. Correct any that are wrong.

- **A1, what the app does:** Auditwave collects compliance evidence inside Jira and does not need an account on your own SaaS. It sells on Marketplace pricing alone.
- **A2, stage:** not built, or pre-submission. No version has ever been listed.
- **A3, who pays:** you charge for the Atlassian app itself, so the model is PvA, not Free.
- **A4, bank requirements:** the bank wants data residency or minimal egress, and a vendor security review. This is likely for a bank, but not confirmed.
- **A5, launch date:** unknown. The timeline in section 5 is in weeks before launch (L).
- **A6, the bank's on-prem Jira:** I assume it is a separate Jira from the 2,000-user Cloud site. If it is the same instance, the answer is the same: no Data Center app.
- **A7, backend:** the app uses Forge UI, with Forge remotes only if you already have a backend.

## 2. Architecture and payment-model decisions

### Forge only (driven by A1 and A2)

The Marketplace accepts no new Connect apps, and Connect support ends 31 Jan 2027†. Build on Forge UI with no Connect module or scope. That keeps the 83%† share and the path to Atlassian Enterprise Certified.

### Paid via Atlassian from version one (driven by A3)

- Forge apps cannot use Paid via Vendor without Atlassian's written permission.
- Enable licensing in the manifest from v1. Check the license in code with `context.license.active` and `filter.appIsLicensed` on triggers.
- Do not launch free and switch later. The switch is a new version, a re-review and an admin-consented major version. Existing installs stay unlicensed until each admin subscribes, so adoption stalls.
- Do not sell from your own site to unlock Jira features. Atlassian has published no ruling that this is allowed, and it reads as Paid via Vendor. Get a written ruling on the ECOHELP ticket before building any external billing.

### Data residency and egress (driven by A4)

- "Runs on Atlassian" is earned automatically, but only if there is no egress except analytics.
- If Auditwave stores all evidence on Forge compute and storage, you can earn that badge, and it matters for a bank.
- If you use remotes, declare every first-hop egress domain and its `inScopeEUD` flag correctly in v1, with no broad wildcards. Each later addition, or a false → true flip, is a major version.
- Bank buyers who still block on egress need three things: data residency for remote data, disclosed egress, and the Atlassian Enterprise Certified badge.

### Pricing the 40-user team (the $5 question)

The bank's license covers all 2,000 Jira users, so your price curve decides what it pays.

- **PvA pricing:** prices are set per host-user count, with lower per-user rates at higher counts.
- **Annual price:** 10 times the monthly price†.

The table shows the bank's annual contract value (ACV) at different effective per-user rates, using 2,000 users × rate × 10 months-equivalent†:

| Effective rate at the 2,000-user tier | Annual price to the bank | Per compliance user (40) per year |
|---|---|---|
| $5.00 | $100,000 | $2,500 |
| $1.00 | $20,000 | $500 |
| $0.50 | $10,000 | $250 |
| $0.25 | $5,000 | $125 |

- **If you apply $5 per user to the 2,000-user tier**, the bank pays $100,000 a year for a 40-person tool. It will probably refuse, or deploy a competitor.
- **What you wanted:** $5 × 40 users is $200 per month. Over a year that is $2,400, or $60 per compliance user.
- **The tradeoff:** the 2,000-user tier rate is the lever. A rate that is attractive to the bank at 2,000 users must still be sane for a 10-user or 100-user site.

Recommended approach:

1. Pick a target ACV for the bank first. I suggest $10,000 to $20,000 a year, which is $250 to $500 per compliance user. Use that to set the rate at the 2,000-user tier.
2. Work backwards to a declining curve. Keep small-site rates higher so the curve holds for every site size, not only the bank.
3. Test the curve against four site sizes: 10, 100, 500 and 2,000 users. I did not invent Atlassian's tier boundaries or your final rates, so confirm both against the Marketplace pricing tool.

Other options and their limits:

- **Standard and Advanced editions** can separate a basic tier from an enterprise tier. A new edition is a new app type and a re-review. An edition does not let the bank license fewer users.
- **Existing customers keep the old price for 60 days†** after a change. Treat the launch price list as sticky.
- **Multi-instance pricing** exists for Enterprise sites.

### Data Center (the infra team's request)

- New Data Center apps are closed (16 Dec 2025†, Bitbucket excepted).
- Atlassian also stopped Data Center sales to new customers on 30 Mar 2026†.
- Existing customers can buy Data Center licenses until 30 Mar 2028†. Data Center reaches end of life on 28 Mar 2029†.
- If you built a Data Center version you could not list it, and its share would be 75%† anyway.

What to tell the infra team:

- **Forge with data residency**, covering remote-stored data.
- **Atlassian Government Cloud** or **Isolated Cloud**, where the bank's requirements fit. Each is a separate app type and a re-review.
- The Enterprise Certified badge needs SOC 2 Type II or ISO 27001, a trust center and a public bug bounty.

### Margin model for finance

PvA partner share (from 1 Oct 2026†):

| Framework of the latest listed version | Partner share | Atlassian keeps |
|---|---|---|
| Forge (no Connect module or scope, OAuth, Forge UI) | 83%† | 17% |
| Connect, or any Connect module or scope | 75%† | 25% |
| Data Center | 75%† | 25% |

Rules for the model:

- **First $1M:** 100%† of Forge revenue is yours until lifetime Forge revenue reaches $1M†, summed across your Forge apps. Connect-era revenue of a migrated app does not count.
- **Bank deal example at the $10,000 ACV rate:** you keep $10,000 while under the $1M threshold†. After it, you keep $8,300† and Atlassian keeps $1,700†.
- **Payout:** within 30 days after the month in which $500 of profit accrues†.
- **Refunds:** full refund within 30 days. Days 31 to 60 are at Atlassian's discretion, and partner approval is needed past $1,500†.
- **Forge consumption:** usage above each monthly free allowance is invoiced to you, free apps included†. Treat it as cost of goods sold, and estimate it from evidence-collection volume for the bank.
- **Testing:** every production install of a paid app is billed, yours included. Test in development or staging with `forge install --license active` (or `inactive`, `trial`).
- **Not in the playbook:** I could not source whether the share is calculated before or after sales tax and payment fees. Ask Atlassian or check the Marketplace docs before finance finalizes.

## 3. Irreversibles register

| Irreversible | Decision | Owner | Lock date |
|---|---|---|---|
| Framework | Forge only, no Connect module or scope | Engineering lead | Before first commit |
| Payment model | PvA with licensing enabled in the manifest | Product and finance | L−10 weeks |
| Price curve and editions | Tiered curve tested at 10, 100, 500 and 2,000 users | Finance | L−9 weeks |
| Scopes and egress at launch | Minimal scopes, one justification each, correct `inScopeEUD`, no wildcards | Engineering lead and security | L−8 weeks |
| App name | "Auditwave for Jira" (the format is correct) | Marketing | L−8 weeks |
| Billing email | Company email domain for PvA | Finance | L−8 weeks |
| Data Center | Declined; document the decision | Product | Now |

## 4. Submission checklist

| # | Prerequisite | Owner |
|---|---|---|
| 1 | Submitter can open tickets in the ECOHELP portal (test ticket) | Partner admin |
| 2 | Partner verification (KYC/KYB), 2 to 3 business days†, once per partner | Legal and finance |
| 3 | App security questionnaire (Forge variant); fail answers block the listing | Security |
| 4 | Privacy & Security tab: data stored and where, one justification per scope, trust-center link | Security |
| 5 | Scope and egress list: each scope with its feature, each remote host with the data sent | Engineering |
| 6 | Privacy policy, End User Terms, DPA, documentation link, support contact | Legal |
| 7 | Payment profile | Finance |
| 8 | Sharing enabled in the developer console, test credentials on the ticket if you use a backend | Engineering |
| 9 | A separate unlicensed copy for testers (a licensed or submitted app can no longer be shared by link) | Engineering |

Backward timeline: allow three weeks per review round plus one returned round†, so six weeks.

| Step | When |
|---|---|
| Prerequisites complete (items 1 to 7) | L−9 weeks |
| Submit | L−8 weeks |
| Returned round, fix everything in one pass | L−5 weeks |
| Resubmit | L−4 weeks |
| Approval buffer | L−1 week |
| Launch | L |

A scan finding rejects the ticket: fix it, then resubmit. The listing is locked in review; ask on the ticket for copy changes.

## 5. Post-listing calendar

| When | Check |
|---|---|
| Launch + 2 review rounds | The app is approved within two rounds |
| 30 days | Share of installs on the latest major version is tracked |
| 90 days | Same check; target is set by you, not by Atlassian |
| Ongoing | Zero Atlassian Marketplace Security (AMS) tickets past due |
| Every 18 months† | At least one new version, or a compliance review starts |

Security fix deadlines (cloud)†:

- Critical: 10 days. A missed deadline hides the app.
- High: 4 weeks. A missed deadline hides an unbadged app on day one.
- Medium: 12 weeks.
- Low: 25 weeks.

Other rules:

- Any release that adds a scope or egress is a major version. It waits for review while the fix deadline runs.
- Ship security fixes as minors and keep them separate from new integrations.
- Report a security incident within 24 hours†.
- No partner response for 90 days hides the app†.

## 6. Open items for you

1. Confirm assumptions A1 to A7.
2. Pick the bank's target ACV and the 2,000-user-tier rate, then build the full curve in the Marketplace pricing tool.
3. Decide whether Auditwave stores all evidence on Forge. That decides whether "Runs on Atlassian" is reachable for the bank.
4. Reply to the infra team with the Data Center answer and the data residency, Government Cloud and Isolated Cloud options.
5. Get Atlassian's confirmation of how the revenue share is calculated (taxes and fees) before finance finalizes margins.

† Atlassian changed its framework, badge and revenue-share rules within one year. Verify every rate, SLA, duration and date against current Atlassian developer docs before relying on it.