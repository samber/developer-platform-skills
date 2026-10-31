# Quarrystone agent plan: verdict on the three-part design

**Verdict:** ❌ Don't ship the plan as written. Items 1 and 2 build on a premise that doesn't hold, and item 3 breaks the credential lifetime rules. The goal (customer agents acting for employees) is right. The fix is mostly a different mechanism for each item.

| # | Your plan | Verdict | Replace with |
| --- | --- | --- | --- |
| 1 | `requested_actor` from the on-behalf-of draft | ❌ | RFC 8693 token exchange with `actor_token` and an `act` claim |
| 2 | Valid Web Bot Auth signature means the user's permissions, skip OAuth | 🔴 Don't | Signature identifies the operator only. A user token carries the delegation. |
| 3 | 90-day agent tokens | ❌ | Short-lived tokens, with fleets minting new ones automatically |
| 4 | Test client signs with the dictionary `Signature-Agent` form | ⚠️ | Test both forms against your actual verifier |

## 1. Don't build on `requested_actor`

- The draft-oauth-ai-agents-on-behalf-of-user draft expired in early 2026. `requested_actor` has no successor.
- Building on an expired individual draft means you own a wire format nobody else implements. Customer agent SDKs won't speak it.
- Borrow its rules, not its wire format.
- The standard, final pieces cover the same need:
  - **RFC 8693 token exchange.** The agent sends the user's `subject_token` plus its own `actor_token`.
  - **`act` claim.** The issued token records the actor chain, so logs read "agent X for user Y".
  - **RFC 8628 device grant.** This gives headless agents a login where no password reaches the agent.
  - **RFC 9728 protected resource metadata.** This lets an agent discover how to authenticate.
- `actor_token` itself is an RFC 8693 parameter, so the part of the draft you wanted is safe to use inside a token-exchange grant.

## 2. A signature is not a user grant 🔴

This is the biggest problem. Web Bot Auth answers "which company's agent sent this?" It explicitly excludes authorization and delegation.

What goes wrong if you treat a valid signature as the user's permissions:

- **No user is named.** A signed request carries no employee identity and no consent. Whose permissions would the edge attach? Any answer is invented.
- **Operator-level trust.** Anyone with a legitimate agent from a known operator could reach any employee's HR data. That is a confused-deputy hole.
- **No audit trail.** You lose the "agent X for user Y" record, and revocation can only cut off the whole operator.
- **You skip OAuth consent.** For payroll, compensation and personal data, that skipped step is the control your customers and auditors will ask about.
- **Weak signature trust.** An unresolved `Signature-Agent` is "a claim rather than an identity" until a fetched key verifies it. Signatures expire within 24 hours, and the draft is still moving.

Where Web Bot Auth does belong at Quarrystone:

- **Edge allow rule.** Let verified operator agents through bot management and CAPTCHA to reach docs and the API.
- **Rate-limit tier.** Key limits per verified operator, separate from the human's quota.
- **Optional second factor.** A customer can require "token plus a signature from operator Z" on top of the user token.
- **Telemetry.** Tag traffic with the verified operator.

In every case the signature gets added on top of the OAuth token, never in place of it.

## 3. 90-day tokens

- Delegated tokens last hours or days, never "until revoked". They must never outlive the user token they derive from.
- A leaked agent context should expire on its own. With 90 days, a transcript leak is a 90-day HR-data exposure.
- Revocation needs to work per agent from the user's settings, and 90-day bearer tokens make that hard.
- "Fleets don't break" is a real requirement, and short tokens meet it:
  - **The long-lived secret is the client credential, not the access token.** Fleets mint short access tokens from it (client credentials grant) or from workload identity federation.
  - **Rotate client secrets with overlap.** Allow two active secrets so rotation doesn't break running agents.
  - **Document refresh behaviour.** Publish expiry and 401 handling in the SDK and docs.
  - **Bind tokens to the agent instance** with DPoP or mTLS where the client supports it.
- Lifetime guide (starting points, to confirm with your security team):
  - Delegated access token: minutes to an hour.
  - Refresh token: bounded, with rotation and an absolute lifetime of days.
  - Fleet client secret: 90 days is fine here, with rotation overlap.

## 4. The signing test client

- The "dictionary `Signature-Agent` form from the latest draft" is a known interop risk. Cloudflare's verifier implements an earlier header form and rejects the dictionary form of later drafts.
- If your edge is Cloudflare, your test client may fail for reasons unrelated to your code.
- Sign with both forms and compare results.
- Don't weaken verification to make the test pass.
- Check the current draft text before fixing the format. The working group adopted it in September 2026, so expect changes.
- Confirm the parts you can already rely on: key id is a JWK SHA-256 thumbprint, `tag` is `web-bot-auth`, and signatures expire within 24 hours.

## Revised plan

**Identity and delegation model**

| Field | Value |
| --- | --- |
| Hosted operator agents | Identified by a Web Bot Auth signature, verified at the CDN or by you. This gives identity only. |
| Authority | The user's, via RFC 8693 exchange. `act` records the agent. |
| Credential | Delegated access token plus the agent's own `actor_token` |
| Scope | Never broader than the user's grant. Set per workflow, not per account. |
| Lifetime | Short, and never longer than the user token |
| Sponsor | A named human or admin at the customer for every agent credential |
| Revocation | Per agent, from the user's settings and the customer admin console |
| Customer fleets | Client credentials or workload identity federation, minting short tokens |
| Approval gate | Out-of-band human approval for irreversible or sensitive writes |

**Quarrystone-specific rules**
- Enforce the user's own row and field permissions at the API. A delegated token should never see more than that user could.
- HR data is regulated, so I'd put credentials above everything else in the rank and gate any write capability on write-safety.
- Separate read and write scopes. Compensation, termination and personal data changes should return `pending_approval`, confirmed through a push or email, never a button in the agent's own session.
- Never let the agent hold an employee's long-lived key or session.

**Agent-safe basics (checklist)**
- Stable machine error codes with the failing field and a next step.
- Idempotency keys on every mutating call.
- Published rate limits, per agent credential, with `Retry-After` on 429.
- Mark user-generated fields (names, notes, free-text HR comments) as untrusted content. They are a prompt-injection path.
- A sandbox or test mode so agents can run end to end without touching real employee records.
- Dry-run or confirm tokens for destructive operations.

**Order of work**
1. **Reachability gate.** Test each surface as each agent class you want to admit. Check for a "block AI bots" preset or CAPTCHA on the CDN.
2. **A. Measurement tags.** Add an agent-class field to every request and take a baseline first.
3. **B. Docs markdown and Context7 claim**, if the docs are public. Low effort.
4. **C. Agent credentials and delegation.** This is your core work: token exchange, device grant, short lifetimes, `act` logging, per-agent revocation.
5. **Web Bot Auth at the edge**, as an identity and rate-limit layer on top of C.
6. **D to G** (skill plus CLI, MCP, claim flow, discovery files): defer until logs or customer evidence justify them. Provision-then-claim is probably deleted if your accounts are sales-led, since agents can't self-serve a customer account.

## Assumptions to confirm
These would move the rungs. Defaults used where I had no answer:
1. Which agents matter: customers' own agent fleets (1e), chat assistants without a shell (1b), or both? This decides whether an MCP server (E) is ever needed.
2. Who controls the edge, and is it Cloudflare? This decides whether the `Signature-Agent` form issue applies to you.
3. How do humans authenticate today: an OAuth provider, SSO only, or API keys? If you already run OAuth, C is a scope review plus the token-exchange grant.
4. Which operations can agents trigger: read-only, or writes to compensation, terminations or personal data? Writes raise the approval-gate priority.
5. Is there a hard date (a customer demo or a deal)? If so, I'd ship the minimal C first: scoped agent-labelled tokens plus the approval gate. The device grant waits until after the date.
6. Effort ceiling: I assumed one engineer for a quarter and a standing agent channel. Tell me if it's config-only.

Hand-offs: grant flows and consent go to `samber/developer-platform-skills@oauth2-provider-design`. Token formats, scopes and rotation go to `samber/developer-platform-skills@api-auth-key-management`.