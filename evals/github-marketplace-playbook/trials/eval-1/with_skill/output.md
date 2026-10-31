# Quaystone on GitHub Marketplace: setup steps for a $12 per-repository plan

**Next action (today, about 20 min):** ask your cofounder to open the app's settings under Advanced and start the transfer to a Quaystone GitHub organization. Everything else waits on this.

Figures marked `†` come from the playbook. Check them against current GitHub Marketplace docs before anyone plans around them.

## Three problems with the plan as stated

1. **Price changes after a month.** A published price is permanent. You can only retire a plan, and buyers stay on it at its old price until they move. GitHub cannot move them. Launching at $12 and "adjusting after a month" means the first buyers keep $12 for good.
   - Test the price first with direct deals or a draft-listing plan. A draft plan can be bought as a free simulation, and no real buyer sees it.
   - If you launch anyway, treat $12 as the grandfathered price.
2. **Monthly only.** Paid plans carry a monthly price plus an annual price. I can't confirm from the playbook that the annual price can be left empty. Ask the onboarding expert before you build around it. Annual plans only matter if GitHub requires them.
3. **Per-unit "per repository".** The docs describe per-unit as per user. The unit label is free text, though, and live listings sell units like "x10 repositories" with a quantity selector. Confirm with the onboarding expert that "repository" is accepted as the unit. The fallback is flat tiers, such as 10, 25 or 50 repos.

## Assumptions

I didn't get to ask the interview questions, so these fill the gaps. Correct any that are wrong.

- It is a GitHub App only, with no Action or OAuth app.
- The app is public. 340 installs exceeds the 100† threshold for requesting paid plans.
- Buyers are mostly teams paying by card. Some may be invoiced enterprises.
- No billing code exists yet, and a billing owner and engineer-weeks still need to be assigned.
- No launch event is pinned to a date.
- Quaystone isn't sold elsewhere today, so the free-plan-versus-direct-sales conflict doesn't apply.

## Rung: go straight to paid plans

Your 340 installs and the self-serve card volume make paid the right rung. Listing as free first and adding a paid plan later forces a second verification and financial onboarding. Go paid in one pass.

Your existing installs can stay as they are. An unlisted public app keeps working while the listing is in review. Decide whether existing free users get a free plan or are grandfathered, and tell them before launch.

## Setup steps

### 1. Move ownership to an organization (week 1)

Only an organization that passed publisher verification can sell. A personal-account app can't.

1. Create or use a Quaystone GitHub organization.
2. Transfer the app to it (app settings, Advanced).
3. Confirm after the transfer that the 340 installs, webhook URL, secrets and keys still work. I can't confirm from the playbook that installs carry over, so test on a throwaway install first.
4. Make a Quaystone organization owner, not just a GitHub App manager, the person who will create the listing. The App manager role can't create it.

### 2. Publisher verification (weeks 1–2)

1. Turn on org-wide 2FA.
2. Verify the company domain.
3. Add a contact email.
4. Request publisher verification before submitting. An approved unverified app shows "App meets the requirements for listing" and can't change pricing.

### 3. App configuration

- Set a **Setup URL** on the app. GitHub calls it optional, but without it you can't process purchases.
- Identify each buyer through the user OAuth flow.
- Keep the app public and generally available, with no preview or invite-only mode.
- Fill in the support URL, the privacy URL, and named contact emails. GitHub uses those emails for payouts.
- Show integration beyond sign-in. GitHub rejects apps that only authenticate.

### 4. Billing handling (weeks 2–5)

The onboarding expert tests this before approval, so build it first.

- **Webhook:** handle `marketplace_purchase` for these actions. Verify the signature and deduplicate by delivery ID.

  | Action | Handling |
  | --- | --- |
  | `purchased` | Provision from `GET /user/marketplace_purchases` after the buyer's OAuth. Store trial fields. |
  | `changed` | Apply the new plan and `seat_count`. |
  | `pending_change` / `pending_change_cancelled` | Show or clear the coming change. |
  | `cancelled` | Deactivate, revoke the token, and delete customer data within 30 days†. |

- **Timing:** upgrades apply at once with proration. Downgrades and paid cancellations arrive at the next cycle. Read `effective_date`, not the delivery time.
- **Unit enforcement:** map the purchased quantity to the number of repositories your bot is enabled on. Decide what happens when a team adds repo 11 on a 10-unit plan. A suggested default is a prompt linking to the upgrade URL.
- **Trials:** 14 days†, one per buyer per product. Grant paid access during the trial.
- **In-app display:** show plan, units, trial days left and billing cycle.
- **Sync:** run a daily job against `GET /marketplace_listing/plans/{plan_id}/accounts`. GitHub never redelivers a failed webhook on its own, and manual redelivery reaches back only 3 days†.
- **Entitlements:** track Marketplace and direct-contract entitlements per account, and flag double purchases to GitHub Support.

### 5. Test on a second app (week 5)

Never test on the live listing.

1. Register a second app with the production configuration. It must be public and never shared.
2. Create its draft listing and publish the plans inside it. Published plans can be bought as free simulations. Plans saved as draft can't.
3. Buy, upgrade, add units, trial and cancel with your own accounts.
4. Force pending downgrades with "Apply Pending Change" in billing settings.

### 6. Listing assets and pricing plan

- **Short description:** 40–80 characters, sentence case, no final period, describes the function. For example: "Automated pull request reviews for GitHub teams".
- **Introductory description:** 150–250 characters, starting with "Quaystone".
- **Detailed description:** up to 1,000 characters, with 3–5 value propositions. Each gets a level-three heading and one or two sentences.
- **Style:** say "teams", not "users". Use the serial comma and no exclamation marks.
- **Logo:** square, at least 200x200 px, transparent, no text.
- **Screenshots:** up to five, at least 1,200 px wide, one aspect ratio, no browser chrome.
- **Categories:** one primary and one optional secondary.
- **Plan:** name, short description, up to four bullets. Set "Available for" to organizations only if per-unit pricing requires it (per-seat plans are organizations only).
- **Pricing:** $12 per repository per month, subject to the three points above.

### 7. Submit and wait (week 6 onward)

- Click "Request publish". An onboarding expert replies by email.
- Financial onboarding comes after review.
- If you hear nothing after four weeks, open a GitHub Support ticket under Billing or Account. Include the app name, app ID, owner and submission date. Never click "Withdraw request".

## Timeline

GitHub publishes no review time. Vendors report 3 weeks to over 2 months for review, and paid financial onboarding has stalled 10 more weeks. Plan for two to four months for paid plans.

| When | Milestone |
| --- | --- |
| Nov 2–6, 2026 | Org transfer, verification request, and confirmation of the unit label and annual-price questions |
| Nov 9–Dec 4 | Billing handling built and tested on the second app |
| Around Dec 7 | Submit |
| Late Jan to early Apr 2027 | Approval and financial onboarding, likely range |

Holidays will slow the review. If you need to be live sooner, keep the unlisted app and add your own Install button. Announce it as "coming to GitHub Marketplace", and list it on approval.

## Money and limits

- GitHub takes a 5%† fee.
- Payout comes at the end of the following month, once a month reaches $500†.
- The first payout can take up to 90 days† after registration. At $12 per repository, $500 is about 42 paid repositories. Budget for cash arriving well after launch.
- Invoiced enterprises can't buy paid apps. In an enterprise, only an enterprise owner who is also an org owner can buy, through the enterprise account. Keep a direct contract path for them.

## Open questions for you

1. Will the onboarding expert accept "repository" as a per-unit label, and is an empty annual price allowed? Ask in the first email.
2. Do you want to settle the price before submitting? I recommend testing it in direct deals first, because of the permanence.
3. Do existing installs get a free plan, a grandfathered path, or a migration offer?
4. Who owns billing code, and how many engineer-weeks do they have? Four weeks of build is my estimate, not a measured figure.