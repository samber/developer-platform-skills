// Shared helpers for the GitHub KPI sheet. Adapted from samber/oss-kpi (MIT).
//
// Configuration lives in Project Settings > Script properties, never in code,
// so the project can be shared or copied without leaking a token:
//   GITHUB_TOKENS   comma-separated personal access tokens (one is enough)
//   GITHUB_PROFILE  user or organization name used as a search query

const SHEET_LIST = 'List GitHub repositories';

function getConfig_(key) {
  const value = PropertiesService.getScriptProperties().getProperty(key);
  if (!value) {
    throw Error(`Missing script property ${key}: set it in Project Settings > Script properties`);
  }
  return value;
}

function getGithubTokens_() {
  return getConfig_('GITHUB_TOKENS').split(',').map((t) => t.trim()).filter(Boolean);
}

function getGithubProfile_() {
  return getConfig_('GITHUB_PROFILE');
}

// Repositories to track: sheet "List GitHub repositories", column A = owner, B = repo.
function getRepoList() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_LIST);
  if (!sheet) throw Error(`Missing sheet "${SHEET_LIST}"`);
  const values = sheet.getRange('A2:B').getValues();
  return values.filter((row) => row[0] && row[1]).map((row) => `${row[0]}/${row[1]}`);
}

// Date in the script's time zone, as YYYY-MM-DD, so every row of one run shares a key.
function todayIso_() {
  return Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
}

// Appends rows to a sheet, creating it with a frozen header row when absent.
function appendRowsToSheet(sheetName, rows, header) {
  if (!rows.length) return;
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    if (header) {
      sheet.appendRow(header);
      sheet.setFrozenRows(1);
    }
  }
  sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, rows[0].length).setValues(rows);
}

// Throws once at the end of a run listing every repository that failed, after the
// successful rows are written: one broken repository must not hide the others,
// and a silent blank row must never read as a zero.
function throwIfFailures_(failures) {
  if (failures.length) {
    throw Error(`Failed for ${failures.length} item(s):\n${failures.join('\n')}`);
  }
}
