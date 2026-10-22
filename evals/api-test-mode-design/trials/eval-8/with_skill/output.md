# Vaultic test-mode credentials: design review

Verdict: ❌ Four of the five proposals should change. Only the mode-in-the-key idea survives, and the key format still needs rework. I read the `api-test-mode-design` skill and its three references, then reviewed against them.

I assumed Vaultic is a data-aggregation/records-like domain with highly sensitive PII (payroll, employee records). You didn't answer the skill's clarifying questions, so open ones are at the end. Findings 2, 3 and 4 hold under any answer.

## Summary

| # | Proposal | Verdict |
|---|---|---|
| 1 | `VLTC-SBX-<uuid>` / `VLTC-PRD-<uuid>`, "unusual so attackers can't recognize them" | ❌ Wrong goal, wrong shape |
| 2 | Sandbox keys may be committed to public example repos | ❌ Reverse it |
| 3 | Quickstart uses the production key locally, with a config flag switching environments | ❌ Reverse it |
| 4 | Sample data is a scrubbed export of a customer's employee list | ❌ Replace with synthetic data |
| 5 | A key sent to the wrong host returns `{"error": "invalid_credentials"}` | ❌ Return a distinct wrong-environment error |

## 1. Key format: keep the mode in the key, drop the obscurity

**Keep:** the mode is visible in the key itself (`SBX` vs `PRD`). A self-describing credential prevents wrong-environment mistakes.

**Change:**
- **"Unusual so attackers can't recognize it" is the wrong goal.**
  - Attackers harvest keys from public repos by pattern. Hiding the pattern doesn't stop that.
  - You also hide the pattern from the defenders who would catch the leak.
  - The skill's rule is to adopt the widely recognized `_test_`/`_live_` shape rather than invent a novel one. A novel scheme buys no leak detection from tooling you don't control.
- **Use a recognized shape.**
  - Example: `vltc_sk_test_<random>` and `vltc_sk_live_<random>`. That is a type prefix, then a `_test_`/`_live_` mode substring.
  - Add a type segment now (`sk` secret, `rk` restricted, `pk` publishable if you ever ship one). Different blast radii deserve different prefixes.
- **Register your prefix for leak detection.** Enroll it with secret-scanning providers so leaks are blocked or revoked automatically. Confirm each provider's current partner-program requirements before promising this.
- **Check the secret part.** A UUID is acceptable only if it is a random v4. Never use a time-ordered or guessable variant. Use a dedicated high-entropy random string.
- Hashing, rotation, and dashboard UX belong to `samber/developer-platform-skills@api-auth-key-management`. This skill owns only the mode identity inside the prefix.
- Enforce the boundary both ways:
  - Live keys reject sandbox values.
  - Sandbox keys reject real values.

## 2. Don't let developers commit sandbox keys to public repos

"Can't touch real employee data" doesn't make a key risk-free. The prefix communicates mode, not risk level.

- On a toggle model, test keys still read and write real account configuration: webhook endpoints, settings, customers.
- A public sandbox key is a free, shared credential. Anyone can burn quota, pollute shared state, or probe your API.
- Per finding 4, your sandbox currently holds data derived from a real customer, so it isn't harmless anyway.
- It trains developers to treat "a key in git" as normal. That habit follows them to the production key.
- It floods your secret-scanning alerts with expected hits. Real leaks then get ignored.

**Instead:**
- Example repos read `VAULTIC_API_KEY` from the environment and ship a `.env.example` with a placeholder.
- If you want zero-setup demos, offer one clearly separate, read-only, synthetic-only, aggressively rate-limited demo credential that you can rotate at will. It is not a developer's own key.
- State this as a rule in the docs.

## 3. Quickstart: never use the production key locally

This is the most dangerous proposal. For payroll and employee data it means live PII and write access on developer laptops, in shell history, in debuggers, and in screen-shares.

The skill's rule:
- Tell integrators never to use live secrets in local development.
- Keep per-environment separation (data stores, redirect allowlists, credentials) rather than one codebase branching on a runtime flag.

A flag is a footgun. A forgotten flag, a bad default, or a copy-pasted config runs sandbox code against live payroll.

**Instead:**
- The quickstart uses only a sandbox key. It works within minutes, before any compliance review.
- The live key exists only in the deployed production environment, injected from a secrets manager. It never sits in a laptop `.env`.
- Environments differ by configuration (host and key), not by an in-code mode switch.
- A production key shouldn't even be issued until the graduation gate in section 7 passes.

## 4. Sample data: use synthetic data, not a scrubbed customer export

"Real production data copied into the sandbox as seed data" is a named failure mode in the skill. The rule is: seed with synthetic data only, never copy in production data.

HR data is the worst case for scrubbing:
- Small cardinalities (title, department, location, hire date, salary band) make re-identification easy even without names.
- Your customer is "friendly" but still entitled to a DPA, consent, and a way to withdraw.
- Every integrator, including competitors and attackers, gets that data forever. It is easily screenshotted and shared.
- Resets and exports keep copying it around.

**Instead, build a synthetic persona library.** The data-aggregation domain's design center is fixture variety. Payroll-shaped examples:
- Biweekly, semi-monthly and monthly pay frequencies.
- Mid-period hire.
- Terminated employee with final pay.
- Retroactive pay adjustment.
- Multi-currency and multi-country employee.
- Contractor vs. employee.
- Garnishment.
- Employee on unpaid leave.
- Missing or malformed record.

Ship it with:
- **Persona/identity carriers.** Fixed test employee IDs select a fixture shape. Fixed test company IDs select an org shape.
- **Minting endpoint** to seed a known state in one call.
- **Reset endpoint**, plus periodic automatic reset.
- **Auto-aging dates**, so the newest pay period is always "now".
- A **starter-fixture library**, so integrators don't hand-write configs.
- **Fixed, non-expiring IDs.** They are API contract; changing one breaks integrators' CI.

## 5. Wrong-environment error: make it explicit

`{"error": "invalid_credentials"}` for a key sent to the wrong host is a named, recurring support-ticket generator (PayPal's "very common support issue"). The developer has a valid key and no clue why it fails.

**Instead:**
- Return a distinct error, e.g. HTTP 401 `wrong_environment`, with a message like "This is a sandbox key; use https://sandbox.api.vaultic.example."
- Add it to your published error catalog. See `samber/developer-platform-skills@api-error-design`.
- **Decide from the prefix alone.** Don't look the key up. Otherwise the endpoint becomes an oracle that tells attackers whether a harvested key is valid.
- Apply the same rule in reverse: a live key against the sandbox host gets the same legible error.
- The design target is zero wrong-mode support tickets, achieved structurally (self-describing prefix plus a legible error), not by warning integrators.

## 6. Isolation model: missing from the proposal

The proposal never states an isolation level. "Sandbox" guarantees nothing by itself.

- **Recommendation: hard separate copy.**
  - Use a separate host, separate keys, and separate data store.
  - Payroll and employee PII means a toggle's failure mode (acting on live data while believing you're in test) has real blast radius. The skill's promotion triggers are met.
  - Your "key sent to the wrong host" scenario already implies separate hosts. Make that explicit.
- **Fallback:** if the engineering budget is weeks, not quarters, or a hard date forces it, ship a soft toggle first. Then:
  - Write the isolation level into the docs.
  - Give an explicit unblock condition for the hard copy: the first cross-mode leakage incident, or a compliance regime landing.
- Never let sandbox credentials reference production resources.

## 7. Gaps to cover before this is a test mode

- **Failure paths (gate: 100%).** Every documented error must be triggerable on demand. Use persona carriers (employee ID or password-like suffix) mapped one-to-one to your real error codes: not found, validation, permission/scope denied, locked record, pagination edge, rate-limited. Add step-up flows too. No sandbox-only error shapes.
- **Events and time (gate).**
  - Provide a "fire this event now" trigger per webhook event (`samber/developer-platform-skills@webhook-platform-design` owns delivery mechanics).
  - Provide a clock primitive for pay-period close, payroll run, and anniversary logic. Cap the per-call advance.
  - Document whether state changes and event delivery are coupled.
- **Quotas.** Don't build a separate limiter by default. Reuse production limits, which keeps integrators' throttling code honest. Add an aggregate volume cap only if you see evaluation-volume abuse.
- **Abuse controls.** Your real risk is leaked-key harvesting, not carding. Mitigate with server-side-only secrets, scoped/restricted keys, and secret-scanning enrollment.
- **Graduation.** Going live to employee data needs a gate. Likely candidates are partner vetting plus a DPA/security review. Pick the lightest shape matching your obligation.
  - Make pre-approval failures explicit ("environment not yet approved"), not a bare 401.
  - Hand integrators the cutover checklist: credentials swapped everywhere, fresh live webhook endpoints and signing secrets, abuse rules before the first live call, one canary per integration path with confirmed event delivery.
  - Document the five cutover pitfalls.
- **Parity.** Derive sandbox config from the same infrastructure-as-code as production. Drift is the root of "works in sandbox, fails live".

## Revised proposal

1. **Keys:** `vltc_sk_test_<random>` and `vltc_sk_live_<random>`, plus `rk_` restricted variants. Register the prefix with secret scanners.
2. **Isolation:** separate sandbox host and data store, stated explicitly in the docs.
3. **Quickstart:** sandbox key only, from an env var. The live key exists only in deployed production.
4. **Public repos:** no committed keys. Use a placeholder `.env.example`, or one separate read-only demo credential.
5. **Data:** a synthetic persona library with mint, reset, and auto-aging dates.
6. **Errors:** a wrong key for the host returns `wrong_environment` with the correct host named, decided from the prefix alone.
7. **Graduation:** an explicit gate, error, and cutover checklist.

## Open questions

These come from the skill's clarifying list. Each can change the design.

1. Is HR data the only domain, or does the API also move money (payroll disbursement)? That would add payments-style gating and settlement simulation.
2. Is a mode toggle acceptable, or must isolation be structural? What is the engineering budget: weeks or quarters?
3. What compliance regime gates going live: DPA, SOC 2 review, partner vetting, or a plan tier?
4. What test infrastructure already exists today (staging, fixtures, a mock server)?
5. Is there time-dependent state (pay periods, payroll runs, contract expirations) and webhook events?
6. Is there an end-user surface (an employee-facing hosted flow) that integrators must also test?
7. By when must integrators have the sandbox, and is it a one-off unblock or a lasting platform surface?
8. Did the friendly customer consent to their data being in a shared sandbox? If it's already deployed, delete it now and notify them.

## Measurement gates

- 100% of documented failure outcomes triggerable on demand.
- Every event fireable on demand, and every time-dependent flow testable via simulated time.
- Wrong-environment tickets and auth failures are at zero by design.
- The graduation checklist is walked end-to-end, including one live canary with confirmed event delivery, before any integration is declared launched.