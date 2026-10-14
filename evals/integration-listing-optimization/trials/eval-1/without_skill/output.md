**Next action (10 min, today):** pull the last 8 weeks of weekly listing views and installs from the Slack Marketplace dashboard. Every other number in this plan depends on that baseline.

# Cadenceloop Q4 plan: listing test → 40 reviews

Today is Thu 2026-10-08. Owners are roles, because I don't have your org chart. Put a name on each before Friday.

## 1. Changes I recommend to the plan

1. **Decouple the review campaign from the A/B winner.** The email campaign doesn't need the winning copy. Running them in sequence pushes the campaign into December, right before the Dec 19 to Jan 2 dead zone. Run them in parallel.
2. **Don't run a classic A/B test.** A single Marketplace listing can't serve two versions at once, so this is a sequential test. A plain 3 weeks of A then 3 weeks of B confounds the result with Thanksgiving and Q4 budget cycles. Use a counterbalanced order instead (section 3).
3. **Check statistical power before committing to six weeks.** Rough rule at 80% power and 5% significance: views per arm ≈ 16·p(1−p)/δ², where p is baseline conversion and δ is the absolute lift to detect.

| Baseline p | Lift to detect | Views needed per arm |
|---|---|---|
| 5% | +20% relative (1 pt) | ~7,600 |
| 5% | +40% relative (2 pts) | ~1,900 |
| 10% | +20% relative (2 pts) | ~3,600 |

   If the listing gets under about 500 views a week, the test can only detect big lifts. In that case run it as a copy refresh with guardrails, not as a statistical contest. Gate decision on Oct 16.
4. **The 40-review target is a stretch.** 40 reviews from 900 workspaces needs about 4.5% of workspaces to review. Typical email-to-review rates are low single digits, and I haven't validated that range for your product. Plan for three outcomes: **low 12, mid 25, stretch 40**. Widen the audience from admins to every standup participant (section 4). That is the lever that makes 40 plausible.
5. **The review campaign contaminates the view-to-install metric.** Existing customers who click through to leave a review add views and zero installs. Route every review ask through your own redirect (`/review`) so you count those clicks yourself, then subtract them from Slack's view count.
6. **No review gating, no incentives.** Ask every segment, not only happy users. Offering rewards for reviews, or filtering out unhappy users before sending the link, risks violating Slack's listing policy and consumer-review rules. Verify Slack's current policy before send. A real 4.3 beats a removed listing.

## 2. Owners (proposed roles)

| Role | Owns |
|---|---|
| **You (exec sponsor)** | Go/no-go on gates, weekly review, unblocking Slack contacts |
| **Head of Growth (plan owner)** | Test design, copy variants, decision rule, weekly dashboard narrative |
| **Growth marketer / copywriter** | Variant A and B copy, email sequence, Marketplace edits |
| **Lifecycle/CRM owner** (may be the marketer) | Segments, sends, suppression lists, email metrics |
| **Engineer (about 2 days total)** | Install logging, `/review` redirect, in-app review prompt, activation event |
| **Analyst, or Growth if none** | Dashboard, weekly data export, reconciliation |
| **Support/CS lead** | Seeding the first reviews personally, flagging unhappy accounts before sends, reply handling |

## 3. Timeline

**Phase 0: setup, Oct 8 to Oct 16** (about 5 working days)

1. Growth: pull baseline views and installs (see next action). Run the power check. Oct 9.
2. Growth: confirm with Slack whether listing edits need re-approval and how long that takes. This decides the test design. Oct 9.
3. Growth: confirm Slack's review policy and any rating-display threshold. The "40" is your assumption, so verify it. Oct 9.
4. Eng: ship install logging, `/review` redirect, and the activation event (section 5). Oct 9 to Oct 15.
5. Growth: write Variant B (A is the current listing). Change one thing: the positioning angle, not a full rewrite. Oct 14.
6. You and Growth: sign the decision rule below. Oct 16. **Gate:** no test starts without it.

**Phase 1: listing test, Oct 19 to Nov 29** (6 weeks, one-week blocks)

| Week | Starts | Version |
|---|---|---|
| 1 | Oct 19 | A |
| 2 | Oct 26 | B |
| 3 | Nov 2 | B |
| 4 | Nov 9 | A |
| 5 | Nov 16 | A |
| 6 | Nov 23 | B (Thanksgiving week) |

- The A, B, B, A, A, B order cancels time trends. If Slack re-approval takes more than 2 days per edit, fall back to two 3-week blocks (A, then B) and treat the result as directional only.
- **Decision rule, signed in advance:**
  - B wins if its view-to-install conversion beats A's by the pre-agreed minimum lift, the 95% interval excludes zero, and 7-day activation doesn't drop more than 5 points.
  - If the interval includes zero, keep the version with better activation. Report "no detectable difference" without spin.
  - No peeking at the winner before Nov 30. Guardrails (uninstalls, complaints) can stop the test early.
- Readout: Mon Nov 30.

**Phase 2: review campaign, Oct 19 to Dec 11** (parallel)

| Date | Action |
|---|---|
| Oct 19 to 23 | CS personally asks 15 to 20 happy, long-standing customers. No incentive. |
| Oct 27 | Wave 1: highest-engagement workspaces, email plus in-app prompt |
| Nov 3 | Reminder to wave 1 non-clickers (max 2 touches per person) |
| Nov 10 | Wave 2: next engagement tier |
| Nov 17 | Wave 3: remaining eligible workspaces |
| Nov 24 to 30 | Send freeze (Thanksgiving) |
| Dec 1 | Top-up wave to close the gap to target |
| Dec 8 | Final reminder to non-reviewers |
| Dec 11 | Stop sending. Dec 11 to 18 is the buffer for moderation lag and late reviews. |

## 4. Review-campaign design

- **Audience:** the 900 active workspaces, but ask individual standup participants (about 2 to 3 per workspace), not only the admin who installed. Admins are fewer and busier.
- **Best channel:** a bot DM right after a successful retro or streak milestone, when satisfaction is highest. Email backs it up. Check the email consent basis for EU recipients.
- **Suppress:** open support tickets, workspaces that churned in the last 30 days, and anyone who already reviewed.
- **Ask structure:** one email, one link (`/review`), one sentence on why reviews matter to a small team. Don't promise anything in return.
- **Funnel math to track per wave:** recipients → delivered → opened → clicked → review page reached → review posted. A review needs about 4.5% of workspaces. If wave 1 yields under 1% of recipients, widen to participants and add the in-app prompt before wave 2.

**Glide path for the mid case (25 reviews)**

| Date | Cumulative reviews |
|---|---|
| Nov 6 | 8 |
| Nov 20 | 16 |
| Dec 4 | 22 |
| Dec 11 | 25 |

Stretch case is 40. If wave 1 is on the low path (under 5 reviews by Nov 6), the Nov 10 review triggers the action below.

## 5. Measurement setup

**Sources of truth**

| Metric | Source | Note |
|---|---|---|
| Listing views, installs | Slack Marketplace dashboard, exported weekly | Views exist only on Slack's side. Verify what the dashboard exposes. |
| Installs (ground truth) | Your OAuth callback log | Reconcile weekly with Slack's count. Investigate gaps over 5%. |
| 7-day activation | App event log | Define as first standup or retro completed within 7 days of install. |
| Review clicks | `/review` redirect log | Subtract from Slack views for the adjusted conversion rate. |
| Email funnel | Email platform | Sends, opens, clicks, unsubscribes |
| Review count and rating | Weekly manual check of the listing | Record in the same sheet, every Monday |

**Events to log** (object-action naming)

- `install_completed` (workspace_id, timestamp, listing_variant)
- `first_standup_completed` (workspace_id, days_since_install)
- `review_link_clicked` (workspace_id, user_id, wave, channel)
- `review_prompt_shown` (in-app)

`listing_variant` is set from the edit log you keep for each listing change, with timestamps, so each install maps to the version live at that moment.

**Weekly dashboard** (one page, same layout every week)

1. Views, installs, conversion by variant, plus adjusted conversion (views minus review clicks)
2. 7-day activation by variant
3. Reviews: cumulative vs glide path, current star average
4. Email funnel per wave
5. Guardrails: uninstalls, unsubscribe rate, support complaints about the campaign
6. Data-quality line: Slack vs OAuth reconciliation gap

**Weekly review (you and Head of Growth, 30 min, Mondays):** the dashboard's first line states one thing: on track, at risk, or off track against the glide path. Then the agenda is the one decision needed this week, not a metric tour.

## 6. Gates and risks

| Gate / risk | Date | If it fails |
|---|---|---|
| Baseline views under ~500/week | Oct 16 | Downgrade the test to a copy refresh with guardrails |
| Slack edits need long re-approval | Oct 16 | Fall back to two 3-week blocks |
| Wave 1 under 1% review yield | Nov 10 | Expand to all participants, add in-app prompt, reset the target to mid case |
| Reviews below the low path (under 8 by Nov 20) | Nov 20 | Escalate: CS personal asks, founder-signed email |
| Low early ratings | Any | Don't suppress. Fix the product complaint, reply publicly to reviews. |
| Slack policy conflict | Oct 9 | Remove the offending step before any send |

## 7. Questions only you can answer

1. What are current weekly views, installs, and the review count today?
2. Does Slack apply a minimum review count before showing the star rating? Where does "40" come from?
3. Who fills each owner role, and is an engineer actually available for 2 days by Oct 15?

**Next:** send me the 8-week baseline (views, installs, current review count) and I'll run the power check and set the real minimum-lift threshold for the decision rule.