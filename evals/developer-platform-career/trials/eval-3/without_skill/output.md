**Do now (5 min):** email the recruiter. Ask for:
1. The full agenda: every round, its length, and who interviews you.
2. Whether a take-home or live coding round exists.
3. Whether the API design round is whiteboard, doc-based, or written in an editor.

**Take-home:** I can't know. I have no information on Perron's process. An onsite already booked after a screen usually means no take-home. Senior backend loops often include a live coding round the email doesn't name, so prepare a light one (Day 8). Don't skip it.

**Your plan has one flaw.** System design and API design are different skills. Your list covers system design only.

| | System design | API design |
|---|---|---|
| Question | How does it scale and survive failure? | What contract do clients depend on for years? |
| Judged on | Components, trade-offs, capacity, failure modes | Resource model, errors, idempotency, pagination, versioning, compatibility |

For a payments company, API design is likely the harder round. Your list covers none of it. Sharding and load balancers matter less than money-moving correctness.

Assumed budget: about 2–3 h/day. Day 1 is today (Thu Oct 8). Onsite is about Sat Oct 17, so confirm the date.

## Nine-day list

1. **Day 1, Oct 8: agenda and baseline.**
   - Send the recruiter email.
   - Read Stripe's API docs on idempotent requests, errors, pagination, versioning, and webhooks. This is the closest public model for Perron.
   - Skim Perron's public docs, API reference, and changelog, if they have them.
   - Write 5 guesses at what the API platform team owns.

2. **Day 2: API design core.**
   - Resource modeling: nouns, sub-resources, and actions such as `POST /payments/{id}/capture`.
   - Pagination: cursor vs offset, and why.
   - Error model: stable machine codes, retryable vs not.
   - Practice: design a Payments API from scratch in 45 min, then compare with Stripe.

3. **Day 3: API design, payments depth.**
   - Idempotency keys. Know the storage, the key scope, the replay response, and the concurrent-duplicate race.
   - Webhooks: signing, retries with backoff, ordering, replay, and at-least-once delivery.
   - Versioning and deprecation: additive changes, pinned versions, breaking-change policy.
   - Rate limiting and per-merchant quotas.
   - Practice: design the refunds API and webhook system.

4. **Day 4: money correctness.** This is the core of system design for payments.
   - Payment state machine: authorize, capture, settle, refund, dispute.
   - Double-entry ledger, and why you never mutate balances in place.
   - Exactly-once effect built from at-least-once delivery plus idempotency.
   - Outbox pattern, sagas, and reconciliation against processors and banks.
   - Timeouts: when a processor call times out, you don't know whether it succeeded. Be ready to explain what you do then.

5. **Day 5: your original list, focused.**
   - Consistency models: where you need serializable, where eventual is fine.
   - Sharding: shard by merchant, hot-merchant skew, resharding.
   - Cache invalidation: why you don't cache balances.
   - Load balancing: L4 vs L7, health checks, retries.
   - Add queues, and Kafka delivery semantics.
   - Don't over-invest here. It's the commodity part.

6. **Day 6: system design mock 1.**
   - Prompt: design a payment processing service. 45 min, timed, out loud.
   - Cover requirements, API, data model, flow, failure modes, then scale.
   - Self-review against Day 4.

7. **Day 7: mock 2 and an API mock.**
   - System design prompt: design a webhook delivery platform.
   - API design prompt: design a subscriptions/billing API, including proration and plan changes.
   - If possible, run one with a friend or Claude playing interviewer.

8. **Day 8: coding and behavioral.**
   - 1 hour of practical coding. Think rate limiter, retry with backoff, idempotency store, or an LRU cache. Use clean code in your strongest language.
   - Prepare 4 stories from senior-level work: an incident, a cross-team API change, a disagreement, a mentoring example.
   - Prepare 5 questions for them, such as how they handle breaking changes with large merchants.

9. **Day 9, Oct 16: light day.**
   - Re-read your own notes only. No new material.
   - Do one 20-min sketch of a payments flow from memory.
   - Check logistics: address, time, ID, and who you meet.
   - Sleep.

**Interview habits for both rounds:**
- Start with clarifying questions: who the clients are, volume, and the correctness bar.
- Say trade-offs out loud.
- In API design, say which choices are hard to undo, and why.

**Next:** send the recruiter email now, then open Stripe's idempotency docs.