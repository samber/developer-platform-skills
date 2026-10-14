# Loamworks GraphQL: versioning, IDs, and the ID migration

I haven't checked this against your codebase or schema. It comes from the GraphQL spec and common practice. Three points up front:

- ❌ Don't put "the question doesn't apply" in writing.
- ❌ Don't ship `id: Int!`.
- ✅ Make the ID migration non-breaking now, before launch.

## 1. Versioning: the claim is half right

**What's right:** GraphQL has no version numbers in the spec. The norm is a single continuously evolving schema where you add fields and mark old ones `@deprecated`.

**What's wrong:** Breaking changes still exist, and compliance's question still applies. `@deprecated` is a flag, not a mechanism. It doesn't make any of your 1,100 integrators stop using the field. At some point you either remove it, which breaks someone, or keep it forever.

Changes that break clients even though no field is removed:
- Making a nullable output field non-null is safe. Making a non-null output field nullable breaks clients.
- Adding an enum value breaks clients with exhaustive switches.
- Adding a required argument or required input field breaks existing queries.
- Adding a union or interface member breaks clients that don't handle it.
- Changing semantics, such as sort order, default page size, validation strictness, or error shape.
- Changing the ID format (your third question).

### Suggested wording for compliance

> The GraphQL API has no version numbers. It evolves additively. Breaking changes are still possible and follow this policy: (1) we classify a change as breaking per the list in Appendix A; (2) a breaking change needs a deprecation notice of at least N months, announced by email and in the changelog; (3) we measure per-field usage by client before removal; (4) we remove a field only after the window ends, and we contact any integrator still using it. A new endpoint version is the last resort for changes that can't be made additively.

You need to set N. The REST API's existing deprecation terms are a sensible anchor. Don't promise "never break" or "zero usage before removal" unless you will fund that.

### Mechanics that make the policy real
1. **Identify clients.** Require a client name or API key on every request, so you know who uses what.
2. **Record usage.** Log field-level usage per client. This is the data behind step 3 of the policy.
3. **Gate schema changes in CI.** Run a schema diff, such as graphql-inspector, Apollo rover, or Hive, against recorded real operations. Breaking changes fail the build.
4. **Default to additive.** Prefer a new field over changing an old one, and use `@deprecated(reason: "Use X")` on the old one.
5. **Keep output fields nullable when unsure.** Loosening a non-null field later is breaking. Tightening a nullable one is safe.
6. **Declare enums extensible.** Say in the docs that clients must handle unknown enum values.
7. **Brown out before removal.** Before removing a field, return errors for it briefly and on a schedule.
8. **Decide the escape hatch now.** If an unavoidable breaking change appears, it ships under a second endpoint such as `/graphql/v2`. The default is that you never need it.

Also note that REST keeps its own versioning rules. A domain change that breaks both surfaces needs a notice for each.

## 2. `id: Int!`: don't

1. **`Int` is 32-bit signed in GraphQL, max 2,147,483,647.** If any primary key is `bigint` or could exceed that, serialization fails. That is a launch-day bug waiting for the first large row.
2. **Per-table integers collide across types.** `User 42` and `Order 42` are different objects. The Global Object Identification pattern (`node(id:)`, Relay-style) needs globally unique IDs. Client caches and refetch logic also lean on this.
3. **It publishes your storage key as API contract.** Clients will parse, sort, and do arithmetic on it. Sharding then can't change anything without breaking them.
4. **Sequential integers invite enumeration.** Authorization must hold regardless, but opaque IDs make guessing harder.

### What to do
- Use `id: ID!` on every object type, opaque and globally unique. `ID` serializes as a string.
- Implement `interface Node { id: ID! }` and `node(id: ID!): Node`. Add `nodes(ids: [ID!]!)` for batch refetch.
- Keep REST paths numeric and unchanged.
- Give integrators a bridge between REST and GraphQL with a separate field, `restId: String`. Call the field what it is. This is the same value REST already exposes, so it carries no new promise.
- Use a string, not `Int`, for `restId` unless every key is guaranteed under 2³¹ forever.
- Make `restId` nullable on day one. If post-sharding objects get no numeric key, a non-null field would then be a breaking change.
- Don't add a `restId` that encodes the shard, a hash, or anything that may change.

**Open question for you:** Are the REST path IDs guaranteed stable through the sharding work? If those numbers also change, that's a REST breaking change and the compliance policy applies there too.

## 3. The ID encoding change four months out

The goal is that the change is invisible to integrators. Integrators will store these IDs in their own databases, so any ID you issue must keep working for years.

### Design now
1. **Version the ID inside the string.** For example, an encoded payload of `v1 | type | key`, in URL-safe, case-sensitive characters. The decoder reads the version first and dispatches. A typed prefix such as `usr_…` is a readable alternative to base64.
2. **Put one codec in one module.** Nothing else encodes or decodes IDs. Add a lint or CI rule that bans `id: Int` and hand-built IDs.
3. **Add golden fixtures.** Keep a file of real v1 IDs with their expected decoded values, and have CI fail if any stops decoding. This is the guard against someone "cleaning up" v1 support.
4. **Document the contract.** IDs are opaque strings. Clients must not parse them, must compare them only for equality, and must treat them as case-sensitive. State a maximum length with headroom, for example 128 characters, so a longer v2 doesn't break column sizes.

### Rules for the migration
- **Never retire v1 decoding.** The server accepts every ID it has ever issued, forever.
- **Pick one policy for what you return, and write it down.** Don't leave it implicit.
  - **Policy (a), the safe one:** existing objects keep their v1 ID for life. Only newly created objects get v2 IDs. Each object has one canonical ID, so client caches and stored references never diverge.
  - **Policy (b):** re-issue v2 IDs for all objects on a date and keep accepting v1 as an alias. This breaks equality between stored IDs and fresh ones, since one object now has two IDs. Avoid it unless forced.
- **Challenge the data team.** Ask why the encoding must change. If a v1 key can be routed to its shard through a lookup or directory table, the ID can stay stable. v1 then resolves through the lookup, and only new objects need shard information embedded in the ID. If routing can't be derived for old keys, ask what the failure case is.
- **Run the cutover as normal evolution.** Ship v2 minting behind a flag. Run both decoders in production first, then flip minting to v2, and announce it in the changelog.

## Decisions for you

1. Pick N for the deprecation window, and approve the compliance wording above.
2. Confirm the REST numeric IDs stay stable through sharding. If not, loop in compliance on REST too.
3. Confirm the largest primary key per table, to settle `restId` as string vs `Int`.
4. Choose ID policy (a) or (b). I recommend (a).
5. Ask the data team whether v1 keys can route to shards through a lookup.
6. Decide whether clients must send a name or key on every request. I recommend yes, because the usage data behind the deprecation policy depends on it.