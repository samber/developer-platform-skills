**No, `extensions.code` alone isn't enough.** It fixes the regex problem, but it leaves three of your five failures in the wrong channel. It also hides a retrofit hazard that applies to the real fix.

I followed `public-graphql-api-design`, mainly steps 2, 4 and 8. I did not re-run the other steps (REST-or-GraphQL gate, depth limits, federation, persisted queries). None of them changes this answer.

## Verdict

- **Codes fix machine-readability.** Integrators can switch on a stable value instead of parsing text.
- **Codes don't fix the channel.** Card declined, region ineligible and refund already issued are expected business outcomes. The skill's anti-pattern is "expected business outcomes reported only through the top-level `errors` array on a third-party surface". With only `extensions.code`, nothing in the schema tells an integrator that `subscriptionCreate` can decline, so they can't discover it from introspection or codegen. Codes also can't carry typed data such as `retryable` or the existing refund.
- **Expired token and DB timeout do belong in top-level `errors`.** They are things the caller can't plan around. Your lead is right about those two, and only those two.

## Where each failure goes

| Failure | Channel | Shape |
|---|---|---|
| Card declined | Result type | `PaymentDeclined` |
| Plan not eligible in region | Result type | `PlanNotAvailableInRegion` |
| Refund already issued | Result type | `RefundAlreadyIssued` |
| Expired token | Top-level `errors` | `extensions.code = TOKEN_EXPIRED` |
| Postgres statement timeout | Top-level `errors` | `extensions.code = TEMPORARILY_UNAVAILABLE` |

## Proposed SDL

This follows your noun-first naming (`subscriptionCreate`, `refundIssue`). Enforce that order schema-wide.

```graphql
enum ErrorCode {
  VALIDATION_FAILED
  PAYMENT_DECLINED
  PLAN_NOT_AVAILABLE_IN_REGION
  REFUND_ALREADY_ISSUED
  UNAUTHENTICATED
  TOKEN_EXPIRED
  TEMPORARILY_UNAVAILABLE
  INTERNAL_ERROR
}

interface Error {
  message: String!   # free text, may change, never a contract
  code: ErrorCode!   # stable contract
}

type Mutation {
  # Nullable on purpose, see "Design notes".
  subscriptionCreate(input: SubscriptionCreateInput!): SubscriptionCreateResult
  refundIssue(input: RefundIssueInput!): RefundIssueResult
}

input SubscriptionCreateInput {
  idempotencyKey: String!
  # customer, plan, payment method...
}

union SubscriptionCreateResult =
  | SubscriptionCreateSuccess
  | PaymentDeclined
  | PlanNotAvailableInRegion
  | ValidationError

type SubscriptionCreateSuccess { subscription: Subscription! }

type PaymentDeclined implements Error {
  message: String!
  code: ErrorCode!
  reason: PaymentDeclineReason!   # coarse enum
  retryable: Boolean!
}

enum PaymentDeclineReason {
  INSUFFICIENT_FUNDS
  CARD_EXPIRED
  AUTHENTICATION_REQUIRED
  DECLINED_GENERIC            # catch-all for sensitive issuer codes
}

type PlanNotAvailableInRegion implements Error {
  message: String!
  code: ErrorCode!
  plan: Plan!                  # object reference, not planId
  region: String!
}

input RefundIssueInput {
  idempotencyKey: String!
  chargeId: ID!
}

union RefundIssueResult =
  | RefundIssueSuccess
  | RefundAlreadyIssued
  | ValidationError

type RefundIssueSuccess { refund: Refund! }

type RefundAlreadyIssued implements Error {
  message: String!
  code: ErrorCode!
  refund: Refund!              # the existing refund
}

type ValidationError implements Error {
  message: String!
  code: ErrorCode!
  field: String
}
```

Top-level errors for the other two:

```json
{ "data": null, "errors": [{
  "message": "Access token expired",
  "extensions": { "code": "TOKEN_EXPIRED" } }] }

{ "data": null, "errors": [{
  "message": "Temporarily unavailable, retry",
  "extensions": { "code": "TEMPORARILY_UNAVAILABLE", "retryable": true, "requestId": "req_..." } }] }
```

Keep `TOKEN_EXPIRED` separate from `UNAUTHENTICATED`, because clients refresh the token in one case and force a re-login in the other. Send the matching HTTP 401 where your transport allows it.

## Design notes

1. **Nullable mutation returns.** Mutations in one document run serially. A non-null return that hits a top-level error nulls the whole `data`. The client then loses the result of an earlier mutation that already succeeded. The skill makes mutation payloads lean nullable for this reason (Shopify's Rule #24).
2. **Timeout on a money mutation is ambiguous.** The charge may or may not have happened. That is why `idempotencyKey` is in both inputs. A retry after `TEMPORARILY_UNAVAILABLE` is then safe. A replay with the same key should return the original success, not `RefundAlreadyIssued`.
3. **Never leak the database.** The timeout message stays generic: no SQLSTATE, no query text, no table names. Give the caller a `requestId` and keep the detail in your logs.
4. **Don't create an existence oracle.** Return `RefundAlreadyIssued` only to callers allowed to see that charge. For an unknown charge and a charge belonging to someone else, behave identically.
5. **Don't pass raw issuer decline codes through.** Map them to the coarse `PaymentDeclineReason` enum. Detailed fraud-flavoured reasons stay in `DECLINED_GENERIC`.
6. **Message text is not a contract.** Say so in the docs, and publish the `ErrorCode` list with its stability guarantee. The regex integrator should migrate to `code` and `__typename`.

## The retrofit hazard

Moving declines from "thrown" to "returned as data" is a behavior change.

- **Silent failure.** An old client that only checks `errors` will see a declined card as a success response with no error. For billing, this is the worst kind of break.
- **Breaking return types.** Changing a shipped field's return type to a union is a schema-breaking change. The skill says so directly.

The safe route:

1. **Ship now (non-breaking):**
   - Add `extensions.code` to every top-level error from the `ErrorCode` enum.
   - Publish the code list.
   - Announce that `message` is unstable.
   - This is your lead's plan, and it is step 1 of this one.
2. **Introduce the result types opt-in**, so old clients keep getting thrown errors until they migrate. Pick one:
   - **Date-versioned schema**, as Shopify does. This is my lean if you have any version header today.
   - **Additive field** on the existing payload type, if the mutations already return an object payload.
   - **New mutation names**, as a last resort.
3. **Deprecate the throwing path** with `@deprecated`, a dated notice, and per-integrator usage telemetry. Contact the regex integrator directly.
4. **Roll out to the remaining mutations.** The error-surface gate requires 100% of mutations to carry business failures in their return type. These two are the start, not the finish.

I'd hand the deprecation and notice-period policy to `api-versioning-policy`, and the full code taxonomy to `api-error-design`.

## Gates for these two mutations

- Every expected business failure is a member of the result union. None of them is thrown.
- A contract test per outcome asserts `__typename` and `code`, never `message`.
- A test that reaches a real statement timeout returns `TEMPORARILY_UNAVAILABLE` with no SQL in the body.
- An unauthorized or unknown `chargeId` returns the same response shape in both cases.
- Changing message wording breaks no test. That would have caught last week's typo fix.

## Questions I need answered

These decide the retrofit path in step 2. I assumed noun-first naming from your mutation names.

1. What do `subscriptionCreate` and `refundIssue` return today: the entity itself, or a payload object? Please share the current SDL and 5–10 real production queries.
2. Do you have any version header or date-versioning today? Is the endpoint third-party only, or do your own apps share it?
3. Which fields and messages do integrators already depend on, beyond the one regex user?
4. Is the API a multi-year primary surface? If yes, go with result types early, as above.
5. Does a REST surface coexist, and should it share `Charge` and `Refund` IDs with the graph?