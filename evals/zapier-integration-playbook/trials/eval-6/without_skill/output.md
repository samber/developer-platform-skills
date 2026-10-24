**Do this first: don't announce the 1.2.0 deprecation on Monday (2026-10-26).** The three goals depend on each other, so the order matters.

**Not verified.** Web access was denied in this session, so I couldn't check any of these against Zapier's docs. Confirm each with your Zapier partner contact or the developer docs before you rely on it.
- The "delist above 5% error rate" rule
- Gold tier at 500 active users
- The deprecation notice window and the migrate command

## Premises to correct

1. **(a) You are not near the 5% line.** 3.2% is already under it. The real goal is under 2% for quality and tier eligibility. The 5% rule is unconfirmed.
2. **(b) 500 users in one quarter is probably out of reach.**
   - 180 users took about 7 months (March to October), roughly 26 per month.
   - 500 by end of Q1 needs about 107 per month, around 4x the current pace.
   - "Active user" may be counted differently by Zapier than by you.
3. **(c) "Strictly better" is an assumption, not a fact.** Check it with a diff and with data (step 3 below).
   - Real Zaps may depend on field keys, output shape, or dedupe IDs that 1.3.0 changed.
   - Part of your 3.2% error rate may come from 1.3.0 itself.
   - A 7-day notice is almost certainly shorter than Zapier's minimum for versions that still have users. Verify.

## Plan

### Phase 0: measure (this week, about 1 day)

1. Pull run errors from the last 90 days, grouped by version, step, error class, and user. Run errors in the Zapier dashboard include problems you didn't cause (expired auth, bad user input, rate limits), so split "ours" from "theirs".
2. Count users still on 1.2.0 versus 1.3.0.
3. Map the 14 open bugs to the ~25 affected users and to error classes. You will probably find that a few bugs cause most of the errors.
4. Get your Kestrelbase customer count and the share who have connected Zapier. That is your real addressable base.

**Exit check:** you know the share of errors that are ours, the 1.2.0 user count, and which bugs matter.

### Phase 1: errors under 2% (weeks 1 to 4)

1. Triage all 14 bugs in week 1. Fix the ones linked to the highest error volume first. Reply to the reporters, because 3 months of silence is itself a risk.
2. Fix the top 3 error classes that are ours. Typical causes are poll or subscribe failures, auth refresh, and pagination.
3. Add a weekly review of the error rate and a new-bug SLA (triage within 5 business days).
4. Add an alert at 3% and a hard escalation at 4%.
5. Target: under 2% on a rolling 30 days, measured on your own errors if the split in Phase 0 shows many are user-caused. Also confirm how Zapier itself measures the rate.

### Phase 1b: the 'Updated Task' trigger (weeks 1 to 3, in parallel)

An 11% activation rate against 55 to 65% for the other steps points to a defect or a setup problem, not demand. Test these in order:
1. Does the trigger actually fire? Check polling versus webhook, the dedupe key, and whether updates produce a new ID.
2. Does the sample data match real payloads?
3. Is the label or description confusing next to 'New Task'?

Compare its failures against the open bugs, since it may be one of them. Fixing this likely lifts activation (and the quarter's user numbers) more than any marketing push.

### Phase 2: the path to 500 (weeks 4 to 13)

1. Confirm the tier criteria and the definition of "active" in writing with Zapier. Check whether error rate, support responsiveness, or other conditions also apply. Phase 1 may be a prerequisite.
2. Get your funnel numbers: customers, connected, activated (Zap running), retained.
3. Run the levers once the integration is clean. Do this after Phase 1, not before, because you don't want to send new users into a 3.2% error rate.
   - Zap templates for the top 5 workflows
   - In-app prompts to Kestrelbase customers who haven't connected Zapier
   - A lifecycle email for customers who connected but never activated
   - A Zapier co-marketing slot, if the partner program offers one
4. Re-forecast at week 6 with real conversion data. If the forecast shows about 300, say so and set Gold as a Q+1 goal. The plan is "meet criteria", not "hit a date".

### Phase 3: retire 1.2.0 (start planning now, execute only when ready)

1. Diff 1.2.0 against 1.3.0 for field keys, output, auth, and dedupe. Classify each change as breaking or non-breaking.
2. Check Zapier's rules (unverified): notice window, whether you can migrate users, and whether deprecation is allowed while Zaps still run on 1.2.0.
3. If the diff shows no breaking changes, migrate users in stages (a small percentage first), watching errors for each step. Zapier's CLI has a migrate command for this; confirm its exact name and limits.
4. If it shows breaking changes, publish a short migration note per change: who is affected, the exact error text, before and after, and what to do.
5. Announce the deprecation only after Phase 1 shows 1.3.0 is stable. Use Zapier's minimum window or longer. Email the named users still on 1.2.0.
6. Track the number of users on 1.2.0 weekly. Expect a long tail and handle the last accounts directly. Deprecate only when that number is zero or the stragglers have been contacted.

## Targets

| Metric | Now | Q-end target |
|---|---|---|
| Error rate (ours) | 3.2% | under 2% |
| Open bugs untouched | 14 | 0 |
| 'Updated Task' activation | 11% | 40% or more (stretch 55%) |
| Users on 1.2.0 | unknown | 0 |
| Active users | 180 | set after Phase 2 step 4 |

## Decisions I need from you

1. Who owns this integration weekly (name and hours)?
2. Can you export the error logs by version, user, and step?
3. Is Gold a hard goal for next quarter, or is "eligible by Q+1" acceptable?

**Next action (about 20 minutes):** export the last 90 days of run errors from the Zapier developer dashboard and count users on 1.2.0. Paste both here and I'll build the error breakdown and the migration timeline.