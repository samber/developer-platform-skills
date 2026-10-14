# Parcelith: Shopify App Store review campaign brief

**Date:** 2026-10-08. **Window:** Black Friday launch (Fri 2026-11-27), about 7 weeks out. **Marketplace:** Shopify App Store, live listing.

## 1. Verdict on marketing's proposal

All three tactics are removed from the plan, not demoted. They are not "risky but maybe": the skill deletes them outright.

| Proposal | Decision | Why |
|---|---|---|
| (a) $50 gift card for a review | ❌ Deleted | Shopify bans incentivized reviews "through the app or external channels." The policy lists removal of reviews, demotion or delisting of the app, and Partner-account termination. Shopify has documented mass takedowns. |
| (b) Six team members each post one | ❌ Deleted | Reviews from your own team are banned. Reviewer-attestation systems now catch them. Untrusted reviewers can also get *genuine* reviews unpublished along with them. |
| (c) Review swap with a partner app | ❌ Deleted | Swaps with other vendors are banned and are caught the same way. Knowing the founder doesn't change that. It also exposes their account, not just yours. |

**"One-time, then we stop" doesn't help.** A launch-window violation still sits on the listing and the Partner account afterward. The skill notes that "just for this launch" is exactly the framing that reappears every time velocity stalls.

**It also gets the goal wrong.** Review recency and velocity outweigh lifetime totals. A one-time burst followed by silence leaves a stale 90-day window. The compliant version is a small standing program, not a spike.

## 2. Assumptions to confirm

The skill's interview is one question per message. I couldn't run it interactively, so these are my assumptions. Correct any that are wrong, because several change the plan.

1. **Funnel data:** Shopify is data-rich, so a partner dashboard and GA4/Meta Pixel wiring exist.
2. **Brand:** Parcelith is a Challenger against a competitor with 240 reviews.
3. **Buyer language:** I don't have it yet. You need it from support tickets and sales notes.
4. **Review base:** 9 reviews at 4.6. I don't know their recency, or whether the competitor's rating is higher or lower than 4.6.
5. **Built for Shopify:** not earned. I don't know whether you're eligible.
6. **Owner and effort ceiling:** unknown.
7. **Deadline:** hard, Nov 27. Intent is both a launch unblock and a compounding asset.

Per the skill, a hard deadline promotes text-only levers over standing programs. A compounding-asset mandate promotes the standing programs. Both apply here, so the plan runs them in parallel.

## 3. Provenance labels

Every ranking claim below carries one of these tiers: vendor-official, corroborated inference, single-source inference, or analogy.

- Built for Shopify badge boosts search rank: **vendor-official**.
- Review recency and velocity affect rank, and "50 reviews in 30 days beats 500 static": **corroborated practitioner inference**. Plan on the direction, not the magnitude.
- Name + subtitle carry about 80% of keyword weight: **single-source inference** (one tracker's estimate). Don't promise it to leadership.
- Email review asks convert at 5-10%: **corroborated practitioner report**.
- Ratings-to-conversion lifts from consumer app stores: **analogy only**. The direction (reviews compound into conversion) likely holds. The magnitudes are unverified for B2B.

## 4. Plan

### Stage 1: Instrument (week 1, about 1-2 hours)

- Confirm the partner dashboard shows installs, uninstalls, and ratings.
- Wire GA4 Measurement ID and Meta Pixel under Distribution → Manage listing → Tracking. This gives the full listing-view → install-click → install funnel. It must be done manually.
- Record the baseline: views, view-to-install conversion, 90-day review velocity, and uninstall rate.
- **Why first:** you can't tell whether the campaign worked without it.

### Stage 2: Text and first screen (weeks 1-3)

This is the highest-efficiency lever and it lands before Black Friday.

1. **Keyword rewrite:** use the real buyer language from question 4.
   - Shopify titles are **brand-first** ("Parcelith Shipping Delay Alerts"), not keyword-first.
   - Search terms are up to five complete words, one concept per term.
   - Set the tagline and subtitle accordingly.
2. **Gallery:** the first three assets should be unique, in-UI, and captioned. Shopify now hard-rejects duplicate and logo-only images.
   - Position 1 is the hero: delay notification in action.
   - Position 2 is the differentiator against the 240-review competitor.
   - Position 3 is the most-loved feature.
   - No pricing or review claims baked into images. No sensitive data.
   - Size is 1600×900.
3. **Demo video:** optional. Shopify allows 2-3 minutes with a promotional tone, and the screencast is capped at 25% of runtime. Add one only if time allows.
4. **Uninstall check:** the skill flags that a better listing can't outrun churn. Look at your uninstall rate before Black Friday, so the installs you win don't become uninstalls.

### Stage 3: Compliant review velocity (start week 2, standing)

Sanctioned triggers only, in this priority order:

1. **In-product prompt via the Reviews API.**
   - Show it at a natural pause, such as right after a delay notification is successfully sent. It must never block the workflow.
   - Include an opt-out from future asks.
2. **Post-support ask:** after a positive support resolution. This is the highest-converting sanctioned moment.
3. **Lifecycle email to your 1,200 merchants.** This is what to do instead of the gift-card email.
   - The ask must be **unconditional and sent to all qualifying active merchants**. Do not send it only to the happy ones. Cherry-picking is treated as manipulation.
   - No reward, discount, or perk of any kind.
   - Use the same copy and the same offer to everyone.
   - At a 5-10% conversion rate, 1,200 merchants gives a **ceiling** of 60-120 reviews. Treat that as a ceiling, not a forecast, because not all 1,200 are active.
4. **Milestone-timed personal asks** to your 10-20 best merchants. This is the lowest volume but the highest quality, and with only 9 reviews each one moves the average.
5. **Negative-review replies:** reply publicly, once per review, to fix the issue and get the review amended.

**Cadence:** stagger the sends over the 7 weeks rather than one blast. That keeps velocity inside the 90-day window through Black Friday and after. After launch, keep the in-product and post-support triggers running permanently. They cost almost nothing once built.

### Stage 4: Badge (decision, not a commitment)

Built for Shopify is the only badge with a vendor-official ranking boost. It takes a quarter or more of engineering and process work, so it won't land by Nov 27. Check eligibility requirements in the official docs and put it on the post-launch roadmap.

### Stage 5: Defend

- Set a 30-60 day listing refresh cycle with a named owner.
- Re-verify Shopify's current review and listing rules each cycle. All five platforms change them on an ongoing basis.

## 5. Replacing the partner swap

Reviews are off the table, but the partner relationship is still useful. Options that are allowed:

- Co-marketing: a joint webinar or newsletter swap to each other's merchants.
- Cross-listing in each other's help docs.
- Introducing each other to merchants who genuinely use both apps. Those merchants can leave reviews on their own, with no coordination and no exchange.

## 6. Measurement

Gates, self-set and not an external bar. Iterate until all five pass:

1. GA4/Pixel funnel wiring is live and the baseline is recorded.
2. Every indexed field carries the buyer language, in brand-first title format.
3. The first three gallery assets are unique, in-UI, and captioned, and every review ask maps to a sanctioned trigger.
4. Every ranking claim in the plan has a provenance label.
5. A 30-60 day refresh cycle exists with a named owner.

KPIs:

- Listing views and view-to-install conversion.
- Keyword coverage, tracked separately from keyword rank.
- Review velocity over the trailing 90 days, plus average rating.
- Uninstall rate.
- Built for Shopify progress.

Treat before/after lifts under 2% as noise. Your traffic is low, so significance will take longer than the launch window allows. Read the trend, not any single week.

## 7. Open questions for you

1. Is the competitor's rating above or below 4.6? It changes how much the review count matters versus the rating.
2. What do merchants type when they search for this? Without it, the keyword rewrite is a guess.
3. Who owns the listing day-to-day, and how many hours a month can they give?
4. Is Parcelith eligible for Built for Shopify, and what's blocking it?

## 8. Talking point for marketing

The three tactics could cost you the listing and the Partner account just before your biggest week. The compliant plan can plausibly add dozens of real reviews by Black Friday (60-120 is the ceiling at the reported 5-10% email rate), and it keeps working after the launch.