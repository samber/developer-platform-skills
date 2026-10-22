# Verdict: don't sign off ❌

The plan treats trust as one bar. The skill's verification step says the opposite: scale review depth to data sensitivity, never one bar for all apps. Apps that read the whole vendor list and every employee's expense reports are exactly the apps a one-time questionnaire can't vouch for.

I assumed a few things the skill would normally ask you about: a B2B setup with org admins approving installs, mostly server-side apps, and no MCP or agent ecosystem yet. Correct me if any of that is wrong. It changes the details, not the verdict.

## What's wrong

**1. One bar for 60 apps hides the real risk.** 🔴
- Every program the skill studied (Google, Microsoft, Salesforce, Shopify, Atlassian) uses the same line. Mandatory independent testing starts when a scope reaches other users' data or PII, not just the installer's own records.
- Reading every employee's expense reports crosses that line. Reading the vendor list probably does too, since it's bulk org-wide data.
- Uniform treatment isn't fair to anyone. A calendar-sync app and an app holding the whole expense corpus end up with the same badge.
- Tiering isn't playing favourites. The tier follows the scope requested, not the vendor, and the same rule applies to everyone.

**2. The questionnaire is the middle rung, not the top.** 🟠
- Self-attestation is cheap (Microsoft says most attestations take about an hour) and isn't independently verified.
- As the only gate for broad-access apps, it asks the apps with the most to lose to grade themselves.

**3. One "Verified" badge conflates different signals.** 🔴
- Identity verification, self-attestation and independent audit are three different things. Microsoft says its identity badge "doesn't imply or indicate quality criteria."
- A single checkmark makes buyers read "audited" into "filled in a form."
- This is a named failure mode in the skill. It's also a liability risk for you if a "Verified" app leaks expense data.

**4. The review is one-shot.** 🟠
- Every program the skill studied reviews again: annually (Google, Microsoft, Atlassian) or on new versions (Salesforce).
- Declarations drift. An app verified in October can request more scope in March.

**5. Nothing enforces the scopes at runtime.** 🔴
- The plan reviews at submission only. The skill requires rejecting any scope request that isn't a subset of what was declared and approved.
- Google's unverified-app warning fires on exactly that divergence.

**6. A warning banner isn't a control.** 🟠
- The skill's design implications say a banner alone doesn't change developer behavior.
- The unverified lane needs a real, enforced ceiling. Google uses a named-test-user list, a 100-user lifetime cap that only verification lifts, and 7-day token expiry.
- Microsoft's real lever is a consent gate: unverified publishers can't get consent for permissions beyond basic profile in risk-managed tenants.
- Your banner covers "unverified." Under your plan, a Verified app with broad scopes has no extra gate at all.

**7. The admin surface is missing.** 🟠
- Installs in B2B workspaces have two consent surfaces: the end user and an org admin.
- Org-wide data access should need admin approval, as Microsoft does for application permissions.
- Per-scope plain-language consent copy, partial grants and a server-side diff of granted versus requested scopes aren't mentioned in the plan either.

## Recommended fix

**Tiers keyed to scope sensitivity:**

| Tier | Trigger (scope reaches…) | Gate | Badge shown |
|---|---|---|---|
| 0 | The installer's own non-sensitive data | Publisher identity verification (domain plus verified account) | "Identity verified" |
| 1 | Org data, but not bulk or other users' | Identity plus questionnaire, with re-attestation every 12 months | "Identity verified, self-attested" |
| 2 | Other users' data or PII, or bulk data (vendor list, all expense reports) | Identity, plus an independent security assessment paid for by the developer, annual recurrence, re-review on scope change | "Independently assessed" |

- **Rank scopes first.** Put each scope into a tier before you review any app, so the tier follows from the scope.
- **Show three separate signals** on the listing, not one badge.
- **Enforce at runtime.** Any scope request outside the approved declaration is rejected, and admin approval is required for Tier 2 grants.
- **Give unverified apps a real testing lane.** Named test users, a hard user cap, short token expiry and a warning screen. The banner stays, but it's the visible part of the gate.
- **Add the baseline OAuth hygiene** (the skill's step 1). PKCE on every client, exact redirect matching, ~1h access tokens, and refresh rotation with reuse detection and a grace window.

## Launch with 60 apps

- Don't hold the whole launch behind assessments. Cost and calendar are a go/no-go for developers: months, with the developer paying the assessor.
- Sort the 60 apps by requested scope now. Launch Tier 0 and 1 apps on schedule.
- Launch Tier 2 apps once assessed, or in a limited-listing state with admin-only install until they pass.
- Tell developers about the tiers in advance, with the scope-to-tier table. Apps that don't need broad scopes will drop them to avoid the cost, which also shrinks your exposure.
- Over-scoped requests are a recurring rejection reason across Salesforce, Shopify and Atlassian. Put "scope requested vs. functionality" on your review checklist.

## Why this matters

In August 2025 the Salesloft Drift OAuth-token campaign hit over 700 organizations. Salesforce then forced PKCE, rotation and de-listing penalties on its ecosystem by May 2026. Building the tiers now is cheaper than retrofitting them across 60 live integrations.

## Questions before I turn this into a full spec

1. Which of the 60 apps would sit in Tier 2, and are any already committed to a launch date?
2. Do you build the authorization server yourselves, or on an identity product? (This changes the effort ranking.)
3. Do any apps act with their own identity (org-wide bot tokens) as well as on behalf of a user?
4. Will an MCP or AI-agent ecosystem plug into this directory?

I can draft the scope-to-tier table and the listing-badge copy next.