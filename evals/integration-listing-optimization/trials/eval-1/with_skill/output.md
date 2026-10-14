**Next action (10 min):** Tell your head of growth that two parts of the Q4 plan can't run on Slack as written. The skill classifies Slack as **data-dark** (vendor-official, from the skill's benchmark file). It says Slack gives submitters no view, install, or conversion data, and no review or rating system. I couldn't browse in this session, so check Slack's current partner docs before the Monday kickoff.

## 1. What breaks

| Plan item | Problem | Replacement |
|---|---|---|
| A/B test two listing descriptions, pick on view-to-install | No view data. The listing is one page, so you can't split traffic. | A/B the two copy variants on **your own landing page**. Self-track installs. Write the Slack listing once, from buyer language. |
| 40 reviews by December, star rating shows up | Slack exposes no review system, so there is nowhere to post a review and no star rating to appear. | Re-aim the review goal at a platform that has reviews. This is your decision (question 3 below). |
| Test for six weeks, then run the email campaign | The campaign doesn't depend on the test winner. Running them in sequence wastes the weeks before December. | Run them in parallel. |
| Weekly dashboard on views and conversion | The view number doesn't exist on Slack. | Dashboard on your own funnel and your install ledger (section 4). |

Three claims here carry a provenance label (vendor-official, corroborated inference, single-source inference, analogy):
- **Vendor-official:** Slack has no analytics or reviews. Verify before kickoff.
- **Corroborated practitioner inference:** the 5-10% email conversion. It is a Shopify-sourced figure, not Slack data. Plan for the low end.
- **Analogy (consumer app stores):** any rating-to-conversion lift numbers. Don't quote them.

## 2. Owners

I have no names, so assign these roles in the kickoff.

| Role | Owns |
|---|---|
| **You** | Final calls, weekly review, the reframe conversation with growth |
| **Head of Growth** | Landing-page test, traffic, dashboard review |
| **Engineering (about 3 days)** | Install ledger, uninstall events, UTM/state plumbing |
| **Lifecycle/email owner** | Review-ask campaign, send ops, unsubscribe handling |
| **Support lead** | Post-support review ask, no cherry-picking |
| **Listing owner** | Listing copy, gallery, 30-60 day refresh. This is your question 7 and I don't know who it is. Name one person. |

## 3. Timeline

Today is Thu 2026-10-08. Week 1 starts Mon 10-12.

1. **Wk 1-2 (10-12 to 10-23): instrument and baseline.**
   - Engineering builds the install ledger: the OAuth token store as the install record, plus the `app_uninstalled` and org-level uninstall events.
   - Define "activated" as the first standup or retro run within 7 days of install, or whatever your product's equivalent is.
   - Add UTM and state parameters to every "Add to Slack" button you control.
   - Pull baseline weekly installs, uninstalls, and activation from the ledger.
   - Draft two description variants from real buyer language (support tickets, sales notes).
   - Write the review-ask email and decide where it points (question 3).
   - **Gate 1 (10-23):** the ledger reconciles to the Slack-side count, and the funnel events fire.
2. **Wk 3-8 (10-26 to 12-04): landing-page A/B, run in parallel with the review campaign.**
   - Split traffic 50/50 across the two variants, and measure landing view to completed install.
   - Variants differ in description copy only. Hold the hero image and layout constant.
   - Cap the test at six weeks. Stop early only on the pre-set rule in section 4.
3. **Wk 4 (11-02): review-ask wave 1.**
   - Send to all qualifying workspaces (definition below).
   - Send one reminder to non-responders on 11-16. Nothing else after that.
4. **Wk 8 (12-07): decide and port.**
   - Port the winning copy to the Slack listing. This is the only listing edit in the plan.
   - Start the 30-60 day refresh clock, owned by the listing owner.
5. **Standing:**
   - Weekly 30-minute review with growth.
   - Watch uninstalls.
   - Re-check Slack's listing rules before each refresh.

## 4. Measurement setup

**Landing-page test (the only real A/B)**
- Primary metric: landing view to completed install, per variant.
- Sample size per arm is roughly 16·p(1−p)/δ², where p is the baseline rate and δ the absolute lift you want to detect (80% power, 5% significance). For example, p=10% and a 20% relative lift (δ=0.02) needs about 3,600 visitors per arm.
- Pre-register the rule: if six-week traffic falls short of the required n, don't declare a winner. Pick on judgment and say so.
- Lifts under 2% count as noise (the skill's rule, analogy-sourced). 2-5% is marginal, 5-10% meaningful, and above 10% a strong winner.
- Caveat: landing-page visitors are not Slack-marketplace browsers. The test shows which copy persuades, not how the listing ranks.

**Install attribution (inference, label it)**
- OAuth installs that carry your UTM or state value came from your own surfaces.
- OAuth installs without them are "marketplace or other". That is a proxy, not a count of marketplace views.

**Review campaign**
- Qualifying workspaces: all active workspaces, with no filter on satisfaction or NPS. Selective asking is the compliance risk the skill names.
- No incentives of any kind (discount, gift card, feature unlock). Platforms treat these as removal-or-termination offenses (Shopify publishes the penalty ladder). Also no team reviews and no swaps.
- Include an opt-out from future asks.
- Check your lawful basis for emailing workspace admins before the send.
- Target math: 900 × 5% = 45, 900 × 3% = 27. Plan on the low end, because 5-10% is a Shopify-sourced figure. Rate your 40-review goal as achievable only if the platform has a review page and the ask converts at 4% or better.
- Post-support ask: the support lead adds a review link after a positive resolution, at a natural pause.

**Weekly dashboard (30-minute review)**
1. Installs, uninstalls, and net installs from the ledger.
2. Activation rate (first run within 7 days).
3. Landing test: visitors, installs, and conversion per arm, plus n against the required n.
4. Review campaign: sends, clicks, published reviews, and trailing-90-day velocity.
5. Listing changes in the last 30 days, and the refresh date.

Retention comes first in the review. Uninstall rate feeds ranking negatively where that is corroborated, and a better listing cannot outrun churn.

## 5. Skill gates

- [ ] Gate 1: Slack classified as data-dark, install ledger in place (10-23).
- [ ] Indexed and visible fields carry buyer language, per Slack's own documented conventions.
- [ ] The first three gallery assets are unique, in-UI, captioned, and show no pricing or review claims in the image.
- [ ] Every review ask maps to a sanctioned trigger.
- [ ] Every ranking claim carries a provenance label.
- [ ] A 30-60 day refresh cycle exists with a named owner.

## 6. Open questions (answer these in this order)

1. By "December", do you mean 12-01 or 12-31? That decides whether the email wave fits.
2. What is your weekly landing-page traffic? It sets the test length.
3. Which review surface do you want to use? G2 and Capterra were not benchmarked in this skill, so I have no provenance on them. Or drop the review goal and keep the email as a feedback survey.
4. Where do the 900 contact emails come from (admin installers, billing contacts), and what is your lawful basis?
5. Who is the listing owner, and what changed on the listing in the last 90 days?

**Next:** answer question 1 and 3 and I'll turn this into a 1-page note for your head of growth.