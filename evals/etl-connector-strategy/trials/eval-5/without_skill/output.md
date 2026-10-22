# Palladia connector: what to know before the sprint

**Do first:** ask the API team the 8 questions at the bottom, and ask for a `Retry-After` header on 429s. Everything else depends on those answers.

## 1. Incremental sync works for only two of four resources

| Resource | `modified_at` | Strategy |
|---|---|---|
| Expenses | yes | Incremental, if it is filterable (see Q1) |
| Reports | yes | Incremental |
| Approvals | no | Full re-pull, or infer from the parent (see below) |
| Vendors | no | Full re-pull and diff |

- **Vendors:** the table is probably small, so a full pull each cycle is fine. Hash each row and upsert only the changes.
- **Approvals:** this is the risky one. The table is large, because it holds several approvals per expense or report. A full re-pull each cycle is expensive. Two options:
  - Re-fetch approvals only for expenses or reports whose `modified_at` moved. This is only correct if an approval change bumps the parent's `modified_at`. Verify that, because it is an assumption.
  - Ask Palladia to add `modified_at` to approvals. It is the cleanest fix and a small change on your side.
- **Do not assume `modified_at` is filterable or sortable.** A field existing is not the same as `modified_since=` or `sort=modified_at` existing. Without a server-side filter, incremental sync still means scanning everything.

## 2. Offset pagination is the biggest risk on 4M rows

- **Drift.** The first sync takes hours. Rows inserted or deleted mid-crawl shift every later offset, so you get duplicates and silently skipped rows. A skipped row is the worst case, because nothing flags it.
- **Deep-offset cost.** `OFFSET 3,900,000` is slow on the server and gets slower the deeper you go. Check whether the API caps page depth or starts timing out.
- **Mitigation: partition by time window, not by one long crawl.**
  1. Slice expenses into windows, for example by `created_at` or `modified_at` per day or week.
  2. Paginate each window with `page=`/`per_page=`. Each window is small, so offsets stay shallow.
  3. Windows can run in parallel and be checkpointed individually.
  4. A failed window retries alone.
  - This needs a date-range filter on the list endpoint (Q1).
- **Sort order must be deterministic.** If the default sort is not unique, such as `created_at` with ties, rows can repeat or vanish between pages. Pass an explicit sort with a tie-break on `id`, or confirm the default is `id`.
- **Longer term, ask for cursor or keyset pagination** (`after_id=` or an opaque cursor). It removes both problems.

## 3. Rate limit: the first sync is slow, and a bare 429 gives you no guidance

Calls needed for 4M expenses (before approvals, reports, and vendors):

| `per_page` | Requests | At 600/min | At 480/min (80%) |
|---|---|---|---|
| 25 | 160,000 | ~4.4 h | ~5.6 h |
| 50 | 80,000 | ~2.2 h | ~2.8 h |
| 100 | 40,000 | ~67 min | ~83 min |
| 500 | 8,000 | ~13 min | ~17 min |

- **Max `per_page` is the biggest lever on first-sync time.** Find out what it is (Q3).
- **Client-side limiter is mandatory.** Use a shared token bucket across all workers, targeting roughly 70-80% of 600/min. Do not rely on reacting to 429s.
- **A bare 429 has no `Retry-After`, no `X-RateLimit-*` headers, and no body.**
  - You cannot tell how long to wait.
  - You cannot tell whether the limit is per token, per customer, or global.
  - Use exponential backoff with jitter, with a floor of about 1 s and a cap of about 60 s.
  - Treat repeated 429s as a signal to halve your rate. That is AIMD (additive increase, multiplicative decrease).
  - **Ask Palladia to add `Retry-After` and a JSON error body.** It is a few lines of server code and removes a lot of guesswork.
- **Check whether the limit is shared.** If it is per customer, your sync competes with the customer's own API use and their other integrations. If it is global across all customers, one big first sync can starve everyone else. In that case you need fair scheduling and a per-tenant concurrency cap.
- **Watch for N+1 calls.** If an expense list item lacks line items, receipts, or approvals, fetching them per row multiplies the request count by 2-5x and the sync becomes impractical. Check what the list payload contains, and whether there is an `include=` or `expand=` parameter.

## 4. Deletes are the subtlest problem

Soft delete sets `is_active=false`, the record is returned for 90 days, then it vanishes with no tombstone.

- **Make sure inactive rows are returned.** Many list endpoints hide inactive rows by default. Confirm you get them (maybe via `include_inactive=true`) in both the backfill and incremental sync (Q4).
- **Check that delete bumps `modified_at`.** If it does not, an incremental sync never sees the delete. This is a common bug.
- **The 90-day cliff:** a record deleted and then purged leaves no trace.
  - If the connector is down, paused, or the customer disconnects for more than ~90 days, those deletes are lost forever. Your destination keeps ghost rows.
  - **Run a periodic reconciliation.** Do it well inside the 90-day window, for example weekly or monthly. List all IDs (or ID + `modified_at`) in Palladia, diff against the destination, and mark anything missing as deleted. It is cheap with a large `per_page` and a minimal field set.
  - **Alert if the last successful sync is older than ~60 days.** Past 90 days, force a full resync.
- **Vendors and approvals:** do they have `is_active` or delete semantics at all? If not, a hard delete is invisible, and only full-diff reconciliation catches it.
- **Backfill vs deleted data:** rows purged before the backfill are simply not there. Document that deletes older than 90 days cannot be reflected for a new customer.

## 5. Correctness details that bite later

- **High-water mark:** record the sync start time, not the end time, as the next cursor. Subtract an overlap such as 5-10 minutes, because a row can be committed after a later one with an earlier `modified_at`. Upserts keyed by `id` make the overlap harmless.
- **Handoff from backfill to incremental:** capture the high-water mark before the backfill begins, so changes made during the multi-hour backfill are picked up by the first incremental run.
- **Timestamps:** confirm timezone and precision (UTC, seconds vs ms). Equality at a window boundary can drop or double rows, so use inclusive bounds plus dedupe by `id`.
- **Idempotency and resumability:** checkpoint per window and per page. A crash at hour 2 should not restart from zero. Make writes idempotent.
- **Cross-resource consistency:** load in dependency order (vendors, reports, expenses, approvals) or tolerate temporarily dangling references. An expense can move between reports, so `report_id` must update.
- **Schema evolution:** you will get fields you do not know about. Store unknown fields rather than failing.
- **Webhooks:** do they exist? Events plus periodic reconciliation beat pure polling and cut API usage.
- **Bulk export:** for tenants with 4M rows, a bulk endpoint (async export job, S3 dump) is far better than 40k+ paginated calls. Worth asking Palladia whether to build one.

## 6. Suggested design

1. Rate limiter: shared token bucket plus AIMD, with backoff and jitter on bare 429s.
2. Backfill: time-windowed, parallel within the budget, checkpointed per window, deterministic sort.
3. Incremental: expenses and reports by `modified_at` with overlap. Vendors by full diff. Approvals by parent change or full diff, depending on Q2.
4. Reconciliation job: ID-set diff for deletes, scheduled well inside 90 days, plus a staleness alarm.
5. Observability: rows per window, 429 rate, effective req/min, and lag per resource. Log structured events at every retry and window boundary.
6. Tests: 429 with no headers, 429 storms, a page that changes mid-crawl, a delete that does not bump `modified_at`, a purge after 90 days, and empty or last pages.

## 7. Questions for the API team (answer before sprint)

1. Is there a server-side filter on `modified_at` (and `created_at`)? Is it sortable?
2. Does an approval change bump the parent expense or report `modified_at`? If not, can approvals and vendors get `modified_at`?
3. What is the max `per_page`? Is there a cap on page depth? What is the default sort?
4. Are `is_active=false` rows returned by default? Is there an `include_inactive` flag? Does a delete bump `modified_at`?
5. Is the 600/min limit per token, per customer, or global? Is a 429 counted against the budget?
6. Can you add `Retry-After`, `X-RateLimit-*` headers, and a JSON body to 429s?
7. Does the list payload include line items, receipts, and approvals, or is it N+1?
8. Do webhooks or a bulk export exist, or could they be built for large tenants?

The most important items: pagination drift (section 2), the 90-day delete cliff (section 4), and the first-sync budget (section 3). Q1, Q3, and Q4 decide the whole design.