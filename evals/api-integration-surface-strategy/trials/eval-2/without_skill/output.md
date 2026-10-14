**Recommendation: no. Do not put GraphQL on the public surface roadmap now.** Fix the mobile over-fetch with a cheap targeted change. Revisit GraphQL only if a trigger below fires.

## Why not

- **Wrong reason.** "REST is legacy" is a fashion argument. Your integrators have no complaints. Your OpenAPI contract, SDK generation, and webhooks work.
- **Wrong scope.** The pain sits on one screen of one client you control. A public surface is a different thing, with different costs.
- **Wrong team fit.** Six engineers with no GraphQL experience would take on a second public API plus a learning curve. You would run both APIs for years, because integrators will not migrate on your schedule.
- **Wrong direction of travel.** B2B logistics integrators mostly consume REST plus webhooks. They build ERP and TMS connectors that expect stable, cacheable, versioned resources. GraphQL gives them little they asked for.

## What GraphQL commits you to

1. **Two public APIs, not a replacement.** Deprecating REST means a migration for every integrator. Expect 12 to 24 months of dual support, with each integrator's engineering team involved.
2. **New security work.** Query depth and complexity limits, cost-based rate limiting, persisted queries, introspection policy, and field-level authorization. For multi-tenant shipment data, a missing field-level check leaks across tenants.
3. **New performance work.** N+1 resolvers need DataLoader-style batching. Per-endpoint rate limits and caching stop working. HTTP and CDN caching mostly stop working as well.
4. **New tooling and operations.** Schema registry, breaking-change checks, per-field metrics, error handling (HTTP 200 with errors), and new docs and SDK strategy. You lose your OpenAPI-driven toolchain for that surface.
5. **Webhooks stay as they are.** GraphQL subscriptions do not replace them. You would still maintain the webhook system.
6. **Ownership.** Schema design is a long-lived governance job. With six engineers, it competes directly with your current roadmap.

Rough size: a credible public GraphQL surface is a 2 to 3 engineer-quarter build before any migration work, plus ongoing ownership. These figures are my estimate, not measured on your system. Ask the team for their own number.

## Fix the real problem first

The mobile over-fetch on the shipment list is a real, narrow problem. Options, cheapest first:

1. **Sparse fieldsets on the existing endpoint.** Add `?fields=id,status,eta,destination` to `GET /shipments`. About a few days of work. Document it in OpenAPI. Integrators benefit too.
2. **Lean list representation.** Return a summary shape on list endpoints and the full shape on detail. Also a few days.
3. **Mobile-specific endpoint.** A purpose-built `GET /mobile/shipments` returning exactly what the screen needs. Keep it internal or undocumented in the public spec.
4. **Backend-for-frontend (BFF).** If mobile will have many such screens, build a small BFF owned by the mobile team. GraphQL is acceptable here, because you control both ends, it is internal, and the blast radius is one team. It also gives the team lead his GraphQL experience without a public commitment.
5. **Measure first.** Check payload size, p95 latency, and how many fields the screen uses. If the over-fetch is 40 KB versus 4 KB, options 1 and 2 solve it. If the screen needs five joined resources, option 4 becomes more attractive.

My pick: option 1 plus 2 now, option 4 only if mobile screens keep hitting this problem.

## Triggers that would change my answer

Revisit GraphQL for the public API if any of these becomes true:

- Several integrators ask for flexible querying or complain about chatty multi-call workflows.
- You ship a partner or app-marketplace surface where third parties build UIs against your data.
- Your internal BFF proves out and the team wants to expose it externally.
- You hire or gain real GraphQL operating experience.
- Mobile-driven endpoint sprawl on REST becomes unmanageable (for example, more than 10 bespoke endpoints).

## How to handle the team lead

- Agree that the over-fetch is real, and give it an owner and a date.
- Run a 1-week spike: sparse fieldsets plus a measured before/after on the shipment list.
- Offer the internal BFF as the place to learn GraphQL.
- Put the public-API decision under a written trigger list, so the question is "has a trigger fired?" and not "who is right?"

## Next action

Pull the shipment-list payload size and field-usage numbers from the mobile app (about 30 minutes), then decide between options 1, 2, and 4. If you send me the numbers, I will help size the choice.