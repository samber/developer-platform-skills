# Change plan: free-tier rate limit and `X-RateLimit-Reset`

I did not check your docs, ToS or SLAs, and I read nothing under `skill-wip/`. Step 1 below closes that gap.

## Verdict

Your platform lead and your colleague are each half right. This is three separate changes, and only one of them needs a version bump.

| Change | Breaking? | Ship as |
|---|---|---|
| Stop abuse now | No | Tonight, using existing ToS rights |
| 1,000 → 300 req/hr | Yes for legitimate clients near the limit, but it is a policy change, not a schema change | Notice period (60–90 days), not API v2 |
| `X-RateLimit-Reset` epoch → seconds-remaining | Yes, definitely | New header added in v1, new semantics only in v2 |

## Why

- **Abuse is the urgent problem, and 18 months of deprecation doesn't solve it.** A v2 with an 18-month window leaves 1,000/hr in force for abusers for 18 months. Tonight's flip is also risky. A client legitimately using 800/hr gets 429s with no warning, and in fintech that can mean failed payments or reconciliations.
- **The limit is a contract term only if you documented it as one.** If the docs or ToS say "1,000 requests/hour" as a guarantee, cutting it needs notice. If they say "up to" or "subject to change", you have more room. Notice still matters either way, but 18 months and a new API version are not required. Sunset headers (RFC 8594) are for retiring a resource, not for changing a quota.
- **The reset header change is the real break.** Clients parse the value as an epoch timestamp. Given `37`, they read 1970 as the reset time, decide the window has already reset, and retry immediately. That is a retry storm against your own capacity problem.

## Plan

### 1. Today (Sat 2026-10-03): decide and contain

1. Check what the public docs, ToS and any partner or SLA contracts say about the free-tier limit. Record the exact wording.
2. Pull 7 days of per-key usage. Find who is abusing it and who is legitimately above 300/hr.
3. Suspend or throttle the clearly abusive keys tonight, using the ToS abuse clause. This needs no contract change.
4. Add controls aimed at abuse, not at everyone:
   - Per-IP and per-ASN limits on key creation.
   - Burst limits per minute.
   - Anomaly throttling per key.
   - Email or phone verification on new free signups.

**Gate:** if step 2 shows fewer than a handful of legitimate keys above 300/hr, the 90-day notice can shrink to 30 days. Legal and compliance should confirm that.

### 2. Limit change: policy rollout, no v2

| Date | Action |
|---|---|
| Mon 2026-10-05 | Email every free-tier key owner. Publish a changelog entry and a docs banner. State the old limit, the new limit, the effective dates and the reason. Offer a paid-tier or limit-increase path. |
| Mon 2026-10-05 | New signups get 300/hr immediately. Nobody has an existing expectation to protect. |
| Tue 2026-11-03 | Existing keys step down to 600/hr. Send a reminder to keys that exceeded 300/hr in the last 14 days. |
| Tue 2027-01-05 | Existing keys step down to 300/hr. This is day 92 after notice. |

Notes:
- The step-down is stepped on purpose: it surfaces the clients that will break while there is still time to talk to them.
- Allow case-by-case exceptions for legitimate high-volume free users, as an allowlist with an expiry date.
- Send responses a header on every call during the window, such as `X-RateLimit-Policy-Notice: 300/hour effective 2027-01-05; see <docs url>`. Don't use `Sunset` for this.
- Rollback: the limit lives in config, not code. Keep a one-line revert and a named owner who can run it.

### 3. Reset header: additive now, semantic change only in v2

1. **Now, in v1:** keep `X-RateLimit-Reset` as epoch seconds, unchanged. Add the IETF-style `RateLimit-Reset` header, which carries seconds remaining. Both are returned. This is non-breaking, so no deprecation clock starts.
2. Document both. Mark `X-RateLimit-Reset` as "epoch seconds, stable in v1".
3. **In v2, when you ship it for other reasons:** `X-RateLimit-Reset` is removed or redefined, and `RateLimit-Reset` is the only reset header. Only then do the standard 18-month deprecation, `Deprecation` and `Sunset` headers apply, and only to v1 as a whole.
4. Don't create v2 just for this header. The additive header gets the same benefit without forcing every client to migrate.

Tests:
- Contract test that v1 `X-RateLimit-Reset` is still a valid epoch.
- Contract test that `RateLimit-Reset` is an integer ≤ the window length.
- Check your own SDKs and the top integrations. Find which clients read the header.

### 4. Measure

- 429 rate per tier, split by new and existing keys.
- Count of distinct legitimate keys hitting 429s after each step.
- Support tickets tagged "rate limit".
- Total request volume and abuse-key volume, to confirm capacity actually recovers.
- Retry-storm check: requests per key in the 60 seconds after a 429.

### 5. Risks

- **Abusers rotate keys.** The signup and anomaly controls in step 1 matter more than the 300 number.
- **Partner or regulator expectations.** A fintech may owe notice under partner agreements. Legal should review the email before it goes out.
- **A silent flip tonight** is the highest-risk option. It also gives you no data on who breaks.

## Decisions needed from you

1. Do the docs or ToS promise the 1,000/hr figure? This sets the notice length.
2. Is there already another reason to ship v2? If yes, bundle the header change there. If no, stay additive.
3. Who owns the rollback and the exceptions list?