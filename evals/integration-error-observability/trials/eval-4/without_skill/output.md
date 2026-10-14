# Gridwell partner health: rebuilt aggregation

## Why last week's alerts missed it

- **Dilution.** The failing app was about 4% of that partner's traffic. A partner-level 5% threshold only fires if the broken app carries more than 5% of the partner's volume. App health was invisible at that grain.
- **Wrong denominator.** The 8x partner went red because 429s counted as errors. Throttling means our limits worked and the partner outgrew its quota. It isn't an outage, and paging on it is noise.
- **Window.** A 24h window moves slowly in both directions, so it detects late and clears late.

## 1. Grain: (minute, partner, app, outcome)

Raw requests roll up into one table. Every dashboard and alert reads from it.

```sql
CREATE TABLE partner_app_minute (
  minute      timestamptz NOT NULL,
  partner_id  text        NOT NULL,
  app_id      text        NOT NULL,  -- 'unattributed' when the join misses
  outcome     text        NOT NULL,  -- success | throttled | client_error | server_fault
  requests    bigint      NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (minute, partner_id, app_id, outcome)
);
```

**Outcome classes** (first match wins):

| Outcome | Rule | Meaning |
|---|---|---|
| `throttled` | The gateway's own rate-limit decision (reason code or header if available, otherwise 429) | Quota and capacity signal |
| `server_fault` | 5xx, gateway timeouts, upstream failures | Our fault |
| `client_error` | Other 4xx (400, 401, 403, 404, 422...) | The app's integration is broken |
| `success` | 2xx, 3xx | Healthy |

Client errors stay in the table because a bad credential returns 401 on 100% of an app's calls. The app is down for the partner, and a server-only rule would miss it again.

## 2. App attribution without edge tagging

The join runs at aggregation time against a key dimension, never per query against raw auth logs.

```sql
CREATE TABLE api_key_map (
  api_key_id  text NOT NULL,   -- key identifier or hash, never the secret
  app_id      text NOT NULL,
  partner_id  text NOT NULL,
  valid_from  timestamptz NOT NULL,
  valid_to    timestamptz,     -- NULL = current
  PRIMARY KEY (api_key_id, valid_from)
);
```

Rollup, run every minute over a trailing 15-minute window and upserted:

```sql
INSERT INTO partner_app_minute (minute, partner_id, app_id, outcome, requests)
SELECT date_trunc('minute', r.ts),
       COALESCE(m.partner_id, r.partner_id, 'unknown'),
       COALESCE(m.app_id, 'unattributed'),
       CASE WHEN r.throttled                      THEN 'throttled'
            WHEN r.status >= 500                  THEN 'server_fault'
            WHEN r.status >= 400                  THEN 'client_error'
            ELSE 'success' END,
       count(*)
FROM edge_requests r
LEFT JOIN api_key_map m
  ON m.api_key_id = r.api_key_id
 AND r.ts >= m.valid_from AND (m.valid_to IS NULL OR r.ts < m.valid_to)
WHERE r.ts >= now() - interval '15 minutes'
GROUP BY 1, 2, 3, 4
ON CONFLICT (minute, partner_id, app_id, outcome)
DO UPDATE SET requests = EXCLUDED.requests;
```

Rules for the join:

- **Point-in-time join.** Key rotation and app reassignment would otherwise rewrite history.
- **Build `api_key_map` from the auth service's key-to-app records.** Use the logs only to backfill gaps. Check that one key never serves two apps. If it does, that key can't be attributed and goes to `unattributed`.
- **Late-arriving auth data.** The trailing 15-minute upsert re-attributes rows once the mapping lands.
- **Never drop a miss.** Misses (invalid keys, brand-new keys) go to `unattributed`.
- **Alert on the join itself.** Ticket if `unattributed` exceeds 1% of requests for 30 minutes. Otherwise a broken join looks like healthy apps.
- **Longer term, tag `app_id` at the edge.** Then the join disappears. The rollup above doesn't depend on it.

## 3. Metrics

Over any window, for each (partner, app):

- **Fault rate** = `server_fault / (total − throttled)`. This is the SLI. Throttled requests never reached the service, so they are excluded from the denominator.
- **Client-error rate** = `client_error / (total − throttled)`.
- **Throttle rate** = `throttled / total`.

Partner-level versions are the same sums across apps.

## 4. Alerts

Each alert has its own route, because each needs a different responder.

| Alert | Condition (per partner × app) | Route |
|---|---|---|
| **Page: app broken** | fault rate ≥ 5% in both the 5m and 1h windows, and ≥ 10 faults in 1h | On-call |
| **Page: partner broken** (old rule, kept as backstop) | partner fault rate ≥ 5% in both 5m and 1h, and ≥ 10 faults in 1h | On-call |
| **Ticket: integration failing** | client-error rate ≥ 25% over 1h, ≥ 50 requests | Partner support, with `app_id` and top status codes |
| **Ticket: low-volume app failing** | fault rate ≥ 20% over 24h, ≥ 10 faults, not already paging | Owning team |
| **Notify: throttling** | throttle rate ≥ 10% over 1h, or quota use ≥ 80% | Account manager and capacity owner. Never pages. |
| **Ticket: attribution gap** | `unattributed` > 1% for 30 min | Platform team |

- **Dual window.** The 5m window catches fast and clears fast. The 1h window blocks one-minute blips.
- **Minimum volume.** It stops a 2-request app from paging at 50%.
- **Threshold values.** The 5%, 25%, 10% and 20% figures are starting points. Tune them in the backtest below.

## 5. Dashboard

- **Main view:** one row per partner with fault rate, client-error rate, throttle rate, volume, and a **worst app** column (app name and its fault rate).
- **Sort** by worst-app fault rate, not partner aggregate. Last week's partner would have shown 4.2% next to "app X: 100%".
- **Drilldown:** partner → app → endpoint and status code. Endpoint is a drilldown only, not an alert dimension.
- **Keep the 24h figure** as a secondary column for trend. Nothing alerts from it except the low-volume ticket.

## 6. Verify before switching over

1. **Backtest last week.** Replay the data through the new rules. The failing app should page within about 10 minutes of its failures starting. Record the actual time to detect.
2. **Backtest last month's 8x partner.** It must produce zero pages and one throttle notification.
3. **Check the join.** `unattributed` should be under 1% on real traffic. Spot-check 20 keys against the auth service.
4. **Run old and new alerts in parallel for one week.** Log disagreements and explain each one. Then remove the old `error rate, last 24h` page.

## Assumptions to confirm

- **429 attribution.** Does a 429 always come from our own limiter? If upstream services also return 429, I need the gateway's throttle reason code.
- **Key-to-app mapping.** Is it 1:1 in the auth service? This changes how much lands in `unattributed`.
- **Failure mode.** What did the failing app's calls actually return, 5xx or 4xx? That decides whether last week's incident would have hit the page rule or the ticket rule.
- **Storage.** I wrote SQL in generic Postgres style. The same shape works in ClickHouse as a materialized view or `AggregatingMergeTree`.