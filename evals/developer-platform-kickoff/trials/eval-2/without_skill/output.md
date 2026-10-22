**I couldn't investigate the cause, because I have no data on the three partners.** `developer-platform-context.md` isn't at the repo root. `git log --all` shows no history for it on any branch, so it was never committed here. This checkout (`example-repo`) is a marketing and affiliation repo with no API or webhook code. I'm working only from your summary of the context file. Nothing below comes from logs, code or partner records.

## Next action (about 30 min)

Pull per-partner request counts from the API gateway or access logs, for each of the three partners and for 10 partners who kept calling:

- **Window:** 8 weeks, daily buckets, grouped by status code and partner credential.
- **Question:** was the drop a cliff, a ramp, or a switch from 2xx to 4xx or 5xx before the traffic stopped?

That one chart rules out most of the hypotheses below.

## Ranked hypotheses

"Silently" means no ticket and no complaint. Partners who hit a loud failure usually complain, so quiet churn points to one of four causes.

| # | Hypothesis | What you'd see | Check |
|---|---|---|---|
| 1 | **Auth or credential expiry or rotation.** Keys or tokens expired or were revoked, and the partner's client swallowed the 401 or 403. This is the likeliest cause given the OAuth question is still open. | Cliff in 2xx, then a burst of 401/403, then nothing. Dates match key age or a rotation job. | Group by credential. Compare key creation and expiry dates and any rotation or SOC 2 hygiene job (forced rotation, key purge). |
| 2 | **A breaking change that slipped past the compatibility promise.** A response shape, enum value, pagination default, rate limit or error code changed. The partner's parser failed and they stopped calling. | Traffic falls right after a deploy. 2xx stays but follow-up calls stop, or 4xx rises on a specific endpoint. | Diff the REST v1 OpenAPI spec and the webhook payload schemas against last month's release. Check with Priya, the contract owner, for any unrecorded change. The VP Eng signs breaking changes, so a missing sign-off means it was never treated as breaking. |
| 3 | **Webhook delivery failure that auto-disabled the subscription.** Retries were exhausted and the endpoint was disabled, so the partner got no events and made no follow-up API calls. | Webhook delivery log shows repeated failures, then "disabled". API calls fall afterwards. | Query the delivery and retry table for the three partners. Check for auto-disable thresholds, TLS or cert changes on their side, and IP allowlist changes on yours. |
| 4 | **Partner-side cause.** They migrated, churned, or were rate-limited into giving up. | Gradual ramp-down. 429s before the stop. No matching change on your side. | Check for 429s. Look at the account status in your CRM. Ask their technical contact directly. |

Check 1 and 3 first. They are the cheapest to confirm and the likeliest to be silent.

## Common-factor check

Compare the three partners against the ones still calling:

- credential type and age
- signup date
- integration language or SDK
- which endpoints they use
- whether they subscribe to webhooks
- webhook endpoint hosting

Whatever the three share and the others don't is the lead. If they share nothing, lean toward hypothesis 4.

## Fix, once the cause is confirmed

Don't ship a fix before the chart and common-factor check point to one cause. Then:

- **Hypothesis 2:** treat it as a breaking-change incident. Revert, or get the VP Eng sign-off and notify partners.
- **Hypotheses 1 and 3:** the structural gap is that nobody learns when a partner goes quiet. Add a "no calls for N days" alert per partner and an expiry warning email 30 days before key expiry. Both are small enough for a few hours a week and one engineer.
- **OAuth:** if hypothesis 1 holds, record it as evidence in the OAuth decision. Don't let it settle that decision on its own.
- **SOC 2 (March window):** any key purge or rotation job that caused this needs a documented partner-notification step. Auditors will want that evidence.

## What I need from you

1. The real path or repo of `developer-platform-context.md`, or paste it.
2. Access to the gateway logs or webhook delivery table. I can run the analysis if you point me at the system, or you can run the query above and paste the results.