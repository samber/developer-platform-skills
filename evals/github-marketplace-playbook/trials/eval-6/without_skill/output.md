# Shutting down Pebble Insights: what to watch for

⚠️ The plan is out of order. Delete the GitHub App and the action repo last, not Friday. Also, today (2026-10-30) is a Friday and the last day of your shutdown month, so please confirm which Friday you mean.

I did not read anything in `skill-wip/`. This comes from general knowledge of GitHub Marketplace. Check the billing and delisting specifics against the current Marketplace docs or GitHub Support before acting.

## 1. Billing (biggest risk)

- **Delisting only stops new purchases.** About 60 orgs stay subscribed and keep getting billed until their plans end or are cancelled.
- **GitHub bills these customers, not you.** Deleting the app does not reliably cancel their subscriptions. You risk orgs paying for a dead product, plus chargebacks and support tickets.
- **Annual plans are prepaid.** Shutting down mid-term means you owe prorated refunds or a service-continuity commitment. Check your Marketplace developer agreement and customer terms.
- **Ask GitHub Support how to retire the plans.** Open a ticket now and confirm the exact sequence. Ask how they cancel or refund the remaining subscriptions and whether the listing can be removed while paid plans are active.
- **Watch your own plan state.** Marketplace sends `marketplace_purchase` webhooks (cancelled, changed). Keep a receiver alive until every subscription is closed.

## 2. Deleting the app registration

- **It kills the product at once for everyone.** It removes every installation, revokes tokens, and stops webhooks.
- **You can't undo it.** The app slug, App ID and private key are gone. Customers who want to come back would have to reinstall a new app.
- **Do it last.** Wait until billing is fully closed, the notice period has ended, and you've done the data steps below.

## 3. Deleting `pebblecart/insights-action`

- **Deleting breaks every customer workflow.** Any workflow with `uses: pebblecart/insights-action@...` fails with "repository not found" and turns CI red.
- **Customers may not read your notices.** The failure shows up in builds, not in your email.
- **Better path:**
  1. Ship a final release (a tag and a major-version tag) that prints a deprecation warning, with the sunset date and a link to the notice. Let it exit 0 or soft-fail so builds don't break.
  2. Update the README, then archive the repo. Archived repos still resolve in `uses:`.
  3. Delete only after a grace period (for example 60 to 90 days).
- **Check the Actions Marketplace listing.** If the action is listed there, delist it as well.
- **Check forks and pinned SHAs.** Forks and SHA-pinned references keep working. Deleting the repo won't stop their use, and it will break anyone depending on your tags.
- **Check whether the action calls the app's backend.** If it does, it will fail after the app is gone, so the final release should say so.

## 4. Customer communication

- **Give notice before anything irreversible.** Email all 60 org owners and billing contacts. Use your app's support contact, plus notices in the README, the docs and any in-app message.
- **State the facts:** the shutdown date, the last billing date, refund or proration terms, how to export data, and what to remove from their workflows.
- **Check your terms.** Contracts or ToS may require a minimum notice period (often 30 days or more). Giving less than that could breach them.
- **Name a support contact** that stays open through the wind-down.

## 5. Data and security

- **Delete or return customer data** collected by the app, per your privacy policy and GDPR where it applies. Offer an export first.
- **Keep what you must keep,** such as billing and tax records and audit logs, for the legal retention period.
- **Revoke and rotate** the app's private key and webhook secret, and any OAuth client secret. Remove them from your infrastructure.
- **Shut down the backend after the app is deleted,** not before. Shutting it down first causes silent failures for customers.
- **Decommission cleanly:** DNS, webhook endpoints, analytics, status page. Leave a static "sunset" page on the app's homepage and setup URLs.

## 6. Suggested order

1. **Now:** open a GitHub Support ticket about retiring the paid plans. Confirm the shutdown date, refund policy and notice period.
2. **Now:** delist the app (this stops new purchases).
3. **Same day:** send the customer notice.
4. **Next:** ship the final deprecation release of the action and archive the repo.
5. **Through the shutdown date:** keep the backend and webhook receiver running, and answer support.
6. **After the last subscription is closed and notice has run:** delete customer data and rotate secrets.
7. **Last:** delete the GitHub App registration, then (after the grace period) the action repo.

## Questions for you

1. Which Friday do you mean, and is "end of this month" a hard date? Today is Oct 30, so is a one-day notice what you intend?
2. How many of the ~60 orgs are on annual plans, and how much prepaid time is left?
3. Does the action call your backend or the app's credentials?
4. What notice and refund terms do your ToS or contracts promise?