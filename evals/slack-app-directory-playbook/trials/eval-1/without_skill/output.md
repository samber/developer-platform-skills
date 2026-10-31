I couldn't reach Slack's docs (the fetch was denied). Everything below comes from my memory of Slack's Marketplace guidelines, so check the items marked ⚠️ against the current page before Monday.

# Verdict: don't submit Monday

Two things will likely get the submission rejected, and one decision protects your launch date.

## Problems with the plan

1. ❌ **Install count.** Slack requires a minimum number of active workspace installs, which I recall as 5. ⚠️ Verify the number and whether your own and sandbox workspaces count.
   - Your 6 installs are 2 internal test workspaces, 2 Developer Program sandboxes and 2 real pilots.
   - I recall reviewers not counting your own or dev workspaces, which would leave you with 2.
   - Fix: get 3 or more real customer workspaces installed and actively using the app, or confirm in writing with Slack that the sandboxes count.

2. ❌ **`users:read.email` without a feature that uses it.** Slack reviews on least privilege and wants every scope tied to a shipped, demonstrable feature.
   - The CRM sync doesn't exist until next quarter.
   - Fix: remove it now and add it later. Adding a scope after approval makes users reinstall or re-consent, but that is cheaper than a rejection.

3. ⚠️ **`channels:history` as a user token.** This is the scope most likely to draw questions.
   - Reviewers will ask why a bot token can't do the job. A bot in the incident channel could read it with `channels:history` as a bot scope, without impersonating a user.
   - If the bot approach doesn't work, write down why. The reason is probably that the responder's own permissions should govern what is read.
   - Also check which channel types you need. Incident channels are often private, which needs `groups:history`, and `channels:history` alone won't cover them.
   - Say plainly in the submission how long you store message content and who can see it.

4. ⚠️ **Timeline.** Review typically takes weeks, and each rejection restarts a cycle. A Monday submission leaves about 5 weeks, which only works if the first pass is clean.
   - Plan for 2 or 3 review rounds, not one.
   - Don't plan the SREcon announcement around the listing going live that day.
   - Have a fallback: a direct install link with "Add to Slack" on your site, and "Marketplace listing coming" in launch copy.

## Revised plan

| When | Action |
|---|---|
| This week | Drop `users:read.email`. Decide on bot vs user token for history. Recruit 3+ real workspaces. |
| Next 1–2 weeks | Finish the checklist below. Run the reviewer test script end to end on a clean workspace. |
| Week 2–3 | Submit once the install and activity threshold is met. |
| Launch | Direct install link is the primary path. The Marketplace listing is a bonus if approved. |

## Submission checklist

**Eligibility**
- [ ] Active real-customer installs meet the current minimum (⚠️ check the number and the activity window).
- [ ] The app has been in use for the required period.
- [ ] Distribution is enabled and the OAuth flow works on a fresh workspace.
- [ ] You are not using a deprecated API (classic apps, legacy RTM, and so on).

**Scopes and permissions**
- [ ] Every scope maps to a live, demonstrable feature, with a one-line justification per scope.
- [ ] `users:read.email` is removed.
- [ ] The token model is justified for `channels:history`, including private-channel handling.
- [ ] Slash command `/pagerline ack` has a clear description and usage hint.
- [ ] Event subscriptions request only what's needed.

**Security and compliance**
- [ ] Request signing is verified on every inbound request.
- [ ] Tokens are encrypted at rest.
- [ ] Token rotation or revocation on `app_uninstalled` and `tokens_revoked` is handled.
- [ ] You can state what message data you store, for how long, and how to delete it.
- [ ] You can answer "who at your company can see customer Slack data?"
- [ ] Your security contact and vulnerability disclosure process are public.

**Listing assets**
- [ ] The app name doesn't use Slack trademarks.
- [ ] Short and long descriptions are written for users, not for you.
- [ ] You have an icon at the required size, with no Slack logo.
- [ ] Screenshots are at the required dimensions, show the real UI, and contain no customer data.
- [ ] You have a privacy policy URL (it must cover Slack data), a support page or email you actually monitor, and a terms of service URL.
- [ ] A landing page or docs site is live.

**Functionality review**
- [ ] The app loads fast and handles errors gracefully.
- [ ] The slash command returns a response within the 3-second window, or uses an ephemeral acknowledgment.
- [ ] The app handles rate limits (HTTP 429 and `Retry-After`) and has no unbounded retry loops.
- [ ] A bot that is removed from a channel fails gracefully.
- [ ] Install, uninstall and reinstall all work.
- [ ] Onboarding doesn't depend on talking to your sales team.

**Reviewer package**
- [ ] A step-by-step test script a reviewer can follow without help.
- [ ] Reviewer access to a test account or sandbox, where the app can be exercised without a paid contract.
- [ ] A way to generate a sample incident in a test environment.
- [ ] A demo video, if the form asks for one.

## Questions I need answered

1. Are your pilot customers on enterprise-grade workspaces (Enterprise Grid, restricted admin approval)? That can add install friction.
2. Do you need private-channel history, or only public incident channels?
3. Can you get 3 or more paying or pilot workspaces by about Nov 13?

If you answer these, I'll draft the scope justifications and the reviewer test script.