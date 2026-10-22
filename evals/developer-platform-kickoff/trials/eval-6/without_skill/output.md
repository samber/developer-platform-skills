# What to do first

**Fix the triple charge first. Treat the callback duplicates as a separate, second piece of work.** They are the same family of problem but not one fix, and the charge is the one costing a customer money now.

## Why not "one fix"

| | Triple charge | Duplicate callbacks |
|---|---|---|
| Direction | Inbound: customer to us | Outbound: us to customer |
| Who retries | Their client library | Our delivery system |
| Who must dedupe | **Us**, on `POST /jobs` | **Them**, with a key we supply |
| Can it be eliminated? | Yes, with idempotency keys | No. At-least-once delivery means duplicates are inherent. We can only make them detectable and rarer. |
| Severity | Money, trust, possible refund or dispute | Annoyance, plus a workaround that already works |

The shared principle is that every retryable operation carries a stable identity, and the receiver dedupes on it. You can give your VP that as the "one fix" in the sense of one design rule. It still ships as two changes.

## Order of work

### 0. Today: remediate the customer (about 1 hour)
- Refund the two extra charges and confirm with the customer.
- Query for other cases: same account, same payload, several `POST /jobs` within a short window, each with a charge. Check whether this customer is the only one hit.
- Check what the 30s timeout really was. If the job succeeded but the response was slow, find out why.

### 1. This sprint: idempotency on `POST /jobs`
1. Accept an `Idempotency-Key` header and scope it per account.
2. Insert the key with a **unique constraint** in the same DB transaction that creates the job. A check-then-insert is a race.
3. Store a hash of the request body with the key and the final response. On replay:
   - **Same key, same body:** return the original response with the original job ID.
   - **Same key, different body:** return 422.
   - **Same key, still in flight:** return 409 or make the request wait. The 30s timeout means this case will happen.
4. Keep keys for at least 24h. Use a TTL you can justify.
5. Make the charge idempotent too. Pass a key derived from the job ID to the payment provider, so a bug in layer 3 cannot double-bill.
6. Decide what happens for clients that send no key:
   - **Optional now:** this is the lowest-risk step. It does not protect the customer who got charged unless their client sends a key.
   - **Required later:** require it once clients have had time to adopt it, or derive a fallback fingerprint.
7. Document it, and tell the affected customer exactly what header to send.

Tests to write:
- The retry after a successful-but-timed-out request.
- Two concurrent identical requests.
- A crash between job creation and response.
- An empty key.
- A key reused with a different body.

### 2. Next, in parallel with step 1: triage the callback duplicates (about half a day)
Find out which kind of duplicate it is before changing anything:
- **Same event ID, several delivery attempts.** This is normal at-least-once behavior. Our retry fires after a slow or timed-out customer response that actually succeeded. The fix is to ship a stable `event_id` and an `attempt` number in every delivery, then document the contract.
- **Different event IDs for the same logical event.** This is a bug in our producer, for example the event emitted twice or two workers racing. Fix the root cause.
- **Worker crash after send, before the ack is recorded.** This needs a lease or visibility timeout review. It is still at-least-once, so it also needs the stable ID.

Then:
1. Publish the contract: "Delivery is at-least-once. Dedupe on `event_id`." This validates the dedupe table your customer already built and lets other customers stop building their own.
2. Retry only on non-2xx or timeout, with backoff, and make the timeout generous enough that slow-but-successful endpoints do not trigger a retry.
3. Optionally give customers a delivery log with a replay button.

## What to tell your VP

> "Both incidents come from the same cause: retries without a stable identity. The principle is the same for both, but the fixes sit on opposite sides of our API. The billing duplicate is a bug that costs money, so I'm fixing it first with idempotency keys on `POST /jobs`. The duplicate callbacks can't be eliminated, because at-least-once delivery is standard. I'll make them detectable with a stable event ID and a documented contract, after I confirm whether any of them are our own bug."

## Open questions
- Is the charge triggered inside `POST /jobs` or by a later async step? This changes where the idempotency record must be written.
- Do you control the client library, or is it the customer's own?
- Do you know the duplicate callbacks' event IDs? If they are identical across the duplicates, that is the quick win.