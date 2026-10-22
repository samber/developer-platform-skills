# Verdict

🔴 **Don't ship the plan as written.** It has two independent faults:

1. **Same CA:** this can turn an external bug into an internal compromise. Fix it regardless of what else you decide.
2. **mTLS alone:** it doesn't cover the end-user "connect" integrations at all. Those need OAuth.

Keep mTLS as a client-authentication option for partner backends, on a separate PKI. Don't make it the whole design.

I haven't seen your code or mesh config, so I'm assuming a standard SPIFFE/SPIRE-style mesh CA. Items marked ❓ depend on facts I don't have.

# Holes, ranked

## 🔴 Critical

**1. Trust-domain collapse (same CA).**
- **Reverse direction:** if the public endpoint trusts the mesh CA, every internal workload cert is a valid external credential. One compromised pod can call the public API with an internal identity.
- **Forward direction:** if any internal service accepts "any cert chaining to the mesh CA" and checks the SPIFFE ID loosely, an external cert may authenticate internally. That's true if a partner can reach an internal listener, through SSRF, a misrouted LB, or a webhook-style callback.
- ❓ Check whether internal authZ is "chains to CA" or "exact SPIFFE ID allowlist". The first is common and would be catastrophic here.

**2. The issuance path becomes an internet-facing attack surface on your crown-jewel CA.**
- Onboarding 500 developers means an enrollment API or portal that can sign certs.
- A CSR or SAN-injection bug could mint `spiffe://oriflamme/…/payments`. That grants the attacker internal identity.
- The mesh CA has never needed to defend against hostile requesters. Its issuer is attested workloads only.

**3. mTLS authenticates a machine, not a user's consent.**
- The "user clicks connect and authorizes access to their own account" flow needs delegated authorization. That means:
  - consent
  - scopes
  - per-user, per-app tokens
  - revocation by the user
  - an "authorized apps" list
- A developer certificate says nothing about which user granted what. You'd end up inventing a token layer on top, so use OAuth 2.0 from the start.
- The browser never holds the developer's cert. At best, the integration's backend does the code exchange.
- Any public client (SPA, mobile app) can't hold a secret or cert at all. It needs Authorization Code + PKCE.

## 🟠 High

**4. Why it worked internally doesn't transfer.**

| Property | Mesh | 500 external devs |
|---|---|---|
| Issuance | Automated, attested workload | Human enrollment, identity unverified |
| Lifetime | Hours, auto-rotated | Developers must rotate by hand or in CI |
| Revocation | Unnecessary (short TTL) | Needed: CRL/OCSP, or an outage on every expiry |
| Client stack | Your gRPC, same libraries | Anything: curl, no-code tools, serverless, old JVMs |
| Network path | Direct, controlled | Corporate TLS-inspecting proxies, which break mTLS |

- Short TTLs cause external outages at 3 a.m. Long TTLs mean revocation becomes a real, untested system.
- Expect the support load of 500 PKI novices.

**5. Edge infrastructure conflict.**
- CDNs, WAFs, and cloud L7 load balancers usually terminate TLS. mTLS then means L4 passthrough, which loses WAF, bot, and DDoS protection.
- The alternative is forwarding the cert in a header. That's spoofable unless you strip and re-set it at exactly one trusted hop.
- The handshake is also unauthenticated CPU work for the attacker.

**6. Identity model mismatch.**
- A SPIFFE ID names a workload. An external identity needs to name a tenant → app → environment → key.
- "One cert per developer" fails for these cases:
  - multiple jobs
  - sandbox vs. prod
  - overlap during rotation
  - an employee who leaves with the private key
  - a key shared across a team
- Mapping the cert subject or DN to a developer record weakly invites confusion attacks (two devs with the same CN or SAN).

**7. Authentication is not authorization.**
- Cert-holders still need scopes, per-tenant isolation, quotas, and rate limits keyed to the client identity.
- mTLS does nothing against the real API threats: BOLA/IDOR, mass assignment, enumeration, abuse.

## 🟡 Medium

**8. Certificate validation footguns.**
- Mesh certs often carry both `serverAuth` and `clientAuth` EKUs. Enforce `clientAuth` and an issuing-CA constraint on the external path.
- Pin the allowed SAN format.
- The TLS CertificateRequest message advertises your CA's DN to the internet.

**9. Key theft is still replay.**
- A stolen key on a laptop or in CI secrets grants full access until you revoke. That's the same exposure as API-key theft, with heavier tooling.
- The gain is that the secret never crosses the wire. Sender-constrained tokens give you that too, at lower cost.

**10. Privacy and compliance for the user-delegated flows.**
- You need a consent record, per-user revocation, and an audit trail of which app accessed which user's data.
- A per-developer certificate gives you none of that.

# Recommended design

## Principle
Keep external and internal trust domains separate. Use standards that solve the actual problem for each case.

## A. Partner backend jobs (machine-to-machine)
1. OAuth 2.0 **client credentials** at your authorization server.
2. Client authentication, in order of preference:
   - `private_key_jwt`: the developer registers a public key or JWKS URL, with no PKI on your side.
   - mTLS per RFC 8705 `self_signed_tls_client_auth`: the developer registers a self-signed cert, so no external CA is needed.
   - mTLS with `tls_client_auth` against a **separate external CA**, offered only to partners who require it.
3. Access tokens live 5–15 minutes, are scoped, and are sender-constrained (cert-bound per RFC 8705, or DPoP).
4. Identity is per app and environment, with multiple registered keys for zero-downtime rotation.

## B. User-authorized integrations
1. **Authorization Code + PKCE**, with exact-match `redirect_uri` and `state`.
2. Consent screen with scopes that show the developer app's verified name.
3. Short-lived access tokens, with rotating refresh tokens and reuse detection.
4. Revocation endpoint, plus an "authorized apps" page where users can revoke.
5. Confidential clients (a backend does the exchange) authenticate as in A. Public clients rely on PKCE alone.

## C. Boundary with the mesh
1. The gateway validates the external token, then performs **token exchange** (RFC 8693) or mints an internal request context.
2. Internal services never see external certs or tokens. The gateway is the only external → internal translator.
3. If external workloads ever need mesh-style identity, use a **separate SPIFFE trust domain** that is never federated into the internal one.
4. The public endpoint trusts only the external CA pool and the authorization server's keys. It does not trust the mesh CA.
5. If you must reuse the PKI software, use a separate root and an offline-rooted intermediate with **name constraints**. The enrollment service must be unable to emit internal URI SANs.

## D. Cross-cutting
- Rate limits and quotas keyed on client ID, and on user ID for delegated calls.
- Object-level authorization checks tested per endpoint.
- Audit log: client, user, scope, and token ID on every call.
- A sandbox environment with separate credentials.
- Rotation and revocation runbooks, tested before launch.

# Rollout order

1. **Decide the trust boundary:** separate CA or no CA. This blocks everything else.
2. **Stand up the authorization server.** Use a proven product or library rather than writing your own. Start with client credentials plus `private_key_jwt`.
3. **Add Authorization Code + PKCE** with a consent UI and revocation.
4. **Add optional mTLS binding** for partners who ask for it.
5. **Pen test** the registration and consent flows, especially redirect URI handling and consent phishing.

# Questions that would change the answer

1. Is the public endpoint gRPC or REST? Browser-adjacent clients rule out gRPC unless you add gRPC-web or a REST facade.
2. Do any internal services authorize on "chains to mesh CA" rather than an exact SPIFFE ID allowlist? (If yes, #1 is worse than rated.)
3. Do you have an authorization server already (Keycloak, Ory, Auth0, an in-house one)?
4. Is there a compliance driver for mTLS, such as a partner or regulator asking for it by name?
5. Do any integrations run purely client-side (SPA or mobile)?