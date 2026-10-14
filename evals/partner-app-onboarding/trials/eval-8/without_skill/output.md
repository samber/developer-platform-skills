**Change the order. Review first, installs later.** Today the install wall sits in front of the thing that would let partners get installs. Fix that and the rest follows.

I'm working from your message only. I haven't checked the current docs, review capacity or install mechanics, so assumptions are marked.

## Diagnosis

1. **Deadlock.** Review needs 5 real installs. Partners can't get real installs without a listing, and the listing needs review. Unless an unlisted install path exists, no partner can start. (Assumption: none exists. Verify first.)
2. **Safety backwards.** HR apps touch employee PII. The current rule makes unreviewed code run on real customer workspaces before anyone reviews it. That is a risk for you and for customers.
3. **Cost lands on the wrong side.** The partner pays three months of engineering before learning the gate exists, or learns it after. That is the "wasted time" complaint.
4. **Three partners in a short window is a pattern.** Don't treat it as venting.

## What to change

1. **Split review from installs.**
   - Review = security, data handling, scopes, quality. No install count needed.
   - Pass review and the app gets listed.
   - Keep a lighter bar for first listing: reviewed, not yet "proven".
2. **Add an unlisted install path.** Private install link or invite code, so a partner can put the app on a design-partner customer's workspace before listing.
   - Gate it behind a lightweight pre-review (scopes plus data handling) because it touches real HR data.
   - Cap it, for example 10 workspaces per unlisted app.
3. **Make "Vessen Certified" a staged ladder, not one wall.**
   - Stage 1, **Reviewed**: passes review, immediate.
   - Stage 2, **Verified**: 10 active installs, 60 days listed.
   - Stage 3, **Certified**: your current 60 installs and 6 months.
   - Keep the Certified bar. It is a trust signal and weakening it hurts customers.
   - Test whether 60 is reachable in niche categories. If the median category can't reach it, the badge is unearnable and nobody will chase it. Consider a threshold per category or a share of the relevant customer base.
4. **Publish the whole path before anyone writes code.**
   - One page: stages, thresholds, review SLA, what you will and won't do for distribution.
   - Put it first in partner docs and in the partner signup flow.
   - Add a pre-build check: "Do you have 5 design-partner customers lined up?"
5. **Seed supply.**
   - Pick a founding cohort of 5 to 8 partners covering the integrations customers ask for most.
   - Make intros to customers in your base who want that integration.
   - Point in-product placement and your CS team at reviewed apps.
   - Take rate: zero until the marketplace has liquidity.

## Fix the damage

Do these this week:

1. **Reply in the Slack thread today, in public.** Say the gate was a design flaw, name the order change, give a date for the new rules. No defensiveness and no excuses.
2. **Call the three partners in private.** Offer a fast-tracked review for their existing app, intros to design customers, and the unlisted install path as soon as it exists.
3. **Don't promise compensation you haven't approved.** If you want a goodwill gesture (credits, free sponsored placement, co-marketing), decide it internally first.
4. **Log how many other partners are stuck at the wall.** That is your outreach list.

## 30 / 60 / 90 days

- **Days 0 to 7:** Slack reply, three calls, stuck-partner list, interim rule: manually review any app from a partner already blocked.
- **Days 7 to 30:** unlisted install path, new review criteria, staged badge, the one-page path published.
- **Days 30 to 90:** founding cohort live, intros running, first numbers read.

## Measure

| Metric | Why |
|---|---|
| Days from signup to first real install | The wall, quantified |
| Share of partners reaching 5 installs within 60 days | Does the new path work |
| Review queue time | Moving review up front creates load |
| Partner satisfaction at day 30 | Catches a repeat of this thread |
| Weekly active installs per account | Whether customers actually use apps |

## Kill and revisit criteria

- If under 40% of founding-cohort partners reach 5 installs in 90 days, the problem is demand, not process. Then narrow to fewer categories and run vendor-built integrations on the top requests.
- If review takes more than 10 business days, you have a staffing gap. Hold new partner intake rather than rebuilding the queue.
- If you can't staff review, don't open the door wider. Stay on a documented API.

## Unknowns that could change this

1. Does an unlisted or private install path already exist?
2. Was the gate published before partners started building, or did they find it late?
3. How many reviews per month can you staff?
4. Why does the 5-install rule exist? If it guards against review spam, a per-partner review cap fixes that without the install requirement.

**Next:** answer question 1. Can a partner today install an unlisted app on a real customer workspace?