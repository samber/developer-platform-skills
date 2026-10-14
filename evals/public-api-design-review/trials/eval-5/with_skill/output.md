# Public API design review: Coastline Retail `/v1` (pagination and list behavior)

## Verdict

**Do not publish yet.** Six Must-change findings are open (below). On Product's request, **keep offset on `/products` as a recorded, conditional deviation**. It does not need to change, and the rest of the surface should not copy it.

The skill's checklist lists "web UI page numbers" as the case where page/offset is the right fit. Numbered pages and jump-to-page need random access, and cursors cannot give you that. The deviation holds if all six conditions below are met.

## Scope

- **Surface:** public `/v1`, pre-publication. I treated this as public beta/GA, so the review is blocking.
- **Rule corpus:** you named none, so findings cite this skill's `review-checklist.md` by item.
- **Evidence:** only your written description. I had no OpenAPI spec and no sampled responses, which the skill says to request. Treat this as a partial review. Dimensions 1–4, 7 and 8 and the five sibling checks were not walked.

## Dimension summary (pagination and filtering evidence only)

| Dimension | Result |
|---|---|
| 5. Pagination | **FAIL**: 5 findings |
| 6. Filtering, sorting, field selection | **FAIL**: 1 finding; sort-field validation unverified |
| 4. Field naming | Partial: `per_page` vs `limit` is a naming split (folded into finding 1) |
| 1, 2, 3, 7, 8, sibling checks | **Not assessed**, spec needed |

## Findings

| # | Finding | Bucket | Cited rule | Fix |
|---|---|---|---|---|
| 1 | Three pagination patterns: `/products` uses page/`per_page`, `/orders` uses cursor/`limit`, `/stores` has none. | Must-change | "One pagination pattern across the whole surface" | Cursor + `limit` is the surface standard. Use `limit` as the size parameter everywhere, so the `/products` deviation is only page vs cursor. |
| 2 | `/stores` returns all 1,400 rows in one array. | Must-change | "Every collection endpoint is paginated" | Cursor pagination with the same default and max as `/orders`. 1,400 rows is small today, but "we don't need pagination for now" is a listed rationalization to reject. |
| 3 | `per_page=5000` is silently clamped to 100. | Must-change | "Requesting past the maximum returns 400, never a silently clamped value" | Return 400 naming the limit and the maximum. Document the default and maximum per endpoint. |
| 4 | `?statuss=shipped` returns the full unfiltered list. | Must-change | "A filter on an unknown field... returns 400/422, never silently ignored" | Enforce centrally with a per-endpoint parameter allowlist, not per handler. Return 400 naming the unknown parameter, on all collections including `/products` and `/stores`. |
| 5 | Cursors are not bound to the sort. An `id` cursor is accepted under `sort=-created_at` and under `sort=total_amount`. | Must-change | "For cursor pagination the sort is encoded into the cursor, so a cursor minted under one sort can't be replayed against another" | Encode sort key, direction and last-row values in the cursor. Keyset on `(sort_col, id)`, because `total_amount` has ties. Return 400 on a sort mismatch. This is a silent wrong-results defect, not a style issue. |
| 6 | Every list carries a `COUNT`-based `total`, and on `/orders` (240M rows) that is your slowest query. | Must-change on `/orders` (and any large collection); Improvement elsewhere | "Total count... is a deliberate cost decision... should be opt-in (`?include_total=true`)" | Drop `total` from cursor-paginated lists by default. The strategy table shows cursor pagination has no total, so `/orders` already contradicts its own pattern. Return `has_more` instead and offer opt-in `include_total`, or an estimate. Removing a published field later is breaking, so doing this before publishing is free. |
| 7 | Cursors are base64'd row IDs. | Improvement | Hyrum's Law (dim. 8): decodable means someone will craft cursors | Fold into finding 5. Make cursors opaque (versioned, signed or encrypted) and document them as opaque. |

**Unverified, so I could not grade them:**
- Whether `has_more` and navigation links exist.
- Whether an invalid `sort` field returns 400.
- Behavior on empty, last-page and out-of-range requests.

The checklist requires all of these to be specified.

## Accepted deviation: offset/page on `/products` (conditional)

**Rationale to record:** the web admin needs numbered pages and jump-to-page, which require random access and a total. The strategy table lists this as offset's one strength.

**Conditions:**
1. Record the rationale in the deviation log. The skill treats this as a precedent, so it applies to admin-facing collections only. `/orders` and `/stores` do not inherit it.
2. Confirm the catalog is small and slow-changing, or cap the maximum page depth. Offset degrades at large offsets and drifts under writes (duplicates and skips between pages). Product needs to confirm the size.
3. Apply the fixes from findings 3 and 4 to `/products` too: `limit` naming, 400 above the maximum, 400 on unknown parameters.
4. Keep `total` on `/products` only if the count is cheap there. Numbered pages justify it, but measure it.
5. Keep the same envelope, `has_more` and error shape as the cursor endpoints.
6. Document the write-drift caveat for external consumers.

**Alternative, not required:** a separate admin-only endpoint with offset, leaving the public `/products` on cursors. That removes the deviation entirely, but it costs a second surface. Choose it only if conditions 2 or 4 fail.

## Ship gate

Findings 1–6 are open, so **publishing is blocked**. Finding 7 can ship open, but the cursor format is far easier to change before release. Because nothing is published, the fixes are not breaking changes for external clients. Check internal consumers first (see question 2).

## Questions that would change this review

1. Can you send the OpenAPI spec and 5–10 real responses across endpoints? Without them, dimensions 1–4, 7 and 8 and the sibling checks (versioning, idempotency, auth, rate limits, docs) stay unreviewed, and the coverage gate fails.
2. Which internal clients already depend on today's behavior (web admin, mobile, partners)? That decides whether the pagination changes count as breaking for them.
3. How many products are there, and how fast does the catalog change? This decides whether offset is safe or needs a depth cap (condition 2).
4. Is the web admin built on this same public API? If it is, the deviation stands. If not, the admin-only endpoint becomes viable.
5. Does your team follow a rule corpus (Zalando, Google AIPs, your own)? If it does, the citations should come from it.