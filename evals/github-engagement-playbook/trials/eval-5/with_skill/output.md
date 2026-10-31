# GitHub engagement plan for vellumgrid/vgdb

**Short version:** Do none of the three tactics as written. Replace them with the plan below.

- **Interview:** I could not run it, so I assumed answers and marked them. Correct any that are wrong.
- **Traffic data:** I have no export, so the diagnosis row is provisional.

## 1. Diagnosis (provisional)

| Item | Reading |
|---|---|
| Your goal | A Trending burst of about 120 stars in 24h on a 4,100-star repo |
| Pattern | Unknown. I have no traffic, referrer or dependents data |
| Assumed row | "Visitors rise, stars and dependents do not", or "downloads grow, stars flat". Confirm with real numbers |

**Do this before next week:**

1. Create the weekly traffic archive. GitHub keeps only 14 days of traffic, and it can't be recovered later.
   - Use the bundled Apps Script files in `scripts/` and `references/tracking-tools.md`.
   - The token needs push access.
2. Read watchers, "Used by" dependents and Go module/registry downloads. Compare each to the same window a quarter ago.
3. Check OSS Insight star history to see what dated your last spike.

Stars are not a target. The "120 stars" figure has no documented basis.

## 2. Your three tactics

### (1) Trending push: ~120 stars in 24h

- **Trending ranks stars gained inside a window, per language.** GitHub publishes no formula `[documented]`.
- **"Star velocity vs your own baseline" is `[folklore]`.**
  - The 120 figure is therefore a guess, not a threshold.
  - Nobody can promise a placement.
- **A Trending burst is launch-sized work, not a weekly task.**
  - Plan it with `samber/developer-relations-skills@oss-launch`.
  - Anchor it to a real event, such as a release with a user-visible change, a benchmark post or a talk.
  - It would be the first step of the sequence, not a goal in itself.
- **What you can do next week:**
  - Cut a real release with a written body (template 1 below).
  - Publish the post that goes with it on Hacker News, Reddit r/golang or your blog.
  - End that post with the star ask (template 14).
  - Stars that arrive from readers who care are legitimate. Report them as an outcome, never a quota.
- **What you must not do:** buy, trade or reward stars.
  - The AUP bans "rank abuse, such as automated starring or following" `[documented]`.
  - StarScout (He et al., ICSE 2026) found 6.0M suspected fake stars. Those stars were about 5x weaker, faded within two months and became a liability. About 90% of the campaign repos were deleted.
  - If anyone proposes a star-exchange, use template 7.

### (2) Topics: 34 drafted

- **Limit:** 20 per repo. Each is lowercase letters, digits and hyphens, up to 50 characters `[documented]`.
  - `Vector_DB` is invalid (uppercase and underscore).
  - `BestVectorDatabase2026` is invalid (uppercase).
  - 34 is over the cap.
- **Use 5-10 accurate topics.** Each feeds `github.com/topics/<name>` `[documented]`. Search weight is unpublished.
- **Suggested set (confirm against what vgdb actually does):**
  - `vector-database`
  - `vector-search`
  - `golang`
  - `go`
  - `rag`
  - `embeddings`
  - `similarity-search`
  - `approximate-nearest-neighbor`
  - `database`
- **Cut:**
  - `BestVectorDatabase2026` is a superlative and a year. It is spammy and stales in January.
  - `AI` and `machine-learning` are generic. Keep them only if you can defend them as true for this repo.
- **Effort:** an hour, once.

### (3) Everyone stars and follows; ask friends

- **Skill scope:** The skill does not cover employee starring directly. The reading below is mine, labelled as such.
- **Fine, my reading:**
  - Employees who genuinely use vgdb, starring from their real accounts, because they want to.
  - A neutral note in Slack: "if you use it and like it, a star helps".
  - No tracking of who did and who did not.
- **Avoid:**
  - Mandates, leaderboards, prizes or time off for starring. The AUP's give-away clause covers engagement "incentivized by ... gifts or other give-aways" `[documented]`.
  - Asking friends or people who don't use the project. That is the "star to enter" pattern, which is policed. It also pulls in stars from accounts that never use vgdb.
  - Any reciprocal star exchange with other projects.
- **Expected effect:** 28 people is under a quarter of the 120 you want. Even a perfect turnout does not change the picture.
- **"Follow" is not a project metric.** Following the org or its accounts feeds the home feed of those followers `[documented]`, but that reaches only the people who follow. The default home is a work dashboard with the feed on a separate tab `[documented]`.
- **Better use of employees:**
  - Answer Q&A (rung 4 below).
  - Review PRs.
  - Post their own real experience off-platform.

## 3. Ranked surfaces (re-ranked)

Default order by value per maintainer hour:

1. Traffic archive and metric swap
2. Small, frequent releases as feed events
3. Topics
4. Discussions Q&A

**Re-rank, with the interview answers I assumed:**

| Assumed answer | Effect |
|---|---|
| A date inside two months (your plan is next week) | Rungs 1-3 are promoted. Discussions opens but carries no deadline metric |
| Compounding asset, with an answerer and backup named | Discussions Q&A moves to rung 2. **Needs your answer to Q3 and Q6** |
| One-off win | Would cut the list to rungs 1-2 |

Result for now:

1. Traffic archive and metric swap
2. Releases as feed events
3. Topics
4. Discussions Q&A (promote only if you name an answerer plus a backup. Delete it if nobody answers publicly, because an unanswered tab reads as abandonment)

## 4. Cadence to next week and beyond

| When | Action | Owner role |
|---|---|---|
| Day 1-2 | Set up the traffic archive and Google Alerts. Pull dependents, downloads and star history | Growth lead |
| Day 1 | Replace the topic list with the 5-10 above | Maintainer |
| Day 1-3 | Back-fill release bodies on the last three releases. Answer open usage issues, oldest first, inside the effort ceiling | Maintainers |
| Next week | Ship one real release (template 1) with the auto-created Announcement (template 2). Never batch fixes to make it look bigger | Maintainer |
| Next week | Publish one off-platform post about that release. End with the template 14 star ask | Growth lead |
| Weeks 2-4 | Open Discussions with Announcements and Q&A. Add a `contact_links` entry in `.github/ISSUE_TEMPLATE/config.yml`. Convert 5-10 answered issues. Pin template 3. Enable Dependabot version updates | Maintainer plus named answerer |
| Weekly | Answer Q&A, mark answers, merge Dependabot PRs, export traffic | Answerer and backup |
| Quarterly | Compare watchers, dependents, downloads and referrers to baseline. Revise topics | Growth lead |

If leadership still wants Trending, plan it as a launch with `oss-launch`. It needs a real hook, such as a release, a benchmark or a talk, and a date.

## 5. Filled templates

Run each through your humanizer skill before posting. Anything in `<angle brackets>` is unknown to me and I left it visible.

### Template 1: release body

```markdown
## <one-line outcome a Go developer gets from this release, not the version number>

<two sentences: who should upgrade to vgdb <version>, and what changes for them>

### Breaking changes

- <change> - migrate with <link to migration guide>

### New

- <capability> (#<PR>) - thanks @<external contributor>

### Fixed

- <symptom the user saw> (#<issue>)

Install: `go get github.com/vellumgrid/vgdb@<version>`
Questions: <link to the Q&A category>
```

Cut any heading that would be empty. Don't invent contributors.

### Template 2: announcement discussion

```markdown
**vgdb <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

Tick "Create a discussion for this release" on the release form and paste this as the body.

### Template 3: start-here pinned post

```markdown
Welcome to vgdb Discussions.

- **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.
```

### Template 8: leadership metric note

GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018). They correlate only moderately with use (He et al., 2026). From this quarter we report:

- Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
- Watchers (who receive release news)
- Dependents ("Used by") and <registry> downloads
- Q&A answered share and median time to answer, once Discussions has a month of history

Stars stay on the sheet as a trailing signal: 4,100 (<change> this quarter).

### Reusable asks

- **Template 14, star ask for the end of the off-GitHub post.** Ask once and offer nothing in return.
  ```markdown
  If vgdb saved you time, a ⭐ on GitHub helps it grow and reach more people: https://github.com/vellumgrid/vgdb
  ```
- **Template 7, star-for-star decline.** Use it if another project proposes a swap.

## 6. Metrics

Track:

- Unique visitors
- Top referrers
- Watchers
- Dependents
- Downloads
- Q&A answered share
- Median time to answer (GraphQL `answer.createdAt` minus `createdAt`)

Cloners are diagnostic only, because CI inflates them. Stars are never a target; they stay on the sheet as a trailing signal.

## 7. Questions I need answered

These change the ranking:

1. Is vgdb a company project (I assumed yes)?
2. Which number does leadership read today, and what decision hangs on it?
3. How many usage questions per week arrive as issues or private messages?
4. What date must the result land by?
5. Is this a one-off win or a compounding asset?
6. Hours per week available, and who answers publicly, with what backup?