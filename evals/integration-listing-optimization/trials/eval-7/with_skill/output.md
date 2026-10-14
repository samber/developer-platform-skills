# Glasswing AppExchange overhaul plan

Next action: Monday morning, open Partner Community → Publishing → Analytics. If that tab loads, the "no numbers" premise is wrong, and everything below gets cheaper.

I read the skill and both references. I didn't browse to verify current AppExchange rules, so every platform claim is labeled by provenance. Your answers to the skill's interview questions 1 and 3-10 are missing, so I've marked my assumptions as such.

## 1. Two premises to challenge first

### "No analytics unless Summit tier"

- The benchmark says AppExchange analytics are free to any partner with an active listing (vendor-documented, per the skill's reference).
- That covers tile views, hovers, unique visitors, lead events and installs by traffic source, plus the top search terms driving visits and installs.
- A separate post-install telemetry API serves churn and renewal work.
- I couldn't confirm this against current Salesforce docs. Someone may have checked a different surface, or Salesforce may have changed access since. Check before accepting the premise.
- If the tab is missing, classify AppExchange as data-dark for you. The plan then collapses to "write once, drive external traffic, self-track installs" (see section 3).

### "A stronger listing fixes the churn"

- The skill's failure mode is blunt: a better listing can't outrun churn. The new installs it wins become the uninstalls that sink it.
- Your theory is half plausible. Fit-qualifying copy can improve the mix.
- Nothing in your data shows that the 31% comes from bad fit rather than onboarding failure, a product gap, or an install-then-evaluate pattern.
- Uninstall rate feeds ranking negatively where corroborated (inference, tier 2). Ship the listing and diagnose churn in parallel. Don't bet the churn number on the listing.

## 2. Assumptions to confirm

| # | Question | My assumption |
|---|---|---|
| 1 | Which marketplace | AppExchange only, live |
| 3 | Brand recognition | Challenger: unknown name in the ecosystem, so keywords matter more than brand |
| 4 | Buyer language | **Missing, the most important input** |
| 5 | Review base | Unknown; counts, average rating and the newest ten need pulling |
| 6 | Badge needs | None; Security Review already passed, since you're listed |
| 7 | Listing owner | Nobody today; name one owner now |
| 8 | Deadline | Ship next week, so text and image levers only |
| 9 | One-off or compounding | Compounding: a 14-month-stale listing needs a refresh cycle |
| 10 | Effort ceiling | Unknown; ask for owner hours per month |

The deadline deletes the badge pursuit and any standing program from the "ship next week" scope. Reviews start as a low-effort sanctioned trigger, not a launch-week deliverable.

## 3. Stage 1: Instrument (Mon)

1. Open the Analytics tab and export everything available, ideally 12+ months of history.
   - Record views, view-to-install conversion by traffic source, and the top search terms.
2. If the data exists, that's your baseline, and you don't need to wait to collect one.
3. If it doesn't, build the starved option:
   - an install ledger from your own auth-token store
   - an uninstall event subscription
   - UTM-tagged external links to the listing
4. Pull your own install and uninstall records with dates. You'll need them for the churn work in section 7 either way.
5. Don't skip a before-snapshot. Screenshot the current listing, including title, tagline, categories and gallery order.

## 4. Stage 2a: Keyword rewrite (ship Tue-Wed)

This is the default rung: highest efficiency, hours not weeks.

1. **Source the buyer words.** Take support tickets, sales-call notes and the AppExchange search-term report (if you have analytics). Build a list of 15-25 phrases buyers actually type.
2. **Find the indexed fields.** AppExchange doesn't publish a field-by-field weighting (nothing vendor-official on its search algorithm). Read the listing builder for the title, tagline, description and search-term fields, then put the strongest phrases there.
3. **Check the title convention.** Don't assume keyword-first. One benchmarked marketplace instructs brand-first, and AppExchange's own guidance decides yours.
4. **Use outcome language.** The 2026 unified marketplace's intent-based search reportedly rewards outcomes ("forecast accuracy", "pipeline hygiene") over feature labels. This is inference, recent and still settling.
5. **Choose the category carefully.** AppExchange allows one category plus two industries, the tightest cap of the five marketplaces. Pick the category where buyers look, not the one that flatters.
6. **Write fit-qualifying copy.** State who it's for and who it isn't (team size, CRM setup, required Salesforce edition, required data). This is the one place the listing can directly attack your 31%.
7. **Track coverage and performance separately.** Coverage is which terms are in indexed fields. Performance is where you rank. Coverage without rank means revisit the rewrite.

## 5. Stage 2b: Screenshot overhaul (ship Thu-Fri)

- **Order:** hero (core value) → differentiator → most-loved feature → outcome or proof → supporting. Pull the most-loved feature from usage data, not opinion. The ordering is an analogy to mobile ASO, not B2B proof.
- **Count:** 4-6 images. The more-is-worse finding is consumer data.
- **Content rules:**
  - real in-product UI, captioned
  - crop out customer data
  - no pricing claims
  - no review claims baked into images
  - no duplicates or logo-only images
- **Size:** the benchmark gives about 700×467 (roughly 3:2) for Salesforce. Confirm in the listing builder.
- **Video:** AppExchange allows 1-3 minutes, but it's not a week-one item. Add it in the next cycle if the analytics show video views matter.
- **Fit angle:** captions can say "for revenue-ops teams running X". That's another no-cost filter.

## 6. Order of changes and what you can learn

- Changing keywords and screenshots in the same week confounds attribution.
- B2B listing traffic is low, so a two-week window may not reach significance anyway. Treat lifts under 2% as noise, and treat 10%+ as a clear winner.
- Suggested sequence: keywords Tuesday, screenshots Thursday, then read the weekly conversion against your baseline. Don't over-read any single week.

## 7. Churn: run in parallel, starting Monday

1. From your ledger and the telemetry API, cut the 31% by:
   - install date and source
   - Salesforce edition and org size
   - the first action or non-action after install
2. Check whether uninstalls cluster in days 0-3 (setup failure), at the trial boundary, or around day 30-45 (value not reached).
3. Interview five recent uninstallers. Ask what they expected from the listing versus what they got.
4. Decide from that data:
   - **Expectation mismatch:** the listing copy matters. Your theory holds, and the fit-qualifying copy is the fix.
   - **Setup or value failure:** the listing can't fix it. Onboarding and product do.
5. Set the success metric as the 45-day uninstall rate for post-overhaul cohorts, compared with the 31% baseline. This takes 45+ days to read.

## 8. Reviews (standing, start small)

Only sanctioned triggers. Never incentivized, never from your own team, never swapped with other vendors.

- AppExchange coaches targeted asks timed to a success milestone, engaging negative reviews publicly so they get amended, and keeping reviews fresh.
- Its Trusted Reviews program badges credible reviewers, so a few detailed reviews from real admins beat many thin ones.
- Start with a named person asking three or four customers who hit a milestone. If you have a review base worth protecting, also reply to any negative review.
- Recency and velocity matter more than lifetime totals (corroborated inference). Pay-off takes quarters, not the launch week.

## 9. Stage 5: Defend (standing)

- Name a listing owner now.
- Refresh every 30-60 days: copy, screenshots, and a check of the competitors' keywords.
- Re-check AppExchange's current listing rules before each cycle. They change.
- Watch uninstalls monthly.

## 10. Gates before shipping

All five must pass. These are self-set, not an external bar.

1. Analytics are on, or AppExchange is classified data-dark with a ledger in place.
2. Every indexed field carries real buyer language, in the convention AppExchange documents.
3. The first three screenshots are unique, in-UI and captioned, and every review ask maps to a sanctioned trigger.
4. Every ranking claim carries a provenance label:
   - vendor-official
   - corroborated inference
   - single-source inference
   - analogy
5. A refresh cycle exists with a named owner.

## 11. Week schedule

| Day | Work |
|---|---|
| Mon | Check analytics, export baseline, snapshot current listing, start the churn cut |
| Tue | Gather buyer language; ship the keyword and category rewrite |
| Wed | Churn interviews; draft screenshots and captions |
| Thu | Ship screenshots |
| Fri | Name the owner; send the first sanctioned review asks; record baseline and changes in memory |

## 12. What I need from you

1. Can you see the Analytics tab? This one answer decides section 3.
2. What exact phrases do buyers use for what Glasswing does?
3. How many reviews does the listing have, and what's the average rating?
4. Who owns the listing, and how many hours a month can they spend?

## 13. What this plan can't promise

- **No predicted lift.** I won't give you a percentage; the only numbers I have are consumer app-store figures.
- **No quantified ranking claims for AppExchange.** The ranking factors are inferred, not published.
- **Churn is not a given.** If the data says setup failure, the listing won't fix it.