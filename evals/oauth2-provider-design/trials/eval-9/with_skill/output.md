# Palisade Grid: authorization server launch pack

Launch is in five weeks. I read the `oauth2-provider-design` skill and its four references, then wrote the two deliverables.

**I could not give you an industry benchmark for most of these metrics.** The skill says: "no industry thresholds exist". It also warns that circulating consent drop-off percentages trace to vendor blogs, not measurements. I won't put an invented number next to a metric. Where a source gives a real reference point, I cite it. Everywhere else, the threshold comes from your own launch baseline, and I label it that way.

**Assumptions to confirm.** The skill asks six clarifying questions first, and I couldn't ask them, so I assumed these:
- Greenfield server, with no implicit or password-grant clients to migrate.
- Partners are mostly server-side confidential apps, with some SPA or native clients.
- Org admins can gate installs as well as end users (B2B).
- Some scopes reach other users' data, so a security assessment may apply to them.

If any of these is wrong, items 1.x and 4.x change.

Spec status: RFC 9700 (BCP 240) is final. The consolidated OAuth 2.1 document is still a draft. Write "OAuth 2.1 profile" or "RFC 9700 compliant" in sign-off docs, never "OAuth 2.1 RFC".

---

## Part 1: Go/no-go checklist for QA sign-off

Every item needs a test or an artifact as evidence. An assertion is not enough. Any ❌ in a 🔴 row blocks launch.

### 1. Protocol core

| # | Check | Evidence | Block? |
|---|---|---|---|
| 1.1 | Discovery document (`/.well-known/oauth-authorization-server`, RFC 8414) lists no `implicit` and no `password` grant | Conformance run + discovery JSON snapshot | 🔴 |
| 1.2 | Supported grants are exactly `authorization_code`, `client_credentials`, `refresh_token`, `device_authorization` (device flow only if you have CLI or headless clients) | Test per grant, plus a negative test per removed grant | 🔴 |
| 1.3 | PKCE S256 is required for every client, public and confidential. Request without `code_challenge` is rejected | Automated test, both client types | 🔴 |
| 1.4 | Redirect URIs use exact string match. Prefix, wildcard and subdomain variants are rejected. Only the port on native `localhost` may differ | Test with 5+ near-miss URIs | 🔴 |
| 1.5 | Bearer tokens in a URI query string are rejected. Header or POST body only | Negative test | 🔴 |
| 1.6 | Authorization codes are single-use, with a lifetime of 10 minutes or less. A replayed code fails | Test: reuse, and use at 10 min + 1 s | 🔴 |
| 1.7 | Access-token TTL is about 1 hour (skill default; GitHub App and Google ~1h, Entra 60-90 min). JWT access tokens are never longer | Config review | 🟠 |
| 1.8 | `/revoke` (RFC 7009) and `/introspect` (RFC 7662) work. Opaque tokens revoke instantly | Test | 🟠 |
| 1.9 | Compliance gates are separate toggles, one per RFC 9700 requirement (the Django OAuth Toolkit `COMPLIANT_BCP_RFC9700_*` shape), not one "2.1 mode" flag | Config listing: every gate on in prod | 🟠 |

### 2. Refresh rotation and reuse detection

| # | Check | Evidence | Block? |
|---|---|---|---|
| 2.1 | Every refresh token belongs to a family traced to the original grant | Schema + test | 🔴 |
| 2.2 | A consumed token replayed outside the grace window revokes the whole family | Staging demo: replay → family dead, successor token also fails | 🔴 |
| 2.3 | A grace window of about 10-30 s is configured and enforced | Config + boundary test at window − 1 s and window + 1 s | 🔴 |
| 2.4 | Concurrent-refresh test (multi-tab or retry, two parallel refreshes inside the window) causes no false logout | Automated test, passing | 🔴 |
| 2.5 | Tokens are hashed at rest. The predecessor hash is kept with a validity timestamp, so the grace window can recognize it. The tension is resolved on purpose, not by dropping hashing | Design note + DB inspection (no cleartext tokens) | 🔴 |
| 2.6 | Browser (SPA) clients get a shorter refresh lifetime. The skill's reference point is Microsoft's 24 h for SPAs against 90-day inactivity elsewhere | Policy config | 🟠 |
| 2.7 | A live-token cap per user and client pair exists (GitHub revokes the oldest above 10) | Test | 🟠 |
| 2.8 | A family revocation event is logged and alertable (client id, family id, whether inside or outside the grace window). The trip rate is a dashboard metric (see Part 2) | Log sample + dashboard panel | 🔴 |

### 3. Granular consent

| # | Check | Evidence | Block? |
|---|---|---|---|
| 3.1 | Every scope has plain-language consent copy, one sentence per scope. No grouped buckets, no raw scope strings. Copy is reviewed like UI copy | Copy table, one row per scope | 🔴 |
| 3.2 | Partial grants work. The token response returns the actually granted scope set | Integration test: user denies 1 of 3 | 🔴 |
| 3.3 | The server diffs granted against requested, always. It never assumes they match | Test: approve-all and approve-partial paths | 🔴 |
| 3.4 | Incremental authorization works, and the re-consent screen shows only the net-new scope. It does not re-list granted scopes | UI test with a screenshot, explicit | 🔴 |
| 3.5 | A denied scope can be re-requested later without penalty | Test | 🟠 |
| 3.6 | Scopes follow `resource:action` with a read/write split and read-only defaults. There is no catch-all `full_access` scope | Scope inventory | 🔴 |
| 3.7 | Scopes are additive-only. No shipped scope has had its meaning changed | Scope changelog review | 🔴 |
| 3.8 | Every scope is bound to a token type (app identity or user delegated) from day one | Scope inventory column | 🔴 |
| 3.9 | Admin consent surface exists: install approval, org-wide grant review, and app-identity scopes consentable by an admin only | Walkthrough as admin and as end user | 🔴 |
| 3.10 | Scope changes that invalidate refresh tokens are known and batched. Each addition is a re-consent event | Release plan | 🟠 |

### 4. App review queue and verification

| # | Check | Evidence | Block? |
|---|---|---|---|
| 4.1 | Registration is manual, via developer portal plus a review step. Dynamic client registration is off. If it is on for an MCP or agent use case, it is gated and rate-limited | Endpoint probe: unauthenticated registration returns an error | 🔴 |
| 4.2 | Every scope is classified into a tier with a named review requirement. The bright line: scopes reaching other users' data or PII trigger a third-party security assessment | Tier table | 🔴 |
| 4.3 | Publisher identity verification (domain + verified account) runs for every listed app | Queue flow test | 🔴 |
| 4.4 | The listing shows identity, self-attestation and audit as three visually distinct signals. Never one checkmark | UI review | 🟠 |
| 4.5 | Runtime enforcement is live: any scope request that is not a subset of what was declared and approved is rejected | Test: request an undeclared scope | 🔴 |
| 4.6 | The unverified testing lane has enforced limits: named test users, a warning screen, a hard user cap, and test-token expiry (Google's model: 100-user lifetime cap, 7-day expiry; re-verify the figures) | Test: attempt user cap + 1 | 🔴 |
| 4.7 | Review queue has an owner, an SLA and an escalation path. The ~30 launch partners are triaged into the queue with tier assigned | Queue export | 🔴 |
| 4.8 | Review checklist covers the recurring rejection themes: over-broad scope requests, weak token handling, misleading listing copy | Checklist doc | 🟠 |
| 4.9 | Re-review triggers are defined: new scope requests, new versions, annual recurrence for assessed apps | Policy doc | 🟠 |

### 5. Launch readiness (ops)

| # | Check | Evidence | Block? |
|---|---|---|---|
| 5.1 | The 4-5 dashboard metrics in Part 2 are live in staging with real events flowing | Dashboard link + screenshots | 🔴 |
| 5.2 | On-call runbook exists for: reuse-detection spike, token endpoint outage, partner locked out, suspected token theft (revoke a client's families) | Runbook | 🔴 |
| 5.3 | Kill switch tested: revoke all tokens for one client without affecting others | Staging drill | 🔴 |
| 5.4 | Partner comms sent: grace-window behavior, scope diff requirement, refresh rotation (clients must store the new refresh token on every use) | Sent message + partner ack tracking | 🟠 |
| 5.5 | Secrets and client credentials are rotatable, with nothing in logs. Token values and auth codes are redacted in logs | Log grep | 🔴 |

**Decision rule:** all 🔴 rows pass → go. Any 🔴 fails → no-go, and re-run the failed gate after the fix. 🟠 rows may ship with a dated, owned follow-up. Don't weaken a gate to make it pass.

---

## Part 2: Post-launch dashboard (5 metrics)

**How to read the "benchmark" column.** The only hard target is metric 5, and that is a design invariant, not an industry figure. Metrics 1 to 4 have no published industry threshold. Each shows its nearest sourced reference point and a rule for deriving the alert from your own baseline.

**Proposed alert rule (mine, not an industry standard):** collect 14 days of data, then alert on a sustained deviation from your own baseline. Set the multiple yourself.

| # | Metric | Industry benchmark | Reference points you can cite | Off when… |
|---|---|---|---|---|
| 1 | **Reuse-detection trip rate** (family revocations per 1,000 active refresh families, per client) | None exists | The tripwire can't tell attacker from legitimate client (RFC 9700 §4.14). Grace window starting value is 10-30 s (Django OAuth Toolkit, Keycloak knobs) | Baseline plus sustained deviation. **One client dominating** → likely a client bug or a too-tight grace window. **Many clients or geographies at once** → suspect theft. Always split trips inside and outside the grace window |
| 2 | **Median app-review turnaround** (and oldest item in queue) | None exists as a standard | Vendor timelines only: Salesforce 1-2 wk verification + 3-4 wk testing, +2-3 wk per resubmission; Google sensitive scopes ~10 days after a complete submission; Microsoft publisher verification "in minutes" for a prepared publisher | Your own SLA breached. With ~30 partners, watch the oldest item, since the median can hide one stuck partner |
| 3 | **Unused-scope share** (apps holding scopes their traffic never uses) | None exists | Over-broad scope requests are a recurring rejection reason at Salesforce, Shopify and Atlassian | Rising share, or any single partner with a large unused set. Feed it into review and runtime enforcement |
| 4 | **Consent outcome mix** (approve, partial grant, deny, admin-blocked), per client | None exists. Do not cite a drop-off percentage; the sources are vendor blogs, not measurements | Slack: over-scoping makes users or admins reject installs | Partial-grant or admin-block rate climbing for one client → that client over-scopes or has bad copy. Also watch re-consent drop-off after any scope addition |
| 5 | **Runtime scope-subset violations** (requests outside the approved declaration) plus **unverified-lane cap hits** | **Target 0 unexplained**, by design (not an industry figure) | Google's unverified-app warning fires on exactly this divergence | Any non-zero value outside a known, in-flight partner change → investigate the same day |

**Baseline plan:** review all five at day 7 and day 14. At day 14, write the numeric alert thresholds into the runbook, so on-call has real numbers, labeled "Palisade Grid baseline" and not "industry".

**On-call reading order when something looks off:** metric 5 (hard failure) → metric 1 (possible theft) → metric 4 (partner or UX issue) → metrics 2 and 3 (process drift).

---

## Open items for you

1. Confirm the four assumptions at the top. Items 1.x, 3.9 and 4.x depend on them.
2. Decide which scopes reach other users' data. These need the third-party assessment tier, which takes months and costs the partner a fee. With launch in five weeks, partners needing it must be flagged now.
3. Pick the grace window value (10-30 s) before QA writes test 2.3.
4. Confirm DPoP is out of scope for launch. The skill treats it as Stage 4, needed only for financial or health data or long-lived agent tokens.