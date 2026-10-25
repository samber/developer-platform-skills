# Partner SDL policy

The rules a platform enforces on every schema a partner submits, whether as a partner subgraph (rung 5) or as the contract behind a mediated extension field (rung 4). Load this when writing the policy check, reviewing a partner's SDL, or wiring the CI gate.

## Contents

- Directive policy table
- Type and field rules
- SDL examples
- Wiring the CI gate
- Removal-impact checks

## Directive policy table

Composition checks that a supergraph is valid. It never checks that a contributor is allowed to claim what it claims. This table is that missing authorization layer. Concept names come first because directive names differ across federation dialects and the open Composite Schemas specification.

| Concept | Apollo Federation directive | Partner may use? | Why |
| --- | --- | --- | --- |
| Ownership transfer | `@override(from:)`, incl. progressive `label:` | Never | Takes resolution of a platform field; progressive labels make the takeover partial and harder to notice. |
| Co-resolution | `@shareable` | Never on platform-owned types or fields; allowed only on types inside the partner's own namespace | Lets the planner route a platform field to the partner. Also the trigger condition for planner CVE-2024-43414. |
| Assertion of another owner's data | `@provides` | Never | The router accepts the partner's values for fields it does not own, without asking the owner. |
| Global visibility | `@inaccessible` | Only on the partner's own namespaced fields | Applied anywhere, it hides the element in every subgraph: one partner can remove platform fields from the API schema. |
| Interface-wide extension | `@interfaceObject` | Never | Adds fields to every implementation of a platform interface at once. |
| Entity extension | `@key` on a platform entity | Yes, only for entities on the extendable allowlist, using the published key fields | This is the legitimate extension point; the allowlist is the contract. |
| Dependency on platform data | `@requires(fields:)` | Only fields on the partner's data-clearance list for that entity | Every required field is shipped to the partner in the entity representation, whether or not the client selected it. |
| Access control | `@authenticated`, `@requiresScopes`, `@policy` | Platform reviews, never trusts | These live in the partner's SDL; a missing or weakened declaration is the partner deciding platform authorization. |
| Visibility tagging | `@tag` | Only platform-assigned tag values | Tags drive contract filtering; a partner-chosen tag can opt a field into a contract it should never reach. |
| Composition version | `@link` federation version | Pinned range set by the platform | A newer dialect than the platform router supports fails composition for everyone. |

## Type and field rules

- Prefix every partner type and root field with the partner namespace (`Acme_Shipment`, or a single `acme` root field returning `AcmeNamespace`). No unprefixed type name ever composes, because same-named types merge or collide with the platform's.
- Make every partner field on a platform type nullable. A non-null partner field that fails propagates null upward and blanks the platform object the client asked for.
- Add partner fields to platform entities only; never add arguments to platform fields or members to platform enums, unions or interfaces.
- Keep partner mutations under the partner namespace. A partner mutation must never be reachable as a platform-named root field.
- Write docstrings for the public audience and mark each partner field's owner (`"""Provided by Acme Logistics. Not covered by the platform SLA."""`).

## SDL examples

```graphql
# ✓ Good - extends an allowlisted entity by its published key, namespaced, nullable
type Order @key(fields: "id") {
  id: ID!
  acmeShipmentStatus: Acme_ShipmentStatus   # nullable: partner outage yields null + error
}

type Acme_ShipmentStatus {
  carrier: String!
  etaDays: Int
}
```

```graphql
# ✗ Bad - claims a platform field, asserts platform data, collides on a type name
type Order @key(fields: "id") {
  id: ID!
  total: Money! @override(from: "billing")      # ownership transfer
  customer: Customer! @provides(fields: "email") # asserts platform-owned data
}

type Money @shareable {                            # unprefixed, co-resolves platform Money
  amount: Int!
  currency: String!
}
```

```graphql
# ✗ Bad - @requires pulls a field outside the partner's clearance list
type Customer @key(fields: "id") {
  id: ID!
  taxId: String @external
  acmeRiskScore: Float @requires(fields: "taxId")  # taxId now ships to the partner on every resolve
}
```

## Wiring the CI gate

Run the policy as a check that blocks the partner's publish, never as a review comment the partner can ignore.

1. The partner runs the composition check against the platform's partner variant in its own CI, before submitting.
2. The platform's registry runs the same composition check on submission.
3. A platform-owned policy step parses the submitted SDL and rejects any row above marked "Never", any unprefixed type, any non-null field on a platform type, and any `@requires` field off the clearance list.
4. Only the platform publishes to the partner variant. Partners never hold publish credentials for it.

Integration note, current command names per registry:

- Apollo GraphOS: `rover subgraph check` / `rover subgraph publish`; custom policy via a check webhook or a separate lint step.
- WunderGraph Cosmo: `wgc subgraph check <name> --schema <file>`; `--label` checks a subgraph that does not exist yet; subgraph check extensions send an HMAC-signed webhook to a self-hosted endpoint that can fail the check - the natural home for the policy step.
- GraphQL Hive: `hive schema:check` / `hive schema:publish`; run the policy step in the same pipeline.

## Removal-impact checks

Removing a partner subgraph removes public fields clients query. Before offboarding:

1. Run the registry's removal-impact check (Cosmo `wgc subgraph check --delete`; Apollo operation checks against a composition without the subgraph).
2. Pull per-field usage for the partner's fields over the notice window.
3. Remove the subgraph from the partner contract first, then from the base graph.
4. Hand notice periods to the versioning policy; a partner's departure is a breaking change for every client that selected its fields.
