**Next action (10 min):** ask the bus owner three questions. (1) Are event IDs stable and unique, and is the bus at-least-once? (2) What does "delivered" mean per channel? (3) How late can opens and clicks arrive? The commitments below depend on these answers.

## 1. What we commit to publicly

These are the public promises. The first block is what we say yes to.

**Commit:**
- **Latency:** 99% of events reach the customer's destination within 60 s of Pulsegrid receiving them (`received_at`). We measure at our egress and exclude time a customer endpoint is failing or slow.
- **Delivery:** at-least-once. Every event carries a stable `id` for dedupe.
- **Retry:** exponential backoff with jitter for 24 h per event.
- **Replay:** 7 days of replay by time range, from dashboard or API.
- **Signing:** HMAC-SHA256 on every HTTPS request, with secret rotation.
- **Schema:** additive changes ship without notice. Breaking changes ship as a new `version` with 12 months' notice.
- **Egress IPs:** static and published.
- **Visibility:** a delivery log (7 days), lag metrics, and failure alerts.
- **Batch exports:** keep them. This surface is additive.

**Do not commit:**
- Exactly-once delivery.
- Global ordering. Ordering is best-effort per user only.
- Sub-second latency.
- Latency for events before Pulsegrid receives them. Provider receipts and offline-device opens arrive late and are outside our control.
- Counts that match batch exports or dashboards to the event. Late arrivals make them differ.
- Retention beyond 7 days.
- Plain HTTP.

**Stage the promises:**
- **Beta (design partners):** the numbers above are targets, with no SLA.
- **GA:** the latency number becomes an SLO, and a monthly delivery-success SLA of 99.9% applies while the destination is healthy.
- Do not sign an SLA before we have 4 weeks of production latency data.

## 2. Event contract (public, versioned)

Types at launch: `message.delivered`, `message.opened`, `message.clicked`.

I recommend adding `message.failed` as a fast follow. Intervention loops need to know about non-delivery.

Envelope fields:
- `id` (unique, dedupe key)
- `type`
- `version`
- `workspace_id`
- `occurred_at` (provider or device clock)
- `received_at` (Pulsegrid clock, the SLO clock)
- `message_id`
- `campaign_id`
- `channel` (push or in-app)
- `user` (the customer's external ID)
- `data` (type-specific)

Rules:
- **Map internal bus events through a translation layer.** Never expose bus schemas directly, or an internal refactor breaks customers.
- **Minimize PII.** Send external user ID only. No device tokens and no message body unless the customer opts in.
- **Document each event type per channel.** For example, APNs has no delivery receipt, so say what "delivered" means there.

## 3. Architecture

```
internal bus
  -> exporter consumer (own consumer group)
  -> translate + filter per destination
  -> durable per-destination queue (keyed by destination_id)
  -> delivery workers (HTTPS | Kinesis)
  -> delivery log + replay store (7 d)
```

- **Isolation:** one durable queue per destination. A slow or dead customer endpoint never blocks other customers or the bus consumer. This is the most important rule in the design.
- **Fairness:** each workspace has a rate quota and a concurrency cap. Defaults come from load testing, not from a number I invent here.
- **Destination abstraction:** a destination has `type`, `config`, `event_filter`, and `status`. HTTPS and Kinesis are two workers behind one interface. Adding Kafka, SQS, or EventBridge later is then cheap.
- **Replay:** the store is the replay source. Replay re-sends the same `id`s.

### HTTPS worker
- **Request:** `POST` JSON with a batch envelope `{events:[...]}`. A batch closes at 100 events, 256 KB, or 250 ms of linger, whichever comes first. The linger cap protects the 60 s budget.
- **Headers:** `Pulsegrid-Signature: t=<ts>,v1=<hmac(ts.body)>`. Customers should reject timestamps older than 5 min. Two secrets are active during rotation.
- **Ack:** `2xx` means ack. Timeout is 10 s. We follow no redirects.
- **Backoff:** honor `Retry-After` on `429` and `5xx`. Adapt concurrency per destination.
- **SSRF defense:** HTTPS only, TLS 1.2 or higher. Resolve DNS, block private and link-local ranges, and pin the resolved IP for the connection.
- **Failure handling:** a destination failing for 72 h goes to `paused`, and we send an alert email. Events stay replayable for 7 days.

### Kinesis worker
- **Cross-account access:** we assume an IAM role in the customer's account, with `ExternalId` to block confused-deputy attacks. We publish a CloudFormation or Terraform snippet for the role.
- **Producer:** `PutRecords`, batched to 500 records. Retry only the records that failed in a partial failure.
- **Partition key:** external user ID. That gives per-user ordering within a shard.
- **Format:** one event per record, same envelope as HTTPS.
- **Region:** the customer picks it. EU customers likely need an EU region, so confirm data-residency handling.

### Management surface (API + dashboard)
- Destination CRUD.
- "Send test event".
- Event-type, app, and campaign filters.
- Pause and resume.
- Secret rotation.
- Delivery log with per-attempt status and latency.
- Replay by time range.
- Lag and failure-rate metrics.

## 4. Build order

The estimates assume 2 engineers and healthy bus guarantees.

1. Verify the bus facts, define the public schema, and build the translation layer: about 1 week.
2. Build the queue, the HTTPS worker, signing, the delivery log, and the dashboard: about 4 weeks. Ship the beta to the 2 HTTPS partners.
3. Build the Kinesis worker and role-setup docs: about 2 weeks, since it reuses the framework. Ship to the third partner.
4. Add replay, auto-pause, and quotas. Run a 4-week latency soak. Then publish the SLO at GA.

## 5. Open risks

- **Bus assumptions:** the "plumbing is mostly there" claim is unverified. Duplicate or missing IDs would break the dedupe promise.
- **Late opens:** these are normal for mobile. They hurt the "real-time" feel but not the SLO, because of the `received_at` clock. Tell customers this up front.
- **Privacy:** customers receive user-level behavioral events. Check DPA and subprocessor wording, and consent flags per user.
- **Pricing:** I did not decide it. Per-event metering is the likely default. Decide before GA.
- **Throughput:** I have no numbers. Load-test per-destination and per-workspace limits before promising any rate.