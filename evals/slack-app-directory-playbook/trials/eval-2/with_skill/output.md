**Don't resubmit with item 1 only. Fix all three first, then resubmit once.**

Why:
- Preliminary review checks listing, links, scope reasons and install access together. Items 2 and 3 are in that same pass.
- Every resubmission at this stage resets your queue position. Preliminary takes up to 10 business days†.
- Resubmitting now returns the same two failures, and you wait up to 10 business days† twice.
- Items 2 and 3 are small. In my estimate they take 2 working days, not a sprint.

**Plan: resubmit Wed 2026-11-04.**

1. **Today, about 1–2 hours: item 1, scope reasons.**
   - List each scope your shipped features call. Drop any scope for a feature that does not exist yet.
   - Rewrite each reason as one sentence with three parts: the feature, the user action that triggers it, and what the app does with the data. Never restate what the scope does.
   - Copy-pasted Slack definitions are the "bad" example in Slack's own guidance.
   - Illustrative examples for Tallyho (swap in your real scopes):
     - `chat:write` (bot): "Posts each team's compiled standup digest to the channel the admin picks in `/tallyho setup`; the app posts nowhere else."
     - `im:write` (bot): "Opens a DM with each member at their configured standup time to ask the three questions; no other DMs are sent."
   - Avoid `*:history` scopes if you can. They trigger enhanced review. If a feature needs one, name the feature and say the message text is not stored.
   - Mark scopes that only enhance the core experience as optional (`bot_optional`, `user_optional`). Never move a core scope there.

2. **Monday, about 1 day: item 2, landing page.**
   - A GitHub README fails the rule. The page must be built for the Slack app, not a doc or repository.
   - Put it on your domain with these parts:
     - overview
     - how it works in Slack
     - the install path
     - a post-install success page with next steps
     - a privacy-policy link
     - what each optional scope unlocks
   - Add the `slack-app-id` meta tag to every page on your domain. It takes minutes, and Slack uses it to suggest the app when your links are shared.

3. **Monday, about 1–2 hours: support (it will fail next).**
   - GitHub Issues alone fails. Add an email or form that needs no new account, with a 2-business-day† response.
   - Check the privacy policy covers all of these:
     - data collected
     - use
     - retention period
     - access, transfer and deletion requests
     - an email or web-form contact
     - data received but never used
   - Make the policy say what Tallyho does with Slack data. A policy silent on Slack data is a common return cause.

4. **Tuesday, about half a day: item 3, testing access.**
   - Your demo workspace login is useless. Reviewers cannot log into any Slack workspace, yours included. That is the "unable to access" note.
   - Replace it with three things:
     - **An install link.** Use a staging app made from your manifest. Set distribution on, keep it unlisted, and send the link only to reviewers.
     - **A Tallyho test account** loaded with dummy data. Add one account per permission role, and a paid tier if the app needs it.
     - **A video, 30–90 seconds.** Show install and OAuth, setup, a full standup cycle, and uninstall.
   - Put all three in the Testing Information field.
   - If Tallyho connects to Jira, Linear or similar, each needs its own test account.

5. **Tuesday, about 1 hour: pre-submit checks.**
   - Remove test slash commands.
   - Every slash command answers `help`.
   - Onboarding exists for the installer and for first-time users.
   - No `@channel`, no `#general` default.
   - Fill the Security & Compliance answers so they match the privacy policy and the landing page.
   - Check your active-workspace count (see questions below).
   - Diff your manifest against the live app with `apps.manifest.export`. That diff is what reviewers test.

6. **Wed 2026-11-04: resubmit once.**
   - If preliminary uses its full window†, the decision lands about 2026-11-18.
   - Functional review follows and takes up to 10 weeks† for a new app. Resubmitting there keeps your place.
   - Plan for one more returned round.

**If you must split the work:** do item 1 today and hold the submission until items 2 and 3 are done. Do not resubmit between steps.

**Two questions that change the plan:**
1. How many workspaces used Tallyho in the last 28 days, sandboxes excluded? Slack blocks submission below 10†, and you must keep that count through the review. I assumed you have 10 or more. If not, you need a pilot first, and this timeline is moot.
2. Is there a launch date or event pinned to this? With functional review up to 10 weeks†, a date inside about 3 months needs the "coming to Slack Marketplace" plan. Do not send the general audience to the unlisted app.

Assumptions I made: Tallyho sends no Slack data to an LLM, and you have no Enterprise Grid or Slack Connect customers. Tell me if either is wrong, because both add review checks.

† Verify against current Slack Marketplace docs. Slack has changed its install gate twice in a year.

**Next (2 minutes):** open your app's OAuth & Permissions page and paste the scope list here. I'll draft the justifications.