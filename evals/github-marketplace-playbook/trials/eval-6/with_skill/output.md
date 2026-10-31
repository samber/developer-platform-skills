# Pebble Insights shutdown: what to watch out for

**Short answer:** don't run the plan as written. All three steps are out of order or irreversible, and they break obligations to about 60 paying orgs. Use the sequence below.

I read the `github-marketplace-playbook` skill and its reference file. Figures marked † come from the skill's notes on GitHub's rules. Check them against current GitHub Marketplace docs before you commit to dates.

## Assumptions

- Today is Friday 2026-10-30, so "end of this month" is tomorrow. If "Friday" means next Friday (2026-11-06), the deletion order problems below still apply.
- Pebble Insights is a paid listing, and the action in `pebblecart/insights-action` calls the app or its backend.
- Some orgs are on annual plans. The count of annual vs monthly buyers sets how long you stay on the hook.
- No enterprise or invoiced buyers are involved. If there are any, they sit on direct contracts, and those need their own notice.

## Problems with each step

### 1. "Click delist today"

- **Notice comes first.** The Developer Agreement requires 30 days'† written notice before removal. Send it to legal-support@github.com, then use "Delist this Listing".
- **Earliest compliant delist is about 2026-11-29**, not today. A shutdown "at the end of this month" can't be fully clean on the Marketplace side.
- **Delisting doesn't end subscriptions.** Existing subscriptions run to their cycle end. Monthly plans run about 30 days. Annual plans can run up to a year, and the app can't be deleted before then.
- **GitHub refunds nothing.** You must choose one of two options:
  - serve every buyer to cycle end, or
  - refund pro rata under your own terms.
- **Annual buyers are the real cost.** Someone who paid 12 months in September is owed about 10 more months of service, or a refund. Pull the list of annual buyers and their renewal dates today.
- **Stop new sales during the notice period.** Retire the paid plans so nobody new buys. Retiring is the only plan change GitHub allows, and existing buyers keep their plan. Confirm in current docs that retiring all plans is allowed before you rely on it.

### 2. "Delete the GitHub App registration on Friday"

Deleting the app is blocked while subscriptions run. Even if it weren't, it would hurt in these ways:

- **Cancellations and plan changes would go unprocessed.** `marketplace_purchase` webhooks (`cancelled`, `changed`, `pending_change`) stop arriving. On full cancellation you owe four things:
  - deactivate the account,
  - revoke the token,
  - delete customer data within 30 days†, and
  - drop paid-cancelled accounts to a free plan if you have one.
- **You lose the trigger for those duties.** Without the app, nothing tells you which buyers cancelled, so the data-deletion clock runs unseen. Keep the webhook endpoint alive and reconcile daily against `GET /marketplace_listing/plans/{plan_id}/accounts`.
- **Installation tokens die immediately for all 60 orgs.** Buyers who paid through their cycle would lose service mid-term. That's likely a breach of your terms and invites chargebacks.
- **Direct contracts need their own handling.** The skill says to reconcile Marketplace and direct-contract entitlements. Don't assume every paying org came through GitHub billing.
- **Support and security duties continue.** GitHub can cut exposure or delist for poor support. You must also be able to report a confirmed security incident within 24 hours†. Keep a monitored support address and the security contact until the last subscription ends.
- **Delete only once all three are true:**
  1. the listing is delisted,
  2. the last paid cycle has ended, and
  3. customer data is deleted and logged.

### 3. "Delete the pebblecart/insights-action repo"

- **Archive it, don't delete it.** Deleting frees the Marketplace name for anyone. A third party could take it and publish something under a name your customers already trust. That's a supply-chain risk for your own users.
- **Deleting breaks customer CI with no warning.** Every workflow that references `pebblecart/insights-action` fails at once, whether pinned to a tag or a SHA. Customers who bought on a monthly or annual plan are paying for a product that stops running.
- **Deleting won't make "nobody use it" true.** Forks and cached copies survive. Archiving keeps history and redirects, and the repo becomes read-only.
- **Delist the action properly.** Uncheck "Publish this Action to the GitHub Marketplace" on every published release, not just the latest. Then archive the repo.
- **Archive timing:** archive after you've shipped a final release with a deprecation notice in the README, the action's runtime log output, and the release notes.
- **Keep the action working through the service period.** It probably depends on the app or your backend, so don't switch either off while paid buyers remain.
- **Transfers drop the verified-creator badge**, so don't "hand it off" to another owner as a shortcut.

## Recommended sequence

| When | Action | Owner |
|---|---|---|
| Today (Fri 10-30) | Export all 60 orgs with plan, billing cycle, renewal date, and Marketplace vs direct contract. | Billing / eng |
| Today | Send written delist notice to legal-support@github.com. Starts the 30-day† clock. | Legal |
| Today | Retire paid plans in the listing so no new purchases land. Verify in docs first. | Product |
| Within 1-2 days | Email all buyers: shutdown date, service-through date, refund or serve-to-term choice, data deletion date, and migration path. Include a direct-contract notice for any off-Marketplace buyers. | Product / support |
| Before 10-31 | Decide per buyer: serve to cycle end, or refund pro rata under your own terms. GitHub won't refund. | Finance |
| Through service period | Keep the app, webhook endpoint, Setup URL flow, and action running. Daily account sync. Monitor support and security mailboxes. | Eng |
| ~2026-11-29 | Click "Delist this Listing". | Product |
| After last cycle ends (monthly ~Nov/Dec, annual up to ~Oct 2027†) | Final release of the action with deprecation notice, then unpublish the Marketplace flag on every release and **archive** the repo. | Eng |
| After last cycle ends | Revoke tokens, deactivate accounts, delete customer data within 30 days† of each cancellation, and log it. | Eng / security |
| Last | Delete the GitHub App registration. | Eng |

If annual buyers make the long tail unacceptable, the only way to end sooner is to refund them pro rata and send a buyer message. Then you can delete once their subscriptions are cancelled and data is deleted.

## Obligations at risk if you follow the original plan

| Original step | What breaks | Consequence |
|---|---|---|
| Delist today | Skips the 30-day† notice | Developer Agreement breach |
| Delete app Friday | Active subscriptions orphaned, webhooks lost | No deactivation, no data deletion trigger, paying buyers cut off |
| Delete action repo | Name freed, workflows fail instantly | Squatting risk, customer CI outage |
| All three together | No buyer message, no refund decision | Chargebacks, support load, reputational damage |

## Questions to answer before you send anything

1. How many of the 60 are annual, and when do they renew?
2. Will you serve to term or refund pro rata?
3. Is the end-of-month shutdown date already public? If so, you may need to amend it to match the notice period.
4. Does the action need the app or your backend to function?
5. Who owns the data-deletion log for the 30-day† duty?

I haven't verified any † figure against live GitHub docs, and I haven't confirmed that retiring every plan is permitted. Treat both as open items for whoever sends the notice.