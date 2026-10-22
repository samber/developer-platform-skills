**Verdict:** don't ship the 10 req/min sandbox cap as the card-testing fix. Card testing happens in live mode, so the cap hits the wrong environment. Split the work into two problems with different controls.

## Problem 1: card testing

**Why the security lead's plan fails**
- The sandbox is useless for carding. Test transactions never reach real card networks, and the card number selects the outcome. A stolen card tested in sandbox returns nothing about whether it is still valid.
- Attackers gain nothing from "practicing" there. Magic values are public and the sandbox does not run fraud systems at full strength.
- 10 req/min is 600x below live (100/s = 6,000/min). One checkout flow is about 5–10 calls, so an integrator's 200-test CI suite (about 1,000 calls) needs about 100 minutes. Integrators can't load-test or exercise 429 handling.
- Fraud in live mode is untouched. Blocking carders in the sandbox while live stays open is the worst trade.

**Build in live mode (do these first)**
1. Add an edge bot challenge on hosted checkout and on authorization endpoints. Stripe reports managed CAPTCHA cut card testing 80% with under 0.02% impact on authorization rates. That is their number, so measure yours.
2. Add endpoint-scoped rate limits on authorize/confirm, separate from the global 100/s.
3. Add velocity rules:
   - cap distinct instruments per customer
   - cap consecutive declines per IP
   - cap small-amount authorizations per merchant and per BIN
4. Put these rules on before any new merchant's first live transaction, as a hard cutover-checklist item.
5. Treat a spike in declines or blocks as an attack in progress. Tighten rules at once.

**One sandbox-side control worth doing:** test keys must reject real card numbers, and the rejection must be identical for valid and invalid real PANs. That way the sandbox can never act as a validity oracle.

Also run an isolation audit. Confirm no test key path reaches a card network or issuer. Submit a known-valid real PAN with a test key and check that the response matches an invalid one.

Document the isolation level in the docs, since "sandbox" alone guarantees nothing. I assume a soft toggle here. For payments, the hard separate copy is the stronger long-term answer. This task doesn't require it.

## Problem 2: competitor scraping

This is evaluation-volume abuse. It is the one case where a dedicated sandbox quota is justified. Model it as an aggregate volume-and-scope cap on the sandbox tier (Plaid's pattern), not a slower per-minute limiter.

**Fix the source first.**
- Find what leaks pricing. Likely candidates are fee fields, fee-by-card-type, volume tiers, and settlement amounts in simulated objects.
- Sandbox fees should come from a flat published test schedule, never from production pricing logic, contracts, or production-derived data.
- If simulated fees equal your public price list, scraping reveals nothing. Anything in the sandbox that is not on the public pricing page is the leak.
- Pricing is an intentional sandbox-versus-production difference. Document it as one.

**Quota design.** Keep the per-second rate at live parity: 100/s, same 429 and `Retry-After` semantics. That keeps integrators' throttling code honest. Add aggregate caps on top:

| Layer | Starting limit | Purpose |
|---|---|---|
| Per-second rate | 100/s, same as live | Throttle-code parity |
| New account, daily volume | 50k requests, 10k live test objects | Covers a normal CI loop (about 20k/day) |
| Integrating account | 1M requests/day, 100k objects | Unlocked by signals: verified email, webhook endpoint registered, 1+ completed write flow |
| Load-test grant | Time-boxed, on request | Legit heavy testing |
| Cluster (shared budget) | One "new account" budget per cluster of linked accounts | Defeats mass account creation |
| Fee-quote sweep | Cap distinct (amount, currency, brand, country) combos on fee-bearing reads, per day | Defense in depth, only if fees stay varied |

- Cluster accounts by network (IP/ASN), device fingerprint, and email domain. Per-account caps alone lose to mass creation, which is the competitors' method.
- Starting values are guesses. No cross-industry threshold exists. Baseline for 2–4 weeks, then tune.
- Detection signals for scrapers:
  - many accounts per network
  - read-heavy with no webhook endpoint and no write flow
  - systematic grid sweeps across amounts and currencies
  - competitor domains
- Over-quota returns a distinct error, `sandbox_quota_exceeded`, with a docs link and a contact path. Shared corporate NAT then has a legible way out.
- Throttle and degrade clusters. Don't ban outright until a human reviews.
- Add a ToS clause banning competitive benchmarking and reverse-engineering of pricing. It is a backstop for enforcement, not a control.

**CAPTCHA on signup**
- Make it risk-based, not universal. Trigger it on disposable email, datacenter ASN, or a cluster over its signup budget.
- It targets mass account creation, not carding.
- Stripe's 0.02% figure covers live-checkout authorization rates. It doesn't transfer to signup friction.
- Set a tolerance for the drop in signup→first-successful-call conversion before launch, then measure.

**Keep these intact**
- Don't throttle magic-value or simulation endpoints harder than other calls. The failure-path coverage gate (100% of documented failures triggerable) depends on them.
- Seed with synthetic data only. Never seed from production.
- Automate periodic resets of shared sandbox data.

## Measurement
- **Live card testing:** card-testing attempts reaching issuers, declines per IP, authorization-rate impact of the new challenge.
- **Sandbox quota health:** 429 rate among verified, integrating accounts (target near 0), and signup→first-call conversion.
- **Scraping:** cluster-detection precision (review a sample by hand), and fee-sweep attempts blocked.
- **Isolation:** the real-PAN oracle test passes, and cross-environment auth tickets stay at zero.

## Estimates (for the engineers executing)
- Fee-source fix: days, after the diff below.
- Sandbox quota and clustering: about 1–2 weeks.
- Live-mode controls: about 1–2 weeks. The edge challenge itself is quicker if your edge vendor supports it.

## Assumptions (I couldn't ask first)
- Card testing hits live checkout or authorize endpoints.
- Sandbox is a shared soft toggle.
- Sandbox fee data is what the competitors scraped.

Confirm these. If the scraped data is not fee data, the source fix changes, but the quota design holds.

**Next (about 30 minutes):** pull what the competitors actually fetched from the sandbox logs. Diff those fee fields against the public pricing page. Anything not on the page is the leak.