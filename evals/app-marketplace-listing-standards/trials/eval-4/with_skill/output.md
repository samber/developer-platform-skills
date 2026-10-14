# Cadenza listing staleness policy

**Next action (15 min):** split the 41% audit, about 246 listings, by defect type and by install count. The ladder below holds for any split. The cohort order and the circuit-breaker threshold depend on it.

I did not run the interview. I assumed the answers below, so tell me which are wrong:
- Partners maintain their own listings. The catalog is about 600 listings now and 700 or fewer in 12 months.
- Buyers are HR admins doing diligence, so tone stays terse and listings must prove function.
- Cadenza can see which API version each app calls, keyed by app ID.
- No badge program exists. Badges are out of scope.
- Cadenza can build a link crawler, roughly 2 engineer-weeks (my estimate). Reviewer hours are limited.

## Answer to leadership

The $200 fee is not a freshness mechanism, and the policy does not count it as one. It renews billing, not content. If those 246 listings all paid, the audit has already shown that payment checks nothing about a dead link or an old screenshot.

The fee does give you one useful thing: a billing contact. Use it as the fallback when the listing contact bounces.

## Design

The policy has three layers:
1. **Floor:** a browse downgrade, applied automatically.
2. **Default:** "out-of-date listing content" becomes a named, rejectable violation. A calendar sweep enforces it.
3. **Promoted:** version-currency enforcement. Your six-month release cadence and published deprecations do the freshness detection for free.

The no-mass-delisting guarantee comes from three levers:
- Severity classes with different clocks.
- Clocks that start in staggered cohorts.
- Screenshot-only defects cannot cause a delist in the first 12 months.

### Severity classes and consequences

| Class | Defect | Flag | Downgrade | Delist |
|---|---|---|---|---|
| A | Dead landing page, support link or privacy policy | Day 0 | Day 30 | Day 90 |
| B | Other dead link (docs, setup guide, pricing page) | Day 0 | Day 45 | Day 120 |
| C | Stale screenshot | Day 0 | Day 60 | Not in cycle 1. From month 12 on: Day 180 |

Class A is fastest because this is HR data. A dead privacy policy is a compliance problem, not cosmetics.

What each stage means:
- **Flag:** the listing contact gets an email and a console banner. Buyers see no change.
- **Downgrade:** the listing leaves browse, categories and top search ranking. It stays reachable by direct URL and installable. **Publish this penalty in the policy.** An undisclosed ranking penalty reads as arbitrary.
- **Delist:** new installs are blocked. Existing installs are never touched. Data is kept. The partner can reinstate by fixing the defect, and a fix clears the flag within 2 business days. After 12 months the listing is archived.

Escalation uses the listing contact first. If it bounces, use the billing contact.

### Objective rules (publish these)

1. **Dead link:**
   - A URL counts as dead after 3 failures over 7 days, from 2 network locations.
   - 401, 403 and 429 responses count as "unverified", not dead. This avoids false positives from bot blocking.
   - A login-walled landing page, or a PDF or repository used as a landing page, is a violation.
2. **Stale screenshot:**
   - The upload stores a capture-date attestation. A screenshot older than 24 months is stale.
   - A screenshot showing a retired Cadenza UI generation is stale regardless of age. Publish reference images of the retired UI so partners can self-check.
   - When Cadenza ships a major UI change, it publishes a notice. Listings showing the old UI start a Class C clock 90 days after that notice. This replaces any "substantial change" wording, which is subjective.
3. **Out-of-date content** is a named, rejectable violation. It covers description, category, screenshots and links that do not match the current app.
4. **Annual recertification:** once per 12 months, the partner clicks "content still accurate". The crawler and the screenshot clock run alongside. Sending the prompt with the fee invoice is fine as a delivery channel. Paying the fee never clears a flag.

### Version-currency layer

- Derive each app's API version from API traffic, not from self-declaration.
- New listings must be on a supported version.
- When a version is deprecated, every listing on it enters a 60-day migration window. The window length follows the HubSpot benchmark. The deprecation also triggers a full re-check of links and screenshots.
- At the end of the window, an unmigrated listing is downgraded.
- At sunset, an unmigrated listing is delisted, because the app is broken at that point. Adjust this to your actual deprecation and sunset dates.
- This layer catches abandoned apps without any crawler. It does not catch a stale screenshot on a current-API app. That is why the crawler and the annual recertification stay.

## Rollout (the no-cliff plan)

1. **Weeks -2 to 0:** build the crawler and its false-positive controls. Pilot 25 listings with no consequences. Fix the notice emails and the crawler rules.
2. **T0:** publish the policy and release a self-serve "listing health" report in the partner console.
3. **T0 to T0+60:** amnesty window. Partners fix things on their own, and no clocks run.
4. **From T0+60:** clocks start in cohorts of about 40 listings per week for 6 weeks.
   - Order cohorts by install count, highest first. That is where buyer harm is greatest.
   - The first buyer-visible downgrade is at T0+90. The first delist is at T0+150.
5. **One-click "retire this listing":** offer it to partners from the first notice. Many dead listings are abandoned products, and this removes them without a penalty or a fight.
6. **Extensions:** one 30-day extension per listing, on request.
7. **Circuit breaker (self-set threshold, not an industry standard):** if more than 25% of a cohort is still unfixed at its downgrade date, pause the next cohort and review the notices.

**Tradeoff:** about 5 months pass before the first delist. This is the price of not delisting a third of the catalog at once.

## Steady state and worst-case SLA

- The crawler runs weekly on all required URLs.
- Every listing is recertified annually.
- Every API deprecation triggers a re-check.
- Every major Cadenza UI change triggers the screenshot clock.
- **Worst-case freshness SLA:** 12 months, borrowed from Adobe's abandoned-listing rule. It is an adjacent-ecosystem benchmark, not something that applies to you.

## Owners

- **Crawler, version telemetry and clock automation:** platform engineering.
- **Screenshot review, UI reference images, appeals:** marketplace content team.
- **Fixing the listing:** the partner's listing contact.

## Gates

| Gate | Where it is met |
|---|---|
| Objective reject criterion on every field | Dead-link and screenshot definitions above |
| One published geometry per visual asset type | Not covered here. Needed when you publish the full rulebook. |
| Taxonomy cap | Not covered here. Needed when you publish the full rulebook. |
| Every listing has a decay trigger, owner and consequence | Ladder and owners above |
| Badge display rules | None, because there is no badge program |

## KPIs

- **Share of the catalog stale beyond the 12-month SLA.** The target is self-set. Start by measuring the baseline, which is 41% now.
- Share of flagged listings fixed before the downgrade date.
- Crawler false-positive rate.
- Count of retirements through the one-click option.
- Count of delists by class.

I have no benchmark for partner fix rates. Do not promise leadership a number until the pilot cohort reports.

## Open items for other owners

- Refund treatment of the $200 fee when a listing is delisted mid-term. This belongs to legal and monetization.
- Whether Cadenza needs a security re-review trigger alongside this policy. That belongs to the app marketplace review process, not this rulebook.

**Next:** do the audit split from the top of this answer, then send me the defect counts. I will turn the cohort sizes and the circuit-breaker threshold into numbers.