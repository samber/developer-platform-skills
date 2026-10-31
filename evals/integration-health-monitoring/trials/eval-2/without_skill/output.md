# Sanity check: the 92% isn't the number you need

**Verdict:** don't announce on 92%. It measures the wrong thing, so it doesn't tell you how many customers retiring 2024-06-01 will break.

## Why 92% doesn't answer the question

1. **Default version isn't the version in use.** `default_version` only applies when a request names no version. Per-request or SDK-pinned versions and per-endpoint webhook versions override it, so an account with a 2025 default can still send traffic on 2024-06-01.
2. **The SDKs hide old pins.** If the Java, Go or Node SDK pins a version at release time, customers on old SDK builds call 2024-06-01 whatever their account says. Upgrading the account default won't change that.
3. **Webhooks are versioned separately.** An endpoint registered on 2024-06-01 keeps receiving that payload shape. Account tables won't show it.
4. **The cutoff tests the wrong thing.** `>= 2025-03-01` says nothing about 2024-06-01. The other 8% may be on 2024-09-01 or 2025-01-01, which you aren't retiring. You need `= 2024-06-01`, plus whatever else sits below your supported floor.
5. **The 92% is probably flattered by new accounts.** Signup defaults to the latest version, so recent signups inflate it. Long-tenured accounts, which are the ones with old integrations, are diluted.
6. **"Active" is undefined and the count is unweighted.** Define active by API calls in the last N days, not logins. One enterprise account on 2024-06-01 counts the same as a dormant trial, so also weight by request volume and revenue.
7. **Small checks on the query itself.** Check how NULL or legacy defaults are handled. Check that the date comparison is on a real date type or ISO string. Check that sub-accounts and multiple API keys aren't double-counted or missed.

## The report to build: effective version in use

Source it from API gateway request logs and webhook delivery logs, not the accounts table. The key field is the effective version each request or delivery was served under, plus how that version was chosen: `header`, `sdk_pin`, `account_default` or `endpoint_config`.

**Window:** 90 days at minimum, so quarterly batch jobs and seasonal peaks show up. Long-tail customers on monthly or quarterly jobs are the ones who get hurt.

**Cuts to include:**

| Cut | Why |
|---|---|
| Distinct accounts with ≥1 request on 2024-06-01 | The real "affected" count |
| Same, split by resolution source | Tells you whether the fix is an account setting, an SDK upgrade, or a code change |
| Request volume and revenue share on 2024-06-01 | Weights the big accounts properly |
| By SDK language and SDK version (from user-agent) | Shows who needs an SDK upgrade and which release to point them at |
| Webhook endpoints registered on 2024-06-01, with last delivery date | Customers can't fix these by changing a header |
| Per account: last-seen date on 2024-06-01, weekly trend | Separates dead integrations from live ones, and shows whether migration is moving |
| Top 50 affected accounts with owner and contact | You need to reach them directly |
| Calls with no identifiable account or SDK (raw HTTP) | Hardest cohort to notify |

**SQL sketch** (table and column names are assumptions; adapt to your schema):

```sql
SELECT account_id,
       resolution_source,         -- header | sdk_pin | account_default | endpoint_config
       sdk_language, sdk_version,
       COUNT(*)            AS requests_90d,
       MAX(request_date)   AS last_seen
FROM   api_request_log
WHERE  effective_version = '2024-06-01'
  AND  request_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP  BY 1, 2, 3, 4;
```

Run the same query against the webhook delivery log, grouped by endpoint.

## Check first: does your gateway log the effective version?

- **If it does:** you can run the report today.
- **If it logs only the header the client sent:** you'll miss every request that fell back to the account default or an SDK pin. Add effective-version logging now and let it collect for a few weeks. This is the likely blocker.
- **If webhook deliveries don't log the endpoint's version:** join to endpoint config instead.

## Announce once

- You have a named list of affected accounts and endpoints, with owners.
- Usage on 2024-06-01 is falling week over week, or you have a plan for the large accounts still on it.
- The migration guide, SDK upgrade versions and a sunset date are ready.
- You've decided what happens at cutoff: hard-fail, or auto-upgrade to the nearest supported version. This affects how loud the notice needs to be.

## Questions for you

1. Does the gateway log the version that was actually served?
2. Do the three SDKs pin a version at release, or read it from the account default?
3. Which versions below 2025-03-01 stay supported after 2024-06-01 is retired?