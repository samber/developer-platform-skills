// GitHub API and page helpers. Adapted from samber/oss-kpi (MIT).
//
// Token permissions: traffic endpoints need push access on each repository.
// Classic PAT: `repo` scope. Fine-grained PAT: Administration read on each repository.

const GITHUB_API = 'https://api.github.com';
const GITHUB_API_VERSION = '2022-11-28';
// Pause between token attempts: a secondary rate limit clears faster when calls are spaced.
const TOKEN_RETRY_DELAY_MS = 1000;

// Tries each token in turn. Returns the parsed body on 2xx, null when every token failed.
function ghRequestWithRetry(path, headers) {
  for (const token of getGithubTokens_()) {
    try {
      const [status, result] = ghRequest_(path, token, headers || {});
      if (status >= 200 && status < 300) return result;
      Logger.log(`HTTP ${status} on ${path}: ${JSON.stringify(result).slice(0, 200)}`);
    } catch (err) {
      Logger.log(`Error on ${path}: ${err}`);
    }
    Utilities.sleep(TOKEN_RETRY_DELAY_MS);
  }
  return null;
}

function ghRequest_(path, token, headers) {
  const response = UrlFetchApp.fetch(GITHUB_API + path, {
    headers: Object.assign({
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': GITHUB_API_VERSION,
    }, headers),
    muteHttpExceptions: true,
    followRedirects: true,
  });
  return [response.getResponseCode(), JSON.parse(response.getContentText() || 'null')];
}

function ghGraphqlRequestWithRetry(body) {
  for (const token of getGithubTokens_()) {
    try {
      const res = UrlFetchApp.fetch(GITHUB_API + '/graphql', {
        method: 'post',
        contentType: 'application/json',
        headers: { Authorization: 'Bearer ' + token },
        payload: JSON.stringify(body),
        muteHttpExceptions: true,
      });
      const result = JSON.parse(res.getContentText() || 'null');
      if (res.getResponseCode() === 200 && result && !result.errors) return result;
      Logger.log(`GraphQL HTTP ${res.getResponseCode()}: ${res.getContentText().slice(0, 200)}`);
    } catch (err) {
      Logger.log(`GraphQL error: ${err}`);
    }
    Utilities.sleep(TOKEN_RETRY_DELAY_MS);
  }
  throw Error('Could not fetch GitHub GraphQL data');
}

// Fetches a public github.com page (the dependents graph has no API).
function ghBrowserRequestWithRetry(url) {
  // Three attempts, two seconds apart: the dependents page often returns a transient 429 or 5xx.
  for (let i = 0; i < 3; i++) {
    const res = UrlFetchApp.fetch(`https://github.com${url}`, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; AppsScript github-dependents)',
        Accept: 'text/html',
      },
      muteHttpExceptions: true,
      followRedirects: true,
    });
    if (res.getResponseCode() === 200) return res.getContentText();
    Logger.log(`HTTP ${res.getResponseCode()} on ${url}, retrying in 2s`);
    Utilities.sleep(2000);
  }
  return null;
}
