Next action: open Partner Dashboard → Apps → Mailwise → Distribution → Built for Shopify, and screenshot every unmet criterion. About 20 minutes. This is the source of truth. I wrote the thresholds below from memory, and Shopify changes them, so confirm each one there.

**Verdict:** 6 weeks is a stretch goal, not a plan. Two gates run on a clock you can't speed up: the 28-day performance data window and review accumulation. The iframe dashboard also fails the auth and UI criteria, so the rebuild comes first. Don't promise the badge to press until Shopify grants it.

## What fails today

1. **Separate Mailwise login.** BFS requires the merchant to be signed in through Shopify, with no second account or credentials. Your iframe login breaks this.
2. **Iframe of the web dashboard.** BFS requires an embedded app built with App Bridge and Polaris that feels native to the admin. A nested iframe also fails on third-party cookies (Safari), and it hurts Web Vitals.
3. **Installs: 20 vs 50 minimum.** These are net, active installs. Dev and test stores don't count.
4. **Reviews: 2 vs about 5 minimum.** A rating floor applies over a trailing window (I recall 4.0+; verify the exact number).
5. **Admin performance.** Web Vitals at the 75th percentile: LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms. Shopify needs enough sessions over 28 days. An iframed dashboard probably misses these.

## Work plan

1. **Weeks 0–1: gap audit and decision.**
   - Run the dashboard check above.
   - Confirm current API use: GraphQL Admin API only, with no REST.
   - Confirm the compliance webhooks work.
   - Confirm scopes are minimal.
   - Confirm billing runs through the Shopify Billing API (if Mailwise bills outside Shopify, that fails too).
   - Estimate the rebuild.
2. **Weeks 1–3: rebuild the app home.**
   - Use managed installation with token exchange and session tokens, so the merchant never sees a Mailwise login.
   - Link the Shopify shop to a Mailwise account automatically. Show a one-click "connect existing account" step only if an account already exists for that email.
   - Build native App Bridge and Polaris screens for the core flows: onboarding, campaign list, and campaign create/send.
   - Keep deep-edit tools, such as the email editor, as an explicit "open in Mailwise" link in a new tab, not an iframe.
   - Don't try to port the whole dashboard.
3. **Week 2 deadline, ship the rebuild.** The 28-day Web Vitals window starts at ship time, so a ship date after week 2 puts BFS past week 6 no matter what else you do.
4. **Weeks 1–6: installs and reviews (marketing, in parallel).**
   - You need about 30 more net installs and 3+ reviews.
   - Use an in-app review prompt after a success moment, such as a first campaign sent. Don't gate it on sentiment, and don't offer incentives. Both violate Shopify's rules.
   - Push installs through the listing, existing Mailwise customers on Shopify, and email to your own base.
   - At the current rate (20 in 3 weeks), 50 is plausible by week 6. A 4.0+ rating on a handful of reviews is fragile, so fix onboarding friction first.
5. **Week 6: submit for BFS review.** Shopify reviews manually after the automated checks, and that review takes time. Expect the badge after week 6 even on a good run.

## Decision for leadership

| Option | Result |
|---|---|
| A. Fund the rebuild now and target the badge, with a realistic date of weeks 8–10 | Honest and achievable |
| B. Run the press push at week 6 on another story (new Shopify features, customer results) and announce the badge when granted | Recommended |
| C. Announce the badge before it is granted | Don't. Shopify can reject it, and the press story turns negative |

**Recommended:** A plus B. Start the rebuild this week and keep the press push on a story you control.

## Risks

- **Rebuild scope creep.** Cap it at the core flows listed above.
- **Review quality.** A few weak reviews sink the rating floor. Fix onboarding before you ask for reviews.
- **Install quality.** Shopify counts net installs, and uninstalls subtract.
- **Criteria drift.** Re-check the criteria list in the Partner Dashboard at week 0 and week 4.

**Next:** after the dashboard screenshot, send me the unmet-criteria list. I'll turn it into a dated task list with owners.