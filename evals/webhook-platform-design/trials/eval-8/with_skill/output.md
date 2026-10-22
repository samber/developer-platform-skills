# Tallyroom webhook plan: what to change, and retry vs replay

I read the `webhook-platform-design` skill and its signing and portal references. I haven't seen your current webhook code, event list or retry behavior, so the "needs checking" items below are assumptions to confirm.

## Verdict

1. ⚠️ **Don't push customer-facing UI to phase 2 as a whole.** A minimal slice of it is what answers "what does the payload actually look like". Pull two items into phase 1: a send-example-event button and a recent-deliveries list.
2. ⚠️ **The Grafana board can't stand in for that slice.** It serves your on-call, and no-code users never see it.
3. ✅ **Keep the docs page, but reorder it** (see below). The signing spec matters least to your biggest ticket source.
4. ✅ **Retry and replay are two different operations.** Name them that way and the argument goes away.

## Why the plan misses the 40%

The skill calls out your exact segment. No-code users think in catch URLs: "show me one real payload before I build against it." They never read the signing spec. They need test events and visible recent deliveries far more than prose.

Your plan gives them example payloads in docs, which is good. A static example only shows what a payload might look like. Their real question is what it looks like for their account, arriving at their automation tool's catch URL, so they can map fields. A "send example event" button answers that directly. It is schema-driven, so the example payload and the delivered payload can't drift apart.

## Phase 1 scope (minimum viable customer surface)

1. **Send example event**, per event type, to a chosen endpoint.
   - Mark test deliveries as test in a way a no-code user can see. For example, use a distinct event flag and a visible field in the payload.
   - The skill notes a common production bug: a sender left pointed at the test URL after setup. Clear labeling prevents that.
   - If you already have a sandbox or test mode, that's a separate concern. This is only the delivery-side button.
2. **Recent deliveries list** per endpoint.
   - Show status, event type and timestamp.
   - Per attempt, show request headers, body, response code and timing.
   - Store headers as well as the body. Your three signing headers (`webhook-id`, `webhook-timestamp`, `webhook-signature`) are part of what a faithful resend needs.
3. **Retry** (single delivery) from that list. See the naming section.
4. **Out-of-band notification** to the subscriber before you auto-disable an endpoint. Use email or the dashboard, since the webhook channel is the broken one.

Phase 2 can hold the rest: range replay with a cost confirmation, filtering by status, failure grouping, and an embeddable or branded portal.

**Build or buy.** The skill's default is managed sending infrastructure, such as Svix, Hookdeck or Convoy. Those ship this portal slice already, and Svix's App Portal has the send-example button and replay. Two things decide it:
- whether customer event data may transit a third-party processor
- your ship date versus how long you want to own this surface

Those are the two questions I'd need answered. Buying infrastructure doesn't remove the work on the event catalog, the contract and the docs.

## Docs page: reorder and complete it

The skill grades webhook docs on five elements, all required before launch. Your plan covers roughly two.

| # | Element | Your plan | Action |
|---|---|---|---|
| 1 | Signature verification with runnable snippets | "Full signing spec" | Adopt Standard Webhooks instead of documenting a bespoke scheme. Show runnable snippets. |
| 2 | Event catalog with schemas and example payloads | Example payloads | Put this first on the page. Generate it from the same OpenAPI 3.1 `webhooks` spec that drives delivery. |
| 3 | Retry policy, exact schedule | Missing | Add it. "We retry with backoff" doesn't count. |
| 4 | Troubleshooting and failure recovery | Missing | Add it. Cover the 200-then-crash blackhole and reconciliation against your API. |
| 5 | Testing tools | Missing | Add it. It's the send-example button and the deliveries list. |

Signing docs must cover three consumer pitfalls:
- Verify every request.
- Verify against the raw body, before any JSON parser touches it.
- Exempt the webhook route from session-auth middleware.

⚠️ Check whether the no-code tools your customers use can verify a signature at all. If many can't, tell them so. Don't present verification as a universal requirement they can't meet.

### The five delivery-contract facts (all must be written as findable sentences)

The skill's pass/fail gate is that each of these is documented explicitly. Fill in what you have, and decide the rest:

| Fact | Skill's default | Needs checking |
|---|---|---|
| Delivery guarantee | At-least-once. Never claim exactly-once. | What you do today |
| Ordering | Best-effort and non-guaranteed. Say so. | |
| Retry schedule | Exponential, spanning roughly a day (Svix: 8 attempts over about 27.5 hours; Shopify's 4 hours is the short end) | Current schedule |
| Ack timeout | About 10 seconds | |
| Dedup ID | `webhook-id`, the same value across retries of one event | Whether you already send a stable ID |

Also decide how to handle responses:
- 2xx acks and stops retries.
- Honor `Retry-After` on a 429.
- Send non-retriable 4xx (anything except 408 and 429) straight to the dead-letter queue.
- Retain dead-lettered events for 7–30 days.
- Document "queue fast, ack fast" for slow-but-correct handlers. No-code tools often do slow work.

## Grafana board (on-call): keep, and scope it

Build it for your own team. Put these on it:
- per-endpoint delivery success rate (the headline number)
- dead-letter rate, where a spike means an endpoint in sustained failure
- time-to-detect a failing endpoint, baselined from your first month and improved from there

Alert on the dead-letter rate and on endpoints about to auto-disable, and feed those alerts into the customer notification above. The board supports on-call. It does not replace anything the customer sees.

## Retry vs replay

Stop arguing about one word. The market uses both words interchangeably, which is why your team can't settle it. The skill says to adopt Hookdeck's definitions verbatim, because they name two different operations:

- **Retry**: a new delivery attempt of the **same event**.
- **Replay**: re-ingest the original as a **new event**.

Which one a button does depends on the `webhook-id` it sends:

| Action | `webhook-id` | Consumer dedup | Where it lives |
|---|---|---|---|
| **Retry** | Same | Works. A handler that already processed it ignores it. | The per-delivery button |
| **Replay** | New | Does not catch it, because the consumer sees a new event | Single-event and range replay, with a cost confirmation for large windows |

**Recommendation.**
- Label the per-delivery button **"Retry"**. It's the safe action for the common case (their handler was broken, now it's fixed), and it keeps dedup working.
- Add **"Replay"** in phase 2 for range and re-ingest, behind a cost confirmation. This is the action where consumers must expect duplicates, so label it clearly.
- Keep the two words in docs, UI and API strictly separate. That fixes the argument at its source.

⚠️ This only works if the stable per-event ID is real. If you don't send one today, "retry" can't promise dedup. Adding it is the first task, because consumers who already built without it can't be helped by a later retrofit.

## Open questions (they change the plan)

1. Which of the five contract facts exist today, and is webhook delivery already in production? Please share the current event list, retry behavior, signing scheme and delivery logging.
2. How many subscriber endpoints, and what's the peak events per second? This drives fan-out isolation and whether FIFO is even worth discussing.
3. May customer event data transit a third-party processor? This decides managed versus self-hosted versus in-house.
4. What's the ship date, and is this a quick feature or the integration surface for years?
5. Who are the remaining 60% of ticket openers? Enterprise integrators will want the contract in writing and may ask for FIFO and asymmetric signing. Typical API developers need verification snippets and a replay path.

## Next steps

1. Confirm whether `webhook-id` is stable across retries. About 30 minutes.
2. Answer questions 1, 3 and 4. Then decide build or buy for the portal slice.
3. Move "send example event" and "recent deliveries" into phase 1.
4. Draft the five contract sentences and the docs page in the new order.
5. Baseline the 40% ticket share now. Re-measure it 60 days after the slice ships. That tells you whether the test button fixed the ticket source.