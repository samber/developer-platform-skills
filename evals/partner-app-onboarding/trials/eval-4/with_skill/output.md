**There is no industry benchmark for "time to first submitted app".** Nobody publishes one. Marketplaces keep partner-onboarding funnel numbers internal. The metric sits in an unnamed gap between two named ones. If the exec wants a benchmark, tell them this is a metric you're defining yourselves, and label it "self-defined" on the dashboard.

**Adjacent numbers you can cite (directional only, all from other contexts):**
- **Time-to-first-call (signup to first API call):** the established DevRel metric.
  - Best-in-class is under ~90 seconds at two leading API companies. That is an aspirational ceiling, not a norm.
  - Working threshold: if it's above ~10 minutes, fix onboarding friction first.
  - Developers who make a first call within 10 minutes are 3-4x likelier to convert to paid. That evidence comes from general dev-tool funnels, not marketplace partners.
- **Time to first deal:** Forrester's 2018 partner-onboarding report says a partner not selling within 90 days "most likely never will". It measures selling, not building. It is not an app-submission benchmark.
- **Review duration, the only well-documented part of the funnel:**

| Platform type | Review time |
|---|---|
| Light self-service commerce platform | 5-10 business days |
| CRM marketplace | up to 60 days total |
| Enterprise collaboration marketplace | 10-15 business days |
| Messaging-platform marketplace | ~10 days, then up to ~10 weeks |
| Application-gated enterprise platform | 6-9 weeks end to end |

  Use these only to judge whether your submission time is long compared with review time.

**Why this works badly as a single north-star, 5 weeks in:**
- **Survivorship bias.** The median covers only partners who already submitted. At 5 weeks the fast ones are in and the stalled ones are invisible, so the number looks great and means little.
- **Fix:** show "% of signups that submitted within 14 / 30 days" per weekly cohort next to the median.
- **No baseline yet.** The skill says to baseline against your own first quarter and track the trend. Set no absolute target.
- **Approval can't show yet.** Review takes 1-10 weeks on comparable platforms, so approvals are barely visible at week 5.

**What belongs on the dashboard:**
1. **North-star:** time to first submitted app (median plus the cohort % above), labelled self-defined.
2. **The four funnel checkpoints**, as conversion and median time per weekly signup cohort:
   - signup to sandbox/credentials provisioned
   - provisioned to first API call (alert above ~10 min)
   - first API call to first app submitted
   - submission to approval
3. **First-review fail rate and rejection cycles.**
   - If the fail rate is above ~30-40%, build a pre-submission validator before adding education requirements. That threshold is self-set, not a standard.
   - Platforms studied show 2-3 rejection cycles. Rejection reasons cluster on UI standards, privacy webhooks and billing compliance.
4. **Submission time vs review duration.** If time-to-submit is far longer than review time, the bottleneck is docs and enablement, not the review team.
5. **Stall point per partner.** Show where each non-submitting partner stopped. Without it, "signed up but nothing shipped" has no diagnosis.

**One gap you should check:** I skipped the skill's interview because you asked for a quick answer. That means this assumes self-service signup with sandbox provisioned at signup, and a review gate you control. If either is wrong, checkpoint 1 and the review rows change. For example, an application-gated entry needs an extra "applied to admitted" step.

**Next:** tell me whether Halmsted partners get a sandbox at signup or only after approval. That decides whether checkpoint 1 is worth tracking.