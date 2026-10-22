# Tracking tools

Contents:

1. Ranked tools
2. GitHub KPI sheet (bundled Apps Script)
3. Google Alerts
4. OSS Insight

## 1. Ranked tools

- effort (highest first): `KPI sheet > Google Alerts == OSS Insight`
- value: `KPI sheet > OSS Insight > Google Alerts`

The tie is real: Alerts and OSS Insight each take minutes once, then cost nothing. Start with the KPI sheet, because GitHub deletes traffic after 14 days and nothing recovers it.

| Tool          | Measures                                                                                                                 | Cost                       |
| ------------- | ------------------------------------------------------------------------------------------------------------------------ | -------------------------- |
| KPI sheet     | Stars, watchers, forks, views, clones, referrers, popular pages, GitHub-wide mentions, dependents, as weekly time series | An hour once, then nothing |
| Google Alerts | New web pages mentioning the project                                                                                     | Minutes once               |
| OSS Insight   | Star and contributor history, issue and PR trends, stargazer geography and companies, repo comparison                    | None                       |

## 2. GitHub KPI sheet (bundled Apps Script)

`scripts/` holds Google Apps Script files that append one dated row per repository on every run. The sheet becomes a time series you can chart.

| File                          | Entry point              | Writes to                                                         |
| ----------------------------- | ------------------------ | ----------------------------------------------------------------- |
| `github-repositories.gs`      | `mainGithubRepositories` | `Github repositories`, `Github referrers`, `Github popular paths` |
| `github-search.gs`            | `mainGithubSearch`       | `Github search stats`                                             |
| `github-dependents.gs`        | `mainGithubDependents`   | `Github dependents`                                               |
| `utils.gs`, `github-utils.gs` | helpers                  | -                                                                 |

Setup:

1. Create a Google Spreadsheet with a sheet named `List GitHub repositories`: column A owner, column B repository, from row 2.
2. Open **Extensions > Apps Script**. Create one script file per `.gs` file and paste each file's content.
3. In **Project Settings > Script properties**, add `GITHUB_TOKENS` (one or more personal access tokens, comma-separated) and `GITHUB_PROFILE` (the user or organization name). Never paste a token into the code.
4. Give each token push access on every tracked repository: the traffic endpoints refuse anything less. Classic token: `repo` scope. Fine-grained token: Administration read on each repository.
5. Run `mainGithubRepositories` once by hand and approve the permissions prompt. Output sheets are created on first run.
6. In **Triggers**, add a weekly time-driven trigger for each entry point.

A run that fails for any repository still writes the others, then raises an error naming the failed ones; Apps Script emails the owner. The `code_unreliable` search column returns inconsistent totals on GitHub's side, so chart the other columns. The dependents script reads the public "Used by" page, which has no API, and breaks when GitHub changes that page's HTML.

## 3. Google Alerts

Create an alert at google.com/alerts for each name a stranger would write: `"<project>"`, `"<owner>/<repo>"`, and the package name when it differs. Set "How often" to once a week and "How many" to all results. Alerts catch blog posts, tutorials and forum threads that never link back, and therefore never show in GitHub's referrers.

## 4. OSS Insight

ossinsight.io builds dashboards for any public repository from the GitHub event archive, with no setup. Use it for what the GitHub API does not keep:

- Star history since creation, and stars per month, to date a spike against a release or a post.
- Issue and PR open and close trends, and median time to first response.
- Stargazer and contributor geography and self-reported companies, in aggregate.
- Side-by-side comparison with a competing repository.

Its numbers come from public events, so they can differ slightly from the repository's own counters. Quote the GitHub figure when the two disagree.
