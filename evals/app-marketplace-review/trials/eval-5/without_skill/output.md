# Halyard Cloud review queue: what to do

**Don't hire a third reviewer first.** Every submission gets the same full manual review, and that design is the problem. A third reviewer adds 50% capacity to a process that spends most of its hours on low-risk work. Fix the process first, then spend the headcount on the part that stays hard.

I haven't seen your data, so the numbers below are illustrative. Step 1 replaces them with real ones.

## The math

- Inflow is 640 reviews a month: 40 new apps and 600 updates.
- Two reviewers have about 240 productive hours a month, so roughly 22 minutes per review even if they did nothing else.
- A full review of a new app takes hours. A routine update takes minutes. Treating them the same is why you're at 6 weeks.

## Next 14 days (no headcount needed)

1. **Measure the work.**
   - Sample the last 100 updates and the last 40 new apps.
   - Tag each one: permissions or scopes changed, new data access, new network domains, new dependencies, or none of these.
   - Pull the last 200 rejections and rank the failure reasons.
   - Everything below depends on this.

2. **Stop the SAST ticket flood.**
   - Sample 100 of the 1,900 tickets, looking for criticals first. Reviewers who stopped opening tickets may have missed real ones.
   - Bulk-close the rest with a note.
   - Change the wiring: run SAST inside the submission flow and send findings to the developer, not the review team.
   - Reviewers should see one summary per submission, limited to new, high-severity findings in the diff.
   - Everything else is advisory, shown to the developer only.

3. **Call the three partners this week.**
   - Give them a dated plan, not an apology.
   - Offer a trusted-publisher fast lane (see tier 0 below). It also solves your problem, so it isn't a favor.

## Days 15 to 60: tier the reviews

| Tier | What qualifies | Treatment |
|---|---|---|
| 0 | Update from a publisher in good standing, with no change to permissions, scopes, data access or domains, no new vulnerable dependencies, and no new high-severity SAST finding | Auto-approve. Sample 10% afterwards. |
| 1 | New dependencies or changed data handling | Diff-only review, about 10 minutes |
| 2 | New permissions, scopes or payment/auth changes, and every new app | Full review, as today |

Illustrative split for the 600 updates: 70% tier 0, 25% tier 1, 5% tier 2.

- **Tier 0:** 420 auto-approved.
- **Tier 1:** 150 × 10 min = 25 hours.
- **Tier 2:** 30 × 60 min = 30 hours.
- **New apps:** 40 × 2 hours = 80 hours.
- **Total:** about 135 hours against 240 available. That clears the backlog with the current team.

Replace my percentages with your step 1 sample before committing.

## Cut the 50% first-submission failure rate

- Take the top five rejection reasons from step 1. Typical ones are a missing privacy policy, a manifest error, requested permissions that don't match the stated function, and a broken install.
- Turn each into an automated pre-submit check that the developer can run themselves. Submissions that fail get bounced at intake with no human involved.
- Publish the checklist, so developers fix problems before submitting.
- Be honest about the gain. Only 40 new apps a month are first submissions, so this mainly saves resubmission cycles. Check whether updates also fail often. If they do, this matters more.

## Where the headcount goes

Hire a **review-automation or security engineer** who can also do reviews, not a third reviewer. They own the intake checks, the tiering rules, the SAST triage and the post-publish scanning. That keeps the automation maintained, which is where homegrown pipelines usually decay.

Switch to a plain reviewer hire only if step 1 shows most of the load is judgment-heavy tier 2 work. In that case tiering won't save enough hours.

Hiring takes 2 to 3 months, so nothing above waits for it.

## Risk guardrails for auto-approval

- **Publisher reputation:** any violation drops the publisher out of tier 0 for 12 months.
- **Post-publish scanning and a kill switch:** continuous scanning, plus the ability to delist fast.
- **Escape-rate tracking:** count post-publish incidents on auto-approved updates. If the rate exceeds a threshold you set in advance, tighten the tier 0 criteria.
- **Audit trail:** every auto-approval records which rules it passed.

## What to track weekly

- Queue age (p50 and p90)
- Throughput by tier
- Escape rate
- First-submission failure rate
- Reviewer hours per tier

## Expected outcome

| Timeframe | Expected state |
|---|---|
| Week 2 | SAST noise gone, partners have a dated plan |
| Week 6 | Tiering live, queue visibly shrinking |
| Week 10 to 12 | Backlog cleared, new hire starting |

## Decisions I need from you

1. Can you share the last 100 updates and 200 rejections so I can replace the illustrative numbers?
2. Does leadership accept auto-approval with sampling, or does policy require a human on every release? That is the biggest lever, and if the answer is no, the plan changes.
3. Do your partners' contracts include review SLAs? That decides how hard the fast lane has to be pushed.