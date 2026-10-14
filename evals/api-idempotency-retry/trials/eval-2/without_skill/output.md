# Review of the Redis SETNX proposal, and how to fix the race

## Verdict

Don't ship the Redis lock as the fix. Fix the race in Postgres with a unique index and an atomic insert.

## Root cause

The controller does check-then-act: `SELECT` the key, then `INSERT` if it's missing. Two requests 30ms apart both run the `SELECT` before either `INSERT` commits. Both see nothing, and both create an invoice.

The invariant is "one key, one invoice". It lives in Postgres, so Postgres has to enforce it. Nothing in your description suggests the keys table has a unique constraint. If it did, the second `INSERT` would have failed, so I'm assuming it doesn't.

## Why the Redis lock is the wrong fix

- **It doesn't make the write atomic.** Redis and Postgres can't commit together. The lock only narrows the window.
- **The 10s TTL can expire mid-request.** A slow query, a lock wait, a GC pause or a deploy can run past 10 seconds. The lock expires, a retry gets in, and you have the same duplicate. A lock without fencing can't fix this.
- **Failover loses locks.** Replication to the Redis replica is asynchronous. If the primary dies right after granting the lock, the replica never saw it.
- **Naive unlock is a second bug.** A plain `DEL` can release a lock that another request now holds, so you'd need a token check in a Lua script.
- **It adds a failure mode.** If Redis is down, you either fail open (duplicates return) or fail closed (the endpoint is down).
- **The scope is ambiguous.** "In front of the endpoint" suggests one lock for everything, which serializes all invoice creation. Even per-key locks leave the problems above.

A Redis lock is acceptable only as an optional optimization to shed load. The DB constraint must stay as the source of correctness.

## The fix

### 1. Clean up, then add a unique index

First find existing duplicates:

```sql
SELECT account_id, key, count(*) FROM idempotency_keys
GROUP BY 1, 2 HAVING count(*) > 1;
```

Resolve them. Last Tuesday's duplicate invoice needs voiding or refunding, and the extra key rows need deleting. Then add the index without locking the table:

```ruby
class AddUniqueIndexToIdempotencyKeys < ActiveRecord::Migration[7.1]
  disable_ddl_transaction!

  def change
    add_index :idempotency_keys, [:account_id, :key],
              unique: true, algorithm: :concurrently
  end
end
```

Scope the key by account or tenant. A global unique key would let one customer collide with another. If duplicates exist when the concurrent build runs, it leaves an `INVALID` index behind, so dedupe first.

Also add a `request_fingerprint` column, a SHA-256 of the request body.

### 2. Claim the key atomically, in the same transaction as the invoice

```ruby
def create
  key = request.headers["Idempotency-Key"]
  return head :bad_request if key.blank?

  fingerprint = Digest::SHA256.hexdigest(request.raw_post)

  ActiveRecord::Base.transaction do
    claimed = IdempotencyKey.insert_all(
      [{ account_id: current_account.id, key: key,
         request_fingerprint: fingerprint }],
      unique_by: %i[account_id key],
      returning: %w[id]
    )

    if claimed.rows.empty?
      existing = IdempotencyKey.find_by!(account_id: current_account.id, key: key)
      if existing.request_fingerprint != fingerprint
        return render json: { error: "idempotency key reused with different request" },
                      status: :unprocessable_entity
      end
      return render json: existing.response_body, status: existing.response_status
    end

    invoice = Invoice.create!(invoice_params.merge(account: current_account))
    body = InvoiceSerializer.new(invoice).as_json
    IdempotencyKey.where(id: claimed.rows.first.first)
                  .update_all(invoice_id: invoice.id,
                              response_status: 201,
                              response_body: body)
    render json: body, status: :created
  end
end
```

Use `insert_all` with `unique_by`, which compiles to `INSERT ... ON CONFLICT DO NOTHING RETURNING id`. Don't use `create` plus `rescue ActiveRecord::RecordNotUnique`. In Postgres, a failed statement aborts the whole transaction unless you use a savepoint (`requires_new: true`).

### Why this serializes the 30ms double-fire

- Request A inserts the key and holds the unique-index entry until its transaction commits.
- Request B's `INSERT` blocks on that entry. The database does the waiting, so you don't need a lock or a TTL.
- If A commits, B's insert is a no-op and returns zero rows. B's follow-up `SELECT` sees A's committed row and replays the stored response.
- If A rolls back (crash, exception), B's insert succeeds and B does the work. No stuck keys, and no lock to expire.

This relies on the default `READ COMMITTED` isolation, which is the Rails default. Under `REPEATABLE READ` the follow-up `SELECT` may not see A's row, and you'd get serialization errors instead.

### 3. Constraints

- **Invoice creation and key claim must share one transaction.** If the key commits first and the invoice fails afterwards, the key is burned and retries replay a missing result.
- **Do side effects after commit.** Emails, webhooks and payment-provider calls inside the transaction can't be rolled back. If the invoice flow has external calls that must be in the request, switch to the Stripe-style two-phase pattern:
  1. Insert the key with `status = started` and `locked_at`.
  2. Do the work.
  3. Mark the key `completed` with the stored response.
  4. Have the loser return `409` while the key is `started`, and let a reaper recover stale `started` keys.
- **Optional belt and braces.** Add `invoices.idempotency_key_id` with a unique index, so even a buggy code path can't create two invoices for one key.
- **Expire old keys** with a nightly job, for example after 24 hours or more. The retention window must exceed your clients' longest retry horizon.

### 4. Test it

Write a test that fires two threads released together through a barrier, using the same key. Each thread needs its own DB connection, and the test must not run inside a wrapping transactional fixture. Assert:

- exactly one `Invoice` exists,
- both responses are identical,
- a different body with the same key returns `422`.

Then drop the unique index and confirm the test fails. A race test that passes without the fix proves nothing. Run it a few hundred iterations, because races are probabilistic.

## Summary

1. Dedupe the keys table and add a unique index on `(account_id, key)`.
2. Replace `SELECT`-then-`INSERT` with `INSERT ... ON CONFLICT DO NOTHING RETURNING`, in the same transaction as invoice creation.
3. Replay the stored response when the conflict path hits, and reject a fingerprint mismatch with `422`.
4. Drop the Redis lock.