# Is the key swap enough before Friday?

**No.** The swap changes the credential. It does not change the webhook secrets, the real-world payment behavior, or the account state. Because this is your first integrator, whatever happens on Friday becomes your template for every later one.

I assume Meshpay has a Stripe-style design: separate test and live keys, signed webhooks, and an account review gate. Adjust any step that doesn't match.

## Do first (today): confirm the review will finish

The whole launch depends on one fact: **will this account's review be complete before Friday?**

- Check the account's review state now and get a committed completion date from whoever owns reviews.
- If anything is outstanding (documents, bank verification, business details), tell the integrator today.
- Don't promise Friday until the review is done. Test the live path before then.

## Fix on our side

### 1. Replace the plain 401 for unreviewed accounts

401 means "your credentials are bad." Here the credentials are fine and the account isn't activated. That mismatch causes real damage:

- The integrator's engineers will think the key is wrong and rotate or re-paste it.
- Their client may treat 401 as non-retryable, or trip an auth-failure alarm.
- Their on-call gets paged for the wrong problem on launch day.
- Your support team can't tell "bad key" from "not activated" in logs.

Return **403 Forbidden** with a machine-readable body:

```json
{
  "error": {
    "type": "account_not_activated",
    "code": "live_mode_pending_review",
    "message": "Your account is still under review. Live payments are disabled until review completes.",
    "doc_url": "https://…/go-live",
    "request_id": "req_…"
  }
}
```

- Keep 401 strictly for missing, malformed, revoked, or wrong-mode keys.
- Show the review status in the dashboard.
- Emit an `account.activated` webhook, or expose a status endpoint, so the integrator can gate their go-live on it.
- Add a test for this exact error shape.
- Add an alert on spikes of this error code. It tells you who is trying to go live early.

### 2. Rewrite the activation doc

Delete "Replace sk_test with sk_live and you're live." Replace it with a go-live checklist, such as the one below. Suggested opening text:

> Live mode requires: (1) completed account review, (2) a live webhook endpoint with its own signing secret, (3) the live API key, (4) a production smoke test. Swapping the key alone is not enough.

### 3. Reduce blast radius for a new live account

- Apply conservative default limits (per-transaction, daily volume, velocity) and raise them after a clean first week.
- Make sure your own fraud and risk monitoring is watching this account from the first live payment.
- Set the first-payout timing and any reserve expectations in writing. Booking platforms are often surprised by payout delays.

## Integrator checklist before Friday

### Configuration (the key swap is only the first line)

1. **Live webhook endpoint.** Register a separate live endpoint. Test-mode webhook registrations don't carry over. It must be publicly reachable over HTTPS.
2. **Live webhook signing secret.** This is the most common miss. If the handler still verifies against the test secret, every live webhook fails signature verification. If verification was skipped, fix that, because it's a security hole.
3. **Base URL and environment.** Confirm whether live uses a different host, and that nothing is hardcoded to the sandbox.
4. **Secret handling.**
   - Store the live key in a secrets manager, not in a repo, a shared chat, or CI logs.
   - Keep test and live keys strictly separated by environment.
   - Know how to rotate the live key, and who is allowed to.
5. **Account details.** Settlement bank account, statement descriptor, supported currencies, fees and minimums, receipt emails.

### Behavior the sandbox didn't prove

400 green payments almost certainly covered the happy path with magic test cards. Live traffic adds:

1. **Declines.** Soft versus hard declines, insufficient funds, expired cards, fraud blocks. Check that the booking flow handles each cleanly (no booking confirmed without payment, no payment taken without a booking).
2. **3-D Secure / strong customer authentication.** If they sell to EU or UK customers, the challenge flow must work end to end, including an abandoned challenge.
3. **Idempotency keys on every create call.** A retry after a timeout in live mode means a double charge unless the request is idempotent.
4. **Webhook robustness.**
   - Deduplicate on event ID.
   - Tolerate out-of-order and delayed delivery.
   - Respond fast and process asynchronously.
   - Reconcile from the API if a webhook is missed.
5. **Booking-specific money flows.**
   - Authorize versus capture, and how long authorizations last.
   - Deposits, cancellations, partial and full refunds, and disputes or chargebacks.
   - Cancellation or refund after a payout.
6. **Timeouts and failure modes.** What the booking UI shows if Meshpay is slow or down. Don't leave the customer in an unknown state.
7. **Data protection.** Confirm no raw card data touches their servers (hosted fields or tokens) and that logs redact keys and payment details.

### Production smoke test (Thursday at the latest)

Once the account is activated, run a small real payment with a real card. Then refund it. Verify the following:

- The live webhook arrives and passes signature verification.
- The booking record updates correctly.
- The refund flows through and appears in the dashboard.
- Reconciliation shows the payment and refund.

Do this before Friday, not on launch day.

## Launch-day plan (both teams)

- **Staged rollout.** Put live payments behind a feature flag. Start with a small percentage of traffic or a limited set of bookings, then ramp up. If the integrator can't do that, schedule the launch for a low-traffic window.
- **Kill switch.** The integrator can disable live payments in minutes, and knows the fallback (a "payments temporarily unavailable" message, or a retry queue).
- **Monitoring.** Payment success rate, webhook failure rate, and rate of 4xx and 5xx from Meshpay. Set alerts and thresholds ahead of time.
- **Named humans.**
  - One contact on each side for launch day.
  - A direct escalation path, not just a support inbox.
  - Agreed response times through the weekend, since a Friday launch means the first real traffic spike lands when coverage is thinnest.
- **Reconciliation.** Match bookings to payments to payouts daily for the first two weeks.

## Suggested timeline

| When | Who | Action |
|---|---|---|
| Today | Meshpay | Confirm review status and completion date |
| Today to Mon | Meshpay | Ship the 403 `account_not_activated` change, `account.activated` signal, and doc rewrite |
| Mon to Tue | Integrator | Live webhook endpoint and signing secret, secrets management, idempotency audit |
| Tue to Wed | Both | Walk through decline, 3DS, refund, and dispute cases. Agree on limits, monitoring, and kill switch |
| Thu | Both | Live smoke test (charge, webhook, refund, reconcile) and go/no-go |
| Fri | Both | Staged rollout with named contacts on call |

## Go/no-go gates for Thursday

Don't launch Friday unless all four hold:

1. The account review is complete.
2. The live webhook has been verified end to end.
3. The live smoke payment and refund both succeeded.
4. The integrator has a working kill switch and alerts.

If any gate fails, move the launch. A one-week slip costs far less than a first-customer incident with real money.