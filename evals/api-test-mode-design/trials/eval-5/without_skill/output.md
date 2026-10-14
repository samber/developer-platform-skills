# Chargeline sandbox quota and abuse posture

**Verdict:** Do not ship 10 req/min plus CAPTCHA for everyone. It doesn't stop card testing. It breaks legitimate integrations. It doesn't stop scraping either, because the rate limit isn't the scraping control. Treat the two problems separately.

## 1. Card testing is a production problem

The security lead says "the sandbox is where attackers practice". That holds only if the sandbox gives a real validity signal on a stolen card.

**Check first (about 1 hour, engineering):**
1. Does sandbox ever call a real network, issuer, or BIN lookup?
2. Does sandbox accept non-test PANs and return different outcomes for them?
3. Do sandbox decline codes mirror production issuer decline codes?

If the answers are no, sandbox is a closed simulator. A stolen card gives the attacker nothing there, so the real card testing is happening in production. If any answer is yes, that leak is the bug. Fix it directly.

### Sandbox controls against card testing (cheap)
- Accept only documented test PANs in sandbox.
- Reject any other PAN with a fixed error. Never validate Luhn, BIN, or expiry beyond that.
- Log every non-test PAN attempt in sandbox. It is a high-signal account flag: a developer never types a real card there.
- Auto-suspend the account after N such attempts (start with 3).
- Make sandbox outcomes depend only on the test PAN and amount magic values. Never on issuer data.

### Production controls (where the fraud is)
- Velocity limits per card, BIN, IP/ASN, device, and merchant. Count authorizations, not requests.
- Pattern rules: many small amounts, high decline ratio, sequential or enumerated PANs, many cards on one merchant.
- Require CVV and AVS on card-not-present flows. Disallow zero-amount and $0.50-style auths, unless the merchant is verified.
- Auto-pause a merchant when the decline ratio exceeds a threshold (start at 40% over 100+ auths in 10 minutes). Alert a human.
- CAPTCHA or 3DS on the merchant's checkout when the card-testing score is high. It goes on **checkout**, not on developer signup.
- New production accounts get low auth caps until KYB and a first verified settlement (start at 100 auths/day and a small daily volume cap). Raise the caps in steps.
- Don't let a sandbox account convert to production keys without a separate review.

## 2. Scraping and reverse-engineering is a data-exposure problem

Competitors mass-create accounts to read simulated data. A rate limit on one account doesn't stop that, because they create many accounts. Fix what the data reveals.

### Data hygiene (the real control)
1. Audit every sandbox response field against one question: can it reveal how we price, route, or score? Likely culprits are fee breakdowns, interchange or markup lines, routing decisions, risk scores, and decline-reason distributions.
2. Make sandbox fees synthetic. Use a fixed public list price, or return no fee detail. Never run the production pricing engine in sandbox.
3. Randomize or flatten risk scores and routing in sandbox, seeded per account. Document that these are not representative.
4. Pricing logic that must be seen by customers belongs on the public pricing page, not in simulated responses.
5. After the audit, scraping the sandbox yields nothing a competitor couldn't read on our website.

### Detection of the mass-account pattern
- Cluster accounts by IP/ASN, device fingerprint, email pattern, signup timing, and payment method on file (if any).
- Flag parameter sweeps: grids over amount × currency × country × card brand, with little or no integration-like behavior (no webhooks configured, no SDK user agent, no error handling).
- Flag read-heavy accounts: many GET/list calls, no writes that look like an app flow.
- Flag disposable email domains and known competitor domains. Use domain match as a review signal, not an auto-ban, since it's easy to evade.

### Response ladder
1. Soft: tighter quotas and a challenge on the next action.
2. Silent: serve degraded or generic synthetic data to flagged clusters (don't reveal the detection).
3. Hard: suspend the cluster after human review. Cite the ToS clause banning competitive analysis and scraping. Have legal add that clause if it's missing.

## 3. Quota design

Quotas are per **account, organization, and verification tier**, not one number for everyone. Tiers are proposed numbers. Tune them from real traffic.

| Tier | How to reach | Sustained rate | Burst | Daily cap | Notes |
|---|---|---|---|---|---|
| T0 Unverified | Signup, email not confirmed | 1 req/s | 5 | 1,000 | Read-only docs examples, no webhooks |
| T1 Verified | Email confirmed + invisible bot check | 10 req/s | 50 | 20,000 | Default developer tier |
| T2 Trusted | GitHub/org-domain link or phone, or 14 days of normal use | 25 req/s | 100 | 100,000 | CI and load testing OK |
| T3 Partner | Production customer or approved request | 100 req/s | 500 | 1,000,000 | Matches production rate |

Rules:
- The 10 req/min figure (0.17 req/s) is about 600× below the production 100 req/s. A test suite or CI run trips it in seconds. Developers will leave, or run tests against production keys.
- Limits are token-bucket, with an `X-RateLimit-*` and `Retry-After` header on every response. Failures return 429 with a clear message.
- Org-level caps: max 5 sandbox accounts per org, and max 3 new accounts per IP/ASN/device per day. This is what blunts mass creation, not the per-request limit.
- Resource caps: objects created per day, stored objects, and webhook endpoints per account (for example 10,000 objects, 5 endpoints).
- Data lifetime: purge inactive T0/T1 sandbox data after 30 days of inactivity. Warn by email first.
- Self-service upgrade: a "request higher limits" form with a 1 business day response, plus an automatic bump to T2 on clean usage.
- Notify at 70%, 85%, and 95% of any daily cap, and say what to do.

## 4. Signup friction

- No visible CAPTCHA by default. Use an invisible, risk-based check (Turnstile or hCaptcha invisible mode). Show a challenge only on a risk signal: datacenter IP, disposable email, a velocity burst from the same ASN, or device fingerprint reuse.
- Require email confirmation before any API key is issued.
- Offer one-click GitHub signup. It raises trust and cuts friction.
- Don't require a credit card for sandbox. It would punish legitimate developers and hurt conversion.
- Measure friction: track signup-to-first-successful-API-call conversion before and after the change. Roll back any control that cuts it by more than 10% without a matching fraud reduction.

## 5. Monitoring

Dashboards and alerts:
- Sandbox: accounts created per hour per ASN, non-test PAN attempts, parameter-sweep score, 429 rate by tier, T0→T1→T2 funnel.
- Production: auth count and decline ratio per merchant, small-amount auth clusters, new-merchant first-week behavior, chargeback and dispute rate.
- Review queue: flagged clusters with evidence, reviewed weekly by security and growth together.

## 6. Rollout

1. **Week 1:** run the sandbox leak check (section 1) and the response-field audit (section 2). These decide how severe each problem is.
2. **Week 1–2:** ship the non-test-PAN rejection and logging, and the per-IP/org signup caps. Both are low risk.
3. **Week 2–3:** ship tiered quotas. Start in shadow mode: log would-be 429s for a week before enforcing.
4. **Week 2–4:** fix the sandbox data exposure. Add the production velocity and auto-pause rules. This is the part that actually reduces card testing losses.
5. **Week 4+:** turn on cluster detection and the response ladder. Review results monthly.

## 7. Position for the security lead

- Agree on the goal: sandbox must not be a free oracle or a free data source.
- Reframe: the sandbox answers "can a stolen card validate here?" with a flat no, so card testing moves to production, and that's where the rules go.
- A 10 req/min cap makes the product unusable without making the attacker's job harder. The attacker opens more accounts. Per-org and per-ASN caps address that.
- The security lead keeps a say: non-test PAN logging, auto-suspend, and the review queue are theirs.

## Open questions

1. Does sandbox ever touch real networks or issuer data? (Section 1 check.)
2. Which response fields expose fees, routing, or risk logic?
3. Is there a ToS clause against competitive analysis and scraping?
4. Which production merchants and flows are being card tested, and what is the current loss per week? That sets the priority of the production rules.

**Next action:** assign the section 1 leak check and the section 2 field audit to one engineer. Estimate about half a day each. Everything else in the rollout depends on their results.