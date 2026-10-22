# Review of the test-mode plan

**Verdict:** keep 1 point with changes, reverse 2, and design the last one now.

| # | Plan item | Verdict | Change |
|---|---|---|---|
| 1 | `{"sandbox_error": ...}` format | ❌ Reverse | Use the production error shape, plus an additive marker |
| 2 | Quarterly rotation of magic numbers | ❌ Reverse | Keep them permanent and append-only |
| 3 | One master list everywhere | ⚠️ Keep, change | One list, but define outcomes per role |
| 4 | Test keys can text a teammate's real phone | ❌ Reverse | Make it a separate, restricted live-mode feature |
| 5 | Delayed carrier rejection | 🎯 Design | Compressed-time magic number, plus a control endpoint |

## 1. Error format: use the production envelope, add a marker

**Problem.** A different error shape means integrators never exercise their real error handling. Their parser reads `error.code`, so it never sees the sandbox shape. Tests pass against the sandbox, then production errors hit untested code. Typed SDKs would also need a second error type.

**Change.**
- Return the exact production error body: same fields, same codes, same HTTP status.
- Mark every test-mode response, successes included, with an additive signal:
  - a response header such as `Textwire-Livemode: false`
  - a body field `"livemode": false`
- Integrators can then tell simulated from real without a second parsing path.

## 2. Rotation: permanent numbers

**Problem.** Hardcoding is the intended use of magic numbers, so rotation punishes the expected behavior.
- Every CI suite, fixture and doc snippet breaks each quarter.
- The worse failure is silent. A retired number stops erroring and behaves like a normal number, so the "error" test either fails confusingly or passes for the wrong reason.
- Nothing is protected. The numbers are public, inert, and never reach a carrier.

**Change.**
- Make the list stable and append-only. Never reassign or retire a number's meaning.
- If a scenario must change, add a new number and mark the old one deprecated in the docs. Keep the old one working.
- Keep every number in a range that can't be a live subscriber. Confirm that none can route if a test key reaches a live path by mistake.
- For scenarios you don't want as numbers, offer an explicit per-request scenario parameter. Don't use rotation for that.

## 3. One master list: keep it, but make it a matrix

One list is good for docs and consistency. The flaw is saying that one number "means the same thing" in every context.

- **Roles differ.** Invalid as a sender (not owned or not allowed), as a voice destination (unreachable) and in purchasing (unavailable) are different failures.
- **Some scenarios exist in one context only.** Voice has busy, no-answer, voicemail and call-dropped. Purchasing has unavailable and already-owned. SMS has landline/not-SMS-capable, opted-out and blocked.
- **One number gives one outcome.** Callers can't combine scenarios, so you need enough numbers to cover each independent outcome.

**Change.** Publish one list where each number has a defined outcome per role. A number that doesn't apply to a role must return a documented result, never undefined behavior.

| Number | SMS destination | SMS sender | Voice destination | Purchase |
|---|---|---|---|---|
| …0001 | `invalid_number` | `invalid_sender` | `invalid_number` | `invalid_number` |
| …0002 (example) | landline, SMS unsupported | not applicable, documented | rings, answers | not applicable, documented |
| …0003 (example) | opted out | not applicable, documented | busy | unavailable |
| …0004 (example) | delayed carrier rejection (see §5) | not applicable, documented | no answer | already owned |
| …0009 (example) | success | success | success | success |

- Only …0001 is fixed by your plan. The other rows are placeholders.
- Include an explicit success number for every role. Integrators need a happy path as much as a failure path.
- Make the "invalid" error share one code across roles wherever the cause is the same.

## 4. Real-phone sends: take it out of test mode

**Problem.** Test mode's core promise is no real side effects and no cost. This breaks that promise.
- **Abuse.** Test keys get pasted into repos, CI logs and screenshots, and are usually guarded less. This opens an SMS-pumping and toll-fraud path, especially for voice, which can reach international premium destinations.
- **Compliance.** Real messages need consent, and real sender registration (A2P 10DLC and equivalents). A test key has neither.
- **Weak trust anchor.** "Verified teammate" goes stale when people leave. The verification flow also becomes a social-engineering target.
- **Not truly end-to-end.** Real carrier delivery needs a registered sender. A test key can't exercise that anyway.

**Change.** Offer the one real end-to-end check as its own mode, not as a test-credential privilege.
- Give it a distinct credential type, for example a live key scoped to an allowlist of verified numbers.
- Add a hard rate limit and spend cap, and a small free quota if you want to absorb the cost.
- Log every send for audit, and require re-verification on a schedule.
- Keep test credentials fully hermetic: no carrier, no billing.

## 5. Delayed carrier rejection: compress time and offer two entry points

Integrators are testing the asynchronous path: a `queued` message that later becomes `undelivered`, with a status callback. Hours of real delay is useless in a test run.

**Recommended design:**
1. **Zero-config path.**
   - Add a magic number (the …0004 slot above).
   - The send returns `queued` immediately.
   - After a short fixed delay, say 30 seconds, the message moves to `undelivered` with a realistic carrier error code (filtered, unreachable, unknown subscriber).
   - Polling `GET message` shows the change.
   - The webhook fires, signed with the test secret.
2. **Explicit control path.**
   - Add a test-only endpoint to trigger a transition on an existing message, for example `POST /test/messages/{id}/events {status, error_code}`. Add an optional `delay` for the first path.
   - This lets integrators test webhook retries, duplicate delivery and out-of-order events on demand.
   - A Stripe-style test clock that advances time is the heavier alternative. Skip it unless you need it for other products.
3. **Same shape as real events.**
   - The callback payload and the later `GET` response match production.
   - Both carry `livemode: false`, per §1.

## Revised plan, in order

1. Production error envelope plus `livemode: false` on every test-mode response.
2. Permanent, append-only magic numbers in a non-routable range.
3. One list with a per-role outcome matrix, including success numbers.
4. Hermetic test credentials. Ship the real-phone check as a separate allowlisted, capped live-mode feature.
5. Delayed-rejection number plus the test event endpoint.

## Questions for the platform team

- Which carrier error codes should the delayed rejection use, and is the 30-second default acceptable?
- Will real-phone verification ship in this release? If not, point integrators to a documented manual check meanwhile.
- Is there a technical reason behind rotation, such as a concern that the numbers are being abused? If so, state it. It may need a different fix.