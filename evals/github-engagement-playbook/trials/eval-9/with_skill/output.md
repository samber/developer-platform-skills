**Do now (10 min):** In Insights > Traffic, export views, clones, referrers and popular paths. GitHub deletes this data after 14 days, so do it before anything else. Paste the export to me if you want a second read.

I answered the interview from the skill with assumptions, listed at the end. Correct me where they are wrong.

## 1. Diagnosis

Row: **"Visitors rise, stars and dependents do not." Reading: the page fails evaluators.**

- Visitors: ~400 to ~1,100 per week, about 2.75x. Referrers are the podcast show notes and the conference site.
- Stars: 310 to 345, +35 in 3 months, about 3 per week.
- Used by: 12, flat.
- Founder's premise ("not enough people know about us") is falsified. Awareness tripled and the repo got visits from the right channels. Reach is not the bottleneck. Conversion is.
- Cause of the stuck "Used by": `[folklore]` GitHub fills it from dependency-graph manifests (go.mod, package.json and similar). An agent installed by binary, Docker image or Helm chart never appears there, however many people run it. Check how Sentinel ships before reading 12 as "nobody uses it".
- Row 3 may also fit: "Downloads or dependents grow, stars flat". Unknown until you pull release-asset, image-pull or registry downloads. When two rows fit, the skill says run the metric swap first (template 8 below).

Not yet known: which paths visitors hit (README only, or docs and Releases too), and whether downloads grow. The export answers both.

## 2. Founder's three proposals

| Proposal | Verdict | Why |
|---|---|---|
| More podcasts | Hold at current cadence. Add a star ask to every new show note and talk slide (template 14). | Inflow already works. More of it into a page that converts at ~0.3% mostly adds visits, not users. `[folklore]` |
| Submit to `github/explore` collections | Skip. | Its PR template attests "This change is not self-promotion". Self-promotion is "unlikely to be accepted". `[documented]` Awesome lists are the better target, since they usually accept an author's PR that meets their criteria. Check each list's rules. |
| Post in popular repos' issues | **No.** | Acceptable Use Policies ban bulk promotion. Maintainers hide it as spam, and it ties your name to spam. `[documented]` The only allowed form is a disclosed answer to that exact issue. |

The founder has a point: if it were pure awareness, more reach would help. The data shows it is not.

## 3. README rewrite this week

Yes, but sequence it. Do not rewrite blind.

1. Today: export traffic (above). This is the "before" baseline.
2. Check popular paths. If visitors hit README only and leave, the first screen is the problem.
3. Rewrite using `samber/developer-relations-skills@readme-optimization`, not from scratch by taste.
4. Have an engineer verify the install and quick-start commands. A wrong command costs more than a weak headline.
5. Ship it, then compare visitor-to-star ratio for 4 weeks against the baseline.

I can run the readme-optimization skill on your current README next.

## 4. Ranked surfaces

Order is value per maintainer hour, assuming a compounding mandate and no date inside 2 months.

1. **Traffic archive and metric swap.** Near-zero effort. Tells you which problem exists. Compounding.
2. **Small, frequent releases as feed events.** Minutes per release. Each Release notifies watchers and shows on stargazers' feeds `[documented]`. Compounding.
3. **Topics.** One hour. 5-10 accurate topics, each feeding a topic page `[documented]`. Search weight is unpublished. Compounding.
4. **Discussions Q&A.** Highest value, standing cost of hours per week. Promote it to rung 2 only if usage questions already arrive weekly and an answerer plus backup is named. If nobody answers publicly, skip it. An unanswered tab reads as abandonment.

Re-rank: no deadline given, so I kept the default order. A date inside 2 months would move rungs 1-3 up. A one-off goal would cut the list to rungs 1-2.

## 5. Cadence

Landing date is unknown. I assumed 6 weeks: **2026-12-11**. Change it if wrong.

1. **Week 1 (Oct 30 - Nov 5)**
   - Marketing: export traffic and set up the KPI sheet (about 1 hour, see `references/tracking-tools.md`).
   - Marketing: add Google Alerts for `"sentinel-agent"` and `"sableridge/sentinel-agent"`.
   - Engineer: confirm how the agent is distributed and where downloads can be counted.
   - Marketing and engineer: send the leadership metric note (template 8) to the founder.
   - Maintainer: set 5-10 topics.
2. **Week 2**
   - Marketing: draft the README with readme-optimization.
   - Engineer: verify install and quick-start commands.
   - Maintainer: back-fill bodies on the last 3 releases (template 1).
   - Marketing: add the star line to the next podcast show note and talk slide (template 14).
3. **Week 3**
   - Ship the README.
   - Maintainer: open Discussions with two categories (Announcements, Q&A) only if the answerer condition holds.
   - Maintainer: pin the start-here post (template 3).
   - Maintainer: add Dependabot version updates.
4. **Every release**
   - Release body, then the auto-created Announcement discussion, then one off-platform post.
   - Cut a release when a user-visible change merges. Do not batch.
5. **Weekly (15-30 min)**
   - Maintainer: merge Dependabot PRs and answer Q&A.
   - Marketing: export traffic.
6. **Week 6 (Dec 11)**
   - Read visitors, referrers, watchers, dependents and downloads against the Oct 30 baseline.
   - Decide on awareness spend with that data.

## 6. Filled templates

**Template 1: release body.** Unknown facts stay as placeholders.

```markdown
## <one-line outcome a user gets, not the version number>

<two sentences: who should upgrade, and what changes for them>

### Breaking changes

- <change> - migrate with <link to migration guide>

### New

- <capability> (#<PR>) - thanks @<external contributor>

### Fixed

- <symptom the user saw> (#<issue>)

Install: `<package manager command pinned to this version>`
Questions: <link to the Q&A category>
```

**Template 2: announcement discussion.**

```markdown
**sentinel-agent <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

Tick "Create a discussion for this release" on the release form and paste this as the body.

**Template 3: start-here pinned post.** Use only if Discussions opens.

```markdown
Welcome to sentinel-agent Discussions.

- **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.
```

**Template 8: leadership metric note.** Send this to the founder.

> GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:
>
> - Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days). Baseline: ~400/week before the podcasts and talk, ~1,100/week now.
> - Watchers (who receive release news): <current>
> - Dependents ("Used by") and <registry or image> downloads: Used by 12, downloads <current>
> - Q&A answered share and median time to answer, once Discussions has a month of history
>
> Stars stay on the sheet as a trailing signal: 345 (+35 this quarter).

## 7. Metrics

Track:
- Unique visitors and top referrers
- Watchers
- Dependents
- Downloads
- Q&A answered share
- Median time to answer (GraphQL `answer.createdAt` minus `createdAt`)

Clones are diagnostic only, because CI inflates them. Stars are never a target.

Never buy, trade or reward stars. StarScout (He et al., ICSE 2026) found about 6.0 million suspected fake stars. They were about five times weaker than real stars and faded within two months. About 90% of the campaign repositories were deleted. `[documented]`

## Assumptions

I did not ask the interview questions. These are my defaults:

1. Company-owned repo.
2. Leadership reads stars, and the decision is how much awareness spend to approve.
3. Usage questions arrive as issues, at an unknown number per week.
4. No fixed landing date, so I used Dec 11.
5. Compounding asset, not a one-off.
6. Effort ceiling is about 2 hours per week, with no named public answerer yet.

**Next:** run the traffic export, then paste the top referrers and popular paths here. I will then pick between row 2 and row 3 and start the README.