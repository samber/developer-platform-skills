Three of the four have a real problem. Only the "single source of truth" idea is partly right. One caveat: I'm answering from memory of GitHub's Marketplace docs, so check the event semantics against the current docs before you act.

**Verdict: items 1 and 4 need fixes, item 2 is wrong, item 3 is wrong and risky.**

1. **Webhook as the only source of truth: not safe.**
   - Webhooks can be dropped, duplicated, or arrive out of order. A missed `purchased` or `cancelled` means a wrong plan forever.
   - Store the plan ID, account ID, and `effective_date`.
   - Key idempotency on the delivery GUID (`X-GitHub-Delivery`).
   - Reconcile on a schedule, and on app load, with the Marketplace REST API (`GET /marketplace_listing/accounts/{account_id}`, authenticated as the app). Treat the API as the tie-breaker.
   - Key entitlements on plan ID, not plan name.
   - Handle all five actions: `purchased`, `changed`, `pending_change`, `pending_change_cancelled`, `cancelled`.

2. **Cutting Team features on the downgrade click: wrong.**
   - GitHub applies downgrades at the end of the billing cycle. The click only produces `pending_change` with a future effective date.
   - If you cut features at that point, you take away time the customer already paid for. That means support tickets and refund requests.
   - Keep Team until the `changed` event (or the effective date).
   - On `pending_change`, record the scheduled change and optionally show "Team ends on <date>".
   - On `pending_change_cancelled`, clear that record.
   - Upgrades are different: they take effect immediately, so grant Team on `changed`/`purchased`.

3. **"GitHub uninstalls the app on cancellation": don't assume it.**
   - As I understand it, cancelling a plan does not uninstall the app. The installation can stay active, and `installation` deleted is a separate event.
   - If you do nothing on `cancelled`, a cancelled customer keeps Team features and keeps consuming your compute.
   - On `cancelled`, revoke paid entitlements and decide the end state. Either move the account to Free (it has a Free plan, so this is probably right) or stop processing.
   - Handle `installation` deleted separately, with a data-retention policy.
   - Verify this on a test listing (see item 4) before you rely on it either way.

4. **QA buying Team on the live listing with a company card and refunding: avoid.**
   - GitHub documents draft listings as the way to test billing flows. Purchases on a draft listing don't create real transactions or card charges.
   - A listing is tied to one app, so create a separate test app with a draft listing. Add Free and Team plans that mirror production. Point its webhook at staging.
   - Buying on the live listing creates real transactions. You can't instantly reverse them yourself, and they may appear in payouts and tax records. It also sends real `purchased` events to production.
   - It also uses a company card for test purchases, which is a finance and compliance issue.
   - The draft listing also lets QA test downgrade, cancel, and pending-change flows, which a buy-and-refund can't do cleanly.

**Also add:**
- A test for out-of-order and duplicate delivery. Redeliver a webhook from the App settings, "Advanced" tab.
- A test that `pending_change` leaves Team features on until the effective date.
- A test that `cancelled` revokes Team features while the app stays installed.

**Next (about 20 minutes):** create the test app with a draft listing, and make QA run the downgrade-then-wait path against it first.