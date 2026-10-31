# Metricly: Shopify App Store ranking plan

## Verdict on the four inputs

| Idea | Verdict | Why |
|---|---|---|
| Subtitle "The #1 analytics app - trusted by 10,000 merchants, 4.9 stars" | ❌ Drop | Shopify's listing requirements restrict superlatives, unsubstantiated claims, and ratings or review stats in listing text. It is also false while you sit on page 3, and it spends the subtitle's limited characters on zero search keywords. |
| "Rate us 5 stars" button | ⚠️ Change | Asking for reviews in-app is fine. Asking for a specific rating is not. Use a neutral prompt ("How is Metricly working for you?") and send everyone to the same review page. |
| Free month for anyone who leaves a review | ❌ Drop | Incentivized reviews violate Shopify's app review policy. The risk is review removal, a listing penalty, or delisting, so it is not worth the ranking gain. A reward for feedback or a support survey is fine if it is not tied to posting on the App Store. |
| "Reviews are the main ranking factor" | ℹ️ Unverified | Shopify doesn't publish ranking weights. Reviews and ratings are a factor. So are keyword relevance (name, subtitle, description, categories), install and listing conversion, retention and uninstalls, and app quality (Built for Shopify). Don't build the plan on one factor. |

⚠️ I couldn't check Shopify's current policy pages from this session. Before shipping anything, have someone read the live App Store requirements and review policy, and confirm the subtitle character limit (I believe it is 62).

## Goal and metrics

Goal: get Metricly into the top 10 for 3–5 realistic keywords within 90 days. Do not target the head term "analytics" first, because it is the most competitive query in the store.

Measure weekly:
- Rank for a fixed list of 15–20 keywords (manual search, logged in a sheet).
- Listing views → installs conversion (Partner Dashboard).
- Installs per week and 30-day uninstall rate.
- Review count, average rating, and review rate (reviews ÷ active installs).

## Phase 0: Baseline (days 1–3)

1. Build the keyword list from the following:
   - Autosuggest on the App Store search box.
   - Competitors' names, subtitles, and categories.
   - Your support and sales tickets ("sales dashboard", "profit tracking", "customer cohorts", and similar).
2. Record today's rank for each keyword. Record conversion, uninstall rate, rating, and review count.
3. Write down your three nearest competitors and their review counts. This tells you how large the review gap really is.

## Phase 1: Listing relevance (weeks 1–2)

Change one block at a time and wait about 2 weeks between changes, so you can attribute rank movement. Start with the subtitle.

1. **Subtitle.** Describe the function with keywords and no claims. Example placeholder, to adapt to real features: `Sales, profit and customer reports in one dashboard` (51 characters).
2. **App name.** Keep the brand and add one descriptive keyword only if the policy allows it.
3. **First lines of the description.** Put the primary keyword and the core benefit up front, in plain language.
4. **Categories and tags.** Choose the most specific categories available. Check whether a less crowded one fits.
5. **Screenshots and video.** The first screenshot should show the outcome, such as a real dashboard with a caption of the question it answers. This lifts conversion, which feeds ranking.
6. **Claims.** Use only claims you can prove. Put customer counts and ratings in a place Shopify allows, such as case studies outside the listing text, and only if they are accurate.

## Phase 2: Legitimate review growth (weeks 2–8)

1. **Trigger a neutral in-app prompt after a success moment.** Examples are the first report viewed three times, or a saved dashboard in week 2. Don't show it on install day.
2. **Ask everyone.** Don't show the review link only to happy users and route unhappy ones elsewhere. That is review gating, and it is a policy risk.
3. **Link directly to the App Store review page.** Use neutral wording, with no star count and no reward.
4. **Add a support follow-up.** After a ticket closes, send a plain email: "If Metricly has helped, a review helps other merchants find it." Avoid asking for a specific rating.
5. **Reply to every review within 48 hours.** Fix the issues that low reviews raise, then say so in the reply. This lifts later ratings and conversion.
6. **Set a target.** Aim for a review rate of 2–5% of active installs per quarter, then compare against the competitor gap from Phase 0.

## Phase 3: Product quality and retention (weeks 3–12)

1. Cut time-to-first-insight. Pre-build the 3 reports most merchants need, so the dashboard isn't empty on day 1.
2. Review uninstall reasons and day-7 activation, and fix the biggest drop-off.
3. Check app performance and Web Vitals impact on the storefront, if any. Slowness drives uninstalls and bad reviews.
4. Check eligibility for Built for Shopify. The badge gives visibility and rank benefits. Confirm the current thresholds (installs, rating, review count, performance, design) in Shopify's docs and track the gap.

## Phase 4: Off-store demand (ongoing, from week 4)

Searches for "Metricly" and installs from outside the store also signal relevance. Run two low-cost channels:
- Short how-to content for merchant questions your keywords imply, such as "how to track profit by product in Shopify".
- Answers in Shopify community and merchant forums, with a link to the listing when relevant.

## 90-day schedule

| Weeks | Work | Gate |
|---|---|---|
| 1 | Baseline and keyword list | Sheet filled |
| 1–2 | Subtitle, then description | Rank re-check at week 3 |
| 2–8 | Review prompt, support follow-up, reply routine | Review rate tracked |
| 3–12 | Activation and uninstall fixes, BFS gap | Uninstall rate down |
| 4+ | Content and forum answers | Branded searches up |
| 12 | Review results, decide next keyword set | Top 10 for 3+ keywords |

## Risks

- **Policy violation.** The 5-star button and the free month are the two highest-risk ideas, so remove both before launch.
- **Slow signal.** Rank changes take time to appear, and changing several things at once hides what worked.
- **Review gap.** If competitors have thousands of reviews, reviews alone won't close the gap in 90 days. Listing conversion and retention have to carry part of the load.

## Decisions for the team

1. Which 3–5 keywords are the real targets? Name them before Phase 1.
2. What are Metricly's three strongest provable differentiators for the subtitle?
3. Who owns the weekly rank log and the review-reply routine?
4. Should the free-month idea become a non-review offer, such as a referral or annual-plan discount?