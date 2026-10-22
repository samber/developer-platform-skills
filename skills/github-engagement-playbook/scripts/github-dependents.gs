// =============================================================
// Port of capricorn86/happy-github-dependents to Google Apps Script.
// Adapted from samber/oss-kpi (MIT). Scrapes the public "Used by" page,
// which has no API: expect breakage when GitHub changes its HTML.
// =============================================================

const DEPENDENTS_SHEET_NAME = 'Github dependents';
const MAX_DURATION_MS = 20 * 60 * 1000;    // Workspace accounts get 30 min per run; free accounts 6 min, so lower this there
const PAGE_DELAY_MS = 2000;                 // be polite
const STALE_AFTER_MS = 365 * 24 * 60 * 60 * 1000; // 1 year

const DEPENDENTS_SHEET_HEADER = [
  'project','type','dependents',
  'stars','forks','last_seen_at',
];

function mainGithubDependents() {
  const start = Date.now();
  const runStart = new Date(start);
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const outSheet = ensureOutputSheet_(ss);

  let projects = getRepoList();
  // shuffle
  projects = projects
    .map(value => ({ value, sort: Math.random() }))
    .sort((a, b) => a.sort - b.sort)
    .map(({ value }) => value)

  const buffer = [];
  let timedOut = false;

  outer:
  for (const project of projects) {
    const types = ['REPOSITORY'];
    // const types = ['REPOSITORY', 'PACKAGE'];

    for (const type of types) {
      let nextUrl = `/${project}/network/dependents?dependent_type=${type}`;
      Logger.log(nextUrl);

      while (nextUrl) {
        if (Date.now() - start > MAX_DURATION_MS) { timedOut = true; break outer; }

        const html = ghBrowserRequestWithRetry(nextUrl);
        if (html == null) { break; }

        for (const d of getPageDependents_(html)) {
          if (!d.user || !d.repo || d.user === 'ghost') continue;
          const dependent = `${d.user}/${d.repo}`;
          buffer.push([
            project,
            type,
            dependent,
            d.stars,
            d.forks,
            runStart,
          ]);
        }
        nextUrl = getNextPageUrl_(html);
        if (nextUrl) Utilities.sleep(PAGE_DELAY_MS);
      }
    }
  }

  if (buffer.length) {
    const startRow = outSheet.getLastRow() + 1;
    outSheet.getRange(startRow, 1, buffer.length, DEPENDENTS_SHEET_HEADER.length).setValues(buffer);
  }
  Logger.log(`Appended ${buffer.length} rows. timedOut=${timedOut}`);
  dedup_();
}

// =================== dedup: keep latest, drop > 1y old ===================
function dedup_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(DEPENDENTS_SHEET_NAME);
  if (!sheet) return;
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  const data = sheet.getRange(2, 1, lastRow - 1, DEPENDENTS_SHEET_HEADER.length).getValues();
  const cutoff = Date.now() - STALE_AFTER_MS;

  // Composite key: (project, dependents_repository, dependents_package, dependent)
  // The two type columns are part of the key so REPOSITORY and PACKAGE rows
  // don't collapse into one.
  const latest = new Map();
  for (const row of data) {
    const ts = toMs_(row[DEPENDENTS_SHEET_HEADER.length-1]);
    if (isNaN(ts) || ts < cutoff) continue;
    const key = `${row[0]}|${row[1]}|${row[2]}`; // project|type|dependent
    const existing = latest.get(key);
    if (!existing || ts > toMs_(existing[DEPENDENTS_SHEET_HEADER.length-1])) latest.set(key, row);
  }

  const kept = [...latest.values()];
  const before = data.length;

  // Single rewrite
  sheet.getRange(2, 1, lastRow - 1, DEPENDENTS_SHEET_HEADER.length).clearContent();
  if (kept.length) sheet.getRange(2, 1, kept.length, DEPENDENTS_SHEET_HEADER.length).setValues(kept);

  Logger.log(`Dedup: ${before} → ${kept.length} (removed ${before - kept.length}).`);
}


// ---------- core ----------

function getNextPageUrl_(html) {
  // Mirror of: querySelectorAll(".paginate-container a") → text === "Next"
  const container = html.match(/<div[^>]*class="[^"]*paginate-container[^"]*"[^>]*>([\s\S]*?)<\/div>/);
  if (!container) return null;
  // Only <a> (active). Disabled "Next" is rendered as <button>, which we want to ignore.
  const m = container[1].match(/<a[^>]+href="([^"]+)"[^>]*>\s*Next\s*<\/a>/);
  if (!m) return null;
  let href = m[1].replace(/&amp;/g, '&');
  return href.replace('https://github.com', '');
}

function getPageDependents_(html) {
  const dependents = [];

  // Scope to #dependents (matches getElementById("dependents"))
  const scope = html.match(/<div[^>]*id="dependents"[\s\S]*$/);
  if (!scope) return dependents;
  const dependentsHtml = scope[0];

  // Iterate .Box-row blocks
  const rows = dependentsHtml.split(/<div[^>]*class="[^"]*Box-row[^"]*"[^>]*>/).slice(1);

  for (const row of rows) {
    const avatarUrl = matchOne_(row, /<img[^>]+src="([^"]+)"/i, '');

    // a[data-hovercard-type="user"] OR a[data-hovercard-type="organization"]
    const user = matchOne_(
      row,
      /<a[^>]+data-hovercard-type="(?:user|organization)"[^>]*>([^<]+)<\/a>/i,
      ''
    ).trim();

    const repo = matchOne_(
      row,
      /<a[^>]+data-hovercard-type="repository"[^>]*>([^<]+)<\/a>/i,
      ''
    ).trim();

    // octicon-star → parent textContent → strip commas → parseInt
    // Stars: anchor past </svg> so we don't grab digits from viewBox="0 0 16 16",
    // then lazy-match through &nbsp;, U+00A0, plain whitespace, or wrapper spans.
    const starsRaw = matchOne_(
      row,
      /octicon-star\b[\s\S]*?<\/svg>[\s\S]{0,200}?(\d[\d,]*)/i,
      '0'
    );
    const stars = parseInt(starsRaw.replace(/,/g, ''), 10) || 0;

    const forks = parseInt(
      matchOne_(row, /octicon-repo-forked\b[\s\S]*?<\/svg>[\s\S]{0,200}?(\d[\d,]*)/i, '0')
        .replace(/,/g, ''),
      10
    ) || 0;

    if (!user || !repo) continue; // skip empty/garbage rows
    dependents.push({ avatarUrl, user, repo, stars, forks });
  }

  return dependents;
}

// ---------- helpers ----------
function toMs_(v) { return v instanceof Date ? v.getTime() : new Date(v).getTime(); }

function ensureOutputSheet_(ss) {
  let s = ss.getSheetByName(DEPENDENTS_SHEET_NAME);
  if (!s) {
    s = ss.insertSheet(DEPENDENTS_SHEET_NAME);
    s.appendRow(DEPENDENTS_SHEET_HEADER);
    s.setFrozenRows(1);
  } else if (s.getLastRow() === 0) {
    s.appendRow(DEPENDENTS_SHEET_HEADER);
    s.setFrozenRows(1);
  }
  return s;
}

function matchOne_(s, re, fallback) {
  const m = s.match(re);
  return m ? m[1] : fallback;
}
