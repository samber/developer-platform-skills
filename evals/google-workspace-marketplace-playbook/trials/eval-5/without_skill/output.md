# Marketplace rejection: fix plan and customer pilot

Caveman-lite, ADHD format. Nothing was run or read. This comes from how Google Workspace Marketplace review generally works, so check the console menu names against what you see.

## The key finding: private listing probably won't work for the pilot

- **A private listing installs only for users in the publisher's own Workspace domain.** Your three customers sit outside that domain, so they can't install it.
- **A project in a personal Gmail account has no organization or domain.** Private visibility may not even be selectable there.
- **A private listing skips Google review.** That would help you, but only if the pilot users were in your domain.

Open the Marketplace SDK Store Listing and look at the visibility options. If "Private" is greyed out or limited to your domain, use the pilot options in step 3.

## Step 0: decide who owns the Cloud project (do first)

A personal-Gmail project is a business risk, and it also blocks the other fixes.

- **Risks:** one person controls the OAuth consent screen, the verification status and the listing. If the cofounder leaves, loses the account or gets suspended, the listing goes with them.
- **Likely fix:** migrate the project into a Cloud organization your company owns. This keeps the project number, so the Apps Script link, the listing and the existing installs stay intact.
  - The cofounder must be Owner of the project.
  - Someone at your company needs Project Mover rights on the target org.
- **Fallback:** create a new project and resubmit. That loses OAuth verification and install history, and every user re-consents.
- Do this before touching scopes, because the consent screen and verification belong to the project.

## Step 1: fix the three rejection reasons (one resubmission)

**1. Two permission prompts.** Likely causes, in order. Check each one.
1. The Apps Script project is linked to a different Cloud project than the one in the Marketplace SDK. Link them to the same one.
2. The `oauthScopes` in `appsscript.json` differ from the scopes declared in the Marketplace SDK and on the OAuth consent screen. Make all three lists identical.
3. Code calls a service that needs a scope you never declared. That triggers a second prompt at first use. Declare it, or remove the call.
4. The second prompt is your own service login, such as an external OAuth or `UrlFetch` to your backend. That prompt is legitimate if it appears in your UI after the Google install prompt. If reviewers counted it, say so explicitly in the submission notes.

While there, narrow the scopes. Prefer `spreadsheets.currentonly` or `drive.file` over the full `spreadsheets` or `drive`. Narrow scopes also avoid the restricted-scope security assessment.

**2. Privacy policy goes to the help center.** Publish a dedicated policy page.
- Host it on the same verified domain as your homepage.
- Name the Google user data you access, why you access it, how you store and share it, and how long you keep it.
- Include the Google API Services "Limited Use" disclosure.
- Use the same URL in the Marketplace SDK listing and on the OAuth consent screen.

**3. Reviewers couldn't log in.**
- Create a dedicated reviewer account for your service with no MFA, no CAPTCHA, no email verification, no IP allowlist and no sales gate.
- Pre-load it with sample data so the add-on does something on the first run.
- Put the credentials and a 3-5 step walkthrough in the submission notes.
- Add an unlisted demo video showing the full flow, including consent.
- Test the login from a clean browser profile and a non-company network before submitting.

## Step 2: check the OAuth verification state

If you use sensitive or restricted scopes, the consent screen needs brand verification. That also requires the homepage and privacy policy to be on a verified domain.
- Restricted scopes (for example full Drive) add a third-party security assessment, which takes weeks and costs money.
- Another reason to narrow the scopes first.

## Step 3: pilot options for the three customers

Ranked by how fast they work and how little they depend on Google review:

| # | Option | Works for outside companies? | Caveat |
|---|---|---|---|
| 1 | **Unverified-app pilot.** Set the consent screen to External, add each pilot user as a test user, and share a test deployment or install link. | Yes | Cap of 100 test users. Refresh tokens expire after 7 days in Testing mode, so users re-consent weekly. Users see the "unverified app" screen. Fine for a short, supervised pilot. |
| 2 | **Unlisted or limited public listing.** | Yes | Still needs Google approval, which is what bounced. Only possible after step 1. |
| 3 | **Customer admins install a private app inside their own domain.** | Only if you publish separately per customer domain | Doesn't scale. Skip it. |
| 4 | **Private listing in your domain.** | No | Only for internal dogfooding. |

**Recommendation:** run option 1 now, in parallel with resubmission. Start it only after step 0, so users don't consent twice when the project moves. Give each customer a named contact and a 2-4 week window.

Two things to settle before inviting anyone:
- Tell the customers they will see an unverified-app warning, and why.
- Check your contracts or terms allow pilot data to flow through an unreviewed app.

## Order of work

1. Confirm the visibility options in the SDK (5 min).
2. Step 0: project ownership and migration.
3. Step 1: fixes, with a test pass on a fresh Google account.
4. Step 3, option 1: invite the three pilot companies.
5. Resubmit with reviewer credentials and the demo video.

## Questions for you

1. Which scopes does the add-on declare? Are any of them restricted?
2. Is it an Editor add-on or a Workspace add-on?
3. Does your company have a Google Workspace org or Cloud organization today?
4. Does the second prompt appear at install or at first run? That tells me which of the four causes it is.