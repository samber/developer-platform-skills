# Chatterbox Systems: OAuth 2.1 sequencing and audit evidence plan

I followed `oauth2-provider-design` and its protocol and verification references. I did not ask the skill's clarifying questions, so the open ones are listed at the end, and the plan states its assumptions.

## Verdict: don't do one big cutover

Your instinct is half right.

- **Keep a single compliance date and a single evidence freeze.** The auditor needs one coherent picture.
- **Don't cut over the behavior in one release.** That would break about 3,100 apps and about 400 iOS customers on the same day.
  - The iOS fleet can't be force-upgraded. Its adoption curve is the critical path.
  - Rotating refresh tokens is the riskiest change for third parties. Any client library that drops the new refresh token gets logged out. The skill says a retrofit with thousands of live integrations makes rotation the expensive rung.
  - A release is not evidence. An auditor wants proof that non-compliant requests are rejected and stay rejected.

Use one named, independently toggleable gate per requirement. This is the Django OAuth Toolkit `COMPLIANT_BCP_RFC9700_*` pattern. Each gate moves through shadow, warn, brownout and enforce, per cohort. The gate history doubles as audit evidence.

## Define "compliant" in week 1

- **Spec status:** RFC 9700 (BCP 240) is final. The OAuth 2.1 document (draft-ietf-oauth-v2-1) was still a draft, at -15 in March 2026. Confirm its current status, and never tell the customer it is a published RFC.
- **Baseline:** Write a control baseline of RFC 9700 plus the 2.1 draft requirements. Get the customer's auditor to accept it in writing before building. I know of no certification program for 2.1, so the deliverable is a control matrix plus evidence.
- **Fallback:** Ask whether the customer's requirement covers the whole platform or only their tenant. A per-org "strict OAuth" policy could close their gap early. It is a fallback only, because the global server stays non-compliant.

## Sequence

Dates are anchored on today (2026-10-09), with the deadline around 2027-05-09.

| Phase | When | Work |
|---|---|---|
| 0. Baseline | Oct 9 – Nov 6 | Agree the control baseline. Log grant type, redirect-match result, PKCE presence and refresh-token age per `client_id`. Classify the 3,100 apps as dormant, active long-tail, or top traffic. Publish the RFC 8414 discovery document. Build every gate in shadow mode, logging "would reject". |
| 1. Stop the bleeding | Nov – Dec | New client registrations are 2.1-only: no implicit, no password, exact redirects, PKCE required. Migrate your own dashboard from implicit to code + PKCE. Start the iOS rewrite. Announce deprecation dates around Nov 16 (≥90 days is my judgment). Send dormant-app notices. |
| 2. Break the easy things | Jan – Feb | Ship the new iOS app in mid-January. Enforce exact redirect matching and PKCE by cohort. Remove implicit for third parties around Feb 15. Rotation is opt-in, then default for new grants. |
| 3. Hard ones | Feb – Mar | Brownouts (1h, 4h, 24h) for password grant. Force rotation. Suspend dormant apps. |
| 4. Kill and verify | Mar 31 – Apr 20 | Hard-disable password grant around Mar 31. Sunset unmigrated legacy refresh tokens around Apr 15. Run an external pentest of the auth server. Freeze evidence about Apr 20. |
| Buffer | Apr 20 – May 9 | Auditor review, slip absorption. |

Notes on the gates:

- **Redirects:** Run exact matching in shadow first. Generate per-app candidate exact URIs from completed flows, and have app owners confirm them in the portal.
- **Rotation:** Use token families, reuse detection and a 10–30s grace window.
  - Per-client compat mode logs reuse but doesn't revoke until that client's date.
  - Legacy tokens become family roots on first use, so the migration is lazy.
  - Any legacy token unused between enablement and Apr 15 is dormant by definition, so sunsetting it is low-impact.
  - Keep the predecessor hash with a validity timestamp so hashing at rest works with the grace window.
- **Confidential clients:** Never-expiring tokens will fail review. If rotation compat blocks some, a documented exception is a bounded fallback: inactivity expiry plus a Google-style per-client cap, with an expiry date.
- **Password grant (iOS):**
  - Use the system browser (`ASWebAuthenticationSession`), not an embedded webview.
  - Until the kill date, allowlist that single `client_id`, rate-limit it, and shorten its token lifetime. This is a time-boxed exception in the register.
  - 400 customers is small enough for named account-team outreach and a per-customer, per-app-version usage dashboard.
  - Pick the kill date now. If adoption lags, the choice is to cut or to lose the customer, so decide that ahead of time.
- **Scopes:** Not required for 2.1, but the skill treats one catch-all scope as a deleted anti-pattern.
  - Protocol compliance comes first.
  - After that, add `resource:action` scopes additively and map the old scope to them.
  - Bind scopes to token type (app vs user) from day one.
  - Add an org-admin approval surface, which this customer's security team will likely want.
  - Don't promise the full taxonomy inside seven months. Commit a dated roadmap item instead.
- **Verification program:** Start with publisher identity verification and enforce runtime scope ⊆ approved scope. Third-party assessment comes later.

## Proving compliance to the auditor

1. **Control matrix:** One row per requirement, with the gate flag, the automated test, and the evidence location.
2. **Discovery document:** `grant_types_supported` has no implicit or password, and `code_challenge_methods_supported` is `["S256"]`.
3. **Negative conformance tests in CI, plus a prod smoke test with a synthetic client:**
   - implicit and password requests are rejected
   - a missing or `plain` PKCE challenge is rejected
   - prefix, extra-path, case, trailing-slash and userinfo redirect variants are rejected
   - bearer tokens in query strings are rejected
   - an auth code replay is rejected, or a code lives longer than 10 minutes
   - replaying a refresh token revokes the whole family
   - concurrent refresh inside the grace window causes no logout
4. **Production telemetry:** Zero implicit, password, non-PKCE and non-exact-redirect requests over the trailing 30 days. Include rejection counts and the reuse-detection trip rate.
5. **Token inventory query:** Show zero refresh tokens with no family or no expiry. Archive the output with a timestamp.
6. **Change history:** Gate flags as code in git, with signed commits.
7. **Exceptions register:** Owner, compensating control and expiry for each exception. Ideally this is empty by freeze.
8. **Independent pentest** of the authorization server (budget needed).
9. **Migration record:** App-migration percentages and customer notices sent.

## Open questions

These answers change the plan:

1. Is the enterprise customer's requirement platform-wide or tenant-only, and are their users on the iOS app?
2. What are the current access-token TTL and the share of the 3,100 apps active in the last 90 days?
3. Are the apps mostly server-side confidential, SPAs or native? How many use implicit today?
4. Can any scope reach other users' or regulated data? That decides whether third-party assessment is mandatory.
5. Is there budget for a pentest, and can the team staff this alongside the iOS rewrite?

Nothing here is written to `developer-platform-context.md` or memory yet. Say if you want it saved.