# DPoP before launch? No. Ship a hardened bearer baseline and make the AS DPoP-ready.

**Recommendation:** Don't make DPoP a launch gate. Ship a hardened baseline (RFC 9700 profile, short-lived tokens, rotating refresh tokens, audience binding, fast revocation, an AS pentest). Add DPoP as an opt-in, per-client capability, then make it mandatory for high-risk scopes once partner libraries support it.

I haven't seen your AS code or surveyed your partners' stacks. Verify the assumptions flagged below.

## Why not DPoP-everywhere in 8 weeks

1. **You'd be hand-writing the hard part.** A custom Node AS must implement:
   - proof validation (`typ`, `alg`, `htm`, `htu`, `iat`, `ath`) and `cnf.jkt` binding;
   - server nonces;
   - a `jti` replay cache. This must be shared and fast across instances, which is new infrastructure.
   - Every resource server endpoint must then enforce it. Gateways, CDNs and proxies that rewrite URLs break `htu` matching, and this is a common failure.
2. **Partners are your weakest link.** Small ATS and payroll vendors on off-the-shelf OAuth libraries will hit one of two outcomes:
   - Their library lacks DPoP, so they must write proof signing and nonce retry logic themselves. Expect bugs and support tickets.
   - They push back, and your directory launches thin.
   
   Library support has been improving, but check the specific libraries your partners use. Ask 10 prospective partners which they use and whether it supports DPoP.
3. **The benefit is smaller for your clients.** Most partners are server-side confidential clients. DPoP matters most for public clients, such as browser and mobile apps, where tokens are easiest to steal. For confidential clients, the main risks are leaked tokens in partner logs or databases and compromised client secrets. DPoP covers only the first, and only if refresh tokens are bound too.
4. **The biggest risk is the home-grown AS itself.** Custom authorization servers fail through redirect URI matching, PKCE downgrade, refresh reuse and token confusion. Sender-constraining tokens does nothing for those flaws.
5. **Cost of a launch slip.** A late or broken launch, or a partner exodus, costs more than the marginal risk reduction, given the sensitivity below.

## Data sensitivity: don't undersell it

"No payments, no health records" is not "low risk."
- **Directory data:** it is bulk PII (names, emails, org structure) for about 450 customers, which makes it valuable for phishing and social engineering.
- **Time-off data:** leave types can reveal medical or parental leave, so they are sensitive even though you hold no health records. Split these into separate scopes.
- **Hardening level:** treat the partner API as holding sensitive PII, and don't treat it as a toy.

## What to ship instead (launch baseline)

**Authorization server**
1. Authorization code flow with PKCE (S256) is mandatory. Remove implicit and password grants.
2. Use exact-match redirect URIs. No wildcards.
3. Access tokens live 5–15 minutes.
4. Refresh tokens rotate on every use, with reuse detection that revokes the whole grant family, plus an absolute lifetime.
5. Confidential clients authenticate with `private_key_jwt` (preferred) or `client_secret_basic`. Support secret and key rotation. Store secrets hashed.
6. Bind each token to an audience (RFC 8707 resource indicators or `aud`) and to the customer tenant.
7. Store opaque tokens hashed at rest. If you use JWTs, follow RFC 9068.
8. Publish AS metadata (RFC 8414).
9. Add token revocation (RFC 7009) and introspection.

**Authorization model**
1. Scopes are least-privilege and read-only by default.
2. Split scopes: `directory:read` (limited fields), `directory:read.sensitive`, `timeoff:read`, `timeoff:read.types`, and a separate scope for bulk export.
3. The customer's admin approves each app per tenant.
4. Add a per-tenant **revoke app** button and a platform-level **kill switch** per app.

**Detection and response**
1. Keep an audit log per customer: which app, which scope, what volume.
2. Rate-limit per client and per tenant. Alert on bulk-read anomalies.
3. Send customer-visible notifications on new grants.

**Partner program (directory)**
1. Run a lightweight security review before listing: TLS, secret storage, incident contact, data retention.
2. Include a contractual breach-notification clause.
3. Provide a reference client in Node, Python and Java showing the correct flow.

**Assurance**
1. Run an independent pentest of the AS before launch (about 2–3 weeks of lead time). Make this a launch gate.
2. Run the AS against an OAuth security checklist (RFC 9700) and a conformance suite.
3. Consider replacing the custom AS core with a certified implementation. For example, `node-oidc-provider` is OpenID-certified and has DPoP support. A migration in 8 weeks is risky, so decide this by week 2, and default to keeping the current AS if it passes the pentest.

## DPoP-ready, not DPoP-required

Build these now so the capability can be switched on later:
- Per-client registration flag `dpop_bound_access_tokens`.
- AS accepts `DPoP` proofs and issues `cnf.jkt`-bound tokens when a client opts in.
- Resource server enforces the binding for any bound token.
- Advertise `dpop_signing_alg_values_supported` in metadata.
- Shared `jti` replay store (for example Redis with TTL) and server nonces.

If the build looks too large for the 8 weeks, ship the metadata and token format hooks only, and implement enforcement in the following quarter.

## Triggers to make DPoP required

- High-risk scopes (bulk export, sensitive time-off types) once the bulk of partners' libraries support it.
- An enterprise customer contractually requires it.
- A real token-leak incident or a pattern in the anomaly data.
- Your top 10 partners' libraries support it natively.

## Eight-week plan

| Weeks | Work |
|---|---|
| 1 | Threat model with the CISO. Survey partner libraries. Decide keep-vs-replace AS. |
| 1–3 | Baseline AS hardening (PKCE, refresh rotation, audience, scopes, revocation). |
| 2–4 | Audit log, rate limits, anomaly alerts, admin revoke UI, kill switch. |
| 3–5 | Reference clients, partner docs, partner security review checklist. |
| 4–6 | DPoP opt-in implementation behind a flag, with replay store. |
| 5–7 | Independent pentest. Fix findings. |
| 8 | Launch with a limited cohort of vetted partners. |

## How to frame it with the CISO

His direction is right, and the question is sequencing. I'd say it like this:
- "DPoP is on the roadmap and the AS will be built to support it. Making it mandatory today shifts the risk from token theft to broken integrations and a delayed launch, and the biggest exposure is a custom AS that hasn't been independently tested."
- Show him the table of threats against controls: token in partner logs (short TTL, audience, revocation, anomaly alerts), stolen refresh token (rotation and reuse detection), AS flaws (pentest).
- Offer the trigger list above as the explicit path to DPoP-required, so it's a decision with criteria and not a refusal.

**Next step:** run the partner library survey and the threat-model session this week. Those two results decide whether DPoP enforcement slides into the launch scope or stays post-launch.