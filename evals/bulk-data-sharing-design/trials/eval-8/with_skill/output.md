**Decision: ship streaming push (HTTPS webhook + Kinesis) first. Add an hourly Parquet file-drop second, as the replay and reconciliation backstop. Strike the native warehouse share for now.**

## Assumptions (I couldn't ask)

Each of these changes the design if wrong.

1. **Freshness demand:** "Inside a minute" comes from 3 design partners. I assumed it's real buying demand. Check that at least 2 of them will pay for it.
2. **Warehouse landscape:** Unknown. The native share is struck, not demoted, until about 30–40% of target accounts sit on one shareable platform. That threshold is self-set. Re-promote the share when they do.
3. **Bus retention:** The internal bus holds at least 7 days of events and can replay by time range. Verify before you publish the replay promise.
4. **Pricing:** Paid add-on. I assumed no free tier.
5. **Compliance:** EU end-user data is in scope. I assumed no India, China or Russia localization customers.

## 1. Camp: why streaming is justified here

The skill ranks streaming push last on effort and efficiency. Three promotion conditions hold:
- The data is event-shaped and append-only.
- Consumers demand sub-minute delivery.
- A 3-hour batch fails the intervention-loop use case outright.

The skill's main warning on streaming is that Braze Currents can't replay events, so a consumer outage means permanent loss. Pulsegrid avoids this by keeping a retry window and a replay window. You already have the bus, so the cost is low.

## 2. Delivery surfaces

Build one fan-out core: bus → per-destination queue → sink. The two sinks are thin.

**HTTPS webhook**
- HTTPS only, TLS 1.2+. Reject private and loopback IPs, and re-resolve DNS at send time, to block SSRF.
- Batched JSON array per request, up to 100 events, with a linger of at most 1 second. Customers can opt for single-event requests.
- At-least-once delivery. Every event carries a stable `event_id` as an idempotency key.
- Signature headers: HMAC-SHA256 over timestamp + body. Each endpoint has its own secret. Rotation keeps the old secret valid during a 24-hour overlap.
- Success is 2xx. On failure, retry with exponential backoff and jitter for up to 72 hours. After that, the event stays only in the replay window.
- Isolate each endpoint in its own queue so a slow customer never delays another.
- Disable and notify an endpoint after sustained failure.

**Kinesis**
- We write with `PutRecords` into the customer's own stream. The customer creates a cross-account IAM role that allows `PutRecords` on that one stream only. We assume it with a per-workspace ExternalId. We never hold static keys.
- Partition key is `user_id`. This gives per-user ordering inside a shard, but we don't promise it publicly.
- Same-region delivery by default. The customer picks a stream in the region where their data is homed.
- Cross-region delivery is opt-in and priced to cover egress.

**Both surfaces**
- JSON envelope.
- Payload schemas are published as JSON Schema per event type.

## 3. Event contract (launch scope)

Three families, named so intervention loops can act on failures too:
- `message.delivered` and `message.delivery_failed`
- `message.opened`
- `message.clicked`

Every event carries these fields:
- `event_id`
- `event_type`
- `schema_version`
- `occurred_at`
- `ingested_at`
- `workspace_id`
- `app_id`
- `user_id` (the customer's external ID)
- `message_id`
- `campaign_id`
- `channel` (push or in-app)
- `payload`

Also in the contract:
- **Duplicates:** possible, so consumers dedupe on `event_id`.
- **Ordering:** not guaranteed. Use `occurred_at`.
- **Erasure:** an erasure request emits a `user.erased` tombstone so the customer can purge downstream copies. This is the delete semantics the skill asks for.
- **Open events:** noisy. Mail-proxy and prefetch opens inflate counts, so document this and flag proxied opens as `machine_open` where we can detect them.
- **Schema evolution:** add-only. New nullable fields and new event types appear freely, and consumers must ignore what they don't know. Never rename, remove or retype in place. A breaking change ships as a new `schema_version`, emitted in parallel with the old one for at least 90 days, with a dated removal. The `api-versioning-policy` skill owns the notice machinery.
- **Pre-delivery check:** validate every emitted event against the published schema in CI and in production. Drift raises an internal alert, not a customer ticket.

## 4. Freshness posture: best-effort target, not an SLA

The clock starts when Pulsegrid ingests the event onto the bus. It stops at the first acknowledged delivery attempt: 2xx for HTTPS, `PutRecords` success for Kinesis.

The clock excludes:
- Device-side latency, such as APNs/FCM receipt delays and the time before a user opens a message.
- Customer endpoint downtime.

| Phase | Posture | Number |
|---|---|---|
| Beta | Best-effort target | 95% of events within 60s |
| GA | Best-effort target | Same, raised to p99 only after about 90 days of measured data |
| Later | Contractual SLA | Considered only if a customer pays for it |

Run the pipeline internally at a p99 of about 15s so 60s has headroom. Run shadow traffic for 2 weeks before you publish any number.

## 5. Cost allocation

| Cost | Payer |
|---|---|
| Our compute, queues, retries | Pulsegrid |
| HTTPS egress from our cloud | Pulsegrid (small, priced into the add-on) |
| Kinesis shards and PUT payload units | Customer |
| Customer endpoint compute and storage | Customer |
| Cross-region Kinesis egress | Pulsegrid pays the cloud bill, so cross-region is opt-in with a surcharge |
| Replay and Parquet file-drop storage | Pulsegrid for the replay window. In the customer's bucket, the customer pays. |

## 6. Pricing

Sell this as a paid add-on or top-tier feature. Every vendor studied gates bulk export, and none offers a free tier. Meter on delivered events per month. Retries are free so customers aren't charged for our retry storms.

The design partners get free access during beta, with a written end date. That is an argued exception, not the default.

## 7. Residency

- The dispatcher runs in the workspace's home region. EU workspaces deliver from EU infrastructure, with no replicas outside the EU.
- For HTTPS, the customer chooses the destination. Document that choice in the DPA. Where it's feasible, offer region-specific source IPs so customers can allowlist.
- For Kinesis, record the stream's region. Warn when it differs from the workspace region.
- If a customer is subject to a localization mandate (India, China, Russia), the status is **not offered** until an in-country deployment exists. That is a legitimate precedented outcome.

## 8. Rollout

1. **Beta, weeks 0–6:** fan-out core plus the HTTPS sink for the two HTTPS partners. Add the Kinesis sink for the third partner in parallel. Best-effort target. Measure real latency.
2. **Replay and reconciliation:** a replay API by time range, plus an hourly Parquet drop of the same events to the customer's bucket. Hive-partitioned `date=/hour=`, files of 256–512 MB where volume allows, schema in a catalog, per-recipient role with ExternalId. This covers late data, lost events and ML backfills.
3. **GA:** publish the freshness posture and event contract. Turn on metering.
4. **After GA:** revisit a contractual SLA. Revisit the warehouse share only when platform concentration appears.
5. **Build vs partner:** evaluate a webhook-delivery vendor (e.g. Svix, Hookdeck) for the HTTPS sink. Build the Kinesis sink yourself, because it is thin.

## 9. What we commit to publicly

**Commit:**
- Events in the launch set (delivery and delivery failure, open, click) are delivered to your HTTPS endpoint or your Kinesis stream.
- At-least-once delivery. Duplicates are possible, and you dedupe on `event_id`.
- A **target** of 95% of events delivered within 60 seconds of ingestion. This is not an SLA.
- We retry failed HTTPS deliveries for 72 hours.
- Events are replayable by time range for 7 days, subject to the bus-retention check.
- Schema changes are add-only. Breaking changes get at least 90 days' notice and parallel emission.
- Delivery stays in the workspace's home region.
- Pricing is a paid add-on, metered on delivered events.

**Do not commit:**
- Ordering of any kind.
- Exactly-once delivery.
- Open events as true human opens.
- Any latency number for device-side events.
- A contractual SLA.
- Warehouse shares.
- Delivery to localization-mandate regions.
- Retention beyond the replay window.

## Measurement gates

1. **Contract completeness:** pass. Schema, versioning and an explicit best-effort posture are written down.
2. **Cost allocation:** pass, including the cross-region case.
3. **Residency:** pass for the EU, with a documented posture. A "not offered" entry for localization regions is pending your confirmation.
4. **Premium gating:** pass. Paid add-on, with a dated beta exception.

**Next:** confirm assumptions 1 and 3 (partner willingness to pay, and bus retention of at least 7 days with time-range replay). Those two decide whether the 60s target and the 7-day replay promise can go public.