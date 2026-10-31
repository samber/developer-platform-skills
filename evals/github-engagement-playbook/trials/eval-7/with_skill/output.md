# GitHub traffic dashboard for Lanternfold

Four of your assumptions need changing before you build this. Do step 1 of the setup today, because each day without an archive is lost for good.

## 1. What breaks in the plan

| Your assumption | Reality | Fix |
|---|---|---|
| "I can pull history back to January from Insights" | Traffic (views, clones, referrers, paths) keeps **14 days only**, shows the top 10 referrers and paths, and needs push access [documented]. Anything before about mid-October is gone. | Start the archive today. Backfill only what other sources keep (see § 2). |
| Monthly cron | A monthly run sees at most 14 of about 30 days, so it **loses about half of every month**. | Run it **weekly**. The bundled script stores the last 7 daily buckets per run. |
| Hardcoded read-only token | A token in script code leaks through a copy, a share or a commit. Traffic endpoints also refuse read-only tokens that lack push access. | Store the token as an Apps Script property, never in code. Use a fine-grained token with Administration read on the 4 repos, or a classic `repo` token if the fine-grained one is refused. Set an expiry and put the renewal in a calendar. |
| Clones = installs, so clones are the headline "adoption" number | Clones count git clones, and CI runs and bots inflate them. Package installs mostly never touch GitHub. | Keep cloners as a diagnostic only. Report registry downloads, dependents and unique visitors (template 8 below). |

Leaving the token out of the code also removes the leak risk. Apps Script's weekly trigger replaces your cron job and needs no server.

## 2. Diagnosis row (§ 1 of the playbook)

I have no numbers from your repos, so I can't fill in the evidence yet. Your clones-as-adoption framing matches this row of the playbook table:

> **Downloads or dependents grow, stars flat → users install from the registry. First action: change the reported metric (template 8) and stop chasing stars.**

Confirm or reject it with the first export, using trends against the same window a quarter earlier. No absolute threshold exists. If visitors are flat and the registry page is missing from the referrers, the problem is inflow rather than metrics. In that case fix the registry-to-repo link, then work off-platform via `samber/developer-relations-skills@oss-distribution-strategy`.

**What you can still backfill to January:**
- **Stars over time:** OSS Insight (ossinsight.io) rebuilds this from the public event archive, with no setup. Its numbers can differ slightly from GitHub's own, so quote GitHub's figure when they disagree.
- **Issue and PR trends, contributors:** also from OSS Insight.
- **Registry downloads:** depends on your registry. Check how far back it keeps daily history before promising a January start. The first-party stats of npm, PyPI and similar registries differ here.
- **Release dates:** the repos' Releases pages. Mark the January launch on every chart.

**What cannot be recovered:** views, clones, referrers and popular paths before the archive starts. Show the dashboard as "since <archive start date>", with the stars and downloads series reaching back to January.

## 3. Setup (about 1 hour)

Uses the bundled Apps Script files in `scripts/` of the skill.

1. **Today:** create a Google Spreadsheet with a sheet named `List GitHub repositories`. Put the owner in column A and the repo name in column B, from row 2, one row per repo (SDK plus the three example apps).
2. **Extensions > Apps Script:** create one file per `.gs` file (`github-repositories.gs`, `github-search.gs`, `github-dependents.gs`, `github-utils.gs`, `utils.gs`) and paste each file's content.
3. **Project Settings > Script properties:** add `GITHUB_TOKENS` (the token, or several comma-separated) and `GITHUB_PROFILE` (`<Lanternfold GitHub org name>`). The token goes here and nowhere else.
4. Check that the token has push access on **all 4 repos**. One missing repo fails only that repo, and the run then raises an error naming it.
5. Run `mainGithubRepositories` once by hand and approve the permissions prompt. Check that three sheets appeared: `Github repositories`, `Github referrers` and `Github popular paths`.
6. **Triggers:** add a **weekly** time-driven trigger for `mainGithubRepositories`, `mainGithubSearch` and `mainGithubDependents`.
7. Chart from the `Github repositories` sheet. Use these columns:
   - `unique_views_7d`
   - `stars`
   - `watchers`
   - `forks`
   - `open_issues`
   - `unique_clones_7d` (diagnostic panel only)

   Skip the `code_unreliable` column from the search sheet: GitHub returns inconsistent totals for it.
8. Add a column or sheet for **registry downloads** by hand or script, once you tell me which registry you ship on.

**Known limits:**
- A failed repo is never written as a blank row, so a gap means "failed", not "zero".
- The dependents script reads GitHub's public "Used by" page, which has no API, so it breaks if GitHub changes that page.
- The `GITHUB_PROFILE` search column counts GitHub-wide mentions in code, not blog posts.

## 4. Blog and press mentions

GitHub referrers will not show these. Posts that never link back never appear there, and the referrer list is capped at the top 10.

1. Create Google Alerts at google.com/alerts for each name a stranger would write: `"Lanternfold"`, `"<owner>/<sdk repo>"` and `"<package name>"` if it differs. Set "How often" to once a week and "How many" to all results.
2. Log hits in a `Mentions` sheet with date, URL, author or outlet, and whether it links to the repo.
3. Read the `Github referrers` sheet each month for the links that do come through.

## 5. Ranked surfaces and re-rank

Order is efficiency (value per maintainer hour). No interview answers were given, so this is the default order.

1. **Traffic archive and metric swap** [documented: 14-day retention]. Near-zero effort and compounding. This is what you are building.
2. **Small, frequent releases as feed events.** Ship each merged fix as its own Release with a written body, and tick "Create a discussion for this release". It notifies release watchers and shows in stargazers' and watchers' feeds [documented].
3. **Topics.** 5-10 accurate topics on each repo [documented: 20 max, lowercase letters, digits and hyphens].
4. **Discussions Q&A.** Highest value but a standing cost. Promote it to rung 2 only if usage questions already arrive as issues **and** someone is named as public answerer with a backup. Skip it if nobody answers publicly, because an unanswered tab reads as abandonment.

Re-rank once you answer the open interview items:
- If a date falls inside two months, rungs 1-3 move up and Discussions carries no deadline metric.
- If this is a one-off win, the list cuts to rungs 1-2.

## 6. Cadence

| When | What | Owner |
|---|---|---|
| Today | Create the sheet, token and weekly triggers. Set the Google Alerts. | Head of DevRel |
| Weeks 1-2 | Check the first 2 runs. Read OSS Insight for stars since January. Set topics. Back-fill bodies on the last 3 releases. | DevRel engineer |
| Weeks 2-4 | Open Discussions (Announcements and Q&A) if an answerer exists. Add a `contact_links` entry in `.github/ISSUE_TEMPLATE/config.yml`. Turn on Dependabot. | DevRel engineer |
| Every release | Release body, the auto-created Announcement, then an off-platform post. | Release owner |
| Weekly | Check the run succeeded, merge Dependabot PRs, answer Q&A if open. | DevRel engineer |
| Quarterly | Read watchers, dependents, downloads and referrers against the baseline. Revise topics. | Head of DevRel |

Add the landing date once you have it; I left it open rather than invent one.

## 7. Filled templates

**Template 8: leadership metric note** (fill the angle brackets from the first export)

> GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:
>
> - Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
> - Watchers (who receive release news)
> - Dependents ("Used by") and `<registry>` downloads
> - Q&A answered share and median time to answer, once Discussions has a month of history
>
> Stars stay on the sheet as a trailing signal: `<current>` (`<change>` this quarter).
>
> Clones are tracked but not reported as adoption: CI and bots inflate them.

**Template 1: release body**

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

**Template 2: announcement discussion**

```markdown
**Lanternfold <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

Tick "Create a discussion for this release" on the release form and paste this as the discussion body.

**Template 3: start-here pinned post** (only if Discussions opens)

```markdown
Welcome to Lanternfold Discussions.

- **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.
```

## 8. Metrics on the dashboard

**Headline:** unique visitors, top referrers, watchers, dependents, registry downloads.

**Once Discussions has a month of history:** Q&A answered share, and median time to answer (GraphQL `answer.createdAt` minus `createdAt`).

**Diagnostic only:** unique cloners. Stars are a trailing signal and never a target. Never buy, trade or reward stars: GitHub's Acceptable Use Policies ban rank abuse, and the StarScout study (He et al., ICSE 2026) found fake stars faded within two months, then became a liability.

## 9. What I need from you

1. Which registry do you ship on (npm, PyPI, Go proxy, other)? This sets the downloads source and how far back it reaches.
2. Do you have push or admin access on all 4 repos, and does the org allow fine-grained tokens?
3. Who answers questions publicly, and with what backup? This decides whether Discussions opens.
4. By what date must leadership see the result?

I have not run anything against your repos or accounts. The first real step is yours: create the sheet and token today.