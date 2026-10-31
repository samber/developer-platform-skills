# Flowmesh Slack Marketplace submission plan

Following `slack-app-directory-playbook`. Figures marked † are Slack figures to verify against current Slack Marketplace docs, because Slack has changed its install gate twice in a year.

## Verdict: submit, but not as described

Three parts of the brief would get the submission refused or returned. The plan below removes them.

| # | Item | Verdict | Why |
|---|---|---|---|
| 1 | "Archive every channel message to Google Drive nightly" template | ❌ **Block it, and ship none like it** | Slack's unsuitable list bars apps that export or back up message data. Automation platforms must block templates that export, back up or bulk-delete Slack data. One such template can fail the whole app. |
| 2 | "Connect once, every Flowmesh user in the company builds flows on it" | ❌ **Change the auth model** | Playbook rule: never share one user's Slack authorization with others, and never expose the Slack token to your users. |
| 3 | "Slack-certified integration" on the launch page | ❌ **Drop the phrase** | The Marketplace Agreement forbids implying Slack endorsement. Slack calls its security review "not a certification". |

Rewrite the launch copy as: "Now available on the Slack Marketplace" (after approval), or "Coming to the Slack Marketplace" before approval. Don't use "certified", "approved by Slack" or "endorsed". Tell marketing now so no asset ships with the phrase.

### Fixing the shared-connection design

- Replace "one person connects, everyone uses it" with a workspace-level bot install. An admin or owner installs the app once, using the bot token.
- Each Flowmesh user who acts as themselves goes through their own authorize step. No one reuses another person's user token.
- Flows run as the bot, which is the default the review prefers. Flowmesh never hands raw Slack tokens to flow builders.
- Reviewers also check the privacy model. A flow builder must not be able to read a private channel, message or file that Slack would hide from them. Guests and Slack Connect members are included in that check.

### Fixing the Google Drive template

- Remove the archive template from the Slack connector, and block any user-built flow that does a bulk history export, backup or bulk delete. Enforce this in the product with a technical block on Slack-history-to-storage destinations, not just a doc line.
- Keep Slack as a trigger or action for event-driven flows. Examples: a new message matching a rule creates a Drive doc, a reaction files one message, `/flowmesh` runs a flow.
- Keep the Google Drive side of that template available for other sources. Flowmesh can still archive other services to Drive, just not Slack message streams.
- The nightly archive likely needs `*:history` scopes. Those trigger enhanced review and are exactly what the playbook says to avoid collecting in bulk.

## Assumptions (not asked, flagged)

1. **Features:** triggers from Slack events, bot actions that post messages, and a slash command. I'm assuming no AI features, so no LLM disclosure is needed. If any feature sends Slack data to an LLM, tell me, because it adds AI disclosures and an unsuitable-list check.
2. **Stage:** building, with an unlisted pilot not yet at the install gate. I don't know your active workspace count.
3. **Launch date:** none given. I assumed the target is 3 months out, which promotes design-partner recruiting to start this week. The install-gate ranking would change if the answer differs.
4. **Enterprise Grid / Slack Connect:** unknown, assumed possible for target customers. I'm treating org-ready deployment and Slack Connect behaviour as part of the review, and the test plan below includes both.

## Install-gate plan (10 active workspaces†)

Slack blocks submission below **10 active workspaces†** (used in the last 28 days, sandboxes excluded). Hold that count through the whole review. Ranked by efficiency:

1. **Existing Flowmesh customers asking for Slack.** Highest yield. Ship an **unlisted distributed pilot** app (the `-staging` app below) to them.
2. **Design partners** recruited for the pilot. Start this week.
3. **Staff or partner teams** on their own paid workspaces.

Never count sandboxes or your own build and test workspaces. Reviewers expect the app proven where it was not built.

Pilot rate limits: unlisted apps get 1 request/minute and 15 objects† on `conversations.history` and `conversations.replies`. Drive pilot flows from events, not history polling, or warn pilot customers.

## Environments as code

- Keep one manifest template in the Flowmesh repo. Apply it with `apps.manifest.update` or the Slack CLI. Never edit app settings by hand.
- Per environment, change only the display name, slash command (`/flowmesh-dev`), and the redirect, request and event URLs.
- Create three apps from it:
  - `flowmesh-dev`: distribution off.
  - `flowmesh-staging`: distribution on, never listed. Send its link only to pilot testers and reviewers.
  - `flowmesh` (production).
- Give each app its own signing secret, client secret and token store.
- Apply manifests from CI with a configuration token. It expires after 12 hours†. Rotate it with `tooling.tokens.rotate` and store the refresh token.
- Before every resubmission, diff the template against the live app (`apps.manifest.export`). That diff is the change list reviewers test.

## Scope table (draft, fill in from the shipped feature list)

Request only scopes for features that exist today. I'm assuming the features in assumption 1; replace any row whose feature isn't shipped.

| Scope | Token | Methods / events | Feature | Justification | Required | Enhanced review |
|---|---|---|---|---|---|---|
| `chat:write` | bot | `chat.postMessage` | "Post to Slack" action | Posts a message to the channel the flow builder picks in the flow editor; posts nowhere else. | Required | No |
| `commands` | bot | slash command | `/flowmesh` | Runs or lists flows when a user types `/flowmesh`; replies ephemerally. | Required | No |
| `channels:read`, `groups:read` | bot | `conversations.list` | Channel picker | Lists only channels the installing user can see, to fill the channel dropdown. Nothing stored. | Required | No |
| `reactions:read` or `app_mentions:read` | bot | events | Event trigger | Fires a flow when a user reacts or @-mentions the app. Only that event is processed; message text is not stored. | Optional | No |
| `team.billing:read` | bot | `team.info` / billing | Plan check | Checks the workspace plan right after OAuth; revoke the token on free workspaces. | Required for automation platforms | No |
| `channels:history`, `groups:history`, `files:read` | — | — | **Do not request** | The archive template was the only reason for these. | — | Yes, avoided |

Rules applied:
- Drop duplicates across bot and user tokens, and default to the bot token.
- Never request ineligible scopes (`identity.*`, `search:read`, `triggers:*`, `workflow.steps:execute`) or `admin.*` (partner program only).
- Mark scopes that only enhance the core experience as optional (`bot_optional`). Never move a core scope there to lighten the consent screen.
- Event triggers on message content need `*:history`. If a "when a message is posted" trigger is core, it triggers enhanced review. Decide that before submitting. Scope it to channels the bot was invited to, and state in the justification that message text is not stored.

## Submission packet checklist

| Item | Owner | Notes |
|---|---|---|
| Listing name, short description (10 words or fewer), long description, icon | Marketing | Service name first ("Flowmesh for Slack"), no superlatives, no "certified". |
| Screenshots, 1600x1000 (8:5), under 2 MB | Marketing | Show the app inside Slack, not only the Flowmesh editor. |
| Pricing label | Product | Pick the Marketplace label matching your plans. Slack charges no listing fee and you bill customers yourself. |
| Landing page built for the Slack app | Marketing | Overview, how it works in Slack, install path, post-install success page, privacy link, what each optional scope unlocks. Not a doc or repo. |
| Support page | Support | Email or form needing no new account. Reply within 2 business days†. |
| Privacy policy | Legal | Must cover Slack data: what is collected, retention, access/deletion requests, contact by email or web form, data received but unused. |
| Test information | Eng | Install link to `flowmesh-staging`, plus Flowmesh and Google Drive test accounts with dummy data. Reviewers can't enter any Slack workspace, yours included. Paid tier if needed, longest trial you can grant. |
| Demo video, 30-90 s | Marketing | Install and OAuth, setup, end-to-end flow, uninstall. Public YouTube link, captions on. |
| Security & Compliance answers | Security | Self-certified, shown to customer admins. Cover retention, encryption, hosting, sub-processors, certifications held (state only what you hold), deletion procedure, SSO/SAML, security contact, disclosure program. Must match the privacy policy. |
| Security review readiness | Security | Contact with email and phone, architecture diagram, one test account per permission role. |
| In-app checks | Eng | Onboarding for the installer and first-time users, "help" reply on `/flowmesh`, ephemeral replies, no `#general` default, no `@channel`, no auto-joining channels, no posting as a user, account linking through an authorize step, signing-secret verification, OAuth `state`, TLS 1.2+, no tokens in logs. |
| Remove test slash commands, clear automated checks | Eng | Done before submit. |
| Enterprise Grid and Slack Connect tests | Eng | Required if answer 4 is yes. Verify org-ready deployment and that Connect users see nothing Slack would hide. |

## Timeline (backward from launch)

Today is 2026-10-30; dates are relative to the launch date L, since none was given.

| Step | Duration | Note |
|---|---|---|
| Remove the archive template, redesign auth, build the scope table | 1-2 weeks | Gate on this before the pilot starts. |
| Pilot to 10 active workspaces† | Depends on customers | Longest pole, so start recruiting now. |
| Submit, automated checks | Same day | Fix and resubmit. |
| Preliminary review† | Up to 10 business days | Each resubmission here resets your queue position, so fix all feedback in one pass. |
| One returned round | +10 business days | Plan for it. |
| Functional review† | Up to 10 weeks for a new app | Can't be expedited. Resubmitting here keeps your place. |
| Publish | On launch day | Approval and publishing are separate. |

Worst case is roughly 3.5 months from submission to approval. Submit at least about 15 weeks before L. If approval can't land before L, announce "coming to the Slack Marketplace", take pilot sign-ups, and publish on approval. Never drive general-audience installs to the unlisted app. Read the current estimate on the submission page and re-plan from it.

## After listing

- **The live app is locked.** Configuration, features and scopes change only through resubmission (up to 6 weeks† for updates). New features or scopes need a video and the staging app.
- **Never put an unreviewed scope in the live install URL.** Installs fail. After approval, update the OAuth URL and ask existing workspaces to reinstall via App Home or a message.
- **Irreversible switches:** token rotation (refresh within 12 hours†, persist each new refresh token, enable on staging first), classic-to-granular permissions (forces every workspace to reinstall), and Deactivate Public Distribution (uninstalls everywhere; unavailable once listed).
- **Obligations:** answer Slack within 2 business days†, keep developer, support and security contacts current, keep a second collaborator on the app, and track installs and uninstalls yourself (OAuth install ledger plus `app_uninstalled`). Broken landing page, broken install flow, an abandoned app, or a substantial unreviewed change gets the app delisted without notice.
- **Discontinuing:** give Slack 10 days' written notice†.

## Visibility

Ranked by efficiency, highest first:
1. Add the `slack-app-id` meta tag on every page of flowmesh's domain.
2. Direct install from the listing, with onboarding for installers who have no Flowmesh account.
3. "Add to Slack" in the product settings.
4. Ask Slack to feature the app, which is one-shot and editorial. Do it when launch material is public.

## Decisions for you

1. **Archive template:** confirm you'll remove it. A bulk-export feature can't be reconciled with a listing.
2. **Auth model:** confirm the bot-token workspace install replaces the shared user connection.
3. **Message-content triggers:** are they core? They decide whether you face enhanced review for `*:history`.
4. **Launch date and current active-workspace count:** these set the real schedule.
5. **Marketing:** approve the "Slack-certified" removal before any asset goes out.