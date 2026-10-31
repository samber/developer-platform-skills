# Pagerline Slack Marketplace plan: sanity check and submission checklist

**Verdict: don't submit Monday.** Three things block it, and the SREcon date is not reachable by listing.

## 1. Do this first (this week)

1. **Recruit 8 more real workspaces now.** You have 2 that count, and the gate is 10†.
2. **Cut `users:read.email` and `channels:history` (user token) from the request.** Details are in section 3.
3. **Reset the SREcon plan to "coming to the Slack Marketplace".** Section 5 has the timeline.

## 2. Install gate: you have 2 of 10

| Workspace | Counts? |
|---|---|
| 2 pilot customers | Yes, if used in the last 28 days† |
| 2 Developer Program sandboxes | No, sandboxes are excluded |
| 2 of your own test workspaces | No, reviewers expect the app proven where it wasn't built |

Slack blocks submission below **10 active workspaces†** and the count must hold through the whole review. Pilot as an unlisted distributed app until then.

The launch is inside three months, so I moved design-partner recruiting to the top. Rank the sources like this:

1. Existing customers already asking for Slack (your two pilots, plus any others).
2. Design partners recruited for the pilot.
3. Staff or partner teams on their own paid workspaces.

New installs of unlisted apps get 1 request/minute and 15 objects† on `conversations.history` and `conversations.replies`. Pagerline's shipped features don't read history, so this shouldn't hurt you. It would hurt if you kept `channels:history`.

## 3. Scope table

| Scope | Token | Methods | Shipped feature | Verdict | Enhanced review |
|---|---|---|---|---|---|
| `chat:write` | bot | `chat.postMessage` (and `chat.update` if the timeline edits in place) | Posts incident timelines to a channel | **Request, required** | No |
| `commands` | bot | Slash-command payloads (no Web API method) | `/pagerline ack` | **Request, required** | No |
| `channels:history` | user | `conversations.history` | None. Your app posts and acks, it doesn't read the channel | **Drop** | Yes (`*:history`) |
| `users:read.email` | bot | `users.info`, `users.lookupByEmail` | None. CRM sync is next quarter | **Drop** | No |

- **`users:read.email`** is a roadmap scope. Reviewers approve what they can test, so it gets the submission returned. Adding it later means a resubmission (up to 6 weeks for updates†) plus a reinstall in every workspace. It also needs explicit user consent before you email Slack users, and your privacy policy would have to cover the CRM sync.
- **`channels:history` as a user token** fails twice. User tokens pass only when the app must act as that user, and `*:history` triggers enhanced review. Your stated reason ("read the incident channel as the responder") describes no feature that exists today.
- **If a shipped feature does read channel messages**, use the bot token, fetch on demand rather than storing copies, and expect a longer review. Tell me and I'll redo the table.

Justifications to paste in. Each names the feature, the trigger, and what is kept:

```
chat:write (bot) - Posts the incident timeline to the channel an admin picks during Pagerline setup, and updates that message as the incident progresses; the app posts nowhere else.
commands (bot) - Provides /pagerline ack, which lets a responder acknowledge an incident from the channel; the reply is visible only to that responder.
```

Also check the privacy model: no user, guest, or Slack Connect member sees an incident or message Slack would hide from them.

## 4. Submission checklist

Owners are roles because I don't know your team. Replace them with names.

**A. Engineering**
- [ ] Keep one manifest in the repo. Create `pagerline-dev` (distribution off, `/pagerline-dev`), `pagerline-staging` (distribution on, never listed), and production. Each app gets its own signing secret, client secret, and token store.
- [ ] Apply manifests from CI. The configuration token expires after 12 hours†, so rotate it with `tooling.tokens.rotate`.
- [ ] Remove test slash commands. Make `/pagerline` reply to `help` and ephemeral by default.
- [ ] Check notifications: configurable channel, no `#general` default, no `@channel`. This is an incident tool, so confirm paging never uses `@channel`.
- [ ] Add onboarding for the installing user and first-time users, with next steps and support. Home tab shows support and pricing, or turn it off. Messages tab answers DMs, or turn it off.
- [ ] No auto-joining channels. Verify requests with the signing secret, use OAuth `state`, TLS 1.2+, never log tokens.
- [ ] Clear the automated checks.
- [ ] If you enable token rotation, enable it on staging first. It is irreversible.

**B. Pages (marketing/product)**
- [ ] Landing page built for the Slack app (not a doc or repo): overview, how it works in Slack, install path, post-install success page, privacy link.
- [ ] Support page: email or form that needs no account, 2-business-day response†. GitHub issues alone fail.
- [ ] Privacy policy: Slack data collected, use, retention, access/deletion requests, email or web-form contact, and a statement on data received but unused (payload IDs, logs).
- [ ] `slack-app-id` meta tag on every page of your domain.

**C. Listing**
- [ ] Name: service first, Slack second ("Pagerline incident timelines for Slack").
- [ ] Short description of 10 words or fewer. Long description with no keyword stuffing or superlatives.
- [ ] Screenshots at 1600x1000 (8:5), JPG or PNG under 2 MB, showing the app inside Slack.
- [ ] Pricing label.
- [ ] Optional: a 30–90 second public YouTube video with captions.
- [ ] Never write "Slack-approved", "certified", or "endorsed".

**D. Test information**
- [ ] An install path reviewers run themselves (staging app link). Don't send Slack workspace logins, because reviewers can't use them.
- [ ] Pagerline test accounts with dummy incidents, on a paid tier if needed, plus accounts on every third-party service you connect.
- [ ] Video demo: install and OAuth, setup, an incident posted, `/pagerline ack`, uninstall.
- [ ] Security contact (email and phone), architecture diagram, one test account per permission role.

**E. Security & Compliance (security lead, self-certified, shown on the listing)**
- [ ] Developer, HQ, terms URL.
- [ ] Data: retention, storage and encryption, data-center locations, hosting provider, sub-processors.
- [ ] Certifications held (state honestly), deletion procedure, HIPAA yes/no.
- [ ] SSO/SAML, security contact, vulnerability disclosure program covering the Slack app, bug bounty, token rotation yes/no.
- [ ] Every answer matches the privacy policy and landing page.
- [ ] AI section only if a feature sends Slack data to an LLM. See assumptions below.

## 5. Timeline

Today is Fri 2026-10-30. "Next Monday" is 2026-11-02. SREcon is about 2026-12-04 (5 weeks out).

| Step | Estimate |
|---|---|
| Recruit 8 more active workspaces | Earliest realistic submit: early to mid December |
| Preliminary review | Up to 10 business days† |
| Functional review (new app) | Up to 10 weeks†, can't be expedited |
| One returned round | Add about a preliminary cycle |
| **Earliest approval** | **About late Feb to March 2027** |

This is my estimate. Read the live estimate on the submission page and re-plan from it.

Even a Monday submission, which the gate blocks, couldn't land before SREcon. Approval and publishing are separate, so you choose the publish date after approval. For SREcon:

1. Announce "Pagerline is coming to the Slack Marketplace".
2. Take pilot sign-ups, which also feeds the install gate.
3. Publish on approval.
4. Don't send general-audience traffic to the unlisted app.

Staying unlisted isn't a way out. Slack's API terms treat the Marketplace as the channel for commercial apps. "Customers create an app from our manifest" counts as commercial distribution too.

## 6. After listing

- The live app is locked. New features or scopes (like `users:read.email` next quarter) need a resubmission with a video and the staging app. Updates take up to 6 weeks†. Ask existing workspaces to reinstall through App Home or a message.
- Never put an unreviewed scope in the live install URL, because installs fail.
- Irreversible switches:
  - Token rotation.
  - The move from classic to granular permissions.
  - Deactivate Public Distribution, which a listed app can't use.
- Answer support within 2 business days†. Keep developer, support, and security contacts current. Add a second collaborator on the app.
- Track installs and uninstalls yourself (OAuth install ledger, `app_uninstalled`). Don't count on Slack for analytics.
- Slack delists without notice for a broken landing page or install flow, an abandoned app, or a substantial change shipped without review.
- Visibility, best first:
  1. The `slack-app-id` meta tag.
  2. Direct install from the listing.
  3. Add to Slack in your product settings.
  4. Asking Slack to feature the app (one-shot, so save it for a launch with public material).

## Assumptions I made (correct me)

1. No shipped feature reads channel history or user emails.
2. No feature sends Slack data to an LLM, so the AI disclosures don't apply. If one does, they do, and the review looks at it hard.
3. Your two pilots were active in the last 28 days.
4. Customers don't need Enterprise Grid or Slack Connect. If they do, test both before submitting.
5. Pagerline isn't on Slack's unsuitable list. It doesn't export or back up messages, move money, or run scripts.

† Verify against the current Slack Marketplace docs. Slack changed its install gate twice in the past year, and its review durations and rate limits change often.