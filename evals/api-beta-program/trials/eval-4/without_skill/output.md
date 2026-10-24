Verdict: don't send the proposal as written. Two of the four pieces are wrong, one is half right, and one gap sits underneath all of them.

**First action this week:** write down the exit criteria. Send Ridgeway Fleet a written note. Do both before you talk to leadership.

## 1. "Extend 6 months because we're close"

❌ "Close" has no definition. Nobody wrote down what done looks like, so nobody can measure the distance.

- Leadership will ask "close to what?" and you have no answer.
- You can't tell whether 6 more months fixes the problem or repeats the first 5.
- Deciding the criteria at the review lets the data pick the criteria. That is motivated reasoning, and it is how previews drift on forever.

**Fix:** write the exit criteria now, before the review. Four weeks is enough. Example gates (tune the numbers to your data):
- Reliability: p95 latency and error rate under X over a 30-day window.
- Accuracy: match quality above X on a labeled route set.
- Usage: N accounts making sustained production calls, not just signing up.
- Operations: on-call runbook, rate limits, and an SLA draft exist.
- Commercial: pricing decided, plus at least 1 account willing to pay or sign.

Then pick one outcome:
- **Ship to GA** if the gates pass.
- **Extend a shorter, gated period** if some gates fail. 3 months, with named fixes, beats 6 open-ended. Make it re-reviewable at the halfway point.
- **Stop or pivot** if usage or accuracy gates can't be reached.

Keep "extend" as an option. Drop "because we're close" until the criteria define close.

## 2. "Auto-expire every beta flag on the new end date"

⚠️ Half right. Expiry dates are good hygiene. But a single date applied to all accounts has two problems.

- **Ridgeway runs production traffic.** On the end date their calls get cut off. They have nothing in writing, so you have no notice period and no promised behavior. That is a self-inflicted outage for your heaviest user.
- **Auto-expire plus no GA decision = silent breakage.** If the review slips, or GA isn't ready on that date, everything turns off by itself.

**Fix:**
- Set expiry per account, with notice. Warn accounts at 30 and 7 days.
- Make the expiry action explicit: downgrade to read-only, move to GA, or require renewal. It should not be a hard cut.
- Exempt or special-case Ridgeway until their agreement exists.
- Keep "nothing lingers" as a goal. The mechanism needs an owner and a decision path, not a timer.

## 3. "12 signups = demand validation"

❌ Signups measure interest. They don't measure demand.

- 3 of 12 made real calls. That is **25% activation**.
- 9 accounts enrolled and never used it. Treat that as a finding, not a footnote. Find out why: friction, wrong fit, no integration time, or no real need.
- Of the 3 active accounts, 1 is Ridgeway. Your real validated demand may be **1 account**, and Ridgeway has no commitment.

**Fix:** show the funnel: 12 enrolled, 3 active, 1 sustained production. Then add what you learn from Ridgeway (volume, use case, what they'd pay). A smaller true number with a clear story survives scrutiny. An inflated one gets picked apart in the room.

Also call the 9 inactive accounts before the review. Even 3 or 4 conversations will tell you more than the signup count.

## 4. Renaming `matches` to `segments` the week before the review

❌ Don't. It is a breaking change to a response field, so it breaks Ridgeway's production integration.

- A rename in the final week means the review judges a shape that has had zero days of real use.
- It adds a regression risk right when you need stable data for the gates.
- It shows the response contract is still moving, which weakens any "ready for GA" argument.

**Fix options, best first:**
1. **Ship the rename now, additively.** Return both `matches` and `segments` for a deprecation window. Ridgeway migrates on their schedule. Review the final shape with real traffic on it.
2. **Do the rename at GA**, under a version bump, with a migration note. If you know `segments` is the final name, this is the cleanest path.
3. If it must land the week before the review, tell Ridgeway first, in writing, with a date.

Pick 1 or 2. Having both fields live before the review gives you evidence that the new shape works.

## The underlying gap: Ridgeway

🟠 This is the biggest risk. A production user with no written terms means:
- No SLA, no notice period, no data-use terms, no support commitment.
- A shape change, outage, or shutdown hits a customer who never agreed to any of it.
- You may be running de facto GA for them while calling it a preview.

**Fix:** within 1 to 2 weeks, send them a short written note. Cover:
- Preview status and the end date.
- No uptime guarantee yet, plus what support they get.
- Notice you'll give before breaking changes (suggest 30 days).
- What happens at the review: GA, extension, or transition.
- Ask what they need from you to commit, and whether they'd sign a design-partner or paid-pilot agreement.

Don't give them a verbal "don't worry about it." Get it in writing.

## Revised proposal for leadership

1. **Decision:** run the exit review against written criteria (attach the list from section 1).
2. **Outcome options:** GA, a gated 3-month extension, or stop. Recommend one based on the data.
3. **Demand:** present the funnel (12, 3, 1), the Ridgeway story, and what you learned from inactive accounts.
4. **Flags:** per-account expiry with notice and an explicit end-state action. Ridgeway handled under their own agreement.
5. **API change:** `segments` added alongside `matches` now. `matches` deprecated with a dated sunset.

## Plan for the next 4 weeks

1. **This week (about 2 hours):** draft exit criteria and get your lead to agree to them.
2. **This week (about 1 hour):** write and send the Ridgeway note.
3. **Week 2:** call the 9 inactive accounts. Aim for 4 conversations of 15 minutes each.
4. **Week 2:** engineering ships `segments` additively, with `matches` still returned.
5. **Week 3:** pull the data against each gate. Draft the recommendation.
6. **Week 4:** hold the review.

One open question changes my advice: what's the plan for pricing and GA readiness (SLA, on-call, rate limits)? If those don't exist yet, a gated extension is more likely the right call than GA, and the criteria should include them.

**Next:** open a doc and write the five exit gates with a number next to each. If you paste them here, I'll sharpen them.