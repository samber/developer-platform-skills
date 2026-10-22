// Weekly repository stats and traffic archive. Adapted from samber/oss-kpi (MIT).
// GitHub keeps traffic for 14 days only: run weekly so no day is lost.

const SHEET_STATS = 'Github repositories';
const SHEET_REFERRERS = 'Github referrers';
const SHEET_PATHS = 'Github popular paths';
// Last 7 daily buckets of the 14 GitHub returns: one weekly run covers one week.
const DAYS_PER_RUN = 7;

const STATS_HEADER = [
  'repository', 'date', 'watchers', 'forks', 'stars', 'open_issues',
  'views_14d', 'unique_views_14d', 'clones_14d', 'unique_clones_14d',
  'views_7d', 'unique_views_7d', 'clones_7d', 'unique_clones_7d',
];
const REFERRERS_HEADER = ['repository', 'date', 'referrer', 'views_14d', 'unique_views_14d'];
const PATHS_HEADER = ['repository', 'date', 'path', 'title', 'views_14d', 'unique_views_14d'];

function sumLast_(items, field) {
  return items.slice(-DAYS_PER_RUN).reduce((acc, cur) => acc + cur[field], 0);
}

function mainGithubRepositories() {
  const date = todayIso_();
  const stats = [];
  const referrers = [];
  const paths = [];
  const failures = [];

  for (const repo of getRepoList()) {
    const base = ghRequestWithRetry(`/repos/${repo}`);
    const views = ghRequestWithRetry(`/repos/${repo}/traffic/views`);
    const clones = ghRequestWithRetry(`/repos/${repo}/traffic/clones`);
    const refs = ghRequestWithRetry(`/repos/${repo}/traffic/popular/referrers`);
    const popular = ghRequestWithRetry(`/repos/${repo}/traffic/popular/paths`);

    if (!base || !views || !clones || !refs || !popular) {
      failures.push(`${repo}: check the token has push access on it`);
      continue;
    }

    stats.push([
      repo, date,
      base.subscribers_count, base.forks_count, base.stargazers_count, base.open_issues_count,
      views.count, views.uniques, clones.count, clones.uniques,
      sumLast_(views.views || [], 'count'), sumLast_(views.views || [], 'uniques'),
      sumLast_(clones.clones || [], 'count'), sumLast_(clones.clones || [], 'uniques'),
    ]);
    for (const r of refs) referrers.push([repo, date, r.referrer, r.count, r.uniques]);
    for (const p of popular) paths.push([repo, date, p.path, p.title, p.count, p.uniques]);
  }

  appendRowsToSheet(SHEET_STATS, stats, STATS_HEADER);
  appendRowsToSheet(SHEET_REFERRERS, referrers, REFERRERS_HEADER);
  appendRowsToSheet(SHEET_PATHS, paths, PATHS_HEADER);
  throwIfFailures_(failures);
}
