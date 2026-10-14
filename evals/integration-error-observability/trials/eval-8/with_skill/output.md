# Spec: Partner Fleet Queue (TV) and Integration Health Score (partner portal)

Status: draft for Sablecrest review. I followed `integration-error-observability`. The skill says to ask its clarifying questions first, and I can't in a one-shot deliverable. Section 1 lists my assumptions and section 11 lists the questions to answer before build.

## 0. Verdict on the brief

Both requests ship as written only with changes. Four changes matter.

| Brief | Problem | Change |
|---|---|---|
| Top 20 by total errors, 24h, descending | A flat error-count leaderboard inverts priority. It ranks the highest-traffic partner first, mixes 4xx, 5xx and 429, and cannot show a partner that went silent. | Rank by blast radius, split by status bucket, add a silent-integration lane and a platform-regression tab (§3). |
| 0-100 score shown to partners | A score that decides tier is a contract once partners see it. They will optimise against it and dispute it. | Own weights, inspectable inputs, an appeal path and a shadow period before the score affects tier (§4–§6). |
| Score decides Premier tier | Errors that are the platform's fault (5xx) or neutral (429) would penalise partners. | Score only partner-attributable behaviour (§4.2). |
| Partners see only a score | A score with no logs behind it tells them something is wrong and gives them no way to act. | The score ships after the per-integration logs and correlation ID that explain it (§7). |

## 1. Assumptions to confirm

- Sablecrest sells a platform API. Partners are ISVs with apps installed across many customer accounts (the fleet segment). Single-account integrators may exist, and the score applies to partners only.
- Inbound requests are tagged with app/client ID and customer account at ingestion. If not, tagging comes first. History before the tag is unqueryable.
- Webhooks exist and record per-attempt delivery outcomes.
- A release/deploy timeline is available as data.
- The partner team owns the TV. The audience is internal only.
- Tier review happens yearly. Premier criteria beyond health (revenue, certification) are out of scope here.

## 2. Shared foundation

Both features read one aggregate, built once and reused (skill steps 4 and 6).

One row per `(app_id, account_id, window)` carries:
- window start and end
- success count (the denominator)
- count per bucket: 4xx, 5xx and 429, never blended
- top error codes, ranked
- deploy markers, overlaid from the release timeline

Rules:
- Buckets: 4xx is the integrator's side, 5xx is the platform's, 429 is neither party's bug.
- Each app is compared against its own rolling baseline, not a global threshold.
- Silent detection is a separate signal. Compare call volume against the app's own baseline and flag drops to zero or near zero. Errors cannot show absence.
- The aggregate keeps both dimensions, `app_id` and `account_id`, because fleet apps fail per install.

## 3. Feature A: internal partner fleet queue (TV)

### 3.1 Purpose
A ranked list the partner team acts on. The question it answers is which partner we should contact first. It is not a scoreboard.

### 3.2 Layout (one screen, 1920×1080, auto-refresh 60s)

Left, "Outreach queue" (top 20):
1. Rank by blast radius: installs affected, then error rate vs the app's own baseline. Raw error count is a displayed column and never the sort key.
2. Columns:
   - partner and app
   - installs affected / installs total
   - error rate vs baseline
   - dominant bucket (4xx / 5xx / 429)
   - first seen
   - top error code
   - named partner contact (owner)
3. Row exclusions:
   - Rows whose spike lines up with a platform deploy (5xx or release-correlated) move to the regression tab.
   - Rows dominated by 429 are tagged "quota conversation" and shown dimmed. Do not label them as failing.

Top right, "Gone quiet": apps whose call volume dropped to or near zero against baseline. Include last-call time.

Bottom right, "Platform regression": integrations whose failures correlate with our last release, aggregated. Owner is the platform team. Keep it visually separate from the outreach queue and never mix the two.

### 3.3 Why not the literal request
- 200/200 installs failing means one partner release broke everything and one call fixes it. 3/200 means a config problem at three customers. A volume sort hides this.
- A top-20 by errors shows large partners every day and small broken ones never.
- A 24h-only window misses slow degradation. Add a 7-day trend arrow per row (long window: creeping failure, short window: sudden break).

### 3.4 Behaviour and limits
- Window: rolling 24h for the queue, 7-day trend for the arrow. Deploy markers drawn on the sparkline.
- Minimum volume floor, to be tuned, so a 3-call app at 66% does not top the list.
- Every row links to the filtered request log for that app (internal view).
- TV exposure: the screen is visible to anyone passing through the area. Show partner and app names and counts only. Never show payloads, customer account names or contact emails. Show contact owner initials only.
- No partner-comparison view is ever exposed externally (§6).

### 3.5 Acceptance
- A partner with 200/200 installs failing outranks a single account with 10× the errors.
- A 429-only partner does not appear as failing.
- An app that dropped to zero appears in "Gone quiet" with no errors recorded.
- A spike within N minutes of a platform deploy appears only in the regression tab.
- Every row has a named contact.

## 4. Feature B: Integration Health Score (partner-facing)

### 4.1 Decision before building: internal vs external
The skill separates these. The internal queue (Feature A) can be rough and iterated. The partner-facing score is a contract the moment it decides tier. Hence a separate computation path, a stricter spec, and a shadow period (§6).

### 4.2 What counts
- Counts against the partner: partner-attributable failures, meaning 4xx from payloads, auth and deleted objects, and failed webhook deliveries caused by partner endpoint failures.
- Never counts against the partner: 5xx (platform), 429 (shown separately as "quota headroom" with a link to the rate-limit policy), and any window that overlaps a declared platform incident or a platform deploy-correlated spike.
- Volume alone is not health. A large partner at a stable 0.5% beats a small one at 30%.

### 4.3 Composition (0-100)

| Component | Measures | Proposed weight |
|---|---|---|
| Error rate vs own baseline | Partner-attributable error rate, rolling 30d, relative to the app's baseline | 40 |
| Install coverage of failures | Share of installs with sustained failures | 25 |
| Trend | Direction over a 90d long window | 20 |
| Time since last clean period | Days since the last window with no partner-attributable incident | 15 |

The weights are a starting proposal. The skill says Sablecrest must set and defend its own. They are not borrowed from any product. Record the reasoning for each weight in the spec of record, because partners will ask.

A score is `null`, shown as "not enough data", for apps below a minimum call volume. Do not compute a score on thin data. A tier decision must not rest on it.

Silent integrations are flagged "no recent activity" next to the score and are not penalised through it. Absence is not an error, and the partner team follows it up via the queue.

### 4.4 Partner portal display
- Score, band (e.g. Healthy / Watch / At risk) and a 90-day trend line.
- Every component expanded with its raw inputs: partner-attributable error counts by bucket, install coverage, the windows used.
- Platform-side 5xx and 429 shown separately, labelled as not counted.
- Each penalty links to the filtered request log and, for webhooks, the delivery-attempt log.
- Visible to every partner role that maintains the integration (engineers, not only the account owner).
- Never show other partners' scores, ranks, percentiles or averages.

### 4.5 Acceptance
- A partner can recompute their score from the inputs shown.
- A 5xx-only incident leaves the score unchanged.
- A 429 burst leaves the score unchanged.
- An app below the volume floor shows "not enough data".

## 5. Tier decision

- The score is one input. A single number must not decide Premier alone.
- Use a trailing window, not a snapshot. Proposal: the score's 12-month history, with a tolerance band and a minimum of N months in band. Sablecrest decides the threshold.
- Document how a platform-caused incident is removed from the window before scoring.
- Publish criteria to partners at least one full review cycle before first use.

## 6. Obligations before any partner sees the score

1. Shadow period: compute and review internally for a full quarter, with no partner display and no tier effect. Compare against the partner team's judgment and fix outliers.
2. Documented recomputation and dispute process: partner submits a challenge, the team recomputes from the logs, and a decision is returned within a stated SLA. If the score affects tier, this exists before launch.
3. Notice period: partners see the score for at least one review cycle before it counts.
4. No cross-partner comparisons, rankings or percentiles in any partner-facing view.
5. No published reliability or availability number derived from this. The fleet measures integrations, including partner code and their customers' configurations, which the platform only partly controls. SLA and uptime publication belongs to `api-status-communication`.
6. Do not present the framing as an industry standard. Provider-side integration SLOs have no published standard. This is a Sablecrest design.

## 7. Build order

1. Audit what partners can see today, as a table of failure class against current visibility (sync API errors, webhooks that never arrived, auth expiry, rate-limit rejection, silent mismatches, volume drop). Baseline = share of the last 20 integration tickets a partner could have answered themselves.
2. Per-integration failure detail in the portal. Default rung: expose the existing webhook delivery-attempt log. Add the request log if the ticket pile shows synchronous API failures. Metadata-only if payload exposure is not cleared by legal and redaction review.
3. Correlation: echo `X-Request-Id` (UUIDv4) on every response, success and failure, and make it searchable in the partner-facing log.
4. Aggregate per `(app_id, account_id)` with the buckets above (§2).
5. Feature A (TV queue). It is internal, cheap once the aggregate exists, and runs through the shadow period.
6. Notification. Default digest per integration, plus immediate state-change alerts (credential revoked, integration disabled). Threshold alerts with a 30-minute-class cooldown and a recovery message are promoted for partners who lose money within hours. Never one alert per failure.
7. Feature B in shadow, then partner display, then tier effect (§6).

Rationale for the order: the score ships last because it needs steps 2 to 4 behind it. Showing partners a number without the logs that explain it converts failures into support tickets and disputes.

## 8. Failure modes to guard against

- Score disputes with no appeal path.
- Platform 5xx or 429 silently lowering a partner's tier.
- Alert fatigue if notifications fire per failure.
- A healthy global rate hiding one failing integration.
- Request ID echoed but not resolvable in a surface the partner can reach.
- A dashboard visible only to the account owner.
- Log retention shorter than the time partners take to notice.
- Payloads exposed without a redaction pass.
- Silent integrations appearing in nothing.
- Competitive screenshots from the TV or portal. Hence no partner names on any external view.

## 9. Measurement

Gates:
- **Failure-class coverage:** share of audited failure classes a partner can now diagnose unaided.
- **Request-ID resolvability:** take one ID from a real response and look it up as an outside user.

Trends (no pass thresholds; no industry benchmark exists):
- Self-serve deflection: re-classify a fresh batch of tickets after launch.
- Time from first failure to partner acting.
- Alert action rate. A falling rate is the alert-fatigue signal. Widen thresholds or lengthen the cooldown before adding a channel.
- Score-dispute rate and dispute overturn rate. A high overturn rate means the score is wrong, not the partners.

## 10. Out of scope

Quota and rate-limit design (`api-rate-limit-policy`), error payload shape (`api-error-design`), webhook retry and dead-lettering (`webhook-platform-design`), portal information architecture (`developer-portal-design`), platform-wide incident communication and SLA publication (`api-status-communication`).

## 11. Open questions (answers change the design)

1. What can partners see today? A URL, or nothing?
2. Segment mix: fleet ISVs only, or single-account integrators and no-code builders too?
3. What do the last 20 integration tickets look like (request not found, webhook never arrived, silent mismatch, auth, rate limits)? This decides the first surface.
4. Is every request tagged with app ID and account at ingestion?
5. Are webhooks in scope, and are delivery attempts recorded per attempt?
6. Do partners lose money within hours of a break, or at the next reconciliation? This decides threshold alerts vs digest.
7. Legal: may request and response bodies be shown to a third party? If not, metadata-only is the ceiling.
8. Deadline and effort ceiling: engineering weeks, log storage, and who answers alerts? Is the tier review date fixed? If it is within two quarters, the shadow period compresses and the score should not affect tier in this cycle.
9. Who decides Premier criteria, and may the score be one input rather than the decider?
10. Who owns appeals and recomputation, and what is the response SLA?
11. Is anyone besides the partner team (e.g. sales) allowed to see the queue?