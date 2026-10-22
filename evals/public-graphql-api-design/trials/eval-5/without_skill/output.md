# Is `extensions.code` on every error enough?

**No.** It's the right first step and fixes the regex complaint, but it leaves four problems open.

## What it fixes

- Integrators can branch on a stable string, not on message text.
- The typo-fix breakage goes away, as long as messages are formally declared non-contract.

## What it leaves open

**1. Expected outcomes still travel on the failure channel.**
Card declined, plan not available in region, and refund already issued are normal business results, not faults. In GraphQL, a top-level `errors` entry also means `data` is often null and generic clients, APM and alerting treat it as an error. You'd page on declines.

The unexpected failures (expired token, statement timeout) belong in top-level `errors`. The business outcomes belong in the payload, as typed data the schema documents.

**2. The code alone doesn't carry what the integrator needs to act.**
Each case needs structured fields:
- Decline: a decline category (`insufficient_funds`, `expired_card`, `authentication_required`) and whether the customer can retry with another card.
- Region: the customer's region, and which plans are eligible.
- Duplicate refund: the existing refund's ID, so the integrator can treat it as done.
- Every error: `retryable`, optional `retryAfter`, and a `requestId` for support.

**3. Timeouts leave the outcome unknown, and retrying can double-charge.**
A statement timeout on `subscriptionCreate` or `refundIssue` doesn't tell you whether the write committed. Once you label it retryable, integrators will retry. Without an idempotency key on both mutations, you'll create duplicate subscriptions and duplicate refunds.

With one, "refund already issued" splits into two cases:
- Same key replayed: return the original result as success.
- Different key against an already-refunded charge: return a real business error.

**4. Raw database errors must not leak.**
Map Postgres timeouts to a generic `SERVICE_UNAVAILABLE` with `retryable: true` and a `requestId`. Never expose the internal message.

## Recommended design

| Case | Channel | Code | Retryable | HTTP / transport |
|---|---|---|---|---|
| Card declined | Payload error (typed) | `CARD_DECLINED` + `declineCategory` | After changing card | 200 |
| Plan not eligible for region | Payload error | `PLAN_NOT_AVAILABLE_IN_REGION` + `region` | No | 200 |
| Refund already issued | Payload error, or success on idempotent replay | `REFUND_ALREADY_ISSUED` + `existingRefundId` | No | 200 |
| Expired token | Top-level error | `UNAUTHENTICATED` (`TOKEN_EXPIRED` as detail) | After refresh | 401 |
| Statement timeout | Top-level error | `SERVICE_UNAVAILABLE` | Yes, with the idempotency key | 503 |

The payload errors can be a union or a nullable `errors` list on the payload, with a `code` enum, the typed fields above, and a human `message`.

## Schema compatibility

Changing a mutation's return type, or adding union members that exhaustive clients don't handle, breaks clients. The safe route is additive:
- Add a nullable `errors: [SubscriptionCreateError!]` field to the existing payloads, as Shopify does with `userErrors`.
- Keep throwing the old way, with `extensions.code` added, until a deprecation date.
- Then stop throwing for business outcomes.

## Rollout

1. **Now:** add `extensions.code`, `requestId` and `retryable` to every top-level error. Default to `INTERNAL` when a throw site has no code, and add a test that fails on uncoded throws.
2. **Next:** add idempotency keys to both mutations.
3. **Then:** add the typed payload errors and document the code enum as an additive-only contract. Never rename or remove a code. Treat a new code as a minor change, and tell integrators to handle unknown codes with a default branch.
4. **Regex integrator:** contact them directly with the code list and a migration date. Publish "messages are not a contract" in the docs, and add snapshot tests on codes, not text.

## What to tell your lead

`extensions.code` is necessary but covers about a third of the problem. Without the payload-versus-throw split, the structured fields, and idempotency, integrators can tell the failures apart but still can't safely react to them, and the timeout case becomes a duplicate-charge risk.