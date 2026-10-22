// Weekly count of GitHub-wide mentions of the profile and each repository.
// Adapted from samber/oss-kpi (MIT).

const SHEET_SEARCH_STATS = 'Github search stats';
// Search allows about 30 requests a minute; 2.5 s between calls stays under it.
const SEARCH_DELAY_MS = 2500;

const SEARCH_HEADER = [
  'query', 'date', 'code_unreliable', 'repositories',
  'issues', 'issues_open', 'issues_closed',
  'pull_requests', 'pull_requests_open', 'pull_requests_closed',
  'discussions', 'users', 'commits', 'topics',
];

function ghDiscussionCount_(query) {
  const body = {
    query: 'query($q:String!){ search(query:$q, type:DISCUSSION){ discussionCount } }',
    variables: { q: query },
  };
  return ghGraphqlRequestWithRetry(body).data.search.discussionCount;
}

// Returns the counts, or null when any search call failed.
function ghSearchCounts_(query) {
  const enc = encodeURIComponent;
  const searches = [
    // The code counter returns inconsistent totals: github/rest-api-description#2956.
    ['code', `/search/code?q=${enc(query)}&per_page=1`],
    ['repositories', `/search/repositories?q=${enc(query)}&per_page=1`],
    ['issues', `/search/issues?q=${enc(query + ' is:issue')}&per_page=1`],
    ['issues_open', `/search/issues?q=${enc(query + ' is:issue is:open')}&per_page=1`],
    ['issues_closed', `/search/issues?q=${enc(query + ' is:issue is:closed')}&per_page=1`],
    ['pull_requests', `/search/issues?q=${enc(query + ' is:pr')}&per_page=1`],
    ['pull_requests_open', `/search/issues?q=${enc(query + ' is:pr is:open')}&per_page=1`],
    ['pull_requests_closed', `/search/issues?q=${enc(query + ' is:pr is:closed')}&per_page=1`],
    ['users', `/search/users?q=${enc(query)}&per_page=1`],
    ['commits', `/search/commits?q=${enc(query)}&per_page=1`],
    ['topics', `/search/topics?q=${enc(query)}&per_page=1`],
  ];

  const out = {};
  for (const [name, path] of searches) {
    Utilities.sleep(SEARCH_DELAY_MS);
    const result = ghRequestWithRetry(path);
    if (!result) return null;
    out[name] = result.total_count;
  }
  out.discussions = ghDiscussionCount_(query);
  return out;
}

function mainGithubSearch() {
  const date = todayIso_();
  const rows = [];
  const failures = [];

  for (const q of [getGithubProfile_()].concat(getRepoList())) {
    const r = ghSearchCounts_(q);
    if (!r) {
      failures.push(q);
      continue;
    }
    rows.push([
      q, date, r.code, r.repositories,
      r.issues, r.issues_open, r.issues_closed,
      r.pull_requests, r.pull_requests_open, r.pull_requests_closed,
      r.discussions, r.users, r.commits, r.topics,
    ]);
  }

  appendRowsToSheet(SHEET_SEARCH_STATS, rows, SEARCH_HEADER);
  throwIfFailures_(failures);
}
