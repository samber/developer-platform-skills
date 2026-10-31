# Paused Shopify app: what to do

**Verdict:** Don't push back on item 2. Fix it. Your Paused banner decides whether you can resubmit tonight. Don't resubmit tonight with only the 500 fixed.

Legend: `†` = published by shopify.dev, which changes requirements without notice. "reported" = forum or practitioner figure.

## Assumptions

Your message leaves these open:
- **Banner:** I don't know if it shows a date or no date. Check it first, because it changes the plan (see Step 0).
- **Billing:** I assume you bill merchants on your own Stripe today. Nothing in the reviewer notes mentions billing.
- **Data:** I assume the app reads orders or customers. That means Level 1 protected customer data, plus Level 2 if you read name, email, address or phone.
- **Launch:** "Next Thursday" is 2026-11-05.
- **Distribution:** The app is public with limited visibility. Distribution can't be switched (rule 2), so this is already locked.

## Step 0: read the Paused banner

- **No date:** the reviewer was blocked on core requirements. Fix every flagged item and mark each resolved, because the dashboard blocks resubmission until you do. Then click **Submit fixes**.
- **A date:** you're in a cooldown and can only resubmit on that date. Reported cooldowns run 2 weeks to a month and lengthen on repeats.

Three actions trigger or extend a cooldown:
- Leaving issues unfixed after two exchanges.
- Sending growing issue counts.
- Disputing a refusal.

## Item 2: why pushing back fails

The rule is explicit: install only from Shopify surfaces, and never ask for a shop domain or send merchants to your site first.

- This is a core requirement, not an exemption you can negotiate. Exemptions are rare (reported). Arguing it risks a cooldown.
- The Built for Shopify exception for contract-based B2B onboarding doesn't help. It applies to Built for Shopify only, not to review.

You don't need to rebuild your whole onboarding. You need to change only the entry path for Shopify installs.

1. Use Shopify-managed installation with token exchange. The merchant installs from the App Store URL and Shopify authenticates before any UI.
2. Land the merchant in your embedded app. The shop domain comes from the install context, so never ask for it.
3. Move SaaS account creation or linking inside the embedded app, after install. Offer "connect your existing account" first. For a merchant with no account, create one in-app.
4. Keep your website onboarding for non-Shopify customers. It can stay as it is.
5. Make sure no step sends the merchant out to sign up before they reach the app UI.

Estimate: days of engineering if your SaaS already has an account-linking API, and more if it doesn't. Item 3 below is the quick one.

## Item 1: the Okta test account

- Create a dedicated reviewer account on your service that is exempt from SSO, 2FA and OTP. Static verification codes are the alternative.
- It must keep working after publish.
- Put the credentials and step-by-step testing instructions in the review notes. Include every step inside your own UI.
- Add test accounts for any third-party service the app connects to, with dummy data.
- Do this tonight. It's quick.

## Item 3: the 500 on the settings page

- Fix it, then retest the whole path, not just that page. A reviewer stops at a blocking failure, so more issues may sit behind the ones they hit.
- Check for web errors across the app: no 404, no 500, no 300 redirects.
- Test uninstall then reinstall. OAuth must run again, and the merchant must return to the workflow without duplicate-record errors.

## Why you shouldn't resubmit tonight

1. **Hidden failures:** The reviewer was blocked at login (item 1) and at install (item 2). They probably never reached billing, protected data or the embedded checks. Fixing only the 500 resubmits an app with unreviewed failures behind it.
2. **Resubmission cost:** Every resubmission slows review†. Staff say resubmitting while queued sends you to the back.
3. **Cooldown risk:** Returning with issues unfixed is a cooldown trigger.

Resubmit once, with all three items fixed and the full path retested on a fresh development store.

## Check this next: billing

This is the likeliest next rejection.

- Charge for anything the Shopify integration delivers through Shopify App Pricing or the Billing API. This covers existing customers, limited-visibility apps, and the Shopify portion of a bundled plan. A free connector into your paid SaaS is in scope (reported).
- A merchant with no SaaS account must never see your Stripe checkout. The reviewer fails apps where they can reach it (reported).
- Staff replies on existing Stripe customers conflict (reported). Ask Partner Support for the answer in writing before you rebuild or rely on either.
- Default to Shopify App Pricing for a new app. Choose manual pricing (Billing API) instead if you need local-currency prices, usage caps† or one-time charges†. Decide before opting in.
- Keep prices only in the Pricing details section. Don't write "billed separately" and don't link to your pricing page. A suspension for that wording was reported.
- Put your plan-splitting logic in the review notes. Shopify publishes no formula for splitting a bundled plan.

Also confirm the following, since a missing item blocks the next round:
- Protected customer data is requested and approved. Shopify refuses requests while the app is in review.
- Compliance webhooks are subscribed.
- Plan changes work from inside the app.
- Your embedded app uses expiring offline tokens. Non-compliant apps lose their listing and new installs after 2027-01-01†.

## Timeline

| Date | Action |
|---|---|
| Sat 10-31 (today) | Read the banner. Fix item 3. Create the SSO-exempt test account. Email Partner Support the billing question. |
| Sun 11-01 to Tue 11-03 | Build the in-app install and onboarding path. Retest the full path on a fresh development store. |
| Tue 11-03 or Wed 11-04 | Resubmit once, with review notes that answer each of the three points. If the banner shows a date, wait for that date instead. |
| Thu 11-05 | **Launch without App Store approval.** |

Expected review time:
- Shopify publishes no SLA.
- Staff quoted about 30 days per review (reported).
- Plan 2-3 rounds and 6-14 weeks to Published (reported).
- A resubmission around 11-03 would get a first answer around early December.
- Published could land anywhere from December to February.

## Launch next Thursday

You can't launch on the App Store next Thursday.

- Announce the integration as "coming to the Shopify App Store".
- Onboard pilot merchants on development stores. Don't switch to a custom app for this. Custom is locked once chosen and means a second app, a second review and reinstalls.
- Don't tell anyone a date for App Store availability.

## Review notes to write

- **Item 1:** the credentials location, and a statement that the account is exempt from SSO, 2FA and OTP and stays valid after publish.
- **Item 2:** a one-line description of the new install flow, with no mention of any dispute.
- **Item 3:** the root cause and the fix, plus the full-path retest you ran.
- **Billing:** the plan-splitting logic and Partner Support's written answer, if you have one.

Keep one owner on the submission contact inbox, with `noreply@shopify.com` allowed. Answer reviewer emails within days.

## Questions I couldn't ask

1. Does the banner show a date or not?
2. How do you charge merchants today?
3. Which customer data does the app read?

The answers can change the plan. A cooldown date overrides the "resubmit Nov 3-4" row, and Stripe billing makes the billing section above urgent.