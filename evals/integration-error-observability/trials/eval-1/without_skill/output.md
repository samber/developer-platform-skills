**Next action (before month starts, about 2 days):** pull the last 60 days of integration tickets. Tag each by root cause. Counts decide what to build.

## Why tickets first

I haven't seen your tickets, so the scope below is a hypothesis. My guess is that most are "did you send event X?" and "why did my endpoint fail?" If the tags show something else, such as signature verification or payload-schema confusion, change the scope.

Tag each ticket with one of these:
1. Customer asks if a webhook was sent.
2. Customer's endpoint failing (timeout, 4xx, 5xx, TLS).
3. Customer wants a resend.
4. Customer misconfigured URL or secret.
5. Real bug on our side.

Rule: build for the top two tags only.

## Scope: build in this order

1. **Delivery log.**
   - Per customer, searchable by shipment ID, event ID, endpoint, status, and time range.
   - Shows each attempt with HTTP code, timeout reason, latency, and retry schedule.
   - Builds on the attempts table you already have.
2. **Plain-language failure reasons.**
   - Map raw codes and timeout reasons to a message plus a fix.
   - Example: "Your endpoint took longer than 10s. Respond 2xx first, process async."
   - This removes the most support work per hour of engineering.
3. **Replay.** One event or a bulk "all failed in the last 24h" action. Idempotency keys must be visible.
4. **Failing-endpoint alerts.** Email the customer's technical contact after N consecutive failures. Add auto-disable later.
5. **Endpoint tester.** Send a test event, show the response. Handles the misconfiguration tickets.

Cut from v1: charts, analytics, custom dashboards, exports. They look good in demos and don't reduce tickets.

## Six-week plan

| Week | Work |
|---|---|
| 0 (before start) | Ticket tagging. Decide the 3 risks below. |
| 1 | Tenant-scoped read API on the attempts data. Indexes. Retention job. |
| 2 | Delivery log UI: list, filters, attempt detail. |
| 3 | Failure-reason mapping. Give internal support access to the same view. |
| 4 | Replay, with rate limits and an audit log. |
| 5 | Alerts and endpoint tester. Beta with 5 to 10 customers who file the most tickets. |
| 6 | Fix beta findings. Add docs and support macros. GA. Measure. |

Week 4 is the one most likely to slip, because replay touches the delivery path.

## Three risks to settle in week 0

1. **Tenant isolation.** The attempts table is internal, so it may not carry a clean customer ID. A data leak between 3PLs and brokers is the worst failure here. Add an authorization test for cross-tenant reads.
2. **Payload and response bodies.**
   - Shipment data has PII: addresses, names, phone numbers.
   - Customer responses can echo secrets.
   - Decide what to store, truncate, or redact. Mask auth headers always.
   - Default: store metadata, plus a truncated response body capped at about 2 KB.
3. **Volume and retention.**
   - 4M webhooks a month is about 4M rows, plus one row per retry.
   - The query load is small. Cost depends on storage and retention.
   - Pick 30 days hot (what customers see), and compare that against the contract.

## Success metric

- Baseline is 15h/week. Target is under 8h/week of integration-ticket time within 60 days of GA.
- Track the share of tickets tagged 1 to 3. Those should fall the most.
- Track dashboard weekly actives and replay usage.
- If tags 1 to 3 don't drop in 30 days, the log is hard to find or hard to read. Fix that before adding features.

## Open questions for you

1. Does the attempts table store customer ID and event ID today?
2. Does it store payloads or response bodies?
3. Is there an existing customer portal or auth to build into? Reusing one saves about a week.

Next: export the tickets and start tagging. Paste the tag counts and I'll tighten the scope.