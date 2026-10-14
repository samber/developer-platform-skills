**Verdict: do not publish /v1 as is.** Every item below is a one-way door. Fixing it after launch breaks clients. Fixing it before launch is cheap.

Next action: tell Product the offer in section 1, then start with the validation work (sections 3 and 4).

## 1. Product's offset on /products

Offset on /products is fine. The reason is catalog size, not the admin UI.

- Offset cost grows with depth: `OFFSET N` scans N rows. A small catalog makes that cost trivial.
- Jump-to-page needs offset and a total. Cursors cannot jump.
- A public contract should not follow an admin UI need, but here the cost is low.

The offer:

1. Keep `page` on /products only, as a documented exception.
2. Cap depth, for example `page * limit <= 10,000`. Past the cap, return 400 `invalid_parameter`.
3. Also accept `cursor` on /products. Cursor is the canonical mode, and `page` is the secondary one. Reject requests that send both.
4. Rename `per_page` to `limit`, so every endpoint uses the same name.
5. Keep `total` on /products as opt-in (see section 5).

This rests on one fact I do not have: the /products row count. If it is above about 1M, or will be soon, move the admin to an internal offset endpoint and keep the public API cursor-only.

## 2. /stores returns all 1,400 stores as a bare array

- **Add an envelope and pagination now:** `{ "data": [...], "next_cursor": null, "has_more": false }`.
- A bare array cannot gain `next_cursor` later. Changing it to an object breaks every client.
- Add `limit` (default 100, max 500) and `cursor`. Today that is 3 pages.
- Use the same envelope on every list endpoint.

## 3. Silent clamp: `per_page=5000` returns 100

- Return 400 with the maximum in the error body: `{"error":"invalid_parameter","param":"limit","max":100}`.
- A silent clamp hides bugs. A client that asks for 5000 and gets 100 may take the short page for the end of the data.
- Validate `0`, negative, non-integer and empty values the same way.
- Always return the effective `limit` in the response.

## 4. `?statuss=shipped` returns the unfiltered list

This is the worst item here. A client that runs a bulk action on "shipped" orders acts on all 240M.

- Reject unknown query parameters with 400 and list the allowed ones.
- Validate enum values. `status=shiped` must also return 400.
- Be strict from day one. Tightening later breaks clients. Loosening later does not.

## 5. `total` via COUNT on 240M rows

- Remove `total` from default responses on every list endpoint.
- Add opt-in `?include_total=true`:
  - Allow it on /products and /stores, where it is cheap.
  - On /orders, either omit it or return `total_estimate` labeled as an estimate. Use planner stats for that, and only when no filter is applied.
- Compute `has_more` by fetching `limit + 1` rows. It costs nothing extra.
- Removing a default field later is a breaking change. Making it opt-in before launch is not.

## 6. /orders cursors: base64 row ID, shared across sorts

Two bugs:

1. **The cursor ignores sort order.** A cursor from `sort=-created_at` works under `sort=total_amount`. It returns silently wrong pages with skipped and duplicated rows. The reason is that an ID says nothing about position in a different ordering.
2. **A bare ID cannot page on a non-unique sort key.** Many orders share a `total_amount`. Use keyset on `(sort_value, id)`, with `id` as the tiebreaker.

Fix:

- Encode in the cursor: format version, sort spec, the last row's sort value and `id`, and a hash of the active filters.
- On each request, compare the cursor's sort spec and filter hash to the request. A mismatch returns 400 `invalid_cursor`.
- Sign the cursor with HMAC so clients cannot forge or edit it, and document it as opaque. Today clients can decode it and depend on its shape.
- Allowlist the sort fields. Only allow fields with a composite index such as `(total_amount, id)`. A sort on an unindexed column over 240M rows will time out.
- Make the default sort `id` or `-created_at`. Always append `id` as the tiebreaker.

## Cross-cutting contract

- One parameter pair: `limit` and `cursor`. `page` exists only on /products.
- One envelope: `data`, `next_cursor`, `has_more`, plus optional `total`.
- One error shape for all 400s.
- Publish the defaults and maximums in the docs.

## Rough effort

My estimate, assuming one backend dev and a normal web framework:

- Validation (unknown params, enums, limit): about 1 day.
- Envelope and `total` change: about 0.5 day.
- Cursor rework plus sort indexes and tests: about 2 to 3 days. The indexes depend on how long they take to build on 240M rows.

## Open questions

1. How many rows does /products have?
2. Do orders need sorts beyond `created_at` and `total_amount`?