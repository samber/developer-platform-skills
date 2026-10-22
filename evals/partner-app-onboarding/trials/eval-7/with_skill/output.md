# Allocating the 4 partner-manager hires at Ostara Cloud

**Recommendation:** put only 2 of the 4 hires on named ISV coverage. Put the other 2 on the two things that are drowning you: the repeated questions and the review gate.

I skipped the one-question-at-a-time interview because you asked for a single deliverable. The assumptions I made are listed at the end, with what would change the answer.

## Why not 4 managers on the ISVs

- The rungs, ordered by unblock power:
  - Default: docs plus a community forum.
  - Real-time chat.
  - Office hours.
  - Named partner managers.
- The ladder stacks. Named managers come last, and only for commercial partners. The documented pattern is to assign them to ISVs and never to individual developers.
- Your pain is 12 repeated questions about event-schema versioning and the review checklist. That is a docs and enablement failure. Named managers fix it one conversation at a time, for 40 accounts only.
- Roughly 860 developers build private integrations for their own employers. They generate no revenue for you, so they get self-serve only.
- Support depth should follow commercial value, not partner count.

## Allocation

| # | Hire | Covers | Owns | Success signal |
|---|---|---|---|---|
| 1 | **ISV partner manager** | Top ~20 ISVs by sell-through revenue | Named relationship, submission and launch coaching, seller-track agreement at first listing, feedback to product | ISV time-to-first-submitted-app, ISV first-review pass rate |
| 2 | **ISV partner manager** | Remaining ~20 ISVs | Same as #1 | Same as #1 |
| 3 | **Developer enablement and support** (title it partner manager only if finance requires) | All ~900 developers | Forum triage, the 12-question deflection backlog, office hours, the event-schema versioning guide and migration notes | Share of Discussions threads that duplicate a known answer, time to first answer |
| 4 | **Review and submission-gate lead** (same title caveat) | All developers | The published review checklist, the pre-submission validator spec, rejection-reason analysis, the 4-checkpoint funnel | First-review fail rate, submission-to-approval time |

- **Split of #1 and #2:** split by revenue, not alphabet. Give #1 the accounts where a lost ISV hurts most.
- **Why 2 ISV managers:** 1:20 is already stretched, and 4 managers would mean 1:10 for accounts that are 4% of your developers.
- **Profile for #3 and #4:** hire technical people, ideally ex-platform or integration engineers. Both roles are closer to developer support than to account management.
- **Title mismatch:** if Finance approved "partner manager" headcount only, ask whether 2 slots can be reclassified. If not, hire PMs with an engineering profile and write the job content as above.

## Sequence

1. **Weeks 0-4, before anyone starts, using current staff:**
   - Rank the Discussions threads and pin one canonical answer for each of the 12 questions.
   - Publish the review checklist with the reason behind each item, so partners don't discover requirements at first rejection.
   - Write the event-schema versioning guide, with a migration page for each breaking change.
   - Disclose every post-launch threshold (tenure, install counts, certification eligibility) in the onboarding docs.
2. **Hire #3 and #4 first.** Their effect on the drowning shows within a quarter. Hire #1 and #2 in parallel if the recruiting pipeline allows. Otherwise hire #1 first and #2 once the ISV list is validated (see assumption 1).
3. **Weeks 4-12:**
   - #3 starts biweekly office hours aimed at the review gate and schema versioning. These need an engineer rather than a peer.
   - #4 scopes the pre-submission validator with engineering and wires the four funnel checkpoints (below).
4. **Quarter 2:** review the allocation against the baselines below.

## Instrument before you hire further

The funnel checkpoints are:

1. Signup to sandbox provisioned.
2. Provisioned to first API call.
3. First API call to first app submitted.
4. Submission to approval.

- "Time-to-first-submitted-app" is a self-defined metric, not an industry-named one. Label it that way in reports.
- Baseline every checkpoint on your own first quarter, then track the trend. Set no absolute pass bar.
- **Working thresholds** (self-set, not industry standards):

  | Signal | Action |
  |---|---|
  | Checkpoint 2 above ~10 minutes | Fix provisioning and quickstart friction before anything else |
  | First-review fail rate above ~30-40% | Build the pre-submission validator before considering mandatory education |
  | Time-to-first-submitted-app far above review duration | The bottleneck is docs and enablement, not the review team |

## Don't do this

- **Mandatory certification before submission.** It isn't standard practice on any major marketplace, and it adds friction without fixing the docs gap.
- **Named managers for the ~860 private-integration developers.** It's the most expensive rung applied to your lowest-value segment.
- **A graded entry tier.** Entry tiers gate nothing at most programs, so don't invent one.
- **Asking for monetization terms at registration.** Seller agreements belong at first listing, not at signup.

## Assumptions and what would change them

1. **The "~40 ISVs" is real.** Verify it from transaction data before assigning accounts. If many of the 40 are dormant, one ISV manager is enough and the other slot goes to #3.
2. **Self-service signup and instant sandboxes already exist.** You didn't say. If sandboxes sit behind approval, fix that first, since partners approved to build but unable to test churn silently.
3. **Time to a first working app is hours to days.** If it is weeks to months, add a guided, higher-touch path for ISVs. That strengthens the case for the ISV managers.
4. **Data sensitivity is medium, not high.** Observability data can carry customer-sensitive content. If it is high, the review gate matters more, so keep #4 as defined. It may also argue for an application-reviewed seller track.
5. **No hard launch date, and the goal is a compounding ecosystem.** That favors the enablement hires. A hard deadline would favor the cheaper rungs (docs plus forum) and delay #1 and #2.
6. **The 12 repeated questions all come from partners.** If a share come from your own customer-facing teams, reassign that share to internal enablement.