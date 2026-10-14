# Idempotency retention: recommendation and review

## Answer

**Set the key TTL to 14 days. Do not cut to 6 hours.** Back it with a permanent unique constraint on the credit ledger.

A retention window has to outlast the longest time a duplicate can legitimately arrive. Storage cost doesn't enter into that. Your replays arrive up to 6 days late, so:

- **24h** already fails: that is where the 61 duplicates came from.
- **6h** makes it worse. It would fail replays of every age and also long client retries.
- **14 days** is about 2.3× the worst replay you've observed, and it leaves margin for the runbook.

The rule to keep is: `TTL ≥ max(DLQ topic retention, runbook max replay age) + margin`.

## Why 14 days is affordable

The 9 GB/month figure is small. At typical cloud storage prices that is a few dollars a month, even if 14 days multiplies the steady-state table by roughly 14×. The cost argument is weak. Cut size, not window (see item 3 below).

## What else is wrong with the retention model

1. **The 9 GB/month growth contradicts a 24h TTL.** A table that expires keys after 24h should hold about one day of keys and stay flat. Steady growth means one of these is happening:
   - Expiry is only checked at read time (`expires_at < now`), and no job deletes the rows.
   - Deletes happen but bloat is never reclaimed (Postgres autovacuum or `DELETE` bloat).
   - Traffic is genuinely growing.

   Cutting to 6h wouldn't fix the first two. Check the table's actual row age distribution before changing anything. If you use Postgres, partition by day and drop partitions instead of running `DELETE`.

2. **The key store is the only defense.** Any TTL is a guess about the future. For credit purchases, add a permanent unique constraint on the ledger, for example `UNIQUE (account_id, source_job_id)`. It costs almost no storage, never expires, and turns any future late replay into a rejected insert instead of a duplicate charge.

3. **Records are probably too big.** If you store full response bodies, store a request fingerprint, the status, and a pointer to the result instead. That makes the 14-day window cheap.

4. **Check that replays reuse the original key.** If the DLQ consumer or runbook generates a new key at replay time, no TTL helps. Confirm the original key travels in the Kafka message headers and survives the replay.

5. **Check downstream windows.** If you forward your key to a payment provider, that provider has its own idempotency window, often 24h. Your check must happen first and must outlive theirs.

6. **Key and side effect must commit atomically.** If the purchase succeeds and the process fails before the key is written (or the key is only marked on success), the DLQ replay will repeat the charge. Write the key in the same transaction as the ledger entry. Store an `in_progress` state too, so concurrent replays don't both proceed.

7. **The runbook has no age cap.** Add a maximum replay age (7 days, matching or below DLQ topic retention), and a pre-replay check against the ledger. Alert when a replay is older than half the TTL.

8. **One TTL for every endpoint.** Use tiers instead. Money-moving operations get the long window plus the ledger constraint. Cheap read-like operations can keep 24h or less. This is where real cost savings come from.

9. **Same key, different payload.** Compare fingerprints and return an error (409 or 422) instead of silently returning the old result.

## Next steps

1. Verify the DLQ topic's `retention.ms` and whether replays carry the original key. Do this first, since both change the numbers above.
2. Add the ledger unique constraint. This is the real fix.
3. Raise the TTL to 14 days.
4. Find out why the table grows despite a 24h TTL.
5. Add the runbook age cap.
6. Reconcile the 61 duplicates (refund or credit reversal) by matching ledger rows that share a source job ID.

I couldn't see your schema or code, so items 1, 4, 5 and 6 are things to check, not confirmed defects.