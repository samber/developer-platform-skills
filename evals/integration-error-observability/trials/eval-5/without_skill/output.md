# Design: webhook replay and "retry this call" for Kettleback

I couldn't inspect the codebase for this, so the design rests on the assumptions listed at the end. Please confirm or correct them.

## TL;DR

- **Webhook replay** is a new async job system with a rate limit, circuit breaker, and pause/cancel controls. A single-event "Resend" button is a one-item job.
- **Retry on `POST /orders`** is a guarded server-side replay. It is only enabled when a duplicate order is provably impossible. There is no bulk version.
- ⚠️ The two features carry different risk. Replaying a webhook is safe because consumers dedupe on event ID. Replaying `POST /orders` can create a duplicate order.
- ℹ️ Most of the 90,000 events probably don't need replaying. Automatic retries run for 12 hours, so many events from a 4-hour outage were delivered once the endpoint came back. The replay tool must find out which events still need it, not blindly resend all 90,000.

---

## Part 1: Webhook replay

### 1.1 Semantics

- A replay re-delivers the stored original payload. It never regenerates the payload from current data.
- It keeps the same `event_id` and `event.created_at`, so partners can dedupe on `event_id`.
- It uses a fresh signature timestamp, so signature-freshness checks on the partner's side still pass.
- It adds the headers `X-Kettleback-Delivery-Kind: replay`, `X-Kettleback-Replay-Job: <id>` and `X-Kettleback-Attempt: <n>`.
- Ordering is oldest-first by default, but delivery order is not guaranteed. Document this. Each payload carries `created_at`, so partners can reorder.
- Replay is bounded by payload retention (assumed 30 days). Older events show "expired, cannot replay".

### 1.2 Which events are eligible

| Filter | Default | Notes |
|---|---|---|
| Endpoint | required | One endpoint per job |
| Time window (event created) | required | Max 30 days |
| Status | `failed` (retries exhausted) | Also selectable: `all non-delivered` |
| Event types | all | Multi-select |
| Include already delivered | off | Explicit opt-in, see below |

The "include already delivered" opt-in covers the case where the partner's endpoint returned 200 but lost the data. It needs its own confirmation, and it is capped (default 10,000 events per job) so it can't be used as a firehose by accident.

At send time, the worker re-checks each event. If the event was delivered successfully after the job was created (for example by an in-flight automatic retry), it is marked `skipped_delivered`. It is not sent again.

### 1.3 Partner flow (UI)

1. The partner opens the endpoint, goes to Deliveries, and clicks **Replay events**.
2. The partner sets the filters.
3. The **dry run** returns:
   - the count by status and event type
   - 5 sample events
   - the estimated duration at the chosen rate
   - the warning "N events were already delivered by automatic retry and are excluded"
4. For 90,000 events at 20/s, the estimate is about 75 minutes.
5. The partner confirms by typing the count, e.g. `90000`. This is a speed bump for large jobs only (over 1,000 events).
6. The job runs asynchronously. The page shows a progress bar and counts for sent, succeeded, failed and skipped, plus a live error breakdown by HTTP status.
7. Controls: **Pause**, **Resume**, **Cancel**, **Change rate**.
8. When the job finishes, the partner gets an email and a downloadable CSV of the failures. A **Retry failures from this job** button creates a child job.

Single event: a **Resend** button on the delivery row. It creates a 1-item job and returns the result inline.

### 1.4 API

Partners will want to script this, so the API comes first and the UI sits on top of it.

```
POST   /v1/webhook_endpoints/{id}/replays        (Idempotency-Key required)
       { filter: {...}, rate_per_sec?: int, dry_run?: bool }
GET    /v1/webhook_endpoints/{id}/replays/{job}
POST   /v1/webhook_endpoints/{id}/replays/{job}/pause | resume | cancel
GET    /v1/webhook_endpoints/{id}/replays/{job}/failures   (paginated / CSV)
```

Rules:
- Job creation is idempotent on `Idempotency-Key`, so a double click can't create two jobs.
- Only one **active** job per endpoint (queued, running or paused). A second request returns `409` with the active job's ID.
- Authorization: the caller must own the endpoint and hold the `webhooks:write` scope. Every action is recorded in the audit log.

### 1.5 Delivery engine (the part that matters at 90k)

- **Cursor, not materialized rows.** Fix an upper bound at creation: `(created_at, id) <= snapshot`. The worker pages through eligible events in batches (say 500) using keyset pagination. The job stores the cursor, so a crash resumes without gaps or duplicates. Per-event results go into the existing attempts table with `kind = replay` and `job_id`.
- **Separate, lower-priority queue.** Live deliveries must never starve behind a replay. Live traffic gets reserved capacity, and replay uses what's left.
- **Per-endpoint concurrency cap shared with live traffic.** Default 5 in-flight deliveries per endpoint for replay.
- **Rate.** Default 20 events/s per job and a hard cap of 100/s. The partner can lower it at any time. Raising it is allowed up to the cap, and the dry-run estimate shows the effect.
- **Adaptive backpressure (AIMD).** On 429, 503 or timeouts, halve the rate and honor `Retry-After`. After 30 s of clean responses, increase the rate by 10%.
- **Circuit breaker.** If more than 50% of the last 200 deliveries fail, auto-pause the job with status `paused_unhealthy`. This stops a partner from burning 90k events (and the retry budget) against an endpoint that is still down. Notify the partner by email and in the UI. Resume is manual.
- **Ramp-up.** Start at 10% of the target rate and reach full rate after about 60 s. This avoids hitting a freshly recovered endpoint with full load.
- **Per-event failure handling.** Replay does one attempt plus one immediate retry. Failures are recorded as `failed` in the job. Replay does **not** reschedule into the 6-retries-over-12-hours schedule, because that would hide the job's final state and re-amplify load.
- **Timeouts.** Same as live deliveries (assumed 10 s) so the endpoint contract stays identical.

### 1.6 Data model

```
webhook_replay_job
  id, partner_id, endpoint_id, parent_job_id (nullable, for "retry failures")
  filter_json, snapshot_upper_bound, cursor
  status: queued|running|paused|paused_unhealthy|completed|cancelled|failed
  rate_per_sec, total_estimated
  sent, succeeded, failed, skipped_delivered, skipped_expired
  created_by, created_at, started_at, finished_at, deleted_at (soft delete)
  idempotency_key  (unique per partner)
```

- A partial unique index enforces one active job per endpoint.
- No `ON DELETE CASCADE`. Jobs are soft-deleted, and their attempts rows stay.
- `created_at` is on every table.

### 1.7 Guardrails and abuse

- Max 500,000 events per job and 1,000,000 replayed events per partner per day. Both are configurable per partner by support.
- Replay never changes the endpoint's URL or secret. If the partner rotated the secret during the outage, the replay uses the **current** secret and signs with it. Document this.
- Disabled endpoints: a job can't start on an endpoint that is auto-disabled for repeated failures. The UI says "re-enable the endpoint first" and offers a health-check ping.
- Before starting a large job, **send a test ping** and require a 2xx. This is a cheap way to catch an endpoint that is still down.

### 1.8 Edge cases to test (pivot values)

- Window of 0 events: dry run returns 0, the job can't be created.
- Exactly 1,000 and 1,001 events: confirmation required only above 1,000.
- Event delivered by an automatic retry between dry run and send: it is skipped, not duplicated.
- Worker crash mid-batch: it resumes from the cursor with no duplicate sends (at-least-once, so an event may be sent twice only at the crash boundary, and the partner dedupes on `event_id`).
- Endpoint returns 429 with `Retry-After: 0`, with a huge value, and with garbage.
- Endpoint slow (timeout), refuses the connection, returns 401, 404, 500, or redirects.
- Circuit breaker boundary: 99 of 200 failures does not trip it, 101 does.
- Two concurrent create requests with the same idempotency key, and with different keys.
- Payload expired mid-job.
- Partner pauses during a batch: in-flight deliveries finish, no new ones start.
- Cancel then resume is rejected.

### 1.9 Observability

- Metrics: jobs by status, events/s, failure rate by status code, queue lag for live versus replay, breaker trips.
- Alert if live delivery latency rises while a replay job is running. That would mean the isolation failed.
- Structured logs include `job_id`, `endpoint_id` and `event_id`.

---

## Part 2: "Retry this call" on failed `POST /orders`

### 2.1 The core problem

`POST /orders` isn't idempotent by nature. A request that timed out or returned 500 may have created the order anyway. A blind retry can charge or ship twice. So the button must be conditional, and when it's disabled the UI says why.

### 2.2 When the button is enabled

All of the following must hold:

| Check | Why |
|---|---|
| Original outcome is `408`, `429`, `5xx`, timeout or network failure | A `400`, `401`, `403`, `404`, `409` or `422` fails the same way on retry. Show "Copy as cURL" instead. |
| **Duplicate-proof** (one of the next two) | Prevents double orders |
| – original request had an `Idempotency-Key` younger than its TTL (assumed 24 h), or | The server returns the original result if the order was created |
| – request carries a partner order reference that we enforce as unique, and a lookup finds no existing order | Reconciles the ambiguous case |
| Stored body is complete (no redacted fields) | Logs usually redact tokens and PII. Replaying a redacted body would send garbage. |
| Request age under 24 h | Prices, stock and tax may have changed |
| Viewer has write permission on the API key's scope | Read-only log viewers must not create orders |
| No retry already succeeded or in flight | Avoids double clicks and duplicate chains |

If the ambiguous case is detected (5xx or timeout, no key, no unique reference), the button is disabled with: "This call may have created an order. Add an `Idempotency-Key` header to enable safe retries."

If the lookup **finds** an order, the button is replaced by a link: "Order #123 was created by this request. No retry needed."

I considered an "override, I accept duplicates" confirmation. I recommend against it. It turns a support button into a duplicate-order generator.

### 2.3 How the retry runs

- The retry runs **server-side**, not from the browser, because we don't hold the partner's secret. It goes through the normal public handler stack as the **same API key identity** recorded in the original log entry. Auth, validation, rate limits and quotas all apply. It does not use a back door.
- The body and headers are replayed exactly.
- With an `Idempotency-Key`, the key is reused, so the server returns the existing order if there is one.
- With the unique reference, the pre-flight lookup above is the guard.
- The button's own idempotency: the retry is keyed on the original request ID (`retry:<request_id>`). A second click, or a second user, gets the first retry's result, not a second call.
- Single-flight lock per request ID. Concurrent clicks wait for the same result.
- Timeout: same as a normal API call.

### 2.4 UX

- Row action **Retry**. It opens a small panel showing the request summary, the original failure, the age, and the duplicate-proof reason ("will reuse idempotency key `abc`").
- The result appears inline: new status and the order link on success, the new error on failure.
- The new log entry is tagged **Retry of #<request_id>** and links back. The original gets a **Retried** badge and a chain view (attempt 1, 2, 3).
- Retry chains are capped at 3 per original request. After that, "contact support" or fix the root cause.
- Only the latest retry result decides the original's status badge.

### 2.5 Data model

```
api_request_retry
  id, original_request_id (unique where status in (pending, succeeded)),
  retry_request_id, requested_by, reason_guard ('idempotency_key'|'unique_reference'),
  status: pending|succeeded|failed, created_at
```

- Soft delete is not needed here, since it's an audit record. Nothing cascades.
- The audit log records user, API key, original request ID and outcome.

### 2.6 Explicitly out of scope

- **No bulk retry for orders.** Someone will ask. A bulk button multiplies the duplicate risk and the stale-price risk, and partners with volume can script retries with idempotency keys themselves.
- No editing of the request body before retry. That is a separate "edit and resend" feature, with its own validation questions.
- Other methods and endpoints: the mechanism is generic, but `POST /orders` is the only endpoint allowlisted at launch. Each additional endpoint needs its own duplicate-proof rule.

### 2.7 Edge cases to test

- Original 500 with key, order exists: the response is the original order, no duplicate (verify with a DB count).
- Original timeout with key, order does not exist: a new order is created once.
- Key at TTL boundary: 23:59 allowed, 24:01 disabled.
- No key, no reference, timeout: button disabled.
- No key, unique reference, order exists: link shown, no retry.
- Body with a redacted field: disabled.
- Double click, two users clicking at the same moment: one call, one result.
- Read-only user: button hidden, and the API rejects it with `403`.
- Retry hits `429`: the result is surfaced and no auto-retry is added.
- Retry chain at 3: blocked.
- Empty body, null reference, empty-string reference (treated as no reference).

---

## Part 3: Cross-cutting

- **Do not change the existing 6 retries over 12 hours.** Replay is the manual layer on top.
- **Check the retry schedule against the outage pattern.** If most of the 6 retries fall in the first hour or two, a 4-hour outage will exhaust them, which would explain the large failed count. Consider stretching the schedule or adding a final retry near hour 12.
- **Follow-up that would remove most replay demand:** a partner-controlled maintenance mode on the endpoint. Events are held, not retried, while it's on, and are delivered in order when it's switched off. It is cheaper for everyone than 90,000 failed events.
- **Docs.** Add a "Recovering from downtime" guide covering dedupe on `event_id`, replay headers, rate behavior, and retry safety with idempotency keys. Add a changelog entry.
- **Support runbook.** Cover how to pause a runaway job, raise a partner's quota, and read the job audit trail.

## Rollout

1. **Single-event resend plus the replay API behind a flag.** Internal endpoints only, then 2–3 design partners.
2. **Replay UI with dry run.** Include the circuit breaker, rate controls and failure CSV. Run the 90k partner's job with the rate set low and support watching.
3. **Order retry button.** Start with partners that use idempotency keys, then widen to the unique-reference path.
4. **Maintenance mode**, as a separate project.

## Assumptions to confirm

1. Webhook payloads are stored for at least 30 days.
2. `POST /orders` supports `Idempotency-Key` with a 24 h TTL, and some partners send a unique external reference.
3. The log viewer stores request bodies, and redacts sensitive fields.
4. Partners consume webhooks idempotently on `event_id`. If they don't, bulk replay can double-apply events on their side.
5. The log viewer sits behind per-user permissions that distinguish read from write.
6. The default replay rate (20/s) and the 500,000-event job cap are starting points, not measured numbers. Check them against your delivery infrastructure's capacity before launch.