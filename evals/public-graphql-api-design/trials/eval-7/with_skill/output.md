# Sablefield public GraphQL schema: review of `Customer`, `Viewer`, `TeamMember` and `updateCustomer`

I applied the `public-graphql-api-design` skill and its references. It asks several clarifying questions first (see the end). I answered your three questions from the SDL you sent, and I flag the points that depend on those answers.

## 1. Collapse into one `User`: no

Keep `Viewer`, `TeamMember` and the person-shaped fields on `Customer` as separate types. The skill covers this case under Giroux's MOIST principle ("Moist Once Is Sometimes Tolerable"). Types that share `name` and `email` can serve different use cases and evolve independently. Design types around client use cases, not around duplicated fields.

Your three types already differ:

- **`Viewer`** is the authenticated caller. It is the natural home for "me" fields such as the caller's own permissions and settings.
- **`TeamMember`** is a colleague seen through a team. It carries `role`.
- **`Customer`** is not a user at all. It is a serviced party that never logs in. A merged `User` would put customers and staff in one type, so every future staff-only field would need per-field auth.

Merging couples all three to one evolution path. Splitting them later would be a breaking change, whereas the duplication costs three lines of SDL.

Your Customer SDL has no name or email today. If they exist elsewhere, the same reasoning applies.

If the duplication still bothers the architect, share it in the resolver layer. Reuse one internal person-loader behind all three types. Don't share it in the public schema.

## 2. `updateCustomer` or `customerUpdate`: pick one, but fix the larger problem first

**The name fork is a documented tie.** Apollo uses verb-first (`updateCustomer`). Shopify uses noun-first (`customerUpdate`), so a type's mutations sort together. The skill's rule is to pick one and enforce it across the whole schema, because a single deviating mutation fails the consistency gate.

**Tiebreakers, in order:**

1. If your internal graph or any existing client already uses one order, keep it. Anything observable is contract (Hyrum's Law).
2. Otherwise choose verb-first. It reads as an action, and field-service mutations are business actions.
3. Choose noun-first only if you expect many CRUD-shaped mutations per type and want them grouped.

Then add a lint rule so the choice holds.

**The bigger problem is the mutation's shape, which has three defects:**

- **Monolithic update.** One `updateCustomer` handling every field is the "one monolithic CRUD update" anti-pattern. Model business actions instead, such as `changeCustomerContact`, `reassignCustomerOwner` and `deactivateCustomer`. These names are illustrations. Use your own domain verbs.
- **Bare `Customer` return.** `Customer` is nullable, with no payload and no typed failures. Return a result type that can carry expected business failures.
- **Merged input.** `CustomerInput` blurs which customer is the target. Per Shopify Rule #22, separate the selection argument from the change data.

```graphql
type Mutation {
  updateCustomer(
    customerId: ID!
    customer: UpdateCustomerInput!
  ): UpdateCustomerResult!
}

union UpdateCustomerResult =
  | UpdateCustomerSuccess
  | ValidationError
  | CustomerNotFound

type UpdateCustomerSuccess { customer: Customer! }
type ValidationError { code: ErrorCode! message: String! field: String }
type CustomerNotFound { code: ErrorCode! message: String! }
```

- **Not-found and forbidden look the same.** `CustomerNotFound` must also be what a caller sees for a customer they aren't allowed to see. Otherwise the response shape tells them whether the customer exists.
- **Keep top-level `errors` for the rest.** Use them only for server faults, malformed queries and authentication.
- **Add a shared `ErrorCode` enum** so clients switch on codes while message text stays free to change.
- **Expect most mutations to need a result union.** If more than one mutation needs it, define a shared `Error` interface.

## 3. The `Customer.accountId` docstring: rewrite it

The docstring "mirrors the account_id column synced nightly from NetSuite" names your database column, your ERP vendor and your sync cadence. Every schema reader, including competitors, would see all three. The skill flags this exactly: docstrings written for the engineering team publish architecture.

Don't just reword it. The field itself is wrong. It is a foreign-key ID (`accountId`), and the same applies to `ownerId`. The skill's rule is to expose object references, not foreign keys (Shopify Rule #8), so integrators get the depth they need in one query.

**Replacement docstring:**

```graphql
"""The account this customer belongs to."""
account: Account!
```

- **Audit every docstring.** Search the whole schema for `column`, `synced`, `cron`, `NetSuite`, `table` and any other vendor or system names.
- **Expose a NetSuite reference deliberately if integrators need one.** Give it a public name such as `externalReference` and document it as a supported field. Don't leak it through a comment.

## Other fixes in the SDL you sent

| Current | Problem | Fix |
|---|---|---|
| `created_at: String!` | snake_case, and a timestamp typed as `String` | `createdAt: DateTime!` (custom scalar) |
| `Active: Boolean` | PascalCase, no `is` prefix, accidentally nullable | `isActive: Boolean!` |
| `addresses: [Address]` | nullable list with nullable items | `[Address!]!` at minimum |
| `accountId: ID!` / `ownerId: ID!` | foreign keys | `account: Account!` and `owner: TeamMember`. Make `owner` nullable unless the domain guarantees one. |
| `Customer` has no `Node` | not refetchable by a global ID | `implements Node` on every entity (`interface Node { id: ID! }`) |
| `role: String!` on `TeamMember` | free-text role | An enum with SCREAMING_SNAKE_CASE values |

**Addresses.** Every list a third party can grow must paginate, and a bare list cannot become a connection later without a breaking change. Use a Relay connection (`addresses(first, after): AddressConnection!`) with a documented maximum page size, e.g. 100. You can keep `[Address!]!` only if the count is small, capped and documented as such. Keep the return type a wrapper if you start from a plain cursor list.

**Result:**

```graphql
interface Node { id: ID! }

type Customer implements Node {
  id: ID!
  account: Account!
  owner: TeamMember
  addresses(first: Int = 20, after: String): AddressConnection!
  createdAt: DateTime!
  isActive: Boolean!
}

type Viewer implements Node { id: ID! name: String! email: String! }
type TeamMember implements Node {
  id: ID!
  name: String!
  email: String!
  role: TeamMemberRole!
}
```

**`email` on `TeamMember`.** This is PII shown to partner integrators. Confirm that is intended, or restrict it by role.

## Things the SDL doesn't show: check before shipping

- **Ceilings.** Set and document a depth limit (the skill suggests the low end, about 5–7 levels, for a public API), page-size caps, and caps on aliases and root fields. Reject over-limit queries before execution and publish the exact error.
- **Introspection.** Keep it off for anonymous production callers.
- **Batching.** Check that `account`, `owner` and `addresses` resolve through a per-request batching loader. An un-batched relationship resolver is an N+1 defect and a must-fix finding.
- **Persisted queries.** Allowlist your own first-party apps only. Never allowlist third-party traffic.
- **Federation.** If your internal graph is federated, only the router may be public. Probe each subgraph from outside your private network and expect a connection failure.

## Open questions that could change this

1. Is this a retrofit with real production queries? If so, send the SDL and 5–10 of those queries. Renaming `created_at` or `Active` is a breaking change for any client that already queries them, so you need to map old names forward.
2. Do installers and partners actually need different data shapes from web or mobile clients? The skill's default for a public API is REST. If no GraphQL trigger holds, a REST surface (or a hybrid) is the right call.
3. Does a REST surface coexist? If so, use one shared ID across both, as GitHub's `node_id` does.
4. Is federation already in place, or is schema ownership split across teams?
5. Is this a one-off surface or the platform's primary API for years? That changes how early to adopt result unions on queries and full Relay connections.
6. Which mutation-naming order does your internal graph use today? That is the cheapest way to break the deadlock.

I didn't save anything to memory, since you didn't mention a memory file. Once you confirm the mutation-naming order, ID strategy and error posture, those are the decisions worth recording.