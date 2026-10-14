**Sequencing: not confirmed. Flip it.** Order: Built for Shopify, then Cloud Fortified prep, then Security Review upkeep.

I skipped the skill's 10-question interview because you asked for a one-shot answer. The open questions at the bottom could change this plan.

## Why the CTO order breaks

1. **Salesforce Security Review is a gate, not a badge.**
   - Okrahead is live on AppExchange, so it already passed.
   - Nothing is left to win. The only risk is failing a re-review, which delists you.
   - Enterprise logos may still care about it, but it is upkeep. It does not need a quarter.
   - Confidence: vendor-official. Failing the review delists the app, and it is not a ranking factor.
2. **Built for Shopify is not "just a sticker."**
   - Shopify says in writing that Built for Shopify apps rank higher in App Store search.
   - No other badge on the five marketplaces has an official ranking statement.
   - Confidence: vendor-official.
3. **Cloud Fortified has no published ranking lift.**
   - It is a trust and procurement asset (official program, effect unquantified).
   - Your H2 launch there makes the lead time matter.
   - You cannot show it before you are live, so only prerequisites fit this quarter.

## Quarter plan (13 weeks)

**Weeks 1-2: baseline and gates (about 2 eng days plus 1 owner day)**
1. Open Partner Dashboard, then Distribution → Manage listing → Tracking. Wire GA4 and Meta Pixel for the Shopify funnel. Native dashboards show installs, uninstalls, and revenue.
2. Open the AppExchange Publishing → Analytics tab. Record views, installs, and top search terms.
3. Pull the current Built for Shopify criteria from Shopify's docs and gap-check them. I did not verify the thresholds, so check the criteria yourself. They typically cover performance, UX, and install and review minimums.
4. Check the Security Review re-review date and any open findings. If one is due this quarter, it jumps the queue because failure means delisting.

**Weeks 3-10: Built for Shopify (about 70% of engineering)**
- Close every gap from step 3. Each gap is an engineering ticket, ranked by the length of its lead time.
- Start the standing review program in parallel, using sanctioned triggers only:
  - Post-support-resolution ask, with an opt-out, routed through the Reviews API.
  - An unconditional lifecycle email to all active users (practitioner-reported 5-10% conversion).
- **Never** incentivize reviews. The penalty ladder ends in Partner-account termination.
- Fix retention gaps first. Uninstall rate hurts ranking, and a badge cannot outrun churn.
- Week 10: submit for Built for Shopify review.

**Weeks 6-12: Atlassian prep (about 25% of engineering, overlapping)**
- Pull the current Cloud Fortified requirements from Atlassian's docs. I did not verify the specifics, so confirm that your pre-launch status is eligible.
- Build what is cheap now and slow to retrofit:
  - Security and reliability evidence.
  - Support process.
  - Compliance paperwork.
- Prepare the listing:
  - Summary field, 250 characters, as the load-bearing search string. This is practitioner inference.
  - Screenshots at 1840×900.
  - Function-only demo video, 30 seconds or less.
- Plan the review ramp. Atlassian auto-invites customers 30 days after purchase, and a star rating shows only after 10 reviews.
- **Gate:** Atlassian prerequisite checklist signed off by week 12.

**Weeks 1-13: Security Review upkeep (about 5%)**
- Keep the Trailblazer Score healthy. Salesforce confirms it influences visibility.
- Re-run the review only if the date from step 4 falls in the quarter.
- Add AppExchange listing hygiene (about 2 hours): outcome-oriented copy, with one category and two industries. This is emerging inference.

**Week 13: review**
- Check Built for Shopify status.
- Check review velocity over the trailing 90 days.
- Check uninstall rate.
- Name a listing owner and set the 30-60 day refresh cycle.

## What this plan changes for the CTO

| CTO ask | Plan |
|---|---|
| Security Review badge first | There is no badge to earn. It is upkeep only. Enterprise logos are already covered because you are listed. |
| Cloud Fortified next | Prerequisites only this quarter, paced to the H2 launch. |
| Built for Shopify last | First, because it has the only vendor-confirmed ranking boost. |

## Open questions that could change this plan

1. Does enterprise procurement ask for something beyond the listing, such as a SOC 2 report or a pen-test report? If so, that work is separate from the AppExchange upkeep above.
2. Shopify funnel: what are your current view-to-install numbers and uninstall rate? If retention is weak, product work moves ahead of badge work.
3. What is the exact H2 date for Atlassian? An early July launch means the prep needs to run harder this quarter.
4. How many engineers are available? The 70/25/5 split assumes a small team.

**Next action:** open Shopify's Built for Shopify requirements page and list each unmet criterion. That list sizes weeks 3-10, and it takes about 30 minutes.