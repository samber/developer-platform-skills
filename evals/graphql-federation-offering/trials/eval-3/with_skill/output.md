# Verdict: do not publish tonight

`rover subgraph check` passing only means the SDL composes. The skill's point is that composition never checks whether a partner is allowed to claim what it claims. This SDL has three blockers that composition accepts.

**Assumptions** (tell me if either is wrong, because they change the verdict):
- "Partners variant" means a separate variant and router from your first-party production supergraph. If Orbweave composes into the production supergraph, that is the one thing the skill refuses outright.
- `Product` with key `id` is on your extendable-entity allowlist. Nothing in the SDL shows that.

## Blockers (most severe first)

1. **`price: Money! @override(from: "catalog")` takes over a platform field.**
   - Step 3 directive policy: `@override` is "Never" for partners.
   - Once published, the router sends every `Product.price` query to Orbweave instead of your catalog subgraph. A partner outage or a wrong price lands on first-party data.
   - Fix: delete the field. Orbweave has no business owning price.

2. **`type Money @shareable` is unprefixed and lets Orbweave co-resolve your `Money` type.**
   - Step 3 and the type rules: partner types must be namespaced, and `@shareable` is never allowed on platform types.
   - The unprefixed name merges with your `Money`, so this is a redefinition, not an extension.
   - Co-resolving shareable fields is also the trigger for planner CVE-2024-43414, an infinite loop. It is fixed in Router 1.52.1 and query-planner 2.8.5, but a partner should not be able to opt you in.
   - Fix: delete it.

3. **`reviewDigest @requires(fields: "email")` ships personal data to the partner.**
   - Step 4: every `@requires` field is sent to Orbweave on each resolve, even when the client never selected it. A list query sends it once per row.
   - `email` is on the clearance list only if you have all of these: tenant consent recorded at install, signed data-processing terms with Orbweave, and a residency check of their hosting region.
   - If any of the three is missing, drop it. A review digest should not need an email address. If it genuinely does, expose a derived, coarser field (a hashed ID, for example) that is hidden from the public schema.
   - The `@external` declaration on `email` goes away with this.

4. **Non-null partner fields on a platform type: `orbweaveRating: Float!` and `price: Money!`.**
   - Step 3 and the exposure gate: a failing non-null partner field nulls the whole `Product`.
   - Fix: make `orbweaveRating` nullable. `price` is already removed by blocker 1.

5. **Unprefixed names: `Review`, `Money`, `Query.reviews`, and `reviewDigest`.**
   - Step 3: every partner type and root field carries the partner prefix, or it collides with or merges into yours. `Review` is a very likely collision.
   - Fix: use `Orbweave_Review`, a single `orbweave` root field, and `orbweaveReviewDigest`. `orbweaveRating` is already prefixed.

## Findings (not blockers)

- **Unused `@provides` import.** It is harmless today, but `@provides` is "Never" for partners, so the policy check should reject the import. Drop it from the `@link` import list.
- **Check the `@link` version.** `federation/v2.7` must sit inside the range your router supports and you pin. A newer dialect than the router supports fails composition for everyone.
- **Rung choice.** This is a partner subgraph (rung 5). That is defensible for a contracted partner. After the fixes, the only live-partner data left is a rating and some reviews, which a platform-operated connector (rung 3) could also serve. Promote to rung 5 only if you will staff partner schema review as a standing job. This is a finding, not a blocker.
- **Docstrings.** Mark each partner field as provided by Orbweave and not covered by your SLA.

## Corrected SDL (what I would accept)

```graphql
extend schema @link(url: "https://specs.apollo.dev/federation/v2.7", import: ["@key", "@external", "@requires"])

type Product @key(fields: "id") {
  id: ID!
  """Provided by Orbweave Reviews. Not covered by the platform SLA."""
  orbweaveRating: Float
}

type Orbweave_Review {
  id: ID!
  body: String!
}

type Orbweave_Namespace {
  reviews(productId: ID!): [Orbweave_Review!]!
}

type Query {
  orbweave: Orbweave_Namespace
}
```

I dropped `reviewDigest` and `@requires`, so the `@external` import is unused here and can come out too. Re-add the digest only after the email decision in blocker 3.

## Gates to add before any publish

1. **Policy check as a blocking step.** A platform-owned step must parse the submitted SDL and reject:
   - `@override`, `@provides`, `@shareable` on platform types, `@interfaceObject`, and `@inaccessible` outside the partner namespace
   - unprefixed types
   - non-null fields on platform types
   - any `@requires` field off the clearance list

   Test it by submitting this exact SDL and confirming it is rejected. Rover cannot do that for you.
2. **Who publishes.** Orbweave runs checks only, with a credential scoped to their own subgraph. Only you publish to the partners variant.
3. **Operation checks** against client usage on the partners variant.

## Runtime controls the SDL cannot show

I could not check these from the SDL. Confirm each one before go-live:

- **Credentials.**
  - No end-user `Authorization`, `Cookie` or platform key reaches Orbweave.
  - Use a per-partner token that is short-lived and bound to Orbweave's audience and the installing tenant.
  - Use an explicit header allowlist, with no catch-all propagation.
- **Orbweave's endpoint.**
  - It authenticates every call (mTLS or a signed platform token).
  - It answers `_service` and introspection only to you. Otherwise anyone can post `_entities` keys and enumerate data.
- **Routing URL.** HTTPS and a public host only, re-checked on every resolution, through a dedicated egress path.
- **Blast radius.**
  - Set a per-partner timeout: client SLA minus internal p95 minus a margin. Router defaults of 30–60 s are too high.
  - Add a circuit breaker, or an egress proxy with outlier detection.
  - Set a request-level deadline above the partner timeout.
  - Price Orbweave fields in the cost model and rate-limit them per partner.
- **Caching.** Orbweave responses are excluded from shared caches and from cross-request deduplication, or keyed per tenant.
- **Visibility.** Use an include-only contract filter, and enforce at request time that only tenants who installed Orbweave see its fields.
- **Operations.** Set up per-partner latency, error and timeout metrics, an owner, a suspension threshold, and an offboarding plan with a removal-impact check.

## Next step

Send Orbweave the rejection reasons and the corrected SDL. Publish only after the policy check exists and passes. If the policy check cannot be ready tonight, the safe fallback is to hold the publish, not to publish and patch later.

I read only the skill and its two policy references. The platform-cases reference and the skill's evals I did not open.