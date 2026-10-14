# Textwire test-mode plan review

I read the `api-test-mode-design` skill and its three references. Of the five plan items, **three should change**, **one should be redesigned**, and **one is a good instinct with the wrong mechanism**.

| # | Plan item | Verdict |
|---|---|---|
| 1 | Errors in a `{"sandbox_error": ...}` format | ❌ Reverse |
| 2 | Rotate magic numbers quarterly | ❌ Reverse |
| 3 | One master list across SMS, voice, and purchasing | ⚠️ Change |
| 4 | Test credentials may send to a teammate's real phone | ❌ Reject, and move the use case to graduation |
| 5 | Carrier rejection hours after submission | ⚠️ Undecided, so here is a concrete design |

## 1. Use the real error shape and flag the mode elsewhere

A magic number must trigger the real published error. The skill lists "magic values that return a sandbox-only error shape" as a design-review failure.

The goal is to let integrators tell simulated errors from real ones. The sandbox-only shape defeats the sandbox's purpose. An integrator's handler for the real `{code, message, ...}` error would never run in test, and the `sandbox_error` branch would never run in production.

**Change:**
- Return the identical error body, HTTP status, and code that production returns for that condition.
- Mark the mode out of band instead. Test keys carry a `_test_` mode substring, every object and response carries `livemode: false`, and a response header such as `X-Textwire-Mode: test` is allowed. None of these alters the error contract.

## 2. Never rotate magic numbers

Treat magic values as API contract: stable, documented, non-expiring. Integrators' CI suites will depend on every entry.
- Additions are free. Changes are breaking.
- Quarterly rotation breaks every integrator's CI four times a year.
- "So nobody hardcodes them" has it backwards. Hardcoding is the intended use.
- The numbers are safe to hardcode because test credentials can only produce simulated outcomes. They never reach a carrier.

If the worry is a magic number colliding with a real number, reserve a block you control (the 555 exchange in the `+1500` area code, as Twilio does) and never assign it to customers.

## 3. Label the catalog per operation

A single flat list for a multi-operation API is the documented integrator trap. Twilio's own catalog shows it. "Can't route" is `...0002` for voice, and the closest SMS equivalent is `...0009`. Cross-reading the wrong table is a known mistake.

Your plan has the same flaw. "+15005550001 means invalid everywhere" hides three different conditions:
- invalid SMS `From`
- invalid voice `To`
- invalid number to purchase

Each has a different field, different handling, and presumably a different real error code. Specifically:
- **Publish one table per operation, keyed by field.** Use the shape `operation × field × number → real error code`. Cover SMS `From`, SMS `To`, voice `From`, voice `To`, and number purchase.
- **Share a number across operations only when it is the same outcome in each.** Mark "not applicable" explicitly where it is not.
- **Cover the full failure catalog, not only "invalid."** Every documented failure needs a trigger. Examples: blocked recipient, unroutable, no international permission, sender not SMS-capable, queue full, unavailable number, and no number available in an area code. One untriggerable failure path fails the audit, because the coverage gate is 100%.
- **Map each value to one entry in your published error catalog.** Don't invent Textwire codes for the sandbox.
- **Make the happy path a value too.** Add a valid `From` and a valid `To`. Add step-up or opt-out behavior if you have any.
- **Restrict test credentials to the magic `From` numbers.** A request with test credentials should not be able to name a real number as `From`, or reference any production resource.

## 4. No real sends from test credentials

This breaks the central guarantee for a communications API. No real message leaves the sandbox, and the strongest design refuses to let test credentials reference production resources at all. Specific problems:
- **It breaks the bidirectional boundary.** Test keys would reject real numbers except a verified exception, which is the hole the boundary exists to close.
- **It is an abuse path.** Test keys are machine-identifiable and routinely leaked. A leaked test key that can reach a real handset can be turned into SMS spam or voice harassment.
- **It makes sandbox behavior diverge.** Delivery, carrier handling, and cost would differ between sandbox and live, and the sandbox would stop being deterministic.

The need is real, though. A green sandbox run is necessary but not sufficient, because no sandbox replicates real carriers. The skill's answer is the **live canary** in the graduation step, not a hole in the sandbox:
- Run one small live send per integration path. Confirm the effect and the event delivery, and reverse it afterwards if possible.
- If integrators need that check before full approval, give them a **pre-approval live tier**. This is my suggestion, not something the skill spells out. It uses live credentials restricted to verified recipient numbers, in the style of a trial account.
- Every other recipient gets an explicit "environment not yet approved" error. Do not return a bare 401.

That gives one true end-to-end check without weakening the sandbox boundary.

## 5. Carrier rejection hours later

This is async state plus time. The skill says to cover it with a magic value, a trigger endpoint, and a clock. Don't make integrators wait hours. Recommended design:

1. **Selector, as a magic `To` number.** Add a number whose message is accepted (HTTP 2xx, status `queued`) and later transitions to `failed`/`undelivered` with a real delivery-failure code from your catalog. Add one number per distinct carrier-rejection code you publish.
2. **Compressed delay by default.** The transition happens within seconds in the sandbox, so CI stays fast.
3. **On-demand trigger.** Add a sandbox-only endpoint: `POST` a message ID plus a target status and error code, and it fires that outcome now. This covers every carrier code without one number each, and it covers cases where the outcome isn't a function of request input.
4. **Optional test clock for "hours later."** If integrators need to test retries or timeouts keyed to elapsed time, attach messages to a clock they advance deliberately. Cap the advance per call and cap what one clock can carry.
5. **Event and poll parity.** The status callback fires with the real payload shape, and `GET message` shows the same state. Document whether a state change and its event delivery are coupled. Otherwise integrators wait for events that never come.
6. **Signing.** Say explicitly whether trigger-fired events carry a valid signature. Your "always verify signatures" rule must not break your own test tooling. Webhook delivery mechanics belong to `webhook-platform-design`.

## What the plan doesn't cover yet

These are required for a complete design:
- **Isolation model.** State the level explicitly. For a communications API, the hard guarantee is that no real message leaves the sandbox. The default is a soft toggle, with mode-prefixed keys routing test traffic to simulation infrastructure. Promote to a structurally separate copy if teams need parallel test data, compliance demands provable isolation, or acting on live data while believing you're in test has real blast radius. A weeks-level budget makes the separate copy a later phase.
- **Keys.** Use a `_test_`/`_live_` mode substring after a type prefix. Enforce the boundary both ways: live keys reject magic numbers, and test keys reject real numbers. A wrong-environment credential must return a legible "wrong environment" error, not an opaque auth failure. Test keys still deserve real secret hygiene. Key lifecycle belongs to `api-auth-key-management`.
- **Simulated objects for the other operations.** Voice needs simulated call lifecycle states and status callbacks. Number purchasing needs simulated purchased numbers that can be released and reset.
- **Reset and seeding.** Give integrators endpoints to mint test objects and to reset to a clean state. Use synthetic data only. Run periodic cleanup of shared sandboxes.
- **Parity.** Derive sandbox config from the same infrastructure-as-code as production. Differences should be intentional and documented.
- **Quotas.** Reuse production rate limits in test by default, which also keeps integrators' throttling code honest. Add a sandbox volume cap only if evaluation-volume abuse shows up.
- **Graduation.** Pick a gate that matches your real obligation, such as sender or number registration or plan tier. Don't import KYC-level weight without a reason. Publish the cutover checklist:
  1. Compliance step submitted and approved before launch day.
  2. Credentials swapped everywhere, and test credentials removed from production config.
  3. Fresh live webhook endpoints and signing secrets.
  4. One live canary per integration path (SMS, voice, purchase), confirming effect and event delivery.
  5. Abuse and rate rules on before the first live send.
- **Publish the five cutover pitfalls** to integrators: forgotten key swap, cross-environment paste, assuming sandbox predicts live, stale live webhook endpoints, and untested real-carrier failure paths.
- **Measurement gates.**
  - 100% of documented failure outcomes are triggerable.
  - Every async event type can be fired on demand.
  - Every time-dependent flow can be tested with simulated time.
  - Cross-environment auth tickets trend to zero.
  - The cutover checklist, including one live canary, is walked before any integration counts as launched.

## Questions I'd normally ask first

I didn't have your answers, so I assumed a communications-like product. These would change the details, mainly steps 1, 5, and 7 of the skill:
1. Is a mode toggle acceptable, or do you need a structurally separate environment? What is the budget, in weeks or quarters?
2. What gates going live: sender or number registration, plan tier, partner vetting, or nothing?
3. What test infrastructure already exists, such as staging or a mock server that integrators currently depend on? A retrofit has to start from that.
4. Is there a hard date, such as one partner waiting, or is this a surface you'll run for years?
5. Is there an end-user-facing surface, such as a hosted opt-in page, that integrators also need to test?

## Recommended order

1. Replace `sandbox_error` with the real error shape and mode flags.
2. Drop rotation, and publish the per-operation catalog as a stable contract.
3. Remove real-phone sends from test credentials.
4. Add the live canary and pre-approval tier to the graduation path.
5. Build carrier-rejection simulation with magic numbers, then the trigger endpoint, then the clock.