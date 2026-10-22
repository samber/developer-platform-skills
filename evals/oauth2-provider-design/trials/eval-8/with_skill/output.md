# OAuth 2.1 sequencing and audit plan for Chatterbox Systems

I based this on the `oauth2-provider-design` skill and its four references.

## Verdict: don't do one big cutover

Seven months is enough. A single cutover release is the one shape likely to miss it, for four reasons:

- **The iOS app can't be force-updated.** About 400 customers run a password-grant app, and you can't remove that grant until they update. A big-bang release either breaks them or slips the date.
- **Prefix redirect matching hides unknown breakage.** Switching 3,100 apps to exact matching at once breaks every app that relied on a prefix, and you don't yet know which ones.
- **Refresh tokens that never expire or rotate have no family structure.** The skill says family grouping is much harder to retrofit onto already-issued tokens than to design into new ones.
- **A cutover can't be rolled back per requirement.** One bad requirement forces you to revert everything.

Use the skill's compliance-gate pattern instead:

- Model each 2.1 requirement as its own flag, enforced per client cohort.
- Roll each flag out through three states: observe, warn, enforce.
- Treat the flag table as your audit artifact.

## Before you start

1. **Pin the standard.**
   - RFC 9700 (BCP 240) is final.
   - OAuth 2.1 (`draft-ietf-oauth-v2-1`) is still a draft. The reference file lists draft-15 from March 2026, so re-check before you cite it.
   - Don't let a contract or questionnaire say "OAuth 2.1 RFC".
   - Get the auditor to agree in writing to "conforms to the OAuth 2.1 profile and RFC 9700" against a control matrix (see Proof, below). Do this in week 1.
2. **Scopes and verification are not 2.1 requirements.** Your single scope tier and the missing app-verification program don't block compliance, so keep them off the seven-month critical path.
   - Ask the security team whether "least privilege" is in their checklist.
   - If it is, promise an additive-only `resource:action` split with a read/write split as a roadmap item. Keep the coarse scope alive during the migration.
   - A single broad scope is the anti-pattern the skill deletes, so plan to leave it. Just don't gate the deadline on it.

## Sequence

Dates assume today (2026-10-17) and a deadline of about 2027-05-17. I chose them as defaults, so adjust them to your release calendar.

### Phase 0: measure and stop the bleeding (weeks 0–4, to mid-Nov)

1. **Log every authorization and token request.** Record:
   - `grant_type` and `response_type`
   - `client_id` and public/confidential status
   - whether PKCE was sent
   - whether the redirect URI matched exactly or only by prefix
   - refresh-token age and last use
2. **Publish the RFC 8414 discovery document** (`/.well-known/oauth-authorization-server`).
3. **Build the gate flags**, one per requirement and per client cohort. Each gate gets a per-client override and a documented rollback.
4. **Lock down new registrations today.** Require:
   - exact redirect URIs
   - PKCE
   - no implicit or password grant
   - rotating refresh tokens

   This stops the debt from growing, and it breaks nobody who already exists.
5. **Cohort the 3,100 apps by activity.** Dormant apps (no token issued in a window you choose) are the cheapest to disable or expire.

### Phase 1: the changes you fully control (weeks 2–10)

1. **Dashboard: move from implicit to authorization code + PKCE.** It's first-party, so you control both sides and it carries no third-party risk. Do it first, because it's also your audit story.
2. **Ship refresh rotation with family reuse detection and a 10–30 second grace window.**
   - Start a new family on the first refresh after enabling the gate.
   - Resolve the hashing-versus-grace-window tension deliberately. For example, keep the predecessor's hash with a validity timestamp.
   - Enforce rotation first for public clients. That is the 2.1 mandate, and confidential clients stay on a bounded non-rotating form until later.
3. **Add refresh expiry and a per-user, per-client cap.** The benchmarks are 90 days of inactivity (Microsoft), 24 hours for SPAs, and a cap of 10 (GitHub) or 100 (Google). Apply expiry to last-use first, so dormant tokens go before active ones.
4. **Reject query-string bearer tokens.** Confirm the codes are single-use with a lifetime of 10 minutes or less.
5. **Ship the new iOS app** with authorization code + PKCE in the system browser (`ASWebAuthenticationSession`). Prefer a universal-link redirect. Target the App Store release for early December, to start the adoption clock.

### Phase 2: third-party migration (months 2–5, mid-Dec to mid-Apr)

1. **Redirect matching.**
   - Run shadow mode and compute each app's "would fail exact matching" set.
   - Propose an exact allowlist per app, but never auto-seed it from logs. An attacker can craft URIs under a prefix, and logging them would legitimize them. The developer confirms each URI in the portal.
   - Flag prefixes whose host has an open redirect.
2. **Implicit and PKCE for third-party apps.**
   - Warn first, then enforce, by cohort: dormant, then low-traffic, then active.
   - Give about 90 days' notice, following the notice-and-sunset discipline in `api-versioning-policy`.
   - Return clear, actionable errors.
3. **Password grant.**
   - Turn it off for every client except the iOS app's `client_id` as soon as the new app ships.
   - Nag in the old app version if you can ship a final old-line update.
   - Contact the roughly 400 customers directly. Tenants are identifiable, so customer success can chase them.
   - Set a hard cutoff date no later than mid-April.
4. **Finish confidential-client rotation** for new and opted-in clients, then default it on.

### Phase 3: evidence and buffer (mid-Apr to mid-May)

- Flip every gate to enforce globally.
- Gather evidence and run an independent test.
- Leave 4–6 weeks of buffer. If a phase slips, it eats this buffer and not the deadline.

### Decisions for you on the iOS fallback

- **Per-tenant enforcement.** If the enterprise customer's users don't run the old iOS app, you could enforce 2.1 for their tenant first. Only use this if the auditor accepts tenant scope, because a server that still serves the password grant elsewhere may not count as compliant.
- **Exception register.** If adoption lags, keep a time-boxed exception, with compensating controls and a named owner. It's a risk against the deadline, not a plan, and it must appear in the evidence pack.

## Proof for the auditor

Build a control matrix. Each row links the requirement, its gate flag, the config evidence, an automated test, and runtime telemetry.

| Requirement | Test and evidence |
|---|---|
| No implicit grant | Discovery document omits it; `response_type=token` returns `unsupported_response_type` |
| No password grant | `grant_type=password` returns `unsupported_grant_type` |
| PKCE (S256) for every client | Request without `code_challenge` is rejected, for public and confidential clients |
| Exact redirect matching | Negative tests: prefix extension, trailing slash, path traversal, subdomain, appended query, case; only the native `localhost` port exception passes |
| No bearer tokens in query strings | Request with the token in the query is rejected; log-scrubbing check |
| Authorization codes single-use, ≤10 min | Replay test and expiry test |
| Refresh rotation and reuse detection | Replayed token revokes the whole family; concurrent-refresh test shows no false logout |
| Access token TTL ≈1 hour; refresh expiry | Config snapshot plus issued-token sample |
| Tokens hashed at rest | Schema and storage review |
| Mix-up defense and `state` handling | RFC 9700 asks for this. Check it against the RFC text, since the skill doesn't cover it |

Support the matrix with seven artifacts:

1. **CI regression suite.** Run the negative tests on every build, so a regression fails the build.
2. **Discovery document and config snapshot.** Dated, in version control, with a history of changes.
3. **Telemetry showing zero legacy successes.** Report legacy-grant successes at zero for a sustained window after enforcement, such as 30 days. Rejects can be nonzero, and they show the gates are live.
4. **Exception register.** Ideally empty by the deadline.
5. **Independent pentest** of the authorization server, scoped to the matrix, with a retest after fixes. This is the strongest single artifact.
6. **Migration record.** Dated notices, per-cohort adoption curves, and flag-flip timestamps.
7. **Staging proof.** The skill's gates require reuse detection demonstrated in staging.

As far as I know there is no formal OAuth 2.1 certification, because it is still a draft. Check this before you tell the auditor one exists. Position your evidence as conformance to a stated profile, not as certification.

## Metrics to watch

- Legacy-grant requests per day, by cohort.
- Share of active apps already on exact redirects.
- Reuse-detection trip rate. It can mean attack or a grace window that's too tight.
- Support tickets per cohort flip.
- iOS app version adoption.

The skill's gates are: protocol conformance verified by test, reuse detection shown in staging, and gates enforced and not just documented.

## Questions that would change this plan

1. Are the 3,100 apps mostly server-side, SPA, or native? SPAs make rotation and expiry the long pole.
2. Does anyone use `client_credentials` today, or is machine access API keys?
3. Does the enterprise customer's team actually use the iOS app or any third-party app?
4. Is the authorization server home-built, or on an identity product with rotation as configuration? That flips the effort estimates.
5. What exactly does the customer's checklist say: "OAuth 2.1", RFC 9700, or something else?

I read the skill and all four references but did not run any commands or write any files. The skill suggests a `developer-platform-context.md` memory file. Say if you want me to record these decisions there.