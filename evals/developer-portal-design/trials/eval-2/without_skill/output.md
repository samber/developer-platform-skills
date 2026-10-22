# Partner developer portal: plugin architecture and navigation

## Recommendation

⚠️ **Don't open the internal Backstage instance to partners. Run a second, partner-only instance built from the same monorepo and the same plugin skills your platform team already has.**

Why the shared instance is risky:

- **No tenancy model.** Backstage has one global catalog graph. Hiding 90 internal services from 40 partners relies entirely on the permission framework. That framework is opt-in per plugin, and any plugin that forgets to check it leaks data.
- **Sensitive catalog content.** The catalog holds internal owners, on-call links, repo URLs, dependency graphs, and Kubernetes and CI annotations. Partners shouldn't see any of that.
- **Mutating plugins in the same process.** Scaffolder, Kubernetes, and CI plugins are installed and may be reachable. An external-auth bug becomes an internal-compromise path.
- **Identity mismatch.** Backstage sign-in resolvers map a login to a `User` entity. Partners are not employees, so you'd be inventing fake users inside your org catalog.

Two things I'm assuming, so correct me if either is wrong:

- You have an API gateway or can buy one (Kong, Apigee, AWS API Gateway, or similar). **Backstage should not issue or validate keys.** The gateway does that, and the portal is its UI.
- Partners authenticate through a dedicated external IdP, not your employee SSO.

| Option | Verdict |
|---|---|
| A. Same instance + external auth layer | 🔴 Works on day one, but the leak risk is permanent and every future plugin needs a partner-exposure review. |
| B. Separate partner Backstage instance | 🟢 Recommended. Isolated blast radius, reuses team skills and plugin code. |
| C. Gateway vendor's built-in portal (Kong, Apigee, Zuplo, and so on) | 🟠 Cheapest if docs needs are modest. Worth comparing if the platform team doesn't want a second Backstage to run. |

## Architecture (option B)

```
Partner browser
   │  developers.<company>.com
   ▼
WAF / CDN ──► Partner IdP (OIDC, MFA, invite-only, org claim)
   │
   ▼
Partner Backstage (separate deploy, DB, secrets, no route to internal network)
   ├─ frontend: stripped sidebar, partner plugins only
   └─ backend plugins:
        auth ─────────── OIDC + custom sign-in resolver → partner User/Group entity
        permission ───── deny-by-default policy + entitlement rule
        catalog ──────── API/System entities only, filled by a one-way provider
        api-docs ─────── OpenAPI / AsyncAPI renderer
        techdocs ─────── prebuilt in CI, read from object storage
        partner-keys ─── custom: key lifecycle via gateway admin API
        partner-usage ── custom: per-key analytics from gateway
        partner-changelog custom: versions and deprecations
        notifications ── deprecation and incident notices
        │
        ├──► Gateway admin API (create, rotate, revoke keys; read usage)
        ├──► Postgres (partner DB, metadata only, no secrets)
        └──► Object storage (TechDocs output, published specs)

Internal side (one-way, push only):
CI on API repos ──► validates + publishes OpenAPI spec and docs, tagged
                    partner-visibility ──► partner catalog / storage
```

### Design rules

1. **Publish, don't expose.** The partner catalog never reads the internal catalog live. CI on each API repo pushes specs and docs to a staging bucket. An `EntityProvider` in the partner instance turns them into `API` and `System` entities. Nothing is published unless the entity carries an explicit visibility annotation, for example `partners.<company>.com/visibility: public` or a list of partner slugs.
2. **Install only what partners need.** Don't install Scaffolder, Kubernetes, Tech Radar, org or ownership graphs, or CI plugins. A hidden menu item is not a control. A plugin that isn't in the backend can't be called.
3. **Deny by default.** A custom `PermissionPolicy` returns DENY for everything except an allowlist of catalog read, TechDocs read, and the partner plugins' own permissions. A conditional rule `isEntitledTo(partner)` filters API entities. Each partner sees only the products they're contracted for.
4. **Identity model.** Each partner is a `Group` (`partner-<slug>`). Individuals are `User` entities created by invite. The sign-in resolver rejects any login that doesn't map to one. There is no guest access, no self-registration, and no second auth provider. A partner admin role can invite and remove colleagues. 40 partners is small enough to onboard by hand.
5. **Secrets never persist in the portal.** The `partner-keys` backend calls the gateway to mint a key and returns it to the browser once. Postgres stores only metadata: key ID, label, partner, environment, scopes, created at, expiry, created by, revoked at. The gateway's own audit log is the record of truth.
6. **Isolation.** Separate DB, separate cloud account or project if possible, separate CI pipeline, and no network path to internal services.

### Custom plugin scope

| Plugin | Does | Key decisions |
|---|---|---|
| `partner-keys` (front + back) | Create, label, rotate, and revoke keys. Sandbox and production are separate. Shows the secret once. | Max keys per partner. Production keys may need approval. Scopes are limited to the partner's entitlements. Rotation has an overlap window. |
| `partner-usage` | Request counts, error rates, and throttling per key, over 7 and 30 days. | Read from gateway analytics and cache. Don't build your own metering. |
| `partner-changelog` | Per-API version, deprecation date, and sunset date. | Drives notifications and the "next steps" banner on deprecated APIs. |
| `partner-entitlements` | Maps partner to API products and environments. | Source of truth is the gateway or CRM. Sync it, don't hand-edit it in the portal. |
| Policy module | Deny-by-default plus `isEntitledTo`. | Needs tests proving partner A can't read partner B's entities. |

Off-the-shelf pieces: catalog, api-docs, TechDocs (`builder: external`), notifications, search (scoped to the partner catalog and docs).

## Partner-facing navigation

```
Home
 ├─ Welcome, status banner, "your next step" checklist
 └─ Quick links: Get a sandbox key · Getting started · Support

APIs                      ← catalog filtered to entitled APIs
 ├─ My APIs (list, with version and lifecycle badges)
 └─ API detail: Overview · Reference (OpenAPI) · Try it (sandbox) ·
                Changelog · Docs

Guides                    ← TechDocs
 ├─ Getting started (first call in 10 minutes)
 ├─ Authentication and API keys
 ├─ Rate limits and quotas
 ├─ Errors and retries
 ├─ Webhooks and events
 ├─ Versioning and deprecation policy
 └─ Go-live checklist

API Keys
 ├─ Sandbox
 └─ Production              (scopes, expiry, rotate, revoke)

Usage                       ← per key, per API

Changelog and Deprecations

Support
 ├─ Contact / open ticket
 ├─ Status page (external link)
 └─ Contract and SLA contacts

Team and Settings           ← partner admin only
 ├─ Members and invites
 └─ Notification preferences
```

Navigation choices:

- **Keys are top-level.** Self-serve keys are the headline ask, so they shouldn't hide inside a profile page.
- **Sandbox first.** The first-run checklist walks partners through a sandbox key, a first call, and then a production key request.
- **Search is scoped** to entitled APIs and guides only.

## Open questions for the platform team

1. Which gateway do you use, and does its admin API support per-consumer keys, scopes, and analytics reads?
2. Do production keys need human approval, or are they instant?
3. Do all 40 partners get the same API set, or is entitlement per partner?
4. Do you need a sandbox with fake data? If so, who owns it?
5. Who handles partner support and incidents, and what is the SLA?

## Rollout

| Phase | Scope |
|---|---|
| 1. Foundation | Partner instance, IdP, deny-by-default policy, publish pipeline, one pilot API and docs |
| 2. Self-serve keys | `partner-keys` with sandbox keys, entitlements sync, audit logging |
| 3. Pilot | Three to five friendly partners, then fix friction |
| 4. Full rollout | All 40 partners, `partner-usage`, changelog, notifications |
| 5. Hardening | Pen test, key-rotation drills, runbook for revoking a leaked key |

🎯 Before go-live, add a test suite that signs in as partner A and verifies no entity, doc, key, or usage data from partner B or from internal services is reachable through the UI or the backend APIs.

I haven't looked at your actual Backstage setup, so check the isolation claims against your instance (version, installed plugins, current auth provider) before committing to this design.