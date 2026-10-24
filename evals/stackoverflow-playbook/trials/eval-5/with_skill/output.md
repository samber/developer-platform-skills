**Start here (10 min):** open data.stackexchange.com, paste the backlog query from the Data Explorer section below, and set `TagName` to `vexalith`. Save the row count and the top 10 rows by views. That is your baseline, and it tells you which threads to answer first.

## Direct answers to your plan

| Your plan | Verdict | Why |
| --- | --- | --- |
| Close the billing and bug questions so the tag looks clean | ❌ Can't, and shouldn't | Close votes need 3,000 rep. Flags need 15. You have 1, Dario has 640, so neither of you can close alone. A closed question can't take new answers, so it loses the workaround that ranks. Billing posts get a redirect and a flag. Bug posts get a workaround. |
| Answer the Flagbeam vs Vexalith vs Togglewright question | ❌ Skip | "Which tool should I pick" is off-topic on Stack Overflow. A vendor answer reads as promotion and invites flags, and the thread is a hazard for your account. |
| Reply to the Portuguese posts in English | ❌ No | pt.stackoverflow.com is a separate site with its own reputation, and answers there go in Portuguese. |
| See new questions the same day | ✅ Yes | Use the tag RSS feed (setup below). |

- **Clean tag is the wrong goal.** The archive ranks in search and AI retrieval. Own the high-view threads instead.
- **Dario cannot lend you his account.** One person, one account. He answers as himself and discloses every time. You two never vote on, accept or bounty each other's posts.
- **No AI drafting.** The ban covers content written "in part or in whole" by an LLM. Debug with AI privately and write every post yourself. That includes the Portuguese ones.

## Posture: Curate (default)

- **Curate** applies while new questions still arrive monthly. 96 open questions suggest they do. Your 4 hours a week is above the 2-hour Maintain ceiling.
- **Check it:** rerun the query with `AND q.CreationDate > DATEADD(day, -90, GETDATE())`. About 1 or more per month means Curate holds. Near zero means switch to Exit: tag excerpt points to your channels, update the top-viewed answers once, stop.
- **Goal assumed:** deflect support and get cited in search and AI answers. Say so if it is wind-down instead.

## Ranked actions

| # | Action | Owner | Hours | Rep gate |
|---|---|---|---|---|
| 1 | Tag excerpt and wiki: routing plus canonical links | You draft, peer-reviewed | 0.5 | any |
| 2 | Answers on high-view threads with outdated or no answers | You | 2 | 1 |
| 3 | Redirect comments and billing flags | Dario | 0.5 | 50 to comment, 15 to flag |
| 4 | Self-answered canonical per recurring theme (first: Django + vexa-py) | You, from week 2 | 1 | 15 |
| 5 | Duplicate flags onto canonicals | Dario | 0.25 | 15 to flag |
| Later | New-question rotation, Staging Ground review, bounty | Alternate days | 0.5 | bounty needs 75 |

- **Your rep path:** answers earn +10 per upvote, so item 2 gets you to 15. Items 4 and 5 unlock after that.
- **Edits:** neither of you reviews the other's tag-wiki edit.
- **Bounty:** it comes out of your own rep, so skip it for months.
- **Gold tag badge:** only 1,000 tag score plus 200 answers lets you close duplicates alone. Promote it if most of the backlog turns out to be repeats.

## Week 1, your 4 hours

1. **0:30** Run the query and record the baseline. Cluster the top 10 by views.
2. **0:30** Draft the tag excerpt and wiki. Get the GitHub issue URLs for vexa-js and vexa-py and the support URL from your team first.
3. **0:15** Set up the feed: `https://stackoverflow.com/feeds/tag/vexalith` goes into your team chat. Add the pt.stackoverflow.com feed for its tag (URL pattern assumed, verify it works).
4. **0:30** Rotation share. You and Dario alternate days, one assignee per question, 15 min each. Acknowledge the same day and answer within 48 h. Don't promise a same-day answer.
5. **2:00** Answer 3 to 5 of the highest-view threads. Each answer must show a working solution with the tested version and carry the disclosure line.
6. **0:15** Friday: write down the numbers (open count, answers posted, rep).

## Backlog clusters

Counts are assumed from your description. Canonical titles come after triage, quoting the literal error string.

| Cluster | Count | Handling |
|---|---|---|
| "Is this a bug?" with stack traces | about 32 | Group by root cause, SDK and version. One canonical per cause, flag the rest as duplicates. Post a workaround plus a disclosed link to the public issue. |
| Billing, e.g. "charged twice for seats" | several | Dario comments the support route and flags as not about programming. Tell your support team these customers are waiting. |
| Tool comparison | 1 | Leave alone. Later, write the real win: a Django + vexa-py how-to canonical. |
| Portuguese, on pt.stackoverflow.com | 3 | See next section. |
| Usage and how-to | about 60 | Sort by views, ignore the near-zero tail. Old-version threads get one migration answer as the duplicate target. |

## Portuguese posts

1. Find a Portuguese-speaking human colleague, or a community member you trust, with their own account on pt.stackoverflow.com. They answer in Portuguese and disclose.
2. No one available: leave the three posts unanswered. An English reply or an LLM translation is worse.
3. Check the pt site's help center on translation tools. I couldn't verify its policy here.
4. Reputation doesn't carry over. Once you pass 200 rep on Stack Overflow, you get +100 on the other sites.

## Routing table (put it in the tag excerpt and on your support page)

| Question type | Where it goes |
|---|---|
| How-to, error messages | Stack Overflow |
| Bugs | `<GitHub issue URL per SDK>` |
| Feature requests | `<URL>` |
| "Why" and "when" questions | Your own channels |
| Billing, account, private data | `<support URL>` |
| "Which tool should I choose" | Not Stack Overflow |
| Portuguese | pt.stackoverflow.com, in Portuguese |

## Templates

Staff write the technical bodies. Every post gets the disclosure line.

**Disclosure (in every post):**
```
Disclosure: I work at Vexalith, which maintains vexa-js and vexa-py.
```

**Bug redirect (Dario, 50+ rep):**
```
Thanks, this looks like a bug rather than a usage question. Please file it at <public issue URL> with the output above; I've posted the workaround below. (I work at Vexalith.)
```

**Billing redirect (Dario):**
```
This needs access to your account, which nobody here has. Please contact <support route>. Flagging to close as not about programming. (I work at Vexalith.)
```

**Tag excerpt:**
```
Vexalith is <one-line neutral definition>. Use for questions about using Vexalith's vexa-js and vexa-py SDKs. For bugs, feature requests or account issues, use Vexalith's own channels.
```

**Tag wiki:**
```
## About
<Two-sentence neutral description, current major version.>
## Before asking
Include Vexalith, language and SDK versions and full error output. Common problems: <canonical links>.
## Where else to ask
Bugs: <issue URL>. Feature requests: <URL>. Account and billing: <support URL>.
```

**Canonical Q&A:** use the skill's template (`references/templates.md`).
- **Question title:** `<tool> fails with "<literal error string>" when <condition>`. The question carries a disclosure line too.
- **Answer:** Cause, Fix, Verify, versions it applies to, disclosure.

**Data Explorer query (open questions with no upvoted or accepted answer, by views):**
```sql
SELECT q.Id AS [Post Link], q.ViewCount, q.Score, q.CreationDate
FROM Posts q
JOIN PostTags pt ON pt.PostId = q.Id
JOIN Tags t ON t.Id = pt.TagId
WHERE t.TagName = ##TagName:string##
  AND q.PostTypeId = 1
  AND q.ClosedDate IS NULL
  AND q.AcceptedAnswerId IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM Posts a
    WHERE a.ParentId = q.Id AND a.PostTypeId = 2 AND a.Score > 0)
ORDER BY q.ViewCount DESC
```
The data refreshes weekly, so use the feed for same-day alerts.

## Measure

Targets are self-set. Stack Overflow publishes no vendor-tag benchmark.

- Answer rate under 30 days: start at 90%.
- Median time to first answer: one business day.
- Canonical coverage of your top 20 support-ticket themes, views on each canonical, and a monthly check of whether AI assistants cite them.
- Hygiene, pass threshold zero: spam flags, AI deletions, undisclosed-affiliation comments, rejected edits.

## Next action

Run the query now. Then paste the top 10 rows (post links and view counts) and I'll cluster them and name the first three canonicals.

Question for you: do you have the public GitHub issue URLs for vexa-js and vexa-py and a support URL? The excerpt and every redirect comment need them.