# Palisade Grid authorization server: launch pack

Launch is about 2026-11-21. I followed `oauth2-provider-design`, including its references.

**Assumptions.** I didn't ask the six clarifying questions, so please correct any of these that are wrong:
- This is a greenfield server.
- The ~30 launch partners are server-side confidential apps.
- Apps act on behalf of signed-in users.
- Some scopes may reach other users' data.
- Org admins can gate installs.
- You are not building on an identity product that already ships DPoP.

If any of those is wrong, tell me. A different answer to the data-sensitivity or client-type question changes sections A, D and E.

## 1. Go/no-go checklist for QA

Every item is blocking, and each needs evidence from a test, not an assertion. Sign-off means every row is ✅ with a link to the test run.

### A. Protocol

| # | Check | Evidence |
|---|---|---|
| A1 | Discovery document (`/.well-known/oauth-authorization-server`, RFC 8414) lists no `implicit` or `password` grant. | Conformance run output |
| A2 | Requests with no PKCE, or `plain` instead of S256, are rejected for every client, confidential ones included. | Negative tests |
| A3 | Redirect URIs match as exact strings. Prefix, wildcard and subdomain variants are rejected. The only exception is the port on native `localhost` redirects. | Negative tests |
| A4 | Authorization codes are single-use, expire within 10 minutes, and a replayed code is rejected. | Replay test |
| A5 | Bearer tokens in query strings are rejected. | Negative test |
| A6 | `/revoke` and `/introspect` work. `device_authorization` works if you ship it. | Integration tests |
| A7 | Each RFC 9700 requirement sits behind its own named, independently toggleable gate. Gate states are recorded for the launch. | Config export |
| A8 | Access-token TTL is about 1 hour. JWT access tokens are never longer than that. | Config + token decode |

### B. Refresh rotation and reuse detection

| # | Check | Evidence |
|---|---|---|
| B1 | Every refresh token belongs to a family tied to the original grant. | Schema + test |
| B2 | Replaying a consumed refresh token outside the grace window revokes the whole family. Demonstrated in staging. | Staging replay test |
| B3 | Concurrent refresh passes without a false logout. This covers multi-tab and retry cases inside a 10-30 s grace window. | Concurrency test |
| B4 | The grace window recognises a just-consumed token even though tokens are hashed at rest, for example by keeping the predecessor's hash with a validity timestamp. | Design note + B3 passing |
| B5 | Refresh tokens are stored hashed. | DB inspection |
| B6 | Revoking a grant kills its access and refresh tokens. A family revocation is logged with client, family ID and reason. | Test + log sample |
| B7 | Refresh-token lifetime is set for confidential clients. Browser clients get a tight cap (Microsoft uses 24 h for SPAs) if any exist. | Config |

### C. Granular consent

| # | Check | Evidence |
|---|---|---|
| C1 | Every scope has its own plain-language sentence. No raw scope strings, no grouped buckets. | Copy review sign-off |
| C2 | The token response returns the granted scope set, and the server computes the granted-versus-requested diff. A partial-grant integration test passes. | Integration test |
| C3 | Re-consent shows only the net-new scope. | UI test with screenshot |
| C4 | Adding a scope triggers re-consent as designed. Existing scopes are never repurposed. | Scope-registry review |
| C5 | Each scope is bound to a token type (app identity or user-delegated). | Scope registry |
| C6 | Org-admin approval path works: queue, org-wide grant review, and admin-only consent for app-identity scopes. | End-to-end test |
| C7 | A partner can re-request a denied scope later without penalty. | Test |

### D. App review queue and verification

| # | Check | Evidence |
|---|---|---|
| D1 | Every scope is classified into a review tier with a named requirement. A scope reaching other users' data or PII is in the highest tier. | Scope-to-tier table |
| D2 | Runtime enforcement rejects any scope request that is not a subset of what was approved at registration. | Negative test |
| D3 | Unverified apps run in a testing lane with a hard user cap, a warning screen and short token expiry. The cap is enforced, not just documented. | Test at cap+1 |
| D4 | Trust signals are shown separately: identity verified, self-attested, independently audited. No single checkmark covers all three. | UI review |
| D5 | Registration is manual or reviewed. No open dynamic client registration endpoint exists. | Endpoint scan |
| D6 | The review queue has an owner, an SLA and an escalation path. Reviewers can approve, reject, request changes and suspend a live app. | Walkthrough |

### E. Partners and operations

| # | Check | Evidence |
|---|---|---|
| E1 | All ~30 launch partners are registered, tiered and tested in staging. Each has run the full flow, including a partial grant and a refresh. | Per-partner test log |
| E2 | Partners were told that refresh tokens rotate and that a replay revokes the family. Partner docs describe the grace window. | Sent comms |
| E3 | Per-client kill switch: an app can be suspended and its tokens revoked in minutes. | Drill |
| E4 | Runbook exists for suspected token theft: family-revocation storms, partner contact, customer notification. | Tabletop |
| E5 | The five dashboard metrics below are live, and alert routing reaches on-call. | Test alert |
| E6 | Launch comms say "RFC 9700" for the security baseline. They don't claim OAuth 2.1 is a published RFC; it is still a draft. | Comms review |

### F. Mutation checks

The skill's gates require these before sign-off, and so do your own testing rules:
- Disable PKCE enforcement. A2 must fail.
- Remove the grace window. B3 must fail.
- Drop the subset check. D2 must fail.
- Stop returning the granted set. C2 must fail.

## 2. Post-launch dashboard

I can't give you an industry benchmark for any of these, and I won't invent one. The skill states plainly that no industry thresholds exist for these metrics. The consent-conversion percentages that circulate come from vendor blogs, not measurements.

Instead, each metric has two things:
- **Reference points**: sourced numbers that frame what normal looks like.
- **Alert rule**: a rule I'm proposing. It is not an industry standard. Set the real thresholds after about 2 weeks of baseline.

With ~30 partners, volumes are small. Alert on counts and trends, not percentages.

| # | Metric | Reference points | Alert rule (my proposal) |
|---|---|---|---|
| 1 | **Reuse-detection trips**: family revocations per day, split by inside or outside the grace window. | RFC 9700 §4.14: a trip can't tell attacker from legitimate client, so treat it as a tripwire, not proof. Design grace window: 10-30 s. | Any trip is logged. Page on a cluster of trips for one client or one user. A steady stream from one partner points to a too-tight window or a client bug. |
| 2 | **Median app-review turnaround** and oldest item in queue. | Program timelines, not thresholds. Google sensitive scopes take about 10 days. Salesforce takes 1-2 weeks verification plus 3-4 weeks testing, and each resubmission adds 2-3 weeks. Microsoft publisher verification takes minutes. | Use your own published SLA. Alert when the oldest item passes it. |
| 3 | **Over-scoped apps**: apps requesting scopes their traffic never uses. | None published. Slack's guidance is that over-asking makes users and admins reject installs. Shopify rejects excessive permission requests. | Review monthly. Any app with a scope unused for 30 days gets flagged to the reviewer. |
| 4 | **Consent outcomes**: approve, partial grant, deny, admin reject. | None published. Don't cite any drop-off figure. | Watch for a step change after any scope or copy change. A rising partial-grant rate for one app means its features are breaking on the diff. |
| 5 | **Token endpoint health**: `invalid_grant` count by cause (reuse, expired, revoked), 5xx rate, p95 latency. | Access tokens last about 1 hour, so each active client should refresh roughly hourly. That gives you a volume sanity check. | Page on sustained 5xx. Treat a jump in `invalid_grant` after a partner deploy as a client-side bug first. |

On-call guidance:
- A zero in metric 1 for week 1 is not proof of safety. Check that the detection path is wired using the B2 staging test.
- Metrics 1 and 5 both cover the false-positive logout risk. Read them together.
- Metric 2 is for the review team. The standing review process behind it belongs to `app-marketplace-review`, which I didn't read.

## 3. Open items for you

1. Confirm or correct the assumptions at the top.
2. Set the review-queue SLA for D6 and metric 2.
3. Decide the unverified-lane user cap. Google's is 100 users lifetime, with 7-day test-token expiry.
4. Decide whether any launch scope reaches other users' data. If so, the highest verification tier (third-party assessment, which the developer pays for) is likely too slow for a 5-week launch. Scope those out of launch or ship with the lowest-risk scopes only.

I did not save anything to the `developer-platform-context.md` memory file.