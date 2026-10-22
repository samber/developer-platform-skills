# Design for a "no traffic" alert at Verandaq

I followed the `integration-error-observability` skill and its alerting and fleet-view references. I haven't checked any of this against your logs.

## Verdict

Build the no-traffic alert, but not as "below 10 calls/hour".

- **Why a fixed threshold fails:** it is the global threshold that the skill's step 4 and `alerting-and-notification.md` reject. Traffic shapes differ by orders of magnitude between integrations.
- **Quiet partners:** a partner that normally makes 3 calls/hour pages constantly. They are always "below 10".
- **Large partners:** one that normally makes 50,000 calls/hour and drops to 500 never fires. That is a 99% outage.
- **Your incident:** a stock-sync partner calling on a schedule may never reach 10 calls/hour. The rule could be both noisy and blind on the very integration that failed.
- **Real fix:** compare each integration to its own baseline.

The deeper bug is in the board, not the alerting. Green currently means "no errors seen". The board needs a third state: silent, meaning "expected traffic is missing". No data must never render as healthy.

## Design

### 1. Add a third health state

| State | Meaning |
|---|---|
| Healthy | Traffic is near baseline and the error rate is near baseline |
| Failing | Error rate is above baseline, split into 4xx, 5xx and 429 |
| Silent | Expected calls are missing (new, separate signal) |

Silence is its own failure class. An absence produces no errors, so it can't be a side effect of error logging.

### 2. Detect silence against each integration's own baseline

Use two detectors, matched to traffic shape.

- **High and steady traffic:** compare the rolling call count with the same hour-of-week over the last 2–4 weeks.
  - Use two windows, as in the skill's multi-window pattern.
  - A short window (about 15–60 minutes) catches a sudden drop.
  - A long window (hours to a day) catches a slow fade.
  - Fire when volume is below a fraction of baseline in both windows. The fraction is yours to set.
- **Low-volume, batch or scheduled traffic (your case):** use the gap since the last call.
  - Learn each integration's usual inter-arrival gap, for example the p99 of past gaps for that hour-of-week.
  - Fire when the current gap exceeds that gap by a margin.
  - A nightly sync that has missed two nights is silent. A 3-calls/hour integration with a 40-minute gap is not.
- **Optional heartbeat:** let partners declare an expected cadence (for example "stock sync every 15 min") when they register an app.
  - Declared cadence is more precise than learned cadence, and it covers new integrations that have no baseline yet.
  - Learned baselines remain the default. A declared cadence is an override, not a requirement.
- **Granularity:** tag silence per integration identity (API key or app ID), as in step 4.
  - For fleet apps, track silence per app and per install.
  - All installs silent points to the partner's release or scheduler.
  - A few installs silent points to a configuration problem at those customers.

### 3. Rule out your own side before blaming the partner

Silence has two possible causes, and the alert must not accuse the partner without checking.

1. **Check ingestion:** are their requests being rejected before the integration tag is attached? WAF blocks, DNS or edge failures, and auth failures at the edge all show up as "no calls" in a tagged view.
2. **Check credentials and state:** was the key revoked, the app disabled, or the subscription lapsed? That is a state-change event and should alert immediately, with no threshold.
3. **Check your deploy timeline:** a silence that starts at one of your releases is yours.

Only silence that survives these checks goes to the partner as "we've seen no calls".

### 4. Notify with a cooldown

Your partner loses money within hours when stock syncs stop (overselling, stale inventory). That promotes threshold-with-cooldown over digest-only, per the skill.

- **Partner message** (one per incident, then a cooldown):

  ```
  Alert: no calls from acme-connector since 3 Oct 02:15 UTC
  Expected: ~96 calls/day (stock sync every ~15 min). Received: 0.
  No platform incident or credential change on our side in this window.
  Last successful call: <link to request log>
  Next alert for this integration no earlier than <cooldown end>.
  ```

- **Cooldown:** set it from your typical outage duration. Salesforce's 30 minutes is a reference point, not a rule.
- **Recovery message:** send one when traffic resumes. Silence is not an all-clear.
- **Escalation:** if nobody acts within N hours, escalate to the Verandaq partner team. An alert with no escalation is only a notification.
- **Digest:** add a "Calls: 0 (expected ~96)" line to the daily per-integration digest as the backstop.
- **Fatigue guard:** track the share of alerts partners act on. If it falls, widen the thresholds or lengthen the cooldown before adding channels.

### 5. Put silence in the provider-side fleet view

- Add a **Silent integrations** list ranked by blast radius (installs affected out of installs total), not by raw volume.
- Show first-seen-silent time, last successful call, and contact owner.
- Keep it apart from your own regression queue.
- This is the view your SRE lead or partner team checks each morning. In this incident it would have shown the partner roughly 11 days earlier.

### 6. Avoid these traps

- **Suppress known-quiet periods:** honor declared maintenance windows and seasonal lulls, or silence alerts become noise.
- **Handle new integrations:** a new integration has no baseline. Use its declared cadence, or a conservative gap rule until it has about two weeks of history.
- **Wording:** say "we've seen no calls", not "your integration is down". The partner's scheduler may be intentionally paused.

## Validate before you ship

1. **Backtest on the incident:** replay the partner's traffic around the 3rd. The rule should fire within hours, not 11 days.
2. **Backtest on 90 days of history:** count false positives per integration. Tune thresholds until the alerts are tolerable.
3. **Track time from failure to partner action** (not to alert sent). That is the number that justifies this rung.

## Questions that would change the design

I assumed the answers below. Tell me where I'm wrong.

1. **Cadence declarations:** can partners declare an expected call cadence at app registration? I assumed yes, as an optional override.
2. **Contacts:** do you have a contact per partner app and a place to send alerts (email, portal, webhook)? I assumed yes, with the Verandaq partner team as the fallback.
3. **Tagging:** is every request tagged with an app or key ID at ingestion? If not, per-integration baselines have no history, and fixing that comes first.
4. **Traffic shapes:** how many integrations are scheduled or batch versus continuous? That decides how much weight the gap-since-last-call detector carries.
5. **Effort ceiling:** who answers these alerts, and with what on-call load? Threshold tuning needs an owner.

## Reply for the SRE lead

> Yes to a no-traffic alert, no to a global 10/hour. A fixed floor is noisy for small integrations and blind to large ones. We're keying silence to each integration's own baseline, adding a "silent" board state so no data never shows green, and alerting with a cooldown and a recovery message. We'll backtest it on the 3rd to confirm it would have fired within hours.