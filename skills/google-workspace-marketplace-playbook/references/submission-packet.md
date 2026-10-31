# Submission packet

Every figure marked `†` changes: confirm it on Google's current page before quoting it.

## OAuth verification (Verification Center)

- Brand: app name identical on consent screen, Marketplace SDK and listing; logo; support email; homepage that describes the app (not only a login page) and links the privacy policy; authorized domains verified in Search Console by a project Owner or Editor.
- Privacy policy: on the homepage's domain, same URL everywhere, says how the app accesses, uses, stores and shares Google user data, and carries the Limited Use statement below.
- Scope list: every scope the code requests, nothing more. Delete OAuth clients not ready for production from the project.
- Up to three doc links for the features using the scopes.
- Restricted: the permitted app type from "What features will you use?"; leave it empty when unsure and Google assigns it. Gmail allows email clients, email backup, productivity add-ons (CRM, mail merge, AI summaries) and reporting for the user; never one-time exports. Drive allows sync or backup of Drive files, productivity apps handling files through their UI, and sharing or security reporting; never backing up your own app data to Drive.

### Justification template

```
<scope> lets <feature name> <user-visible action>. Users <what they see>.
<narrower scope> cannot work because <specific failure>.
```

```
// ✓ Good - names the feature, the screen, and why the narrower scope fails
gmail.send lets "Send follow-up" email a quote from the deal page. Users click Send and see the
message in Gmail Sent. gmail.compose is broader than needed: the app never reads or edits drafts.

// ✗ Bad - restates the scope and promises future use
We need gmail.modify to access Gmail and for upcoming inbox features.
```

### Demo video checklist

- Unlisted YouTube link; English consent screen (language switch bottom left).
- Full grant flow from your app's button, including Sign in with Google if used.
- Consent screen shows the app name; the address bar shows the OAuth client ID.
- One segment per sensitive or restricted scope showing the feature using it; every OAuth client if several.
- If any data trains a personalized model, the user's explicit consent to it on screen.

### Limited Use statement (site or in app)

Also required: an in-app disclosure of what data is used and why, shown right before the consent request (never only in the privacy policy); help docs on how users delete their data; consent requested in context for each agentic capability (MCP tool, skill) before it first touches user data.

```
The use of information received from Google Workspace scopes will adhere to the Google User
Data Policy, including the Limited Use requirements.
```

## CASA (restricted scopes only)

- Starts on Trust & Safety's email, after the rest of verification.
- Google assigns AL1 or AL2†; an authorized lab runs it; existing ISO 27001 or SOC 2 can shorten it through the accelerator.
- Developer pays the lab. Google charges nothing itself; labs set prices. Practitioner reports put assessments at about $500 to $4,500†, and TAC Security's 2026 list prices ($675 AL1, $5,400 AL2†) show AL2 can exceed that. Labs quote 2-6 weeks†.
- Revalidate every 12 months† after the letter date; a new restricted scope may force an early one.
- Required measures include OAuth tokens encrypted at rest, managed keys, and prompt-injection protection for AI features.

## Marketplace SDK and store listing

- App Configuration: visibility (permanent), install setting, integrations (Workspace add-on deployment ID, Editor add-on script ID and version, Chat API configuration, Drive API, web app universal nav URL), scopes identical to the consent screen, trader status and developer address for the EEA, a deliverable developer email (rejections and enforcement land there).
- Listing: name ≤50 characters†, Google product names only in the branding guidelines' "for Gmail™" form with attribution ("Gmail™ is a trademark of Google LLC"), since the create-listing help says to avoid them: expect reviewer questions; short description ≤200 characters† and a different detailed one; icons and screenshots that show the real app; Terms, Privacy and Support URLs that open the right pages.
- Pricing: Google bills nothing. State that you are the seller, the total price with mandatory fees (no drip pricing), how usage pricing is calculated, renewal terms, and the UK 14-day cancellation right for subscriptions.
- Reviewer access: a test account on your service with sample data, and steps to reach every scoped feature.
- Draft testers: up to 100†, Gmail accounts only for public listings, plus an opt-out URL.

## Per-integration review criteria (pre-check)

- Chat app: unprompted welcome message distinct from Help; a Help command; replies every time it is addressed; a delay notice past 2 seconds†; notifications can be turned off; DM support (Google's recommendation, and what lets admins install it for users); no staging URLs.
- Editor add-on: Apps Script V8 runtime; menus from `onInstall` and `onOpen`; errors in dialogs; confirmation before overwriting content; one blue primary action.
- Workspace add-on: homepage card; welcome card whose sign-in page names your service as a third party; Gmail universal actions (Sign out, Support) work.
- Meet add-on: works with third-party cookies off; One Tap plus Sign in with Google; license needs and pricing link stated.
- Drive app: files go to a picked or app-specific folder, never dumped in My Drive; no Chrome extension manipulating Drive pages.
- Web app: the universal navigation URL opens a working app, not a marketing page.

## Admin-facing doc snippet

```
OAuth client ID: <id>.apps.googleusercontent.com
Scopes: <list, one line each with the feature that needs it>
Admin install: Admin console > Apps > Google Workspace Marketplace apps > Install app > Admin install.
Restricted services: mark the client ID Trusted under Security > API controls.
```

## Featuring gates (cannot be bought)

- Security verification badge: CASA AL2†, up to 3 weeks† to appear, per Cloud project.
- Editor's choice: Workspace add-on, individually installable, free or free trial, 100,000 installs† (10,000 and rating 4+ if published in the last 6 months†).
- Recommended for Google Workspace: yearly application, AL2 if accepted.
