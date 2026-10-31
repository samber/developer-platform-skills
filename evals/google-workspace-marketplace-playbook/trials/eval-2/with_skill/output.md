# Ferrovia: Google Workspace Marketplace path for full Drive scanning

## Verdict ❌

**The Internal plan does not work, and it is not faster.**

- **Internal only covers one organization.** It works only for users of the organization that owns the Cloud project. Ferrovia sells to about 60 other firms, so none of their users can use an Internal app.
- **Internal apps fail Marketplace review.** The admin domain-wide install you are counting on goes through that listing.
- **Admin install does not skip verification for your scopes.** It removes the per-user consent prompt for an approved app. A domain-install-only app skips brand verification only. "Scan every contract" needs a restricted Drive scope, and restricted scopes still require OAuth verification plus a paid CASA assessment.
- **The unverified-app route caps out at 100 users†.** That cap is for the app's lifetime and never resets. Sixty firms will pass it in the first few weeks.

Your instinct on the user side is right: after an admin installs an approved app domain-wide, users never see a consent prompt. You still have to get approved first.

## Assumptions (I could not ask)

1. **App type:** a web app, listed on Marketplace with a universal navigation URL.
2. **Data flow:** contract content reaches your servers and probably an AI model.
3. **Installers:** firm admins install for the whole firm.
4. **Stage:** building, with no verification started and no launch date.
5. **Cloud project:** ownership is unknown. If one person owns it, moving it into an organization with two owners is step one.
6. **Platform:** all 60 firms run Google Workspace. If some run Microsoft 365, they need a different integration.

## Scope table

| Feature | API method | Minimum scope | Tier | Justification |
| --- | --- | --- | --- | --- |
| Enumerate and scan every contract in the firm's Drive | `files.list`, `files.get` (download and export) | `drive.readonly` | **Restricted** | `drive.readonly` lets "Contract scan" read the content of every file in the firm's Drive. Admins see an index of clauses and risks. `drive.file` cannot work because it only reaches files a user opened or picked, and the product must find contracts nobody picks. |
| Write the analysis report back to Drive (optional) | `files.create` | `drive.file` | Non-sensitive | The app can only touch files it created. |

- **Do not request `drive`.** Ferrovia never edits customers' contracts, so use the `.readonly` variant.
- **Do not request `drive.metadata.readonly` as well.** `drive.readonly` already covers listing and reading.
- **Declare the same scopes in three places:** code, the Marketplace SDK, and the consent screen's Data Access page. Any drift shows users the unverified screen or a second consent prompt, which is a top rejection cause.

## Fastest realistic path

The restricted rung cannot be avoided for the core product. The only way to move faster is to start every gate in parallel, in this order:

1. **Project setup (this week).**
   - Move the Cloud project into an organization with two owners and billing enabled, before saving Marketplace visibility.
   - Visibility is permanent once saved, so choose public. Customers cannot use a private listing.
2. **Brand verification (this week).**
   - Verify the domain in Search Console.
   - Use a homepage that describes the app and links the privacy policy, with the same privacy URL on the consent screen.
   - Publish branding within 7 days† of passing.
3. **Data access request in the Verification Center (target: submitted in about 2 weeks).**
   - Include the scope justification above.
   - Include an unlisted English demo video: the full grant flow from your app's button, the app name on the consent screen, the OAuth client ID in the address bar, and one segment showing the scan feature.
4. **App type.**
   - Drive permits sync or backup, productivity apps that handle files through their UI, and sharing or security reporting.
   - Contract analytics most plausibly counts as a productivity app, but this is a judgment call. If unsure, leave the field empty and let Google assign the type.
5. **CASA (restricted scopes only).**
   - You cannot book it yourself. Trust & Safety emails you when to start, as the last step of verification.
   - Google assigns AL1 or AL2†, and may raise the level as users grow†.
   - Budget roughly $500 to $4,500†, and note that TAC Security's 2026 list prices run from $675 (AL1) to $5,400 (AL2)†.
   - Labs quote 2 to 6 weeks†. Existing ISO 27001 or SOC 2 can shorten it.
   - Required measures include OAuth tokens encrypted at rest, managed keys, and prompt-injection protection for any AI features.
   - Revalidate every 12 months†.
6. **Marketplace SDK and listing (in parallel with steps 3 to 5).**
   - Enable the Marketplace SDK (not the Marketplace API).
   - Set the install setting to Individual + Admin, the default.
   - Add a test account with sample contracts and steps to reach the scan feature.
   - Handle partial grants by detecting missing scopes and re-prompting per feature. Reviewers reject apps that break on partial grants.
7. **Submit.**
   - The listing cannot be approved before OAuth verification completes, so the slower gate sets your date.
   - Answer Trust & Safety mail fast, because review pauses until you reply.

## Rough timeline†

These are estimates from the skill's ranges, not Google commitments. Verify each against Google's current docs.

| Step | Duration |
| --- | --- |
| Verification, restricted (several weeks†) | about 4 to 6 weeks |
| CASA | 2 to 6 weeks, starting after Trust & Safety's email |
| One rejection round | allow about 2 weeks |
| Marketplace review | runs in parallel |

- **Earliest realistic approval:** about late January to February 2027, assuming submission in mid-November.
- **Holiday risk:** the year-end holidays may slow both Google and the labs.
- **Do not promise firms a go-live before the Letter of Validation arrives.**

## Pilots before approval

- **Use OAuth Testing status** with named test users, through your own web app's OAuth flow.
  - Limits: a tester warning, a user cap, and short-lived tokens†.
  - Keep it to one to three design-partner firms.
- **Do not onboard the 60 firms on an unverified app.**
  - The 100-user lifetime cap† would run out, and there is no reset.
  - Switch to In production before submitting. Leaving Testing status on is a named rejection cause.
- **Draft testers on a public listing must be Gmail accounts.** Workspace-domain customers cannot preview the listing.

## Constraints that will matter to law firms

- **Limited Use applies to all Drive data.**
  - Use it only for user-facing features, with no ads.
  - No human reads the data without the user's consent for specific data.
  - No training or improving AI models beyond that user's own personalized model.
  - If contracts feed a shared model, drop that design now.
- **Disclosure and consent.**
  - Add an in-app disclosure right before consent, plus help docs on deleting data.
  - Add the Limited Use statement to the site or app.
  - Request consent in context for each agentic capability before it first touches data.
- **Admin documentation.**
  - Publish the OAuth client ID, the scopes, and the install path (Admin console > Apps > Google Workspace Marketplace apps > Install app > Admin install).
  - Tell admins to mark the client ID Trusted under Security > API controls if they restrict API access.
  - Expect law-firm security teams to ask for the CASA letter anyway.
- **Future scope changes.**
  - Any new sensitive or restricted scope means new verification before you ship it.
  - Each admin must re-authorize the new scopes in the Admin console.

## What I could not settle

- **Domain-wide delegation.** I did not evaluate service-account domain-wide delegation as an alternative. The skill does not cover it for third-party SaaS, so verify it against Google's current docs before ruling it in or out.
- **Marketplace billing and featuring.** Google bills nothing, so Ferrovia bills firms directly, and featuring cannot be bought.

## Questions that would change the plan

1. Do all 60 firms run Workspace, or do some run Microsoft 365?
2. Who owns the Cloud project today?
3. Is there a hard launch date? A date inside 6 weeks cannot be met on the restricted rung, so the date moves rather than the scope.
4. Does contract content go to an AI model, and whose?