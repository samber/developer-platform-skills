# Flowmesh Slack Marketplace submission plan

**Slack's Marketplace requirements change often, so I wrote this from memory, not from the live docs.** Check each rule below against the current Slack docs before you commit dates. Do that first, in week 0.

## Three problems to fix before submitting

1. **"Slack-certified integration" can't go on the launch page.**
   - As far as I know, Slack has no "certified" status or badge. Marketplace approval means the app passed review.
   - Slack's brand guidelines forbid implying endorsement.
   - Use "Available on the Slack Marketplace" after approval, with Slack's own badge assets if the guidelines allow them.
   - Don't publish any "Slack" wording on a launch page before approval.

2. **"One person connects, the whole company builds flows" is a permission-escalation risk.**
   - A flow built by user B would act with the access of user A, who did the install.
   - B could then read channels, including private ones, that B can't see in Slack.
   - Reviewers look hard at this.
   - **Decision needed:** which model do you use?
     - **Per-user authorization.** Each flow author connects their own Slack identity. This is the safest and the easiest to get approved.
     - **Shared workspace bot, with Flowmesh-side controls.** An admin chooses which channels the bot may touch. Flow authors can only pick from that list.
   - I recommend the shared bot with an admin-set allowlist. It keeps the one-connect experience and closes the escalation hole. Without both pieces, expect rejection.

3. **The nightly archive-every-message-to-Drive template is the highest review risk.**
   - It needs `channels:history`, `groups:history`, and possibly `im:history` and `mpim:history`. Reviewers push back on these scopes.
   - It is a bulk copy of customer conversations into a second system. Slack's API terms restrict bulk export and retention of message data.
   - It must honor message deletions and edits, or you hold data the author deleted.
   - It may also raise legal-hold, retention, and GDPR questions for your customers.
   - **Recommendation:** don't build the listing around this template.
     - Ship the connector first with narrow scopes, covering triggers, posting messages, and reactions.
     - Make the archive template a separate, admin-only capability. It would be public channels only, opt-in, and have deletion sync and a clear disclosure.
     - Request the history scopes only when that capability is on, or in a later update after approval.

## Assumptions to confirm (these change the plan)

- Is the Slack app already set up for public distribution with OAuth v2 and granular scopes? Or does it still use legacy tokens or a custom install?
- How many workspaces have it installed and active today? I recall Slack requiring a minimum number of active installs before review (about 10), so verify the current threshold.
- Do you receive events through the Events API over HTTPS, or through Socket Mode? Marketplace apps generally can't use Socket Mode.
- Does Flowmesh already have a privacy policy, a support page, and a security contact?

## Plan

**Week 0: decisions and fact check (owner: product lead and engineering lead)**
1. Read the current Marketplace guidelines, the app review checklist, the API terms, and the brand guidelines. Record the exact requirements.
2. Decide the permission model (problem 2) and the archive template's scope (problem 3).
3. Confirm the install-count threshold. If you're short, start a pilot to get there.

**Weeks 1–3: engineering fixes (owner: engineering)**
1. Use OAuth v2 with the minimum scopes. Write a one-line justification for each scope, because the submission form asks for one.
2. Handle `app_uninstalled` and `tokens_revoked`: delete tokens and stop flows.
3. Add token rotation if you can.
4. Respect Slack's rate limits with backoff, and honor `Retry-After`.
5. Build the admin allowlist of channels and enforce it server-side.
6. Verify request signatures on every inbound Slack call.
7. Encrypt tokens at rest. Write audit logs for who built which flow against which channel.
8. For the archive template, if you keep it: public channels only, an admin opt-in, handling of `message_deleted` and `message_changed`, and a retention setting.

**Weeks 2–4: listing and legal (owner: marketing, legal, support)**
1. Write the app description, the icon, screenshots, and a short demo video.
2. Publish a privacy policy that names the Slack data you access, where it's stored, how long, and how to delete it.
3. Publish a support page with a monitored channel.
4. Prepare a security contact and a short security questionnaire answer set. Reviewers may ask about SOC 2, encryption, and subprocessors.
5. Marketing drafts the launch copy with the approved wording only (problem 1).

**Week 4: internal review (owner: security)**
1. Run through the Slack review checklist against a test workspace. Use a fresh install, then uninstall and reinstall.
2. Test as a non-admin Flowmesh user to confirm the escalation path is closed.
3. Fix gaps before submitting. A rejection can cost weeks.

**Week 5: submit (owner: product lead)**
1. Submit with working test credentials and step-by-step review instructions.
2. Explain scope choices in the form, especially anything touching message history.
3. Name one person to answer reviewer questions within a day.

**Weeks 6–9: review and iteration**
1. Expect at least one round of feedback. Budget time for scope reductions.
2. If the history scopes are rejected, ship without the archive template and re-request later.

**Launch (after approval)**
1. Update the launch page with "Available on the Slack Marketplace" and the official badge if allowed.
2. Announce, then watch install, uninstall, and error rates for 30 days.

## Risks and fallbacks

| Risk | Likelihood | Fallback |
|---|---|---|
| Reviewers reject history scopes | High if archive stays in scope | Remove the template from the first submission |
| Install threshold not met | Medium | Pilot with customers to reach it before submitting |
| Shared-credential model rejected | Medium | Move to per-user authorization |
| Marketing publishes "certified" early | Medium | Legal sign-off on all Slack wording before publication |

## Questions for you

1. Which permission model do you want: per-user, or shared bot with an admin allowlist?
2. Do you want to keep the archive template in the first submission, or split it out? I recommend splitting it out.
3. How many workspaces have the connector installed today?
4. Who is the single reviewer contact?