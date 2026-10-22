# Traceloom API auth review: three items

**Verdict:** items 1 and 2 are wrong as planned, and item 3 is the most urgent. I reviewed against the `api-auth-key-management` skill (OWASP API2 anchors, key-vs-OAuth boundary, ownership tiers, rotation runbook).

| # | Plan | Verdict | Fix |
|---|------|---------|-----|
| 1 | Extend API keys with per-request scopes, short expiry, per-app revocation | ❌ Reinventing OAuth | Use OAuth 2.0 for partner apps |
| 2 | Paste the API key into the browser JS snippet | 🔴 Never ship a long-lived key to a browser | Write-only ingest key, or a short-lived server-minted token |
| 3 | One long-lived admin key per customer CI, stored in runners | 🔴 Blast radius is the whole account | Service-account key per pipeline, least scope, then OIDC federation |

## 1. Partner apps reading dashboards on customers' behalf

**Verdict: ❌ Use OAuth, not extended keys.**

- **What a key answers.** A static key says which app is calling. Partner apps need to know that a customer granted permission and within what limits. That is a different question.
- **What you'd be building.** Per-request scopes, short expiry and per-app revocation are the three things OAuth exists to provide. The skill names this heuristic: bolting expiry, scopes and fine-grained revocation onto a static key means reinventing OAuth. You would end up with a worse, home-grown OAuth, plus its security review.
- **A key has no consent step.** A static key can't capture a customer's consent, so it can't say "customer X approved app Y for dashboards read-only". You would have to invent that flow anyway, which is a consent screen.
- **This matches the skill's trigger.** Question 3 asks whether third-party apps act on behalf of your users. Yes, so the boundary is OAuth.

**Do this:**
- Authorization code flow with PKCE, tokens in the 5-60 minute range, refresh tokens that can be revoked.
- Scopes such as `dashboards:read`, defined in the permission taxonomy.
- Per-app and per-customer-grant revocation. The customer can revoke an app from their settings, and you can revoke an app globally.
- Partner app registration and verification before an app can request consent.
- Hand the details to `samber/developer-platform-skills@oauth2-provider-design`: scope granularity, consent screens, token lifecycle and app verification.

**Keep keys for what they're good at:**
- A customer calling Traceloom as themselves, server-to-server.
- Rate limiting by caller.

This needs no "whole new auth system" beyond an authorization server. Many teams buy or embed one rather than build it. I haven't seen your stack, so that is a build-vs-buy question for you.

## 2. Browser SDK calling ingest, API key pasted into the JS snippet

**Verdict: 🔴 Don't ship.**

- **The key is public.** Anything in a customer's frontend is readable by every visitor. A pasted key is a published key.
- **The skill is explicit.** "Never ship a long-lived key to a browser or other semi-trusted client: mint a short-lived scoped token server-side instead."
- **What a leak enables.** If the key is a normal secret key, anyone can read or write the customer's data. At minimum they can poison ingest with fake telemetry. You would also be teaching customers in your own docs that pasting secrets into HTML is fine.

**Options, ranked by effort (low to high):**
1. **Publishable, write-only ingest key.** Follow Stripe's `pk_` vs `sk_` model, and give it its own prefix such as `tl_pub_live_`.
   - It can only call ingest.
   - It cannot read anything.
   - It is bound to allowed origins, rate-limited, and rotatable.
   - It is explicitly documented as public.
   - A leak then costs spam at worst, and is bounded by quota and origin checks. This is the cheapest and the right default for a telemetry SDK.
2. **Short-lived token minted server-side.** The customer's backend calls Traceloom with its secret key and gets a token valid for 1-10 minutes, scoped to ingest, which it hands to the browser. This is the OpenAI ephemeral token pattern. It gives stronger containment but needs a customer backend step.

**Do not:**
- Use a secret key in the snippet, even with a "don't share this" warning.
- Rely on origin checks alone as the security boundary. Origin headers are trivially forged outside a browser. Treat them as abuse reduction on top of a write-only key.

Also add the prefix+checksum format and GitHub Secret Scanning registration. Publishable keys will still end up in public repos, but then they are harmless.

## 3. One long-lived admin key per customer CI, stored in runners

**Verdict: 🔴 Highest risk of the three, and already live. Treat it as a standing incident.**

Problems:
- **Admin scope for a pipeline job.** CI needs a narrow set of actions, such as deploy markers or config sync. An admin key turns any runner compromise or log leak into a full account takeover. This is the "trusted internal service" logic the skill rejects: small scopes beat it every time.
- **Long-lived and stored in runners.** There is no expiry, and runners are a common leak path (logs, forks, third-party actions, shared runners). The skill cites GitGuardian: 64% of valid secrets leaked in 2022 were still valid years later.
- **One key per customer.** It is shared across pipelines and people. You can't revoke one pipeline without breaking the rest, and you can't tell which pipeline did what. "Invisible infrastructure" is the skill's name for a key with no owner, scope documentation or expiry.
- **Ownership is unclear.** I don't know whether these are org-owned or tied to an individual's account. If they are personal, you also have a departed-employee exposure.

**Fix in two phases:**

Phase 1, now (days):
- **Inventory** every issued admin key: owner, last-used, consuming system.
- **Introduce service-account keys.** These are decoupled from any human's employment and are the skill's correct default for unattended workloads.
- **Scope them restrictively.**
  - Use a coarse scope set (read vs write, per product area) with a restrictive default.
  - Use one key per pipeline per environment.
  - Make fail-open scope defaults impossible: omitting scopes must not mean full access.
- **Add expiry and rotation.**
  - Use an atomic roll with a dual-key overlap of 24 hours to 7 days.
  - Delete the old key only after last-used shows zero traffic.
  - Aim for roughly 90 days for third-party integration keys. This is a practitioner convention, not a standard.
- **Migrate customers off the admin key.** Announce a deprecation window with a self-service migration path. Cap the window and then revoke.
- **Revoke immediately, with zero grace, any admin key found leaked or on a departed person's account.**

Phase 2, the direction to head:
- **Workload identity federation (OIDC).** The CI environment (GitHub Actions, GitLab) attests its identity and Traceloom exchanges that for a short-lived scoped token. No stored secret exists to leak. The skill flags this as the direction the industry is moving for CI. It is the highest-effort rung, so promote it once phase 1 is done.

## Cross-cutting and open questions

**Apply to all three:**
- **Storage:** hash-only (SHA-256, shown once), with an indexed `key_prefix` column and constant-time comparison.
- **Dashboard:** a label, last-used timestamp, and self-service create, rotate and revoke for each key.
- **Audit log:** every create, use, rotate and revoke event, with who and when.
- **Rate limiting:** treat key validation and creation endpoints like login endpoints.

**I need answers on these. They change the plan, and I assumed rather than asked:**
1. **Retrofit or greenfield?** How are the current keys stored: plaintext, hashed or encrypted? Roughly how many live keys exist?
2. **Is there an existing RBAC system?** If yes, scopes can reuse it and fine-grained scoping gets much cheaper.
3. **Is SOC 2 or PCI in scope?** Enterprise buyers will ask for SOC 2 Type II. That makes expiry, audit logs and evidence generation requirements rather than good practice.
4. **Ship date and engineering budget?** A hard date promotes the cheap rungs: write-only publishable keys for item 2, and scoped service-account keys for item 3 before OIDC.
5. **Do the CI admin keys belong to organizations or to individuals?** That decides whether there is also an offboarding exposure.

**Suggested order:**
1. Item 3 phase 1 (inventory and scope the live admin keys).
2. Item 2, as a publishable write-only key, before the SDK docs ship.
3. Item 1, as an OAuth authorization server.
4. Item 3 phase 2 (OIDC).

I haven't saved anything to `developer-platform-context.md`. Say so if you want the design decisions recorded there.