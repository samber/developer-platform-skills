# Review: Traceloom auth plans

**Verdict:** none of the three ships as written.

| # | Plan | Verdict | Severity |
|---|------|---------|----------|
| 2 | Paste API key into browser SDK | ❌ Blocker, unless the key is a new write-only type | 🔴 |
| 3 | One long-lived admin key in CI | ❌ Existing exposure, needs a migration | 🟠 |
| 1 | Extend API keys for partner apps | ⚠️ Right idea, wrong mechanism | 🟠 |

The root problem is that one credential type (the API key) is stretched across three different jobs. Each job needs its own credential type.

| Job | Credential |
|-----|-----------|
| Browser sends events (public by nature) | Publishable, ingest-only key |
| CI automation (a machine acting for the customer) | Scoped key or short-lived federated token |
| Partner app reading dashboards (acts for a user) | Delegated token (OAuth) |

## 1. Partner apps reading dashboards: use OAuth, reuse your scopes

Your instinct to avoid a whole new auth system is good, but extending API keys leads there anyway.

### Why extending API keys falls short

- **Short expiry needs a renewal path.** A partner can't ask the customer for a new key every few minutes. A renewal path is a refresh token, so you end up rebuilding OAuth.
- **Per-app revocation needs an app identity and a grant record.** That is a client registry plus a "customer X authorized app Y" table. API keys have neither.
- **There is no consent step.** Today the customer would copy a key into a partner's UI. That trains customers to hand secrets to third parties, and it is phishable.
- **"Per-request scopes" is the wrong unit.** Scopes belong to the grant: what the customer approved. Per-request narrowing is an optional extra on top, via token exchange.
- **There is no "on whose behalf".** A dashboard read acts for a specific user with specific permissions. An API key identifies only the tenant, so the audit trail can't say "app Y acted for user Z".

### What to build instead

1. **Authorization server.** OAuth 2.1 authorization code with PKCE. Use an off-the-shelf server (Ory Hydra, Keycloak, or your cloud's) rather than writing one.
2. **Client registry.** Partners register apps with redirect URIs and a vetting step. Rate limits are per app.
3. **Consent screen.** It lists the scopes in plain language. A tenant admin can restrict which apps users may authorize.
4. **Tokens.** Access tokens live 5–15 minutes. Refresh tokens rotate with reuse detection.
5. **Revocation.** Revoke per grant using RFC 7009. The customer sees an "Authorized apps" page with a revoke button, and you can also kill an app globally.
6. **Resolution at the gateway.** Both API keys and tokens resolve to the same principal: `{tenant, user, app, scopes}`.
7. **Scopes.** Start with read-only, such as `dashboards:read`. Add resource-level limits (which dashboards) later.
8. **Audit log.** Record the app, user, and scope on every call.

### What carries over from your plan

Your scope vocabulary, your enforcement layer, and your revocation UI idea all carry over. Only grant issuance is new. Keep API keys for the customer's own server-to-server use.

## 2. Browser SDK: a key in frontend JS is public

Anything in a customer's frontend is readable by every visitor. So the key you document there must be safe to leak.

### The requirement

- **Never document pasting the existing API key.** If that key can read data or touch config, you are telling every customer to publish their account.
- **Issue a separate publishable key type**, like Stripe's `pk_` or a Sentry DSN:
  - It has a distinct prefix, e.g. `pk_ingest_`, so humans and secret scanners can tell it apart from a secret key.
  - It can only ingest. It cannot read, list, or configure anything.
  - It is bound to one project or environment.
  - There can be many per project, with rotation and revocation without downtime.

### Abuse controls

A leaked ingest key still allows abuse, so add these:

- **Per-key rate limits and daily quotas.** This stops quota exhaustion and billing attacks.
- **Customer-set spend caps.** Over-cap events are dropped, not billed.
- **Origin allowlist.** Enforce it via CORS and an `Origin` check. This only stops casual misuse, since non-browser clients can spoof `Origin`.
- **Strict validation.** Enforce payload size and schema limits.
- **Poisoning defenses.** Flag anomalous volume, and let the customer filter or quarantine events by key.
- **No data in responses.** Ingest responses must never echo stored data.
- **Opt-in server relay.** Offer it for stricter customers. Their backend mints a short-lived ingest token (minutes) and the browser uses that.

Ship the SDK only after the publishable key type exists.

## 3. CI on one long-lived admin key: reduce blast radius, then retire it

This key is already in the wild, so it is the one that needs a migration plan.

### Why it is a problem

- **Full admin from any leak.** A leak through logs, a forked-PR exfiltration, a compromised runner, or a departing employee gives full admin access.
- **No expiry, so no forced rotation.** Rotation is painful because everything shares one key, so it never happens.
- **No attribution.** You can't tell which pipeline did what.

### Fix, in order of effort

1. **Add scoped, per-pipeline keys.** Cover what CI actually does, such as deploy markers and alert-rule uploads, instead of admin.
2. **Add expiry and overlap.** Cap lifetime at about 90 days, and let two keys be active at once so rotation has no downtime.
3. **Add visibility.** Show last-used time, last-used IP, and a per-key audit log. Add optional IP allowlisting.
4. **Support secret scanning.** Use a recognizable key prefix and register with GitHub secret scanning and GitLab. Leaked keys then get flagged or auto-revoked.
5. **Add workload identity federation (best end state).**
   - The runner presents its OIDC token (GitHub Actions, GitLab) and exchanges it for a short-lived Traceloom token.
   - You bind it to claims such as repo, branch, and environment.
   - No stored secret exists on the runner at all.
6. **Migrate the existing keys.**
   - Inventory the issued admin keys.
   - Notify customers with a migration guide.
   - Set a deprecation date, then stop issuing admin keys for CI.

## Suggested order

1. **Now:** confirm the SDK will not use an existing key. Define the ingest-only key type (item 2).
2. **Next:** scoped keys, `last_used` tracking, and key prefixes (item 3, steps 1–4). These also give you the key infrastructure item 2 needs.
3. **Then:** the OAuth authorization server for partners (item 1), before any partner builds on API keys. Once partners depend on keys, the migration gets expensive.
4. **Later:** OIDC federation for CI, and the admin-key sunset.

## Questions to confirm

- Can your current API keys read data, or only ingest?
- Does any ingest endpoint return stored data?
- How many customers hold the admin CI key, and is any rotation process in place?