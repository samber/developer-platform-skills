# Loamworks GraphQL: versioning, IDs, and the ID-encoding change

I read the skill and its four references. You haven't answered the skill's clarifying questions, so I flagged my assumptions where they matter.

## Summary

| Question | Verdict |
|---|---|
| "GraphQL doesn't do versions, so breaking changes don't apply" | ❌ Don't put that in writing. |
| `id: Int!` with REST's numeric PKs | ❌ Use `id: ID!` on a `Node` interface, with opaque global IDs. |
| ID encoding changes in about 4 months | ⚠️ Plan for it now. Make the encoding opaque and versioned from day one, and accept old IDs forever. |

## 1. "GraphQL has no versions" is wrong

**The claim that breaks.** Deprecation is a mechanism, not a policy, and it doesn't remove breaking changes. Three problems:

- **Removing a deprecated field is still a breaking change.** Giroux's caution in the skill applies: deprecation "requires work from integrators at best, or constitutes a breaking change at worst." With about 1,100 integrators, the removal date and notice period are what your compliance team is really asking about.
- **Many breaking changes can't be deprecated.** Examples:
  - changing a field's type or nullability;
  - adding a member to a result union that clients already handle;
  - tightening a depth or page-size ceiling;
  - changing a field's meaning;
  - changing the ID format (your question 3).
- **Versioned GraphQL APIs exist.** Shopify ships date-based versions of its GraphQL Admin API every quarter, supports each for at least 12 months, and requires it for new public app submissions. The paradigm doesn't decide the policy. You do.

**What to tell compliance.** Replace "the question doesn't apply" with a written evolution policy. The skill makes this a decision for your team, which it hands to `api-versioning-policy`. Here is my recommendation:

1. **Additive-first.** New fields, types and payload members ship without notice. Design shapes so they can grow: payload objects and result unions, never bare scalars.
2. **Deprecate with `@deprecated(reason: ...)`.** Announce the date, name the replacement, and track per-field usage by client.
3. **Remove only after a published notice period and only once usage telemetry shows the field is quiet.** You set the period. Shopify's 12-month floor is a reference point, not a rule for you.
4. **Name the escape hatch for changes deprecation can't express.** Choose one:
   - an opt-in request header, like GitHub's ID migration (section 3);
   - date-versioning, like Shopify.
5. **Give the REST surface its own existing policy.** It keeps whatever versioning it has today. I don't know what that is, so state it separately.

Suggested sentence for the document: *"The GraphQL API evolves additively. Fields are deprecated with a published notice period before removal. Changes that can't be expressed as deprecation, such as identifier format, ship behind an opt-in mechanism with a published sunset date."*

If you can't commit to the notice period yet, say so. That is better than claiming it doesn't apply.

## 2. IDs: don't use `Int!`

Use this:

```graphql
interface Node { id: ID! }
type Order implements Node { id: ID! ... }
type Query { node(id: ID!): Node }
```

**Why `Int!` fails:**

1. **It can't implement `Node`**, which requires `id: ID!`. You'd lose refetch-by-ID.
2. **GraphQL `Int` is signed 32-bit** (max 2,147,483,647). If any PK is `bigint`, large values will fail serialization. Check this against your tables.
3. **It exposes an implementation detail.** The skill's anti-pattern list names `mysql_id`-style fields, and a raw PK is the same thing.
4. **It makes question 3 a breaking change.** Moving `Int` to anything else changes the type in every client's query variables (`$id: Int!` becomes `$id: ID!`) and is not deprecatable. Hyrum's Law applies: once integrators see numeric IDs, those numbers are the contract.

**Bridging REST and GraphQL.** Don't copy numeric IDs into GraphQL. Use GitHub's approach, where one identity system serves both APIs:

- REST paths keep their numeric IDs, unchanged.
- Add a `node_id` field to REST responses. The addition is non-breaking.
- `node_id` is the GraphQL global `id`. An integrator fetches via REST, takes `node_id`, and passes it to `node(id: ...)`.
- Never expose `authorId: Int`-style foreign keys. Expose references instead (`author: User!`).

**Decision for you.** Integrators with six years of stored numeric IDs may want to look up an object from a legacy ID. You can serve that with a dedicated documented lookup, or by telling them to use REST's `node_id`. Don't add a numeric `databaseId` field to the GraphQL types. It would freeze the numbers, and sharding may break them.

## 3. The ID encoding will change in about four months

You're right to raise this now, because the answer shapes launch.

**At launch**
- Document that IDs are **opaque strings: don't parse, don't construct, store as-is.**
- Document a generous maximum length so a longer encoding later isn't a breaking change.
- Embed a **format version** inside the encoded payload. Base64 of `v1:<type>:<pk>` is the shape. The server can then decode every generation.

**At the sharding cutover** (GitHub's precedent)
- GitHub changed its global ID encoding without a forced migration. It shipped an `X-Github-Next-Global-ID` header: `1` always returns the new format, `0` returns legacy or new based on the object's creation date.
- **Any consumer who never stored an ID needed no change.** The blast radius shrank to the integrators who had persisted IDs.

Rules for your cutover:

1. **Accept every ID generation as input, permanently.** An integrator's stored ID must keep working. If sharding needs a shard key in the new encoding, the data team owns a legacy-to-shard lookup. This is the real engineering cost, and I can't size it without knowing the sharding design.
2. **Keep an existing object's output ID stable by default.** The new format applies to objects created after cutover, or by opt-in header. Normalized client caches (Relay, Apollo) key on `id`. If the same object returns a different string over time, clients get duplicate or stale entries.
3. **Gate any forced re-encoding of existing objects behind the opt-in header, with a published sunset.** This is the escape hatch from section 1, and it should be written into the policy now.
4. **Test it before launch.** Write a decode test for the v1 format and a fixture "v2" format to prove the dual-decode path.

**Question for the data team.** Do the numeric PKs in REST paths survive sharding unchanged? If they do, REST paths stay stable. If they don't, REST has the same problem.

## Assumptions to confirm

- REST stays alive and keeps its own versioning.
- Some PKs may be `bigint`.
- Sharding needs a new ID shape, not just a new database.
- You haven't yet decided which of the skill's step 1 triggers justified GraphQL. Name it in the decision record: different client shapes, nested variable data, or high-latency mobile.

## Deferred

I haven't covered these yet, and they should be settled before SDL:

- mutation-naming order;
- pagination (Relay connections, with a page-size cap);
- error surface (hybrid split);
- depth and breadth ceilings;
- federation boundary, if you have one;
- persisted-query policy (first-party allowlist only).

Tell me which fork you want first. I suggest the mutation-naming order, since it's a one-line decision.