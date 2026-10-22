# Why the opening sentence can't stay as written

I wrote the page without "Ledgerwise guarantees exactly-once delivery of every event, in the order the events occurred." Both halves are claims your system can't keep.

- **Exactly-once:** If a customer's server processes an event and crashes before it returns 200, you have to retry, and the customer sees the event twice. Every "exactly-once" claim in this market is at-least-once delivery plus dedup tooling. Printing it as a guarantee on a reliability page gives enterprise buyers a sentence to quote back at you after the first duplicate.
- **In order:** With retries and parallel workers, strict ordering means one failing endpoint blocks its whole queue. Stripe, Svix, Shopify and GitHub all document best-effort ordering for that reason.
- **Your scale:** At about 1,400 endpoints and 300 events/s peak, one slow customer must not delay the other 1,399. Per-endpoint isolation is incompatible with a global ordering promise.

Instead, the page opens with the sentence below. It answers the same buyer question, "will we lose events, and can we handle duplicates and ordering?", with a contract you can defend:

> **Ledgerwise delivers every event at least once, with a stable event ID on every delivery so duplicates are safe to discard. Ordering is best-effort, and each event carries what you need to put it back in order.**

For the CTO: the honest contract is the stronger sales asset. Enterprise buyers who ask about this on every call know exactly-once doesn't exist. A written retry schedule, a dedup ID and a replay button read as engineering maturity. A false guarantee reads as marketing.

**Before publishing**, check the bracketed `[confirm]` items against what you actually run. I proposed values (retry schedule, retention, auto-disable window) but could not see your system, and the page must match reality.

---

# Event delivery reliability

*Ledgerwise outbound events (webhooks)*

Ledgerwise delivers every event at least once, with a stable event ID on every delivery so duplicates are safe to discard. Ordering is best-effort, and each event carries what you need to put it back in order.

## The delivery contract

| Question | Answer |
|---|---|
| **Delivery guarantee** | At-least-once. We retry until your endpoint acknowledges. |
| **Duplicates** | Possible. The `webhook-id` header is identical across every retry of the same event. Use it to deduplicate. |
| **Ordering** | Best-effort, not guaranteed. Retries and parallel delivery can reorder events. |
| **Acknowledgement** | Return any `2xx` within **10 seconds**. |
| **Retry schedule** | 8 attempts over about 27.5 hours (exact schedule below). |
| **Dedup ID location** | `webhook-id` HTTP header. |
| **Signing** | Standard Webhooks (HMAC-SHA256, replay-protected). |

## Duplicates: how to handle them

If your server processes an event but fails before replying `200`, we can't know it succeeded. We retry, and you receive the event again. This is inherent to any reliable delivery system.

1. Read `webhook-id` from the request headers.
2. Check whether you have already processed that ID. A unique-keyed table or a short-lived cache works.
3. If yes, return `200` and do nothing.
4. If no, process the event, record the ID, and return `200`. Record the ID in the same transaction as your side effect where you can.

Return `200` fast. Queue the work and acknowledge. A slow handler looks like a failing one once you pass the 10-second timeout.

## Ordering: how to handle it

We don't guarantee order. A retried `invoice.created` can arrive after the `invoice.paid` that followed it. Don't infer order from arrival time or from `webhook-timestamp`, which is the delivery attempt time.

Instead:
- Treat each event as a notification, then read the current state of the object from the Ledgerwise API when order matters.
- Compare the object's `[version / updated_at field — confirm]` against what you hold, and ignore events older than your stored state.

`[Confirm: if you offer per-endpoint FIFO as an opt-in, document it here with its tradeoff: one failing delivery blocks that endpoint's queue. If not, delete this note.]`

## Retries

We retry with exponential backoff, never at a fixed interval, so a struggling endpoint isn't hammered. `[confirm schedule]`

| Attempt | Delay after previous failure |
|---|---|
| 1 | Immediately |
| 2 | 5 seconds |
| 3 | 5 minutes |
| 4 | 30 minutes |
| 5 | 2 hours |
| 6 | 5 hours |
| 7 | 10 hours |
| 8 | 10 hours |

That is about 27.5 hours, enough to cover a deploy gone wrong or a multi-hour outage.

How we treat your responses:
- **`2xx`:** Acknowledged, no more retries.
- **Timeout, `5xx`, connection error:** Retried on the schedule.
- **`429` with `Retry-After`:** We honor your stated delay instead of our own schedule.
- **Other `4xx` (except `408` and `429`):** Treated as permanent. We don't retry. The event goes to the dead-letter queue.

Each endpoint is delivered and retried independently. A slow or failing endpoint never delays delivery to anyone else.

## When delivery fails for good

An event is dead-lettered in exactly two cases: the 8 attempts are exhausted, or your endpoint returned a permanent `4xx`.

- Dead-lettered events are kept for **`[30]` days** with full headers and body, and can be replayed.
- After **`[sustained failure window, e.g. 5 days of consecutive failures]`** we disable the endpoint and notify your account admins by **email and in the dashboard**. We don't use the webhook channel, since it's the thing that's broken.
- Re-enable the endpoint from the dashboard or API, then replay what you missed.

## Replay and retry

- **Retry:** Another delivery attempt of the same event. The `webhook-id` is unchanged.
- **Replay:** Re-sends a stored event from the log as a new delivery, from the dashboard or API. You can replay a single event or a time range. Large ranges ask for confirmation first.

Replayed events keep their original `webhook-id`, so your dedup logic still applies. `[confirm]`

## Reconcile high-stakes events

For events that move money (`invoice.paid`, `payment.failed`, `[others]`), run a periodic reconciliation job. List recent invoices through the Ledgerwise API and compare them with what you processed. This is our recommended practice, not a workaround. It catches the cases retries can't, such as an endpoint that acknowledged an event and then lost it.

## Verifying signatures

Every delivery follows [Standard Webhooks](https://www.standardwebhooks.com/). Three headers:

```
webhook-id: msg_2KWPBgLlAfxdpx2AI54pPJ85f4W
webhook-timestamp: 1706100000
webhook-signature: v1,K5oZfzN95Z9UVu1EsfQmfVNQhnkZ2pj9o9NDN/H/pI4=
```

The signature is `base64(HMAC-SHA256(secret, "{webhook-id}.{webhook-timestamp}.{raw_body}"))`, prefixed `v1,`. Your secret starts with `whsec_`.

1. Verify every request, including handlers that only post a notification.
2. Verify against the raw body, before any JSON parser touches it. In Express, use `express.raw({ type: 'application/json' })` on the webhook route.
3. Reject deliveries whose `webhook-timestamp` is more than **5 minutes** from your clock. This blocks replayed captures.
4. Exempt the webhook route from session-auth middleware. It authenticates by signature.

Secret rotation has no downtime. During a rotation we sign with the old and new secrets at once, and `webhook-signature` carries both, space-separated. Deploy the new secret, confirm deliveries verify, then revoke the old one. `[confirm; ed25519 asymmetric signing (whpk_/whsk_) if offered]`

`[Add runnable verification snippets: Node, Python, Go.]`

## Event catalog

Events are named `resource.action` in the past tense, for example `invoice.paid` and `invoice.voided`. Every event type has a documented schema and example payload in the [event catalog `link`].

- Endpoints with no event filter receive **all** event types. Select the events you want to avoid noise.
- Subresource events do not bubble to parent events `[confirm]`.
- Fields are only ever added. We never repurpose or remove a field in an existing event type. A breaking change ships as a new event type name.

## Debug and test

In the dashboard:
- **Delivery log:** filter by endpoint, event type and status. Open any attempt to see request headers, body, response code and timing.
- **Send example event:** pick any event type and send a realistic sample payload to your endpoint, before you write handler code. Test deliveries are clearly marked as test events.
- **Failure alerts:** exhausted deliveries are grouped by endpoint and status code, with notification.

A handler that returns `200` and then throws has told us delivery succeeded. We can't see inside it. That's the case reconciliation exists for.

Endpoint changes can take a minute or two to reach the delivery path. That's expected.

Endpoint states: **active**, **paused** (you stopped it, configuration kept) and **disabled** (we stopped it after sustained failure). Deleting an endpoint discards its delivery state. Recreating it starts fresh, so pause it instead if you only want to stop deliveries.

## Our commitments

`[Only if your SLO backs them, otherwise omit.]` We track per-endpoint delivery success rate and dead-letter rate. `[Status page link]` shows delivery incidents caused on our side.

---

## Open items before this ships

1. **Verify every bracketed value against production.** The retry schedule, retention, auto-disable window and replay behavior are proposals borrowed from Svix's documented design. The page is a contract, and each wrong number is a future support ticket.
2. **Decide on managed or in-house delivery.** At 300 events/s across 1,400 endpoints, it is worth asking whether you want to operate the retry, dead-letter and portal machinery yourself. Managed infrastructure (Svix, Hookdeck or Convoy class) is the default unless customer event data can't transit a third party. I didn't have your answer to that, so the page doesn't depend on it.
3. **Ship the supporting features before the page.** The page promises a stable `webhook-id`, a delivery log with replay, and test events. If any is missing at launch, cut that section rather than publish it.
4. **Questions I could not ask, which would change the page:**
   - Is this greenfield or a retrofit of an existing system?
   - Are your consumers mostly enterprise, typical API developers or no-code tools?
   - What is your ship date?