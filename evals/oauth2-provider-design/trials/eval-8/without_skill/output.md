# OAuth 2.1 migration: sequencing and audit proof

## Do this first (this week, about 2 hours)
Ask the auditor in writing what "OAuth 2.1 compliant" means. OAuth 2.1 is an IETF draft, and I'm not certain of its current status, so check that. A draft has no certification and no official conformance suite. You need four answers:
1. Which document and version? Propose a pinned draft version plus RFC 9700 (the OAuth Security BCP, which is a published RFC).
2. Which scope? Authorization server only, or also your own clients? All tenants, or just theirs?
3. What counts as evidence?
4. Would they accept a time-boxed, documented exception for any single item? Don't plan on one, but ask.

## Your instinct: partly right
Don't ship one big release. Do keep one visible cutover date.

- **Why not a single release:** it is one rollback unit with 3,100 third-party apps in the blast radius. You also can't update the iOS app on 400 customers' phones.
- **What to do instead:** ship each change dark, behind per-feature and per-client flags. Enforce by cohort. Then flip the final switches on one announced date that the auditor sees.

## What "compliant" demands, mapped to your gaps

| Today | 2.1 requires | Work |
|---|---|---|
| Implicit (your dashboard) | Removed | Move dashboard to code + PKCE |
| ROPC (iOS app) | Removed | New app release, then kill endpoint |
| Prefix redirect match | Exact string match (loopback port is the only exception) | Registry cleanup + enforcement |
| No PKCE | PKCE on every code flow, S256 | Add, then require |
| Refresh tokens never expire or rotate | Public clients: sender-constrained or one-time use | Rotation with reuse detection, plus expiry |
| One scope tier | Not required | **Defer.** Not on the critical path |

## Timeline (about 30 weeks, last 4 are buffer)

**Weeks 0–3: scope and measure**
1. Get the auditor definition above.
2. Add telemetry per request: grant type, `client_id`, redirect match type (exact vs prefix), PKCE present, client app version, refresh-token age.
3. Build a client inventory. Likely a big share of the 3,100 apps are dead (no tokens used in 12 months). Plan to disable those with notice.
4. Start the iOS work now. It is the long pole.

**Weeks 2–10: additive, non-breaking**
1. Support PKCE (S256 only) alongside current flows.
2. Migrate your own dashboard to code + PKCE. You control it, so this is the quick win and your reference implementation.
3. **Strict mode for new registrations immediately**, so the legacy pile stops growing.
4. Ship refresh rotation with a grace window and reuse detection (reuse revokes the token family).
5. Add redirect matching in report-only mode: log what exact matching would reject.
6. Publish RFC 8414 metadata and deprecation headers on legacy grants.

**Weeks 6–18: migration**
1. Release the new iOS app (system browser session, code + PKCE). Tell the ~400 customers by account. Show app version in telemetry to track adoption.
2. Auto-register, as exact URIs, the redirect URIs observed in the last 90 days of logs. This grandfathers working apps and removes most breakage.
3. Email third parties and publish a migration guide. Set cutoff dates at least 90 days out.

**Weeks 14–24: enforcement waves, per cohort**
1. Run a brownout 2 weeks before each cutoff: a scheduled 1–4 hour disablement that surfaces forgotten clients.
2. Enforce in this order: exact redirect, then PKCE required, then rotation for everyone, then implicit off, then ROPC off.
3. Cap every existing never-expiring refresh token with an absolute expiry at the final date.

**Weeks 26–30: freeze and buffer**
Assemble the evidence pack and hand it to the auditor. Don't schedule enforcement here.

## Risks to decide on early
- **Rotation breaks old clients.** The old iOS app and some third-party apps may ignore the new `refresh_token` in the response. A grace window and per-client flags soften this. Test the old app against rotation before enabling it.
- **Customers who never update the iOS app.** Pick a hard ROPC cutoff date now, with escalating in-app and email notices. If the auditor allows an exception, document it with an expiry and compensating controls (rate limits, MFA). Don't count on it.
- **Per-tenant enforcement for the enterprise.** This could give you early proof for them. Ask whether the auditor accepts it, since a shared authorization server usually means they'll want global behavior.

## Proving compliance to the auditor
Build a pack of six items:

1. **Conformance matrix.** One row per requirement, citing the pinned draft section and RFC 9700. Each row names the control, the test, and the evidence location.
2. **Automated negative tests.** Run them in CI and nightly against production, and keep the results. Each must pass:
   - Implicit request returns `unsupported_response_type`.
   - Password grant returns `unsupported_grant_type`.
   - Authorization code request without `code_challenge` is rejected.
   - `plain` PKCE method is rejected.
   - Redirect URIs with a prefix, subpath, extra query, or different case are rejected.
   - Access token in a query string is rejected.
   - Replaying a rotated refresh token revokes the family.
   - An expired refresh token is rejected.
3. **Configuration evidence.** Discovery metadata showing `response_types_supported: ["code"]`, the allowed grant types, and `code_challenge_methods_supported: ["S256"]`. This supports the tests but proves nothing alone.
4. **Data evidence.** Dated queries and dashboards showing:
   - Zero implicit and ROPC requests after the cutoff.
   - Zero registered clients with non-exact redirect URIs.
   - Zero refresh tokens without expiry.
5. **Independent validation.** An external pen test of the OAuth flows. Also give the auditor a sandbox tenant and the test harness so they can run the negative tests themselves. Check what the OpenID Foundation suite covers before citing it, because it targets OIDC and FAPI rather than 2.1.
6. **Change record.** ADRs, release notes, customer communications, brownout dates, and an exception register (empty is best).

Then keep it true after the audit: keep the negative tests as a permanent CI gate, alert on any legacy grant attempt, and re-attest quarterly.

## Decisions I need from you
1. What did the auditor say "compliant" means, and which version?
2. Can you tell which of the 3,100 apps are active? If not, telemetry is week 1.
3. What is the iOS release and force-update situation?