# Vessen partner program: fixing the install wall

I didn't run the skill's one-question-at-a-time interview, because you asked for a single complete answer. The recommendations below rest on assumptions, listed at the end with what would change if they're wrong.

## Diagnosis

Three partners hitting the same wall is a design defect, not a complaint to manage. It matches two failure modes in the skill's list:

- **Hidden post-launch walls.** The skill's own example is a review that needs ≥5 active installs before it starts, and a certification that needs 6 months listed plus 60 installs. Partners find these after they think they're done. Yours found out after three months of build.
- **Unmeasured funnel.** Your funnel stops at "submitted" and "approved". The stretch where an app is built but can't enter review has no checkpoint, so nobody saw partners pile up there.

There is also a structural problem. Review can't start until an app has 5 real-customer installs, and the badge can't start until 60. That only works if a partner can get real customers onto an app that hasn't been reviewed. If they can't, the wall is circular. This is the first thing to confirm.

HR data is high-sensitivity, so letting unreviewed apps onto real customer workspaces is a risk. That tension shapes the fix.

## What to change

### 1. This week: disclose and respond

1. Put every threshold where a partner reads it before building: signup page, program agreement summary, onboarding docs, and the submit screen. Use one page, "Path from first build to listed to Certified", with the exact numbers, what counts as a "real customer workspace", and who is excluded (the partner's own and affiliated workspaces).
2. Reply in the Slack thread. Acknowledge that the thresholds were not disclosed early enough, and say what changes and by when. Don't defend the gate in that reply.
3. Decide whether to offer the three affected partners a one-time review fast-track. This is a precedent and fairness call for you to make. I'd make it explicitly, with a stated reason, rather than quietly.

### 2. Next 30 days: give partners a legitimate route to the 5 installs

Pick one of these three, in this order of preference:

- **Pre-review unlisted install (preferred).** A partner gets a private install link for design-partner customers before review.
  - Gate it behind an automated baseline check: requested scopes, data-handling declaration, and the privacy and webhook requirements.
  - Show customer admins an explicit "not yet reviewed" warning and require an admin opt-in.
  - Add a partner dashboard counter: "3 of 5 installs toward review".
- **Move the wall.** If the 5 installs exist to prove demand or to protect reviewer time, review at submission and make installs gate public listing or featured placement instead. This is a bad fit for high-sensitivity HR data. Don't pick it unless the automated baseline in the first option is strong.
- **Lower the number.** This is the weakest fix, because it only moves the wall. Slack lowered its threshold from 10 to 5, so there is precedent, but it doesn't fix the circularity or the disclosure problem.

Before choosing, ask the team what the 5-install rule is protecting: reviewer capacity, spam, or demand evidence. If nobody can answer, the rule has no job and should be redesigned.

### 3. The "Vessen Certified" badge: keep it, but make the path visible

- Keep the 6-month and 60-install bar. Certification is a post-launch quality signal, not a gate on submission, and that's normal across the five ecosystems the skill studied.
- Publish the badge as a progress tracker in the partner dashboard: months listed and installs, with the current value of each.
- Add a non-gating, displayable credential, such as a "Vessen Verified Developer" course. This gives partners something buyer-facing during the 6 months before they can reach Certified, and it's the skill's "credentialed education loop" rung.
- Don't make that course a prerequisite for submission. Quality belongs at the review gate.

### 4. Instrument the part you couldn't see

Add checkpoints around the wall to the skill's four-checkpoint funnel:

1. Signup to sandbox provisioned.
2. Provisioned to first API call. Treat anything over ~10 minutes as a friction problem to fix first.
3. First API call to build complete.
4. **New:** build complete to 5 installs.
5. **New:** 5 installs to review started, then submission to approval.

Pull this from existing data now. Count partners stuck below 5 installs and how long they've been there. That tells you whether the three complaints are the tip or the whole iceberg.

Also track time-to-first-submitted-app. This metric is self-defined, so label it that way in reports. If it far exceeds review duration, the bottleneck is docs and enablement, not the review team.

### 5. Support for the hardest step

Getting the first 5 customer installs is a go-to-market problem, not a coding one. Add office hours or a short guide on finding design-partner customers, and a partner-customer matching list if you can staff one. Keep named partner managers for commercial ISVs only. Vessen's HR partners may include ISVs, which is one of the assumptions below.

## Order of work

| When | Action | Effort |
|---|---|---|
| This week | Disclosure page, in-flow notices, Slack reply, fast-track decision | Low |
| This week | Query the stuck-below-5 partner count | Low |
| Weeks 2-4 | Decide what the 5-install rule protects, then pick a route in section 2 | Medium |
| Weeks 2-6 | Dashboard progress counters, baseline automated check | Medium |
| Next quarter | Verified Developer credential, office hours | Medium |

## Assumptions to confirm

These stand in for the interview questions I couldn't ask:

1. **Can unreviewed apps be installed by customers today?** I assumed they can't, which is the circularity concern. If they already can via a private link, the main fix is disclosure and the dashboard counter.
2. **Is the data high-sensitivity?** I assumed yes, because the platform is HR. If it's lower, the move-the-wall option becomes viable.
3. **Who are the partners?** I assumed a mix of ISVs and small teams. If they're mostly ISVs, named partner managers could help break the install deadlock.
4. **Hard deadline or open-ended?** I assumed open-ended. A hard date would favor the cheap fixes (disclosure, lowering the number) and push the baseline check later.
5. **Effort ceiling.** The baseline automated check and dashboard counters need engineering time. If you have none, do section 1 and the data pull now, and defer the rest.

I haven't verified anything about Vessen's actual platform, install mechanics, or partner list. Everything above comes from the skill and its two reference files. The archetype figures change often, so re-check them against current platform pages before citing them to partners.