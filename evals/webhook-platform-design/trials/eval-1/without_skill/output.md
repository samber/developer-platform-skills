# Draft reliability page, with one change to your opening sentence

**I didn't keep the opening sentence verbatim, because it promises something no webhook system can deliver.** Sentence-level fix first, then the page.

## Why the sentence can't ship

- **Exactly-once delivery is impossible over HTTP.** If your POST times out, you can't know whether the customer's endpoint processed it. You either retry, which risks a duplicate, or don't, which risks a loss. A retrying system, which you need, is at-least-once by construction.
- **Global ordering conflicts with retries.** If event A fails and event B succeeds, either B is delivered first or B waits behind A. Waiting behind A means one dead customer endpoint stalls everything behind it.
- **Enterprise buyers who ask about this tend to know the above.** Their security and legal reviewers will quote this sentence back to you in a dispute or SLA credit claim. A hard "guarantees" is also the wording most likely to carry contractual weight.

The question buyers are asking is really "will I lose events, double-charge, or process things out of order?" You can answer that truthfully and strongly:

> **Ledgerwise never silently drops an event, delivers each event at least once, and gives every event a stable ID and per-invoice sequence number so your system processes each event exactly once and in order.**

---

## Page copy

# Event delivery reliability

Ledgerwise sends outbound events to your registered endpoints when invoices, payments, and customers change. This page states what we guarantee, what we don't, and what you do on your side to get exactly-once, in-order processing.

## The short version

- **Every event is delivered at least once.** We keep retrying until your endpoint acknowledges the event or the retry window closes.
- **Duplicates can happen, and you can detect them.** Every event carries a unique `event_id`, identical across all retries.
- **Order is guaranteed per resource, not globally.** Events for the same invoice carry an increasing `sequence` number. Across different invoices, there is no ordering guarantee.
- **Nothing is dropped silently.** An event that can't be delivered is retained, visible in your dashboard, and replayable.

## What we guarantee

| Property | Guarantee |
|---|---|
| Delivery | At-least-once to every registered, healthy endpoint |
| Durability | Events are persisted before the originating API call returns [confirm: true in your architecture] |
| Retries | Exponential backoff for [X hours/days] [fill in actual schedule] |
| Identity | Stable `event_id` across retries |
| Ordering | Per-resource `sequence`, strictly increasing |
| Retention | Undelivered events retained [N days] and replayable [confirm] |
| Visibility | Delivery attempts, response codes, and failures shown per endpoint |

## What we do not guarantee

- **Exactly-once delivery.** No system that talks over a network can guarantee it. We deliver at least once and give you what you need to deduplicate.
- **Global ordering.** Events for different resources may arrive in any order.
- **Arrival order within a resource during retries.** If event 4 fails and event 5 succeeds, 5 can arrive first. Use `sequence` to detect this.
- **Delivery to endpoints that are down beyond the retry window.** Those events are retained and replayable, but not pushed again automatically.

## How to get exactly-once, in-order processing

1. **Deduplicate on `event_id`.** Store processed IDs, and ignore any you've already seen. Keep them at least as long as our retry window.
2. **Order with `sequence`.** For each resource, apply an event only when its `sequence` is the next expected one. If it's higher, hold it or fetch current state from the API. If it's lower or equal, it's stale, so ignore it.
3. **Acknowledge fast.** Return a `2xx` within [N] seconds, then process asynchronously. Slow responses are treated as failures and retried.
4. **Treat events as notifications when in doubt.** Fetching the resource from the API always gives the current truth.

## Scale and isolation

We currently deliver to about 1,400 customer endpoints and handle peaks of around 300 events per second. [Confirm whether you want to publish these numbers.] Each endpoint has its own delivery queue, so a slow or failing endpoint delays only its own events, never anyone else's.

## Failure handling

- **Endpoint returns non-2xx, or times out:** retried on the schedule above.
- **Endpoint fails persistently:** the endpoint is flagged in your dashboard and we notify your account contacts [confirm]. Events keep accumulating up to the retention limit.
- **Recovery:** after you fix the endpoint, replay missed events from the dashboard or API [confirm this exists].

## Monitoring and support

- Delivery logs per event and per attempt: [link]
- Status page: [link]
- Questions or incident reports: [contact]

---

## Before you publish

- **Every `[bracketed]` item is a placeholder, not a fact.** Fill in your real retry schedule, retention, timeout, and whether replay and per-endpoint queues exist. Don't publish a guarantee your system doesn't back.
- **Per-resource sequencing needs to exist.** If events don't carry a `sequence` today, add it before launch, or drop the ordering row.
- **Check the numbers with your CTO.** The 1,400 and 300/s figures are yours. Confirm you're comfortable making them public.
- **Pitch for the CTO:** "At-least-once with idempotency keys is what Stripe, GitHub, and Shopify document. Enterprise security teams read 'exactly-once' as a red flag, and they trust this model."

I can also draft a short sales-call answer to "do you guarantee exactly-once?" if that would help.