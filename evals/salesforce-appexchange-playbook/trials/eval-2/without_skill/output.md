# Fieldmark on AppExchange: what you need to do

## Bottom line

**No, you can't skip the security review.** Salesforce requires it for every public AppExchange listing, packaged or not. A listing for an external web app that connects through a Connected App is reviewed too. The review covers your web app, its infrastructure, and how you handle OAuth tokens and customer data.

"Live next month" is unlikely. Plan on 2–4 months from kickoff to a published listing. Checkout at $40/user/month is probably not available for a package-less app (details below).

I haven't verified current fees, rates or timelines against live Salesforce docs, so treat those as things to confirm. Salesforce has changed its connected-app rules several times since 2024. Confirm the specifics with your Partner Account Manager or in the Partner Community before committing dates to marketing.

## Why "no package, no review" is wrong

- The review exists to protect customer data, wherever the code runs.
- Fieldmark pulls account and work-order data out of customer orgs and holds their OAuth refresh tokens. That is the risk the review targets.
- Expect a web application and infrastructure scan, plus a questionnaire on how you store and protect that data.

## What to do, in order

1. **Join the Partner Program (days).**
   - Create a Salesforce Partner Community account.
   - Sign the Partner Program agreement.
   - Set up the partner business org and the Partner Console.
   - Someone with legal authority at Fieldmark must sign.
2. **Confirm your listing type with Salesforce (this week).** Ask your partner contact these questions:
   - Is a listing for a package-less connected app still supported?
   - Does your 2024 Connected App need to move to an External Client App?
   - What does the review submission look like for an external app?
   - Do customers now have to install or approve the app in their own org? Salesforce tightened its rules on uninstalled connected apps in 2025. Your "nothing gets installed" premise may no longer hold, and it affects the customer-facing install steps and the review.
3. **Audit your OAuth setup before submitting (1–2 weeks).**
   - Request the narrowest scopes you need, not `full`.
   - Use PKCE and the web-server flow.
   - Encrypt refresh tokens at rest, ideally with per-tenant keys.
   - Handle revocation and disconnect cleanly.
   - Cap your API call volume per customer, because you spend their org's API limits.
   - Document how you delete a customer's data on disconnect.
4. **Prepare the security evidence (2–4 weeks).**
   - Run a clean external vulnerability scan against your web app and fix the findings.
   - Aim for a strong TLS configuration, e.g. an A grade on SSL Labs.
   - Keep a secure development lifecycle write-up, and dependency and code scan results.
   - Enforce MFA on admin and cloud consoles.
   - Write incident-response and data-handling policies.
   - Have an independent pen-test report if you can get one. It speeds up review.
5. **Prepare a test environment for the reviewers.** Give them a working tenant with sample Salesforce data and credentials, so they can run the full OAuth flow.
6. **Pay the review fee and submit.**
   - Fees have changed over time, so ask for the current figure.
   - Budget for a fix-and-resubmit cycle. First submissions often fail on something. Each cycle costs queue time and may cost another fee.
7. **Build the listing in parallel.**
   - Screenshots, a demo video, and a description that doesn't misuse Salesforce trademarks.
   - Privacy policy, terms, a support contact, and a security/trust page.
   - Pricing text.
   - Don't publish the listing until the review passes.

## The $40/user/month AppExchange checkout

- I believe AppExchange Checkout is built around managed-package licensing through the License Management App. If that's right, a package-less web app probably can't use it as-is.
- Ask your partner contact directly whether checkout supports a package-less or external-client-app listing.
- Salesforce takes a revenue share on checkout sales. I recall roughly 15%, but verify. At 15%, $40 nets about $34 per user per month before payment fees.
- Billing yourself is the common alternative. The listing sends buyers to your site, and you charge through your own billing system at $40 per user per month. This is allowed, keeps all the revenue, and works for a package-less app. You lose the "buy with Salesforce contract" convenience for customers.
- Recommendation: **launch with your own billing and treat checkout as a later phase.** Don't hold the lead-gen listing for it.

## What marketing can do next month

- Start the Partner Program signup and the review now. That is the earliest possible path to a live listing.
- Build a "Fieldmark for Salesforce" landing page and docs page on your own site. It can capture leads and rank for "Salesforce field service integration" while the review runs.
- Don't present Fieldmark as "on AppExchange" before the listing is live. Use Salesforce trademarks only as their brand guidelines allow.

## Open questions for you

1. Is your Connected App owned by a production org you control, and how many scopes does it request?
2. Do you store Salesforce data (accounts, work orders) in your own database, or only pass it through?
3. Have you had a pen test or a vulnerability scan in the last 12 months?
4. Does marketing need the listing for the brand, or only for leads? If only leads, the landing page may cover most of the value in the short term.

Answers to 1–3 would let me turn this into a dated plan with owners.