# Brightpier listing field rules (v2 draft)

## How to use these rules

- Every rule is a pass/fail test. If you can't point to a rule ID, you can't reject.
- **Auto** rules run in the submission console at submit time. A listing that fails one never reaches a reviewer.
- **Reviewer** rules need human judgment, but each has a written test.
- Every rejection cites the rule ID and quotes the offending text. The partner's fix message comes from the table, so identical failures get identical wording.
- If a case fits no rule, approve it. Then log it in the precedent log (see the end) and propose a rule.

I haven't seen your field list, so I assumed the usual marketplace fields. Rename or drop rows to match your schema. Each threshold is a starting value, so adjust it against your own dispute data.

## Replaces the old five lines

| Old line | Now enforced as |
|---|---|
| "Demonstrate clear value" | T2, D1–D4, M1 |
| "Establish trust with the buyer" | P1–P4, S1–S3, C1–C3 |

## Title (T)

| ID | Rule | Test | Check |
|---|---|---|---|
| T1 | Length | 3–60 characters. | Auto |
| T2 | Names the product, not the benefit | Title contains the product or vendor name. A bare phrase like "Best CRM Tool" fails. | Auto (name match), reviewer on edge cases |
| T3 | No ranking or promo words | Fails on "best", "#1", "top", "free" (unless the plan is free, see P2), "official" (unless the vendor has verified status), and ALL CAPS words over 4 letters. | Auto |
| T4 | No keyword stuffing | No term repeated more than once. No more than one separator (`|`, `-`, `/`). | Auto |

## Short description (D)

| ID | Rule | Test | Check |
|---|---|---|---|
| D1 | Length | 40–160 characters. | Auto |
| D2 | States what it does | A reader can complete "This lets [user] [do something]". Names an action and an object. "Powerful, flexible solution" fails. | Reviewer |
| D3 | Names the user | A role, team, or use case appears. For example "finance teams" or "Shopify stores". | Reviewer |
| D4 | No unsupported superlatives | "Fastest", "most secure", "leading", "trusted by thousands" fail unless C1 evidence is attached. | Auto (flag), reviewer (decide) |

## Long description (M)

| ID | Rule | Test | Check |
|---|---|---|---|
| M1 | Concrete outcome | Contains at least one specific capability and one specific result. Example: "Syncs invoices to your ledger every 15 minutes". | Reviewer |
| M2 | Setup and requirements | States prerequisites: accounts, plans, permissions, and supported platforms or versions. | Reviewer |
| M3 | Limitations | States at least one real limit (volume, region, unsupported case), or "None known" explicitly. | Auto (field must be filled) |
| M4 | Length | 300–4,000 characters. | Auto |
| M5 | No copy of another listing | Under 20% text overlap with any other listing outside the same vendor. | Auto |
| M6 | No competitor disparagement | Naming a competitor is allowed for comparison. Negative claims without a source fail. | Reviewer |

## Claims and evidence (C)

This replaces "establish trust". Trust claims become checkable evidence.

| ID | Rule | Test | Check |
|---|---|---|---|
| C1 | Every quantified or superlative claim has a source | Each number, ranking, or customer count needs an attached link or document dated within 24 months. | Reviewer |
| C2 | Certifications are verifiable | A named certification (SOC 2, ISO 27001, etc.) needs a report date or a public registry link. | Reviewer |
| C3 | Customer logos and quotes need permission | The vendor ticks a confirmation box. The listing fails if it's unticked. | Auto |

## Pricing (P)

| ID | Rule | Test | Check |
|---|---|---|---|
| P1 | Pricing model declared | One of: free, free trial, paid, usage-based, contact sales. | Auto |
| P2 | "Free" means free | If the listing says "free", a plan with no payment method required must exist. A trial must say its length. | Auto + reviewer |
| P3 | Price shown for paid plans | At least the starting price, billing period, and currency. "Contact sales" is allowed only when P1 is set to that model. | Auto |
| P4 | Extra costs disclosed | Per-seat, per-usage, or setup fees that apply to the listed plan appear in the description or a linked pricing page. | Reviewer |

## Support and ownership (S)

| ID | Rule | Test | Check |
|---|---|---|---|
| S1 | Working support contact | Email or help URL. The console sends a test message or fetches the URL (HTTP 200). | Auto |
| S2 | Support response time stated | A number of business hours or days. | Auto (field filled) |
| S3 | Vendor identity | Legal entity name, country, and a company website whose domain matches the support contact or has a verified link. | Auto + reviewer on mismatch |

## Privacy and data (P-D)

| ID | Rule | Test | Check |
|---|---|---|---|
| PD1 | Privacy policy link | Loads and mentions the product or vendor by name. | Auto (loads), reviewer (content) |
| PD2 | Data access declared | The vendor selects which buyer data the product reads or writes. The selection must match the permissions requested at install. | Auto |
| PD3 | Data location and retention | Stated as region(s) and a retention period, or "not stored". | Auto (field filled) |

## Media (I)

| ID | Rule | Test | Check |
|---|---|---|---|
| I1 | Logo | Square, at least 256×256 px, no text-only placeholder. | Auto |
| I2 | Screenshots | 2–8 images, at least 1,280×720. At least one shows the real product UI. | Auto (size), reviewer (real UI) |
| I3 | No misleading imagery | Images show features that exist. No mock-ups of unreleased functionality and no third-party logos implying endorsement. | Reviewer |
| I4 | Readable | Text in screenshots is legible at 50% scale. | Reviewer |

## Category and tags (K)

| ID | Rule | Test | Check |
|---|---|---|---|
| K1 | One primary category | Chosen from the list. Reviewer may recategorize without rejecting. | Reviewer |
| K2 | Tags | Max 5, each relevant to a feature in the description. | Auto (count), reviewer (relevance) |

## Rejection and fix messages

Reviewers pick from this table and don't write free text for the reason. They may add a quote of the offending text.

| Code | Message to partner |
|---|---|
| T2 | Your title doesn't contain your product or company name. Add it, for example "Acme Invoice Sync". |
| D2 | Your short description doesn't say what the product does. Rewrite it as "[Product] lets [user] [action]". |
| M1 | Your description lists no concrete capability and result. Add at least one of each. |
| C1 | "[quoted claim]" has no source. Attach a document or link dated within 24 months, or remove the claim. |
| P2 | The listing says "free" but no plan is free. Remove the word or add a free plan. |
| S1 | Your support contact didn't respond to the console test. Provide one that works. |

Write the remaining codes on the same pattern: what's wrong, the quoted text, and the exact fix.

## Consistency rules for the three reviewers

These address the "someone approved the same thing" disputes.

1. **Precedent log.** One shared table with the rule ID, the listing, the verdict, and one sentence on why. It must be searched before any judgment-rule rejection. If a matching approval exists, approve.
2. **Dispute handling.** When a partner cites another listing, check the log. If that listing broke the same rule, approve the disputed listing now and flag the other for re-review under the same rule. Don't defend a rejection on reviewer discretion.
3. **Calibration.** Once a week, all three reviewers blind-review the same 10 listings and compare verdicts. Any split becomes a rule edit or a precedent entry.
4. **Grandfathering.** When a rule changes, existing listings get a 60-day fix window. Don't reject them retroactively.
5. **Tracking.** Record disputes per rule ID. A rule with more than 2 overturned rejections in a month is rewritten.

## Console implementation

- Run every **Auto** rule inline on the form, with the fix message shown at the field.
- Block submission on Auto failures. Reviewers should never see those.
- Show reviewer-rule tests as hints beside the fields, so partners can self-check before they submit.
- Pre-fill the rejection form from the code table.

Over time, most of the one-in-five disputes should become pre-submit errors, or become a rule edit when the rule turns out to be the problem.