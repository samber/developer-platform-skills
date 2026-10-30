**Next action (today):** Tell sales the bank and insurer cannot buy through Marketplace. Then file the Marketplace submission this week.

## Date mismatch, please confirm

- You say March 18 is about five weeks away. Today is 2026-10-30, which makes it about 20 weeks away (139 days).
- I plan for the five-week case because you stated it. The 20-week case is at the end of the timeline section.

## Assumptions (one per gap)

1. Tessellate is a GitHub App owned by an organization, not a personal account. If it is personal, transfer it first (app settings > Advanced).
2. You have not confirmed 100 or more installs†. That count gates paid plans.
3. The product is already sold outside Marketplace.
4. The conference is pinned to March 18.
5. No engineer has been assigned to billing events. This is the biggest schedule risk.

## Goal 1: bank and insurer buy via Marketplace

This cannot work. Both pay GitHub by invoice, and invoiced enterprises cannot buy paid apps. Even for other enterprises, only an enterprise owner who is also an org owner can buy, and only through the enterprise account.

Marketplace is not their procurement route. What to do:

1. **Direct contract path.** Sign an order form and invoice them yourselves. This is the only route that works for both.
2. **Install the public app.** The contract covers payment. The org owner installs the app (listed or unlisted) at the customer's own GitHub org, and this does not depend on Marketplace.
3. **Entitlements.** Keep two sources per account (Marketplace and direct contract) and reconcile them. Report any double purchase to GitHub Support.
4. **Customer restrictions.** Ask each bank's platform team about their app-install policies now. Their security review is likelier to slow the deal than Marketplace is.
5. **Sales message.** "Marketplace is for discovery and card-paying teams. Procurement for you stays a direct contract, and the product is the same."

## Goal 2: announce Marketplace on March 18

Approval time is not published. Vendors report 3 weeks to over 2 months. Plan on about 8 weeks for a free listing and 2 to 4 months for paid plans, because financial onboarding comes after review. Five weeks is too short for either, so do not promise "available on Marketplace" on stage.

**Pick the listing rung (best first):**

- **Unlisted public app, Install button on your site.** This is the safe path for the conference.
- **Free listing.** Choose it if the bank and insurer are your only paid buyers.
- **Paid plans.** Choose them only if you have 100 or more installs† and card-paying teams already self-serve. Adding paid plans to a live free listing triggers a second verification and review, so go straight to paid if you qualify.

Free listings carry a small risk: GitHub notes are inconsistent about a free plan for a product sold elsewhere. No enforcement is documented, but know the risk.

**Conference wording:** "Install today. Coming to GitHub Marketplace." Switch to "now on Marketplace" only if approval lands before March 18. Use `samber/developer-platform-skills@app-marketplace-launch-marketing` for the announcement itself.

## Gates and owners

Owners are roles, so name a person for each.

1. **Org owner:** Publisher verification (org-wide 2FA, verified domain, contact email), needed before paid plans. Create the listing yourself, because the GitHub App manager role cannot.
2. **Engineer:** Make the app public and installable by any account, with no preview or invite-only state. Prove integration beyond sign-in.
3. **Engineer:** Set a Setup URL and identify buyers through the user OAuth flow. Without it you cannot process purchases.
4. **Engineer:** Handle `marketplace_purchase` events on every listing, free included. Paid plans add trials and changes, plus monthly and annual prices.
5. **Product or marketing:** Listing copy to GitHub's field rules, with support and privacy URLs and named contact emails.
6. **Engineer:** A second public development app with a draft listing for tests. Never test on the live listing.
7. **Founder or finance:** Financial onboarding for paid plans. Payouts need a $500† month and can start up to 90 days† after registration.

## Billing events (engineer-weeks, see assumption 5)

| Action | Do |
|---|---|
| `purchased` | Provision from `GET /user/marketplace_purchases` after OAuth. Store the trial fields. |
| `pending_change` | Show the coming change and keep current access. |
| `pending_change_cancelled` | Clear the notice. |
| `changed` | Apply plan, seats and cycle. Compare `previous_marketplace_purchase`. |
| `cancelled` | Drop to your free plan, or deactivate, revoke the token and delete data within 30 days†. |

- Verify the webhook signature, deduplicate by delivery ID, and sync daily against `GET /marketplace_listing/plans/{plan_id}/accounts`. GitHub never resends failed deliveries.
- Read `effective_date`, never the delivery time.
- Trials last 14 days†, one per buyer per product.
- Show plan, seats, trial days left and cycle in your app.
- **Prices are permanent once published.** You can only retire a plan, and buyers stay on it. Test prices in the draft listing or in direct deals first.

## Test plan

1. Register the second app with the production config.
2. Publish plans inside its draft listing. Published plans can be bought as free simulations. Plans saved as draft cannot.
3. Buy, upgrade, trial and cancel with your own accounts.
4. Force pending downgrades with "Apply Pending Change" in billing settings.

## Timeline (five-week case, dates relative to the day you submit)

| When | Step |
|---|---|
| Week 0 | Sales message sent. Billing engineer named. Install count checked. Org verification started. Submit with "Request publish". |
| Weeks 0-3 | Build billing events and tests on the dev app. Listing assets done. |
| Week 3 | Install button and docs live on your site. Unlisted app is the fallback. |
| Week 4 | Silence after four weeks: open a GitHub Support ticket with app name, app ID, owner and submission date. File it under Billing or Account. If a bot closes it, reply to the closure email. **Never click "Withdraw request"**, which reportedly resets your place. |
| Week 5 (March 18) | Announce "coming to Marketplace". List on approval. |

**20-week case:** If March 18 is really 2027, submit now and aim for a fully listed paid plan, since two to four months fits. Keep the unlisted fallback in case review runs long, and use the week-4 support ticket if you hear nothing.

## Risks

- ⚠️ Billing capacity is unassigned.
- ⚠️ The 100-install† gate may block paid plans.
- ⚠️ Two entitlement sources can double-bill an account.
- ℹ️ Every figure marked † needs checking against current GitHub Marketplace docs. GitHub has changed its fee (currently 5%†) and categories before.

## Questions

- Is March 18 five weeks away or about twenty?
- How many installs do you have today?
- Who owns billing events, and how many engineer-weeks can they spend?

**Next:** Answer those three, then send the sales message.