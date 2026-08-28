# Graduation gates and the cutover checklist

Every vendor surveyed gates production access behind some compliance or review step - graduation is never purely technical, even when the credential swap itself is trivial. Use the gate shapes to pick yours, then hand integrators the cutover checklist.

## Five gate shapes (cross-vendor)

| Vendor  | Gate shape                                  | Mechanics                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stripe  | KYC account activation                      | Testable immediately after signup; accepting real payments requires a completed KYC application (business, product, personal-relationship details) driven by regulator/financial-partner obligations. Often near-instant, but can require ID, proof of address, bank-ownership, or tax-ID verification. Business origin country cannot be changed after activation - a one-way door inside the compliance step. |
| Plaid   | Tiered, partly automated review             | Sandbox free and immediate. US/Canada teams get an auto-approved Trial plan (up to 10 production Items, gated major-bank OAuth) after identity verification, with flagged cases getting manual follow-up in 2-3 business days. EU/UK still runs a slower (~1 week) compliance process. The only surveyed vendor that moved toward self-service, auto-approved graduation.                                       |
| PayPal  | Approved-partner gate                       | Sandbox credentials work before approval; a live call without approval returns a flat 401 Unauthorized. Going live requires approved-partner status, a business account, and settlement reconfiguration - commonly coordinated with a PayPal representative, not self-service.                                                                                                                                  |
| GitHub  | Publisher verification + install thresholds | Apps work immediately with real data, zero gate. The gate appears only when monetizing: a paid Marketplace listing requires publisher verification (org-owned app, 2FA, verified domain) and install thresholds (GitHub Apps ≥100 installs, OAuth apps ≥200 users). Graduation decoupled from "does it work" and tied to commercial listing eligibility.                                                        |
| Shopify | Physical store-object graduation            | A development store cannot process real transactions and cannot be converted; going live means transferring to a merchant/paid-plan store. Shopify Payments can only be tested on a paid plan - the gate is a plan tier, not a review process.                                                                                                                                                                  |

Design implications: match the gate to the actual obligation (regulatory KYC, partner vetting, commercial listing, plan tier) - don't import a heavier gate shape than the domain requires. Tell integrators to submit the compliance step _early_, since review can take days regardless of vendor. And make the pre-approval failure legible: PayPal's flat 401 for an unapproved live call is the anti-pattern - return an explicit "environment not yet approved" error instead.

## Cutover checklist (provider designs it, integrator runs it)

1. Compliance/verification step submitted and approved - before the planned launch date, not on it.
2. Live credentials issued and swapped in every deployed environment; test credentials removed from production configuration.
3. Fresh live-mode webhook endpoints created, event subscriptions re-created, and live signing secrets captured - a test-mode signing secret does not carry over to live.
4. One small real canary transaction (or equivalent live operation) run per integration path, confirming both the operation's settlement/effect and its event delivery - ideally reversed/refunded afterwards.
5. Abuse-prevention and fraud rules configured before the first live transaction, not after an incident.

The canary step exists because a green sandbox run is necessary but not sufficient. Every vendor surveyed cautions that its sandbox doesn't fully replicate production:

- No real card networks or delivery carriers.
- Instant test settlement versus days-long live settlement.
- Fraud systems not running at full strength.

## The five recurring cutover pitfalls

Recurring across the survey regardless of vendor - each maps to a checklist line above:

1. Forgetting to swap test keys for live keys at launch, leaving the core function broken in production.
2. Pasting a live key into a sandbox context (or vice versa) - an opaque authentication failure rather than a clear "wrong environment" error; called out explicitly as a frequent PayPal support issue.
3. Assuming sandbox success predicts live behavior - "sandbox payments do not prove behavior on real card networks or live payment rails."
4. Forgetting fresh live-mode webhook endpoints, signing secrets, and event subscriptions.
5. Under-testing failure paths that only surface with real money or real delivery (real declines, disputes, settlement delay) because sandbox happy-path testing never forces them.

## Reactive triggers - signals to revisit an earlier stage

Not a one-time checklist; these mean "go back":

- A spike in declines or blocked responses at the payment layer signals an abuse attack in progress - tighten fraud rules and edge controls immediately, not as a one-off.
- Environment or institution-access errors from a tiered-access platform mean the integration never actually cleared the review step it assumed it had.
- Webhooks silently stopping (no errors, no deliveries) usually means a stale or unregistered live-mode endpoint - a cutover step that was silently skipped.
