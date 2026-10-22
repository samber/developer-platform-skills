# What breaks when you cut API version 2026-04-01

Following `webhook-platform-design`, steps 2 and 6 and the failure-mode list. I read the SKILL.md and its event-taxonomy and subscription-lifecycle references. I did not read your code, so each finding below follows from what you described.

**Bottom line:** your current design is the failure mode the skill names: "An API version bump silently reshaping event payloads a subscriber already stores." Three choices combine to cause it:

- The delivery service renders the current API version.
- Customers persist the payloads.
- Your log can't replay what was actually sent.

## What breaks, ranked by blast radius

### 1. Existing customers' stored data breaks on cutover (critical)

- Every endpoint gets the new shape the moment the delivery service renders `2026-04-01`. `carrier` changes from `"UPS"` to `{...}` with no opt-in.
- Customers who write payloads straight into tables break in one of three ways:
  - **Hard failure:** a typed `VARCHAR` column rejects the object, inserts fail, and the endpoint returns 5xx. You then retry for roughly a day and eventually auto-disable healthy endpoints.
  - **Silent corruption:** ORMs and loose pipelines coerce the object to `"[object Object]"` or a JSON blob. Nobody notices until reports look wrong. This is the worst case, because your retry and DLQ machinery never fires.
  - **Downstream breakage:** joins, indexes, and dashboards keyed on `carrier = 'UPS'` stop matching.
- You can't fix this with a changelog entry. Customers on a pinned REST version don't expect their webhook shape to move.

### 2. You have no versioning policy for webhooks, only an accident

- The skill requires picking one camp deliberately:
  - **Camp 1:** pin each endpoint to an API version and render per that version (Stripe).
  - **Camp 2:** version the event type, with additive-only evolution otherwise (Svix and Standard Webhooks).
- "Render whatever the current API version returns" is neither camp. It is the ambient GitHub/Shopify default, which the skill says a deliberate choice replaces.
- Changing `carrier` from string to object is a repurposed field. The immutability principle says add fields, never repurpose them.
- **Recommendation: Camp 1.** You already date-version the API, so you likely have the per-version rendering machinery.
  - Store an `api_version` on every webhook endpoint.
  - Freeze every existing endpoint at its pre-cutover version.
  - Default new endpoints to the current version.
  - Let customers upgrade per endpoint, after they've seen test events in the new shape.
- Camp 2 is the alternative if you'd rather avoid carrying old renderers. It would mean `v2.shipment.updated`, with both types emitted during a deprecation window. It costs more catalog and duplicate-delivery overhead for a single field change.

### 3. Your delivery log can't replay or debug what was sent

- Your metadata (event type, timestamp, delivery id) is in headers and the log stores only the body.
- This is a named anti-pattern: "A delivery log that stores only the body while the envelope carries metadata in headers."
- Consequences:
  - A replay can't reconstruct the original event, because it has no type, id, or timestamp.
  - Support can't answer "what did we send customer X on March 3?" or "which shape did they get?"
  - Any signature check is unverifiable after the fact. This matters if you sign over `{id}.{timestamp}.{body}`, as Standard Webhooks does.
- The skill says to build the log for this from day one. Fix: store the exact request, meaning headers plus raw body bytes, per attempt, with response code and timing.

### 4. Render-at-delivery means events aren't immutable and retries straddle the cutover

- Because you render at delivery time, an event created before the cutover and retried after it goes out in the new shape. Your retry span is likely hours to a day.
- The same event ID can therefore arrive in two different shapes.
- A replay of a three-month-old event also comes out in today's shape.
- Fix: render once, at emit time, and persist the rendered payload per endpoint version. Retries and replays then resend identical bytes. The skill notes Stripe's rule that retrieving an old event under a newer version doesn't reshape it retroactively.

### 5. Webhook shape and REST shape can disagree

- Customers who reconcile via your API, which the skill recommends for high-stakes events, call REST under their own pinned version.
- If the webhook endpoint is pinned differently from the API key, the same shipment has a string `carrier` in one place and an object in the other.
- Fix: make the webhook version visible and settable, and document the relationship to the REST version.

### 6. Consumers can't tell which shape they received

- Version metadata isn't mentioned in your envelope, and your metadata lives in headers.
- Add a version marker, for example an `api-version` header plus a field in the body, so consumers can branch their parsers during migration.

### 7. Docs, test events, and catalog drift

- The event catalog, example payloads, and "send example event" must all render per endpoint version.
- If test events always use the latest shape, a customer testing on a pinned endpoint sees something their endpoint will never receive.
- Publish the per-version schemas from the same OpenAPI 3.1 `webhooks` spec that drives delivery, so docs and payloads can't drift.
- Your no-code customers will see the new shape only if you show it to them. They rely on test events and visible recent deliveries, not on prose.

### 8. Lesser issues

- **Payload size:** embedding the full shipment plus a nested carrier object grows every payload. Stay under about 20kb.
- **Longer term:** consider thin payloads (event id plus resource id). They remove this entire class of problem, because the notification never changes shape when the API version bumps. Stripe's dual-run pattern (emit both flavors with a discriminator field) is the way to migrate later.

## Things I couldn't verify (answers change the plan)

1. **Is your `delivery id` the same across retries of one event?** If it changes per attempt, customers can't dedup, which is another named anti-pattern. They also have no stable event ID to key their tables on. Please check this before anything else.
2. **Do you sign deliveries, and over what?** If the signature covers the body, it must be computed over the exact bytes sent for that endpoint's version.
3. **Has `2026-04-01` already shipped to the delivery service?** Today is 2026-10-10. If the renderer already serves it, finding 1 may be live. Check endpoint error rates and customer tables now.
4. **How many endpoints, and which consumer types?** This decides how aggressive the forced-upgrade deadline can be.

## Recommended sequence

1. **Stop the bleed:** if not yet live, hold the webhook renderer on the old version. If live, roll webhooks back to the old shape for existing endpoints.
2. **Add `api_version` per endpoint** and pin every existing endpoint to its pre-cutover version.
3. **Render at emit time** and persist the payload, headers, and raw body per attempt, with a version marker.
4. **Ship version-aware test events and docs**, so customers can preview the new shape on a pinned endpoint.
5. **Announce a dated migration path** with a per-endpoint upgrade control and a sunset date for the old shape.
   - Use `version-migration-guide` for the write-up.
   - Use `api-versioning-policy` for the longer-term policy.
6. **Evaluate thin payloads** for the next major event-schema revision.

Two checks to pass before launch, per the skill:

- **Contract completeness:** the guarantee, ordering position, retry schedule, ack timeout, and dedup ID location are all documented.
- **Docs rubric:** the five elements exist (signature verification, event catalog, exact retry schedule, troubleshooting, testing tools).