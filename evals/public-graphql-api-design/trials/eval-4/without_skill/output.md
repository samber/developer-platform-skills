**Verdict: don't ship it as proposed.** Offset and `totalCount` are fine on `workspaces` and wrong on the other two. You have six weeks, so doing it right now costs days, and fixing it after launch costs a breaking change.

I haven't seen your code. I'm assuming GraphQL and a Postgres-like store.

## Why the plan breaks

1. **Fixing it after launch is a breaking change.** Once partners build on `limit`/`offset`, those args are your contract. Moving to cursors means a deprecation cycle, and some partners will never migrate. "Upgrade later once the pressure is off" is the expensive path.
2. **`documents` offset drifts.** Customers add rows all day, so a new row shifts every page by one. Clients get duplicates and skipped rows. A nightly sync can silently miss documents.
3. **`auditEvents` offset is unusable at depth.** `OFFSET n` reads and discards n rows, so deep pages on 2 billion rows time out. Anyone can also send `offset: 1900000000` and tie up a database worker.
4. **A non-null `totalCount` is the most expensive field here.** An exact `COUNT(*)` on 40 million rows takes seconds, and on 2 billion rows it is effectively impossible. It runs on every request, unless your resolver only computes it when the field is selected. "Page 4 of 217" is also wrong the moment someone adds a document. Making it non-null also means you can never degrade it later without a breaking change.
5. **An unclamped `limit: 100000` is an outage waiting to happen.** One request can exhaust memory or hit gateway timeouts, and any partner can send it, not only your biggest customer. A single huge response also fails all-or-nothing and can't resume.
6. **The nightly sync is the wrong use case for offset.** That customer needs "everything that changed since last night", not page 4 of 217.

## What to ship instead

| Field | Pagination | `totalCount` | Max page size |
|---|---|---|---|
| `workspaces` | Plain list, no pagination args. It's about 30 rows and nearly static. | Not needed, since the list length is the count. | Hard cap 100 |
| `documents` | Cursor connection: `first`/`after`, `pageInfo { hasNextPage endCursor }`. Keyset on `(createdAt, id)`. | Nullable, computed only when selected, documented as approximate. Cache it per workspace. | 1,000 |
| `auditEvents` | Cursor connection only. Append-only data makes this easy: the cursor is a monotonic id. | Leave it out. Require or default a time-range filter. | 1,000 |

- **Cursors are not much harder than offset.** It's roughly a few days for a shared connection helper, not an afternoon, and it fits your six weeks.
- **Replace "page 4 of 217" in the UI.** Use next/previous and "about 8.7M documents". If product insists on numbered pages, restrict that to `documents` with a capped offset (say ≤ 10,000), and plan to remove it.
- **Make the cursor opaque** (base64-encoded). That lets you change the keys behind it without another breaking change.

## The biggest customer's nightly sync

Give them a purpose-built path instead of one 100,000-row call:

1. **Incremental sync (recommended):** `documents(first: 1000, after: $cursor, updatedSince: $ts)`. This needs an index on `(updatedAt, id)`. They loop until `hasNextPage` is false, and every request is bounded and resumable.
2. **Full dump, if they truly need everything:** an async export job (`createExport` → poll → signed URL to a file in object storage). This takes the load off the API.

Tell them now. Moving a big customer onto a loop is easier before launch than after.

## Also before launch

- Add per-request query cost limits and rate limits per API key. Clamping `first` alone doesn't stop expensive queries.
- Reject out-of-range `first` with a clear error rather than silently clamping, so clients notice.

## Minimum if time gets tight

Ship cursor pagination with the 1,000 clamp on `documents` and `auditEvents`, skip `totalCount` entirely, and leave `workspaces` as a plain list. You can add a nullable `totalCount` later without breaking anyone. You can't take away a non-null one.

Two questions would sharpen this: is `documents` scoped per workspace (which makes counts much cheaper), and what is the sync customer's tolerance for changing their integration before launch?