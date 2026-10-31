# Play: don't flip to private. Fix the three review points and move the Cloud project into an organization. Resubmit once as a public listing.

Assumptions, since I can't ask mid-task. Correct me if any is wrong:
- It's an Apps Script Editor add-on for Sheets that calls your backend.
- Your customers are Workspace domains.
- The listing was submitted as public.
- The scopes are sensitive, not restricted. If you request any restricted scope, add CASA to the plan.

Every figure marked `†` comes from the skill's notes. Check it against current Google docs before you quote it.

## 1. Why "flip to private" won't work

- **Private listings only serve the publisher's own organization, never customers.** Your three pilot companies could not install it.
- **Visibility is permanent once saved.** If public is already saved, you can't flip it. If it isn't saved, going private locks you out of customers for good.
- **A consumer Gmail account can publish only public.** Your cofounder's personal-account project can't go private at all.

Keep it public. Fix it in place.

## 2. Step 1: move the Cloud project (do this first)

Listing, OAuth verification and CASA all key on this project. Right now your cofounder's personal account is a single point of failure. If they lose access, only a support case recovers the listing.

1. Move the **existing** project into a Google Cloud organization. Don't create a new one, or you lose the verification and review history tied to this one.
2. Set at least two Owners on the project, and enable billing.
3. Check that the Owner and contact emails are current, and that the developer email on the Marketplace SDK is deliverable. Rejections and annual CASA notices go there.
4. If the add-on still runs on Apps Script's default project, move it to a standard Cloud project.
5. Check that the Search Console domain verification for your homepage is held by an Owner or Editor of the project.

## 3. Step 2: one fix per review point

### "Users see two permission prompts"

The usual cause is scope drift between the three places that must be identical.

1. Diff the scope lists in three places:
   - the add-on manifest `oauthScopes`
   - the Marketplace SDK scopes
   - the OAuth consent screen's Data Access page
2. Make all three identical, with nothing extra. Drop any scope that no shipped feature calls.
3. Write a table of feature → API method → minimum scope → tier. Use the narrowest scope per feature, `.readonly` where nothing writes. Read the Sheets scope page for the tier of each one.
4. Add a written justification for each sensitive scope:
   ```
   <scope> lets <feature> <user-visible action>. Users <what they see>.
   <narrower scope> cannot work because <specific failure>.
   ```
5. Test a partial grant: a user who ticks only some scopes must see a re-prompt for the missing ones, not a broken add-on. Reviewers reject apps that break on a partial grant.
6. Retest on a clean test account and on a domain-installed account. After an admin install, users must never see a consent prompt.

### "Privacy policy link goes to our help center"

1. Publish a dedicated privacy policy page on the same domain as your homepage.
2. State how the app accesses, uses, stores and shares Google user data. Include the Limited Use statement:
   > The use of information received from Google Workspace scopes will adhere to the Google User Data Policy, including the Limited Use requirements.
3. Use the same URL in three places: the homepage link, the consent screen, and the Marketplace SDK and listing.
4. Make the homepage describe the app. A login page alone fails. Link the policy from it.
5. Confirm the policy says no ads, no human reading without consent, and no AI training on customer data.
6. Add an in-app disclosure of what data is used and why, shown right before the consent request. Add help docs on how users delete their data.
7. Re-run brand verification if the app name or logo changed. Publish the branding within 7 days† of passing.

### "Reviewers couldn't get past our login"

1. Create a dedicated reviewer account on your service with sample data already loaded.
2. Remove everything that stops a reviewer:
   - MFA
   - email-confirmation loops
   - CAPTCHA
   - IP allowlists
   - expiring trials
3. Write step-by-step access instructions that reach every scoped feature. Put them in the submission, not in a support ticket.
4. Check that the welcome card's sign-in page names your service as a third party and that Sign out and Support work.
5. Re-record the demo video: full grant flow from your button, consent screen showing the app name, address bar showing the OAuth client ID, one segment per sensitive scope.
6. Smoke-test the credentials from a clean browser the day before you submit, and again the day you submit.

## 4. Step 3: how to run the pilot

Two things are true at once:
- The Marketplace review can't approve you before OAuth verification completes.
- Testing status is a named rejection cause. Switch to **In production** before submitting.

Options, best first:

1. **Pilot after approval, by admin install.** Each customer's Workspace admin installs the add-on domain-wide. Users get no consent prompt. This is the pilot you want, and it needs the public listing approved.
2. **Pilot through your web app's own OAuth flow while you fix things.**
   - Set the project to **Testing** with the three customers' people as named test users.
   - Expect a tester warning screen, a user cap†, and short-lived tokens†.
   - This covers only what your web app does. It does not deliver the Sheets add-on to those users.
   - Switch back to **In production** before you resubmit.
3. **Draft testers on the listing.** Up to 100†, but they must be Gmail accounts. Customer Workspace users can't preview this way.
4. **Last resort: let customers use the unverified app.** Sensitive scopes unverified cap at 100 users† over the app's lifetime, with no reset until verified. Customers see the "Google hasn't verified this app" screen, which hurts trust. I don't recommend it for three customer companies.

Tell your three customers now that add-on access arrives after approval. Offer them the web-app pilot in the meantime.

## 5. Plan

Today is Sat 2026-10-31. These dates are estimates.

| When | What | Owner |
|---|---|---|
| Mon Nov 2 – Fri Nov 6 | Move the project into an organization, set two Owners, enable billing | You + cofounder |
| Nov 2 – Nov 6 | Align scopes in all three places, rebuild the scope table, test the partial grant | Engineering |
| Nov 2 – Nov 6 | Publish the privacy policy and fix the homepage | You |
| Nov 9 – Nov 12 | Build the reviewer account and instructions, re-record the demo video | Engineering |
| Nov 4 – Nov 12 (optional) | Web-app pilot in Testing status | Engineering |
| Fri Nov 13 | Switch to In production, run the final checklist, resubmit once | You |
| Nov 13 – Dec 11 | Review: 2–4 weeks† for sensitive scopes | Google |
| Within a day of any mail | Answer Trust & Safety. **The review pauses until you reply.** | You |
| After approval | Admin-install pilot at the three customers | You + customer admins |

Allow one more rejection round of 2–4 weeks†, and Google's holiday slowdown. Worst case is January. Tell the three customers "December, not November."

## 6. What pauses the clock

- Unanswered Trust & Safety email
- Testing status at submission
- Verification not yet complete
- A non-deliverable developer email
- Reviewer login failing during the check

## 7. Questions for you

1. Is it an Editor add-on or a Workspace add-on, and which Sheets scopes does it request now?
2. Was the listing saved as public already?
3. Do you have any restricted scopes? If so, CASA adds weeks† and a lab fee.