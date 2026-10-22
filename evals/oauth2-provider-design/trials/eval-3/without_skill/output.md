# DPoP on everything at launch: no. Ship a hardened bearer baseline and make DPoP opt-in.

## Verdict

Mandatory DPoP on every partner token is the wrong call for this launch.

- **Wrong cost.** You'd put a protocol most off-the-shelf OAuth client libraries don't support on the critical path of eight weeks of partner onboarding.
- **Wrong risk target.** The largest risk in your design is a hand-written authorization server, not bearer tokens.
- **Wrong data fit.** The data is employee directory and time-off records. That is real PII, but it has no payments or health data, and you have about 450 tenants.

The CISO has a real point. Sender-constrained tokens do reduce the damage from a leaked token, and DPoP is a published standard (RFC 9449). The case for it is sound. The case for requiring it on everything, now, is not. His line that bearer tokens are "a solved problem" also cuts the other way. Bearer plus the current security best practices (RFC 9700) is the well-understood, widely supported option. DPoP is the newer one.

## Why not mandate it

1. **Partner libraries.** Your partners are small ATS and payroll vendors on stock OAuth libraries. Many of those libraries have no DPoP support, or only partial support. Each partner would need to write proof generation, key management, `ath` hashing, nonce retry and `htm`/`htu` handling themselves. Expect onboarding to stall and support tickets to pile up. Directory launch dates usually slip on partner readiness, not on your own code.
2. **Your authorization server.** You wrote it yourself. DPoP adds server-side work:
   - proof validation;
   - a `jti` replay cache that works across instances;
   - server nonces;
   - `cnf.jkt` binding on access and refresh tokens;
   - exact URL normalization.

   Each of these is a place for a subtle bug, and a bug here weakens the control you added it for. Eight weeks is tight for hand-rolling this safely.
3. **Smaller benefit than it looks.** Your partners are mostly confidential server-side clients. If the DPoP private key sits in the same database or secret store as the token, one breach of that store gives the attacker both. DPoP only pays off when the key is non-extractable (HSM/KMS) or the leak is token-only (logs, proxies, a stolen refresh token in transit). Small vendors rarely have that setup.
4. **Proportionality.** A leaked directory or time-off token is bad, but it is bounded: no money moves and no health data is exposed. Short lifetimes, narrow scopes and fast revocation cap the damage at a much lower cost.

## What to ship instead (8-week plan)

### Weeks 1–3: Authorization server baseline (RFC 9700 and OAuth 2.1 profile)

- Authorization code with PKCE (S256) is required for every user-delegated flow. Remove implicit and password grants.
- Match redirect URIs exactly, with no wildcards.
- Send the `iss` parameter in authorization responses (RFC 9207) to stop mix-up attacks.
- Restrict audience with resource indicators (RFC 8707), so a token for the time-off API can't be replayed against another API.
- Use short-lived access tokens, 5–15 minutes. Prefer opaque (reference) tokens with introspection, because revocation is immediate.
- Rotate refresh tokens on every use. On reuse, revoke the whole token family. Set an absolute lifetime.

### Weeks 2–4: Client authentication and tenant model

- Server-to-server partners use `private_key_jwt` client authentication, not shared secrets. It is widely supported and removes the largest source of leaked credentials. Allow `client_secret_basic` as a fallback, with enforced rotation.
- Each customer's admin installs and consents per tenant, and can revoke at any time.
- Tokens are bound to one tenant and one partner app.
- Scopes are narrow and split by sensitivity, for example `directory:read`, `directory:read_sensitive`, `timeoff:read`, `timeoff:write`. Sensitive fields (birth date, home address) get their own scope.

### Weeks 3–5: Leak containment and detection

- Use recognizable token prefixes (for example `kh_at_`, `kh_rt_`). Register them with GitHub secret scanning so leaked tokens are revoked automatically.
- Never log tokens. Log a hash of each token and an ID.
- Rate-limit per token and per tenant. Alert on unusual volume, bulk directory export, or a sudden change of source IP or ASN.
- Offer an optional per-partner IP allowlist for customers who want it.
- Provide a customer-visible audit log of what each app accessed, and one-click revoke.

### Weeks 4–7: Verification

- Get an independent pentest of the authorization server before launch. This is the highest-value security spend, and it should come out of the DPoP effort.
- Alternatively, replace the custom pieces with a maintained, certified implementation. `node-oidc-provider` is a certified Node option and supports DPoP.
- Run your flows against the RFC 9700 checklist as a conformance test. Cover PKCE downgrade, redirect handling, refresh reuse, audience confusion and token endpoint client authentication.

### Weeks 5–8: Partner program terms

- Set minimum partner security requirements: TLS, encrypted token storage, a breach-notification window, and a short security questionnaire.
- Add tiers. Partners that request broader scopes (sensitive fields, bulk export, write) face a higher bar, including a review.

## Where DPoP fits

Build it as an opt-in feature rather than skipping it.

1. **Launch.** Support DPoP in the authorization server and advertise it in metadata (`dpop_signing_alg_values_supported`). Let a client register for DPoP-bound tokens. Partners with capable libraries or KMS-held keys can use it from day one. This is your "ahead of the curve" story, and it costs partners nothing.
2. **After launch.** Require DPoP only for the highest-risk scope classes (`directory:read_sensitive`, bulk export, write). Do that once the client library ecosystem supports it and you have measured partner adoption.
3. **Review at 6–12 months.** Revisit a blanket mandate with real adoption data.

If the authorization server is hand-rolled, I'd still wait to ship even the opt-in DPoP until the pentest covers it. A subtly broken DPoP check is worse than none, because it gives a false sense of safety.

## How to put it to the CISO

- **Same goal.** Limit the damage when a token leaks. The baseline above does that with short lifetimes, rotation with reuse detection, narrow scopes, secret scanning and instant revocation.
- **Lower cost.** It doesn't depend on every small vendor's library.
- **Not abandoning DPoP.** It ships opt-in at launch and becomes mandatory for sensitive scopes when the ecosystem is ready.
- **Better use of the budget.** The weakest link today is the self-written authorization server, so the pentest and RFC 9700 conformance buy more risk reduction than DPoP does.

## What would change my answer

- If partners include public clients (browser or mobile apps holding tokens), DPoP matters more. Move it up for those clients.
- If your largest customers' contracts or audits (for example a SOC 2 control or an enterprise security questionnaire) require sender-constrained tokens, mandate it for those scopes.
- If most committed partners already use a library with DPoP support, say Java or Node with a recent version, the cost argument weakens. Survey your first 10 to 15 partners before deciding.
- If the directory later adds payroll or health data, rerun this analysis. Sender-constraining would then be well justified.

I didn't see your authorization server's code or your partner list. Treat the library-support and effort claims as general industry patterns to check against your actual partners.