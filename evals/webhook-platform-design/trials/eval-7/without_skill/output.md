# Clearbend webhook subscription: proposed design

## Recommendation

1. Replace the boolean `enabled` with a `status` state machine.
2. Add an event buffer with a retention window. This is what answers the maintenance-window question.
3. Add read, update, replay and backlog endpoints, so Support stops using delete and recreate.

I haven't seen your delivery pipeline, so I'm assuming a queue per subscription with retries and a retention limit. The first thing to verify is what delete and recreate does to the stuck backlog. It probably does one of two things:

- **It drops the backlog.** The stuck events are discarded or orphaned, and the endpoint only receives new ones.
- **It resets failure state.** A circuit breaker or backoff counter clears, and the queue starts draining again.

If it drops events, "it works fine" is silent data loss. For an HR platform that means missed hires, terminations and comp changes. Confirm which it is before committing to the semantics below.

## Subscription object

```json
{
  "id": "sub_01J...",
  "url": "https://customer.example.com/hooks/clearbend",
  "description": "Prod HRIS sync",
  "event_types": ["employee.created", "employee.terminated"],
  "status": "active",
  "status_reason": null,
  "pause": null,
  "maintenance_windows": [
    {
      "id": "mw_01J...",
      "starts_at": "2026-11-14T22:00:00Z",
      "ends_at": "2026-11-15T02:00:00Z",
      "mode": "buffer"
    }
  ],
  "delivery": {
    "ordering": "none",
    "max_in_flight": 10,
    "resume_rate_per_sec": 20
  },
  "retention_hours": 168,
  "secrets": [
    { "id": "whsec_a", "created_at": "...", "expires_at": null },
    { "id": "whsec_b", "created_at": "...", "expires_at": "2026-11-20T00:00:00Z" }
  ],
  "health": {
    "last_success_at": "...",
    "last_failure_at": "...",
    "consecutive_failures": 0,
    "backlog": { "pending": 0, "oldest_event_at": null }
  },
  "version": 7,
  "created_at": "...",
  "updated_at": "...",
  "deleted_at": null
}
```

**Writable:**
- `url`
- `description`
- `event_types`
- `status` (`active` or `paused` only)
- `pause`
- `maintenance_windows`
- `delivery`
- `retention_hours`, within platform limits

**Read-only:**
- `health`
- `secrets`, changed only through the rotate endpoint
- `status_reason`
- the timestamps

### `status`

| Value | Meaning | Who sets it |
|---|---|---|
| `active` | Delivering normally | customer |
| `paused` | Capturing events, not delivering | customer, or a maintenance window |
| `failing` | Delivering with retries and backoff; backlog is growing | system |
| `suspended` | Platform stopped delivery after sustained failure; events still buffered until retention expires | system |
| `disabled` | Not capturing events. Events during this period are not recoverable. | customer, explicit only |

**`paused` and `disabled` are different.** Today `enabled: false` is ambiguous. If it drops events, it is a data-loss switch behind a friendly name.
- Make `paused` the default way to stop deliveries.
- Require `disabled` to be a deliberate choice, and have the API warn that events are not captured.

**Backward compatibility:** keep `enabled` for one deprecation cycle.
- `enabled: false` maps to `paused`, not `disabled`.
- Document that change loudly.

### `pause` and `maintenance_windows`

- **Ad hoc pause:** `pause: { "reason": "...", "resume_at": "<optional ISO time>" }`. If `resume_at` is set, the subscription resumes automatically.
- **Scheduled window:** `maintenance_windows[]` lets an enterprise schedule downtime ahead of time. The platform pauses at `starts_at` and resumes at `ends_at`, with no human action on either side.
- **`mode`:**
  - `buffer`: capture and hold events. This is the default and the expected choice.
  - `skip`: drop events in the window. Offer it only if a customer asks for it, because it is data loss by design.

## What happens to events during a maintenance window

This is the answer for the two enterprise accounts.

1. **Capture continues.** Events generated during the window are written to the subscription's queue. Nothing is attempted against their URL, so there are no failed deliveries and no retry noise.
2. **Retention bounds the buffer.** Events are held for `retention_hours` (168 h / 7 days as the starting default, adjustable by contract). If the pause plus the drain outlasts retention, the oldest events expire and are lost. The API should warn when a window is longer than 50% of retention.
3. **Resume drains the backlog at a controlled rate.** Delivery restarts at `resume_rate_per_sec`, not all at once, so a customer's recovering system isn't hit by the whole backlog. New events queue behind the backlog.
4. **Delivery is at-least-once and unordered by default.** Duplicates are possible, so consumers dedupe on the event `id`.
   - Offer `ordering: "per_entity"` (ordered per employee ID) as opt-in.
   - Don't promise global ordering.
5. **Backlog visibility.** `health.backlog` shows pending count and oldest event age, so the customer and Support can see the drain progress.
6. **Safety net.** Even if something goes wrong, the replay endpoint below can redeliver any event inside the retention period.

Decisions for you before you answer the accounts:
- Retention length (7 days is a guess).
- Whether ordering is a v1 promise.
- Whether to offer `skip` mode at all.

## Endpoints

| Method and path | Purpose |
|---|---|
| `GET /subscriptions` and `GET /subscriptions/{id}` | List and read. Return `health` and `version`. |
| `PATCH /subscriptions/{id}` | Update url, event types, windows, delivery. Use `If-Match: version` to prevent lost updates. |
| `POST /subscriptions/{id}/pause` and `/resume` | Explicit actions with an audit trail. |
| `POST /subscriptions/{id}/replay` | Redeliver events by `{ "from": ts, "to": ts }` or `{ "event_ids": [...] }`, within retention. Returns a replay job ID. |
| `POST /subscriptions/{id}/backlog/purge` | Intentionally discard pending events. Requires explicit confirmation and is logged. |
| `POST /subscriptions/{id}/secrets/rotate` | Adds a new secret and gives the old one an expiry, so there's no signature-verification gap. |
| `POST /subscriptions/{id}/test` | Sends a ping event and returns the result. |
| `DELETE /subscriptions/{id}` | Soft delete (`deleted_at`). Does not purge the buffer for the retention window, so an accidental delete is recoverable. |

Replay makes delete and recreate unnecessary. It also lets Support fix a stuck backlog without losing the subscription ID or secret, or any events.

## Support playbook change

Replace "delete and recreate" with:

1. Check `health` to see the failure cause, then fix the customer's endpoint if it is the cause.
2. `resume` if the subscription is `suspended`.
3. `replay` the affected range if events were missed.
4. Use `purge` only if the customer asks for it.

Until the new endpoints ship, tell Support to stop deleting subscriptions if that drops events. Check that first.

## Rollout order

1. **Now:** audit what delete does to buffered events, and stop the practice if it loses data.
2. **v1:** `GET`, `PATCH`, `pause` and `resume`, the `status` field, buffering, retention. This covers the enterprise questions.
3. **v1.1:** scheduled `maintenance_windows`, `replay`, `health.backlog`.
4. **v2:** secret rotation, `ordering`, `purge`.