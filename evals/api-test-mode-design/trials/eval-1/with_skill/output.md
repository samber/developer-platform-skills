**Build the soft test-mode toggle plus magic test cards on your existing stack, and do both in 6 weeks. Don't build the separate sandbox now, and don't ship a doc-only answer.**

Stop using the corporate card in staging today. Real money moves and card data leaks into test logs. It also breaks your own rule that test inputs must never touch real networks.

## Assumptions

I couldn't ask questions, so I assumed these. Correct me if any are wrong, because each changes a step below.

- **KYC (Q3):** going live is gated by KYC on the platform and its vendors.
- **Time-dependent flows (Q5):** you have payout holds or settlement delay. If you don't, drop the simulated-time work in step 3.
- **Staging (Q4):** the current staging environment stays for internal use. Partners stop depending on it.
- **Hosted checkout (Q6):** it is in scope. Merchants embed it, so integrators must test it too.
- **Demand (Q7):** one partner is waiting on the deal, with a hard 6-week date.

## Why not the other two options

**Separate sandbox, two quarters: deleted from this pass.**
- Your budget is weeks, not quarters. The skill's rule: a weeks budget removes the hard separate copy from this pass.
- It doesn't unblock the partner. Two quarters is about 26 weeks against a 6-week deadline.
- Leakage is the real risk it solves. You can contain that risk in the toggle with the guards below.
- **Revisit when** the first cross-mode leakage incident happens, or a compliance regime demands demonstrable isolation, or parallel-team testing needs separate data. The hard copy is the better long-term model, so keep it on the roadmap.

**Doc telling partners to make a separate account: ruled out, not just demoted.**
- That is the "no test mode" option. It is viable only for APIs that touch no money.
- Payflux moves money between platforms and vendors, so this option is out entirely.
- "Be careful with test data" produces real charges and real payouts. It also leaves the 3DS and dispute paths untestable.
- A prospect's security review will not accept it.

## What to build

### 1. Isolation: soft toggle, with guards

State the level in the docs: *logical isolation, same host, shared infrastructure, same rate limits, data reset on request.* Don't just say "sandbox".

- **Mode flag:** add `livemode` to every object (platforms, vendors, payments, payouts, webhooks).
- **Keys:** use a type prefix plus a `_test_` or `_live_` substring, for example `sk_test_…`, `pk_test_…`, `rk_test_…`.
  - Follow the Stripe-style shape, because scanners and engineers already recognize it.
  - Add your own brand prefix in front. This is my judgment: it keeps Stripe's scanner alerts from firing on your keys.
  - Enroll the pattern in GitHub secret scanning.
  - Key lifecycle belongs to `api-auth-key-management`.
- **Hard guards:**
  - A test key can never reference a live object. Enforce this with a DB constraint, not only application code.
  - In test mode, the payment-processor adapter is swapped for a simulator at the boundary. The test code path holds no real processor credentials and makes no real network call.
  - Live rejects test values and test rejects real card numbers, in both directions.
- **Wrong-mode errors:** a wrong-environment key returns a legible error such as `wrong_environment: test key used on live resource`. Never return an opaque 401.
- **Both sides of the marketplace:** test mode needs test platforms and test vendors, not only test payments. Provide auto-provisioned fictional personas for both sides, in several states: KYC verified, KYC pending, payouts blocked.

### 2. Failure paths: magic values first

The carrier is the card number. Publish stable values that never expire. Each one maps one-to-one to your **real** published error code.

- Happy path, per network: Visa, Mastercard, Amex.
- Generic decline.
- Insufficient funds, with its own `decline_code`.
- Expired card and bad CVC.
- Processing error.
- 3DS challenge required.
- Succeed, then dispute.
- Fraud-review block.
- **Payflux-specific, by vendor persona:** payout fails, vendor KYC pending, vendor account restricted, split-payment partial failure.

Use tokens such as `pm_test_visa` in example code, not raw card numbers.

Add a small set of test-only endpoints for what no input can encode:
- Mint a test platform or vendor.
- Force a vendor into a KYC state.
- Force a payout into a state.

Skip the config-driven fixture builder. Your data shapes don't vary enough to justify it.

### 3. Events and time

- **Fire event now:** add `POST /test/events` and a CLI trigger, one per event type. Delivery mechanics (signing, retries, logs) belong to `webhook-platform-design`.
- **Two traps to document:** state changes and event delivery may be decoupled, and the CLI trigger may not carry a valid signature. Put both next to your "always verify signatures" rule.
- **Time:** add a "settle now / advance payout" endpoint first, so nobody waits days for settlement. Capped test clocks are the next rung up; build them only if renewals or scheduled jobs exist.
- **Reset:** add per-account `POST /test/reset`. Seed with synthetic data only, never copied production data.
- **Parity:** deploy test mode from the same infrastructure-as-code as live.

### 4. Hosted checkout, mirrored

- A session created with a test key renders in test mode with a visible "Test mode" banner.
- It accepts only magic cards and rejects real card numbers.
- It shows the 3DS challenge simulation.
- A real PAN typed into a test session is rejected and never stored or logged.

### 5. Credentials, quotas, abuse

- **Test keys aren't risk-free.** They still read and write real account config, such as webhook endpoints. Say so in the docs.
- **Quotas:** reuse live rate limits in test mode. This keeps integrators' throttling code honest, and it is cheapest.
- **Carding abuse is a live-mode control, not a sandbox one.** Before the first live transaction, turn on:
  - an edge bot challenge on checkout,
  - endpoint-scoped rate limits,
  - caps on cards per customer and consecutive declines per IP.

### 6. Graduation to live

- **Gate:** KYC activation for platform and vendors. Return an explicit `environment_not_approved` error before approval.
- **Cutover checklist:**
  1. Submit KYC early, before the launch date.
  2. Swap credentials in every environment and remove test keys from production config.
  3. Create fresh live webhook endpoints and signing secrets. Test secrets don't carry over.
  4. Run one small real canary per integration path, with confirmed settlement and confirmed event delivery, then refund it.
  5. Turn on the abuse rules from step 5 before the first live transaction.
- **Publish these pitfalls for integrators:**
  1. Key swap forgotten.
  2. Cross-environment paste.
  3. "Sandbox success predicts live".
  4. Stale live webhook endpoints.
  5. Untested real-money failure paths.

## 6-week plan (4 engineers)

These durations are my estimates, assuming the toggle fits your existing data model. They are not measured. Integrators start in week 3, which leaves 3 weeks of margin on the hard date.

| Weeks | Engineer | Work |
|---|---|---|
| 1–3 | A | Mode flag, key issuance and prefixes, DB cross-mode constraint, wrong-environment errors. |
| 1–3 | B | Processor simulator, magic card catalog, vendor personas. |
| 2–3 | C | Hosted-checkout test rendering, test banner, real-PAN rejection. |
| 2–3 | D | Fire-event endpoint and CLI, reset endpoint, docs and magic-value catalog v1. |
| **End of week 3** | | **Partner developers start integrating.** |
| 4–5 | A, B | Settle-now and payout-state endpoints, KYC-state forcing. |
| 4–5 | C | Mirrored checkout 3DS and dispute flows. |
| 4–5 | D | Cutover checklist and pitfalls doc. |
| 6 | All | Failure-path audit, leakage tests, live canary rehearsal, live abuse rules. |

Give the engineer who wanted the separate sandbox ownership of A's isolation guards and the leakage tests. Their instinct is right about risk, so put it to work there.

## Acceptance gates

Ship only when all of these pass.

1. **Failure-path coverage is 100%.** Every documented decline, error, 3DS flow, dispute and payout failure is triggerable on demand. One untriggerable path fails the audit.
2. **Event and time coverage is 100%.** Every event type is fireable on demand, and every time-dependent flow is testable without waiting.
3. **Zero cross-mode leaks in testing.** Attempt every cross-reference between test and live objects. All must be rejected.
4. **Graduation exercise done.** One live canary with confirmed event delivery before you call the integration launched.

Also track support tickets caused by wrong-mode keys. The target is zero, reached through prefixes and clear errors, not warnings.

## Next action

Today, disable the corporate card in staging and tell the logistics platform's developers the target date: sandbox keys in week 3.

If you want, I can draft the magic-card catalog mapped to your real error codes. I'd need your published error list first.