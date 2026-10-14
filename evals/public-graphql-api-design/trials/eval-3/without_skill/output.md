**Don't sign off yet.** All three of your safeguards fail or backfire once the partner can reach the subgraph directly. The latency complaint is real, but a direct subgraph route isn't the right fix. I haven't inspected your configs. This is based on your description, so check the points marked "verify".

## Why each safeguard doesn't hold

**1. Introspection off and a separate API key**
- Disabling introspection hides the schema from casual discovery. It doesn't protect any data, and it isn't an access control.
- Federated subgraphs usually still serve `_service { sdl }`, because composition and the router need it. Verify that it's blocked.
- Field-suggestion errors ("Did you mean…") leak names unless they're disabled too.
- The partner will probably know the payments schema anyway, since it's the same data they query through the router.
- The API key is a single shared secret. It gives no per-user or per-tenant identity.

**2. Tagging every type with `@key`**
- Every `@key` type becomes a lookup the subgraph serves directly through `_entities(representations: [...])`. A caller who knows an ID can fetch the object, with no traversal from a parent.
- This is the risk for a partner on a direct route. Your router probably enforces authentication, authorization, tenant scoping and limits before traffic reaches a subgraph. Subgraphs typically trust the router and its forwarded identity headers.
- Going direct skips all of that. Verify these four things:
  - Does `__resolveReference` (or its equivalent) check tenant ownership?
  - Does the subgraph trust a header like `x-user-id` or `x-tenant-id` that the partner could now set themselves?
  - Are router-enforced directives (`@authenticated`, `@requiresScopes`, `@policy`) the only authorization layer?
  - Where do rate limits, depth and cost limits, and audit logging live?
- If any answer is "the router", then in a B2B payments system a partner could read another tenant's payments by guessing or enumerating IDs.
- `@key` isn't free flexibility. Each key commits you to a resolver, makes the type a cross-subgraph contract, and makes the key hard to change later. Reserve it for types that genuinely cross subgraphs.

**3. "Everything is on an internal VPC"**
- That protects the subgraph only while it's unreachable from outside. Giving the partner direct access means opening an ingress or peering path to it, and that removes the protection.
- The payments subgraph then becomes an externally exposed edge. Check what it can reach internally (ledger, accounts, the database), because any flaw there becomes a route inward.
- A static key over the internet, with no mTLS, IP allowlist, or per-partner scoping, is thin protection for payments data.

## What I'd do instead

1. **Find the cause of the latency.** Compare the router's total time with per-subgraph time in traces. If most of the time is in the subgraphs, bypassing the router won't help. If it's query planning or overhead, there are fixes that keep the router in the path:
   - Persisted queries.
   - A warmed query-plan cache.
   - Batching, or entity caching.
   - Fewer round-trips in the report query.
2. **Give the partner their own router instance or listener.** Use a dedicated deployment for batch traffic, with its own capacity, rate limits, auth and quotas. The overnight job can't starve interactive traffic, and every policy stays in place.
3. **Or build a purpose-made reporting path.** Bulk traffic usually fits an async export (file or object-store delivery) or a read-replica-backed endpoint better than live GraphQL. It also keeps heavy reads off the payments primary.
4. **Narrow `@key`.** Review the new types and remove it from any that don't cross subgraphs.

## If the business insists on direct access

Make these conditions of sign-off:
- Per-partner credentials (OAuth client credentials or mTLS), not a shared static key. They need rotation and revocation.
- Tenant identity derived from the credential inside the subgraph, never from a client-settable header.
- Authorization enforced in the subgraph itself, including `_entities` and every `@key` resolver.
- Introspection, `_service` SDL exposure and field suggestions disabled for external callers.
- Depth, cost and rate limits, a timeout, and audit logging on that path.
- A read replica as the data source for the reporting job.
- A network allowlist or private connectivity, not open internet.
- A penetration test or security review before go-live.

## Bottom line

The safeguards are real but fit an internal-only subgraph. They don't suit a subgraph that an external partner calls directly.

I can draft the router-latency investigation checklist or the sign-off conditions as a ticket if you want either.