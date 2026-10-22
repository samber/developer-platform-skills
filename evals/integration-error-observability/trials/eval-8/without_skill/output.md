# Spec: Partner Error Leaderboard and Integration Health Score

Status: draft for review. Weights, thresholds, and dates are proposals marked **[DECIDE]**.

## 0. Decisions needed first

1. **Raw error count ranks volume, not quality.** A partner sending 10M calls a day will always beat a partner with a broken integration sending 5k. §1 builds what you asked for (total errors, descending). It also shows volume and error rate beside it, so the TV doesn't mislead the team. **[DECIDE]** whether to keep the raw sort as the default or switch to a rate-based sort.
2. **Which errors count as "partner errors"?** Our own 5xx and outages would otherwise put partners on the board for our failures. §1 shows the total as requested and splits it by cause. §2 scores only partner-attributable errors.
3. **The Health Score decides Premier tier.** That is a contractual and commercial consequence, so §2.7 adds safeguards. Legal and partner management must sign off before launch. The score must not be the only input.

## 1. Internal partner error leaderboard

### 1.1 Goal
Show the partner team, at a glance, which partners are hitting the most errors right now, so they can reach out or investigate.

### 1.2 Users and placement
- Audience: the partner team only, on a TV in their area.
- It is internal. It must not be reachable from the partner portal or any partner-facing URL.
- Access: SSO-gated, group `partner-team`. The TV uses a read-only kiosk token.
- Because the TV is visible to visitors, show partner display names only. No contact details, API keys, or endpoints.

### 1.3 Ranking
- Population: every partner with at least one request in the window.
- Window: rolling 24 hours, ending now. Not calendar day.
- Metric: total errors in the window, sorted descending.
- Tie-break: higher error rate, then partner name ascending, so the order is stable.
- Display: top 20 rows.
- "Error" means any API response with status ≥ 400 or a webhook delivery that failed after exhausting retries. **[DECIDE]** whether 429 counts. Recommendation: count it, but break it out.

### 1.4 Columns

| Column | Definition |
|---|---|
| Rank | 1–20 |
| Partner | Display name |
| Total errors | Count in the 24h window |
| Δ vs. previous 24h | Change from the 24h before the window, as a number and an arrow |
| Requests | Total requests in the window |
| Error rate | Errors ÷ requests |
| Cause split | Partner-side (4xx) / platform-side (5xx) / rate-limited (429), as a small stacked bar |
| Top error | Most frequent error code |

Rows with an error rate above **[DECIDE: 5%]** get a visual flag. Rows where platform-side errors are the majority get a "platform" tag, so the team doesn't chase a partner for our outage.

### 1.5 Behavior
- Refresh every 60 seconds. The header shows "Updated hh:mm:ss".
- If data is more than 5 minutes stale, show a red "STALE DATA" banner. A frozen TV looks like a quiet day, so the stale state must be unmistakable.
- Zero-error state: "No errors in the last 24h".
- Fewer than 20 partners: show only the rows that exist.
- Layout: 1080p landscape, readable from 5 m. Minimum 28 px row text, high contrast, no hover-only information.
- Partners with an agreed maintenance window or a flagged test integration can be excluded via an `exclude_from_leaderboard` flag, with an audit log of who set it and why.

### 1.6 Data
- Source: the API gateway request log and the webhook delivery log, aggregated into 1-minute buckets per partner and status class.
- The aggregation table holds `partner_id`, `bucket_start`, `requests`, `errors_4xx`, `errors_5xx`, `errors_429`, `webhook_failures`, `top_error_code`, with a `created_at` column.
- The leaderboard sums the last 1,440 buckets.
- Traffic is attributed to a partner by API credential. Unattributable traffic is excluded and counted in a hidden "unattributed" metric that the team can check.

### 1.7 Acceptance criteria
- Ordering matches a manual SQL check on a fixed fixture, including ties.
- A fixture with a platform outage shows the cause split and the "platform" tag.
- Stale data triggers the banner within 5 minutes.
- No partner-facing route serves this data (automated route test).
- Load: the query runs in under 2 s at the current partner count plus 10×.

## 2. Integration Health Score (partner portal)

### 2.1 Goal
Give each partner an accurate, explainable 0–100 score for the health of their integration, with clear guidance on how to improve it. The score also informs next year's Premier tier decisions.

### 2.2 Principles
Because the score affects tier status, it must be:
- **Explainable:** partners see every component and how it is computed.
- **Fair:** it measures what partners control, normalized for size.
- **Stable:** it doesn't swing on one bad day.
- **Contestable:** partners can dispute it.
- **Not sole authority:** it is one input to the tier decision (§2.7).

### 2.3 Components (proposed weights **[DECIDE]**)

| Component | Weight | Measure | Subscore 100 → 0 |
|---|---|---|---|
| Error rate | 35 | Partner-attributable errors (4xx excluding 429 and auth-expired-by-us cases) ÷ requests, 30-day rolling | ≤0.5% → 100, ≥5% → 0, linear |
| Webhook reliability | 20 | Webhook deliveries acknowledged first try ÷ total, 30 days | ≥99% → 100, ≤90% → 0 |
| Rate-limit discipline | 15 | 429s ÷ requests, 30 days | ≤0.1% → 100, ≥2% → 0 |
| API version currency | 15 | Share of traffic on supported (non-deprecated) versions | 100% → 100, 0% → 0 |
| Security hygiene | 15 | Credential rotation within policy (quarterly), no use of deprecated auth | Pass-all → 100, each miss −50 |

Score = Σ(weight × subscore) ÷ 100, rounded to an integer.

The thresholds above are placeholders. Calibrate them on at least 90 days of real partner data before launch and publish the final values.

### 2.4 Rules that keep the score fair
- **Platform-caused errors are excluded.** 5xx, our incidents, and any bucket overlapping a declared incident are removed from numerator and denominator.
- **Rates, not counts.** The score is size-neutral by construction.
- **Minimum volume:** under **[DECIDE: 10,000]** requests in 30 days, show "Not enough data" and no score. Never show a score computed from tiny samples.
- **Smoothing:** 30-day window, recomputed daily, with a displayed 90-day trend line.
- **New partners:** a 60-day onboarding grace period. The score is shown but marked "provisional" and is not used for tier decisions.
- **Missing component** (for example, no webhooks configured): drop that component and re-normalize the remaining weights. Never score it as zero.
- **Deterministic:** the same inputs always give the same score. No ML or opaque model.

### 2.5 Portal UX
- Header: score (0–100), band label, 90-day sparkline.
  - Bands **[DECIDE]**: 90–100 Healthy, 70–89 Fair, 50–69 At risk, 0–49 Critical. Bands are shown with a label and an icon, never by color alone.
- Component breakdown: each component's subscore, weight, raw measure, and threshold, with a plain-language explanation.
- "What's hurting your score": the top 3 contributors, each with the most common error codes, an example request ID, and a docs link.
- Data freshness: "Last updated <date>, covers <window>".
- Visible only to the partner's own users with portal access. No peer comparison and no rank, so partners never see other partners' data.
- Score history is exportable as CSV.
- Show the tier-relevance rules in plain language: how the score is used, the review date, and the disputes link.

### 2.6 Disputes and corrections
- A "Dispute this score" button opens a request that references a date range and component.
- The partner team responds within **[DECIDE: 5 business days]**.
- If the cause was platform-side or misattributed, the data is corrected and the score is recomputed. The portal keeps a visible "corrected on <date>" note.
- Every manual correction is logged with who, when, and why.

### 2.7 Premier tier use (safeguards)
- The score is **one input**. A human partner manager makes the final decision and records the reasoning.
- Publish the tier criteria, including the score threshold and the measurement window, to partners at least **[DECIDE: 90 days]** before the evaluation date.
- Send each partner an at-risk notice when their score drops below the threshold, followed by a remediation plan opportunity before any downgrade.
- Evaluate on the average over the full evaluation window, not a snapshot on one date.
- Provisional-score and "Not enough data" partners are evaluated manually.
- Legal reviews the partner agreements. If tier benefits are contractual, the score methodology may need to be a contractual schedule.
- Retain the methodology version used for each decision. Publish a version number on the portal, and never change weights mid-evaluation window.

### 2.8 Data and architecture
- Reuse the §1.6 aggregation, extended with daily rollups per component. `health_score_daily` holds `partner_id`, `date`, per-component subscores and raw measures, `score`, `methodology_version`, `provisional`, and `created_at`.
- Nightly job computes the score, idempotently, so re-runs for a date overwrite that date only.
- A partner never has rows deleted. Corrections add a new row version with a reason.
- The portal API returns only the authenticated partner's rows. Authorization is enforced server-side by `partner_id`, and the dashboard never trusts a client-supplied ID.

### 2.9 Acceptance criteria
- Golden-file tests: fixed input traffic gives the exact expected score for every component.
- Pivot cases: error rate exactly at each threshold, 0 requests, requests just below and above the minimum volume, a missing component, 100% platform errors, and a partner with all five components at zero.
- Platform incident buckets are provably excluded.
- Cross-tenant test: partner A cannot read partner B's score by any route.
- The recomputation is deterministic across repeated runs.
- The portal shows the same number as the stored value, with no rounding mismatch.

## 3. Rollout

1. Build the shared aggregation and the leaderboard (internal, low risk).
2. Run the score in **shadow mode** for 60–90 days. It is computed but invisible to partners. Calibrate thresholds and look for surprising outliers.
3. Review the shadow results with the partner team. Check that the Premier-tier partners you would expect to score well do, and investigate every surprise.
4. Soft launch in the portal, labeled "beta, not used for tier decisions".
5. Announce the criteria, then start the notice period (§2.7).
6. Use the score for Premier decisions only after one full evaluation window with the published methodology.

## 4. Out of scope
- Partner-to-partner comparison or public rankings.
- Automated tier changes with no human review.
- Alerting partners automatically from the leaderboard (a future option).
- Latency scoring (a candidate v2 component).

## 5. Open questions
1. Raw-count sort or rate sort as the leaderboard default? (§0)
2. Does 429 count as an error on the leaderboard?
3. Final weights, thresholds, and band cut-offs after calibration.
4. Does the partner agreement already define Premier criteria, and can the score be added without an amendment?
5. Who owns disputes, and what is the SLA?
6. Who may see the TV, and is partner name display acceptable to the partners under their agreements?