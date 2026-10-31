# Board prep for the 14th: what to give the CEO

Don't give him a plan to close the star gap. Give him a one-page memo that proposes a better metric, shows what stars can realistically do, and fixes the Kubernetes docs gap. Below is the memo, ready to paste.

## Two checks before you send it (about 30 minutes)

1. **Which Q3?** Today is Oct 30. If "Q3" means calendar Q3, it has already ended. Confirm the deadline in the slide.
2. **Is the downloads number real?** A few CI-heavy dependents can inflate npm downloads. Look at the top 10 dependents and the per-version breakdown. If one or two of them account for most of the growth, say so in the memo instead of letting a board member find it.

---

## Memo: Stars vs. adoption for pgnest

**Summary:** pgnest adoption grew 2.3–2.7× this year. Stars grew 6%. The 2,000-star target measures the wrong thing, and the gap can't be closed legitimately by the deadline. I propose replacing it with adoption metrics and spending effort on the Kubernetes onboarding gap that drives both adoption and support load.

### The numbers (Jan → now)

| Metric | Jan | Now | Change |
|---|---|---|---|
| npm weekly downloads | 41k | 96k | +134% |
| "Used by" repos | 290 | 770 | +166% |
| GitHub stars | 1,140 | 1,205 | +5.7% (+65) |
| Stars per dependent repo | 3.9 | 1.6 | stars lag usage |

### How big is the star gap?

- We need +795 stars. We gained 65 in about 10 months, roughly 6 a month.
- At that pace the target takes about 10 years. Even a strong launch usually brings low hundreds of stars, not 800. That is my estimate, not a measurement.
- Buying or farming stars is off the table. GitHub removes fake stars. Postgres infrastructure buyers check credibility, and a flagged repo costs far more than a missed slide.

### Why stars don't track usage for us

A connection pooler is infrastructure. People install it, set it up once and never think about it again. They don't browse GitHub or star it. Our users show up in dependents and downloads, not stars.

### Proposal

1. **Replace the headline star target** with these metrics:
   - "Used by" repos: 770 now, target 1,200 (the current growth rate gets there).
   - Weekly downloads, reported with the share from the top 10 dependents.
   - Median time from first install to a working pool on Kubernetes (new, see below).
   - Config-question issues per week (6–8 now).
2. **Keep stars as a secondary indicator** with a realistic target of about 1,400 over the next two quarters, which would be 3× our current pace. The stretch case needs a successful launch.
3. **Fix the Kubernetes gap.** About 60% of our issues are pool-sizing questions on Kubernetes, 6–8 a week. That is a documentation and defaults problem, and it costs a 9-engineer team a lot of time.

### Kubernetes onboarding plan (4–6 weeks, 1–2 engineers part-time)

1. **Week 1:** Read the last 50 of these issues and group the questions. Expect a handful of repeating ones, such as pool size vs. `max_connections` across replicas, and transaction vs. session mode.
2. **Weeks 1–2:** Write one "Pool sizing on Kubernetes" guide with a worked formula and a copy-paste Helm values example. Link it from the README and pin it in the issue template.
3. **Weeks 2–3:** Add an issue-template check that points to the guide before filing. Track the weekly config-question count.
4. **Weeks 3–5:** Make the defaults smarter. If the pooler can derive a safe default from the server's `max_connections` and the replica count, most of these questions go away.
5. **Week 5–6:** Publish the guide as a post and submit it to Hacker News and r/kubernetes. A useful, specific guide is the kind of content that gets shared and brings in stars as a side effect.

**Expected result:** config issues fall by at least half (target ≤3 a week), onboarding time is measurable, and stars get a modest lift. I'll report all three at the next board meeting.

### Risks

- The download numbers may include CI or mirror traffic (check pending).
- The guide may not cut issues if the root cause is unclear defaults. That is why step 4 exists.
- If the board insists on a star target, the honest options are a long timeline or a larger launch budget, not shortcuts.

---

## Questions for you

- What does the npm package contain? If it's a client or wrapper and the pooler ships separately (Docker, Helm), downloads undercount real deployments. That would be useful to say in the memo.
- Is the 2,000 target tied to anything (a funding milestone, a bonus, a commitment)? If so, the CEO's framing matters more and I'd soften the memo.
- Do you have Docker pulls or Helm chart installs? Either would be a stronger "real usage" metric than npm.