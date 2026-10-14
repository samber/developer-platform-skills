**Move "Send test event" from phase 2 to phase 1. It fixes the 40% of tickets that your docs page and Grafana board don't touch.**

I didn't read anything under `skill-wip/`. I haven't seen your ticket data, so the ticket analysis rests on your 40% figure and what you described.

## Why the current plan misses the ticket driver

1. **No-code tools need a live sample to build.** Zapier, Make and n8n generally map fields from a real incoming request. The user creates the catch-hook URL, then the tool waits for a sample. Nothing can send one until the user triggers a real booking in Tallyroom. Reading a docs page doesn't unblock that, and this is why they ask "what does the payload look like" before building anything.
2. **A signing spec is for engineers.** No-code users mostly can't verify HMAC. In Zapier's Catch Hook it takes a code step. They need a simpler option or a clear "skip signing" path.
3. **A Grafana board is internal.** It helps your on-call. The customer who asks "did my webhook fire, and what did it send?" still can't see anything.

## Phase 1 (do now, in this order)

1. **"Send test event" button** next to each webhook endpoint.
   - Event type picker, default `booking.created`.
   - It sends a realistic, clearly fake payload (`"test": true`, an obvious sample name) through the real delivery path and signs it like a real event.
   - Time estimate for engineering: small if you already have a delivery queue (days, not weeks). Verify that against your code.
2. **Minimal customer-facing delivery log.** The last 7 to 30 days per endpoint, showing:
   - event type
   - timestamp
   - HTTP status your endpoint received
   - response snippet
   - the exact payload sent
   - a copy button on the payload

   This is the same UI as the resend button, so it's the smallest useful slice of "customer-facing UI".
3. **Docs page.** Keep it, but reorder it:
   - Start with "Connect Zapier / Make / n8n in 3 steps", using the test-event button.
   - Then show one real example payload per event type, copyable, generated from the same fixtures as the test button so they can't drift.
   - Then the field reference.
   - Then the signing spec as its own section, labeled "for custom code".
4. **No-code signing path.** Decide one option and document it:
   - a per-endpoint secret header the tool can match with a filter step, or
   - optional signing, with a stated trade-off.

   Don't leave no-code users staring at a spec they can't implement.
5. **Grafana board.** Keep it for on-call. Track delivery success rate, p95 latency, retry count and queue age. Add one panel for test-event usage, because it tells you whether the fix works.

## Phase 2

- Self-serve alerts on endpoint failures
- Bulk replay after an outage
- Filtering and search in the log

## Retry vs replay: stop arguing

The two words mean different things. Assign them:

| | Retry | Replay |
|---|---|---|
| Meaning | Re-attempt a **failed** delivery | Re-send an event that **already succeeded** or is old |
| Where | Per-row button, shown only on failed rows | Phase-2 bulk action, with date range |
| Risk | Low | Duplicates in the receiver, such as double Google Sheets rows |
| Confirmation | None | Required, with a warning |

**Decision: the per-delivery button says "Retry", shown on failed rows only.**

- Your automatic system already retries, so the word matches how users think about failure.
- Replay is reserved for the later bulk action, where duplicate risk is real.
- Optionally, show a secondary "Resend" on successful rows with the duplicate warning. "Resend" is the word customers use in tickets.

**Semantics to lock down, whatever the label:**

- The same event ID and the same payload.
- A new delivery attempt ID.
- A fresh signature timestamp.
- Document that receivers must dedupe on event ID.
- Show in the log that a manual retry happened, so support can see it.

## Success check

Measure in the 4 weeks after launch:

- "What does the payload look like" tickets: expect a large drop. Set the target yourself from your current weekly baseline.
- Share of new endpoints that receive a test event before their first real one.
- Time from endpoint creation to first successful delivery.

If the first ticket category doesn't fall, interview five of those customers. The sample-payload need may be hiding a different blocker.

**Next step (about 10 minutes):** pull the last 30 tickets in that 40% bucket and tag each with the tool the customer was wiring in. If Zapier, Make and n8n cover most of them, the plan above holds.