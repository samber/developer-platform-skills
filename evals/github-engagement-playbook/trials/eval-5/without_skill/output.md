# Plan for next week: what to run, what to cut

## Verdict on the three items

| Item | Verdict |
|---|---|
| 1. Hit Trending with ~120 stars in 24h | ⚠️ Keep the goal, change the method. |
| 2. 34 topics | ❌ Not possible as drafted. |
| 3. All 28 staff star and follow, plus friends | ⚠️ Staff yes, friends no. |

## 1. Trending

**What's known:** GitHub doesn't publish the Trending formula. Star velocity against baseline is the common belief, and it fits what people observe. Treat "120 stars" as your growth lead's guess, not a fact.

**Calibrate first (10 minutes, today):**
1. Open the Go trending page, daily view: `github.com/trending/go?since=daily`.
2. Note the "stars today" count of repos ranked #10 and #25. That's your real target.
3. Repeat the check on Monday, Wednesday, and Friday, because the bar moves.

**The problem:** 28 employees give at most 28 stars, about 23% of 120. The other ~90 have to come from real strangers. That needs an outside event, not a star request.

**Create a real catalyst:**
1. Pick one concrete news item. A release is the best option, e.g. a vgdb version with a benchmark result or a new feature. A bare "please star us" post doesn't count.
2. Publish a short write-up with reproducible numbers: methodology, hardware, and a comparison against the alternatives people already know.
3. Launch the same day, Tuesday to Thursday, around 08:00–10:00 US Eastern:
   - Show HN, titled factually, e.g. "Show HN: vgdb – open-source vector DB in Go (v0.x)". Don't put "please star" in it.
   - r/golang and r/vectordatabase. Lead with the technical content.
   - Golang Weekly: submit the link beforehand.
   - Gophers Slack #show-and-tell, and relevant Discords.
   - Maintainers answering comments live for the first 6 hours. That's where the stars come from.
4. Have a good-first-issue list and a clean `README` quickstart ready before the launch. Check that `docker run` or `go install` works in under 2 minutes.
5. Don't ask anyone to star. If the repo is good, a "star if useful" line in the README is enough.

**Realistic outcome:** a good HN front-page day usually brings hundreds of stars. A flat day brings 10–30. Trending is a side effect of a launch, so plan the launch and let the ranking follow.

## 2. Topics

Three facts make the draft list unusable:
- **GitHub allows a maximum of 20 topics per repo.** 34 can't be saved.
- **Topics must be lowercase letters, numbers, and hyphens.** `Vector_DB` and `BestVectorDatabase2026` are invalid as written. `Vector_DB` would become `vector-db`.
- **`BestVectorDatabase2026` is a superlative with a year.** It reads as spam and becomes stale in January. It also doesn't match what people search for.

**Use 10–15 topics.** Choose topics that people actually browse and that describe the repo. Check topic page sizes at `github.com/topics/<name>`, and prefer the ones with a real population.

Suggested set (verify each against its topic page before saving):

`vector-database`, `vector-search`, `similarity-search`, `embeddings`, `nearest-neighbor-search`, `hnsw`, `golang`, `go`, `database`, `rag`, `machine-learning`, `ai`, `semantic-search`, `llm`, `open-source`

Drop `ai` and `machine-learning` if you're near the cap. They are huge and your repo will be buried there. Keep `vector-database`, `vector-search`, `golang`, and `rag`. Those are where your users look.

Also fill in the repo description, the website URL, and the social preview image (1280×640). These matter more than extra topics.

## 3. Employees and friends

**Employees: fine, on these terms**
- Ask in a normal internal post. Say it's optional and has no tracking or leaderboard. Never make it a performance or culture signal.
- Stars should come from people who have actually looked at the repo. Better still, ask them to try it and file an issue or PR.
- Anyone who posts publicly about the repo should say they work at Vellumgrid.
- Skip the "follow" ask. Following the repo or the org does nothing for Trending. Follows of the org account are only mildly useful for reach.
- Spread it out. 28 stars in 10 minutes looks like what it is. The days around the launch are fine.

**Friends: don't do it**
- A coordinated "star it for us" drive to move a ranking falls under GitHub's rules on inauthentic activity and rank manipulation, and Trending applies spam filtering. Possible consequences are removal from Trending, stars purged, or account and repo flags. Check GitHub's current Acceptable Use Policy for the exact wording.
- The cost is high for the gain. A flagged vector DB repo gets noticed by exactly the people you want to impress, and some of them check star quality.
- Friends who don't use the product give you stars with no usage behind them, so the number is misleading for both of you.
- The honest version that works: ask friends who might use it to try it and tell you what broke. That produces issues and actual stars.

## Execution timeline

**Today – Monday**
1. Calibrate the Trending bar (above).
2. Fix the topics: trim to ≤15 and make them valid.
3. Finalize the release, benchmark post, and README quickstart.
4. Draft the HN and Reddit posts. Assign two maintainers for live replies.

**Tuesday or Wednesday (launch day)**
1. 08:00–10:00 ET: ship the release and post to HN, then r/golang.
2. Internal message to staff: "We launched. Try it; star it if you like it."
3. Maintainers reply to every comment within about 15 minutes.
4. Log stars per hour in a sheet.

**Thursday – Friday**
1. Send the newsletter and the Golang Weekly submission.
2. Triage new issues quickly. First responses build credibility.
3. Record the final numbers: stars/day, Trending position and duration, referrers (GitHub Insights → Traffic).

## What to tell your growth lead

- The goal (visibility in the Go community) is right.
- The formula part is partly right: velocity matters, but it comes from a launch event.
- 120 is a guess. Replace it with the real #25 number.
- Stars are a vanity metric. Track GitHub Insights → Traffic (unique visitors, clones), `go get` or Docker pulls, issues from strangers, and contributors. Report those alongside stars.

If you want, I can draft the Show HN post, the internal staff message, or the final 15-topic list next. Which one first?