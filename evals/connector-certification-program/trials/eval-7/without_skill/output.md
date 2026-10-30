**Verdict: not ready for exec review.** Fix the five issues below first. The tier ladder is fine for a first pass, but the Platinum tier and the seal have real problems.

## Problems, ranked

1. **Platinum has no stated trust gate.**
   - Top 10 by installs does not say "passes security review."
   - An app with an open security finding could get homepage placement, a webinar slot, and a +40% boost.
   - Fix: require Gold's gates (security review plus a reliability bar) before an app is rank-eligible.

2. **Search boost on install count creates a feedback loop.**
   - Installs earn the boost, the boost earns more installs, and the leaders stay on top.
   - New and niche apps cannot catch up.
   - Customers get ranked by popularity, not fit.
   - +40% is large. Cut it to a small tie-breaker, or drop it and rank on relevance.
   - A/B test the boost before launch.

3. **Nothing in the structure measures whether an app works.**
   - You track no per-app error rates. So badges say "popular" and "reviewed," never "reliable."
   - HR data sync failures hit your brand, not just the partner's.
   - Instrument first: sync failure rate, webhook failure rate, and API error rate per app.
   - Collect 4 to 8 weeks of baseline, then set thresholds from the data.
   - Until then, do not imply quality. Name tiers for what they certify, such as "Verified" for security review.

4. **"Quillbarrow Approved" overlaps the tiers.**
   - Customers see two trust signals: Silver or Gold (security review) and a seal (manual check).
   - Nobody can say what the seal adds. "Checked manually" is not a standard.
   - It also reads as an endorsement, so it creates liability if an approved app fails. Get legal input.
   - Fix: fold it into the top trust level and define what is checked, or drop it.

5. **Tiers mix three separate axes.**
   - Popularity: installs.
   - Trust: security review.
   - Quality: manual check, and error rate once you have it.
   - Gold differs from Silver only by install count. Platinum is a rank, not a standard, so it is a different kind of thing from the other three tiers.

## Smaller gaps

- **Security review lifecycle:** the proposal does not say whether the review expires. Define a re-review trigger, such as new scopes or an annual cycle. Define revocation too. HR data is sensitive PII.
- **Install metric:** it needs a definition. Count active installs, not cumulative. Installs scale with customer base, so apps in big categories always win.
- **Recalculation cadence:** it is unstated. Platinum is zero-sum, so an app can lose its tier without doing anything wrong.
- **Quarterly webinar:** is it one per app, or one shared? Ten per quarter is real team capacity. Name the owner.
- **Cold start:** a new app starts at Bronze with no path to Gold except slow organic installs.

## Recommended shape

1. **Trust track, criteria-based:** Listed, then Verified (security review), then Verified Plus (security review, plus reliability thresholds once measured, plus the manual check). Anyone who meets the criteria gets it, with no quota.
2. **Merchandising track, separate from badges:** a "Featured" program with curated, rotating slots, homepage placement, and webinars. Eligibility requires the top trust level. Selection is editorial, and installs are one input among several.
3. **Search ranking:** relevance first. Only a small boost for the top trust level.
4. **Ship the error-rate instrumentation before launch.** Add the reliability criteria in a v2 once the baseline exists.

## Questions to answer before exec review

1. What is the install distribution? How many of the 150 apps would pass 500 installs? If only about 15 do, Gold is nearly empty.
2. How many apps have passed security review today, and how long does a review take? That sets your review capacity.
3. What exactly does the manual check cover?
4. Who owns the webinar and homepage work each quarter?

**Next:** run the install query for question 1 (active installs per app, last 90 days). It takes about 15 minutes. Then check whether the Gold threshold is sensible.