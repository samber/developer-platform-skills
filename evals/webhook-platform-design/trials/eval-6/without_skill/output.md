# What breaks when 2026-04-01 reshapes `carrier`

Ranked by blast radius. This comes from reasoning about your description. I haven't inspected your delivery service, schemas, or any customer integrations.

## Root cause

Webhook payloads are rendered with whatever API version is current, so an API version bump is also a webhook breaking change. A REST client picks its version per request. A webhook receiver never makes a request, so it has no way to pick one. On cutover, every endpoint gets the new shape on the next delivery, including customers who pinned `2025-xx` for their REST calls.

## 1. 🔴 Customer tables get corrupted silently

`carrier: "UPS"` becomes `carrier: {…}`. What happens next depends on how the customer ingests it:

- **Loose ingestion** (no-code tools, `str()` or string coercion, JS template strings):
  - The column fills with `[object Object]`, a Python dict repr, or serialized JSON.
  - No error is raised, so nothing alerts.
  - Joins, group-bys, and "shipments per carrier" reports go wrong.
- **Strict ingestion** (typed columns, JSON-schema validators, generated deserializers, ORMs):
  - Inserts fail and the receiver returns 4xx or 5xx.
  - Your retries then pile onto a broken endpoint.
  - Endpoints that hit your auto-disable threshold go dark.
- **Mixed history**: old rows hold a string and new rows hold an object, or a stringified object, in the same column. Backfills and BI queries have to special-case the cutover date.

Customers can't fix this on their own schedule because the change lands on your date, not theirs.

## 2. 🔴 Headers carry the metadata, so raw-body pipelines lose it

Event type, timestamp, and delivery id are in HTTP headers. Customers who write the payload "straight into their tables" are the ones most likely to drop headers. Consequences:

- **No dedupe key.** Retries create duplicate rows, and the cutover makes retries more likely (see §1).
- **No event type**, so they can't route or distinguish `shipment.created` from `shipment.updated`.
- **No event time.** They store receipt time instead, which is wrong for delayed or retried deliveries.

Nothing in the body tells a receiver which API version it is. The only way to detect the new shape is to sniff `typeof carrier`.

## 3. 🟠 The same event renders differently over time

Because the body is rendered at delivery time, not frozen at event time:

- A retry of a pre-cutover event that happens after cutover sends a different body under the same delivery id. Body-hash dedupe breaks, and a customer may end up with one shipment in two shapes.
- Manual resends and replays return the new shape for old events.
- If you sign the body, signatures stay valid but mean less. The signed content is not what was originally emitted.
- In-flight and queued events at the cutover moment are a mix of both shapes, with no clean boundary.

## 4. 🟠 The delivery log can't answer support's questions

The log stores the request body only:

- **Event type, timestamp, delivery id, and signature are missing** unless headers are stored somewhere else. Support can't look up "delivery X" or tell what a body was.
- **No version marker.** Logged bodies from before and after cutover are only distinguishable by sniffing `carrier`.
- **Resend semantics are ambiguous.** Re-render gives the new shape. Replaying the stored body gives the old shape to an endpoint you may have moved to the new version. Decide which is correct before launch.
- **Typed indexing may reject documents.** If log bodies go into Elasticsearch, BigQuery, or a typed JSON column, `carrier` changing from string to object can cause a mapping conflict and dropped writes.

## 5. 🟡 Other surfaces to check

- Subscription filters, routing rules, or alert rules that match on `carrier` as a string.
- CSV and report exports, and internal analytics on delivery-log bodies.
- SDK types, OpenAPI schema, docs examples, and sandbox and test events (a test event in the old shape will mislead).
- Any customer-side code that treats `carrier` as a string key (maps, switch statements, `LIKE` queries).

## What to do before cutover

1. **Pin the webhook version per endpoint.**
   - Store the version on the endpoint, defaulting new endpoints to the latest.
   - At cutover, set every existing endpoint to its previous version, not the new one.
   - Transform from one canonical event snapshot to the pinned shape at delivery, so retries and replays are stable.
2. **Prefer an additive change on webhooks.**
   - Keep `carrier` as a string in the pinned old version.
   - In the new version, consider `carrier` as the object only for opted-in endpoints.
   - Alternatively, add `carrier_details` and leave `carrier` alone for one deprecation window.
3. **Put identity in the body.** Add `id` (delivery or event id), `type`, `created_at`, and `api_version`, and keep the headers as well. This makes raw-body-to-table pipelines safe.
4. **Fix the log.** Store headers (minus secrets), the pinned version, and the rendered body. Define resend as either "same bytes" or "re-render at the endpoint's pinned version", and document it.
5. **Give customers a safe upgrade path.**
   - Add a per-endpoint version switch in the dashboard.
   - Add a "send test event in version X" button.
   - Optionally add dual-delivery (old and new to different URLs) for a canary period.
6. **Notify with detection signals, not announcements.**
   - Publish the exact diff and a before/after payload.
   - Email the endpoints that will be affected.
   - Warn on deliveries still using the deprecated shape, for example with a header such as `Deprecation` or `Sunset`, plus a dashboard banner.
7. **Track adoption.** Count endpoints by pinned version and watch 4xx/5xx rates per endpoint around the change. Name the stragglers and contact them directly before any forced removal.
8. **Check your own consumers.** Confirm that log indexing, internal analytics, and exports tolerate both shapes before the first new-shape event ships.

## Decision for you

Does the dashboard offer webhook version pinning today? If not, build it before shipping 2026-04-01. If you can't, don't change an existing field's type in webhooks. Add a new field instead.