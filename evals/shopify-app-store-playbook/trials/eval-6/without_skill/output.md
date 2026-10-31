**Short answer:** yes. Handle the unanswered email first, because it can block the sprint.

## 1. Answer the "app quality check" email today ⚠️

1. **Check it's real.** Don't click its links yet. Open the Partner Dashboard, find your app, and look in its notifications and distribution/review sections. Shopify posts real review issues there. Phishing aimed at app developers is common, so if nothing shows up, treat the email as suspect.
2. **Read the deadline.** Shopify requests like this usually come with a date. After it, the app can be hidden from search or delisted, and ten days of silence may already have used up much of the window.
3. **Reply or fix in the channel the email names.** If you can't tell the channel, answer the email thread and the Partner Dashboard item.
4. **Check the usual causes before replying:**
   - The three mandatory privacy webhooks are handled: `customers/data_request`, `customers/redact`, `shop/redact`.
   - Webhook HMAC verification works.
   - The app uses current API versions and no deprecated APIs.
   - The privacy policy URL is live.
   - The support contact and emergency developer email are current and monitored. Ten days of silence suggests the contact address may be unmonitored.
5. **Fix the inbox.** Make sure someone owns that mailbox so the next notice doesn't sit unread.

## 2. Customer names and emails need approval first 🔐

Shopify treats customer name, email, phone, and address as protected customer data. A code push alone won't get you access.

- **Request access in the Partner Dashboard** (app > API access requests > Protected customer data).
  - Name and email are in the higher tier, usually called Level 2.
  - You must justify each field, and you must be able to explain why you can't work without it.
- **Until approved**, those fields come back empty or the API returns an access error. Your sprint feature would pass tests in a dev store and fail for real merchants.
- **Expect to show data-protection practices** such as:
  - Encryption in transit and at rest.
  - Limited staff access.
  - A retention and deletion policy.
  - Separation of test and production data.
  - Breach response.
  - Honoring the redact webhooks, which now matters much more because you'd be storing PII.
- **Don't expect "push for review right away" to work.** The data-access request has its own review, with a wait you don't control. Submit it at the start of the sprint, not at the end. Plan for the feature to ship behind a flag after approval.

## 3. Other things the feature changes

- **Scopes:** adding `read_customers` (or similar) makes existing merchants re-approve the app. Expect some drop-off and support questions.
- **Privacy policy and listing:** update both to describe the new data you store, how long you keep it, and who can see it.
- **Redaction:** names and emails copied into tickets must be deleted or anonymized when `customers/redact` or `shop/redact` arrives. Copies in backups, search indexes, logs, and exports are easy to miss. Build this before launch, not after.
- **Minimize:** store only what the ticket needs. Consider fetching on demand instead of copying.
- **Logs and error tracking:** make sure names and emails don't leak into logs, Sentry, or analytics.

## Suggested order

1. Today: verify the email, find the deadline, and reply or fix.
2. Day 1 of the sprint: submit the protected-data request.
3. Sprint: build the sync behind a flag, with redaction handling and the policy updates.
4. After approval: enable the flag and submit the app update.

## Questions that would sharpen this

- What does the quality-check email actually ask for, and by when?
- Do you already store any customer PII, for example from ticket emails?
- Do you already handle the three privacy webhooks?