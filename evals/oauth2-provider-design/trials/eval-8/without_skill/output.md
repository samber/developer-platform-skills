# OAuth 2.1 migration plan for Chatterbox Systems

**Next action this week:** email the customer's security team and get "OAuth 2.1 compliant" defined in writing (see Step 0). Everything else depends on it.

## Verdict on the big cutover

❌ **Don't do one big cutover.** The reasons:

- **You don't control the clients.** Roughly 3,100 third-party apps ship on their own schedules. The iOS app depends on App Store review and on customers updating, some through slow MDM rollouts.
- **It can't be rolled back.** If you remove implicit, ROPC and prefix matching on one day, a failure can't be traced to a cause, and you can't un-break 3,100 integrations.
- **It hides a dependency.** Existing refresh tokens never expire, so many old-iOS users are never forced to log in. When you start expiring tokens, they all re-login at once through ROPC, which you're removing. The sequence therefore has to be: new app adopted, then expiry enforced, then ROPC off.
- **It puts the whole risk on the deadline.** If it slips, you have nothing to show the auditor. A staged plan leaves you with partial compliance and a documented exception list.

✅ **Do this instead:** one dated enforcement milestone per feature, driven by a per-client `legacy` / `strict` profile flag. Everything moves from legacy to strict. The count of legacy clients is your burn-down metric. At zero, you delete the legacy code. That deletion is also your audit evidence.

## Step 0: define "compliant" (weeks 1–2)

OAuth 2.1 is an IETF draft, not a final standard, and there is no certification for it. Check its current status and pin a draft version. Without a pinned profile the auditor can move the goalposts.

Get the customer to sign off on a short profile that covers:

- The pinned draft version of `draft-ietf-oauth-v2-1`.
- RFC 9700 (OAuth Security BCP), RFC 7636 (PKCE) and RFC 8252 (native apps).
- Whether it applies to the whole platform or only to their tenant's apps and users. This changes your effort a lot.
- Whether the test is a point in time (the deadline date) or continuous.
- Whether a dated exception list with compensating controls is acceptable, if one or two stragglers remain.
- Whether they expect granular scopes. OAuth 2.1 doesn't require them, but auditors sometimes ask about least privilege. Your single scope tier is not a 2.1 violation. Keep it off the critical path, and offer additive scopes later if they insist.

**Requirement checklist:**

| Gap | OAuth 2.1 requirement | Your status |
|---|---|---|
| Implicit grant | Removed | ❌ live (own dashboard) |
| ROPC | Removed | ❌ live (old iOS app, ~400 customers) |
| Redirect matching | Exact string match (loopback port may vary for native apps) | ❌ prefix |
| PKCE | Required for all authorization-code clients, S256, downgrade rejected | ❓ verify |
| Refresh tokens (public clients) | Sender-constrained or one-time-use rotation | ❌ |
| Refresh token lifetime | Not mandated, but the BCP expects limits | ❌ never expire |
| Bearer token in query string | Forbidden | ❓ verify |
| Scopes | Not required | n/a |

## Step 1: measure before you change anything (weeks 1–3)

Add logging per `client_id`. This telemetry decides the rest of the plan.

- Count requests by grant type, `response_type`, PKCE present or absent, and redirect match type (exact vs prefix-only).
- Log refresh token age, last-used time and, for public clients, concurrency of refresh calls.
- Log ROPC logins by app version.

Then triage the 3,100 apps:

- **Dead (no traffic in 90 days):** likely a large share. Disable them after notice. Don't delete them.
- **Top 50 by traffic:** direct outreach, with a named owner on your side for each.
- **The long tail:** automated email, dashboard banner and `Sunset`/`Deprecation` headers (RFC 8594).

Confirm in week 1 that the iOS app's source and build pipeline still exist. If they don't, the iOS rebuild is your longest pole and the whole schedule moves.

## Step 2: ship additive, non-breaking changes (Nov)

Nothing here breaks existing clients.

1. Support PKCE and publish AS metadata (RFC 8414), listing only S256.
2. **Migrate your own dashboard from implicit to code + PKCE first.** You control it, and it proves the path works.
3. **Make `strict` the default for newly registered apps.** This stops the debt growing. Start the clock with a date of about Dec 1.
4. Add refresh token expiry (idle and absolute) and rotation with reuse detection. Keep a short grace window so a network failure mid-refresh doesn't lock a user out. Gate all of this behind the per-client flag.
5. Run exact redirect matching in **shadow mode**. Log every request that would be rejected, then pre-register each client's observed redirect URIs as exact values.
6. Start building the new iOS app on ASWebAuthenticationSession with code + PKCE.

Rotation is mandatory for public clients. For confidential clients, client authentication plus expiry is acceptable under 2.1. Rotating those too is simpler to explain to an auditor, but it is optional.

## Step 3: announce and enforce in order (Dec–Mar)

Avoid enforcement dates between about Dec 15 and Jan 5.

| When | Action |
|---|---|
| Dec 1 | Deprecation notice to all apps, with dates and migration guide. New apps strict-only. |
| Mid-Dec | iOS app submitted to the App Store. |
| Jan | Dashboard fully off implicit. Disable dead apps. First **brownout** (the deprecated feature fails for 1 hour, announced). |
| Feb | Enforce exact redirect matching and turn off implicit for contacted apps. Brownouts escalate to 24 hours. |
| Mar | Minimum iOS app version enforced. ROPC off. Refresh expiry enforced everywhere. |
| Apr 1–15 | Remove legacy code paths. Code freeze Apr 15. |
| Apr 15 – May 9 | Evidence pack, third-party test, auditor window. About three weeks of buffer. |

Notes on the order:

- **Refresh expiry hits old-iOS users last.** Enforce it per client, only after that app version has a ROPC-free replacement and adoption is high.
- **Rotation on the old iOS client is also a risk.** The old app may not persist a rotated refresh token. Exempt that client until the version floor, and list it on the exceptions register in the meantime.
- **iOS customer comms:** have customer success contact the ~400 customers by name. Use an in-app update prompt first, then a hard block at the version floor.
- **Fallback if iOS adoption lags:** a documented exception for that one `client_id` with compensating controls (rate limiting, per-tenant disable, MFA if possible). Make the enterprise customer's own tenant ROPC-free earlier if they don't use that app.

## Step 4: prove it to the auditor

Build the evidence pack as you go, not at the end.

1. **Signed compliance profile** from Step 0.
2. **Traceability matrix:** requirement → control → automated test → evidence artifact → owner.
3. **Dated configuration snapshots:** AS metadata showing `grant_types_supported` as `authorization_code`, `refresh_token` and `client_credentials` only, and `code_challenge_methods_supported: ["S256"]`.
4. **Negative tests in CI, also run as weekly synthetic probes against production.** Each must be rejected:
   - `response_type=token`.
   - `grant_type=password`.
   - An authorize request without `code_challenge`.
   - The `plain` PKCE method.
   - A wrong code verifier.
   - A redirect URI that differs by prefix, trailing slash, extra path, query string, case, or wildcard.
   - A non-HTTPS redirect (except loopback).
   - Authorization code reuse (it should revoke the tokens it issued).
   - Refresh token reuse (it should revoke the token family).
   - An expired refresh token.
   - A bearer token in the query string.
5. **Production data evidence:** scripted queries, output saved with dates.
   - Legacy-grant requests: 0 in the trailing 30 days.
   - Legacy client count: 0, or only the named exceptions.
   - Every registered redirect URI is exact, with no wildcards.
   - No active refresh token without an expiry.
6. **Independent verification:** a third-party pentest scoped to the checklist. Don't claim a 2.1 conformance certification, because none exists. The OpenID Foundation suite covers OIDC and FAPI, not 2.1.
7. **Exceptions register,** if anything remains: client, reason, compensating control, owner, expiry date.
8. **Change trail:** deprecation notices sent, release notes, PRs that removed the legacy code, and a CI gate that fails if a legacy grant is reintroduced.
9. **Mid-point checkpoint** with the customer at about month 3, to show the dashboard burn-down. This is your best churn protection. Consider an interim attestation letter.

## Decisions I need from you

1. Does the iOS app's source and build pipeline still exist and build today?
2. Does the customer's requirement cover the whole platform or only their tenant?
3. Do you know the share of the 3,100 apps with traffic in the last 90 days? If not, Step 1 finds it.
4. Are you willing to disable dead apps after notice, and to set a hard iOS version floor?
5. Does the customer accept a dated exception list as a pass?

If you answer 1 and 2 first, I can turn this into a dated plan with owners.