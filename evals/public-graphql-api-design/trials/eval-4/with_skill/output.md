# Sanity check: Nimbus Archive list fields

Don't ship this proposal as written. Offset on `documents` and `auditEvents` is the wrong design. The non-null `totalCount` and the unclamped `limit` are one-way doors, so you can't walk them back after launch without breaking clients. Only `workspaces` is fine as proposed, apart from the non-null `totalCount`.

I followed the `public-graphql-api-design` skill, including its pagination reference. I didn't ask the skill's clarifying questions because you asked for a sanity check. The assumptions are at the end.

## Why "upgrade after launch" is the problem

- **Moving from offset to cursor changes the arguments.** You'd replace `limit`/`offset` with `first`/`after`. If the return type also changes from a list to a connection, that's a second break.
- **Anything observable becomes contract (Hyrum's Law).** Once partners build "page 4 of 217" UIs and your biggest customer runs a 100k nightly sync, removing either is a breaking change on a public API.
- **Non-null is a promise you can't retract.** A non-null `totalCount` can only be removed or made nullable as a breaking change.

## Verdict per field

| Field | Proposal | Verdict | Do this instead |
|---|---|---|---|
| `documents` (~40M, constant inserts) | `limit`/`offset` + non-null `totalCount` | ❌ | Cursor connection, `first` capped, nullable `totalCount` |
| `auditEvents` (~2B, append-only) | same | ❌ worst case | Cursor connection, no `totalCount` at all |
| `workspaces` (≤~30, static) | same | ⚠️ offset is defensible here | Same connection shape for consistency, tiny cost |

### `documents`

- **Offset breaks under writes.** Customers add documents all day, so offset pagination duplicates and skips rows between page fetches. Your partners' syncs would silently miss or double-count documents.
- **Deep offsets are slow.** `OFFSET 4,000,000` scans four million rows to return 20. Cursor pagination on an indexed `(created_at, id)` costs the same on page 1 and page 200,000.
- **Use a connection.** Default to the Relay connection (`edges`/`node`/`cursor`/`pageInfo`, `first`/`after`). Make the cursor opaque and encode the sort key plus ID. Index whatever the cursor filters and sorts on, or it degrades to the same full-scan cost.

### `auditEvents`

- **It's the worst fit for offset.** 2B rows and constant appends mean that if you sort newest-first, every insert shifts every page. Deep scans over 2B rows are an outage risk.
- **Use a cursor on `(occurred_at, id)`.** Add a required or defaulted time-range filter so a client can't sweep the whole table by accident.
- **Drop `totalCount` entirely.** `COUNT(*)` over 2B rows is not something to put behind a public field. A count of a live, append-only table is stale the moment you return it.

### `workspaces`

- **Offset is the one niche where it survives:** small, mostly static data. Page jumping and drift aren't real risks at ~30 rows.
- **Still use the connection shape.** "Nobody has more than about 30" is an observation, not an enforced limit. A bare list or offset arguments can't be fixed later without a break. Framework support makes the connection nearly free, and it keeps the schema consistent for strangers reading it.
- **Cap `first`** at a documented maximum here too.

## `totalCount` and "page 4 of 217"

Your UI's page-number design is what forces `totalCount`, so question the design.

- **Cost.** An exact count over a filtered 40M-row table is expensive on every paginated response.
- **Accuracy.** The count drifts with constant inserts, so "217" is wrong by the time it renders. Page numbers also don't work on a cursor API, because you can't jump to page 4.
- **The skill's rule.** Never ship a non-null `totalCount` on a public schema unless the count is cheap at real data scale. Your `documents` and `auditEvents` counts aren't.

What to ship:

1. **`documents`:** a nullable `totalCount: Int`. Compute it only when the client selects the field. Document it as an estimate, or serve exact counts from a separate, explicitly costed query.
2. **`auditEvents`:** no `totalCount`.
3. **`workspaces`:** an exact count is cheap, so non-null would work. I'd still make it nullable so all three connection types follow one rule.
4. **UIs:** use next/previous, infinite scroll, or "about 40M documents". Page numbers on 40M live rows imply precision that doesn't exist.

## `documents(limit: 100000)`

Clamp it, with no exception for your biggest customer.

- **Server cost.** A 100k-row response holds a database connection, balloons memory, and times out at proxies. One customer can degrade everyone else.
- **Cost models.** Page size is the multiplier a cost budget prices lists by. A 100k page makes your future rate-limit scoring meaningless.
- **Unclamped is a worse door to close.** Clamping later breaks that customer's sync. Clamp now, while nobody depends on it.

Set a documented, enforced `first` maximum (100 is the skill's example default). The server clamps it and the docs state the exact behavior for an over-limit request.

**Their nightly sync is a bulk-export need, and there are three ways to serve it:**

1. **Cursor loop.** They iterate with `first: 500` or so (your call on the cap), following `endCursor`. Same data, a few hundred requests, no special endpoint.
2. **Incremental sync.** Add a typed filter such as `updatedAfter`, backed by an index. Nightly syncs then pull the delta instead of 40M rows. Soft deletes need tombstones or a deletion-feed field so the customer sees removals.
3. **Async bulk export.** For full dumps, offer an export job that returns a file. This is bulk-export territory, so a REST or job-style endpoint may suit it better than GraphQL.

I'd ship #1 at launch and #2 shortly after. Treat #3 as a possible post-launch addition.

## Six weeks: the effort is small

- **Cursor pagination is days, not weeks.** Most GraphQL server frameworks implement Relay connections natively. The real work is the keyset query and the supporting index per field.
- **A cheap stopgap exists if you're truly squeezed.** Return a wrapper object from day one, such as `DocumentPage { nodes, endCursor, hasNextPage }` with `first`/`after` arguments. This keeps promotion to a full connection additive. Never return a bare list.

```graphql
type Query {
  documents(first: Int, after: String, filter: DocumentFilter, orderBy: DocumentOrder): DocumentConnection!
  auditEvents(first: Int, after: String, filter: AuditEventFilter!): AuditEventConnection!
  workspaces(first: Int, after: String): WorkspaceConnection!
}

type DocumentConnection {
  edges: [DocumentEdge!]!
  pageInfo: PageInfo!
  totalCount: Int # nullable: estimate or skipped when expensive
}

type AuditEventConnection {
  edges: [AuditEventEdge!]!
  pageInfo: PageInfo!
  # no totalCount: 2B rows
}
```

Keep the filters and ordering typed (`input DocumentOrder`, `input DocumentFilter`), never `String` or `JSON`. The cursor must embed the active sort key.

## Launch gates for this part

These pass or fail the skill's pagination and ceiling checks:

- ✅ All three growing lists use cursor connections with a documented, enforced `first` cap. The only deviation is `workspaces`, where offset would be defensible but I'd still use a connection.
- ✅ A request over the cap is clamped or rejected as documented, and the docs state which.
- ✅ A nullable `totalCount` on `documents` only, and none on `auditEvents`.
- ✅ Indexes exist for every cursor sort key, load-tested at real scale, not on a dev dataset.
- ⚠️ Before launch, also set the other ceilings (depth, aliases, cost), keep introspection off for anonymous production callers, and verify no subgraph is reachable if you federate. None of that is in your question, but all of it is a day-one contract.

## My assumptions

I assumed greenfield (no clients yet), third-party partners on the same endpoint, GraphQL already chosen, and no federation. Tell me if any of these is wrong.

- **GraphQL gate:** the skill says to re-ask whether GraphQL fits at all. It fits if web, mobile, and partner clients need different shapes of the same data. Bulk sync is the one use case here that fits REST or export better.
- **Sort orders:** which sorts does `documents` need? Each one needs its own supporting index and cursor encoding.
- **Retrofit:** if any client already exists today, I need the current SDL and real queries before mapping old identities forward.