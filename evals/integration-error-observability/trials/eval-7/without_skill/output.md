# Design for a "no traffic" alert on the integration health board

**Verdict:** Build the alert, but not as a flat 10 calls/hour. The real bug is that the board treats *no data* as *healthy*. Fix that first, then add per-integration silence detection.

## Why the 10/hr rule fails

| Case | What happens |
|---|---|
| Small partner that normally makes 2 calls/hr | Fires all day (false positive), and the team learns to ignore it |
| Large partner that normally makes 5,000 calls/hr and drops to 50 | Never fires (false negative), though it is a near-total outage |
| Night, weekend, or holiday lull | Fires on normal seasonality |
| Partner that syncs stock in a nightly batch | Fires 23 hours a day |
| One integration with several flows (orders OK, stock sync dead) | The aggregate looks fine and the dead flow is masked |

The root cause is that the board only evaluates traffic that exists. Zero requests produce zero errors, which computes to a 0% error rate and a green status. An absence alert patches one case. The structural fix is that green must require positive evidence.

## Design

### 1. Add a fourth state: "silent" (grey or amber)

- States become green, amber, red, and **silent/unknown**.
- Green requires recent successful traffic or a recent successful synthetic check.
- No evidence means not green. This one change would have flagged the incident on the 3rd.

### 2. Drive the watch-list from the registry, not from observed traffic

- Evaluate every integration × flow in the integration registry (for example `partnerX/stock-sync`).
- A series that stops emitting disappears from dashboards and queries. Registry-driven evaluation emits an explicit zero or "last seen: N hours ago".
- In Prometheus terms, join against the registry or use `absent_over_time` per entry. Do not rely on `rate() < x`, which returns nothing when the series is gone.

### 3. Alert per flow, not per integration

- Stock sync, order push, and webhook acks have different cadences and different owners.
- Aggregating hides the exact failure you just had.

### 4. Use a per-flow expected gap instead of a fixed count

For each flow, compute a baseline from the trailing 4 weeks, bucketed by hour-of-week. Then derive a silence window.

- **Statistical default.** If the expected rate is λ calls/hr, the chance of a gap of length T under normal behavior is roughly e^(−λT). Choose T so that this is about 1e-4, which gives T ≈ 9/λ.
  - A 2/hr partner gets a window of about 4.5 hours.
  - A 5,000/hr partner gets one of about 6 seconds, so add a floor (see below).
- **Declared cadence overrides learned cadence.** Scheduled flows (for example "stock sync every 15 min" or "nightly at 02:00") store `expected_interval` and `grace` in the registry. Alert when `now − last_success > expected_interval + grace`. This is a dead-man's switch and is more precise than any inferred baseline.
- **Floor and ceiling.** Set a minimum window (for example 15 min) so jitter does not page, and a maximum (for example 24–48 h) so very quiet flows still get caught.

```yaml
# registry entry (illustrative)
partnerX:
  flows:
    stock-sync:
      cadence: every 15m          # declared; falls back to learned baseline
      grace: 10m
      silence_severity: ticket    # page only for tier-1 partners
      owner: partner-success
```

### 5. Add a second detector for partial collapse

- Silence is the extreme case. Also alert when volume falls below about 20% of the seasonal baseline for 3 consecutive windows.
- This catches a partner whose retries keep running or whose scheduler is half-dead, which a gap detector would miss.

### 6. Track the business outcome, not only the traffic

- Add a freshness SLO such as "age of the last successfully applied stock update per partner".
- The partner's complaint was that syncs had not landed. That is a freshness metric, and it works even if traffic is noisy or retried.

### 7. Route silence differently from failure

- A failing call usually means we should fix something. Silence usually means the partner should fix something.
- Send silence alerts to a ticket or Slack channel owned by partner success or the account owner. Include the last-seen time, the usual cadence, and a draft outreach message.
- Page only for tier-1 partners or revenue-critical flows.

### 8. Guard against false positives

- **Our own pipeline.** If many integrations go silent at once, the cause is probably our gateway or metrics ingestion. Add a meta-alert: when more than N% of flows are silent, page the platform team and suppress the per-partner alerts.
- **Lifecycle state.** Registry states such as `onboarding`, `paused`, `churned`, and `maintenance` suppress alerts. New integrations use declared cadence only, until about 14 days of baseline exist.
- **Partner maintenance windows.** Allow partners to pre-announce downtime.
- **Hysteresis.** Fire after the window is exceeded. Resolve only after traffic returns for 2 or more windows, so the alert does not flap.

### 9. Optional: active probing

- For critical flows, a synthetic check can call the partner's callback or health endpoint. It separates "the partner is silent" from "our inbound path is broken", which is useful for the meta-alert above.

## Rollout

1. **Backfill.** Replay the last 90 days of traffic through the detector in shadow mode. Confirm it fires for this incident and measure how many hours after the 3rd it would have fired. For a 15-minute cadence, expect under an hour, against eleven days today.
2. **Tune on precision.** Review every historical alert and label it true or false. Adjust the floor, the grace period, and the drop ratio.
3. **Ship in ticket-only mode** for two weeks before enabling any paging.
4. **Track two numbers:** time-to-detect for silent partners, and the false-positive rate per week.
5. **Document the new state** ("silent" is not green) on the board, with the definition in the runbook.

## What to tell the SRE lead

- Keep the idea, but replace the 10/hr threshold with a per-flow expected gap, using declared cadence where known and learned baseline otherwise.
- Alert on staleness (`now − last_success`), not on a count, and watch every registered flow even if it has emitted nothing.
- Add the "silent" state to the board so that no data never shows as green.
- Add a meta-alert so an outage on our side does not look like fifty partners going quiet.