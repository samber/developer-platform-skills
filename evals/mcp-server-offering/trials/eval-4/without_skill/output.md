# Kestrel MCP server: pre-security-review design review

⚠️ **Verdict: don't start the security review on this design yet.** Fix the token passthrough first. It is the one decision that makes most of the other findings worse.

This is a review of the design as you described it. I haven't seen the code.

## Next actions

1. Replace token passthrough with audience-bound tokens plus token exchange (🔴 1).
2. Give background agents their own delegated credential, not a user's session token (🔴 2).
3. Verify the cache design: key it per user and re-check authorization on every read (🔴 3).
4. Answer the open questions at the bottom. The review team will ask them first.

## 🔴 Blockers

### 1. Token passthrough is a known anti-pattern

The MCP authorization spec explicitly forbids a server from accepting tokens that weren't issued to it, or forwarding them downstream.

- **No audience check.** Any valid Kestrel session token is accepted, whether it was minted for the web app, a mobile client, or something else. The MCP server can't tell "token meant for me" from "token stolen from elsewhere".
- **Confused deputy.** The internal analytics API sees the user's own token and can't tell the MCP server from the user's browser. It can't apply MCP-specific rate limits, scopes, or audit tags.
- **Larger blast radius.** The token works against all of Kestrel, not only analytics. A leak from the MCP server, the AI gateway, a log line, or a heap dump is a full account takeover for that user.
- **"Same token means same permissions" is a convenience, not a requirement.** You can keep that property without the risk (see the target design).

### 2. Session bearer tokens are the wrong credential for background agents

Interactive session tokens assume a human at a keyboard. Your agents are unattended.

- **Lifetime mismatch.** Sessions have idle and absolute timeouts, so you will either break long runs or be pushed to lengthen session lifetimes. Longer lifetimes are the wrong fix.
- **No least privilege.** The agent holds everything the user can do, including admin and destructive actions. An unattended agent that reads customer data is the textbook prompt-injection target, so the blast radius should be tiny.
- **No attribution.** Banks and insurers need to tell "user did X" from "agent acting for user did X" (model-risk, DORA-style third-party and audit duties). With a passthrough, the logs can't show it.
- **Credential sprawl.** The user's live session now sits in a third party's AI gateway: its config, logs, and traces.
- **The standard OAuth flow is interactive.** MCP's flow expects a browser consent step, and background agents can't do that. You need an admin-approved, non-interactive path.

### 3. Cache and sticky sessions can quietly break your authorization claim

"Permissions match exactly" holds only if every read is authorized as the calling user. In-memory workspace state undermines that:

- **Cache key.** Process-per-tenant stops cross-tenant leaks. Within a tenant, if the cache is keyed by workspace and not by user, user A's authorized read serves user B who lacks access.
- **Staleness.** After a role change, offboarding, logout, or token revocation, the process keeps serving cached state until it expires.
- **Session identity.** If the sticky key is the MCP session ID or a cookie, a stolen or guessed ID could resume someone else's session. The session ID is routing, not authentication. Validate the bearer token on every request, and bind the session to the token's subject.
- **Mid-session expiry.** Check token expiry and revocation per call, not only at session start.
- **Stickiness is an optimization, not a correctness dependency.** Pod restarts, deploys, and LB failover will drop sessions. A cold cache must be safe, only slower.
- **Memory.** Unbounded per-session caches are a DoS and memory-exposure risk (core dumps, swap, heap snapshots holding bank data). Set TTLs, size caps, and clear on logout.

## 🟠 High

### 4. Tenant binding

How does a request reach the right tenant process?

- **Routing from a trusted source.** If the LB routes on a header or hostname the caller controls, a misroute is possible. Route on a verified claim, or make the process refuse any token whose tenant claim differs from its own.
- **Enforce downstream too.** The analytics API should derive the tenant from the credential, never from a request parameter the MCP server supplies.
- **Check the process boundary.** Same host, same service account, and the same internal API credentials mean "process per tenant" is a convention, not a security boundary. Confirm separate identities and secrets per tenant, plus network policy.

### 5. Prompt injection through tool output

Analytics data includes user-controlled strings: dashboard names, event properties, comments, and query labels. With no human in the loop, a poisoned value can steer the agent into more reads or into exfiltration.

- **Narrow scopes per tool.** Default to read-only. Gate writes and exports behind separate scopes.
- **Cap volume.** Set row limits, export size limits, and per-agent rate limits. Bulk export is the exfiltration path.
- **Mark untrusted content.** Return data as clearly delimited data, and keep tool descriptions static and reviewed.
- **Query injection.** If tools accept filters or query text, validate them and enforce cost and timeout limits downstream.

### 6. The AI gateway is a party in your trust chain

It is customer-operated, but it sees every token and every result.

- **Don't rely on the VPC.** Customer traffic arrives over a network path you don't fully control. Use TLS everywhere, and mTLS or private connectivity if the customer can support it.
- **Authenticate the client app, not only the user.** Register the gateway or agent as an OAuth client with its own client credentials.
- **Redact credentials in your own logs, traces, and error reports.** Treat the `Authorization` header like a password.
- **Data residency and DLP.** Results flow into customer LLM context. Document what data classes can leave via tools, since banks will ask.

### 7. Audit, revocation, and kill switch

- **Audit record.** Per call: tenant, user, agent or client ID, gateway, tool, parameters (redacted as needed), result size, and correlation ID that continues into the internal API's logs.
- **Revocation.** Define how fast a revoked user or agent stops working, and how that reaches the cache. Aim for seconds to minutes, not session lifetime.
- **Kill switch.** Provide per-tenant and per-agent disablement, because banks will require it.

## 🟢 Lower priority

- **HTTP hardening.** Validate `Origin` and reject unexpected values (DNS rebinding). Disable permissive CORS. Set body size limits, request timeouts, and rate limits. Run behind a hardened Express config (`helmet`, trust-proxy set correctly for the LB).
- **SSRF.** If any tool fetches a URL, allow-list destinations and block the metadata endpoint and internal ranges.
- **Single point of failure.** One process per tenant means an outage is tenant-wide. Run at least two replicas, with the cache treated as best-effort.
- **Dependencies.** Pin and scan the MCP SDK and Express dependencies. This SDK is moving fast.
- **Secrets.** Internal API credentials come from a secrets manager with per-tenant scope and rotation.

## ✅ What's already good

- Process per tenant is a solid isolation start.
- Self-hosting in your own VPC keeps data in your control.
- Enforcing authorization in the downstream API is the right place. Keep it there, and don't re-implement permission checks in the MCP server.

## Recommended target design

1. **MCP server is an OAuth resource server.** It publishes protected-resource metadata (RFC 9728) and accepts only tokens whose audience is the MCP server (RFC 8707 resource indicators).
2. **Agents get their own credential**, not the session token. A customer admin approves an agent client once. It then obtains short-lived, narrowly scoped tokens non-interactively, on behalf of a named user or service identity, and supports refresh and revocation.
3. **Token exchange for the downstream call** (RFC 8693). The MCP server exchanges the incoming token for a short-lived analytics-API token with a narrower audience and scope. It carries the user as subject and the agent as actor (`act` claim). Downstream permissions still equal the user's, intersected with the agent's scopes.
4. **Cache rules.** Key by tenant and user (or authorize per read), apply TTL and size caps, invalidate on revocation, and make cold start safe.
5. **Validate the token on every request**, including tenant claim, audience, expiry, and revocation. Treat the session ID purely as a routing hint.

If the exchange path is too much for the first release, the minimum acceptable stopgap is: an audience-bound token for the MCP server, plus a distinct agent credential, plus per-call validation. That alone removes the worst of 🔴 1 and 2.

## Questions to answer before the review

1. What is the session token's lifetime, and how would a multi-hour background run stay authenticated today?
2. Is the cache keyed by user or by workspace? What invalidates it on permission change or logout?
3. What is the sticky-session key (cookie, `Mcp-Session-Id`, token hash)? Is it bound to the token subject?
4. How does the LB pick the tenant process? Does the process verify the tenant claim itself?
5. Does the internal analytics API support an audience-restricted or exchanged token, or only full session tokens?
6. Which tools write or export data? Are there per-tool scopes and volume caps?
7. What do the AI gateways store (logs, traces, prompt history) and who at the customer can read it?
8. What logging exists today, and does it redact `Authorization`?
9. Can you revoke a single agent or tenant within minutes?
10. Do customers have contractual requirements (data residency, subprocessors, audit-log export) that apply to this server?