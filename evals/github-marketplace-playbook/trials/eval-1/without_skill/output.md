# GitHub Marketplace setup for Quaystone ($12 per repository per month, per-unit, monthly only)

I wrote this from memory of GitHub's Marketplace docs and did not check them live. Items marked ⚠️ are ones I'm unsure of, or ones that change often. Check them against the current docs before you rely on them.

## Blockers to fix first

1. 🔴 **The app is on a personal account.** You can't publish paid plans from a personal account. A verified organization has to own the app. The cofounder transfers it to the Quaystone org. Installs, app ID and keys should carry over, but test this on a staging app first.
2. 🔴 **Price changes are sticky.** ⚠️ As I remember it, you can't edit the price of a published plan. You retire it and create a new one, and existing subscribers stay on the old price. "Adjust after a month" therefore means a second plan and a grandfathered cohort. Pick $12 knowing that.
3. 🟠 **Your 340 installs don't become paying customers.** They stay on whatever you do today. Decide now whether to add a free plan, grandfather them, or cut them off. I recommend a free plan or a dated grace window. Otherwise your own entitlement code is what turns them off.

## Steps

### Phase 1: Ownership and verification (start now, it has the longest lead time)

1. Create or confirm the Quaystone GitHub organization.
   - Enforce 2FA for all members.
   - Make sure you and the cofounder are both owners.
2. Apply for verified publisher status on the org.
   - This involves domain verification and an identity check.
   - ⚠️ Review time varies from days to weeks, so start immediately.
3. The cofounder transfers the app: App settings → Advanced → Transfer ownership → the Quaystone org.
   - Do this on a throwaway app first.
   - Afterwards, confirm the installs still show, the webhook still fires, and the private key and client secret still work.
4. Complete financial onboarding in the org.
   - Provide a bank account, tax forms (W-9 or W-8) and a legal entity.
   - Without this you can't be paid.
5. Confirm the app is public and meets the install threshold for paid listings.
   - ⚠️ I recall 100 installs for GitHub Apps. You have 340, so you clear it.

### Phase 2: Code changes (can run in parallel with Phase 1)

6. Add a `marketplace_purchase` webhook handler.
   - Handle the actions `purchased`, `changed`, `cancelled`, `pending_change` and `pending_change_cancelled`.
   - Verify the webhook signature.
   - Make the handler idempotent.
7. Enforce entitlement from `unit_count`. **This is the main engineering work.**
   - Per-unit billing means the customer types a quantity at checkout. GitHub doesn't count the repositories they actually installed.
   - Decide what the bot does when a customer has 30 repos installed but bought 10 units.
   - Options: block the extras, cap review at the purchased count, or warn and allow a grace period.
8. Handle the post-purchase flow.
   - Set a setup or redirect URL so a new buyer lands on your onboarding page.
   - Map the GitHub account to your own account record.
9. Test with the Marketplace stubbed endpoints and the purchase webhooks before you submit.
   - Cover upgrade, downgrade, cancel and quantity change.
   - ⚠️ From memory, upgrades apply immediately and downgrades or cancellations apply at the end of the billing cycle.

### Phase 3: The listing

10. Prepare the listing assets.
    - Logo and a short description.
    - Up to five screenshots (⚠️ verify the limit).
    - Primary category.
    - Support contact.
    - Privacy policy URL and terms URL.
    - Status page, if you have one.
11. Create the plan.
    - Plan type: per-unit.
    - Unit name: `repository`.
    - Price: $12 per unit per month.
    - ⚠️ The form may also ask for a yearly price. If it's required, enter 12× monthly with no discount and don't promote it. If you can leave it blank, do.
    - Decide on the free plan from blocker 3 (it's a separate plan).
    - Decide whether to enable a free trial on the paid plan. ⚠️ I recall 14 days.
12. Accept the Marketplace product agreement as an org owner.
13. Submit for review.
    - GitHub's onboarding team reviews the listing.
    - ⚠️ Expect back-and-forth. I'm not confident about the timeline, so don't promise a launch date.
14. After approval, publish.
    - Run a real $12 purchase from a test account on a throwaway repo.
    - Confirm the webhook arrives, the entitlement works, and the cancel flow works.

### Phase 4: After launch

15. Review conversion and quantity data after a month.
    - Look at units per customer, trial-to-paid, and cancellations.
16. If you change price, create a new plan and retire the old one.
    - Existing subscribers stay on the retired plan until you migrate them.

## Questions that change the plan

- Do you bill any customers outside GitHub today (Stripe or invoices)? If so, I need to check how that interacts with Marketplace billing terms. ⚠️
- How many of the 340 installs are active, and how many repos does a typical install cover? That tells you whether $12 per repo hits a few large accounts or many small ones.
- Is a free plan acceptable, or must every user pay?
- What's the fee and payout schedule? ⚠️ I don't remember GitHub's current revenue share or minimum payout, so check the Marketplace terms before you model revenue.

## Suggested order for this week

1. Today: start org verification and financial onboarding. They are the slowest steps and need no code.
2. This week: do the staging transfer test, then the real transfer.
3. In parallel: build the webhook handler and the entitlement logic.
4. Then: build the listing, submit it, and wait for review.