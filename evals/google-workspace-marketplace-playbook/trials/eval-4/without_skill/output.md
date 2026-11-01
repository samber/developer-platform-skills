# What breaks if you push the manifest on Tuesday

**Short answer:** the new scope is not a manifest change. It is a new permission grant that Google, each of the 40 org admins, and each user must approve. If you ship Tuesday morning without that groundwork, existing Docs and Sheets users get blocked from features that work today, and Calendar stays dark in most orgs.

I'm working from general knowledge of the Workspace Marketplace and OAuth verification process. I haven't checked your console, and review times and exact limits below are the parts to confirm there.

## What breaks, in order of damage

1. **Existing Docs and Sheets features stop until users re-authorize.**
   - Authorization is per script project (Apps Script) or per app (OAuth). It is not per feature.
   - Once the deployed version asks for a scope the user hasn't granted, menu items and sidebar actions throw an authorization prompt, or an auth card in a card-based add-on.
   - Users who only use the Docs and Sheets features get interrupted too.

2. **Installable triggers fail silently, if you use them.** Time-driven and `onEdit`-style installable triggers stop running for each owner until they re-authorize. The only signal is a "needs authorization" failure email, so scheduled jobs go quiet.

3. **Domain-wide installs do not inherit the new scope.**
   - An admin approved the old scope set for their org. A new scope needs a fresh admin approval.
   - Orgs that restrict third-party API access (Admin console, Security, API controls) will block users from consenting at all.
   - Some of the 40 orgs will clear this in a day. Others will need a security review that takes weeks.
   - So Tuesday will not be a clean cutover. The rollout will have a long tail.

4. **Unverified-scope friction.**
   - `calendar.events` is a sensitive scope, which means OAuth verification: a justification, a demo video of the feature in the production app, and a privacy-policy check.
   - Until the scope is verified on your Cloud project's consent screen, users see the "Google hasn't verified this app" screen, and the unverified-app user cap may apply.
   - The scope must already be on the consent screen and in the Marketplace app configuration before you deploy. If it isn't, authorization fails outright.
   - The Calendar API must also be enabled on the project, or calls fail with a 403.

5. **The Marketplace listing goes through review before it goes live.**
   - A published app's new version with new scopes, and edits to the listing text, are reviewed before they publish. Review takes days, sometimes longer.
   - Pushing code does not control what users run. They run the version pinned in the Marketplace app configuration, and changing that pinned version is what triggers review.
   - Engineering can't hit a Tuesday-morning deadline by pushing. The deadline is set by when Google approves.

6. **The description rewrite creates a mismatch in either order.**
   - Copy that mentions Calendar while the approved scope set doesn't include it fails review, and misleads users in the meantime.
   - A new scope with listing text that doesn't disclose it is a classic verification rejection.
   - The listing text, privacy policy, consent screen and demo video must all describe the same Calendar behavior.

7. **The permission wording will alarm customers.**
   - `calendar.events` shows users "See, create, change, and delete events on all calendars you can access."
   - For a Docs and Sheets add-on, that is a large jump. Customer security teams will push back, and some will want justification.
   - Check whether a narrower scope covers the feature (for example `calendar.events.owned`, `calendar.app.created`, or `calendar.freebusy`). A narrower scope means a lighter consent screen and an easier review. Confirm the current scope names in Google's scope list.

## What to do instead

**Now to Monday (get approvals while nothing user-facing changes):**
1. Confirm the narrowest scope that covers the feature.
2. Add the scope to the consent screen and the Marketplace app configuration, and enable the Calendar API.
3. Update the privacy policy, including the data-use disclosure for Calendar data.
4. Record the demo video and submit OAuth verification.
5. Submit the new version and the new listing text together, so the reviewer sees one consistent story.
6. Test the upgrade path, not a fresh install. Use a test org with an existing domain-wide install, grant the old scopes, then ship the new version. Check that Docs and Sheets features, triggers and admin approval behave as expected.

**Before approval lands:**
7. Email the admin contact at each of the 40 orgs with the exact scope, the reason, how to approve it, and the date. Give the slow orgs a head start.
8. Prepare a support macro and a help page for "Why is it asking for new permissions?"
9. Prepare a rollback plan. A rollback removes the scope but doesn't undo grants, and reverting the pinned version is the real lever.

**Tuesday (or whenever approval lands):**
10. Switch the pinned version, publish the new description, send the customer announcement, and turn on the Calendar UI.
11. Watch auth-error rates and support volume for the first 48 hours. Expect a staggered rollout across orgs.

## Decision for you

**Option A:** Move launch and the description rewrite to the day approval lands, and tell marketing the date is approval-driven. This is the safest choice.

**Option B:** Keep Tuesday as the date for the code, and keep Calendar disabled for users. Ship the description rewrite only after the scope is approved.

If a hard Tuesday date is non-negotiable, the fallback is to decouple Calendar from the existing add-on. A separate add-on or listing means existing users never face a re-consent. The cost is a second listing to review and maintain. If your backend is your own server, incremental OAuth is another option, but the scope still has to be verified.

## Open questions that change the plan
- Is this an Apps Script add-on or a card-based Workspace add-on with your own backend?
- Do you use installable triggers?
- Has the Calendar scope been submitted for verification yet?
- Do any of the 40 orgs have strict API controls?