# Ledgerlink sandbox v2: seeding and errors

**Domain:** data aggregation. Magic values ride the identity (test username and password), and the design center is fixture variety, not transaction outcomes. I read the skill and its three references and followed its five-step order.

## Verdict

Three parts of the plan break the skill's failure-mode checklist. Two others need a redesign.

| Plan item | Finding | Fix |
|---|---|---|
| Export 50,000 real accounts, scrub names and emails | ❌ "Real production data copied into the sandbox as seed data" is a named anti-pattern. | Synthetic data only (§2). |
| One shared sandbox, no cleanup jobs | ❌ "Shared sandbox with no reset mechanism" is a named anti-pattern. | Per-integrator state plus reset and TTL (§1, §3). |
| `/sandbox/force_error?code=X` hits "whatever call comes next" | ⚠️ It is global state in a shared environment, so it is non-deterministic. | Scope errors to an item and operation (§4). |
| No way to build the gig, small-business, joint and student shapes | ⚠️ Fixtures vary by integrator. | Promote the config-driven fixture builder and ship a starter library (§2). |
| "Read-mostly, so no cleanup" | ℹ️ This is false in the sandbox. Integrators mint items, arm errors and fire events. | Overlay TTL and reset (§3). |

## Assumptions

The skill says to batch questions before designing. You asked for the full answer, so I assumed the following. Correct me on any of them.

1. **Isolation budget:** quarters, not weeks, and a compounding platform surface rather than a one-off unblock. If it is weeks, the hard per-team copy drops out of this pass and the tenant overlay in §1 is the whole isolation story.
2. **Compliance gate for live:** partner vetting plus a security review.
3. **Existing infrastructure:** a staging environment exists, and integrators may already depend on parts of it.
4. **Time-dependent state:** yes. Consent expiry and sync lag.
5. **Async events:** yes. Webhooks.
6. **End-user surface:** a hosted bank-link flow. It needs a mirrored sandbox version.

## 1. Isolation model

**State the level in the docs:** "The sandbox is a separate environment with its own host and credentials. Each integrator gets a private writable overlay on a shared, immutable synthetic baseline. Nothing is shared between integrators except the read-only baseline."

- **Environment boundary (non-negotiable, cheap):**
  - Use a separate host, `sandbox.ledgerlink…`.
  - Use separate credentials.
  - Add no code path from sandbox credentials to production data.
  - This follows Plaid's model.
  - The "no test mode" rung is ruled out, because your API carries sensitive third-party financial data.
- **Per-integrator isolation (replaces "one shared sandbox"):**
  - The 50,000 synthetic accounts are a shared, read-only baseline.
  - Anything an integrator creates or mutates lives in a tenant-scoped overlay. That covers items, forced errors, webhook endpoints, tokens and fixtures.
  - Overlay writes are copy-on-write, so they never touch the baseline.
  - With this design, integrator A's `force_error` cannot break integrator B's CI run.
- **Full hard copy (Stripe Sandboxes style):** promote it only if teams need parallel, non-polluting environments inside one integrator, or a compliance review demands it. Revisit it when you see the first cross-tenant leak or when the compliance regime lands.
- **Keys:** use a type prefix plus a `_test_` / `_live_` substring, for example `ll_sk_test_…` and `ll_sk_live_…`.
  - Enroll the prefixes in GitHub secret scanning.
  - Reject test values on live keys, and reject real values on test keys.
  - A wrong-environment credential returns a clear `wrong_environment` error, never an opaque 401.
  - Key lifecycle belongs to `api-auth-key-management`.

## 2. Seeding

### Drop the production export

- Scrubbing names and emails is not anonymization. Transaction descriptions carry names ("ZELLE TO J SMITH"), employers, landlords and partial account numbers.
- Amount, date and merchant combinations re-identify people.
- No scrubber reliably catches free-text leakage.
- The data was probably collected under end-user consent for aggregation, not for sandbox reuse. Counsel should confirm that reading.
- The sandbox is lower-trust than production: broader access, weaker audit, and leaked test keys.

### Generate instead

- **Generator:** build a seeded generator, so the same persona always yields byte-identical data.
  - Calibrate it from aggregate statistics only: income cadence distributions, MCC mix, balance quantiles. Have privacy review approve the aggregates.
  - Merchants are fictional or from public MCC tables.
- **Baseline:** 50,000 accounts, so the "realistic scale" goal is met without using any real data.
- **Auto-aging:** date fields shift daily so the newest transaction is always "today". This is a cheap substitute for a clock.

### Identity-carried personas (the magic-value carrier)

Persona data is API contract. It is stable, documented and non-expiring. Changes ship as new names (`…_v2`), never as edits.

| Username | Shape |
|---|---|
| `user_good` | Happy-path basics. |
| `user_transactions_dynamic` | History that evolves on each sync. |
| `user_gig_worker` | Three income streams: weekly rideshare payouts, daily irregular delivery payouts, and lumpy net-30 freelance invoices. Negative-balance dips between payouts. |
| `user_small_business` | Payroll runs, card-processor deposits, sales-tax debits, seasonal revenue swings. |
| `user_joint_account` | Two owners returned by the identity product. Transactions attributable per owner. Shared and individual accounts mixed. |
| `user_thin_file_student` | Under 90 days of history, small balances, aid disbursements, few merchants. Tests empty and short-history states. |

### Config-driven fixture builder (promoted)

- Your integrators' end-user shapes genuinely vary, and they keep asking for new ones. This is the case where the skill says to promote the builder, the most work of the three simulation primitives.
- **Endpoint:** `POST /sandbox/fixtures` takes a full description of accounts, history and forced errors. It returns an item in the caller's overlay.
- **Starter library:** ship `ledgerlink/sandbox-fixtures` with the four personas above as editable configs. Without it, every integrator hand-writes JSON.
- **Sequence:** the personas come first (cheap, days each). The builder follows.

## 3. Events, time and reset

- **Events:** `POST /sandbox/items/{id}/fire_webhook {event}` for every event type (transactions updated, login required, consent expiring).
  - Document that state changes and delivery are decoupled, so integrators don't wait for events that never come.
  - Signing and retries belong to `webhook-platform-design`.
- **Time:**
  - Auto-aging covers history.
  - For consent expiry and sync lag, add `POST /sandbox/items/{id}/advance {days}` with a per-call cap.
  - Without it, a 90-day consent flow can only be tested by waiting.
- **Reset:**
  - `POST /sandbox/reset` returns the caller's overlay to baseline in one call.
  - Add an idle TTL on overlay objects, for example 30 days.
  - The baseline is immutable, so it needs no cleanup.
  - This replaces "no cleanup jobs."
- **Parity:** build sandbox config from the same infrastructure-as-code as production, so any difference is deliberate and documented.

## 4. Error testing

### Why `force_error?code=X` fails

- "Whatever call comes next" can be a health check, a retry, or another integrator's request.
- It is not scoped to an item, an operation or a tenant.
- It can't express "fail the third sync" or "fail only transactions fetch, not login".
- An unlabeled free-form `code` invites sandbox-only error shapes.

### Replacement: two mechanisms

**A. Magic values on the persona (default).** The password suffix selects the error.

- `user_good` with password `error_ITEM_LOGIN_REQUIRED` triggers that error.
- `mfa_questions_<n>_<m>` forces a multi-factor flow.
- `error_INSTITUTION_DOWN` and `error_RATE_LIMIT_EXCEEDED` work the same way.
- No new API surface is needed.
- Every suffix maps one-to-one onto your published error catalog (`api-error-design`). Never invent a sandbox-only error shape.

**B. Scoped on-demand arming**, for outcomes no input can encode:

```
POST /sandbox/items/{item_id}/force_error
{ "operation": "transactions_sync",   // required, labeled per operation
  "code": "PRODUCT_NOT_READY",        // must be in the real catalog
  "count": 1,                         // fail the next N matching calls
  "after_calls": 0,                   // optional: skip N calls first
  "expires_in_s": 300 }               // auto-disarm
```

- It applies to one item, one operation and one tenant.
- An unknown `code` returns 400 and lists the valid codes.
- The response echoes what was armed.
- Companion endpoints force state: `reset_login` (back to login-required), `set_verification_status`, `set_consent_expired`.

**Label every value per operation.** The same suffix can mean different things on login, accounts, transactions and identity. An unlabeled catalog is a documented trap.

## 5. Quotas and abuse

- Reuse production rate limits in the sandbox. It keeps integrators' throttling code honest, and three of six surveyed vendors do the same.
- Add an aggregate volume-and-scope cap per tenant only if load tests or scraping of the baseline become a problem.
- Leaked-key risk gets server-side-only secrets, scoped keys and secret-scanning enrollment.
- Carding abuse is a live-mode control, not a sandbox one.

## 6. Graduation to live

- **Gate:** a tiered, partly automated review. Auto-approve a trial with a small cap on real linked items, and add manual review for flagged cases.
- **Error before approval:** an explicit `environment_not_approved`. Never a flat 401.
- **Cutover checklist (publish it):**
  1. The compliance step is approved before launch day.
  2. Live credentials are swapped everywhere, and test keys are removed from production config.
  3. Fresh live webhook endpoints and signing secrets are created. Test secrets don't carry over.
  4. A live canary links one real account owned by the integrator and confirms both the data and the webhook delivery.
  5. Abuse and rate rules are on before the first real link.
- **Document the five recurring pitfalls:** the key swap is forgotten, a key is pasted across environments, sandbox success is assumed to predict live, stale webhook endpoints are left behind, and untested real-world failures show up only in production.
- **Sandbox limits:** it won't reproduce real bank latency, messy data, OAuth edge cases or institution outages.

## 7. Ship order and gates

1. Environment boundary, keys, and the tenant overlay.
2. Generator plus the four personas and magic-value error suffixes.
3. Scoped `force_error`, `fire_webhook`, `reset` and overlay TTL.
4. `advance` and the fixture builder with the starter library.
5. Graduation gate and the checklist docs.

**Gates (all must pass):**

- **Failure-path coverage:** every code in the error catalog is triggerable deterministically. The target is 100%, and one untriggerable code fails the audit.
- **Event and time coverage:** every event type is fireable on demand, and every time-dependent flow is testable without waiting.
- **Cross-environment incidents:** wrong-mode credential tickets are tracked, with a design target of zero.
- **Graduation exercise:** walk the checklist end to end, including one live canary with confirmed event delivery, before declaring any integration launched.

## Decisions for you

1. Confirm the assumptions above, mainly weeks vs quarters.
2. Pick the production-derived aggregates that privacy review will allow for generator calibration. None is also a valid answer.
3. Confirm the review-gate shape for live access.