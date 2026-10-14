# Kestrel Analytics MCP server: design review before the security review

**Verdict: not ready for security review.** Two findings fail the skill's own auth gates, and one of them is a spec MUST violation. The rest can be fixed on the same pass. I reviewed the design as you described it. I haven't seen the code or the tool list.

## Gate status

| Gate | Status | Why |
|---|---|---|
| Auth conformance | ❌ Fail | Bearer passthrough; audience validation and protected-resource metadata unconfirmed |
| Safety coverage | ⚠️ Can't assess | No tool list or risk tiers given |
| Curation (5-15 tools) | ⚠️ Can't assess | Same |
| Evidence hygiene | ✅ n/a | No business case supplied |

## Blockers

### 1. ❌ Passing the caller's session token to the internal API is forbidden

The MCP spec forbids forwarding a caller's bearer token upstream. It is the confused-deputy shape. In your setup it causes these problems:

- **No audience binding.** A Kestrel session token isn't minted for this MCP server. The server has no way to reject a token meant for something else, and no way to stop a token captured here from working against the main product. Banks' reviewers will ask about this first.
- **The token travels further than it should.** It crosses the customer's AI gateway, sits in your Express request logs and in any APM, and then reaches the internal API. A session token usually grants far more than analytics reads, so one leak gives the whole session.
- **Attribution is lost.** The internal API sees "Alice", never "Alice via agent X, session Y". For unattended agents in regulated shops, that audit trail is the main thing they will ask for.
- **Lifetimes don't fit background agents.** Interactive session tokens expire and get revoked. Long-running agents either break or get long-lived session tokens, which is worse.

**Fix, keeping your "permissions match exactly" goal:**

1. Make the MCP server an OAuth 2.1 resource server. It validates tokens and never mints them.
2. Publish protected-resource metadata (RFC 9728). Require resource indicators (RFC 8707) and reject any token whose audience isn't this server. Validate the issuer (RFC 9207).
3. Call the internal analytics API with your own upstream token, obtained through token exchange (RFC 8693). Use the validated user token as `subject_token` and the MCP server's client identity as the actor.
4. Have the internal API enforce the exchanged token's permissions. The user stays the principal, so permissions match exactly. The `act` claim adds agent and session attribution.

The extra plumbing is a token-exchange endpoint on your authorization server. The authorization-server design is `oauth2-provider-design` territory. Here you only need the resource-server side.

### 2. ❌ Sticky sessions plus in-memory workspace cache

Two separate problems:

**Security: the cache can bypass permissions.** Your "permissions match exactly" claim holds only if each call is authorized against the caller. If the cache holds workspace state fetched under one user's permissions, a second user in the same tenant can read it on a cache hit. Check what the cache keys on. If it's tenant or session, it can leak data across users or roles. Revoked or changed permissions also don't take effect while the entry lives.

**Architecture: stickiness is the wrong baseline.** The 2026-07-28 spec revision is stateless. Every instance should be interchangeable behind a plain load balancer.

Pinning breaks in practice:
- Customer AI gateways may not preserve your LB cookie or affinity.
- A restart or failover silently loses state.
- Session identity gets mistaken for authentication.

**Fix:**
- Treat the cache as a pure performance cache that can always be rebuilt. No tool result should depend on landing on the same instance.
- Key every entry by (tenant, principal or permission set). Re-check authorization on every call. Cache only permission-neutral data, or invalidate on permission change.
- Set a TTL, and set it shorter than the token lifetime.
- If cold-start cost hurts, move the state to a per-tenant external store (for example Redis, encrypted, in the VPC), not process memory.
- Drop the sticky-session requirement at the LB. Test by killing a process mid-run and confirming results stay correct.

## High-priority findings

3. 🟠 **Tenant binding.** One process per tenant is a good isolation choice. Enforce it. The token's tenant claim must equal the process's tenant, and a mismatch must be rejected, not just mis-routed. Test with a valid token from tenant B sent to tenant A's process.

4. 🟠 **Unattended agents need server-side controls.** Your customers run background agents through their own gateway, so the skill's "enterprise agent fleets" profile applies. Client-side prompts and tool annotations won't protect you there. Design for this profile:
   - Per-credential and per-tenant rate limits.
   - Query cost and size caps: row limits, time-range limits, timeouts, pagination with cursor and `limit` (default 20-50). An unbounded analytics query is your equivalent of the "endlessly closing tickets" incident.
   - Attribution and asynchronous audit on every call: user, agent client, session, tool, parameters (scrubbed), tool-surface version.

5. 🟠 **Tool surface and risk tiers are unspecified.** Send the list. For an analytics product I expect read-only to be enough at launch (Stage 1). If any write tool exists (saved queries, exports, scheduled reports, sharing), it needs exactly one risk tier and a named safety pattern. Exports and sharing are data-exfiltration paths even though they aren't destructive, so tier them as Contained Write or higher. Mirroring your API endpoints is the main failure mode here. Aim for 5-15 workflow-level tools with prefixed names like `kestrel_run_query`, and write the descriptions carefully.

6. 🟠 **Prompt injection via data.** Analytics results can contain attacker-controlled text: event properties, dimension values, free-text fields. In a bank, an agent with both read access and an export or send tool is the exfiltration chain. Return results as data. Keep untrusted strings out of tool descriptions, and sanitize description content. Bound result sizes.

## Medium findings

7. 🟡 **Revocation and token lifetime.** Define what happens when the user's access is revoked mid-run. Use short-lived upstream tokens, a TTL on cached state, and a re-validation point per call, not per session.

8. 🟡 **Hosting choice.** The skill's default is a managed platform. Self-hosting in your VPC is the "starved option", and your case justifies it: regulated customers, residency expectations, per-tenant isolation, and a custom policy layer you must run yourself. Accept the cost knowingly. It means months to production-grade plus standing maintenance, and you absorb spec churn (four breaking revisions in 20 months) and the OAuth machinery yourself. Pin SDK versions.

9. 🟡 **Gateway interoperability.** Banks front you with their gateway. Support:
   - Stable tool names and request IDs for correlation.
   - OpenTelemetry spans (session → tool call → downstream operation) that flow into their stack.
   - Accurate registry metadata, because large customers mirror it into private allowlisted catalogs.
   - No dependence on client cookies.

10. 🟡 **Hardening floor.**
    - Schema-validate every input and bound sizes and ranges.
    - Sanitize paths.
    - Return tool errors inside the result with actionable messages. Never leak stack traces or internal hostnames.
    - Strip `Authorization` from logs.
    - Origin validation applies to local HTTP servers only. It's not your main risk on a remote deployment.

11. 🟡 **Versioning and tests.** A tool-description change alters which tool agents pick, so treat it like a code change. Add golden-prompt CI, hash the full surface (names, descriptions, schemas), log a surface-version marker on each call, and give deprecations at least 90 days.

## Recommended order

1. Replace token passthrough with the validate-then-exchange flow (blocker 1).
2. Rework the cache: per-principal keys, per-call authorization, stateless instances, no LB stickiness (blocker 2).
3. Enforce the tenant claim against the process tenant.
4. Add read-only lockdown. **Test that write tools are actually absent**, since a documented GitHub bug shipped write tools despite the flag.
5. Add rate limits and query caps, then attribution and audit.
6. Run the security review on the corrected design.

Stage gates after launch: Stage 1 (read-only) moves on once real-agent call volume is sustained and tool error rate is under 2%. Treat that 2% as a default to calibrate, not an industry standard. Stage 2 (writes) only after a clean audit trail and zero unattributed writes.

## Questions that would change the design

1. **Tool list:** which tools exist, and are any of them writes (exports, saved queries, sharing)?
2. **Authorization server:** does Kestrel already run an OAuth 2.1 authorization server that can support audience-restricted tokens and token exchange? If not, this MCP project becomes its first consumer.
3. **Demand:** have banks or insurers asked for MCP in RFPs or security questionnaires? A hard RFP deadline would push toward a managed platform and a read-only launch. No demand after two quarters means maintain it as table stakes.
4. **Cache contents:** what does the cached workspace state hold, and does it vary by user permission? If it's permission-neutral and rebuildable, the fix is much smaller.
5. **Agent identity:** do your customers' gateways authenticate as a user (delegated) or as a service identity? That decides whether token exchange uses user delegation or a service principal with an actor claim.