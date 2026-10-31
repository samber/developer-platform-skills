# GitHub traffic dashboard for Lanternfold: corrected plan and script

I haven't run any of this. I don't have your repo names, token or sheet. Three parts of your plan don't work as stated, so I changed them.

## What I changed

| Your plan | Problem | Fix |
|---|---|---|
| Pull history back to January from Insights | ❌ GitHub keeps only the last 14 days of views and clones. Insights and the API both show that window. Anything before it is gone unless something snapshotted it. | Start snapshotting now. Backfill January onward from sources that keep history (below). |
| Monthly cron | ❌ A monthly run would lose about half of each month (14-day window). | Run daily. The script upserts by (repo, date), so reruns are safe. |
| Read-only token hardcoded in the script | 🔐 A token in a script ends up in git history, backups and shell history. A "read-only" token also may not work: traffic endpoints need admin-level read on the repo. | Fine-grained PAT, repo-scoped to the 4 repos, `Administration: read` plus `Metadata: read`. Keep it in an env var or secrets manager, never in the file. Check the permission name in GitHub's token UI, because I haven't verified it against the current docs. |
| Clones = installs, headline adoption number | ⚠️ A clone is not an install. CI runs, bots, mirrors, forks and your own team all clone. Example apps inflate it further. Nobody installs an SDK by cloning it. | Use package-registry downloads as the headline. Show unique cloners as a secondary, labelled "repo interest". |

## Backfill from January

- **Stars and forks:** the API returns `starred_at` and `created_at`, so full history is recoverable.
- **Package downloads:** npm's range API goes back about 18 months. PyPI via pypistats gives about 180 days. Which language is the SDK in? I'll add the matching fetcher.
- **Releases:** per-asset download counts are cumulative, so snapshot those daily too.
- **Issues and PRs:** `created_at` gives a full history.

## Script

Python 3.11+. Install: `pip install requests gspread feedparser`.

Environment variables:
- `GITHUB_TOKEN`
- `GOOGLE_SA_JSON`: path to a Google service-account key file
- `SHEET_ID`: the sheet must be shared with the service account's email

```python
#!/usr/bin/env python3
"""Daily snapshot of GitHub traffic for Lanternfold repos into Google Sheets."""
import os
import sys
import requests
import gspread

REPOS = ["lanternfold/sdk", "lanternfold/example-1", "lanternfold/example-2", "lanternfold/example-3"]  # replace with real names
API = "https://api.github.com"
TIMEOUT_S = 30  # GitHub answers in well under 30 s; fail loudly rather than hang cron
TRAFFIC_HEADER = ["repo", "date", "views", "unique_views", "clones", "unique_clones"]
SNAPSHOT_HEADER = ["repo", "date", "stars", "forks", "open_issues", "release_downloads"]


def gh(path: str):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    r = requests.get(
        f"{API}{path}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        timeout=TIMEOUT_S,
    )
    r.raise_for_status()  # 403/404 on traffic = token lacks admin read; never swallow it
    return r.json()


def traffic_rows(repo: str) -> dict:
    """Merge 14 daily buckets of views and clones into one row per day."""
    rows: dict[str, dict] = {}
    for kind in ("views", "clones"):
        for b in gh(f"/repos/{repo}/traffic/{kind}?per=day")[kind]:
            day = b["timestamp"][:10]
            row = rows.setdefault(day, dict(views=0, unique_views=0, clones=0, unique_clones=0))
            row[kind] = b["count"]
            row["unique_" + kind] = b["uniques"]
    return rows


def snapshot_row(repo: str, today: str) -> list:
    info = gh(f"/repos/{repo}")
    downloads = sum(
        a["download_count"]
        for rel in gh(f"/repos/{repo}/releases?per_page=100")
        for a in rel["assets"]
    )
    return [repo, today, info["stargazers_count"], info["forks_count"], info["open_issues_count"], downloads]


def upsert(ws, header: list, key_cols: int, rows: list[list]):
    """Replace rows whose (repo, date) key exists, append the rest."""
    existing = ws.get_all_values()
    if not existing:
        ws.append_row(header)
        existing = [header]
    index = {tuple(r[:key_cols]): i + 1 for i, r in enumerate(existing) if i > 0}
    appends = []
    for row in rows:
        key = tuple(str(c) for c in row[:key_cols])
        if key in index:
            ws.update(f"A{index[key]}", [row])
        else:
            appends.append(row)
    if appends:
        ws.append_rows(appends)


def main():
    from datetime import date
    sheet = gspread.service_account(filename=os.environ["GOOGLE_SA_JSON"]).open_by_key(os.environ["SHEET_ID"])
    traffic_ws = sheet.worksheet("traffic")
    snap_ws = sheet.worksheet("snapshots")
    today = date.today().isoformat()
    traffic, snaps = [], []
    for repo in REPOS:
        for day, v in sorted(traffic_rows(repo).items()):
            traffic.append([repo, day, v["views"], v["unique_views"], v["clones"], v["unique_clones"]])
        snaps.append(snapshot_row(repo, today))
    upsert(traffic_ws, TRAFFIC_HEADER, 2, traffic)
    upsert(snap_ws, SNAPSHOT_HEADER, 2, snaps)


if __name__ == "__main__":
    main()
```

Create two worksheet tabs named `traffic` and `snapshots` before the first run.

Cron, daily at 06:10. This is a 2-line crontab with the secrets in a `chmod 600` env file:

```
10 6 * * * set -a; . /etc/lanternfold/dashboard.env; set +a; /usr/bin/python3 /opt/lanternfold/gh_traffic.py >> /var/log/gh_traffic.log 2>&1
```

A GitHub Actions scheduled workflow with repo secrets is easier. It needs no server and the token stays in the secrets store.

## Blog mentions

GitHub can't answer this. The referrers endpoint lists only the top 10 sites and covers visits to your repos, not articles that mention you. Options, cheapest first:

1. **Google Alerts** for `"Lanternfold"` and the SDK name, delivered as an RSS feed, polled daily into a `mentions` tab. It's free and catches blogs and news. It misses a lot, but it's a fine start.
2. **Search API** (Brave, Bing or SerpAPI), queried daily for the same terms with a date filter. It costs a little and gives better coverage.
3. **Hacker News Algolia API** (free) plus a Reddit search, as complements.

Feed poller to bolt on. It dedupes by URL and goes in the same script or a sibling:

```python
import feedparser

ALERT_FEEDS = ["https://www.google.com/alerts/feeds/<id>/<id>"]  # paste your Alert RSS URLs

def mention_rows(seen_urls: set[str]) -> list[list]:
    out = []
    for feed in ALERT_FEEDS:
        for e in feedparser.parse(feed).entries:
            if e.link not in seen_urls:
                out.append([e.get("published", ""), e.title, e.link])
                seen_urls.add(e.link)
    return out
```

Append the results to a `mentions` tab with columns `published, title, url`. Load existing URLs from column C first.

## Dashboard

In Looker Studio or the Sheets chart tools, use these panels:
- **Headline:** weekly package downloads. This is the adoption number.
- **Interest:** unique cloners and unique views per repo, weekly.
- **Growth:** stars and forks over time.
- **Mentions:** a count per week and a list of the newest links.

## What I need from you

1. The 4 repo names (`owner/name`).
2. The SDK's language and registry (npm, PyPI, crates, Go modules). Go has no download counts, so the headline there would be something like unique `go get` proxies, or just stars plus unique cloners.
3. Whether to run it as cron on a server or as GitHub Actions. I recommend Actions.
4. The exact launch date, for the backfill window.

Once I have those, I'll add the package-download fetcher and the January backfill for stars, forks and releases.