**Ship this:** 1 primary category + up to 2 secondary (3 max), picked from a fixed tree. Replace free-text tags with controlled facets, plus a hidden, capped synonym field that only feeds search. Fix the ~40 mismatched listings before you launch any of it.

First action: pull the 40 mismatched listings into a sheet with columns `listing`, `current category`, `proposed category`, `last-30-day views`.

## Why not 8 categories + unlimited tags

- **Visibility is zero-sum.** A category page ranks a fixed number of slots. More placements make each page longer and noisier. They do not make any vendor easier to find.
- **Placements multiply.** If vendors average 4 categories, 340 listings become about 1,360 placements. Across about 40 leaves, that is about 34 apps per leaf instead of about 8.
- **The long tail loses.** A vendor at position 30 on 8 pages is still not found. Vendors who fill all 8 slots crowd out honest ones, and everyone feels pushed to do the same.
- **Buyers lose trust.** Browsing is how most buyers find apps. Irrelevant apps in a category teach them the categories are unreliable. That is the same damage the 40 broken listings already cause.
- **Unlimited tags sprawl.** You get `crm`, `CRM`, `crm-software`, `customer relationship` and keyword stuffing. Nobody owns them, nobody can moderate them, and they cannot be shown or filtered cleanly.

The product team is right on one point: some apps genuinely span categories. Search is also growing and needs a broader vocabulary. Both needs have a cheaper fix.

## Spec

**1. Browse tree (what buyers navigate)**
- Two levels. About 10 to 15 top-level categories and 35 to 50 leaves for 340 listings. These numbers are judgment, not data. Aim for 5 to 15 apps per leaf, and split or merge leaves outside that range.
- Primary category is required. It decides canonical placement, breadcrumbs and the default URL.
- Up to 2 secondary categories are optional. They show under "also in" and rank below primary placements.
- Name categories by buyer job ("Collect payments"), not by vendor jargon.
- Add a "Needs review" state. Vendors cannot publish category changes unreviewed, so fit is checked at submission.

**2. Facets (what buyers filter on)**
- Controlled values only. Candidates: integrates-with (picked from a list), use case, industry, company size, pricing model, compliance.
- Facets are structured data, so they work as filters, search ranking signals and comparison fields.
- Ship 4 or 5 facets at first. Add more only when search logs show demand.

**3. Synonym field (what search matches, never shown)**
- Free text, but capped at 10 terms of 30 characters each. It is not displayed, not browsable, and has no tag pages.
- Moderate it with a blocklist, a duplicate check against the title, and a check that terms relate to the app.
- Search indexes title, summary, categories, facets and synonyms.
- You own a central synonym map (`CRM` = `customer relationship management`), fed by zero-result and low-click queries. This helps all vendors, not only those who tag well.

**4. Discoverability levers for vendors (the real complaint)**
- Send each vendor a monthly report: impressions, clicks, the search queries that surfaced them, and queries that nearly matched.
- Add "related apps" blocks, curated collections, and a short new-listing exposure window.
- Rank by relevance plus engagement, not by how many places a vendor listed itself.
- Offer a listing-quality checklist: summary, screenshots, integrations filled in.

## The 40 broken listings

They are about 12% of the catalog, and they are likely the real cause of "nobody finds us" for those vendors. The cause was probably a taxonomy rewrite with no migration step.

1. Build the old-to-new mapping table. Propose a new category for each of the 40. Prioritize by traffic. (Estimate: about 3 to 4 hours for one reviewer at about 5 minutes each.)
2. Optional triage aid: classify each description against the new leaves and use the result only to pre-fill proposals. A human approves every move.
3. Notify vendors with the proposed move. If there is no reply in 14 days, the proposal applies.
4. Assign a named owner. Add a fit check at submission and a quarterly drift check.
5. Do this before launching the new rules. Otherwise the new limits sit on a tree you already know is wrong.

## How to know it worked

Measure the baseline now, then re-read after 4 to 6 weeks:
- Category-page click-through to listing pages.
- Search zero-result rate and search-to-listing click rate.
- Share of listings with at least one view per month, and the spread of impressions across vendors.
- Vendor complaints, tracked separately for the 40 fixed listings and for everyone else.

If browse click-through does not rise after the fixes, raise the secondary cap from 2 to 3. If search click-through stays flat, widen the synonym map before adding any tag surface. Revisit the 3-category cap only with measured evidence, not on complaints alone.

## Rollout

1. Fix the 40 and freeze the tree. About 1 week including vendor notice.
2. Ship the primary + 2 secondary categories, with review at submission. About 1 to 2 days of engineering, plus time to build the review UI.
3. Ship facets and the capped synonym field, then the synonym map. About 1 to 2 weeks.
4. Ship the vendor report and related-apps blocks.
5. Re-read the metrics at week 6.

**Assumption:** I do not have your current tree size, traffic data or the vendor complaint breakdown. Check the numbers above against your analytics before you lock them.

Next: build the 40-listing sheet and send it to me, and I will draft the old-to-new category mapping.