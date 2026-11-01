# Plan for Pipeworks CRM Sync

Fix support and compatibility first, tidy the readme second, and ask for reviews honestly. Skip all three of your growth lead's tactics. I haven't checked current wp.org rules against live pages, so check the wording against the current Plugin Guidelines before you act.

## Verdict on the three suggestions

| Suggestion | Verdict | Why |
|---|---|---|
| Daily SVN commits to look fresh | ❌ Don't | The Plugin Directory treats SVN as a development log, and empty commits don't change what users see. "Tested up to 6.2" and a 14-month-old release are the real freshness signals. Fake churn also looks bad if the plugin team ever audits you. |
| 20% discount for 5-star reviews | ❌ Don't | wp.org prohibits incentivized or manipulated reviews. A "5-star only" condition is worse, because it also games the rating. The penalty can be review removal or plugin closure, and you'd put 3 years of history at risk for a small rating gain. |
| Answer paid-plan billing in the wp.org forum | ❌ Don't | The forums are for the free plugin hosted there. Commercial support for a paid product is not allowed, and billing details are personal data in a public thread. Answer once with a pointer, and handle billing in your helpdesk. |

## What to do

### 1. Fix support first (days 1–14)

This is probably your biggest lever. wp.org shows "issues resolved in the last two months" on your plugin page, and 60% unanswered tells visitors the plugin is abandoned.

1. **Subscribe a human to the forum.** Use the plugin's forum RSS or email subscription, and add support reps through the plugin's team settings.
2. **Triage the backlog.** Reply to every unanswered thread, even if the answer is "fixed in the next release" or "no longer reproducible, please reopen if it persists." Mark threads resolved only after replying.
3. **Set an internal target** of a first reply within 2 business days, and track it weekly.
4. **Stop the auto-reply loop.** If support@ goes to a helpdesk that only auto-replies, make a person own the queue. Add a forum-to-helpdesk handoff for issues that need private data.
5. **Pin one forum reply template for paid or billing questions.** For example: "Billing and paid-plan questions can't be handled in these forums. Please contact us at [your support page]. Happy to help with the free plugin here."

### 2. Ship a real compatibility release (weeks 2–5)

1. Test against the current WordPress release and supported PHP versions. Fix deprecations and warnings, and run your security checks, including escaping, nonces, and capability checks.
2. Bump `Tested up to`, `Requires at least`, and `Requires PHP`. Write a changelog that says what changed.
3. Release it. Then tag a fresh compatibility bump on each new WordPress major release, ideally testing the release candidates beforehand.
4. After that, release when there is something real to ship. A modest cadence tied to actual fixes beats daily noise.

An outdated "tested up to" can show a compatibility warning on the plugin page. That likely costs you more installs than anything else on this list.

### 3. Clean up the readme (same release)

1. **Tags:** wp.org only uses the first 5, and stuffing 18 reads as keyword spam. Keep 5 that describe what the plugin does.
2. **hubspot and salesforce:** keep them only if the plugin actually integrates with those products. If it does, naming them is accurate and useful, so put them in the top 5, mentioned factually. If it doesn't, remove them. Competitor tags that don't match the product are a guideline problem and a trust problem.
3. **Name and short description:** put the searchable terms there, in plain language. For example: "Pipeworks CRM Sync – sync WordPress forms and users with [CRMs you support]."
4. **Target long-tail searches** like "sync WordPress forms to HubSpot." Page 4 for the generic head term "crm" is not a realistic place to win. Pick 5–10 specific queries, record your current position for each, and track them.
5. **Check the rest of the page:** current screenshots, an FAQ that answers the top forum questions, and a banner and icon.

### 4. Ask for reviews honestly (after the release)

1. Add a one-time, dismissible admin notice after a successful sync, with neutral wording and a link to your wp.org reviews page.
2. Don't offer anything in exchange for a review, and don't filter by sentiment. Don't send only happy users to wp.org and unhappy ones to private support.
3. Reply politely to existing reviews, especially low ones about problems you've now fixed. Many reviewers update their rating when the fix lands.
4. If you want to reward customers, do it on a basis unrelated to reviews, such as a newsletter or loyalty discount that anyone can get.

### 5. Measure

- Weekly: forum first-reply time, resolved percentage, new reviews and average rating, active installs.
- Every 2–4 weeks: position for your 5–10 target queries.
- Compare the support and compatibility changes against the baseline after about 8–12 weeks.

wp.org doesn't publish its ranking formula, so I can't promise a position. In practice, the signals it appears to weigh are text relevance, active installs, ratings, support responsiveness, and compatibility freshness. Steps 1–3 improve all of those honestly.

## Reply to your growth lead

Their goal, looking active and getting reviews, is right, but those three tactics break wp.org rules and put the plugin at risk. The same goal is met safely by fixing support, shipping a real compatibility release, and asking for reviews without incentives.