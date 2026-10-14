**Verdict:** the design has a bug and the copy can't ship. Approve the replacement copy in section 4, not marketing's draft.

## 1. Root cause

Two mistakes combined.

1. The PSP charge is an external side effect inside a DB transaction. A rollback can't undo a card charge.
2. The idempotency key lived in the same transaction. The crash rolled it back with everything else. On retry the key was missing, so the handler ran again.

Probably also true, so check it: the key was never forwarded to the PSP. If it had been, the PSP would have deduplicated the second charge.

## 2. Fix

Split the handler into short transactions around the external call. Never hold a transaction open across the PSP or the mail provider.

1. **Tx 1: record intent, then commit.** In one short transaction, do three things:
   - Insert the idempotency record `(account_id, key)` with a unique constraint, the request body hash, and status `in_progress`.
   - Insert the subscription with status `pending`.
   - Generate and persist `psp_idempotency_key`. Generate it once here. Never regenerate it per attempt.
2. **Call the PSP outside any transaction.** Send `psp_idempotency_key` on the charge. Set metadata `subscription_id` so the charge is findable later.
3. **Tx 2: record the outcome, then commit.** In one transaction:
   - Set the subscription to `active` (or `failed`).
   - Store the `charge_id`.
   - Insert an `outbox` row for the receipt email.
   - Mark the idempotency record `completed` and store the response.
4. **Send the receipt from an outbox worker.** The worker retries until it succeeds. Pass a provider idempotency key if the provider supports one, derived from the `charge_id`. Delivery is at-least-once, so a rare duplicate receipt is acceptable. A duplicate charge is not.
5. **Treat PSP timeouts as unknown, not failed.** Set the state to `charge_unknown`. Never retry the charge blindly. Resolve it by looking up the PSP charge by key or metadata, or from the PSP webhook.
6. **Run a reconciler.** A sweeper finds `pending` and `charge_unknown` subscriptions older than N minutes (start with 5). It asks the PSP what happened and finishes Tx 2 or marks the subscription `failed`. The PSP webhook feeds the same code path.

### Retry rules for the API

| Situation | Response |
|---|---|
| Same key, same body, `completed` | Replay the stored response |
| Same key, same body, `in_progress` | `409` with `Retry-After`, or resume the state machine |
| Same key, different body | `422` |
| Key older than retention | Treat as new, after the PSP lookup in step 5 |

### Crash analysis

| Crash point | State on restart | Retry outcome |
|---|---|---|
| Before Tx 1 | Nothing stored | Clean run |
| After Tx 1, before PSP call | `pending`, no charge | Resume and charge once |
| After PSP charge, before Tx 2 (last week's bug) | `pending`, charge exists | The PSP key returns the same charge, then Tx 2 runs. No double charge. |
| After Tx 2, before email | Outbox row exists | Worker sends the email |
| After email, before outbox mark | Outbox row still unsent | Duplicate receipt possible. Acceptable. |

### Tests (about half a day)

- Use a fake PSP that charges and then drops the connection. Run the exact incident. Assert exactly one charge.
- Inject a crash at each row of the table above.
- Fire two concurrent requests with the same key.
- Retry with the same key and a different body.
- Break the code on purpose: remove the PSP key, and confirm the test fails.

### Cleanup now

1. Refund last week's duplicate charge.
2. Audit for other duplicates. Look for charges with the same customer and amount within a short window, and for PSP charges with no matching subscription row.

## 3. Copy review: "guaranteed exactly-once delivery, powered by idempotency keys"

**Not approved.** Three problems:

1. **Technically false.** Exactly-once delivery is impossible over an unreliable network. Idempotency keys give at-most-one effect per key, so duplicates are suppressed. They don't guarantee a request arrives once. Our webhooks and receipt emails are at-least-once.
2. **"Guaranteed" is a promise.** Customers and lawyers read it as an SLA. Last week's incident is a counter-example.
3. **It hides conditions.** The client must send the key, reuse it on retry, stay within the retention window, and keep the body identical.

## 4. Replacement copy

> **Retry safely with idempotency keys.**
> Send an `Idempotency-Key` header with each `POST /v1/subscriptions`. If a request times out or your client retries, we return the original result instead of creating or charging a second time. Keys are kept for **[retention period, to be confirmed by engineering]**.
>
> *Webhooks and email receipts are delivered at least once. Use the event ID to deduplicate.*

Words to avoid: "guaranteed", "exactly-once", "never charged twice".

## 5. Order of work

1. **Now, about 15 minutes:** send marketing the verdict and the replacement copy.
2. **Now, about 15 minutes:** refund the duplicate charge and start the duplicate audit.
3. **Then, 2 to 3 days with tests:** ship the redesign.
4. **After the redesign is live:** publish the new page. Don't publish an idempotency claim before the fix is in production.

**Next action:** confirm the retention window with the PSP docs and fill the placeholder in section 4.