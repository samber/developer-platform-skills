# Quillbridge Stack Overflow backlog: revised 8-week plan

I changed four things in your Q1 plan before scheduling it. Three of them would likely get the account suspended or your answers removed, and the fourth makes the 8-week goal impossible.

## What I changed, and why

| Your plan | Problem | Replacement |
|---|---|---|
| One shared `QuillbridgeSupport` account | Stack Overflow's terms require one account per person. Shared accounts get suspended, and the answers are then often deleted. | Each of the 4 engineers answers from their own named account. |
| Answers drafted by the internal LLM | Stack Overflow's generative-AI policy bans posting AI-generated answers, and a human check doesn't change that. Moderators and the community remove them. Please re-read the current policy before Week 1. | The assistant only finds the right doc section and reproduces the issue. The engineer writes the answer and runs the code. |
| 25 colleagues upvote to push answers above stale ones | Soliciting votes is vote manipulation. The system detects clustered votes from related accounts and reverses them. It can also flag your answers and accounts. | Ask for no votes. Good answers earn votes from visitors, and accepted answers come from the asker. |
| The bio says "Quillbridge team", so disclosure is covered | Stack Overflow's self-promotion rules require affiliation disclosure in the post, not only in the profile. | Add a line to every answer: "Disclosure: I work for Quillbridge, the maker of this SDK." |
| Clear all 338, oldest first, in 8 weeks | The capacity doesn't exist (see below), and a 2019 answer rarely deflects a 2026 ticket. | Triage by traffic and ticket overlap. Answer the roughly 80–110 questions that matter. Close, flag or comment on the rest. |

**Capacity check.** 4 engineers × 3 h × 8 weeks = 96 hours. Spread over 338 questions, that is about 17 minutes each, including reproduction and review. A real answer to an SDK question takes 30–45 minutes. Expect roughly 100–130 answers in total, and fewer if you reserve time for new questions. Plan for that number.

**The goal is fewer tickets, not an empty list.** Many of the 338 are probably obsolete, duplicates, unclear or about old SDK versions. Answering them adds effort and no deflection.

## Week-by-week plan

### Week 1: Triage and setup (all 4 engineers, 12 h)

1. Pull all 338 unanswered questions with views, creation date, score, SDK version mentioned and linked duplicates. Use the Stack Exchange API or the Data Explorer.
2. Pull the last 6 months of support tickets and tag the top 10 themes (auth, batch size, schema drift and so on).
3. Sort each question into one bucket:
   - **A: Answer now.** More than 500 views, or it matches a top-10 ticket theme.
   - **B: Answer if time allows.** Low views, still valid.
   - **C: Close or comment.** Duplicate, obsolete SDK version, unclear or off-topic. Vote to close if you have the reputation. Otherwise flag it, or comment asking for a version or reproduction.
   - **D: Docs gap.** The honest answer is "the docs don't say". Log it for a docs fix.
4. Each engineer uses their own account and checks that it has the reputation needed for comments and close votes.
5. Write a one-page answer standard: disclosure line, minimal reproducible snippet, SDK version tested, link to the docs.
6. Record the baseline (see the metrics table).

**Done when:** a ranked list of Bucket A exists, with an owner for each question.

### Weeks 2–3: Bucket A, highest traffic first (12 h/week each)

- Each engineer takes about 6–8 questions per week, at 30–45 minutes per answer.
- Workflow: reproduce the issue on the current SDK, write the answer by hand, and have a second engineer review it before posting.
- Ship docs fixes for Bucket D in the same week. One doc page can replace many answers.
- Friday: 30-minute sync to compare answers posted against the quota and flag anything the community pushed back on.

**Target:** about 25–30 answers posted by the end of Week 3.

### Weeks 4–5: Rest of Bucket A, then Bucket B

- Same workflow and quota.
- Start the Bucket C cleanup: close votes, flags and clarifying comments. This takes about 10 minutes per question.
- Watch the early answers. If any were downvoted or flagged, read why and adjust the standard before posting more.

**Target:** cumulative 60–70 answers.

### Week 6: New-question watch and mid-point check

- Set up an alert on the `[quillbridge]` tag for new questions (the Stack Overflow tag RSS feed and a Slack channel is enough).
- Set a response target of 2 working days for new questions. Clearing the backlog without this lets it grow back.
- Mid-point review: compare ticket volume for the top-10 themes against the baseline. Move effort to the themes that still generate tickets.

### Week 7: Bucket B and the long tail

- Answer Bucket B questions that still apply. Leave the rest alone.
- Link the most useful Stack Overflow answers from the docs where the docs are thin.
- Check that every answer carries the disclosure line and a tested SDK version.

**Target:** cumulative 100–130 answers.

### Week 8: Measure, report, hand off

1. Re-run the metrics and compare to the Week 1 baseline.
2. Report to leadership with honest numbers: answers posted, questions closed or flagged, docs pages fixed, change in ticket volume for the matched themes.
3. Move to steady state: one engineer per week on rotation, about 2 hours, covering new questions only. The docs-gap list becomes a docs backlog.
4. Decide what stays in the unanswered list, and write down why (obsolete, unclear, not reproducible).

## Metrics

| Metric | Baseline (Week 1) | Week 8 target |
|---|---|---|
| Unanswered questions | 338 | Below 150, mostly Bucket C and obsolete |
| Unanswered with more than 500 views | Measure it | 0 |
| Answers posted by the team | 0 | 100–130 |
| Answers with a score of 0 or below, or flagged | n/a | Below 10% |
| Acceptance rate on answered questions | Measure it | Track it, no target until you have data |
| Support tickets in the top-10 themes (per week) | Measure it | Down 10–20%, optimistic, and only credible with a baseline |
| Median time to first answer on new questions | Measure it | Under 2 working days |

Don't promise the ticket reduction before you have the baseline. Stack Overflow views convert to avoided tickets at a rate you don't know yet, so report it as a trend.

## Risks

- **Reputation:** new accounts have little reputation and can't vote to close or comment freely. Have the engineers start by answering Bucket A questions, which earns reputation fast.
- **Community pushback:** vendor answers draw scrutiny. Answers that are specific, tested and disclosed are accepted. Short answers that mostly link to docs get downvoted.
- **Quality drift:** if the second-engineer review slips, wrong answers stay public for years. Keep the review step even if the quota drops.
- **Product signal:** if one question type keeps recurring, fix the SDK error message or the docs, not the answers.

## Decisions for you

1. Are the 4 engineers willing to answer under their own names? This is the biggest change to your plan.
2. Do you have ticket data with themes, so the baseline exists?
3. Should the internal assistant be limited to search and reproduction, as above? I'd say yes.