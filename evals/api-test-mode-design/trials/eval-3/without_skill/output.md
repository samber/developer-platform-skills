# Design review: Renewly sandbox time, webhook button, dunning shortcut

## Verdict

⚠️ **Don't ship as designed.** The three pieces share one root problem. Each is a point fix for "developers can't see billing events fast enough." The plan leaves out the one mechanism that solves all three: **controllable time plus scripted payment outcomes, exposed via API**.

The plan has four gaps:

- It doesn't cover the annual renewal or the 7-day dunning window.
- It isn't deterministic.
- The webhook button conflicts with your own signature docs.
- The dunning shortcut risks teaching integrators states that can't occur in production.

## 1. Compressed time (10-minute trials, 15-minute renewal jobs)

### 🔴 It doesn't cover the cases you listed

- **Dunning (3 retries over 7 days) and annual renewal** both fall under "contact support." That covers two of your four scenarios, and they are the ones most likely to break an integrator. Dunning has the most branching: past_due, retry succeeds, retries exhausted, cancellation.
- **Monthly renewal isn't compressed at all.** A 15-minute job only helps if the billing period is also shortened. Otherwise a subscription created today isn't due for 30 days. If you do shorten the period, you have added a second compression rule that the plan doesn't define.

### 🔴 It's non-deterministic

- A 10-minute trial is detected by a job that runs every 15 minutes. The trial expires 10 to 25 minutes after creation, depending on job phase.
- Developers can't write assertions or CI tests against "somewhere in the next 25 minutes."
- A developer who sleeps 11 minutes and sees nothing will file a bug.

### 🟠 Sandbox and production behave differently

- Integrators hardcode or derive date logic. Examples are showing "trial ends on X," computing days left, and grace-period math. A 10-minute trial exercises none of it.
- Month-end, leap-year, DST, and timezone edge cases only appear with real calendar math.
- Many customers hitting the `:00/:15` job boundary together produces bursty webhooks and ordering races. Production doesn't look like that.
- It's unclear what `trial_will_end` (usually sent days before expiry) does in a 10-minute trial. It probably fires immediately or never.
- Docs say 14 days and the sandbox says 10 minutes. Every example needs an asterisk.

### 🔴 "Contact support to fast-forward" doesn't scale

- It's manual, slow, and unusable in CI.
- It adds support load and creates an audit and authorization question: who may change the time of whose account?

### ✅ Recommendation: test clocks

Attach each sandbox customer to a **test clock**. A clock is an API object holding simulated "now."

```
POST /v1/test_clocks                  {"frozen_time": "2026-10-03T09:00:00Z"}
POST /v1/customers                    {"test_clock": "clk_123", ...}
POST /v1/test_clocks/clk_123/advance  {"frozen_time": "2026-10-17T09:00:01Z"}   # trial ends
GET  /v1/test_clocks/clk_123          -> {"status": "advancing" | "ready"}
```

- It runs the real state machine and real code paths. Trial expiry, monthly, annual, and every dunning retry happen in order, with real calendar math.
- Advancing a year is one call.
- Developers can see the dunning retry schedule, for example day 1, 3, and 7, instead of guessing.
- Advance is asynchronous. It reports `advancing`/`ready` and emits an event when done.
- Guardrails:
  - Cap the advance distance per call, for example two billing periods. Otherwise a 10-year advance on a monthly plan emits 120 renewals.
  - Cap clocks per account.
  - Auto-delete old clocks.
  - Allow clocks in sandbox only.
- The 10-minute trial and 15-minute job then become unnecessary. Keep them only as an optional "real-time demo mode," not as the primary mechanism.
- **Keep "contact support" out of the docs.** It reads as a feature gap.

## 2. "Fire webhook" button with a sample `subscription.renewed`

The feature is useful. As specified, it conflicts with your docs and creates a risk.

### 🔴 Signature handling must be exactly right

- **Sign with the endpoint's real sandbox secret.** Your docs say to always verify.
  - An unsigned or differently signed sample trains developers to disable verification "for testing."
  - That habit then ships to production.
- **Sign with a fresh timestamp from wall-clock time at delivery, not simulated clock time.**
  - Test clocks and sample payloads carry simulated or example times.
  - If the signature timestamp follows them, replay-tolerance checks (typically about 5 minutes) fail for correct integrations.
  - Document this explicitly.
- **Give every click a new unique event ID.** Otherwise a handler's idempotency or dedupe check silently drops the second click and the developer thinks the handler is broken.

### 🔴 Forged-event risk

A valid-signed `subscription.renewed` with example data is exactly what an entitlement-extending handler acts on.

- The button must be **sandbox-only**, with a separate signing secret from live. It must be impossible to target a live-mode endpoint.
- Mark payloads with `livemode: false` and a clear marker such as `"sample": true`.
- Use IDs that can't collide with real objects (reserved prefix, for example `sub_sample_…`).
- Use obviously fake PII.

### 🟠 Sample payloads drift and mislead

- A hand-written example goes stale against the real schema.
  - Generate samples from the **same serializer and schema version** as real events.
  - Keep sample and real events the same shape. Separate handler paths for "sample" would defeat the purpose.
- Example IDs don't exist in the integrator's database or in the API.
  - A handler that does `GET /subscriptions/{id}` after receiving the event will 404.
  - A sample that doesn't survive the standard "fetch then act" pattern teaches little.
  - Best fix: let the button fire against a **real sandbox subscription**, chosen from a dropdown. Fall back to a synthetic one only when none exists.

### 🟠 Scope is too narrow

`subscription.renewed` is the happy path. The events integrators get wrong are `invoice.payment_failed`, the retry-exhausted and cancellation events, `trial_will_end`, and refunds.

- Add an event-type dropdown.
- Add **resend** for past real events.
- Add a delivery log showing request, response code, latency, and retries.
- Add a CLI or tunnel to forward events to localhost, so developers aren't forced onto a public URL.

## 3. Reaching the dunning state without the clickthrough

Creating a customer, a subscription, and three failed payments by hand is the right thing to complain about. Two details need fixing.

### ℹ️ Count the failures correctly

"3 retries" means **4 failed charges**: the initial attempt plus 3 retries. Make sure the docs and any scenario are unambiguous.

### ✅ Recommendation: scripted payment outcomes plus scenarios

1. **Test payment methods with scripted behavior** (magic tokens or a `behavior` field):
   - `always_decline`
   - `decline_n_times_then_succeed` (for example 2, to test recovery on retry 3)
   - `decline_insufficient_funds`, `decline_expired`, and similar decline reasons
   - `requires_authentication`

   These let developers test the success-after-retry path as well as the failure path.

2. **A scenario endpoint** that seeds a state in one call:

   ```
   POST /v1/sandbox/scenarios  {"name": "dunning", "stage": "retry_2_of_3"}
   ```

   It returns the customer, subscription, and test clock, ready to advance.

### 🔴 Seed by driving the real state machine, not by writing rows

- A scenario must create the real objects, attach a failing test payment method, and advance a test clock. It must not write a `past_due` record directly.
- Direct writes can produce states production can never reach.
  - Integrators then build and test against impossible states.
  - Real transitions (events, invoice records, retry timestamps) never fire, so their handlers never run.
- Every intermediate event (`invoice.payment_failed` ×N, state changes) must be emitted, as in production.

## 4. Smaller items

- Document the exact dunning schedule (retry days, final state after exhaustion, emails sent).
- Make `trial_end`, `current_period_end`, and `next_payment_attempt` the source of truth. Don't encourage hardcoded durations.
- Show the clock and the `livemode` flag prominently in the dashboard so nobody confuses sandbox with live.
- Offer an optional real-time mode only if there is demand. Don't make it the default.

## 5. Proposed shape, in priority order

1. **Test clocks**: the API, advance, and event emission. This replaces compressed time and the support-driven fast-forward.
2. **Scripted test payment methods**: decline-then-succeed and similar.
3. **Scenario seeding** built on 1 and 2, including a one-call dunning state.
4. **Webhook button** (sandbox-only, real secret, fresh wall-clock timestamp, unique IDs, real objects, event-type dropdown, resend, delivery log).
5. Docs covering the retry schedule, signature timestamps under test clocks, and a recommended CI pattern: create a clock, advance it, and assert on events.

## Open questions

- Is the current renewal engine event-driven or poll-based? Test clocks are easier to build if "now" is injectable.
- Should the sandbox have one global clock or per-customer clocks? Per-customer is much more useful for parallel tests.
- What is the exact dunning schedule, and what state follows exhaustion (canceled or unpaid)?
- Are signing secrets already separate between live and sandbox?