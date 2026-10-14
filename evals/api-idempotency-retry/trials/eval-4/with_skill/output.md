# Meterly idempotency retention: recommendation

**Don't cut to 6 hours. Raise the replay window to 14 days.** Derive it from the longest retry chain, not from storage cost. The 61 duplicates are the cost of a window shorter than the replay chain. A 6-hour window would make every DLQ replay a brand-new purchase.

I couldn't ask the clarifying questions, so the assumptions are stated below. Check them before shipping.

## 1. Retention

| Horizon | Current | Recommended | Purpose |
|---|---|---|---|
| Replay window | 24h | **14 days** | A reused key replays the stored result. After expiry, a reused key is a new request. |
| Reaper threshold | not defined (see §2) | **17 days** (window + 72h) | Records stay for human recovery, then get deleted. |
| DLQ max age | unbounded | **7 days**, enforced | Older messages need a human decision, not a blind replay. |

- **Why 14 days:** you observed replays at 5–6 days. The real limit is the DLQ topic's retention, plus however long a weekend, holiday or incident can delay the runbook. If that retention is the Kafka default of 7 days, then 7 days + margin fits easily inside 14.
- **Enforce the cap on the runbook side.** The window should be DLQ max age + 1 day or more. Any message older than the window must not replay automatically. Otherwise a replay past the window creates a duplicate with no warning.
- **Cost:** 9 GB/month is about 0.3 GB/day. At steady state, 24h is 0.3 GB, 14 days is about 4.2 GB, and 17 days is about 5.1 GB. This assumes the 9 GB/month is the ingest rate and expired rows are deleted. Compared with the 61 duplicate purchases, that is cheap.
- **Document the window.** Publish the number to integrators, and tell them what happens after expiry ("treated as a new request").

## 2. Other problems in the retention model

1. **The table shouldn't be growing at all.** With a 24h window and a working reaper, the table plateaus. Steady growth of 9 GB/month means expired rows are never deleted.
   - **Likely cause:** there is probably no reaper job, or it isn't deleting.
   - **Consequence:** a 6-hour TTL wouldn't reduce storage. It would break correctness and leave the real problem in place.
   - **Fix:** run a reaper, and partition the table by day so dropping a partition replaces mass `DELETE`s and the bloat they leave.
   - **If growth is real ingest:** confirm that, then size from the steady-state figures above.

2. **Do replays carry the original key?** Pull the 61 cases and check. If the runbook or consumer mints a fresh key per replay, no TTL fixes it. The key must be event-derived and stored with the DLQ message, e.g. `credit-purchase-${purchaseIntentId}`. A fresh key per attempt is the anti-pattern that defeats the whole mechanism.

3. **Stored-failure policy is probably undecided, and extending the window exposes it.** If the original failed with a 5xx and you store failures verbatim (Stripe v1), a replay inside the 14-day window just returns the stored failure and never re-executes.
   - **What the 24h expiry did:** it accidentally made replays work by erasing the failure.
   - **Needed decision:** a retryable failure that never committed a side effect must be re-attemptable under the same key. Store terminal outcomes as replayable, and treat transient failures as re-executable. Decide this explicitly and document it.

4. **"Failed" may mean "succeeded, response lost."** A job that timed out after the purchase committed lands in the DLQ even though the credits were bought. The skill's three-state table covers this case, which should replay the stored response. It only works if:
   - The claim and the purchase commit in one ACID transaction.
   - The key has three states: absent, in-flight, complete.
   - An in-flight duplicate gets a 409 (`concurrent_idempotent_requests`). A replay racing a slow original must never pass through.

5. **If the purchase calls a payment processor mid-flight,** use recovery points: record intent before the external call, record the charge id after it. A replay then resumes after the charge instead of charging again.

6. **Check the basics.**
   - Scope keys by `(account_id, key)` with a unique constraint as the atomic claim. Don't do check-then-insert.
   - Store a payload fingerprint and return 409 `invalid_idempotent_request` on mismatch.
   - Store the full response verbatim.

7. **Add a business-level backstop.** A key window is always finite. Add a unique constraint on the purchase's natural identity (e.g. purchase intent id) so a replay past any window fails closed instead of double-charging.

8. **Say "safe within the key scope and window."** Never write "exactly-once".

## 3. Verification

- **Concurrency gate:** fire N identical concurrent requests with one key. Exactly one purchase must execute.
- **Replay gate:** replay a DLQ message at day 6, and again at day 13. Each must return the stored result, or re-execute only if the original had no committed effect. Day 15 must be blocked by the runbook cap.
- **Crash gate:** kill the service between the processor charge and the response, then retry. There must be zero repeat charges.
- **Alarm:** the production duplicate-purchase rate within the window should be zero. Any non-zero value means a gate regressed.
- **Cleanup:** reconcile and refund the 61 existing duplicates separately.

## 4. Assumptions to confirm

- **DLQ retention and replay cap.** I assumed a 7-day Kafka retention.
- **Postgres-like store.** I assumed unique constraints and transactions are available.
- **Payment processor call.** I assumed the purchase calls an external processor mid-flight.
- **Replay key.** I assumed replays could carry the original key. If they can't today, fix that first.

I didn't check the Meterly code or data. These recommendations come from the skill and the facts you gave.