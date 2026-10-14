**Do not reuse the loop as is.** Next action, about 20 minutes: replace the system design prompt (URL shortener or Twitter) and cut the second coding round, using the plan below.

## Why the current loop fails

- **No API signal.** Nothing in it tests API design, versioning, backward compatibility or deprecation. That is the whole job.
- **Generic system design prompts are the wrong test.** The prompts are well known and rehearsed, and they are not your domain. They test scale-out, not contract design.
- **No Staff signal.** A senior loop tests whether the candidate can build. Staff needs scope, ambiguity, influence across teams, and the ability to say no. Two coding rounds add the least new information for this level.
- **Behavioral round is too generic.** "Tell me about a conflict" does not separate Senior from Staff.

## Proposed loop: 4 hours live

The recruiter call stays outside the budget. Each round has one interviewer.

1. **API design (60 min), replaces the URL shortener.**
   - Prompt: "Design the public send-message API for a CPaaS."
   - Probe each of these: idempotency keys, async delivery status and webhooks, multi-tenant rate limits, pagination, error model, auth.
   - Then add: "A top customer is on v1 and you need a breaking change. What do you do?"
   - Signals: contract-first thinking, customer empathy, knowing which decisions are one-way doors.
2. **API review critique (45 min).**
   - Hand the candidate a flawed spec, one page. Seed it with 5 or 6 flaws: a non-idempotent POST, offset pagination on a hot table, a leaky error model, an unversioned enum, a webhook with no retry or signature, and a naming inconsistency.
   - The candidate reads for 10 minutes, then critiques it.
   - Signals: taste, prioritization (which flaws matter most), and whether they can explain tradeoffs without being dogmatic.
3. **Coding (60 min), keep one round and make it API-shaped.**
   - Pick one task: implement an idempotency-key middleware, a token-bucket rate limiter, or webhook retry with backoff.
   - Signals: working code, edge cases (concurrent duplicates, clock skew, partial failure), and tests.
4. **Technical leadership deep dive (60 min), replaces the generic behavioral round.**
   - Anchor on one past project where they owned an external or shared interface.
   - Probe: how they drove adoption across teams they did not manage, a breaking change they shipped or blocked, a time they said no, and how they handled a customer escalation about the API.
   - Signals: scope beyond their own team, influence without authority, judgment under ambiguity.

Total: 4 × 60 = 4 hours live (3h45 if you trim the review to 45 minutes, as listed above). The remaining hour covers writing scorecards (about 10 minutes each) and one decision call.

⚠️ **Open question:** does your 5-hour cap count debrief time per person? If it does, a 4-person debrief takes about 2 person-hours and breaks the budget. Fix: written scorecards submitted before the debrief, and a 20-minute decision call with only the hiring manager and one other interviewer. If that is still too much, drop round 2 and fold three of its flaws into round 1.

## What the recruiter screen must check

Add three questions to the first call, so you do not spend interviewer hours on mismatches:

1. "Have you owned an API used by customers outside your company? Roughly how many consumers?"
2. "Have you shipped or retired a versioned API? What happened to the customers who did not migrate?"
3. "What was your scope at your last level: one team, several teams, or the whole org?"

Reject or hold if the answers are "internal only", "never versioned anything", and "one team".

## Interviewer staffing

- Rounds 1, 2 and 4 need someone who has operated a public API at scale, ideally Staff or above. Do not assign these to someone who has only built internal services.
- Give every interviewer a rubric with Senior, Staff and Principal-level examples. Without it, scores drift toward "good senior".

## Cost of the changes

- Writing the prompts, the flawed spec and the rubrics takes about 3 to 4 hours, once. After that the loop is reusable.
- The flawed spec in round 2 is the largest single item (about 1.5 hours).

**Next:** tell me whether the 5 hours include debrief time. Then I can lock the plan, and I can draft the flawed spec and the four rubrics.