# Where to start: Freightwise developer-facing webhook dashboard

I followed the `integration-error-observability` skill and its four references. The skill wants its clarifying questions answered before it designs anything. Since you want the full answer now, I've stated my assumptions explicitly. The questions that could change the plan are in section 4.

## 1. First actions

1. **Classify the last 20 integration tickets** before any build work. Use these classes: webhook never arrived, synchronous API error, auth or credential failure, rate-limit confusion, silent data mismatch. For each ticket, ask whether the integrator could have answered it themselves from a surface you could ship. That share is your baseline, and the pile decides the build order. It takes about half a day, and you can do it this month before the 6 weeks start.
2. **Check the attempts table for these fields:** event ID, destination endpoint ID, attempt number, timestamp, HTTP status or transport failure reason, response body received, and next retry time. You already store the status code and timeout reason. If the other fields are missing, adding them is week-1 work.
3. **Confirm every attempt is tagged with an integration identity** (app, API key or endpoint owner, plus account) at write time. Aggregation can only be as granular as that tag, and history written without it can't be queried by integration.
4. **Get legal and data sign-off on what leaves your tenancy.** Webhook payloads for shipment tracking likely carry consignee names, addresses and phone numbers. Customer endpoints can also echo secrets in their response bodies. Do this now, because it can delete options. If bodies can't be shown, metadata-only is your ceiling, and that still covers most "webhook never arrived" tickets.

## 2. Recommended build: expose the delivery-attempt log

This is the skill's default rung when you send webhooks and already record attempts. It is mostly an access-control and interface job, which fits a fixed 6-week window. It also targets the most expensive ticket in a webhook platform, "your webhook never arrived".

Each log row should show:
- Event ID, endpoint, attempt number, UTC timestamp, and next scheduled retry.
- The real failure reason. Keep timeout, connection refused, TLS failure and non-2xx distinct, as your table already does. Never show a generic "delivery failed".
- The response body your worker received, subject to redaction.
- Identifiers the integrator can copy and search, matching what they see in their own payloads and headers.

Rules that keep it from failing:
- **Access:** scope it to the partner engineer who maintains the integration, not only the account owner.
- **Tenant isolation:** enforce it structurally, for example with row-level security, not by an application-level `WHERE account_id` clause.
- **Redaction:** strip credentials and signing secrets completely, never partially masked. Mask PII to the level legal allows, and show that a field was withheld.
- **Retention:** publish it, and make it longer than the time partners take to notice a failure. If they reconcile weekly, 24 hours guarantees the evidence expires first.

## 3. Six-week plan

I based these timings on my estimate for a small team, not on the skill. At 4M webhooks a month (about 1.5 per second on average), volume won't be a constraint.

| Week | Deliverable |
|---|---|
| Pre-start | Ticket audit, legal answer, attempts-table field check, questions in section 4 answered |
| 1 | Add missing fields and the identity tag. Define the access model. Echo `X-Request-Id` on every API response, success and failure. Add the event ID as the webhook-side identifier |
| 2–3 | Delivery-attempt log: API plus UI, filters (endpoint, status, failure reason, time), search by event ID and request ID |
| 4 | Redaction, retention policy, docs placed next to the error docs. Beta with 3–5 partners. Support uses the same view |
| 5 | Per-endpoint aggregation, with timeouts, 4xx, 5xx and connection or TLS failures kept separate. Per-integration digest. Immediate alert when an endpoint is disabled or credentials are revoked |
| 6 | Buffer and one stretch item, chosen from the audit (see below) |

**Chosen from the audit, for week 6 or later:**
- **Replay** if tickets show partners losing events during their own downtime. It is the highest-effort rung. The rules are:
  - Keep a bounded, published window (Stripe uses 15 days).
  - Reuse the original event ID so consumers can deduplicate.
  - Run it independently of your automatic retry schedule.
  - Rate-limit bulk replay.
  - Don't offer replay for synchronous API calls.
- **Threshold alert with a 30-minute cooldown**, if partners lose money within hours of a failure. For shipment tracking that seems plausible, but I haven't confirmed it. Send a recovery message, and name the top error codes and the filtered-log link in every alert. Don't alert per failure.
- **Request log** if synchronous API errors are a large share of the ticket pile. The skill's order is to ship the delivery log first and add the request log once the audit shows API errors.
- **Internal fleet view for support** (a ranked list of failing integrations):
  - Rank by blast radius (installs affected out of installs total), not raw error count.
  - Add a silent-integration signal for endpoints whose volume dropped to zero. Absence produces no errors, so it needs its own detection.
  - Check each spike against your deploy timeline before blaming a partner.
  - Don't publish per-partner reliability numbers or health grades yet.

**Correlation ID rule:** don't ship the header without the log. Once the log exists, make the ID searchable in it. Otherwise partners will quote IDs nobody outside engineering can look up.

## 4. Questions that could change the plan

1. Who breaks: single-customer engineers, or 3PL and broker software vendors whose app runs across many shipper accounts? Fleet vendors get little from a per-account dashboard. They need cross-install aggregation and push alerts, so weeks 5–6 matter more for them.
2. What can an integrator see today? I assumed nothing.
3. What did the last 20 tickets look like? This is the biggest unknown.
4. Do partners lose money within hours when webhooks fail, or does it surface at reconciliation? This decides digest versus threshold alert.
5. Is there a no-code or agent-builder audience? If so, add a plain-language "what to do" line to each failure.
6. What is the effort ceiling beyond the 6 weeks? Who answers the alerts you start sending, and who tunes the thresholds?

## 5. How to know it worked

- **Failure-class coverage (gate):** every class in your ticket pile has a surface, or a written reason it doesn't.
- **ID resolvability (gate):** take one real ID from a response and look it up as an outside partner would.
- **Self-serve deflection:** reclassify a fresh batch of tickets about 4–6 weeks after launch and compare. The direction matters, not the level. I can't promise a number of hours saved from the 15 hours a week, because no published benchmark exists. Your own before-and-after is the evidence.
- **Trends to watch, not pass or fail:** time from first failure to partner action, and the share of alerts partners act on. A falling action rate means alert fatigue is arriving.

## 6. Mistakes to avoid

- Shipping logs and calling it done, with no push notification. Fleet partners still hear about outages from their own customers.
- A blended error rate. Split it so you can say whose problem it is.
- Exposing payloads before redaction. Once partners build against a field set, you can't quietly withdraw it.
- Replay that double-delivers alongside your own retries.