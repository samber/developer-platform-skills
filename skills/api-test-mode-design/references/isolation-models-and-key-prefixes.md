# Isolation models and test-key prefixes: cross-vendor comparison

How six platforms structurally separate test data from live data, ranked from hardest to softest isolation, plus the credential conventions that make the mode visible in the key itself.

## Isolation architecture by vendor

| Vendor                  | Model                                | Mechanics                                                                                                                                                                                                                                                                                         |
| ----------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Plaid                   | Hard separate-copy (hardest)         | Two entirely separate environments on different hosts (`sandbox.plaid.com` vs. production), each with its own `client_id`/`secret`. Explicit rule: "Items cannot be moved between environments. The Sandbox environment supports only test Items." No toggle, no shared account.                  |
| Stripe Sandboxes        | Hard separate-copy                   | A separate, isolated copy of the account with its own keys, webhooks, customers, and configuration - teams run parallel tests without polluting shared test data. Stripe made Sandboxes the default for new accounts: "Test mode is no longer the default testing method."                        |
| Shopify                 | Hard separate-copy (non-convertible) | Development stores the integrator owns and controls; they cannot process real transactions, cannot be converted to production, and cannot be transferred to a client directly - a dedicated "client transfer store" mechanism exists for merchant handoff (a three-way split not seen elsewhere). |
| Stripe legacy test mode | Soft toggle                          | A toggle on the same live account: swap to `sk_test_`/`pk_test_` keys and calls route through test infrastructure. A `livemode` boolean on every object marks which side it belongs to; test data is invisible to live calls and vice versa. Kept for existing accounts alongside Sandboxes.      |
| PayPal                  | Soft toggle over disjoint accounts   | A dashboard toggle switches which credentials and transaction data you see; underneath, the sandbox account "is not linked to your production account in any way," and sandbox transactions live on a separate mirrored test site. Soft toggle UX, hard account-level separation.                 |
| GitHub                  | None (integrator convention)         | No test mode at all. Isolation is achieved entirely by developer convention - separate test apps, organizations, and repositories, plus a tunnel tool to forward webhook deliveries locally. The only surveyed vendor pushing isolation responsibility onto the integrator.                       |

Generalizable lesson: a toggle is cheap to build but risks accidental cross-contamination when the toggle state isn't obvious in the UI. A fully separate copy costs more but makes cross-mode leakage structurally impossible rather than merely policy-forbidden. Stripe running both models side by side - and moving its default to the hard one - is the clearest signal of where a payments-grade platform lands as it matures.

Caveat: even a "true sandbox" is often only partially isolated. Stripe test mode, Paddle sandbox, and Plaid sandbox are all stateful but _shared_, rate-limited, and tied to a provider account, not per-session isolated.

One vendor comparison even found a "Mock" product with full per-user isolation while its "Sandbox" counterpart was the shared, cross-contaminating environment. Never let the word "sandbox" imply an isolation level; state the level explicitly in the design.

Two structural surfaces, not one: PayPal splits the Sandbox Test Site (a mirrored end-user site where fictional accounts log in and see transaction history) from the Developer Dashboard (where the integrator manages those accounts and reads credentials). When the product has an end-user-facing side, buyer-experience testing needs the mirrored surface, not just API responses.

PayPal's sandbox also auto-provisions fictional accounts for _both_ sides of its marketplace - a personal (buyer) and a business (seller) account with generated credentials, recognizable by convention (`sb-[random-string]@personal.example.com`). A two-sided product's test mode must model account variety on both sides, not just transaction variety.

## Test-key prefix taxonomy (Stripe)

Each row is a distinct blast-radius level, not just a mode label:

| Prefix                  | Type                   | Mode         | Client-safe?     | Capability                                   |
| ----------------------- | ---------------------- | ------------ | ---------------- | -------------------------------------------- |
| `pk_test_` / `pk_live_` | Publishable            | test / live  | Yes              | Tokenize, identify account in browser/mobile |
| `sk_test_` / `sk_live_` | Secret                 | test / live  | No (server only) | Full account API access                      |
| `rk_test_` / `rk_live_` | Restricted             | test / live  | No (server only) | Scoped least-privilege access                |
| `sk_org_`               | Organization secret    | -            | No               | Org-level access across accounts             |
| `whsec_`                | Webhook signing secret | per-endpoint | No               | Verify webhook authenticity (not an API key) |

The middle substring (`_test_` vs. `_live_`) is the mode switch. Live secret/restricted keys are shown only once at creation - captured and stored immediately, never re-displayed.

**The convention is externally codified**: GitHub secret scanning / push protection treats `sk_live_`, `sk_test_`, `rk_live_`, and `rk_test_` as officially documented, zero-false-positive push-protection targets. Third-party tooling recognizes and blocks these exact prefixes independent of Stripe's own dashboard. Adopt the widely recognized `_test_`/`_live_` shape rather than inventing a novel one - a recognized prefix buys free, automatic leak detection from scanners the vendor doesn't control.

## Sandbox quotas across twelve vendors

Sandbox-_specific_ numeric rate limits are the sparsest-documented axis in this survey - which is itself the finding. Snapshot: vendors revise published limits.

| Vendor                                                          | Sandbox quota posture                                                                                                                                                                                                                                                                                                                                                                     |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Twilio, PayPal, Shopify, Coinbase (CDP Checkouts/Payments API)  | Production limits applied unchanged in test mode - four of twelve, the plurality position. Shopify adds _functional_ rather than numeric test limits (test gateway incompatible with POS and subscription checkouts, a ~$1 minimum test amount). Coinbase states the parity explicitly in its sandbox documentation rather than leaving it implicit.                                    |
| Stripe, Square                                                  | No distinct sandbox rate limit published. Stripe's nearest functional throttle is unrelated to request volume: the test-clock cap on how much simulated time one advance may jump. Square documents only a qualitative warning that high-volume bursts return a `RATE_LIMITED` error, with no numeric threshold disclosed for either environment.                                       |
| Plaid, Adyen (Legal Entity Management API)                      | Numerically stricter sandbox quotas, tiered or split. Plaid: pre-production tiers cap aggregate call volume and gate major-bank access (Trial supports up to 10 production Items) - a volume-and-scope cap, not a per-minute limiter. Adyen's Legal Entity Management API (its KYC/onboarding product, not its core Payments/Checkout API) publishes an explicit numeric split: 700 requests per 5 seconds live versus 200 requests per 5 seconds test, plus a 5-failures-per-10-seconds throttle - roughly 3.5x more restrictive in test. |
| Checkout.com, Braintree                                         | Documented as stricter in sandbox, but without a full published table. Checkout.com states lower rate limits apply to its sandbox environment, with no figures given for either side. Braintree discloses a sandbox-only throttle (50 requests per minute per IP address, then a 5-minute block) with no equivalent production figure published.                                       |
| GitHub, SendGrid                                                | No sandbox concept to compare against. GitHub's published numbers (60 requests/hour unauthenticated, 5,000 requests/hour for user tokens, plus secondary concurrency and per-endpoint point budgets) apply identically everywhere since there is no test mode. SendGrid's "sandbox mode" is a boolean flag on a single endpoint, not a separate environment with its own credentials or rate-limit tier. |

Design takeaway: don't default to building a separate sandbox limiter. Build one when the failure mode is evaluation-volume abuse - free-tier scraping, load tests against a shared sandbox - and model it on Plaid's aggregate volume-and-scope cap, or Adyen's explicit numeric split, rather than on a faster per-minute limiter.

## Vendors that identify mode without a prefix

An alternative design, not a lesser one - but it carries a named cost:

- **Plaid**: environment-specific `client_id`/`secret` pairs with no shared prefix; the environment identity lives in which host you call, not in the credential string.
- **PayPal**: entirely separate sandbox and live Client ID / Secret pairs. Pasting a live key into a sandbox context (or vice versa) produces an authentication failure - flagged in the research as "a very common support issue," i.e. the cost of a non-self-describing credential is a recurring, avoidable support burden.
- **Twilio**: a separate, region-specific Test Account SID and Auth Token used only for magic-value testing.
- **GitHub**: OAuth tokens, App JWTs, and PATs with no test/live prefix at all - consistent with having no test mode.

Design takeaway: a self-describing prefix is optional for correctness, but it materially reduces one specific failure mode, a wrong-environment credential silently accepted or opaquely rejected. This is the shared-ground point with the sibling key-management skill: the prefix communicates _mode_, not _risk level_. Test keys still read and write real account configuration on toggle-model platforms.
