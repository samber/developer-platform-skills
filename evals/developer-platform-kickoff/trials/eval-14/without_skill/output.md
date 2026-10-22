**Start with the 40% failure.** Don't start with "better error handling". Your boss has bundled three problems that need three different fixes. Pick the one that cost you most, which is the nine silent days.

**Next action (30 min):** Pull logs for the two failing partners. Find the first failing hour, the status codes, and the error cause. Then answer one question: did any metric or alert exist for per-partner failure rate? That answer sets your first deliverable.

## The three problems

| # | Symptom | Real problem | Fix type |
|---|---|---|---|
| 1 | 40% failures for 9 days, found by partner's customer | Detection. No per-partner alerting. | Monitoring |
| 2 | 50-min outage, customers learned from Twitter | Incident communication. No owned channel. | Process |
| 3 | "Got a 400, no idea why" | Error response design. The API doesn't explain itself. | API change plus docs |

Only #3 is "error handling" in the code sense. #1 and #2 are not code problems. Say this to your boss first. It stops the project becoming a vague refactor.

## Order of work

**1. Detection (week 1–2). Do this first.**
- Alert on per-partner error rate, not global. A 40% failure on 2 of 18 partners is invisible in global totals. That is likely why nobody noticed.
- Start simple: success rate per partner per 15 minutes. Page when it drops below a threshold for 30 minutes. Pick thresholds from each partner's normal traffic.
- Add a "silence" alert too. A partner whose calls drop to zero is also broken.
- With only 18 partners, a weekly health table is cheap. It lists calls, error rate, and top error per partner.
- Name an owner for each alert. An alert with no on-call owner would have missed those nine days too.
- Add a partner-facing step: when you spot a partner's failures, tell them before their customer does. Give the AE a one-line summary.

**2. Incident communication (week 2–3).**
- Stand up a status page. Hosted is fine, and it takes about a day.
- Give every one of the 18 partners a subscription path (email or webhook). Their own customers hear from them, not Twitter.
- Write a template and a rule: first public acknowledgement within a fixed time (e.g. 15 minutes of confirmed impact). Agree the number with your team. I'm proposing it, not citing a standard.
- Name an incident communicator, separate from the people fixing it.
- Do a short postmortem for the 50 minutes and send it to partners.

**3. Actionable 400s (weeks 3–6).**
- First, cluster the "got a 400" tickets. Group by the real cause, not by ticket. Expect a few causes to account for most tickets. Count before assuming.
- For each top cause, fix the response, not only the docs. A 400 should return a structured body with:
  - a stable machine-readable code
  - the offending field
  - what was expected
  - a link to the docs page
  - a request ID
- Then write one docs page per top code. Each page should have the exact message, the cause, numbered fix steps, and how to confirm it worked. This is a stopgap for any message the product should simply make clearer.
- Put the request ID in every error. Support can then find the call in seconds.
- Generate the error catalog and docs table from one source file, so code and docs can't drift.

## What to hand your boss

One page, three lines:

1. Detect: per-partner failure alerts, owned, by end of week 2.
2. Communicate: status page and partner subscriptions, by end of week 3.
3. Explain: structured errors and top-N docs pages, by week 6.

Success measures (set baselines now):
- Time from failure start to detection. Target: minutes, not days.
- Time from outage start to first public message.
- Count of "got a 400" tickets per month.
- Share of incidents where you contacted the partner first.

## Questions that change this plan

1. Did the two partners share a cause (same endpoint, same release, same auth path)? If yes, add a regression check to your release process.
2. Do you have request-level logs with a partner ID? If not, adding the ID is step zero.
3. Who is on call for partner-facing traffic today?
4. Are the 400s mostly validation errors, auth errors, or something else? The ticket cluster will tell you.

**Next:** run the 30-minute log pull and send me the first failing hour and status codes. I'll turn that into the alert spec.