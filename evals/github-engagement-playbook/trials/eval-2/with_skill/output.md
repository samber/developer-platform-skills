# Plan for the CEO: replace the star target with adoption metrics

**What to give him:** a one-page reframe plus a 15-day plan. Don't give him a way to add 795 stars, because none exists. This is a draft for you to review. I couldn't run the skill's interview, so interview answers 4 (landing date), 5 (one-off or compounding) and 6 (hours and answerer) are assumptions, listed at the end.

## 1. Diagnosis

Your numbers match two rows of the playbook's table:

| Metric | January | Now | Change |
|---|---|---|---|
| npm weekly downloads | 41k | 96k | +134% |
| "Used by" repos | 290 | 770 | +166% |
| GitHub stars | 1,140 | 1,205 | +65 (+5.7%) |

- **Primary row: "Downloads or dependents grow, stars flat."** Users install from the registry and never visit the repo to star it. The first action is to change the reported metric (template 8) and stop chasing stars.
- **Secondary row: "Usage questions pile up in issues."** About 60% of your issues are Kubernetes pool-size questions. I read "6-8 a week" as that 60% slice, which implies about 10-13 issues a week in total. The fix is a named answerer and Discussions Q&A.
- **The gap is not closable organically.** You need 795 stars. You gained 65 in about 10 months, roughly 6.5 a month. Reaching 2,000 would take about 10 years at that pace.
- **The "Q3" in the slide needs a date.** If it means calendar Q3 2026, it ended on Sept 30. If it means Q3 2027, you'd need about 70 stars a month, roughly 11 times your current pace.
- **Buying or trading stars is not an option.**
  - GitHub's Acceptable Use Policies ban "rank abuse, such as automated starring" [documented].
  - StarScout (He et al., ICSE 2026) found 6.0 million suspected fake stars across 18,617 repositories. They were about five times weaker than real stars and faded within two months. About 90% of the campaign repositories were deleted.
  - For a database-infrastructure product sold to engineers, a purged star count looks worse than a flat one.
- ⚠️ **Gaps in the evidence:**
  - **No traffic data.** Without visitor and referrer data, the first table row ("no inflow") can't be ruled out. GitHub keeps only 14 days of traffic [documented]. If you start the archive today, the board slide will have about two weeks of baseline and no trend.
  - **Source of the January figures.** Confirm whether they come from a recorded source or from memory. A board slide needs provenance.
  - **npm downloads are noisy.** They count CI reruns and mirror traffic [folklore], so lead with "Used by" and show downloads as supporting evidence.

## 2. Ranked surfaces, with the re-rank

Ranked by value per maintainer hour. Cadence is sequence, not rank.

1. **Traffic archive and metric swap.** About an hour once, and it compounds. It tells you which problem you actually have.
2. **Small, frequent releases as feed events.** Minutes to an hour per release. Each GitHub Release notifies release watchers and appears on stargazers' and watchers' Feed tab [documented]. Tick "Create a discussion for this release" with an Announcement category.
3. **Topics.** About an hour once: 5-10 accurate topics, each feeding `github.com/topics/<name>` [documented]. Search weight is unpublished.
4. **Discussions Q&A.** A standing weekly job. It builds an indexed, answered support archive and credits helpers [documented].

**Re-rank:**
- **The board date is inside two months, so rungs 1-3 are promoted.** Discussions opens but carries no deadline metric. Q&A answered share needs a month of history, so it can't be on the Nov 14 slide.
- **Discussions moves up to rung 2 only if you name one answerer and one backup.** The 6-8 weekly questions justify it, but I don't know who answers. If nobody will answer publicly, skip Discussions. An unanswered tab reads as abandonment.
- **If the CEO wants a one-off win, cut the list to rungs 1-2.** Everything else only helps next quarter.

Dependabot and the label scheme (`references/labels.md`) are small standing additions to this list, not ranked rungs.

My own addition, not from the playbook: a "sizing pools on Kubernetes" docs page would remove the repeated question at its source. The sibling skill `developer-relations-skills@developer-troubleshooting-docs` covers that. Link the page from every Q&A answer (template 4).

## 3. Cadence to the board meeting

Owner roles: **Maintainer** (an engineer on the repo), **Answerer** (named by you, with a backup), **You** (DevRel or eng lead), **CEO**.

| When | Owner | Action |
|---|---|---|
| Oct 30-31 | You | Set up the KPI sheet from `references/tracking-tools.md` (Apps Script, a token with push access, weekly trigger). Create Google Alerts for `"pgnest"` and `"oriolith/pgnest"`. Pull star history from OSS Insight to date the star changes against your releases. |
| Oct 30-31 | You | Replace the January figures with sourced ones, or footnote them as approximate. |
| Nov 2-4 | Maintainer | Set 5-10 accurate topics. Back-fill release bodies on the last three releases (template 1). |
| Nov 2-4 | Answerer | Answer open Kubernetes pool-size issues, oldest first, inside the hours ceiling. |
| Nov 4-6 | Maintainer | Open Discussions with two categories, Announcements and Q&A. Add a `contact_links` entry in `.github/ISSUE_TEMPLATE/config.yml` pointing questions to Q&A. Enable Dependabot version updates. |
| Nov 4-6 | Maintainer | Convert 5-10 answered usage issues to discussions (template 5). Post and pin the start-here post (template 3). |
| Nov 6-10 | Maintainer | Ship any merged user-visible change as its own release (templates 1 and 2). Never batch fixes to make a release bigger. |
| Nov 9-11 | You | Read the first week of traffic. Draft the board slide with template 8. |
| Nov 12 | You + CEO | Review the slide and agree the answer to "why not stars". |
| Nov 14 | CEO | Present. |
| Weekly after | Answerer | Answer Q&A inside the stated target and mark answers. Label new issues, PRs and discussions. Merge Dependabot PRs. Export traffic. |
| Quarterly | You | Read watchers, dependents, downloads and referrers against the baseline, and revise topics. |

**Hours.** My estimate is 8-10 hours in total before the 14th, then 3-4 hours a week once Discussions is live. That is my own sizing, not a playbook figure, and it assumes the interview's hours ceiling allows it.

**Star asks.** If any blog post, talk or newsletter ships before the 14th, end it with the single line from template 14. Nothing is offered in return, and no star asks go in other repositories' issues.

## 4. Filled templates

I left unknown values as visible `<placeholders>`. I did not run these through a humanizer skill.

### Template 8: leadership metric note (the board slide)

> **Replace** "GitHub stars: target 2,000 by Q3" **with:**
>
> GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:
>
> - Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
> - Watchers (who receive release news): `<current watchers>`
> - Dependents ("Used by") 770 (up from 290 in January) and npm downloads 96k a week (up from 41k)
> - Q&A answered share and median time to answer, once Discussions has a month of history
>
> Stars stay on the sheet as a trailing signal: 1,205 (+65 this quarter).

Suggested speaker line: "Usage grew about 2.4 times since January while stars barely moved. People install pgnest; they don't visit the repo. We now measure what reflects adoption."

### Template 1: release body (one per release)

```markdown
## <one-line outcome a user gets, not the version number>

<two sentences: who should upgrade, and what changes for them>

### Breaking changes

- <change> - migrate with <link to migration guide>

### New

- <capability> (#<PR>) - thanks @<external contributor>

### Fixed

- <symptom the user saw> (#<issue>)

Install: `npm install <npm package>@<version>`
Questions: <link to the Q&A category>
```

Cut any section that is empty for that release.

### Template 2: announcement discussion

Paste this as the discussion body when you tick "Create a discussion for this release".

```markdown
**pgnest <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

### Template 3: start-here pinned post

```markdown
Welcome to pgnest Discussions.

- **Q&A** - usage questions, such as sizing pools on Kubernetes. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.
```

Don't promise a response target until the Answerer and backup have agreed to it.

## 5. Metrics

| Metric | Baseline today | Note |
|---|---|---|
| Unique visitors, top referrers | None yet | Archive starts Oct 30. Check that the npm page and docs appear as referrers. |
| Watchers | `<read from the sidebar>` | |
| Dependents | 770 | Over the next quarter, continuing the trend would mean about 910 (480 added in about 10 months, roughly 48 a month). This is my arithmetic, not a promise. |
| npm downloads | 96k a week | Continuing the trend would mean about 112k a quarter out. Treat as supporting evidence only. |
| Q&A answered share | None | Report after a month of history. |
| Median time to answer | None | GraphQL `answer.createdAt` minus `createdAt`. |
| Cloners | Diagnostic only | CI inflates them. |
| Stars | 1,205 | Trailing signal only, never a target. |

## 6. Open points

1. **Which "Q3"?** The target date decides how bad the star gap looks.
2. **Who is the Answerer, who is the backup, and what is the weekly hours ceiling?** Discussions is conditional on this.
3. **Does the CEO need a replacement number?** If so, use dependents on the trend-continuation basis above, with a target set after four weeks of baseline.
4. **Is "6-8 a week" the 60% slice, or all issues?** If it's all issues, the K8s share is about 4-5 a week and the load is lighter than I assumed.
5. **Check ahead of the meeting that the repo's package registry page links back to the repo.** If it doesn't, fix that first. It is the cheapest inflow fix, and the playbook points to `sdk-package-publishing` for it.