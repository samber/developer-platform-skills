# Magic-value catalogs: worked examples across five product domains

A magic value is a fake input that is not random filler - it is a deterministic key that selects a specific test outcome. These catalogs show how five vendors shape the pattern to their domain. Treat every table below as a snapshot: vendors periodically update their lists (Stripe says so explicitly), so verify against the vendor's live testing docs before hard-coding any value into an automated suite.

## Stripe: the card number is the key (payments)

The card number alone decides the outcome. Expiry, CVC, and ZIP can be anything valid. Test values don't expire - the catalog is a stable, long-lived contract integrators memorize, not a rotating fixture set.

| Number                                                                         | Outcome                                                                                            |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| `4242 4242 4242 4242`                                                          | Always succeeds (the canonical happy path)                                                         |
| `4000 0000 0000 0002`                                                          | Generic decline (`card_declined`)                                                                  |
| `4000 0000 0000 9995`                                                          | Insufficient funds - a distinct `decline_code`, so the integrator's UI can show specific messaging |
| `4000 0000 0000 9987` / `9979`                                                 | Lost card / stolen card                                                                            |
| `4000 0000 0000 0069` / `0127` / `0119`                                        | Expired card / incorrect CVC / processing error                                                    |
| `4000 0000 0000 0259`                                                          | Charge succeeds, then is disputed as fraudulent - tests dispute handling, not just declines        |
| `4100 0000 0000 0019`                                                          | Fraud-review: always blocks (risk "highest")                                                       |
| `4000 0000 0000 4954` / `9235`                                                 | Highest risk but processes / elevated risk                                                         |
| `4000 0027 6000 3184`                                                          | 3DS2 challenge required                                                                            |
| `4000 0025 0000 3155`                                                          | Authentication required only on setup / off-session                                                |
| `4000 0000 0000 3220`                                                          | 3DS required on every transaction (always-challenge variant)                                       |
| `5555 5555 5555 4444` (MC), `3782 822463 10005` (Amex, 15 digits, 4-digit CVC) | Non-Visa happy paths - cover more than one network                                                 |

Two transferable lessons:

1. **Token over raw value**: Stripe recommends a token (`pm_card_visa`) instead of a raw number in test code - raw sensitive values in server-side code become a compliance habit that carries into production paths.
2. **Bidirectional mode boundary**: test values only work with test keys; a live key rejects them outright, and a real card in test mode violates the platform's terms. Enforce both directions, not just "live rejects test."

## Twilio: magic numbers split by operation, restricted to test credentials (communications)

Test credentials can never touch real numbers or carriers - a request made with test credentials cannot even specify a live account number as `From`, so the _only_ usable `From` is a documented magic number. No call is placed, no SMS sent, no status callbacks fire: the request never reaches a real network.

The catalog splits by **operation type**, and the same numeric suffix means different things across operations - a documented trap:

- Number purchasing: `+15005550006` valid/available; `+15005550000` unavailable (21422); `+15005550001` invalid (21421); area code 533 has none available; area code 500 is available.
- SMS `From`: `+15005550006` valid; `+15005550001` invalid (21212); `+15005550007` not SMS-capable/not owned (21606); `+15005550008` queue full (21611).
- SMS `To`: `+15005550009` can't receive SMS (21614); `+15005550002` can't route (21612); `+15005550003` no international permission (21408); `+15005550004` blocked (21610).
- Voice `To`: `+15005550001` invalid (21217); `+15005550002` can't route (21214); `+15005550003` no international permissions (21215); `+15005550004` blocked (21216).

Note "can't route" is `...0002` for voice but SMS uses `...0009` for its closest equivalent - cross-referencing the wrong operation's table is an easy, documented mistake. Design lesson: one flat catalog for a multi-operation API invites exactly this confusion; label every value with the operation and field it applies to. For OTP flows there is no universal always-correct code - a reminder that not every domain admits a magic value.

## Plaid: the username is the magic value (data aggregation)

- Personas select the fake data shape: `user_good`/`pass_good` for basic access, `user_transactions_dynamic` for evolving history, plus role personas (`user_small_business`, `user_yuppie`, …).
- Error simulation rides the password: `user_good` + password `error_ITEM_LOCKED` deterministically triggers that error - failure modes parameterized without one endpoint per error.
- MFA the same way: password `mfa_questions_<n>_<m>` forces a multi-factor flow; two named institutions always launch MFA regardless of credentials.
- `user_custom` accepts a full JSON config shaping accounts, transactions, identity, and forced error codes in one request - the most granular fixture-construction mechanism surveyed. Plaid publishes a starter-fixture repo (`plaid/sandbox-custom-users`) rather than expecting integrators to hand-write configs.
- Identity verification uses reserved sample identities: the name "Leslie Knope" deterministically passes, the surname "Gergich" is deliberately blocklisted - the same pattern applied to an identity product.
- Reset/lifecycle endpoints, distinct from event firing: `/sandbox/item/reset_login` forces re-auth state to test the recovery flow; `/sandbox/item/set_verification_status` skips real micro-deposit timing; `/sandbox/public_token/create` mints test objects directly for seeding.
- Sandbox items auto-age (auto-transition to a login-required state after 30 days) and `user_custom` date fields auto-shift daily so the newest date is always "today" - a low-effort substitute for a true time-manipulation primitive.

## PayPal: the name field drives the outcome (payments, contrast case)

Entering a rejection-trigger string (e.g. `CCREJECT-REFUSED`) in the "Name on Card" field, with any valid test card number, forces that decline - the opposite convention from Stripe, where the number itself varies. Trigger values are case-sensitive, and every rejection returns the same AVS/CVV placeholder values regardless of reason - so rejection _reasons_ cannot be distinguished from those fields. The older Classic API puts magic values directly into transaction fields (amount, authorization ID, CVV2, street) for finer-grained negative testing.

## Shopify and GitHub: the lightweight end of the spectrum

- **Shopify's Bogus Gateway** ("Test payment gateway"): payment method name `Bogus Gateway`, then a card number of `1` (approved), `2` (declined), or `3` (gateway failure) - the simplest scheme surveyed, usable only on a development store. Shopify Payments' own test mode reuses Stripe's card catalog directly - a platform built on a processor inheriting the processor's magic values instead of inventing its own is a reusable pattern.
- Shopify has **no "send test webhook" button**: fire real order webhooks via a Bogus Gateway test order, or use the CLI trigger - whose payloads carry valid JSON but **not a valid HMAC signature** for the app's secret. If guidance says "always verify signatures," it must carve out the vendor's own test trigger, or the rule breaks the test tooling.
- **GitHub** (no sandbox, no fire-webhook endpoint) offers three narrower mechanics:
  - Webhook redelivery: replay a past real delivery.
  - A `ping` event via REST.
  - A REST-triggered test push for repository webhooks, with deliveries inspectable in the UI.

  It also documents an event-suppression limit: pushing more than 3 tags at once fires no `push` event at all, silently, the kind of threshold trap a catalog should name explicitly.

## What the cross-domain comparison teaches

- The magic value's _carrier_ is domain-shaped: card number (payments), phone number per operation (communications), username/password (data aggregation), name field (PayPal), single digit (Shopify). Pick the carrier integrators already type in that domain.
- Every catalog needs deliberate-failure values, not just happy paths - and the failure values should map one-to-one onto the API's real, documented error codes.
- Include the domain's step-up flows (3DS challenges, MFA, identity review), not just success/decline binaries.
- Publish the catalog as documentation with stable values; it is API contract, and integrators' CI suites will depend on every entry.
