**No, the key swap is not enough. Do not launch Friday on `sk_test` → `sk_live` alone.** Submit the review step today and fix the 401 before Friday.

Assumptions, because I could not ask the skill's clarifying questions: Meshpay is payments-like, test mode is a toggle on the account, and the review is KYC-style. Say so if any of these is wrong.

## What the doc and the 401 get wrong

1. **The activation doc skips the gate.** Graduation is never purely a credential swap. Every vendor surveyed gates live behind a compliance or review step. 400 green sandbox payments prove the integrator's code works against the sandbox. They do not prove it works on live.
2. **The plain 401 is the named anti-pattern.** It is PayPal's flat 401 for an unapproved live call. The integrator cannot tell a bad key, a wrong environment, or an unfinished review from a 401. Return an explicit error instead:
   - HTTP `403` (or the status your error catalog already uses for "forbidden state"), with a stable code such as `account_not_approved_for_live`.
   - A message like "Your account has not completed review. Live mode is not enabled."
   - A link to the review status page.
   - Add a sibling code for a wrong-environment key, such as `test_key_used_in_live` or `live_key_used_in_test`, so the two cases are distinguishable.
3. **Wrong-mode keys should fail loudly by design.** Your `sk_test` / `sk_live` prefixes already carry mode. Use them so a pasted wrong-mode key returns a clear message, not an auth failure. The design target is zero wrong-environment tickets, achieved structurally.

## Do now: Meshpay (Saturday 2026-10-03)

1. Check the integrator's review status today. Review can take days regardless of vendor, and an unapproved account cannot go live Friday. If review is not done, tell them now. Move the launch date or agree a limited live canary.
2. Ship the explicit error from point 2 above. Write one test that calls live with an unreviewed account and asserts the new code. Write a second test with a wrong-mode key.
3. Rewrite the activation doc. It must contain: the review requirement, the cutover checklist below, and the five pitfalls below.
4. Turn on live-mode abuse controls before the first live payment:
   - Edge bot challenge on checkout.
   - Per-endpoint rate limits.
   - Caps on instruments per customer and on consecutive declines per IP.
   - Carding hits live endpoints, not the sandbox. Stripe reports managed CAPTCHA on Checkout cut card testing by 80%, with under 0.02% impact on authorization rates.
5. Check the other failure paths with the integrator's integration in mind: every documented decline, dispute and step-up outcome must be triggerable in the sandbox. A failure path with no deterministic trigger fails the audit.

## Do now: the integrator (before Friday)

1. **Review is submitted and approved before launch day, not on it.** Confirm approval in writing.
2. **Swap credentials in every deployed environment** (every service, worker and CI job), not just one `.env`. Remove `sk_test` from production config.
3. **Create fresh live-mode webhook endpoints.** Re-create the event subscriptions. Capture the new live signing secret. The test signing secret does not carry over. Their working webhook handlers will verify against the wrong secret and silently reject every live event.
4. **Run one small real canary per integration path** (for example one booking payment, one refund). Confirm two things: the payment effect and the webhook delivery. Refund it afterwards.
5. **Test real-money failure paths** the sandbox never forced: real declines, a dispute, a refund, and slow settlement. Instant sandbox settlement differs from days-long live settlement.
6. **Never use live secrets in local development.** Keep per-environment config (data stores, redirect allowlists, credentials) instead of one codebase branching on a runtime flag.

## The five pitfalls to put in the doc

1. Forgetting to swap test keys for live keys, so the core function breaks in production.
2. Pasting a live key into a sandbox context, or the reverse, and getting an opaque auth failure.
3. Assuming sandbox success predicts live behavior. No sandbox replicates real card networks, settlement timing or full-strength fraud systems.
4. Forgetting fresh live webhook endpoints, signing secrets and subscriptions.
5. Under-testing failure paths that only surface with real money.

## Friday go / no-go

- **Go** only if: review approved, canary passed with webhook confirmed, abuse rules on.
- **No-go or limited launch** if review is pending. Do not launch on a key swap and hope.
- **Watch after launch.** Treat these as signals to go back a step:
  - A spike in declines or blocked responses means an attack in progress. Tighten fraud rules immediately.
  - Webhooks going silent with no errors means a stale or unregistered live endpoint. A cutover step was skipped.
  - Environment or access errors mean the integration never cleared review.

This is your first integrator, so track from day one: wrong-mode auth failures (target zero) and sandbox-to-live conversion time. No industry threshold exists, so baseline them in month one.

**Next, in under 2 minutes:** check this integrator's review status in your admin tool. Then tell me if the assumptions at the top are wrong and I will adjust the plan.