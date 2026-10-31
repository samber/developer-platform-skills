# Submission packet

Load before a Teams app, a linked SaaS offer or a co-sell solution goes to review. Each section lists what reviewers check and the defect they most often return.

## Teams app: before submitting

- **Names match everywhere.** App name, description, developer name, terms of use and privacy URLs, and icons are identical in the manifest and Partner Center. A mismatch fails validation.
- **Name rule.** Never copy an existing app name; prefix or suffix a common noun with your brand ("Acme Tasks", not "Tasks"); never use "Teams" or "Microsoft", or Beta, Dev, Preview or UAT.
- **Value.** A tab must add value beyond hosting your existing website; notification-only bots and unfurl-only apps get flagged as low value.
- **Description.** No "MS", "MSFT", "O365" or bare "Teams"; no "#1", "best" or competitor comparisons; disclose every external account or admin consent the app needs.
- **Screenshots.** At least three, captioned, showing the app inside Teams on each client it supports.
- **Domains.** `validDomains` and `messageHandlers` list only production domains you control.
- **Bots.** Send a welcome message; answer "Hi", "Hello" and "Help"; never dead-end on irrelevant input; never request payment details in chat.
- **Mobile.** Hide what mobile does not support; never sell features on mobile.
- **Sign-in.** Clear sign-in, sign-out and sign-up paths; state complex setup in the description.
- **No ads.** Advertising is banned in the app.
- **Manifest.** Latest schema; channel-enabled apps need schema 1.25 or later for new submissions†.

## Teams app: notes for certification

- Two or more test accounts for collaborative scopes, none behind MFA, none needing your team online (testers work across time zones).
- Setup steps, a demo video link for complex flows, and the single sign-on fallback flow.
- Support, privacy and EULA links that resolve without login. Missing links are a top rejection cause.

## Linked SaaS offer

- The SaaS offer is live (not preview), has at least one priced plan, and uses per-user pricing.
- The manifest declares `subscriptionOffer` as `publisherId.offerId`; "Additional purchases" is set to Yes.
- Admin and non-admin users can buy; admins can bulk-buy in the Teams admin center; "Set up now" reaches the landing page.
- Assigning, removing and reassigning licenses shows correct counts and users in your app.
- Notes for certification carry an end-to-end functional document, SaaS configuration steps and license-management instructions.
- Publish both the app and the offer yourself, or hold written authorization from the other publisher.

## SaaS offer certification

- API tokens minted with the same tenant ID and Entra app ID entered in Technical configuration; a mismatch fails `resolve`.
- Every webhook call validated through the Get Operation API before acting; plan and seat changes answered within 10 seconds.
- Admin consent for SSO disclosed in the offer description; Fulfillment API v2 only.

## Co-sell solution

| Item                           | Required for                     | Note                                                                      |
| ------------------------------ | -------------------------------- | ------------------------------------------------------------------------- |
| Business profile, PartnerID    | co-sell ready                    | complete in Partner Center                                                |
| Sales contact per geography    | co-sell ready                    | one contact may cover several regions                                     |
| One-pager                      | co-sell ready                    | Microsoft template, customer-ready                                        |
| Pitch deck                     | co-sell ready                    | Microsoft template; references the architecture diagram                   |
| Reference architecture diagram | Azure IP co-sell eligible (SaaS) | shows your IP deployed on and driving consumption of named Azure services |
| Case study, channel deck       | optional                         | up to five more documents or videos                                       |

† Verify in Partner Center before quoting: Microsoft changes schema minimums and program criteria often.
