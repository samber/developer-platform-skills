**Do first, 10 minutes:** open the 11 question issues. Pick the 3 you can answer in under 5 minutes each and answer them now. Don't enable Discussions yet.

## Verdict on Discussions

Not now.

- You check notifications every two weeks. A Discussions tab nobody answers looks dead, and that's the opposite of your goal.
- Moving questions from Issues to Discussions doesn't shrink the queue. It splits it into two places you must watch with the same 2 hours.
- The 11 questions are a backlog problem. They're also a docs problem and an intake problem. Discussions fixes none of those.
- Revisit after the talk, using the trigger in week 5.

## Assumptions

- I haven't seen the repo. Everything below rests on what you told me.
- Budget is 2h a week, so 10h total.
- Real activity beats fake activity. Nothing here is "post something so the graph is green".

## Week 1 (2h): clear the questions

1. **15 min.** Run `gh issue list --state open --limit 200` and label the 11 `question`. Note the other open issues: count, oldest, and whether any are real bugs.
2. **90 min.** Answer each of the 11 in about 8 minutes. For each:
   - Write the answer.
   - Close it with a link to a doc, or to the fix in a docs PR.
   - End with "Closing as answered. Reopen if this doesn't solve it."
3. **15 min.** Group repeat questions. Any theme asked 2+ times becomes a FAQ section in the README or docs. Draft it now and finish it in week 3.

**Done when:** 0 question-issues open, and a list of FAQ topics exists.

## Week 2 (2h): stop new questions arriving

1. **45 min.** Add `.github/ISSUE_TEMPLATE/config.yml` with `blank_issues_enabled: false` and a contact link: "Usage question → README FAQ / docs". Add one bug form with required fields only: brambleq version, Rust version, minimal repro, expected vs actual.
2. **15 min.** Write a "Getting help" section in the README stating the promise: "I'm a solo maintainer. I respond within 14 days, best-effort." Set the promise to what you can keep, because you check every two weeks.
3. **15 min.** Enable private vulnerability reporting (repo Settings → Security) and add a short `SECURITY.md`.
4. **45 min.** Backfill the 3 empty release bodies. Use `git log <prev-tag>..<tag>` and read the diffs. One section per release: Breaking, Added, Fixed. Each entry says what the user now observes, in 1-2 sentences. Drop internal churn. Delete any number you can't back with a measurement. Release bodies stay editable, so this is safe.

**Done when:** the issue chooser shows the route-away link, the README states the 14-day promise, and 3 releases have real notes.

## Week 3 (2h): make the repo hold up under a stranger

1. **30 min.** On a clean machine or container, follow the README quickstart exactly. Fix whatever breaks. The talk audience will do this.
2. **30 min.** Check that CI is green and the badges are current. Run `cargo update` and `cargo audit`, and fix or note what you find.
3. **45 min.** Triage the non-question issues. Reply to each with a decision (will fix, won't fix, needs info) and add a label.
4. **15 min.** Finish the FAQ from week 1.

**Done when:** the quickstart works cold and every open issue has a human reply.

## Week 4 (2h): ship one release with real notes

1. **60 min.** Cut a release with the fixes from weeks 2-3. Use the same Breaking/Added/Fixed format. If anything breaks callers, list it first with who is affected and what to do. Check every line against the diff before publishing.
2. **30 min.** Label 3-5 issues `good first issue`. Each needs a real description and a file pointer. Skip it if you can't write them honestly.
3. **30 min.** Pin one issue titled "Roadmap / what's next", 5-10 lines. Add a link to the talk in the README once the schedule is public.

**Done when:** the latest release is under 2 weeks old and has a real body.

## Week 5 (2h): freeze and prepare for the spike

1. **30 min.** No refactors this week. Do a final pass: the latest release, README, and issue list all look current.
2. **45 min.** Write the post-talk policy now, while nothing is on fire. Pick the numbers:
   - If question or issue inflow exceeds N a week after the talk (say 10), enable Discussions as a **routing target** in the chooser.
   - Do that only if at least one person besides you can answer in it, or if you are willing to say "community-answered, no maintainer SLA".
   - Otherwise keep the README FAQ and close with a link.
3. **30 min.** Block a 2h slot on the calendar for the week after the talk to triage the inflow. Don't rely on notifications.
4. **15 min.** Skim your slides against the repo: every link works, every version number is current.

**Done when:** the post-talk rule is written down and the post-talk slot is on the calendar.

## Don't do these

- **No bot greeting or stale bot.** The first reply must be human. If you add a stale sweep later, restrict it to items waiting on the reporter, warn before closing, and run it dry first.
- **No churn commits to make activity look real.** The signals that matter are recent releases with real notes, answered issues, and a working quickstart.
- **Don't reorganize labels.** Keep `question`, `bug`, `enhancement`, `good first issue` and add nothing else.

## What I need from you

1. How many open issues in total (11 questions plus what)? If there are 30+ bugs, week 3 triage needs more time and something else shrinks.
2. Do you have a chat or forum already, such as Discord or Matrix? If yes, the chooser links there and we skip the Discussions question entirely.

**Next:** open the repo and answer the first 3 question-issues.