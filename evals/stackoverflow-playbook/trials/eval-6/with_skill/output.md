# Brindlecore [brindledb] Stack Overflow quarterly slide

I could not run the query. Data Explorer needs a browser session, and the Stack Exchange API call from this shell needed approval I didn't push for. **I have no real numbers for [brindledb] and won't invent any.** Run the query below and fill in the slide.

## Direct answers to the three asks

**(a) Answer rate against an industry benchmark for vendor tags: there is none.** Stack Overflow publishes no vendor-tag benchmark, and I found no credible third-party one. Don't put "vs industry" on the slide. Use a self-set target (start at 90% answered within 30 days) and show your own quarter-over-quarter trend.

**(b) Total team reputation with a +5,000/quarter target: don't use it as the headline KPI.**
- Two engineers at about 1,800 rep each reaching +5,000 combined means near-daily upvotes. The only fast route is colleagues voting for each other. Serial votes between colleagues are reversed automatically, and coordinated voting can suspend every account involved.
- A reputation target also pushes the team toward easy answers on fresh questions. The metrics that help the business are canonicals and answers on high-view threads, and those earn little rep.
- Reputation is a gate, not a goal. Track it as a guardrail only (see "Reputation" below).

**(c) "Questions edited or cleaned up" as the activity metric: drop it.**
- At about 1,800 rep, both engineers are below the 2,000 threshold for unreviewed edits. Their edits go to peer review, and edits that change another author's intent are rejected.
- Never rewrite another author's solution. Post a new answer instead.
- Every edit bumps the thread to the Active tab, and Stack Overflow's ranking rewards fewer bulk edits. Batch any edits weekly.
- Counting edits rewards the behaviour the ranking penalises. Replace it with the activity metrics below.

## Posture

I assumed **Curate**, since new [brindledb] questions presumably still arrive monthly. Confirm with the tag's monthly new-question count from the query below. If it is near zero, switch to Exit.

## Query: quarterly answer rate

Run it on data.stackexchange.com (Stack Overflow database, refreshed weekly). The window ends 30 days before the last refresh so every question has had its full 30 days to be answered. For a run today, use `Start` = 2026-07-01 and `End` = 2026-09-23. Re-run for full Q3 (to 2026-09-30) after the refresh following Oct 30.

```sql
-- [brindledb] answer rate: share of open questions created in the window
-- that received any answer within 30 days of being asked.
SELECT
  COUNT(*)                                                   AS Questions,
  SUM(AnsweredIn30d)                                         AS AnsweredWithin30d,
  SUM(HasAcceptedOrUpvoted)                                  AS AcceptedOrUpvoted,
  CAST(100.0 * SUM(AnsweredIn30d) / NULLIF(COUNT(*), 0) AS DECIMAL(5,1))
                                                             AS AnswerRatePct
FROM (
  SELECT
    q.Id,
    CASE WHEN EXISTS (
      SELECT 1 FROM Posts a
      WHERE a.ParentId = q.Id AND a.PostTypeId = 2
        AND a.CreationDate <= DATEADD(day, 30, q.CreationDate)
    ) THEN 1 ELSE 0 END AS AnsweredIn30d,
    CASE WHEN q.AcceptedAnswerId IS NOT NULL OR EXISTS (
      SELECT 1 FROM Posts a
      WHERE a.ParentId = q.Id AND a.PostTypeId = 2 AND a.Score > 0
    ) THEN 1 ELSE 0 END AS HasAcceptedOrUpvoted
  FROM Posts q
  JOIN PostTags pt ON pt.PostId = q.Id
  JOIN Tags t ON t.Id = pt.TagId
  WHERE t.TagName = 'brindledb'
    AND q.PostTypeId = 1
    AND q.ClosedDate IS NULL
    AND q.CreationDate >= ##Start:string##
    AND q.CreationDate <  DATEADD(day, 1, CAST(##End:string## AS datetime))
) x
```

Companion query: median hours to first answer for the same window.

```sql
SELECT TOP 1
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY HoursToFirst) OVER () AS MedianHoursToFirstAnswer
FROM (
  SELECT q.Id,
         DATEDIFF(hour, q.CreationDate, MIN(a.CreationDate)) AS HoursToFirst
  FROM Posts q
  JOIN PostTags pt ON pt.PostId = q.Id
  JOIN Tags t ON t.Id = pt.TagId
  JOIN Posts a ON a.ParentId = q.Id AND a.PostTypeId = 2
  WHERE t.TagName = 'brindledb'
    AND q.PostTypeId = 1
    AND q.ClosedDate IS NULL
    AND q.CreationDate >= ##Start:string##
    AND q.CreationDate <  DATEADD(day, 1, CAST(##End:string## AS datetime))
  GROUP BY q.Id, q.CreationDate
) y
```

Caveats:
- SEDE excludes deleted posts. Closed questions are excluded on purpose, matching the playbook's `ClosedDate IS NULL` filter on both sides.
- "Answered" counts any answer, including community ones. To isolate staff, add `AND a.OwnerUserId IN (<id1>, <id2>)` inside the `EXISTS`.
- The backlog query from the playbook templates (open questions with no upvoted or accepted answer, ordered by views) is the companion list for the weekly steward.

## Metrics for the slide

| Metric | Source | Target (self-set) |
| --- | --- | --- |
| Answer rate within 30 days | Query above | 90% |
| Median time to first answer | Companion query | 1 business day |
| Canonical coverage: top 20 support-ticket themes with a self-answered canonical | Support tickets vs posted canonicals | Count, rising each quarter |
| Views on canonicals | Post view counts | Trend, not a target |
| Monthly AI-citation spot check | Manual check in AI assistants | Report found / not found |
| Hygiene (pass threshold zero) | Moderator messages, flags, deletions | 0 spam flags, 0 AI deletions, 0 undisclosed-affiliation comments, 0 rejected edits |

Reputation: show it as a footnote ("both accounts at about 1,800 rep, 2,000 edit threshold reachable"), not a KPI. Nothing in the table above needs more than 15 rep (self-answered canonicals).

## Ranked actions for the next quarter

| Action | Owner | Hours/week | Rep gate |
| --- | --- | --- | --- |
| Tag excerpt and wiki: route bugs, requests and billing to Brindlecore channels | Steward | one-off, about 1 | any, peer-reviewed |
| Self-answered canonical per recurring support theme (5-10 this quarter) | Both engineers | about 1-2 | 15 |
| New answers on high-view threads with outdated answers | Both engineers | about 1 | 1 |
| Duplicate flags onto canonicals | Both engineers | about 0.5 | 15 to flag; 3,000 to vote |
| Daily 15-minute tag-feed rotation | Alternating | about 1.75 | 1 |

Disclose in every post that names Brindlecore, including the question half of a self-answered pair. Use the playbook's disclosure line: "Disclosure: I work at Brindlecore, which maintains BrindleDB." Write the posts by hand, with no generative AI in any part. At about 1,800 rep, neither engineer can vote to close alone, so duplicate handling is by flag.

## Open items

- Do you want the staff-only variant of the answer rate? I need the two Stack Overflow user ids.
- Confirm hours per week and where bugs and account issues go today. That decides whether Curate or Maintain fits.
- Confirm that [brindledb] exists as a tag. Creating one needs 1,500 rep, which both engineers have.