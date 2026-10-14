## Short answer

Don't ship the engineer's proposal, and don't send the PM's email as the fix. Make the server handle a retry that arrives while the first attempt is still running. The 10-second rule is a different fix from that one, and it fails here.

## Why the 10-second rule fails

In your incident the first attempt was alive at 40s, and the client retried at 10s. Under the proposed rule, the retry arrives with a key that has no response and is older than 10s, so it is let through. That recreates the bug: two labels and two carrier charges.

The rule treats "slow" and "dead" as the same thing, and no timeout can separate them. Any threshold either duplicates work on slow requests or leaves a dead request blocked for too long. It also has a check-then-act race, so two simultaneous retries can both pass.

## What to build

### 1. Claim the key atomically before doing any work

Insert the key with `status = in_progress` using a unique constraint (`INSERT ... ON CONFLICT DO NOTHING`, or an equivalent compare-and-set). Whoever inserts the row owns the request. Store these fields:

- a hash of the request payload
- `owner_id`
- `lease_expires_at`
- `status`: `in_progress`, `completed`, or `failed_definitive`
- the stored response

### 2. Define what a retry does for each state

| Key state | Behavior |
|---|---|
| Absent | Claim it and run the flow. |
| `completed` | Replay the stored response. |
| `in_progress`, lease live | Do not run the flow. Either hold the request open and poll the row for up to about 25s, then return the result, or return `409` with `Retry-After`. Prefer the hold, because the client gets the label without a second round trip. |
| `in_progress`, lease expired | Recover (section 4). Never blindly re-run. |
| Same key, different payload hash | Return `422`. The key is being reused for a different request. |

### 3. Keep the lease alive with a heartbeat

Use a short lease, for example 30s, that the owner renews every few seconds while it works. A slow carrier call keeps renewing it. A crashed worker stops renewing, so the lease expires within seconds. Set a hard timeout on the carrier call, and make the lease logic aware of it. This is the legitimate version of the engineer's idea: it detects a dead worker through a heartbeat rather than guessing from elapsed time.

### 4. Make the carrier call idempotent too

The money is spent at the carrier, so the server-side key alone isn't enough. Cover three cases:

- **Carrier supports idempotency keys or client references.** Send a deterministic one derived from your key.
- **Carrier doesn't support them.** Write a `carrier_call_started` record with your own reference before you call, then record the result after.
- **Recovery after a crash or an ambiguous timeout.** If the record says the call started but has no result, look the shipment up at the carrier by your reference before deciding anything. If a label exists, adopt it. If none exists, retry. If you can't tell, mark it `needs_reconciliation` and void any duplicate. Never re-run when you don't know.

### 5. Define what gets stored

Store definitive outcomes, including a final failure after the carrier was reached. Don't store failures from before any side effect, such as validation errors or a carrier rejection of the request. For those, release the key so the client can retry.

### 6. Fix the 40-second problem itself

Consider making the endpoint asynchronous. Return `202` with a shipment ID right away, then deliver the label by polling or webhook. A 40s synchronous call will keep colliding with client timeouts. It's a bigger change, so it can follow the idempotency fix.

### 7. Clean up the existing damage

Query for idempotency keys or shipment references that have two labels. Void the extras, claim the carrier refunds, and tell the affected client. Add an alert on "more than one label per key" so this class of bug shows up quickly.

### 8. Tests that would have caught this

- Two concurrent requests with the same key against a slow fake carrier. Expect one carrier call.
- A retry at 10s against a 40s carrier call. Expect one label, with the retry waiting or getting `409`.
- `kill -9` the worker mid-flight. Expect recovery through carrier lookup, with no duplicate.
- Same key, different payload. Expect `422`.
- A carrier timeout where the label was actually created. Expect it to be adopted, not duplicated.

## On the PM's email

Don't send it as the fix. The client behaved correctly. Retrying with the same idempotency key is exactly what the key is for. Asking customers to retry less papers over a server bug, and it will fail anyway, because networks and timeouts exist. Once the server is fixed, aggressive retries are harmless.

A better communication, after the fix ships:

- Tell the affected client what happened, that you've voided the duplicate label and refunded the charge, and that it can't recur.
- Document recommended client behavior for this endpoint: a timeout above your p99, with 60s as a starting point; reuse the same key on retries; use exponential backoff with jitter; honor `Retry-After` and `409`. That is guidance, not a request to stop retrying.

## Order of work

1. Atomic claim plus the in-progress retry behavior (steps 1 and 2). This alone would have prevented the incident.
2. Carrier-side idempotency and reconciliation (step 4). This protects the money.
3. Heartbeat leases and crash recovery (step 3).
4. Duplicate cleanup and alerting (step 7), which can run in parallel with the rest.
5. Client documentation, then the asynchronous API as a follow-up.