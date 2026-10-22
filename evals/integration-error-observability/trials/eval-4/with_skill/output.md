**Next action:** add `app_id` to the edge log line. Until that ships, run the join pipeline in section 2. Then replay last week through the new rules (section 7). If the broken app doesn't alert, the design is wrong.

Assumptions I could not check are marked ⚠️ and collected in the questions at the end.

## 1. Why the old number failed

| Symptom | Cause | Fix |
|---|---|---|
| Partner at 4.2% all week, one app at 100% | The rate is blended across apps. A fully broken app that carries about 4% of traffic caps the blend near 4.2%, under the 5% page. | Compute the rate per app, not per partner. |
| Biggest partner red after an 8x scale-up | 429s were counted as errors. A partner that scales successfully looked like a broken one. | Split 429 from 4xx and 5xx. Throttling gets its own signal and its own owner. |
| Page at a global 5% | One threshold for every traffic shape. | Compare each app to its own baseline, with a minimum-volume floor. |

## 2. Tag by app: interim join, then edge tag

**Permanent fix:** attach `app_id` at the edge when the request arrives. Retrofitting later leaves history unqueryable by app. Today's join is the retrofit case.

**Interim: join to the auth service logs.**

1. Make sure both logs carry the same `request_id`. Verify this first (question 1). Without a shared ID, the fallback join is `api_key_id` plus a time window, which is lossy.
2. Run the join as a streaming or micro-batch job, not a nightly one. Join latency is added directly to detection time. Target a lag under 2 minutes.
3. Keep the unmatched rows. Emit `app_id = 'unattributed'` and graph its share. A rising share means the join is broken, and that failure must not be silent.
4. Write the result into the same rollup table the edge tag will feed later. Then dropping the join is a config change.

Simplified join:

```sql
SELECT e.request_id, e.ts, e.status, e.error_code, e.endpoint,
       COALESCE(a.app_id, 'unattributed') AS app_id,
       a.partner_id, a.api_key_id
FROM edge_log e
LEFT JOIN auth_log a
  ON a.request_id = e.request_id
 AND a.ts BETWEEN e.ts - INTERVAL '5 seconds' AND e.ts + INTERVAL '5 seconds';
```

## 3. Aggregation schema

One row per (`partner_id`, `app_id`, `api_key_id`) per 1-minute bucket. Roll up to 5-minute, 1-hour and 24-hour windows from that.

| Field | Note |
|---|---|
| `partner_id`, `app_id`, `api_key_id` | `app_id` is the new dimension. |
| `window_start`, `window_end` | Explicit, so a rate is interpretable. |
| `n_total` | All calls. |
| `n_2xx_3xx` | Successes. |
| `n_4xx` | Excludes 429. |
| `n_5xx` | Ours. |
| `n_429` | Throttled. |
| `top_error_codes` | Ranked, top 5 per bucket. |
| `installs_affected`, `installs_total` | If a customer-account ID exists ⚠️. |
| `deploy_marker` | Our release IDs overlaid on the timeline. |

**Rate definitions.** Throttled calls never reached the handler, so they stay out of the denominator for the error rates.

```
admitted     = n_total - n_429
rate_4xx     = n_4xx / admitted     # integrator-side
rate_5xx     = n_5xx / admitted     # ours
throttle_rate = n_429 / n_total     # quota conversation
```

Never publish or alert on a blended number. The dashboard column that today reads "error rate, last 24h" becomes three columns.

**Separate signal: volume drop.** Compare `n_total` per app to the same hour-of-week over the prior 4 weeks. An app that stops calling produces no errors and appears in no error view.

## 4. Alert rules

Every rule runs per app. Thresholds are starting values I chose, not industry numbers (self-set). Tune them from your own baseline.

| # | Signal | Condition | Goes to | Channel |
|---|---|---|---|---|
| A1 | App hard-failing (4xx) | `rate_4xx ≥ 25%` in 15 min AND `n_4xx ≥ 20` | Partner team queue and the partner | Ticket plus partner alert. **Not** an on-call page. |
| A2 | App degraded (4xx), slow | `rate_4xx ≥ max(3× own 7-day baseline, 5%)` over 6 h AND `n_4xx ≥ 100` | Partner | Digest highlight |
| A3 | Our failure (5xx) | `rate_5xx ≥ 2%` in 5 min AND `n_5xx ≥ 20`, confirmed in 1 h | **Our on-call** | Page |
| A4 | Throttling | `throttle_rate ≥ 10%` in 15 min, or limit utilisation ≥ 80% | Partner and account manager | Quota conversation. Never a page. |
| A5 | Silent app | `n_total ≤ 10%` of baseline for 30 min, baseline volume ≥ 100/h | Partner team | Ticket |
| A6 | Join health | `unattributed` share > 2% | Our platform team | Page during the interim only |

**Why A1 is not a page.** A 4xx failure is usually the integrator's payload, auth or deleted object. Paging ourselves for it is what turned the channel noisy. But it must reach someone: the partner team queue, plus a direct partner alert, so the partner learns before their own customers do. That is the failure from last week.

**Why A1 and A2 differ.** A1 is a short window for a sudden break. A2 is a long window for slow creep. A design with only one misses half the failures (multiwindow burn-rate pattern, Google SRE Workbook).

**Volume floors.** The `n ≥ 20` and `n ≥ 100` conditions stop a 3-call app at 100% from paging anyone.

**Cooldown and recovery.**
- One alert per (`app_id`, signal) incident. Cooldown starts at 30 minutes, the Salesforce Agentforce default. Replace it with your typical incident duration once you have data.
- Send a recovery message when the rate returns to baseline.
- Escalate to the partner team lead if an A1 is unacknowledged after 4 h.
- Before sending any 5xx alert, check the deploy marker. A spike right after our release is our regression, and the message must say so.

**Partner alert template (A1):**

```
Alert: acme-payroll-sync (app) error rate 100% over last 15 min (baseline 0.3%)
Started 14:05 UTC, ongoing. 412 failed calls across 38 installs.
Top error: invalid_employee_id (97% of failures).
No platform release in this window; this pattern indicates a change on your side.
Failed requests: <log link filtered to this app>
Next alert for this app no earlier than 14:35 UTC.
```

## 5. Dashboards

**Partner view** (replaces the single number), one row per app:

| App | Calls 24h | 4xx rate | 5xx rate | Throttled | Top error | Trend vs baseline |
|---|---|---|---|---|---|---|

Also show the log link for each row. Scope access so a partner engineer who is not an account owner can see it (⚠️ question 5).

**Our fleet view**, one row per (`partner`, `app`):
- Rank by blast radius: `installs_affected / installs_total`, then admitted call volume. Do not rank by raw error count.
- 200 of 200 installs failing points at a partner-side release. 3 of 200 points at a configuration problem.
- Show the dominant bucket (4xx, 5xx, 429), first-seen time against our deploys, and a silent-apps panel.
- Keep a separate tab for failures correlated with our last release. That is the regression queue. Never mix it into the outreach queue.

## 6. Notification posture for partners

Payroll and benefits vendors likely lose money within hours of a break (pay runs, enrolment windows) ⚠️. If so, start at threshold alert with cooldown plus a daily per-app digest, plus immediate alerts for state changes (key revoked, app disabled). If not, start with the digest alone.

Digest per app, example body:

```
Integration health - acme-payroll-sync - 7 Oct
Calls 61,200 (-2% vs prior day)  |  Integrator-side (4xx) 1,904  |  Platform-side (5xx) 3  |  Throttled (429) 0
Top 4xx: invalid_employee_id 1,610; missing_pay_period 201
Request log: <link>
```

Do not send the digest and the threshold alert to the same place at the same cadence.

## 7. Validation: run before shipping

1. **Replay last week** through the new pipeline. Expect A1 to fire for the broken app within 15 minutes of the failure starting. If it does not, stop and fix.
2. **Replay the 8x month.** Expect A4 to fire and no A3 or A1. The partner shows as throttled, not broken.
3. **Break one app on staging** at 100% 4xx. Expect A1 plus a partner message with the right top error code.
4. **Stop traffic from one app.** Expect A5.
5. **Remove the join** in a test run. Expect A6.
6. **Mutation check:** disable the `app_id` grouping. Test 1 must fail. If it still passes, the test checks the blend, not the app.

Measure success by:
- **Time from first failure to partner awareness.** Measure until the partner acts, not until the alert is sent. Track it per alert type.
- **Alert action rate.** A sustained fall means fatigue. Widen thresholds or lengthen the cooldown before adding another channel.
- **`unattributed` share.** Target 0% after the edge tag ships.

## 8. Build order

1. Add the 429 split to the existing dashboard and page logic. This is the cheapest change and stops the false red immediately (about half a day, ⚠️ depends on your metrics stack).
2. Build the join and rollup, and replay last week (test 1).
3. Ship A1, A3, A5 and the partner-facing table.
4. Add `app_id` at the edge. Then remove the join and A6.
5. Add the digest and A2, A4.

## Questions that change the design

1. Do the edge log and the auth log share a `request_id`? If not, the join is lossy and A1 will miss some failures.
2. Does the auth service log every request, or only token issuance? If only issuance, per-request attribution needs the edge tag first.
3. Do you know the customer account per request? Without it there is no install coverage, and the blast-radius ranking falls back to call volume.
4. How soon does a break cost your partners money: hours or a reconciliation cycle? That sets the alert rung in section 6.
5. Who can open the partner dashboard today: account owner only, or also the partner's engineers?
6. Which engineering team owns quota? A4 hands off to it (`api-rate-limit-policy`). The 80% utilisation rule needs the limit values.

Next: answer question 1, then I turn sections 3 and 4 into the exact SQL and alert config for your stack.