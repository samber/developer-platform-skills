# Northwind Ledger: webhook event catalog design

I read `webhook-platform-design/SKILL.md` and `references/event-taxonomy-and-payload-design.md`. The skill asks for clarifying questions first. They are batched at the end, and everything below uses the stated assumptions.

## Verdict

1. **Don't copy GitHub's shape** (`X-Northwind-Event: invoice` header plus `{"action": "paid"}` in the body). Use `invoice.paid` as a single name.
2. **Rename all three example events** to `resource.action`, past tense.
3. **Don't fire all three events.** A line-item change fires one event, `invoice.updated`, and no `customer.updated`.

## 1. Why not the GitHub shape

The skill names this as the shape to avoid. Splitting the event name across a header and a body field means no single string names the event.

- **Subscriptions can't select by one name.** Subscribers pick events by catalog name. With a split, they would subscribe to `invoice` and then filter on `action` in their own code. Per-event filtering, docs, test events and delivery logs all get awkward.
- **Header-split envelopes need a header-capturing log.** If metadata rides in headers, your delivery log and replay must store headers and body, or replay is unfaithful. Build the log for that from day one.
- **GitHub's surrounding design is weak.** GitHub signs the body only, with no timestamp, so a captured request replays forever. It also does zero automatic retries. GitHub gets away with that only because it ships a deliveries API and "reconcile yourself" docs. The skill lists both as failure modes.
- **The familiarity argument is cheap to satisfy.** `invoice.paid` is the Stripe and Standard Webhooks convention. It is just as familiar to integrators, and arguably more so for an accounting product.

Keep the reusable lesson from GitHub: small body, metadata in headers. Do it the Standard Webhooks way instead:

- **Headers:** `webhook-id`, `webhook-timestamp`, `webhook-signature`.
- **Body:** `{ "type": "invoice.paid", "timestamp": "...", "data": { ... } }`.

## 2. Names

| Proposed | Problem | Use |
|---|---|---|
| `invoice` + `action: paid` | Name split across header and body | `invoice.paid` |
| `customer_update` | Underscore-joined, verb-first, present tense | `customer.updated` |
| `payrunExecute` | camelCase, verb-first, present tense | `payrun.executed` |

Rules for the catalog:

- Format: `resource.action`, action in past tense, dot-delimited, identifiers limited to `[a-zA-Z0-9_.]`. Pick this once and never mix conventions.
- **Pay run naming needs a decision.** "Executed" is ambiguous for a process that takes time. Prefer outcome events: `payrun.completed` and `payrun.failed`. Add `payrun.started` only if someone needs it.
- **Define the catalog before launch.** Each event gets a stable name, a description and a payload schema. An undocumented event is effectively unsubscribable.
- **Check each event against five principles:** self-contained, immutable (add fields, never repurpose), traceable, actionable, debuggable.
- **Versioning:** pick one camp. I'd recommend versioning the event type (`v2.invoice.paid` on a breaking change, additive-only otherwise). The alternative is pinning each endpoint to an API version, Stripe-style. Either is fine. Drifting into both, or letting an API version bump silently reshape stored payloads, is the failure.
- **Payload size:** keep it under about 20 KB. Decide thin vs full payloads once, platform-wide. For accounting, I'd go full (snapshot) plus `previous_attributes` on `*.updated` events, with money fields as minor units plus a currency code.

## 3. Line-item change: fire one event

Answer: fire `invoice.updated` only. Do not fire a line-item event unless line items are independently addressable resources. Never fire `customer.updated`.

**Rule to write down:** subresource events do not bubble to parent events. Stripe's answer is "never", so `customer.subscription.updated` fires no `customer.updated`. The skill's requirement is to state the rule either way, because silence breeds subscriber assumptions.

**Why firing all three is not safer:**

- **`customer.updated` would be false.** The customer record didn't change. Subscribers syncing a CRM or ledger on it would do wasted or wrong work.
- **Semantic duplicates can't be deduped.** At-least-once delivery already gives consumers exact duplicates, which they dedupe by `webhook-id`. Three events for one change have three different IDs, so they look like three distinct facts.
- **Ordering across the three is undefined.** Delivery is best-effort ordered. A consumer can see `invoice.updated` before the line-item event, or the reverse, and must handle both.
- **Load goes up threefold** on the fan-out path, and every slow endpoint gets three chances to fail.
- **The failure it protects against is better handled elsewhere.** What you really want is that a consumer never misses a change. Cover that with a retry schedule and DLQ, a replay API, and documented periodic reconciliation against your API. The skill treats reconciliation as vendor-endorsed practice.

**Concrete design:**

- Line items are part of the invoice. `invoice.updated` carries the full invoice, including `lines[]`, plus `previous_attributes` showing what changed.
- If you do expose line items as their own API resource, give them their own events (`invoice_line.updated`). Fire only the events for resources that actually changed, and still don't bubble to the customer.
- If a real consumer need appears (for example, "notify me when any invoice for customer X changes"), solve it with filtering. Don't solve it by emitting extra events. Filtering has two independent axes: event type, and recipient or channel scoping.

## 4. Delivery contract (five facts to publish)

These must be explicit in the docs. Missing any one fails the contract-completeness gate.

1. **Guarantee:** at-least-once. Never claim exactly-once.
2. **Ordering:** best-effort, not guaranteed. Subscribers must not infer order from timestamps.
3. **Retry schedule:** exponential backoff spanning roughly a day, with the exact schedule published. Honor `Retry-After` on 429. Send non-retriable 4xx (other than 408 and 429) straight to the DLQ. Auto-disable after sustained failure and notify out-of-band.
4. **Ack timeout:** about 10 seconds. Tell consumers to queue the work and return 2xx quickly.
5. **Dedup ID:** `webhook-id`, stable across retries of the same event.

Signing follows Standard Webhooks: HMAC-SHA256 over `{id}.{timestamp}.{raw_body}`, `whsec_` secrets, and multiple signatures per header so rotation has no downtime. Docs must cover three consumer pitfalls: verify every request, verify against the raw body, and exempt the webhook route from session auth.

## 5. What to ship around the catalog

- **Subscription states:** active, paused (subscriber-initiated), disabled (platform-initiated).
- **Portal:** delivery logs (headers and body), retry and replay as distinct operations, and a "send example event" button driven by each schema.
- **Docs:** the five-element rubric: signature verification snippets, catalog with example payloads, exact retry schedule, troubleshooting, and testing tools.
- **Build vs buy:** the default is managed sending infrastructure unless customer financial data may not transit a third-party processor, which is plausible for accounting. If it can't, that option is deleted from the menu. You would then self-host a gateway or build in-house. Buying infrastructure still leaves the taxonomy, contract and docs to you.

## Clarifying questions (please answer; they can change the above)

1. **Greenfield or retrofit?** If a GitHub-style shape already shipped to anyone, I need the current event list and retry and signing behavior.
2. **Scale:** how many subscriber endpoints, and what peak events per second?
3. **Consumers:** enterprise integrators, typical API developers, or no-code tools?
4. **Effort and data:** how much engineering and on-call capacity can you commit? May customer financial event data go to a third-party processor?
5. **Deadline:** when must webhooks ship, and is this a quick feature or the long-term integration surface?
6. **Streaming:** is any need really live client-side push? That would be a complementary WebSocket or GraphQL-subscription surface, not a webhook.
7. **Line items:** are they independently addressable API resources today?