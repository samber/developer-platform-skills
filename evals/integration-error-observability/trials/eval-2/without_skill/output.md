# Fix plan: one searchable request ID across Palmate

I haven't seen Palmate's code or log stack, so this is a design built from your description. Step 0 checks it against reality before any code changes.

## Root cause

The edge ID is a label, not a key. Each service logs under its own ID, so the ID in the header matches nothing downstream. That likely explains most of the "not found" answers, but not all of them. Four other failure modes produce the same symptom:

| Failure mode | Why the search comes up empty |
|---|---|
| Edge-terminated requests (WAF, auth failure, rate limit, edge timeout, 502/504) | No service ever logs them, and the edge may log nothing searchable either. |
| Sampling | Logs or traces for 4xx/5xx were dropped before they were indexed. |
| Retention | Partners file tickets weeks later, after the logs expired. |
| Async work and vendor calls | The tax engine and card processor have their own IDs, and nothing maps ours to theirs. |

## Step 0: measure first (about 1 day)

Take 50 recent "ID not found" tickets and bucket each into one of the five modes above. This sets the order of work and gives you a baseline. Also check two things:
- whether the edge ID reaches the services at all, or only as a header that gets dropped or overwritten
- whether the IDs partners quote are mangled (case, truncation, whitespace)

## Design

### 1. One ID, minted only at the edge
- Format: `req_` + 26-character ULID or UUIDv7 in base32. It is opaque and carries no customer data.
- The edge always mints it. It never trusts an inbound ID. If a partner sends their own `X-Request-Id`, log it as `client_request_id`.
- Return `X-Palmate-Request-Id` on every response, not only 4xx/5xx. Also put it in the JSON error body as `request_id`, because partners paste bodies into tickets more often than headers. Make sure edge-generated error pages carry it too.

### 2. Propagate and never re-mint
- Pass `X-Palmate-Request-Id` and W3C `traceparent` on every hop: HTTP, gRPC metadata, and queue message headers.
- Put it in a shared middleware library. It reads the ID into the request context and installs a context-bound logger, so every log line gets `request_id` automatically.
- Services never generate an ID for request-scoped work. For work with no inbound request (cron, queue consumer without a header), mint `int_<ulid>`. Increment a `request_id_minted_internally` metric so leaks show up.
- Add a lint gate that bans the raw global logger and any `uuid.New()` / `ulid.Make()` used as a request ID.
- Migration bridge: for one release, services also log their old local ID as `local_id` next to `request_id`. Old logs stay joinable. Then remove it.

### 3. External calls (tax engine, card processor)
- Send our ID in whatever the vendor supports: metadata/reference field, custom header, or both.
- Derive idempotency keys from `request_id + call_site`. They must be stable across retries of the same logical call.
- Write one structured log line per outbound attempt:
  `{request_id, upstream: "tax_engine"|"card_processor", upstream_request_id, attempt, status, latency_ms, error_class}`
- Store `upstream_request_id` from the vendor's response headers or body. Support can then go from our ID to the vendor's ID for escalations, and back.
- Add the same fields as span attributes.

### 4. A guaranteed record for every ID we hand out
- The edge writes one canonical wide event per request, including requests rejected at the edge:
  `request_id, client_request_id, account/partner_id, method, route, status, error_code, latency_ms, service_hops, upstream_summary`.
- Rule: an ID is never returned unless this event has been written. Then "not in anything I can search" is impossible by construction.
- Index `request_id` as a first-class field in the log store, the trace store, and the error tracker.
- Keep all 4xx/5xx. Tail-based sampling keeps 100% of traces with status ≥ 400 or any error span, and a log sampler must never drop those lines.
- Retention: canonical events for 13 months (cheap, one row per request). Verbose service logs for at least the ticket horizon, which is typically 90 days. Confirm the horizon from your ticket ages in step 0.

### 5. Support tooling
- One saved view or console page: paste an ID and get the timeline across edge, services, and vendor calls, with vendor IDs shown.
- Normalize input before lookup: trim whitespace, lowercase, strip quotes. Optionally add a check character to the ID so a typo returns "invalid ID", not "not found".
- Reverse lookup by vendor ID, for cases where the processor reports a failure first.
- Tag "ID not found" outcomes in the ticket system with a reason, so the metric keeps measuring.

### 6. Prove it stays fixed
- CI contract test: send a request through staging with a failing path and a success path. Assert the ID appears in the edge event, every service's logs, and each outbound-call log line.
- Production audit job: sample N emitted IDs per hour and check each one resolves in the canonical store and in every service its `service_hops` lists. Alert on orphan ratio > 0.1%.
- Alert on a rising `request_id_minted_internally`.

## Rollout order

1. Step 0 measurement and the baseline "not found" rate.
2. Canonical edge event, plus keeping all errors under sampling. This covers edge-terminated requests, sampling, and retention.
3. Shared middleware and logger in each service, with `local_id` bridging. Start with the busiest services.
4. Outbound-call logging and vendor ID capture.
5. Support lookup view.
6. Contract test and audit job, then remove `local_id`.

## Done when

- The "not found" share of partner tickets falls from ~50% to under 2%, and the remainder is attributable to partner typos or expired data.
- The audit job's orphan ratio stays below 0.1% for 30 days.
- No service mints a request-scoped ID, enforced by lint.
- Support can reach the tax engine and processor IDs for any request from one lookup.

## Decisions for you

- Return the ID on 2xx responses too? I recommend yes. It's free, and partners can then quote successes.
- Retention horizon: pick it from step 0's ticket-age data. The 13 months for canonical events is a guess at the cost/value balance.
- Which vendor fields can carry our ID? I need the tax engine and processor API docs, or whoever owns those integrations, to confirm.