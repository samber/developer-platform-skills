# Slack Marketplace submission packet

Everything the preliminary review checks before a reviewer touches the app. Items marked † change often: verify against the current Slack Marketplace guidelines.

## Contents

1. Scope justifications
2. Listing fields
3. Pages
4. Test information
5. Security & Compliance answers
6. In-app checks reviewers run
7. MCP server apps

## 1. Scope justifications

One sentence per scope: the feature, the user action that triggers it, and what the app does with the data. Never restate the scope's definition.

```
// ✓ Good - names the feature, the trigger and what is kept
chat:write (bot) - Posts the incident summary to the channel a user picks in /acme-alert setup; the app posts nowhere else.
channels:history (bot) - Reads messages in channels the bot was invited to, only to detect "ACME-1234" ticket keys and unfurl them; message text is not stored.

// ✗ Bad - restates the scope, or justifies a feature that does not exist yet
chat:write - Allows the app to send messages.
reactions:write (bot) - Needed for the emoji voting we plan to add.
```

## 2. Listing fields

- **Name**: unique and spellable; integrations name the service first and Slack second ("Task notifications for Slack", never "Slack task notifications").
- **Short description**: 10 words or fewer, plain text, shown in search and on profile cards.
- **Long description**: the integrated service in one line, the problem, how the app works in Slack; Slack formatting and standard emoji codes allowed; no keyword stuffing, no superlatives.
- **Icon**: distinctive, high resolution, little text.
- **Screenshots**: 1600x1000 px (8:5), JPG or PNG under 2 MB, showing the app inside Slack, never only your own UI. Blurry, off-ratio or unrelated images get the submission returned.
- **Video** (optional): 30-90 seconds, public YouTube link (not a channel or playlist), captions on, ads off, the production app in a realistic workspace.
- **Pricing label**: Paid; Paid with free trial; Free and paid plans available; Free; Included with service subscription. Slack charges no listing fee and does not bill for Marketplace apps; you bill customers yourself.
- **Languages**: declare one only when every message, interactive component and related page works in it; keep one language across descriptions, images, video and pages.
- **Direct install** (optional): the URL must 302 to `slack.com/oauth/v2/authorize`, and onboarding must handle installers with no account on your service.
- **AI apps**: say on the listing and landing page that LLM output can be inaccurate; agent-container apps add that a paid Slack plan is needed for the agent.

## 3. Pages

- **Landing page**: public, built for the Slack app (never a PDF, doc or repository), with overview, how it works in Slack, the install path, a post-install success page with next steps, and a privacy-policy link. Explain what each optional scope unlocks.
- **Support page**: public; email or form that needs no new account (GitHub issues alone fail); response within 2 business days†.
- **Privacy policy**: data collected, use, retention period, how to request access, transfer or deletion, an email or web-form contact (a postal address alone fails), and a statement on data received but never used (slash-command payload IDs, logs).

## 4. Test information

- An install path reviewers run themselves. Never send credentials to your Slack workspace: reviewers cannot use it.
- Test accounts made for testing, on your service and every third-party service the app connects, loaded with dummy data. Paid tier if the app needs it; the longest trial you can grant.
- Video demo: install and OAuth, setup, end-to-end use, uninstall. For updates: the new feature and how each new scope is used.
- Updates with new features or scopes: a staging app cloned from the published manifest, installable from the Testing Information field.
- Security review readiness: a security contact (email and phone), an architecture diagram, one test account per permission role.

## 5. Security & Compliance answers

The fields are self-certified and shown on the listing's Security & Compliance tab, where customer admins read them before approving the app; the field list below follows that tab† and may differ in the form. Write them for the buyer's security team, and make every answer match the privacy policy and landing page.

- General: developer, headquarters, terms of service URL.
- Data: retention, archiving and removal, storage and encryption, data-center locations, hosting provider, sub-processors.
- Compliance: certifications held, deletion-request procedure, HIPAA yes or no.
- Security: SSO and SAML, security team, security contact, vulnerability disclosure program covering the Slack app, bug bounty, third-party authorization, token rotation yes or no.
- AI: model used, retention and how the LLM uses user data, LLM data tenancy, LLM data residency.

## 6. In-app checks reviewers run

- Onboarding for both the installing user and first-time users, with next steps and support; Home tab shows support and pricing, or is turned off.
- A "help" reply on every slash command; Messages tab answers DMs when message input is on, or is turned off.
- Slash commands prefixed with the app name, ephemeral by default; shortcuts start with a verb and acknowledge within 3 seconds.
- Notifications configurable and batched; no `#general` by default, no `@channel`, no posting as a user.
- Account linking through an authorize step, never by mapping users by hand; explicit consent before emailing Slack users.
- No auto-joining channels.
- Agent or Assistant UI: disclaimer that the agent needs a paid Slack plan, the rest of the app works on free plans, Assistant Overview of 25 words or fewer, a "help" reply in the Chat tab, a thread status while responding, metadata stored instead of Slack data.
- Enterprise installs: after OAuth, check the installing user's domain matches the customer's expected domain.
- Requests verified with the signing secret, OAuth `state` used, TLS 1.2+, tokens never logged or exposed.

## 7. MCP server apps

- `mcp:connect` bot scope, optional unless MCP is the only function; HTTPS server URL on a domain you control that passes TLS verification.
- OAuth to your server uses the redirect `https://oauth2.slack.com/external/auth/callback`; run Fetch Tools in App Settings before submitting.
- Every tool: human-readable title, accurate description, `readOnlyHint`, valid `inputSchema`.
- Submission notes walk install, authentication, a tool call and its response; one screenshot shows a tool in a Slackbot conversation; the long description and landing page show the most-used tools.
- MCP Apps iframes show only the triggering tool's output, never your whole product, and match the tool descriptions.
- After listing, repeated tool failures switch the app off automatically.
