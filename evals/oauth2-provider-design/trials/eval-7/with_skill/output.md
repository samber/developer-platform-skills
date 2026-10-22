# Verdict: do not sign off

The plan has three problems, and the second is blocking. One of the three ("same bar for every app") is a fairness instinct that works against you here.

## What's wrong

### 1. A single questionnaire bar is the wrong design, and it's not even-handed

The skill's rule is to scale review depth to data sensitivity, never one bar for all apps. Every program it studied does this:

- Google tiers scopes into non-sensitive, sensitive and restricted.
- Microsoft keeps three separate signals.
- Salesforce, Shopify and Atlassian all scale review to the data an app can reach.

Equal paperwork for unequal risk is not neutral. A calendar-sync app and an app that reads every employee's expense reports pass the same check. If a bulk-access app leaks tokens, every customer's trust in the Verified badge goes down with it.

You can keep the fairness goal without one bar. Make the rule objective and keyed to scope, not to the app. Any app requesting a scope of the same class gets the same review, and nobody is favoured.

### 2. Self-attestation can't gate apps that read other users' data

This is the blocking issue. Your description says some apps will read the whole vendor list and every employee's expense reports. That is access to other users' data and PII, not the installing admin's own records.

The skill treats that as the bright line. At that point every studied program requires independent testing: Google's CASA, Microsoft's M365 Certification, and Salesforce's Security Review, which includes cross-org isolation and OAuth token handling. Microsoft says outright that its attestations are not independently verified.

The cautionary case is Salesloft Drift (August 2025). A stolen-OAuth-token campaign hit 700+ organizations. Salesforce then forced mandatory PKCE and rotation, with de-listing as the penalty, enforced May 11, 2026. A questionnaire would not have caught that class of failure.

### 3. One "Verified" badge conflates three different things

Identity verification, self-attestation and independent audit are different signals. Microsoft's docs say the identity badge "doesn't imply or indicate quality criteria." One checkmark on every listing makes buyers read "audited" into "filled in a form."

That is a liability for a spend-management product. A customer's finance team will treat "Verified" as an assurance you haven't actually made.

### 4. A warning banner is a weak control

The skill's point is that a banner alone doesn't change developer behavior, and admins click through banners. Four gaps:

- **No enforced ceiling for unverified apps.** Google caps unverified apps at 100 users for the app's lifetime, plus 7-day test-token expiry. Without a cap, "unverified" just means "installed anyway."
- **No runtime enforcement.** Declarations drift. Reject any scope request that isn't a subset of what was approved at registration. Google's warning fires on exactly that divergence.
- **Banner and consent gate are different things.** Microsoft's real lever is blocking consent beyond basic profile for unverified publishers in risk-managed tenants. Make the bottom tier a gate, not decoration.
- **Admins are missing.** In B2B an org admin gates the install. They need an approval queue and org-wide grant review. This is a first-class part of the design, not an add-on for the first enterprise customer who asks.

### 5. One-shot review isn't enough

A single review at submission never gets rechecked. Google, Microsoft and Atlassian reassess annually, and Salesforce re-reviews on new versions. Add re-review when an app adds a scope or ships a version that changes data access.

## What I'd ship instead

| Tier | Trigger | Requirement | Badge |
|---|---|---|---|
| 1 | Every listed app | Publisher identity verification: domain plus verified business account, no fee. It also gets the testing lane, with a hard user cap. | "Identity verified" |
| 2 | Scopes limited to the installing user's own or the org's low-sensitivity data | Tier 1 plus a security questionnaire (self-attested). Review it, don't just collect it. | "Security self-attested" |
| 3 | Any scope reaching other users' data, bulk vendor data or employee expense reports | Tier 2 plus a third-party security assessment, repeated annually and on new scope. The developer pays the assessor. | "Independently assessed" |

Tier 3 costs developers months and money. Google's CASA runs about $500+ for the scan tier and $5,000+ for the pentest tier, per community reports. That cost is acceptable because it applies only to the apps that can do real damage.

Supporting rules:

- **Scopes:**
  - Use `resource:action` naming with read/write split and read-only defaults.
  - Do not ship a single broad catch-all scope.
  - Bind each scope to a token type (app-identity versus user-delegated) from day one.
  - Never repurpose an existing scope's meaning.
- **Protocol:**
  - PKCE (S256) for every client.
  - No implicit or password grants.
  - Exact redirect-URI matching.
  - Refresh-token rotation with reuse detection and a 10-30 s grace window.
- **Registration:** manual registration with a review step. No open dynamic client registration.
- **Consent screen:**
  - Write plain-language copy per scope.
  - Always diff granted scopes against requested scopes on the server, since partial grants are possible.
  - Show only the net-new scope on re-consent.
- **Admin surface:** an approval queue, org-wide grant review, and a separate admin-only tier for app-identity permissions.
- **Launch triage:** with 60 apps, classify each app's requested scopes into a tier now. Apps that need Tier 3 and aren't ready can list as "Identity verified" with reduced scopes, or wait.

## Open questions

These affect the design, so please answer them:

1. Is this greenfield, or do OAuth clients already exist? If so, which grants are live?
2. Do apps act only on behalf of a signed-in user, or also with their own identity (bot or org-wide tokens)?
3. Do any scopes reach regulated financial data? That would move DPoP or mTLS into scope.
4. Who approves installs: end users, org admins, or both?
5. Are you building the authorization server yourself or on an identity product?
6. What is your timeline? Assessment adds months, so it decides whether Tier 3 apps launch on day one.

I haven't verified the vendor-doc figures or current OAuth 2.1 draft status beyond what the skill and its reference file state. I took them from there as given.