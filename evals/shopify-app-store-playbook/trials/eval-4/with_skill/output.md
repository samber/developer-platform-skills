# Metricly: Shopify App Store ranking plan

**Route:** Listed. Metricly is live and stuck on page 3 for "analytics".

**Legend:** `†` is a figure from shopify.dev. Shopify changes these without notice, so check the live requirements page before acting. "Reported" means a forum or practitioner claim, not a Shopify-published rule.

**Assumptions.** I could not ask questions, so each gap below has one assumption.
- Metricly is a public app on Shopify App Store billing, not a custom app.
- It has fewer than 50 net installs from paid-plan shops. Built for Shopify is therefore not yet reachable.
- It still uses the original app-card subtitle and title, with no tuned search terms.
- It does not yet use expiring offline tokens.
- Nobody has checked the Partner Dashboard Distribution page.

## Verdict on the team's three ideas

| Idea | Verdict | Why |
|---|---|---|
| Subtitle: "The #1 analytics app - trusted by 10,000 merchants, 4.9 stars" | ❌ Do not ship | Shopify bans stats, "best" claims, testimonials and keyword-stuffed subtitles in the listing†. The packet says the subtitle is one merchant-benefit phrase, with no stats and no keywords added for search. A listing that breaks this fails the quality check and can be demoted. |
| "Rate us 5 stars" button on the dashboard | ❌ Do not ship | Reviews may only be requested through App Bridge's Reviews API (`shopify.reviews.request()`). Shopify shows it at most once per 60 days and 3 times a year†, and never on mobile. Never wire it to a button. The "5 stars" wording is also not neutral. |
| One free month for anyone who leaves a review | ❌ Do not ship, highest risk | Incentivized reviews break requirement 6. Shopify removes the reviews and demotes or delists the app for it†. Your best-rated reviews would disappear and the app could lose its listing. |
| "Reviews are the main ranking factor" | ⚠️ Partly true, overstated | Shopify publishes no ranking formula. Published: Built for Shopify and the "increased visibility" achievement boost search†. Reported: an exact phrase in the app title outweighs review count early. Merchant engagement, uninstall rate and install velocity also count (reported). Reviews matter, but they are not the one lever. |

## Plan

### Phase 1: remove the violations (this week)

1. Drop all three ideas above.
2. Audit the current listing against the packet:
   - Subtitle: one benefit phrase, no stats and no search keywords.
   - App details: no "first/best/only", no testimonials, no stats.
   - Screenshots: no reviews, no pricing, no Shopify logo.
   - Pricing appears only in Pricing details.
3. Search the app and the emails for any existing review incentive, review gate, or "only ask happy users" filter. Remove them. A past incentive is a delisting risk, so check first.
4. Check the Quality-check inbox. Answer any email within 7 days† and ship required changes within 30 days†.

### Phase 2: lift the published ranking levers (weeks 1-4)

1. **Title.** Lead with the Metricly brand and add the category term "Analytics" within 30 characters†. Never start with Shopify. This is the reported lever for an exact-phrase match. Keep the TOML app name and the listing name similar, because Shopify checks both.
2. **Subtitle.** Write a plain merchant benefit, for example "See which products and channels drive your sales". It has no stats and no stuffed keywords.
3. **Search terms.** Use up to five†, one idea each (for example sales reports, profit tracking, cohort analysis). Match the categories and tags to Metricly's primary function.
4. **Screenshots.** Use 3-6 real UI images at 1600 x 900†. The first image should show the core report. Do copy and media order with `samber/developer-platform-skills@integration-listing-optimization`.
5. **Uninstall rate and activation (reported).** Find where merchants drop out between install and the first report. Fix the empty-state onboarding. Fewer uninstalls help ranking and Built for Shopify.
6. **Reply publicly to every review**, negative ones first.

### Phase 3: earn reviews the allowed way (starts week 2)

- **Trigger.** Define a real milestone, for example the first dashboard populated after a successful data sync, or the first scheduled report delivered.
- **Mechanism.** Call `shopify.reviews.request()` once, after that milestone. It will not show more than once per 60 days or 3 times a year†, and never on mobile.
- **No incentive, no gating, no filtering.** Everyone who hits the milestone gets the same neutral prompt. Do not ask only happy merchants.
- **Support-led asks.** If a support thread resolves well, you may reply in neutral words with a link to the listing. You may not offer anything in return.
- **Setting expectations.** Reviews will come slowly. Count on tens per quarter at most, not hundreds.

### Phase 4: Built for Shopify (check in week 4, apply when it passes)

Apply only when the Partner Dashboard Distribution page shows every prerequisite passing†:
- 50 net installs from active paid-plan shops.
- 5 reviews, and the unpublished rating floor.
- Admin Web Vitals at p75: LCP 2.5 s, CLS 0.1, INP 200 ms, with 100 calls in 28 days.

Analytics apps must use Web Pixel extensions, never script tags†. Failing one criterion three times in a row suspends the application for three months†. Do not apply early. The badge and "increased visibility" are the strongest published boost, so this is the priority once the prerequisites pass.

### Phase 5: paid traffic for launch weeks only

Store Ads (CPC, search, category, homepage) buy traffic, and relevance lowers the price. Use them for a launch window or a feature release. Do not treat them as the ranking strategy.

## Deadline at risk

Migrate to expiring offline tokens before 2027-01-01†. After that date, non-compliant apps lose their listing and new installs. Their old tokens get 403 errors from 2027-04-01†. If Metricly is not migrated, this outranks every ranking task, so make it the first engineering ticket.

## What to expect

- Shopify publishes no timeline for ranking changes. Expect weeks after a title or search-term change, not days.
- Moving from page 3 to page 1 for a head term like "analytics" is not guaranteed. It is a competitive keyword. Track secondary terms too, such as "sales reports" and "profit analytics".
- Measure weekly: impressions, installs, install-to-activation rate, uninstall rate, review count and rating, and rank for five tracked terms.

## Decisions for you

1. Has any review incentive, rate-us prompt, or happy-user filter ever run on Metricly? If yes, we need a cleanup plan before anything else.
2. Is the app migrated to expiring offline tokens?
3. How many net installs from paid-plan shops and how many reviews does Metricly have today? That tells us whether Built for Shopify is in reach this quarter.