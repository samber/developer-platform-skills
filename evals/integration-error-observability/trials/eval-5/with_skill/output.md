# Kettleback: webhook replay and failed-order handling

I followed the `integration-error-observability` skill. It asks eight clarifying questions first, but you asked for the complete deliverable, so I used the assumptions below. Flip any of them and the affected section changes.

## Assumptions

| # | Assumption | Affects |
|---|---|---|
| A1 | Partners are ISVs with fleets of installs, not single-account integrators. | Replay is scoped per endpoint, and partner engineers need access. |
| A2 | The delivery machinery already records per-attempt outcomes (6 retries over 12 h). | The delivery log is the base for replay. |
| A3 | Events are stored for at least 30 days. | Replay window. |
| A4 | The log viewer is partner-facing, and request/response bodies are already stored internally. | The request-log rung is cheap, but a redaction pass is still required. |
| A5 | `POST /orders` has side effects: charges, fulfilment, inventory. | No server-side re-run. |
| A6 | No deadline pressure. | Phasing at the end. |

Open questions that could change the design:
1. Does `POST /orders` accept an `Idempotency-Key` today?
2. Can a partner engineer who is not an account user open the log viewer?
3. Can request bodies be shown to partners (PII)?

## Feature 1: webhook replay

### Decision

Build it. The skill promotes replay when integrators lose events during their own downtime, and that is exactly this request. It ranks last on efficiency, so it must not ship before its prerequisite.

**Prerequisite (phase 0):** expose the delivery-attempt log you already write. A replay button without it only tells partners what you did, not why their endpoint failed.

Each row shows:
- event ID
- endpoint
- attempt number and timestamp
- the real failure reason (timeout, connection refused, TLS failure, non-2xx)
- the response body your server received back
- the next retry time

### Four design decisions

**1. Window: 30 days from event creation.**
- Publish the number.
- The 30 days follows A3: the window can never exceed event retention.
- Stripe's comparable limit is 15 days.
- Past the window, the UI offers the pull API below.

**2. Independence from automatic retry.**
- A replay never cancels, resets or shifts the 6-attempt schedule.
- The two mechanisms run in parallel.
- Checkout.com documents that manual resend can duplicate a pending automatic retry, so we design around it instead of hoping.

**3. Idempotency.**
- Every replay carries the same `event.id` as the original, so the consumer can deduplicate.
- Add headers:
  - `X-Kettleback-Delivery-Id`, new per attempt.
  - `X-Kettleback-Delivery-Type: automatic | manual-replay`.
  - `X-Kettleback-Replay-Job-Id`, on bulk jobs.
- Re-sign the payload with a fresh signature timestamp. Otherwise partners with timestamp-tolerance checks reject the replay.
- Document that consumers must dedupe on `event.id`.

**4. Scope: three levels.**

| Scope | Use | Limits |
|---|---|---|
| Single event | "Resend" on a delivery-log row | Rate-limited per endpoint, no job needed |
| Selection | Checkbox on filtered rows | Up to 500 events, runs as a mini job |
| Bulk job | Endpoint + time range + status filter | Async job, described below |

A replay can only go to the endpoint registered on the event. Partners cannot supply a new URL, because that would make replay an exfiltration path.

### Bulk replay: the 90,000-event case

#### Default scope: exhausted events only

The partner's 4-hour outage creates a trap. Retries run for 12 hours, so when they press the button right after recovery, many of the 90,000 events are still in their automatic retry schedule and will deliver by themselves. Replaying those causes duplicates for no benefit.

The preview step shows two counts:
- **Exhausted** (retries used up): selected by default.
- **Still retrying:** unchecked by default, with a warning that they may be delivered twice. If included, it still does not cancel the schedule (decision 2).

#### Job flow

1. **Filter:** endpoint, time range, event types, status.
2. **Dry run:** shows the counts, a sample payload, estimated duration, and the rate.
3. **Canary:** sends 1 event and waits for a 2xx, so a still-broken endpoint fails after 1 event, not 90,000.
4. **Confirm:** the user types the event count. This is a guard against bulk side effects, not a formality.
5. **Run** asynchronously, with pause, resume and cancel.
6. **Summary:** counts of delivered, failed and skipped, a downloadable list of failed event IDs, and a notification when done.

#### Rate control

Without it, a partner recovering from an outage becomes your next incident, and your recipient's.

| Control | Setting |
|---|---|
| Default rate | 25 events/s per job (a placeholder to tune against real partner capacity) |
| Partner override | 1 to 100 events/s, set by the partner to match their capacity |
| Concurrency | 1 active bulk job per endpoint |
| Priority | Replay queue sits strictly below live deliveries and automatic retries |
| Auto-backoff | Failure rate above 20% over a 30-second window slows the job by half |
| Auto-pause | Sustained failures pause the job, and the partner gets a notification |

Duration for 90,000 events:

| Rate | Time |
|---|---|
| 10/s | 2.5 h |
| 25/s | 1 h |
| 100/s | 15 min |

Ordering:
- Events are sent in creation order, but the platform does not guarantee delivery order.
- The docs say so, and tell partners to compare `event.created` or the object version, and to re-fetch current state when in doubt.

Live traffic keeps priority, so a large job never delays real-time events for the same or other partners.

#### Cheaper alternative: pull-based catch-up

Offer `GET /events?created[gte]=…&created[lte]=…&delivery_status=failed`, with cursor pagination.
- It lets a partner reconcile at their own pace, with no push load.
- It covers events older than the 30-day replay window, up to event retention.
- It is a small addition once the delivery log exists.

For planned maintenance, add **pause delivery** on an endpoint. Events queue instead of burning their 6 retries, and resume drains them at the controlled rate. This removes most replay need for maintenance windows. It is optional for v1.

### Access, audit, safety

- **Access:** partner engineers need access even when they are not account users (A1). Use a partner-level role scoped to their apps' endpoints.
- **Authorization:** replay requires the "webhooks:write" permission, not just read access to logs.
- **Audit:** log who started which job, when, with what filter, plus pause and cancel actions. The job appears in the delivery log, with replay deliveries labelled `manual-replay`.
- **Redaction:** the payload shown in the console goes through the redaction pass. Delivery sends the original payload, since it goes to the partner's own endpoint.
- **Failures:** a replay that fails shows up as another delivery-log row with the real reason. It is not retried automatically.

### Fleet view (provider side)

Add replay jobs to the internal view:
- jobs running, with rate and failure ratio
- partners with a paused job
- partners with repeated bulk jobs, which signals unstable endpoints worth outreach

## Feature 2: "retry this call" on failed `POST /orders`

### Decision

**Do not build a server-side re-run in the log viewer.** The skill is explicit: re-issuing a POST on the integrator's behalf creates side effects nobody authorised. Here that means duplicate orders, charges or shipments.

The button is also useless for most failures:

| Failure class | Does retrying help? | What the viewer shows instead |
|---|---|---|
| 4xx (validation, auth) | No, it fails the same way | Error code, offending field, a fix hint, and the button replaced by "Fix and re-send from your client" |
| 429 | Only after waiting | `Retry-After` value; hands off to the rate-limit policy |
| 5xx | Maybe | Whether an order may exist, plus the safe-retry instructions below |
| Timeout / network | Unknown outcome | Same as 5xx: the order may have been created |

### What to ship instead

1. **Full request detail** (step 2 of the skill), with error code, request ID and field-level detail on every row.
2. **"Copy as cURL"** with the original `Idempotency-Key`. Credentials are never included and the cURL uses a placeholder, because the redaction pass strips secrets unconditionally. The partner re-issues from their own client with their own credentials.
3. **Order lookup by idempotency key or external reference** next to each failed 5xx or timeout row. It answers "did this order actually get created?" before any retry.
4. **Idempotency:** if `POST /orders` does not support `Idempotency-Key` today (open question 1), it is the real fix. It makes partner-side retries safe, and any future "retry" feature depends on it.

Re-evaluate only if tickets show that copy-and-reissue is not enough. A later version could allow retry in **test mode only**, or in live mode with these constraints:
- a mandatory idempotency key
- a duplicate check
- an explicit confirmation naming the side effects
- execution under the partner's own session

### Request IDs

Every response, success or failure, carries `X-Request-Id`, and the log viewer is searchable by it. If that is not true today, it comes before everything else here: a header that no external surface can resolve is ticket decoration.

## Phasing

| Phase | Ships | Why first |
|---|---|---|
| 0 | Delivery-attempt log exposed, request ID searchable, cURL copy with order lookup | Cheap, and the prerequisite for the rest |
| 1 | Single-event and selection replay, 30-day window, headers, audit | Covers most partners' missed events |
| 2 | Bulk jobs with canary, rate control, auto-backoff, pull API | The 90,000-event partner |
| 3 | Pause delivery, replay-job alerts, fleet view | Prevents the need and surfaces repeat offenders |

Do not give the 90,000-event partner a one-off script run by your team. It would skip the controls that protect you both.

## Failure modes to avoid

- Replay that cancels or resets the 6-attempt schedule.
- Replay without a stable event ID, which turns missed events into duplicates.
- Bulk replay with no rate control, which hammers a freshly recovered endpoint.
- Including still-retrying events by default.
- A server-side re-run of `POST /orders` for 4xx failures, which can never succeed.
- Replay available only to the account owner.
- Retention shorter than the replay window.

## Measurement

- **Failure-class coverage:** the ticket pile ("webhook never arrived", "order failed") has a surface for each class.
- **Request-ID resolvability:** take an ID from a real response and look it up as an outside user.
- **Self-serve deflection:** re-run the ticket classification after shipping and compare to your own baseline.
- **Replay duplicates:** count manual replays that hit an event already delivered. A rising rate means the default scope is wrong.
- **Bulk-job outcome:** the share of jobs that complete without auto-pause. These numbers have no industry benchmark, so treat them as trends, not pass marks.