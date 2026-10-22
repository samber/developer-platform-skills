# Security design: Oriflamme external API

## Verdict

**Reject the plan as the primary mechanism.** Keep mTLS and SPIFFE inside the mesh, where they work. Put OAuth2 at the public edge, and treat client certificates as an optional extra for a few high-trust partners, issued from a separate CA.

I couldn't ask the skill's clarifying questions, so I assumed the following. If any is wrong, the affected section changes.

| # | Assumption | Effect if wrong |
|---|---|---|
| 1 | gRPC is already internal, so the service definitions likely contain admin and debug RPCs. | If greenfield, the exposure audit is lighter. |
| 2 | Consumers are a mix of partner backends and a browser "connect" flow. | If every consumer is SDK-mediated, raw public gRPC becomes viable. |
| 3 | Browsers are involved in the connect flow. | If they aren't, "Connect-RPC" below can become "raw gRPC edge plus HTTP alongside". |
| 4 | You have no strong constraint on the REST surface. | A mandatory REST surface favours the Envoy transcoder or grpc-gateway. |

## Holes in the plan

Ordered by severity.

### 🔴 1. It cannot express the end-user case

- A client certificate identifies a developer's workload. It says nothing about a user who clicked "connect" and consented to specific access to their own account.
- Those integrations need delegated authorization: consent, per-user scopes, refresh, and user-initiated revocation. mTLS has none of these.
- The correct flow is Authorization Code + PKCE (RFC 7636).
- You would have to bolt on OAuth2 anyway. That leaves two auth systems, with mTLS doing the job it is worst at.

### 🔴 2. Sharing the mesh CA puts the internal trust boundary at risk

- Every certificate you hand out chains to the root your internal services trust.
- If any internal verifier checks only the chain, or checks SAN patterns loosely, an external key becomes a path into the mesh.
- A leaked developer key is then a credential under your root. Developers will leak keys: laptops, CI logs, public repos.
- The issuing service becomes internet-facing and holds signing power over the mesh trust domain. That makes it a high-value target.
- Even without a trust-bundle mistake, SPIFFE ID namespacing must be airtight. A developer-influenced SAN or CSR field is a squatting risk.

### 🔴 3. Authenticated is not authorized

- mTLS answers "who is this connection". It does not answer "may this caller invoke this RPC on this object".
- The skill's step 7 requires method-level scope enforcement. A certificate has no scopes.
- Mesh authorization policy is usually "any workload in the trust domain". External identities that inherit it get far too much access.
- Cross-tenant object access (BOLA) needs a subject or tenant claim checked against the resource. A certificate gives you connection identity only.

### 🟠 4. Revocation and rotation at 500 unknown parties

- CRL and OCSP are rarely enforced reliably in gRPC stacks.
- The honest alternative is short-lived certificates with automated issuance. That means building ACME-like or CSR-signing infrastructure, which is an identity provider by another name.
- Each developer needs to generate keys, manage expiry, and configure TLS correctly in their language. Expect an onboarding drop-off and a permanent support queue.
- Offboarding is awkward. A certificate per developer doesn't map to teams, environments (sandbox vs prod), several apps per developer, or employee turnover.

### 🟠 5. It conflicts with the edge you need

- An edge that does WAF, L7 HTTP/2-aware balancing, rate limiting and token checks terminates TLS. Client-certificate identity then has to be forwarded in a header.
- Forwarded identity headers are spoofable unless every ingress path strips them.
- Partners behind TLS-inspecting corporate proxies, and any CDN or managed load balancer that terminates TLS, will break end-to-end mTLS.

### 🟠 6. mTLS does not close the exposure hole

- Admin, debug and monitoring RPCs, and server reflection, are reachable by every certificate holder. The skill's exposure audit exists because TLS and auth do not close this.
- With 500 holders, the exposed surface equals the entire service definition unless the gateway allowlists methods.

### 🟡 7. The caller's identity disappears at the first hop

- Behind the edge, the mesh sees your gateway's SPIFFE ID, not the external caller.
- Downstream services need a verified claim set: client_id, user, scopes, tenant. You must design that propagation anyway.
- Done carelessly it becomes a confused-deputy risk. Raw external tokens must not be forwarded internally.

### 🟡 8. Three years without incident is weak evidence

- You control both ends internally. Identities are known and rotation is automated.
- None of that holds for 500 developers you've never met.

### 🟡 9. No quota attribution

- Certificates don't give you a per-project handle for quotas and coarse gating.
- That is the job of API keys or client_ids, which complement authentication.

### ✅ What the plan gets right

- Strong, early rejection of unauthenticated connections is a real DoS and abuse benefit.
- Key-bound credentials are phishing-resistant compared with bearer secrets.
- You can keep both properties without the downsides, as shown in section 5 below.

## Recommended design

Skill order: gate, then edge, then auth, then audit.

### 1. Gate: what the edge speaks

- Keep gRPC internal. The public edge is **Connect-RPC**, the skill's default rung.
- The browser connect flow rules out raw public gRPC as the only surface.
- One server speaks Connect, gRPC and gRPC-Web, so partner backends can still use native gRPC.
- If Envoy is already your mesh data plane and a second runtime is the real cost, use the Envoy gRPC-JSON transcoder instead. Set `convert_grpc_status: true` and include all error-detail types in the descriptor.
- Use unary RPCs by default, and enable the buf `UNARY_RPC` lint unless streaming is genuinely needed.

### 2. TLS

- Use one-way TLS with a public CA certificate, TLS 1.2 minimum and 1.3 preferred.
- Credentials travel as metadata, so never allow plaintext.
- Use L7 HTTP/2-aware balancing at the edge.
- Set client keepalive below the balancer idle timeout (vendor defaults as of 2026, reverify before quoting):

  | Balancer | Idle timeout |
  |---|---|
  | AWS ALB | 60 s |
  | AWS NLB | 350 s |
  | GCP external Application LB | 600 s |

### 3. Authentication by caller type

| Caller | Flow | Notes |
|---|---|---|
| Partner backend job | OAuth2 Client Credentials | Authenticate the client with `private_key_jwt`, not a shared secret. |
| End user "connect" | Authorization Code + PKCE | Consent screen, per-scope grants, refresh-token rotation, revocation endpoint (RFC 7009), user-visible "connected apps" page. |
| Project identification | API key | Quota attribution and coarse gating only. It is never an identity. |

- Use an established identity provider rather than a hand-rolled issuer.
- Access tokens should be JWTs signed with RS256 (JWT access-token profile, RFC 9068). Required claims are `exp`, `aud`, `iss`, `sub`, `client_id` and `scope`. Lifetime should be 5 to 15 minutes, with `aud` validated against Oriflamme's API.
- Rotate the JWKS and cache it. Use introspection (RFC 7662) with a cache for anything that needs immediate revocation.
- Short token lifetimes are your revocation story. This replaces the CRL problem from hole 4.
- Follow the OAuth security BCP (RFC 9700).

### 4. Authorization

- Keep an RPC-to-scope table, for example `oriflamme.orders.read` for `GetOrder`. Enforce it in a server interceptor or at the gateway on every method, with a default of deny.
- Check ownership as well as scope. Compare the token's `sub` or tenant against the resource owner, so one valid token cannot read another tenant's objects.
- For a token issued to a user, authorize against the user's grants, not the client's full capabilities.

### 5. Optional: certificates for a few high-assurance partners

- Make it opt-in, only where a partner asks.
- Use a **separate CA hierarchy and trust domain**. Never include it in a mesh trust bundle. Constrain the URI SAN and name space, and never accept an external SPIFFE ID.
- Bind it to OAuth rather than replacing it: mTLS client authentication at the token endpoint and certificate-bound access tokens (RFC 8705). DPoP (RFC 9449) is the lighter alternative.
- Terminate it at an edge that supports it, not behind a TLS-terminating CDN.

### 6. The boundary with the mesh

- The gateway validates the token, enforces scope, and rate-limits. It then calls the mesh over normal mTLS with its own SPIFFE identity.
- The gateway strips every inbound identity and authorization header. It mints a short-lived, signed internal context (client_id, user, tenant, scopes) for downstream services. Internal services must trust only that context, never raw external tokens.
- External callers never receive SPIFFE identities.

### 7. Rate limiting and errors

- Limit per client_id and per user.
- Return `RESOURCE_EXHAUSTED` (429 when transcoded) with a `RetryInfo` detail.
- Use `UNAUTHENTICATED` for a missing or invalid token and `PERMISSION_DENIED` for a missing scope.
- Strip `DebugInfo` from error details before they leave the edge. Sanitizing `message` alone is not enough.
- Document that the HTTP status line is lossy, because `INVALID_ARGUMENT`, `FAILED_PRECONDITION` and `OUT_OF_RANGE` all become 400. The body envelope is the source of truth.
- Use a deliberate mapping on the server, not the client-side gRPC-to-HTTP table.

### 8. Exposure audit (mandatory, before launch)

1. Disable server reflection on every publicly reachable listener.
2. Enumerate every service and method in the internal definitions.
3. Publish through an **allowlist**. The gateway routes only listed methods. Admin, debug, health and monitoring RPCs are not reachable from outside.
4. Where practical, publish a separate public proto package rather than the internal one.
5. Run `buf breaking` (FILE category) plus a diff of the `google.api.http` annotations in CI. buf does not inspect those annotations.

## Pass gates before launch

- ✅ A token with the wrong `aud`, an expired `exp`, or a missing scope is rejected on every public method.
- ✅ A valid token for tenant A cannot read tenant B's resource.
- ✅ A gRPC reflection request (for example `grpcurl` list) against the public hostname fails.
- ✅ Calling an internal-only method through the edge returns a not-found style error.
- ✅ A client cert signed by the external CA is rejected by every internal service.
- ✅ Forged `x-forwarded-*` or identity headers from outside are stripped.
- ✅ A user can revoke a connected app, and its access fails within one token lifetime.
- ✅ Rate-limit responses carry `RetryInfo`.
- ✅ Error responses contain no `DebugInfo`.

## Open decisions for you

1. Which IdP: build, buy, or reuse the one you already run?
2. Does any partner contractually require mTLS? If so, section 5 applies to them.
3. Is Envoy already your data plane? That decides Connect-RPC vs the Envoy transcoder.
4. Should the exposed API be a separate public proto package, or an allowlist over the internal one?

I'd decide 4 first, because it shapes the audit.