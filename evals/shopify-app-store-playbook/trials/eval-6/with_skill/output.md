**Short answer:** yes, two things. The unanswered quality-check email is urgent. The customer name and email sync will fail review if you push it right away.

Legend: `†` means Shopify-published, and Shopify changes these without notice. "Reported" means forum or practitioner figures.

## Assumptions

You didn't say these, so I assumed them. Tell me if any is wrong.

- Your app is public, and "listed for a year" means it is on the App Store.
- It already reads orders or tickets data from Shopify.
- You haven't yet requested protected customer data access for names and emails.

## 1. Reply to the quality-check email today

You are at day 10. The rules are:

- Answer within **7 days†**. Silence demotes the app in the store.
- Ship the required changes within **30 days†**, or the app can be unpublished.

So you are already past the reply window. About 20 days are left on the fix clock, assuming the 30 days started when the email arrived.

Do this now:

1. Reply to the email today. Name an owner and give a date for each required change.
2. Read the list of required changes. Check whether one of them touches customer data, billing, or tokens.
3. Check that a support email is on file. Shopify doesn't support third-party apps, so you answer merchants yourself.
4. Keep the review contact inbox free to receive `noreply@shopify.com`. A missed mail is how this one went unanswered.

## 2. Don't ship the name and email sync straight to review

This is the main risk. Reading customer name and email is Level 2 protected customer data. The rules are:

- Reading orders or customers is Level 1 and needs approval.
- Name, email, address, and phone are Level 2. Each field needs its own one-line reason and a completed data-protection form.
- **Request this before you submit.** Shopify refuses protected-data requests while the app is in review.
- Unapproved fields come back **redacted**. The sync could pass your tests and then write blank names and emails into live tickets.

Plan it this way:

1. Submit the protected-data request first, with a reason for each field. For example: "customer name and email shown on the support ticket so agents know who they are replying to."
2. Complete the data-protection details.
3. Wait for approval, then push the app update.
4. While you wait, build the sync against a development store. Test the redacted case so it fails clearly instead of writing empty values.

Timing is the second risk:

- Reviews run **2-3 rounds and 6-14 weeks to Published** (reported). Staff have quoted about 30 days per review.
- Every resubmission slows review†. Resubmitting while queued sends you to the back.
- So "next sprint, then review right away" is realistic for the code. It is not realistic for the release date. Plan for the feature to go live weeks later.

Also, since you are now handling more personal data:

- Check that the three compliance webhooks are live: customer data request, customer redact, and shop redact. Ticket records that hold names and emails must be erasable through them.
- Ask what customer data you will store in your own system, and for how long. The data-protection form will ask this.
- Mention the new fields in the review notes so a reviewer doesn't misread them.

## 3. Check two deadlines that may already apply to you

- **Expiring offline access tokens by 2027-01-01†.** Non-compliant apps lose their listing and new installs. Their old tokens get 403 errors from 2027-04-01†. Because the app is a year old, check whether you already request them (`expiring=1`).
- **Latest App Bridge with session tokens, and GraphQL Admin API only†.** The quality check may be about this, so look for it in the email.

Fold the token migration into the same update as the sync if it is not done. It saves a review round.

## 4. Billing check

A support desk is usually a paid SaaS. If merchants pay you through your own Stripe for what the Shopify integration delivers, that conflicts with the review rules. The rules say charges for the Shopify integration go through Shopify App Pricing or the Billing API. Staff have applied this to existing customers too (reported), though earlier replies said otherwise. If this applies to you, get Partner Support's answer in writing before the next submission, and say so in the review notes.

## Sequence

| Step | When | Owner |
| --- | --- | --- |
| Reply to the quality-check email | Today | Whoever owns the inbox |
| Read the required-changes list, assign owners | This week | Engineering lead |
| Ship quality-check fixes | Before day 30 | Engineering |
| Submit protected-data request (Level 1, plus name and email) | Next sprint, start of sprint | Engineering plus whoever fills in the data-protection form |
| Build sync on a development store, test the redacted case | Next sprint | Engineering |
| Submit the app update | After the protected-data approval | Engineering |
| Plan for 2-3 review rounds | The following weeks | Review contact |

## Questions that would change this advice

1. What exactly does the quality-check email ask you to fix? That sets the real deadline and may reorder everything.
2. Do you already hold Level 1 access for orders or customers? If not, that request comes first.
3. Does the new update also include the token migration? It should.