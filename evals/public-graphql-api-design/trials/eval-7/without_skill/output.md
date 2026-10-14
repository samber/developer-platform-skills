## Verdict

1. **Don't merge into `User`.** Keep `Viewer`, `TeamMember` and the customer's person data as separate types.
2. **Pick `updateCustomer`.** Time-box the decision, then spend the effort on the input and payload types.
3. **Rewrite the `accountId` docstring.** The current one leaks internals into a public schema.

## 1. `User` collapse: no

The duplication is of syntax, not of knowledge. Three types with `name` and `email` is not a DRY violation. DRY applies when two places must change together. These won't.

- **Different people, different trust.** `Viewer` is the caller, so their own email is fine to show them. `TeamMember` is a colleague on the account. A customer is an external person who never logs in. A merged `User` forces one exposure decision onto all three.
- **Different lifecycles.** Customers have addresses and an account. Team members have a role. Viewers may be partner integrators with no role at all. A merged type needs nullable fields (`role: String`, `email: String`) that mean "not applicable" in one case and "hidden from you" in another. Clients can't tell which.
- **Public schema is append-only.** You can't remove a field from a published type without a breaking change. Merging couples the three evolution paths forever, and splitting later is far costlier than merging later.
- **Fine-grained PII control.** Partners and installers will get different scopes. Per-type field visibility is much easier to reason about than per-role masking on one type.

If the architect still wants sharing, use `interface Person { id: ID! name: String! }`. It is additive and lets clients write one fragment. Leave `email` off the interface, since email exposure is exactly the per-type decision above.

Related fix: `Customer.ownerId: ID!` should be `owner: TeamMember`. Raw foreign keys in a public graph force clients into N+1 lookups.

## 2. `updateCustomer` vs `customerUpdate`

Both are fine, and neither is wrong. GitHub uses verb-first (`updateIssue`). Shopify uses noun-first (`customerUpdate`), which groups related mutations alphabetically in docs.

**Recommend `updateCustomer`.** It reads as English, and the sorting benefit only matters if your docs list mutations alphabetically. Keep noun-first only if the internal graph already uses it everywhere. Whichever you choose, enforce it with a schema lint rule so the debate doesn't return.

The mutation has bigger problems than its name:

- **Input type.** `CustomerInput` is shared between create and update, so required fields collide with partial-update semantics. Use `UpdateCustomerInput` with `id: ID!` and every other field optional. Define what omitted vs `null` means.
- **Return type.** A nullable `Customer` hides why a call failed. Return `UpdateCustomerPayload { customer: Customer, userErrors: [UserError!]! }`. Adding a field to a payload later is non-breaking, but changing a bare return type is not.

## 3. `Customer.accountId` docstring

> "mirrors the account_id column synced nightly from NetSuite"

This publishes three internal details:

- a database column name,
- the vendor (NetSuite),
- the sync mechanism and cadence.

Introspection exposes it to every partner and installer. It also invites integrators to depend on NetSuite behavior and timing, which you'd then have to preserve.

**Replace with:**

```graphql
"""
The ID of the account this customer belongs to.
"""
accountId: ID!
```

- Add a freshness note only if you're willing to make it a contract, for example "Account reassignment can take up to 24 hours to appear." Don't name the system.
- Check whether this ID is the raw NetSuite internal ID. If so, it leaks the ERP identifier and ties your API to that system. Expose an opaque Sablefield ID instead, ideally as `account: Account`.
- Audit every other description in the schema for the same leaks (table names, vendors, job names, internal team names). Do it before publishing, because introspection makes them permanent.

## Other fixes in the snippet

```graphql
"""A person or business that Sablefield's customers serve."""
type Customer implements Node {
  id: ID!
  account: Account!
  owner: TeamMember
  addresses: [Address!]!   # or a connection if the list is unbounded
  createdAt: DateTime!
  isActive: Boolean!
}
```

- **Naming.** `created_at` becomes `createdAt` and `Active` becomes `isActive`. Public GraphQL is camelCase, and `Active` is the odd one out.
- **Scalars.** Use a `DateTime` scalar, not `String`, for timestamps.
- **Nullability.** `[Address]` is a nullable list of nullable items, which is almost never intended. `Boolean` for a flag should be `Boolean!`. Output fields that can fail on permissions can stay nullable. Loosening later breaks clients, and tightening doesn't.
- **IDs.** Make IDs opaque and global, and implement `Node`.
- **Descriptions.** Add a description on every type, field and argument. For a partner API they are the docs.
- **Authorization.** Decide per-field auth before launch. Customer addresses are PII, and each installer must only see their own customers.

Do you want me to draft the full public SDL with descriptions, the `UpdateCustomerInput` and payload types, and a lint config that enforces the naming convention?