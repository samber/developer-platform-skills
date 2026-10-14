# Verdict: Prism is fine as a stopgap, but it is not the sandbox

❌ Don't ship it as "Sandbox". ✅ Ship it this week as a **Mock API** with an honest label, and build the real sandbox as a soft test-mode toggle over the next few weeks.

The Prism mock fails the one thing your integrators need. It is stateless, so it can't test the order lifecycle, cancellations mid-flow, or the shipped and delivered webhooks.

## Assumptions

I couldn't ask the skill's seven clarifying questions, so I assumed the answers below. Correct any that are wrong, because several change the design.

| # | Question | Assumed answer |
|---|---|---|
| 1 | Domain | Order and fulfillment. No money moves. The hard guarantee is that no real warehouse, carrier, or retailer system is ever touched from test. This is closest to the communications-like case. |
| 2 | Isolation appetite and budget | A toggle on the live account is acceptable. Budget is weeks, not quarters. |
| 3 | Graduation gate | Unknown. I assumed account approval or plan tier. |
| 4 | Existing test infrastructure | None. The mock would be the first thing integrators depend on. |
| 5 | Time and async | Yes. Allocation, transit, and delivery take time, and webhooks are asynchronous. |
| 6 | End-user surface | None. The API is the whole product. |
| 7 | Deadline and lifespan | "This week" is a preference, not a hard external date. The sandbox is a compounding surface you will run for years. |

## Why the Prism proposal fails

It does give you spec-valid responses on every endpoint, and that is real, cheap value. Against the lifecycle your integrators care about, it fails in four ways.

1. **No state.** After `POST /orders`, a `GET` returns the spec example, not the order just created. `allocate` on a made-up ID "succeeds". `cancel` after `shipped` succeeds, because the mock has no concept of "after". The state-machine rules (which transitions are legal, which return a conflict error) are exactly what integrators need to validate. The skill calls this the week-three gap: bugs a stateless mock cannot reproduce because it doesn't know what happened on a prior call.
2. **No `shipped` or `delivered` webhooks.** A spec describes webhook payload shapes, not the moment the state changed. Even if Prism could fire a callback, nothing ties the event to an order that actually reached `shipped`. Your integrators' listener code would go untested.
3. **Failure paths aren't triggerable.** Prism can return a documented error through a `Prefer: code=` header. That tests the integrator's error handler against a spec example. It does not test your business rule. Nothing makes "out of stock at allocation" or "cancel rejected after shipment" happen for a real reason.
4. **No time.** Allocation delay, transit, and delivery either don't exist or require waiting.

There is also a labeling problem. The word "Sandbox" with no stated isolation level promises a stateful environment. Integrators will build CI against it, find it doesn't behave like production, and file tickets. The skill lists "a mock server shipped as the sandbox" as a named failure mode. It also drifts silently: when the real API's behavior changes, the mock keeps simulating the old behavior while production breaks.

## What to ship this week

1. Deploy Prism, but on a **different host** from the one you'll later use for the real sandbox, for example `mock.hookline.dev`. Magic values and hostnames become contract once integrators put them in CI, so keep `sandbox.hookline.dev` free for the real thing.
2. Label the docs page **"Mock API (stateless)"** and state the isolation level explicitly. Suggested wording:
   > Returns spec-shaped responses only. No state is kept between calls. No webhooks are sent. Not suitable for testing order lifecycle, cancellations, or event handling. A stateful test mode is coming; this page will link to it.
3. Don't promise a date for the real sandbox unless the work is scheduled.

## The real design: soft test mode

This follows the skill's workflow, in order.

### 1. Isolation: soft toggle

- **Model:** one account, a `livemode` boolean on every object, and mode-prefixed keys. `hl_test_…` keys route to a **fulfillment simulator** that never calls a real warehouse, carrier, or retailer system. `hl_live_…` keys go to the live path.
- **Why not a hard separate-copy?**
  - Weeks of budget deletes it from this pass.
  - **Unblock condition:** the first cross-mode leakage incident, or a compliance regime that demands demonstrable isolation.
  - Promote it earlier if integrator teams need parallel testing without sharing data.
- **State the isolation level in the docs.** Suggested wording:
  > Test mode shares your account and configuration with live mode. Test objects are invisible to live calls and vice versa. Test keys can read and write your account's webhook endpoints.
- **Hostname:** `sandbox.hookline.dev` can stay as an alias, but the **key** decides the mode. A test key on the live host, or a live key on the sandbox host, returns a clear `wrong_environment` error. It must not return an opaque 401.
- **Parity:** the simulator runs the same state-machine and validation code as production, with only the outbound fulfillment calls swapped for simulated ones. It is not generated from the spec.

### 2. Make every failure path triggerable

**Default: magic values, labeled per operation.** Your integrators already type SKUs, postal codes, and references, so use those as the carrier. Each value must trigger a **real** error code from your published catalog, never a sandbox-only error shape. The codes below are illustrative; I haven't seen your catalog.

| Operation | Magic input | Outcome |
|---|---|---|
| `create` | SKU `TEST-OK` | Happy path |
| `create` | Ship-to postal code `00000` | Address rejected, using your real address-validation error |
| `allocate` | SKU `TEST-OOS` | Insufficient stock at allocation |
| `allocate` | SKU `TEST-SPLIT` | Partial allocation across two warehouses (tests multi-shipment handling) |
| `allocate` | SKU `TEST-BACKORDER` | Backordered, allocation deferred |
| `ship` | Reference `TEST-CARRIER-DELAY` | Carrier exception, then recovery |
| `deliver` | Reference `TEST-DELIVERY-FAIL` | Delivery attempt fails, order returned |
| `cancel` | Any order, in `created` or `allocated` state | Succeeds |
| `cancel` | Any order, after `shipped` | Rejected with your real "not cancellable" error |

Rules:
- Publish the catalog as a stable contract. Additions are free, but changes break integrators' CI.
- Label every value by operation. The same input must not mean different things across calls.

**Step up to simulation endpoints for what no input can encode.** Cancellation mid-flow is the clearest case, because the interesting bit is the timing, not the request body.
- `POST /v1/test/orders` mints an order directly in a target state (`allocated`, `shipped`, and so on).
- `POST /v1/test/orders/{id}/advance` moves it to the next lifecycle state.
- Together these let an integrator test "cancel arrives while the order is shipping" deterministically.

**Deferred: the config-driven fixture builder.** It is high effort and starved for now.
- **Unblock condition:** integrators' data shapes (multi-warehouse, bundles, partial shipments) vary enough that magic values can't express them.
- Ship a starter-fixture library with it, not just the endpoint.

### 3. Events and time

- **Test-event triggering:** `POST /v1/test/orders/{id}/events` with `{"type": "order.shipped"}` and the same for `order.delivered`. Cover every event type you publish, not only these two.
- **Document the decoupling.** If `advance` changes state and the event is delivered separately, or with a delay, say so. Otherwise integrators wait for events that never come.
- **Signatures:** test events must carry a valid signature for the test endpoint's own secret. Delivery, retry, and log mechanics belong to `webhook-platform-design`.
- **Time:**
  - By default, simulated transit and delivery compress to seconds.
  - Offer an optional manual **test clock** that integrators advance deliberately, with state transitions and events firing as if the time had passed.
  - Cap the advance per call and the complexity one clock can carry.
  - Nothing should require waiting real calendar time.
- **Reset and seeding:**
  - `POST /v1/test/reset` returns the account's test data to clean.
  - Seed with synthetic data only, never copied production orders.
  - Run periodic cleanup on shared test data.

### 4. Credentials, quotas, abuse

- **Prefix:** use `hl_test_` and `hl_live_`, modeled on the externally recognized `_test_`/`_live_` shape. Enforce it both ways: live keys reject test values, and test keys reject real ones. Key lifecycle belongs to `api-auth-key-management`.
- **Test keys are not risk-free.** On a toggle model they still touch real account configuration, such as webhook endpoints, so they need real secret hygiene.
- **Quotas:** reuse your production limits in test mode. That also keeps integrators' throttling code honest. Build a dedicated sandbox cap only if evaluation-volume abuse appears, such as load tests against shared infrastructure. Model it as an aggregate volume cap, not a faster per-minute limiter.
- **Carding abuse doesn't apply.** There is no payment instrument in this API, so don't import that mitigation.

### 5. Graduation to live

Your gate is unknown (assumption 3). Match it to your actual obligation: account approval, plan tier, or retailer vetting. Don't import KYC-weight process you don't need.

- **Legible pre-approval error:** an unapproved account calling live gets an explicit `environment_not_approved`, not a bare 401.
- **Cutover checklist to publish:**
  1. Approval submitted and granted **before** launch day.
  2. Live keys swapped in every deployed environment, test keys removed.
  3. **Fresh live webhook endpoints, subscriptions, and signing secrets.** Test-mode secrets don't carry over.
  4. One canary order per integration path, confirming both the effect and the `shipped`/`delivered` event delivery.
  5. Abuse and rate rules on before the first live order.
- **Open question on the canary:** an order API's real "effect" moves physical goods. Decide whether canaries use a flagged low-value SKU, a warehouse "hold" setting, or cancel-before-ship. Cancel-before-ship won't exercise the `shipped` event, so it can't cover the full path.
- **Five pitfalls to document:** forgotten key swap, cross-environment paste, assuming sandbox success predicts live, stale live webhook endpoints, and under-tested real-world failures. In your domain the last one means real carrier delays, split shipments, and delivery exceptions that the simulator only approximates.

## Rough sequence

| When | Deliverable |
|---|---|
| Week 1 | Prism mock on `mock.hookline.dev`, labeled "Mock API (stateless)" with the isolation statement. |
| Weeks 2-4 | Soft toggle with the state machine and the `livemode` flag. Magic values, `advance`, event triggering, and reset. Key prefixes and `wrong_environment` error. |
| After that | Test clock. Graduation docs and checklist. Fixture builder and hard separate-copy stay deferred until their unblock conditions hit. |

I haven't estimated effort inside the 2-4 week window. It depends on how much of your lifecycle state machine and webhook infrastructure already exists as reusable code.

## Measurement

- **Failure-path coverage (gate: 100%):** every documented failure outcome is triggerable on demand.
  - Today's Prism proposal covers none of the business-rule failures, only spec-example responses.
- **Event and time coverage (gate: 100%):** every event type is fireable, and every time-dependent flow is testable without waiting.
  - Today's Prism proposal: 0 events fireable, no time simulation.
- **Cross-environment incidents:** target zero, achieved by self-describing prefixes and a legible error, not by warning integrators.
- **Graduation exercise:** walk the checklist end to end, including one live canary with confirmed event delivery, before calling any integration launched.

## Decisions I need from you

1. Is a toggle on the live account acceptable, and is the budget really weeks (assumptions 2 and 7)?
2. What gates going live, if anything (assumption 3)?
3. What is your canary approach for an API whose live effect moves physical goods?
4. Can you share your published error-code catalog, so I can map each magic value onto the real code?