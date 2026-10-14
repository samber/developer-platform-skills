Two decisions: keep the GitHub shape with tweaks, and do not fire all three events.

## 1. Event shape

Keep `X-Northwind-Event` plus `action` in the body. Change four things:

1. **Repeat the type in the body.** Use `"event": "invoice", "action": "paid"`. GitHub omits it, and consumers who queue or store payloads lose the header. Body-only data survives Kafka, S3, and log replay.
2. **Use one naming convention.** Your three examples use three styles (`invoice`, `customer_update`, `payrunExecute`). Fix it now, because names cannot change once customers subscribe.
   - Event is a singular lowercase noun: `invoice`, `customer`, `line_item`, `payrun`.
   - Action is a past-tense verb: `created`, `updated`, `paid`, `voided`, `executed`.
   - `customer_update` becomes `customer` + `updated`.
   - `payrunExecute` becomes `payrun` + `executed`.
   - Past tense states a fact that already happened. Consumers cannot mistake it for a command.
3. **Add an envelope** for an accounting product:
   ```json
   {
     "id": "evt_01J...",
     "event": "invoice",
     "action": "paid",
     "created_at": "2026-10-10T09:21:00Z",
     "api_version": "2026-10-01",
     "resource_version": 17,
     "data": { "invoice": { "...": "..." } }
   }
   ```
   - `id` is the idempotency key for the consumer.
   - `resource_version` lets consumers detect out-of-order delivery and drop stale events.
   - `api_version` lets you change payloads without breaking subscribers.
4. **Sign the raw body.** Use an HMAC in `X-Northwind-Signature` and include a timestamp to block replay.

Also decide these before launch:
- Subscription granularity: per `event`, or per `event.action`? Support both. GitHub's per-event-only filter is a known pain.
- Payload style: send a full snapshot or just IDs. For money data, send a snapshot with amounts as integer minor units plus currency.
- Delivery: promise at-least-once with retries. Offer a replay endpoint and a list-events API.

## 2. Line item changes

Do not fire all three. Firing them feels safe, but it creates three problems:

- **Double counting.** A consumer subscribed to both `invoice` and `line_item` applies the same change twice. In accounting, that means wrong totals.
- **Ordering races.** Three events arrive in any order. The `customer` event can land before the `invoice` event it depends on.
- **Cost.** Every consumer pays for 3x the traffic and 3x the dedupe logic.

Rule: fire one event per entity that actually changed state and has its own lifecycle. Do not fire cascade events.

For your case:

| Entity | Fire? | Why |
|---|---|---|
| `invoice.updated` | ✅ Yes | A line item is part of the invoice. Include the changed lines, plus a `changes` or `previous` block. |
| `line_item.*` | ❌ No | Only add it if line items have their own API endpoint and lifecycle. Then fire it instead of `invoice.updated`, not as well. |
| `customer.*` | ❌ No | The customer record did not change. A derived balance is not a customer change. |

If a consumer needs customer balance changes, add a deliberate `customer.balance_updated` event. It should fire only when you persist and expose that balance. Do not use it as a safety net.

Real safety comes from the delivery layer:
- at-least-once delivery with retries
- the event `id` for dedupe
- `resource_version` for ordering
- a replay endpoint for missed events

Also decide what an edit means on a finalized or paid invoice. Most accounting products block it and require a credit note. Then the right event is `credit_note.created`, not `invoice.updated`.

## Next action (about 15 min)

Write a one-page naming table: every entity, its actions, and one sentence on when each fires. Do it before any code. Paste it here and I'll review it for gaps and fan-out risks.