# Fixing the duplicate-invoice race at Orbitshelf

**Verdict:** don't ship the Redis `SETNX` lock. The bug is the check-then-insert in the controller, and the lock leaves it in place. Make the claim atomic in Postgres instead. It takes one unique index and one changed query, and the claim commits in the same transaction as the invoice.

I followed the `api-idempotency-retry` skill and its key-lifecycle reference. I didn't ask its clarifying questions first, so the assumptions are listed at the end.

## Why the race happens

```
T0  req A: SELECT key  -> none
T+30ms  req B: SELECT key  -> none   (A hasn't inserted yet)
    A: INSERT key, create invoice
    B: INSERT key, create invoice    <- both succeed
```

Two requests 30ms apart are enough for both SELECTs to run before either INSERT. This is a TOCTOU race.

Both INSERTs succeeded, so one of these must also be true:
- There is no unique index on `(account_id, idempotency_key)`.
- The index exists but is not scoped as expected.
- A `rescue ActiveRecord::RecordNotUnique` swallows the error and carries on.

Check `\d idempotency_keys` and the controller's rescues before anything else.

## Why the Redis `SETNX` lock is the wrong fix

1. **It doesn't remove the race.** The SELECT-then-INSERT is still there. The lock only narrows the window, and only while it is held.
2. **The 10s TTL isn't a guarantee.** If a request stalls past 10s (GC pause, slow DB, network stall), the lock expires. A second request then takes it while the first is still running, and the first can still write. Kleppmann's analysis is that without a fencing token, no timing assumption fixes this. Fencing tokens would need Postgres to check them, which makes Postgres the arbiter again.
3. **A Redis failover or restart can drop the lock.** Then two holders exist.
4. **Redis becomes a new hard dependency on the write path.** If Redis is down, you either fail open (the race returns) or fail closed (invoices stop). Neither is acceptable for a bug Postgres can already prevent.
5. **It has no in-flight state.** The loser of a `SETNX` has nothing useful to say. It can only error or wait, and it can't replay the first request's stored response.
6. **No surveyed vendor uses a distributed lock for this claim.** Stripe, AWS, Twilio, and Resend all arbitrate in the store.

## The fix

### 1. Migration: make the database pick the winner

Dedupe any existing duplicates first, or the index build fails.

```ruby
class AddUniqueIndexToIdempotencyKeys < ActiveRecord::Migration[7.1]
  disable_ddl_transaction!   # required for CONCURRENTLY

  def change
    add_index :idempotency_keys, [:account_id, :idempotency_key],
              unique: true, algorithm: :concurrently,
              name: "idx_idempotency_keys_account_key"
    # Scope is per caller, never global.
    add_column :idempotency_keys, :request_fingerprint, :text
    add_column :idempotency_keys, :locked_at, :datetime
    add_column :idempotency_keys, :response_status, :integer
    add_column :idempotency_keys, :response_body, :jsonb
  end
end
```

`request_fingerprint` is NOT NULL in the reference schema. Backfill it and then add the constraint, because existing rows have no value.

### 2. Controller: insert first, branch on the result

```ruby
def create
  key         = request.headers["Idempotency-Key"] or return render_error(400, "idempotency_key_required")
  fingerprint = Digest::SHA256.hexdigest(request.raw_post)

  status, body = ActiveRecord::Base.transaction do
    # Claim: the unique index picks one winner. Never SELECT first.
    claimed = IdempotencyKey.insert(
      { account_id: current_account.id, idempotency_key: key,
        request_fingerprint: fingerprint, locked_at: Time.current },
      unique_by: :idx_idempotency_keys_account_key,   # ON CONFLICT DO NOTHING
      returning: %w[id]
    ).rows.first

    if claimed
      # Winner: create the invoice in the SAME transaction as the claim.
      invoice = current_account.invoices.create!(invoice_params)
      resp = [201, InvoiceSerializer.new(invoice).as_json]
      IdempotencyKey.where(id: claimed.first)
                    .update_all(response_status: resp[0], response_body: resp[1], locked_at: nil)
      resp
    else
      existing = IdempotencyKey.find_by!(account_id: current_account.id, idempotency_key: key)
      if existing.request_fingerprint != fingerprint
        [409, { code: "invalid_idempotent_request",
                message: "This key was already used with a different payload. Use a new key or resend the original." }]
      elsif existing.response_status
        [existing.response_status, existing.response_body]            # replay verbatim
      else
        [409, { code: "concurrent_idempotent_requests",
                message: "A request with this key is in progress. Wait and retry." }]
      end
    end
  end

  render json: body, status: status
end
```

### Why this closes the race

- **The concurrent loser waits.** If B's INSERT hits A's uncommitted row, Postgres blocks B on the unique index until A commits or rolls back.
- **If A commits,** B's INSERT does nothing, B reads the committed row, and B replays A's stored response verbatim. B gets the same invoice and no duplicate exists.
- **If A rolls back,** B's INSERT succeeds and B proceeds as a first attempt. No orphan key is left behind.
- **Atomicity.** Claim and invoice commit or abort together, so you can't have a key without an invoice, or the reverse.
- **No 409 in-flight case in this single-transaction flow.** The `concurrent_idempotent_requests` branch is still needed for any multi-phase flow. It is also a safe default if you later commit the claim before the work.

### 3. Behaviors to define while you're there

- **Payload mismatch:** the same key with a different body returns 409 `invalid_idempotent_request`. It is never silently replayed.
- **Stored failures:** decide whether a stored 4xx/5xx replays (Stripe v1) or may be re-attempted. Pick one and document it.
- **Retention:** keep keys for a ~24h replay window, but size it from your longest retry chain, such as a DLQ replay. Keep records for ~72h before reaping. A reused key after expiry is a new request.
- **Key derivation, for your docs:** tell integrators to mint the key on their side. The best form is derived from the event, like `invoice-${orderId}`. Never use a fresh UUID per attempt.

### 4. If invoice creation calls something that can't be rolled back

If creating the invoice also charges a card or sends an email, one transaction isn't enough. Split the work into phases using a `recovery_point` column (`started`, `invoice_created`, `charge_recorded`, `finished`). Record intent before each external call. Add a completer job for abandoned in-flight keys and a reaper for expired ones. If it's pure DB work, skip this.

## Verify before declaring it fixed

1. **Concurrency gate.** Fire 20 or more simultaneous identical requests with one key. Exactly one invoice row must exist. Every response must be either the 201 or a verbatim replay of it. Run it in CI.
2. **Mutation check.** Revert to SELECT-then-INSERT, or drop the index, and confirm the test fails. Otherwise the test isn't protecting anything.
3. **Mismatch test:** the same key with a different body returns 409.
4. **Rollback test:** force an invoice-creation failure and confirm no key row survives.
5. **Replay test:** the second call after completion returns the byte-identical stored response.

## Assumptions to confirm

- Invoice creation is local to Postgres (see section 4 if not).
- A reaper job for old keys is acceptable.
- Existing duplicate key rows can be deduped before the index build.
- Your Rails version supports `insert` with `unique_by:` (Rails 6+).

Also check where duplicate invoices already exist. The customer from last Tuesday will probably need a manual credit or void. Consider a separate unique index on the invoice's business identifier as a second backstop.