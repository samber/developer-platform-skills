**Do not start writing the connector next sprint. Spend the sprint on three things: collect named demand evidence, fix 4 API gaps, and pick one platform.** A connector built on today's API fails the certification bar for reasons no connector code can fix.

This is a first-pass strategy from your API facts alone. I did not run the full interview, so the open questions at the end can change the ranking.

## 1. Demand gate (blocks build approval)

You gave no demand evidence. The gate needs named, checkable artifacts:

- Tickets asking for a named ETL platform.
- Lost-deal or churn notes citing data-stack mismatch.
- API logs showing hand-rolled extraction. At 600 req/min, a data-team service account paging the expenses endpoint on a loop is the pattern to look for.
- Security or procurement questionnaires asking about warehouse sync.

Without these, do not build. Reopen the decision when you have, for example, three named-platform tickets in a quarter or one lost deal citing the gap. Write the case on support deflection and retention. No ETL platform pays a source vendor, so book no revenue line.

## 2. Extraction-readiness audit (the main finding)

| Resource | Cursor | Delete signal | Verdict |
|---|---|---|---|
| expenses | `modified_at` (verify below) | `is_active=false`, 90-day window, then silent disappearance | Conditional pass |
| reports | `modified_at` (verify below) | Not stated | Conditional pass, ask about deletes |
| approvals | None | Not stated | Fail. Full refresh, or add `modified_at` |
| vendors | None | Not stated | Fail. Full refresh is tolerable if small, but needs an exclusion note |

Gaps, ranked by cost:

1. **Offset pagination (`page=`, `per_page=`) is the biggest risk.**
   - Offsets shift under concurrent inserts and deletes. A multi-hour scan of a live customer silently skips and duplicates rows.
   - Deep offsets are slow server-side, so page 40,000 costs far more than page 1.
   - A mid-backfill failure cannot resume exactly. You restart or guess.
   - Fix: add keyset or opaque cursor pagination with a deterministic sort (`modified_at, id`). Fallback: a filterable time window (`modified_since`, `created_before`) plus a stable sort.
2. **No bulk or backfill path. The 4M-row first sync is the problem case.**
   - Request counts at full 600/min and zero retries (`per_page` is unknown to me, so these are scenarios):

     | `per_page` | Requests | Time at 100% of limit |
     |---|---|---|
     | 50 | 80,000 | ~133 min |
     | 100 | 40,000 | ~67 min |
     | 200 | 20,000 | ~33 min |

   - Real time is 2 to 4 times longer. The limit is probably shared with the customer's own API use, so the connector can only take part of it. Add retries and offset slowdown on top.
   - The sync also burns the customer's whole API budget for hours.
   - Fix: an async export job (request, poll, download files) for first sync, then incremental by cursor. Cheaper fallbacks: a higher rate limit for connector service accounts, or a documented larger `per_page` cap.
3. **Missing `modified_at` on approvals and vendors.**
   - Fix: add an indexed, filterable, sortable `modified_at`.
   - Interim for approvals: if an approval change bumps the parent report's `modified_at`, re-fetch approvals only for changed reports. Prove that before relying on it.
   - Vendors: full refresh each sync is acceptable if the table is small. Hard deletes still go unseen, so add an explicit exclusion note.
4. **A bare 429 with no body.**
   - Connectors have no signal for when to retry, so they guess and often hammer harder.
   - Fix: send `Retry-After`, plus `X-RateLimit-Remaining` and a reset header. This is hours of work.
   - Until then, the connector needs a client-side token bucket set well under 600/min (assume about 50% if the limit is shared), with exponential backoff and jitter.
5. **The delete signal exists but has a hard expiry.**
   - After 90 days the record vanishes, which is a hard delete with no signal.
   - Any connector paused or broken for more than about 80 days (leave margin) loses deletes forever.
   - Required behavior: if the last successful sync is older than the window minus margin, force a full re-import. Also run a periodic full reconciliation for expenses.
   - Fix upstream: a durable "changes and deletes since cursor" feed that outlives 90 days. Build it when customers report missed deletes. Do not promise it at launch.

Verify these before trusting `modified_at` (I am assuming nothing about them):

- Does the list endpoint filter and sort by `modified_at`? Is there a `modified_since` parameter?
- Does the soft delete (`is_active=false`) bump `modified_at`? If not, deletes are invisible to incremental sync.
- Do status changes, line-item edits, receipt attachments, and approval transitions bump the parent's `modified_at`?
- Does the list return inactive rows by default, or only with a flag?
- What is the timestamp precision and timezone? Ties at the same second can drop records at page boundaries.

If any answer is no, that resource fails the cursor check. Fix the API or write an exclusion note. Do not skip it silently.

## 3. Sync design (works on any platform)

1. At the start of a backfill, record the high-water `modified_at`. Do not take it at the end.
2. Backfill by time-windowed partitions (for example one month of `created_at` each), not one giant offset scan. Checkpoint per window.
3. Switch to incremental from the saved high-water mark, re-query a small overlap window, and upsert by stable key so the overlap cannot duplicate.
4. Keep inactive rows and write `is_active=false` through as a soft-delete flag in the warehouse.
5. Run a periodic full reconciliation to catch purged records.

## 4. Platform and build path

I cannot choose a platform without knowing where your customers' data stacks run (open question 2). Default ranking, as of the 2026-08-30 reference snapshot (re-verify before committing):

1. **Platform-managed listing (default).**
   - Fivetran "By Request": the platform builds and maintains it, and the platform absorbs the maintenance tax.
   - Weeks of API-doc analysis, and it can reject you outright.
   - Offset pagination, no cursor on two resources, and a bare 429 weaken your candidacy. Fix the API first.
2. **Vendor-SDK connector.**
   - Fivetran's Partner-Built program is closed to new sources, so the live self-build route is the Fivetran Connector SDK (Python, community connector, no badge).
   - On Airbyte, the low-code manifest handles page/offset pagination well and gives the fastest path to listing.
   - You own fixes, so you need a named owner.
   - Promote to this rung if validated demand justifies standing engineering, if the managed queue rejects you, or if you want control of cursor logic.
3. **Custom open-spec tap.** Use it only if a strategic segment runs open-source-first stacks. It has 100% of the maintenance tax and the highest decay risk.

Pick one platform first, and add a second only after you measure the first connector's maintenance load. Get an explicit pick from your team before step 4 begins.

## 5. CDC wording (customer-facing)

Never write "CDC support". Log-based CDC reads a database transaction log, and no public API gives a multi-tenant SaaS that. Write this instead:

> "Incremental sync every [N] minutes, eventually consistent. Changes overwritten within one interval are not captured. Deleted expenses are flagged inactive for 90 days, then removed. Records purged while a connection was paused or inactive for more than [X] days require a full re-sync. Approvals and vendors are fully refreshed each sync."

Fill in `[N]` and `[X]`. Webhooks, if you have them, are a freshness supplement only. They capture nothing from before the connection date, so they do not replace backfill.

## 6. Certification targets

- Listing and certification are separate bars. Listing means passing the platform's test suite. Certification is earned later and graded on reliability.
- Build in from day one: every supported sync mode tested, incremental wherever the source allows it, and fast, actionable failure messages.
- Adopt Airbyte's ≥95% sync-success and ≤3-business-day response bars as your own SLOs. Airbyte's formal Partner Certified tier is destination-only.
- Clock: Fivetran requires promotion from Private Preview to Beta within six months. That turns a listing into a schedule commitment.
- No platform charges a source vendor for the badge. The cost is engineering time.

## 7. Maintenance plan

- Budget 15 to 30% of the original build cost per year, reaching 50% in high-change phases. These are vendor-published estimates, so treat them as an order of magnitude.
- Name the month-13 owner and a standing budget before launch. "Side task" is the documented decay path.
- Monitor sync failures and schema-drift errors yourself. A marketplace-tier listing has no platform SLA.
- Your own API changes are your connector's main upkeep cost. Commit to additive versioning with published sunset dates. Industry data shows 87.3% of breaking versions ship with no deprecation notice.

## Proposed sprint

| Step | Work | Estimate |
|---|---|---|
| 1 | Answer the five `modified_at` checks above | ~1 day |
| 2 | Add `Retry-After` and rate-limit headers to 429 responses | ~1 day |
| 3 | Add `modified_at` to approvals and vendors (indexed, filterable, sortable) | days, depending on schema |
| 4 | Add cursor or time-window pagination to expenses and reports | about a sprint |
| 5 | Collect demand artifacts and commission a customer-stack survey | ~2 days |

Scope the bulk or export endpoint for the sprint after that. Connector code starts once steps 1 to 5 pass and the demand gate is met.

## Open questions

These can re-rank everything above. Answer them one at a time if you want me to refine.

1. What demand evidence exists? Support tickets, lost deals, hand-rolled pipelines visible in API logs, or only an internal hypothesis?
2. Which ETL platforms do customers' data teams actually run: managed commercial, self-hosted or open-source, or open-spec taps? This decides the platform.
3. Is the 600 req/min limit per API key, per tenant, or per IP? Is it shared with the customer's own app traffic?
4. What are the `per_page` default and maximum?
5. Do reports, approvals, and vendors support deletion? How does it behave?
6. Who owns the connector in month 13: a named team with budget, a side task, or nobody yet?
7. Is there a deadline (a deal or a competitive evaluation)? A deadline promotes the managed queue. A compounding mandate with real capacity promotes the SDK path.

**Next:** run the five `modified_at` checks against your staging API and paste the results (about 1 day).