**Verdict: three of the four parts of the plan fail as written. Fix the order and the targets, then run a smaller version.**

Next action (10 min): run the Data Explorer query at the bottom for `[oakhollow]`. Sort by views. The result decides how much of this plan is worth doing at all.

## Direct answers

**1. Priya closes all 80 as duplicates over one weekend. No.**
- 3,100 rep gives her one close vote, not a closure. Only a gold tag badge (1,000 tag score and 200 answers in `[oakhollow]`) lets one person close a duplicate alone. Check the live privileges page, because thresholds move.
- Colleagues cannot supply the other votes. Coordinated votes are reversed, and every account involved can be suspended.
- Her options: flag, use her one close vote, or get the badge. The rest of the votes must come from independent community members. A weekend burst of 80 flags will also hit the daily flag and vote caps.
- About 40 of the 80 are on the sunset v1 SDK. A v2 canonical does not answer them, and a wrong duplicate target gets reopened. Those need a separate v1-to-v2 migration answer as their target.
- "Slightly different wording" is not proof of one root cause. Webhook signature mismatch usually has several causes (assumed here, so verify). Cluster by cause first, with one canonical per cluster.
- Ignore the near-zero-view tail. Closing threads nobody reads does not help.

**2. Edit each question to add a pointer line. No.**
- The site posts the duplicate link itself, so a pointer adds nothing.
- Editing other authors' questions to add your own line is the "hands off others' work" pattern. A rewrite that changes intent gets rolled back.
- Every edit bumps the thread to the Active tab, so 80 edits means 80 bumps.
- Any pointer to Oakhollow must carry the disclosure line in the post itself.
- Instead, add one comment only where the fix is version-specific (template below). Batch these weekly.

**3. $2,000 on 100-200 rep bounties for the 15 hardest questions. No.**
- A bounty is paid in the poster's own reputation, not cash. The $2,000 cannot buy rep.
- 15 bounties at 100-200 rep cost 1,500-3,000 rep. Priya has 3,100, so this would drop her below the 3,000 close-vote gate.
- Bounty ranks last in value per hour. It is one-shot, and it bumps the thread.
- "Hardest" is not "most viewed". Bounty only a hard question that also has high views.
- Colleagues never bounty each other's posts.
- Spend the money on staff hours for canonicals and the migration answer, which compound. I did not find a policy source on paying outsiders for answers, so treat paying for answers as unverified and do not do it.
- If you still want a bounty, put one on at most 2-3 threads and keep the cost well under Priya's margin above 3,000. Or use a different staff account with spare rep. That account must be a real person's single account.

**4. Start an Oakhollow Collective. No.**
- Join a Collective only if your technology already has one. The playbook gives no path for a vendor to start one.
- Check with Stack Overflow if you want it. I could not confirm self-service creation from the playbook.
- With about 80 questions in the tag, a Collective is far out of proportion. The "own space" you want is the tag excerpt and wiki, which cost almost nothing.

## Posture

**Curate** (default). Predicate: new questions still arrive monthly and the goal is citation or deflection. Flip to **Maintain** (under ~2 h/week) if fewer than a few new questions a month. Flip to **Exit** if almost none arrive. With a sunset v1 and only 80 questions, Maintain is a likely fit. The query below gives the number.

## Ranked actions

| # | Action | Owner | Hours | Rep gate |
|---|---|---|---|---|
| 1 | Run the query, cluster the top-viewed ~25 questions by root cause | Priya | 2 | none |
| 2 | Tag excerpt and wiki: routing, canonical links | Priya | 1 | any, peer-reviewed |
| 3 | Self-answered canonical per verified cause, 2-4 of them | Priya or another engineer, written by hand, no AI | 2-3 each | 15 |
| 4 | One v1-to-v2 migration answer as duplicate target for v1 questions | same | 3 | 15 |
| 5 | Duplicate flags on top-viewed matches only | Priya | 2 | 15 flag, 3,000 vote |
| 6 | One edit batch per week, version-specific comments | Priya | 1/week | none |
| 7 | New-question rotation, 15 min/day | one assignee per question | 1.5/week | 1 |
| 8 | Optional: 2-3 bounties | someone with spare rep | 1 | 75 |

Badge path: the combination of 200 tag answers and 1,000 tag score takes months. Only worth it if most of the backlog is repeats, and the canonical flags above build toward it.

All posts: staff write them by hand. No generative AI, even for drafting. Debug with AI privately, write the post yourself.

## Backlog clusters (assumed, verify against the real threads)

| Cluster | Canonical | Notes |
|---|---|---|
| A. Body parsed before verification (JSON middleware mutates payload) | assumed, v2 | likely the biggest |
| B. Wrong or stale endpoint secret | assumed, v2 | |
| C. Timestamp tolerance and clock skew | assumed, v2 | |
| D. v1 SDK signature scheme | migration answer | duplicate target for all v1 threads |
| E. Not a signature problem | none | redirect, do not close as duplicate |

## Routing table (tag excerpt and wiki)

| Problem | Route |
|---|---|
| How-to, error string | Stack Overflow `[oakhollow]` |
| Bug | public issue tracker (`<URL>`) |
| Feature request | `<URL>` |
| Account, billing, private data | `<support URL>` |

## Templates

Fill every `<...>`. Technical bodies are for staff.

Canonical question:

```
Title: oakhollow-node fails with "<literal error string>" when <condition>

I run <code> with oakhollow-node <version> on <environment>.
It fails with:
    <full error output>
Expected: <what should happen>.
What I tried: <one or two things that do not work>.
Disclosure: I work at Oakhollow, which maintains oakhollow-node; I'm posting this Q&A to document a common fix.
```

Canonical answer:

```
Cause: <one sentence>.
Fix:
    <code or config>
Verify: <command and expected output>.
Applies to versions <range>; for v1, see <migration answer link>.
Disclosure: I work at Oakhollow, which maintains oakhollow-node.
```

Version-specific comment on a duplicate:

```
The <version> fix is in the second code block of the linked answer. (I work at Oakhollow.)
```

Tag excerpt:

```
Oakhollow is a payments API. Use for questions about using oakhollow-node and the Oakhollow API. For bugs, feature requests or account issues, use Oakhollow's own channels.
```

Tag wiki:

```
## About
<Two-sentence neutral description, current major version. v1 is end of life.>
## Before asking
Include oakhollow-node and Node versions and full error output. Common problems: <canonical links>.
## Where else to ask
Bugs: <issue URL>. Feature requests: <URL>. Account and billing: <support URL>.
```

## Metrics

Targets are self-set; Stack Overflow publishes no vendor-tag benchmark.

- Answer rate under 30 days: start at 90%. Median time to first answer: one business day.
- Canonical coverage of your top 20 ticket themes. Views on canonicals.
- Hygiene, pass threshold zero: spam flags, AI deletions, undisclosed-affiliation comments, rejected edits.

Baseline query (data.stackexchange.com, refreshed weekly; enter `oakhollow` as TagName):

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

For the answer-rate metric, add `AND q.CreationDate > DATEADD(day, -30, GETDATE())` and compare with all open questions in the tag over the same window, keeping the same `ClosedDate IS NULL` filter on both sides.

## Open questions

- How many new `[oakhollow]` questions arrive per month? This picks Curate, Maintain or Exit.
- Do Priya's tag score and answer count come anywhere near the gold badge?
- Is the goal deflecting support, being cited in search and AI answers, or winding down v1? A citation goal promotes canonicals. A deflection goal promotes the rotation.
- How many hours per week, and by what date must a result show?