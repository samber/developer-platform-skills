**Verdict: don't ship as written.** Three of your four required scenarios (monthly renewal, dunning, annual renewal) have no self-serve path. The webhook button also breaks your own "always verify signatures" rule.

Next action: replace the 10-minute and 15-minute compression with a test clock (finding 1).

**Assumptions.** The skill asks clarifying questions first. I couldn't ask, so I assumed the answers below. Tell me which are wrong.
1. Domain is payments-like: money moves, graduation is compliance-gated.
2. Isolation is a soft toggle: one account, a mode flag on every object, `_test_`/`_live_` keys. Budget is weeks, not quarters.
3. The live gate is payment-processor activation or KYC.
4. No staging environment or mock server integrators depend on yet.
5. Time-dependent state and async events are core, not a stub.
6. There is a hosted checkout page, so it needs a test-mode mirror. Tell me if the API is the whole product.
7. This is a compounding platform surface, not a one-partner unblock. If a partner deadline is driving it, keep magic values plus the toggle and push the clock later.

## Findings, worst first

### 1. 🔴 The 10-minute trial and 15-minute renewal job is the wrong primitive
- **Three of four scenarios are uncovered.**
  - Dunning spans 7 days, the monthly renewal is 30 days, and the annual renewal is 365 days.
  - Your plan sends all three to "contact support to fast-forward".
  - That is time-dependent logic testable only by waiting, or by a human. CI can't open a ticket.
- **Sandbox behavior diverges from live.**
  - A trial that is 10 minutes in sandbox and 14 days live changes `trial_end`.
  - Integrator logic that computes "days left in trial" or schedules reminders behaves differently.
  - Any pre-expiry event, such as a "trial ending in 3 days" notice, has no sane timing at 10 minutes.
  - This is the "works in sandbox, fails live" drift the skill names as the root cause.
- **Renewals arrive up to 15 minutes late, at a random point in that window.** Integrator tests get flaky, and they can't assert on a deterministic moment.
- **Keep nothing of the compression. Replace it with a test clock:**
  1. A clock object has a frozen time. Test customers and subscriptions attach to it.
  2. `POST /v1/test_clocks/{id}/advance {frozen_time}` moves time forward. State transitions and events fire as if that time had passed.
  3. Trials stay 14 days. The renewal job and the dunning schedule stay identical to live: 3 retries over 7 days.
  4. Cap the advance per call. Cap what one clock carries: customers, subscriptions, and billing cycles per advance. Start with "up to two billing intervals of the longest plan on the clock". Annual plans then work in one call. The numbers are proposals to tune.
  5. Advancing is async. Return `status: advancing`, then `ready`. Emit events in timestamp order. Document that state and event delivery can lag.
  6. Delete a clock and everything attached to it in one call. This is also your reset path.
- **Each scenario on the clock:**
  - Trial expiry: advance 14 days.
  - Monthly renewal: advance one month.
  - Dunning: attach a failing payment method, then advance 7 days.
  - Annual renewal: advance one year.
- **Cheaper fallback if the clock slips.** Auto-aging fixtures whose date fields shift daily. This covers display logic only, not state transitions.

### 2. 🔴 "Contact support to fast-forward": delete it
- Support becomes the clock, with latency and a queue. Integrators can't automate it.
- Removing it makes the time-coverage gate pass: every time-dependent flow testable without waiting and without a human.

### 3. 🔴 Fire-webhook button: signature trap and coverage gap
- **Signing.** Your docs say "always verify signatures". Does the dashboard button send a correctly signed request?
  - If it sends unsigned, or signs with a different static secret, integrators have to disable verification to use your button. That trains them to ship without it.
  - Required: sign with the endpoint's own test-mode signing secret, using the same scheme as live.
  - If some trigger path (CLI, sample sender) can't produce a valid signature, say so next to the "always verify" rule.
- **Example payload with example data.**
  - A handler that looks up the subscription ID gets a 404, because the ID doesn't exist in the sandbox.
  - Fire the event for a real test object, or say plainly that it is a shape-only sample.
  - Set `livemode: false` in the payload. The shape must match live exactly.
- **One event type.** The coverage gate requires every event type fireable on demand. At minimum you need triggers for these events:
  - trial ending and trial ended
  - renewal succeeded
  - payment failed, per retry
  - subscription moved to past-due
  - subscription canceled after dunning exhausted
  - annual renewal succeeded
- **Dashboard only.** CI can't click. Expose the same trigger as an API endpoint or CLI command: "fire event type X for test object Y now".
- **Decoupling.** If advancing the clock changes state but events lag or don't fire, document it. Otherwise integrators wait for events that never come.
- **Delivery mechanics** (retries, delivery logs, resend) belong to `webhook-platform-design`. This design owns only how a test event gets triggered.

### 4. 🟠 Dunning setup friction: customer, subscription, three failed payments
Fix it with three layers, cheapest first:
1. **Magic values on the payment-method token.** Use tokens, not raw card-like numbers. Each maps one-to-one to a real error code from your published catalog. No sandbox-only error shapes.
   - `pm_test_decline_always`: every charge fails with the generic-decline code.
   - `pm_test_decline_n` (labeled per operation): the first N charges fail, then it succeeds. This covers the "dunning recovered" path.
   - `pm_test_insufficient_funds`, `pm_test_expired_card`, `pm_test_auth_required`.
2. **A scenario endpoint.** `POST /v1/sandbox/scenarios {"name": "dunning_retry_2"}` creates a customer, subscription, failing token, and clock, already advanced to the named state.
   - Start with 5 to 6 named scenarios: `trial_expiring`, `renewal_due`, `dunning_retry_1`, `dunning_retry_2`, `dunning_exhausted`, `annual_renewal_due`.
   - Skip the full config-driven fixture builder for now. It is the most work, and your data shapes don't vary enough to justify it.
3. **The clock does the rest.** Create a subscription with `pm_test_decline_always`, advance 7 days, and all 3 retries fire. That is two calls instead of clicking through everything.

Label every magic value per operation, and treat the catalog as API contract: additions are free, changes break integrators' CI.

### 5. 🟠 Isolation level and keys are unstated
- Write the isolation level in the docs: "test mode is a flag on one account, not a separate environment". "Sandbox" alone guarantees nothing.
- Use mode-prefixed keys with the codified shape: `sk_test_…` and `sk_live_…`, so secret scanners catch leaks.
- Enforce both directions. Live keys reject test objects. Test keys reject live ones.
- A wrong-mode key returns a clear "wrong environment" error, never an opaque 401.
- Test keys still read and write real account configuration. Tell integrators to treat them as secrets.
- Promote to a separate copy of the environment if teams need parallel testing, or a leak between modes would cause real damage.
- Test-mode webhook endpoints and signing secrets are separate from live. Test secrets don't carry over.

### 6. 🟠 Hosted checkout and billing portal
If integrators embed or redirect to a hosted page, it needs a test-mode mirror that accepts the magic tokens. Otherwise they can't test the card-entry and failed-payment UX. This is question 6, still open.

### 7. 🟠 No graduation path in the plan
- **Gate.** Match your real obligation: payment-processor activation or KYC. Before approval, return an explicit "environment not yet approved" error.
- **Cutover checklist, to publish as docs:**
  1. Swap credentials everywhere.
  2. Create fresh live webhook endpoints and signing secrets.
  3. Turn abuse rules on before the first live charge.
  4. Run one small live canary per path: a real charge and a real renewal. Confirm the effect and the event delivery, then refund.
- **Five pitfalls to document:**
  1. Key swap forgotten.
  2. Cross-environment paste.
  3. Assuming sandbox predicts live.
  4. Stale test webhook endpoints.
  5. Untested real-money failure paths.
- A green sandbox run doesn't prove real network timing, real decline behavior, or real fraud checks.

### 8. 🟢 Smaller items
- **Quotas.** Reuse production rate limits in test mode. A separate tier is needed only if you see evaluation-volume abuse.
- **Card-testing abuse.** Handle it with live-mode controls: bot challenge, per-IP decline caps, rate limits on checkout. The sandbox is useless for carding.
- **Seed data.** Use synthetic data only, never production copies. Run periodic cleanup of old clocks and objects.
- **Parity.** Build sandbox config from the same infrastructure-as-code as production. After this redesign the only sandbox-specific differences are the clock and the magic tokens. Document both.

## What to keep, change, delete

- **Delete:** the 10-minute trial, the 15-minute renewal jobs, and the "contact support to fast-forward" docs line.
- **Change:** the fire-webhook button. Sign it with the endpoint's test secret, fire it on real test objects, cover every event type, and add an API or CLI equivalent.
- **Add, in this order:**
  1. Magic payment tokens.
  2. Test clock, with a per-advance cap.
  3. Event triggers for all event types.
  4. Named scenarios.
  5. Reset and cleanup.
  6. Cutover docs and the live gate.

## Gates before launch

Both gates are pass/fail.
- **Failure-path coverage:** every documented failure is triggerable by a magic token or a simulation call. The failures are decline codes, past-due, dunning exhausted, and cancel. Target 100%.
- **Event and time coverage:** every event type is fireable on demand, and every time flow is testable by advancing the clock, never by waiting. Target 100%.
- **Cross-mode incidents:** track wrong-mode-key tickets. Target zero, reached structurally through prefixes and clear errors.
- **Graduation:** walk the checklist end to end, including one live canary, before declaring any integration launched.

## Effort, ranked
Rough estimates for a team that already has the billing job scheduler; these are my guesses, not measured.
- Magic tokens: days.
- Event triggers plus signing: about a week.
- Test clock: several weeks. It is the largest item and the only one that needs scheduler changes.
- Scenarios, reset, cutover docs: a few days each.

If you must cut scope, ship tokens and event triggers first. They unblock the dunning flow on their own, with the clock arriving later.

**Next action:** answer the 7 assumptions above, mainly 2 (soft toggle vs separate environment) and 7 (partner deadline vs long-lived platform). Those two change the order of work.