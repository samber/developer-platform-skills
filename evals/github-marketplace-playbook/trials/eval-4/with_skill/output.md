**Four problems, ranked by damage. Items 2, 3 and 4 are wrong. Item 1 is half right.** Figures marked † come from the playbook. Check them against current GitHub Marketplace docs before you plan around them.

**1. "Update the plan on every `marketplace_purchase` webhook, single source of truth": half right**

- Webhooks are the right trigger, but they cannot be the only source.
- GitHub never redelivers a failed delivery on its own. Manual redelivery reaches back only 3 days†. One missed `cancelled` or `changed` leaves a customer on the wrong plan forever.
- Add a daily sync against `GET /marketplace_listing/plans/{plan_id}/accounts`.
- Verify the webhook signature.
- Deduplicate by delivery ID.
- Provision a new purchase from `GET /user/marketplace_purchases` after the buyer's OAuth. Do not trust the webhook alone for that.
- Your setup needs a Setup URL on the app and the user OAuth flow to identify the buyer. Without them you cannot process purchases.
- Marketplace is also not your only entitlement source if you sell direct. Invoiced enterprises cannot buy paid apps on Marketplace, so you need a direct contract path. Reconcile both sources per account. Report double purchases to GitHub Support.
- Handle every event, not just changes. `pending_change`, `pending_change_cancelled`, `changed` and `cancelled` each need their own handling.

**2. "Cut Team features on the downgrade click": wrong**

- A downgrade click produces `pending_change`, not an immediate change.
- The customer already paid for the cycle. The downgrade takes effect at the next cycle, via `changed`.
- Read `effective_date`, never the delivery time.
- On `pending_change`, show the coming change and keep current access.
- Apply Free only on the `changed` event.
- On `pending_change_cancelled`, clear the notice.
- Upgrades are the opposite: they apply at once, with proration.
- Cutting features early takes away service the customer paid for.

**3. "On cancellation GitHub uninstalls the app, so we do nothing": wrong**

- GitHub does not uninstall the app.
- You have a Free plan, so a cancelled Team plan means you drop the account to Free.
- On a full cancellation (free plan or trial: at once; paid: at cycle end), you must:
  1. Deactivate the account.
  2. Revoke the token.
  3. Delete customer data within 30 days†.
- Skipping this breaks a listing requirement. The onboarding expert tests these duties.
- Cancellation also arrives on the free plan, so you must handle it on every listing.

**4. "QA buys Team on the live listing with a company card and refunds it": wrong, and the riskiest**

- Never test purchases on the live listing.
- A real purchase makes a real subscription with a real fee. GitHub refunds nothing. A refund is your own action under your own terms.
- It also pollutes your live buyer list and your reconciliation data.
- Build a test path instead:
  1. Register a second public app with production configuration. It must be installable by any account and never shared.
  2. Create a draft listing for it.
  3. Publish the plans inside the draft. Published plans in a draft listing can be bought free as simulations. Plans saved as draft cannot.
  4. Buy, upgrade, trial and cancel with your own accounts.
  5. Force pending downgrades with "Apply Pending Change" in billing settings.
- That covers items 2 and 3 above too, so test them there.

**Also check before you change the plan**

- Trials last 14 days†, one per buyer per product. Grant paid access during the trial.
- Treat the $40 Team price as permanent. You can retire a plan, but buyers keep it at its price and GitHub cannot move them. Test any price change in the draft listing first.
- Show plan, seats, trial days left and billing cycle in your app. Link upgrades through the upgrade URL.

**Next action:** open the webhook handler and write the test plan on the second app. Start with the downgrade case from item 2. It takes about half a day for someone who knows the handler. The daily sync from item 1 adds about another day.