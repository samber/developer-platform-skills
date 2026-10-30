**Verdict: ship (1). Rewrite (2). Change (3). Next action: delete the "skip OAuth" rule from the edge design today.**

I haven't checked the latest revisions of either draft. Verify the spec details below against the current text before you build.

## (2) Web Bot Auth as user permissions: reject

This is the blocking flaw. Fix it before anything else.

- Web Bot Auth builds on HTTP Message Signatures (RFC 9421). It proves which operator key signed the request.
- It does not prove that any user consented, and it does not say which user.
- One operator serves many customers and many employees. A valid signature carries no `sub`.
- Treating it as "the user's permissions" is a confused deputy. A known operator could then read any employee's salary or PII.
- There is no consent, no per-user revocation, no scope limit, and no audit trail of whose data was read.
- You are an HR API, so this is a GDPR exposure and a breach waiting to happen.

Use it for what it proves, which is the actor:

1. Verify the signature at the edge and treat the result as actor authentication. Use it for allowlisting, rate-limit tiers, and bot policy.
2. Still require the OAuth token for user authorization. Never accept a signature in place of one.
3. Bind the two together. Put the operator's key thumbprint in the token's `cnf` claim (like `jkt` in DPoP) and have the edge check that the signing key matches. A stolen token then fails without the operator's key.
4. Strip any internal "verified agent" header on inbound requests. Only the edge may set it.

Hardening for the signature itself:

- Require the covered components to include `@authority` and `@method`.
- Add `content-digest` for requests with a body.
- Cover `signature-agent` itself, or an attacker can swap the key directory.
- Require `created` and `expires` with a short window, plus a nonce replay cache.
- Require `tag="web-bot-auth"`.
- Fetch key directories with SSRF protection, a size cap, and caching. Pin the operator's allowed directory hosts at onboarding.

## (1) On-behalf-of draft with `requested_actor`: good, with guardrails

- The shape is right. The token has `sub` set to the user and `act` set to the agent, and the agent authenticates itself.
- It is an individual draft, not a standard. Pin the draft revision, feature-flag it, and document what you implement.
- Consider RFC 8693 token exchange with `act` as a fallback. That is standardized.
- Make effective scope an intersection: user permissions ∩ the user's grant to the agent ∩ the agent's registered scopes ∩ tenant policy. The agent should never get all of the user's permissions.
- Let the tenant admin allowlist agents and cap their scopes. Use field-level scopes for compensation, health, and national IDs.
- Cap delegation depth, so agent-calls-agent chains can't grow unbounded.
- Show users a grant list where they can revoke access.

## (3) 90-day agent tokens: reject, but keep the goal

Fleets breaking is a real problem, but a long access-token lifetime is the wrong fix.

- An employee is terminated or changes role. A 90-day JWT keeps acting with old rights for up to 90 days.
- Agents leak tokens into logs, prompts, and via prompt injection. A leaked 90-day bearer token is a 90-day breach.

Do this instead:

1. Set access tokens to 5–15 minutes.
2. Use rotating refresh tokens with sender constraint (DPoP, mTLS, or the Web Bot Auth key). Issue one per agent instance, never one shared across a fleet.
3. Put 90 days on the grant, not the token. It can be an absolute grant lifetime with re-consent, or an idle timeout, so fleets run unattended.
4. Revoke on events. You own the HR data, so you know when an employee is terminated or changes role. Emit those events (Shared Signals / CAEP style) and kill the grants immediately.
5. Use introspection or a revocation list for high-risk scopes.

Fleets then renew silently and do not break, and a termination takes effect within minutes.

## Test client and `Signature-Agent`

- The dictionary form is a real change from the older plain-string form. As I recall, the newer draft keys the member to the signature label and covers it as `"signature-agent";key="sig1"`. Confirm against the current text.
- Your test client only proves that your client and your verifier agree with each other.
- Real operators and CDNs may still send the string form. Accept both during the transition, and add conformance tests for each form and for the draft's published test vectors.
- Add negative tests: header not covered by the signature, expired signature, replayed nonce, unknown key directory, and a swapped `Signature-Agent`.

## Questions to answer before coding

1. Does the agent act only for logged-in employees, or also for HR admins? Admin delegation needs a stricter policy.
2. Are agent operators registered per tenant, or global? That changes who approves them.
3. Which fields need per-request user step-up (CIBA or re-consent)? Compensation is the obvious one.

**Next:** rewrite (2) as "Web Bot Auth = actor authentication, bound to the token via `cnf`", then confirm the access and refresh TTLs for (3).