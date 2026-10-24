# Agent identity and delegation

Contents: two questions, standards status, operator identity, delegated authority, credential model, provision-then-claim, anti-patterns.

## Two questions, never one

- **Who sent this request?** Operator identity: which company's agent, verified cryptographically or by IP.
- **On whose authority does it act?** Delegation: which user granted what, for how long.

A signed request answers the first only. Web Bot Auth explicitly excludes authorization and delegation. Never attach user permissions to a signature.

## Standards status

Re-check drafts before committing; versions below are the last known state.

| Item | Status | Use |
| --- | --- | --- |
| RFC 9421 HTTP Message Signatures | final | base of agent request signing |
| Web Bot Auth (`draft-ietf-webbotauth-httpsig-protocol`) | IETF working-group draft, adopted September 2026 | verify operator identity; expect changes |
| RFC 8693 Token Exchange | final | on-behalf-of tokens, actor chain in the `act` claim |
| RFC 8628 Device Authorization Grant | final | CLI and headless agent login |
| RFC 9728 Protected Resource Metadata | final | lets an agent discover how to authenticate |
| OAuth 2.1 | working-group draft | the profile MCP authorization builds on |
| Identity assertion grant, transaction tokens | working-group drafts | enterprise agent fleets; watch, do not depend |
| Agent-specific OAuth profiles (individual drafts) | individual or expired | borrow their rules, never their wire format |

One expired example: the on-behalf-of-user draft expired in early 2026. Its `requested_actor` parameter has no successor. `actor_token` itself comes from RFC 8693 and stays safe inside a token-exchange grant.

## Operator identity

- Accept verified agents through your CDN's verified-bot or signed-agent category, or verify signatures yourself.
- Signature rules from the draft: key id is a JWK SHA-256 thumbprint, `tag` is `web-bot-auth`, signatures expire within 24 hours, and an unresolved `Signature-Agent` is "a claim rather than an identity" until a fetched key verifies it.
- Known interop issue: Cloudflare's verifier implements an earlier `Signature-Agent` header form and rejects the dictionary form of later drafts. If you operate an agent, test signing against both.
- Fallback: vendor-published IP lists for crawler and fetcher tokens.

## Delegated authority

Rules, each with the reason:

1. Issue each agent its own credential, never the human's. Revoking one agent must not log the human out. A coding agent driving the user's locally logged-in CLI is the one place this fails: it inherits the human's per-install session, including its refresh token. Bound that session with refresh-token rotation, an absolute lifetime and the narrowest scopes the CLI needs, list it as an exception, and attribute its calls by env-var tagging. Per-agent revocation is impossible on this path.
2. Scope the agent token no broader than the user's grant, and narrower where the job allows. An agent needs the workflow's scopes, not the account's.
3. Keep agent tokens short-lived and never longer-lived than the user token they derive from. A leaked agent context then expires on its own.
4. Bind the token to the agent instance (sender-constrained, for example DPoP or mTLS) where the client supports it. A token copied out of a transcript then fails.
5. Name a sponsoring human for every agent credential. Someone must answer for what it does, and revoke it.
6. Record the actor chain (`act`) so logs show "agent X for user Y". Audit and abuse response need both names.
7. Give CLIs and headless agents the device grant: the agent prints a code, the human approves in a browser, no password reaches the agent.
8. Put irreversible or money-moving actions behind a human approval the agent cannot answer itself. The approval must travel out of the agent's channel: a push, email or second device, never a confirm button in the session a browser agent is driving. A `pending_approval` state the user confirms elsewhere works today; backchannel standards have no proven agent deployment.

Hand formats, scopes and rotation to `samber/developer-platform-skills@api-auth-key-management`; grant flows and consent to `samber/developer-platform-skills@oauth2-provider-design`.

## Credential model template

| Field | Value |
| --- | --- |
| Agent class | coding agent / browser agent / fleet |
| Identified by | credential, signature, IP list |
| Authority | own (autonomous) or user's (delegated) |
| Credential | agent-labelled key, delegated access token, device-grant token |
| Scope | named scopes |
| Lifetime | hours or days for delegated tokens, never "until revoked"; fleets mint short tokens from client credentials or workload identity federation (details: `samber/developer-platform-skills@api-auth-key-management`) |
| Sponsor | the human accountable |
| Revocation | per agent, from the user's settings |
| Approval gate | which actions need a human |

## Provision-then-claim

The working agent-signup pattern: the agent creates a resource without an account, gets credentials and a claim link, and a human claims it later.

Shape:

1. One unauthenticated call creates the resource and returns connection details, a `claim_url` and `expires_at`. The claim URL is single-use, expires with the resource, works only after the human logs in or signs up, and never acts as a session.
2. Unclaimed resources expire (one vendor uses 72 hours) and run under quotas small enough to make abuse unprofitable.
3. Operations that need a human return a named error (for example `capability_requires_claim`), never a generic 403.
4. Claiming moves state through unclaimed, claiming, claimed; it revokes pre-claim tokens and rotates credentials.
5. The claim lands the resource in the human's normal account and billing.
6. In products that move money, unclaimed resources run in test or sandbox mode only. Live mode starts at claim.
7. Terms of Service and any data processing agreement are accepted at claim. Unclaimed resources hold no personal data.

A CLI signup command can run the device grant against a new-account page instead, when the product needs an account before any resource exists.

Abuse controls to design in the same pass: per-IP and per-signature creation caps, no outbound network or email from unclaimed resources where abuse would use them, and a kill switch.

## Anti-patterns

- Agents automating the human signup form and solving CAPTCHAs.
- A session secret passed in a query string so an agent browser can set it.
- One shared "AI integration" key per customer, so no action traces to an agent or a human.
- Trusting a self-declared agent header as authority to skip a check.
