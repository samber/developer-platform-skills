I couldn't run any of this. The Stack Exchange API calls were blocked: `curl` and WebFetch both needed approval I didn't have. So I have no numbers, and I haven't invented any. Below are the queries to run, a slide template with blanks, and three problems with the VP's asks that you should raise before the slide goes out.

## Do this first (about 5 minutes)

1. Open https://data.stackexchange.com/stackoverflow/query/new and paste the queries below. Set `Start` to `2026-07-01` and `End` to `2026-10-01` for Q3.
2. Fill in the two engineers' Stack Overflow user IDs (the `<ID1>`, `<ID2>` placeholders).
3. SEDE data refreshes weekly (Sundays), so figures can lag by up to 7 days. Footnote the data date on the slide.

## (a) Answer rate and peer benchmark

No published "industry benchmark for vendor tags" exists. If someone cites a figure, ask for the source. The defensible benchmark is a peer-tag comparison computed the same way.

```sql
-- Per-tag answer rate for the quarter. Includes brindledb and peer vendor tags.
SELECT
  t.TagName,
  COUNT(*)                                                         AS questions,
  SUM(CASE WHEN p.AnswerCount > 0 THEN 1 ELSE 0 END)              AS answered,
  CAST(100.0 * SUM(CASE WHEN p.AnswerCount > 0 THEN 1 ELSE 0 END)
       / COUNT(*) AS DECIMAL(5,1))                                 AS pct_answered,
  CAST(100.0 * SUM(CASE WHEN p.AcceptedAnswerId IS NOT NULL THEN 1 ELSE 0 END)
       / COUNT(*) AS DECIMAL(5,1))                                 AS pct_accepted,
  CAST(100.0 * SUM(CASE WHEN p.Score >= 1 AND p.AnswerCount = 0 THEN 1 ELSE 0 END)
       / COUNT(*) AS DECIMAL(5,1))                                 AS pct_unanswered_scored
FROM Posts p
JOIN PostTags pt ON pt.PostId = p.Id
JOIN Tags t      ON t.Id = pt.TagId
WHERE p.PostTypeId = 1
  AND p.CreationDate >= '##Start:string?2026-07-01##'
  AND p.CreationDate <  '##End:string?2026-10-01##'
  AND t.TagName IN ('brindledb','timescaledb','influxdb','questdb','clickhouse','victoriametrics','prometheus')
GROUP BY t.TagName
ORDER BY questions DESC;
```

Add a second figure, "answered by us", which is the number a VP usually means by "our answer rate":

```sql
-- Share of [brindledb] questions with at least one answer from our two engineers.
SELECT
  COUNT(DISTINCT q.Id) AS questions,
  COUNT(DISTINCT CASE WHEN a.OwnerUserId IN (<ID1>,<ID2>) THEN q.Id END) AS answered_by_us
FROM Posts q
JOIN PostTags pt ON pt.PostId = q.Id
JOIN Tags t      ON t.Id = pt.TagId AND t.TagName = 'brindledb'
LEFT JOIN Posts a ON a.ParentId = q.Id AND a.PostTypeId = 2
WHERE q.PostTypeId = 1
  AND q.CreationDate >= '##Start:string?2026-07-01##'
  AND q.CreationDate <  '##End:string?2026-10-01##';
```

Caveats:
- Check the tag exists first (`/tags/brindledb/info`). If it has fewer than about 30 questions a quarter, percentages swing wildly. Show raw counts next to them.
- `AnswerCount` counts deleted-then-undeleted edge cases loosely. That's fine for a slide, but footnote the definition.

## (b) Reputation

SEDE can't give exact reputation gained per period. Use the API, which is exact:

```
https://api.stackexchange.com/2.3/users/<ID1>;<ID2>/reputation-history?site=stackoverflow&pagesize=100&fromdate=1782864000&todate=1790812800
```

- The two timestamps are placeholders for 2026-07-01 and 2026-10-01 UTC. Compute them yourself with `date -u -j -f %F 2026-07-01 +%s`.
- Sum `reputation_change` across pages, using `page=N` until `has_more` is false.
- Also sum it separately for events on posts tagged `brindledb`. This is the number that reflects tag work.

## (c) "Questions edited or cleaned up"

```sql
-- Edits by our engineers in the quarter, split by post type and ownership.
SELECT
  ph.UserId,
  CASE WHEN p.PostTypeId = 1 THEN 'question' ELSE 'answer' END AS kind,
  CASE WHEN p.OwnerUserId = ph.UserId THEN 'own' ELSE 'others' END AS ownership,
  COUNT(*) AS edits
FROM PostHistory ph
JOIN Posts p ON p.Id = ph.PostId
WHERE ph.PostHistoryTypeId IN (4,5,6)  -- title, body, tags
  AND ph.UserId IN (<ID1>,<ID2>)
  AND ph.CreationDate >= '##Start:string?2026-07-01##'
  AND ph.CreationDate <  '##End:string?2026-10-01##'
GROUP BY ph.UserId,
  CASE WHEN p.PostTypeId = 1 THEN 'question' ELSE 'answer' END,
  CASE WHEN p.OwnerUserId = ph.UserId THEN 'own' ELSE 'others' END;
```

## Slide template

| Metric | Brindledb | Peer median | Source |
|---|---|---|---|
| Questions in quarter | __ | __ | query (a) |
| % answered | __% | __% | query (a) |
| % accepted | __% | __% | query (a) |
| % answered by Brindlecore | __% | n/a | query (a2) |
| Rep gained, tag-scoped | __ | n/a | API |
| Edits to others' posts | __ | n/a | query (c) |

## Three problems to raise with the VP

1. **The +5,000 rep target is probably unreachable on a niche tag.** Answer upvotes give +10 each, accepted answers +15, and rep is capped at 200 per day per person. Reaching 5,000 means roughly 400–500 upvotes a quarter. Check query (a)'s question volume first. A tag with 40 questions a quarter can't support that. Set the target from the tag's actual volume. Rep is also a poor headline KPI because it rewards chasing popular questions over [brindledb] ones, and it's partly outside your control.
2. **Both engineers sit around 1,800 rep, below the 2,000 threshold for direct edits.** Verify the current threshold at `/help/privileges`. Their edits to other people's posts are likely suggested edits that need review. Rejected ones count for nothing, and approved ones add only +2 rep each, with a lifetime cap of 1,000. Query (c)'s "others" rows overstate impact unless you also count approved versus rejected suggestions (`PostHistoryTypeId` 24 for accepted suggestions, via `SuggestedEdits`).
3. **"Questions edited" measures effort, not outcome.** It doesn't show whether developers got help. Replace it, or pair it with time-to-first-answer and the share of questions answered by Brindlecore. Heavy editing of old posts also bumps them to the front page, which regulars sometimes dislike. Tidying is fine in moderation, but don't make volume a goal.

The most useful next step is to run queries (a) and (a2) and send me the output. I can then turn the real numbers into the final slide wording. If you'd rather I fetch them directly, approve one WebFetch or `curl` call to `api.stackexchange.com` and I'll do it.