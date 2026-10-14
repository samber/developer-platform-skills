# Go/no-go for Vantle events: ❌ NO-GO on the docs as written, 🟢 GO on the ship date if the fixes below land by day 6

I only have your description of the docs, not the page itself. Your description fails both gates the webhook-platform-design skill uses, and both are cheap to fix in nine days.

## Gate 1: delivery contract completeness (fails)

All five facts must be written as findable sentences. A missing one fails the gate.

| Fact | Status from what you described |
|---|---|
| Delivery guarantee (at-least-once) | ⚠️ Not mentioned. Confirm it's stated, and that "exactly-once" appears nowhere. |
| Ordering position | ⚠️ Not mentioned. Without a best-effort statement, subscribers assume FIFO. |
| Retry schedule | ❌ One vague sentence. |
| Ack timeout | ⚠️ Not mentioned. |
| Dedup ID location | ⚠️ Not mentioned. Name the header or field, and say it stays the same across retries. |

## Gate 2: five-element docs rubric (fails)

| Element | Status |
|---|---|
| 1. Signature verification with runnable snippets | ✅ Present (Node and Python). Verify the content, see below. |
| 2. Event catalog with schemas and examples | ✅ Present. |
| 3. Retry policy, exact schedule | ❌ **Fails.** "We retry failed deliveries with exponential backoff" is the exact example the rubric rejects. |
| 4. Troubleshooting and failure recovery | ⚠️ Present, but it can't be right yet. Recovery docs depend on the retry span, the dead-letter retention, the auto-disable rule and the replay tooling. None of those are defined. |
| 5. Testing tools | ⚠️ Covers the CLI only. Check that it also covers a "send example event" action and a delivery log. |

The writer being happy and the docs being reviewed don't show that the contract is complete. Reviewers read what's on the page and can't see what's missing from it.

## Why a missing schedule matters

- Subscribers size their outage tolerance and their reconciliation jobs from the retry span. A span of 4 hours and a span of 27 hours need different handling.
- Anything left implicit becomes a subscriber assumption, then a support ticket.
- Your enterprise buyers will ask for this in writing during security review.

## Fix list, ordered by what blocks launch

1. **Day 1–2: confirm what engineering actually built.** Get the real retry schedule, ack timeout, dedup ID, dead-letter retention and auto-disable behavior. Docs must describe the implementation, not a wish. If the implementation is thinner than the defaults below, that is the real go/no-go risk: either engineering closes the gap or the docs state the weaker contract honestly.
2. **Day 2–3: replace the one sentence with a retry section.** Use this skeleton and fill the brackets from step 1:
   - Guarantee: at-least-once. Your handler may see the same event twice. Dedup on `[header/field]`, which is identical across retries.
   - Ordering: best-effort, not guaranteed. Don't infer order from timestamps.
   - Ack: return a 2xx within `[N]` seconds. Queue the work and respond fast.
   - Schedule: attempt 1 immediately, then `[exact intervals]`, total span `[X]`.
   - Response handling:
     - Non-retriable 4xx (anything except 408/429) goes straight to dead-letter.
     - A 429 with `Retry-After` is honored.
   - After exhaustion: the event is dead-lettered and kept `[7–30]` days. The endpoint is auto-disabled after `[rule]`, with an email or dashboard notice.
   - Default to start from if you have no schedule yet: a fixed exponential schedule spanning about a day. Svix's is immediate, +5s, +5m, +30m, +2h, +5h, +10h, +10h (about 27.5 hours). Shopify's 4-hour span is the short end. Your 9-day deadline favors the shorter, simpler span, but choose it against real subscriber outage durations.
3. **Day 3–4: rewrite the troubleshooting page against that policy.** It should cover:
   - How to read a failed delivery.
   - How to recover, using replay for events lost to a broken handler and retry for single attempts. Keep those two words distinct.
   - The "200-then-crash" blackhole.
   - A recommendation to reconcile periodically against your API for high-stakes events.
   - Only link to tooling that exists. If there is no delivery log or replay at launch, say so and give the reconciliation path.
4. **Day 4: check the signing section (element 1).** Having Node and Python snippets isn't enough. Confirm they:
   - Use HMAC-SHA256 over `id.timestamp.raw_body`.
   - Reject timestamps outside a tolerance window (about 5 minutes).
   - Verify against the raw body. Express needs `express.raw` on that route.
   - Exempt the route from session auth.
   - State "verify every request."
   - Describe rotation with overlapping secrets.

   If the signature covers the body only, there is no replay protection. Treat that as a launch blocker, not a docs problem.
5. **Day 4–5: widen the Testing section.** A CLI-only testing story serves code-first developers. No-code and workflow-tool users need a "send example event" action driven by each event type's schema, and visible recent deliveries. Test deliveries must be clearly marked as test events. If that tooling doesn't exist, ship the docs for what exists and mark it as a fast-follow.
6. **Day 5: check the catalog (element 2).** Confirm:
   - Event names follow one convention (`resource.action`, past tense).
   - Each event has an example payload.
   - The page states what happens to payloads when the API version changes.
   - It says whether child-resource events also fire parent events.
   - An endpoint with no filter receives every event.
7. **Day 6: re-run both gates.** Check the five contract facts are findable and all five docs elements exist. A cold read by someone who hasn't seen the docs, trying to answer the five facts in under five minutes, is a good test.
8. **Days 7–9: buffer.** Use them for engineering gaps found in step 1.

## What would flip this to a hard NO-GO

- Signatures that don't cover the timestamp. That is a design flaw, not wording.
- No stable per-event ID across retries. You can't retrofit it for subscribers who already built without it.
- Zero automatic retries, with no deliveries-list and redeliver API behind it.
- Engineering can't confirm the retry behavior by day 3.

## Decisions I need from you

- **What does engineering actually run today?** Retry schedule, ack timeout, dead-letter and auto-disable behavior. The whole plan hinges on this.
- **Is delivery built in-house or on a managed provider?** A managed provider already has a documented schedule you can copy.
- **Who are your consumers?** Enterprise integrators, typical API developers, no-code tools, or a mix? That sets how much weight the testing tooling gets.
- **Do you have a delivery log and replay at launch?** The troubleshooting page can only promise what exists.

Send me the docs page and the engineering answers and I'll write the finished retry section and check the other four elements against the page.