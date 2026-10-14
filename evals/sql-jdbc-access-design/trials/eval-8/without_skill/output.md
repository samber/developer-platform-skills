**Start here: do not scope one project yet. Spend this week on a one-page "data sharing" split. Draft the page from this answer, then take it to the Head of Product.**

## Diagnosis

Four requests share a name, not a problem. Each one has a different user, risk, and owner.

| # | Request | Real problem | Type |
|---|---|---|---|
| 1 | Agencies see aggregate data across brands | Cross-tenant access and permissions | Product feature, authorization model |
| 2 | One monster report slows everyone | Noisy neighbor on shared analytics DB | Platform reliability, no customer-facing feature |
| 3 | 12 customers want Looker on their own data | Customer-facing BI connectivity | Product feature, query access |
| 4 | 2 customers want nightly Parquet to their S3 | Bulk export / data delivery | Product feature, batch pipeline |

Items 3 and 4 are one family: "customer pulls their own data out." Item 1 is a different family: "someone sees data that is not theirs." Item 2 is internal and may be a prerequisite for item 3.

## Dependencies

- **Item 3 makes item 2 worse.** Twelve customers running Looker on the shared DB add monster-report load. Fix isolation before, or together with, Looker.
- **Item 1 is the risky one.** It crosses tenant boundaries. A mistake leaks one brand's data to another brand's agency. It needs a permission model: who grants access, per brand, revocable, audited.
- **Item 4 is the cheapest.** It is a scheduled job, tenant-scoped, with no live-query load. Two customers can already use it.

## Recommended shape

Run one program with three tracks, not one project. The Head of Product gets one roadmap line and one owner. Engineering gets scoped deliverables.

1. **Track A, analytics isolation (item 2).** Internal. Do first. Candidates: per-tenant query limits and timeouts, a read replica, or a workload queue. Pick after you measure.
2. **Track B, customer data out (items 3 and 4).** Ship Parquet export first (small, two customers waiting). Then Looker access, built on the isolation from Track A. Both reuse the same tenant-scoped data layer.
3. **Track C, partner agency views (item 1).** Separate. Start with the permission and consent design. Sales' three agencies are the pilot, not the whole feature.

## Order and sizing

I do not know your team or stack, so these are guesses. Replace them with real estimates from engineering.

| Step | Item | Rough size |
|---|---|---|
| 1 | Measure: which queries hurt the shared DB, how often, which customers | Days |
| 2 | Parquet export for 2 customers | Small |
| 3 | Isolation fix (Track A) | Medium |
| 4 | Looker access for 12 customers, pilot with 2 to 3 first | Medium |
| 5 | Agency cross-brand views (Track C) | Large. Needs design first |

Item 2 could be a quick win or a quarter of work. Step 1 tells you which.

## What to do this week

1. **Ask the four requesters one question each.** "What outcome do you need, by when, and what happens if it slips?" Sales: is a deal waiting on the agencies? Engineering: how often does the monster report hit, and who is hurt? Looker customers: self-serve dashboards, or something else? S3 customers: is the Parquet format a hard requirement?
2. **Check the 12 Looker asks.** Do they want live query access, or would a nightly file in a warehouse do? If a file is enough, items 3 and 4 collapse into one export feature. This may be your biggest scope cut.
3. **Pull the slow-query data.** Find the monster report's owner, frequency, and cost. This decides how urgent Track A is.
4. **Write the one-pager for the Head of Product.** Four requests, three tracks, a dependency note, a proposed order, and a rename. Drop "Data sharing" as the umbrella. Use "Customer data access" for Track B and name the others separately.
5. **Decide the agency question separately.** Which brands consent to sharing, and who can revoke? Product and legal should answer this before engineering designs anything.

## Open questions I cannot answer for you

- Is any sales deal blocked on the agency feature? That sets its priority.
- Does the quarter have capacity for all three tracks? If not, I would cut Track C to design-only and ship Tracks A and B.
- Are the 12 Looker customers on one plan tier? That may affect pricing and packaging.

**Next action:** send the four requesters the question in step 1. It takes about 20 minutes. Paste their answers here and I will tighten the one-pager.