# Stripe Connect plan: what to tighten before shipping

I haven't checked this against live Stripe docs or your account config, so confirm the items marked **verify** with Stripe. Three of your five pieces conflict with each other. Fix those first.

## ❌ Blockers

**1. Destination charges can't give you a 45-day hold.**
- A destination charge transfers the vendor's share to their balance at charge time.
- With full Dashboards, the vendor controls their own payout schedule, so they can pay out immediately.
- Platform-set payout delays are capped at about 31 days in most countries, and a full-Dashboard account doesn't give you that control anyway. **Verify** both.

Pick one:
- **Separate charges and transfers (recommended).**
  - Charge on the platform, keep the funds in your balance, and create the transfer at day 45 with `source_transaction`.
  - Your name stays on the statement.
  - You lose `application_fee_amount` and just transfer `amount − fee`.
  - **Verify** Stripe's limits on how long you can defer a transfer.
- **Destination charges with no real hold.** Keep the fee mechanics and give up the hold, or replace it with a risk-based reserve.

**2. Vendors can't self-serve refunds on destination charges.**
- The charge belongs to your platform account. The vendor's Dashboard only shows a transfer from you, not the customer's payment.
- You need your own refund request flow, and your backend executes it.
- Pass `reverse_transfer: true` and `refund_application_fee: true` on refunds of destination charges. Neither is on by default.
- Self-serve refunds only come with direct charges. Direct charges put the vendor's name on the statement, which breaks your goal.

**3. `losses_collector: stripe` doesn't remove your chargeback exposure.**
- It governs negative balances on the connected account. It doesn't move the dispute off a platform-owned charge.
- The dispute is filed against your charge, and the dispute fee and disputed amount debit your balance.
- Vendors can't answer the dispute in their Dashboard. You have to collect evidence from them.
- **Verify** with Stripe, in writing, exactly what losses it covers in your configuration.

## ⚠️ Tighten

4. **The hold window is shorter than the dispute window.** Card disputes run about 120 days, and some run longer. A 45-day hold leaves days 46 to 120 exposed. Options:
   - Hold longer for new vendors.
   - Keep a rolling reserve of 5 to 10%.
   - Tier holds by vendor risk and refund rate.
5. **Cross-border.** Destination charges without `on_behalf_of` generally only work when the platform and vendor are in the same region. Adding `on_behalf_of` makes the vendor the business of record, which changes the statement descriptor. If vendors are international, separate charges and transfers avoid this.
6. **Statement descriptor.** Set it at the platform level and use `statement_descriptor_suffix` per app. Test it on a real card, because banks truncate.
7. **Fee math.**
   - Stripe processing fees hit your balance, not the vendor's, so the platform fee must cover them with margin on small tickets.
   - Check partial refunds: do you refund a proportional share of your fee?
   - Check that `fees_collector` is consistent with what you expect. **Verify.**
8. **Transfer failures and negative balances.** Once you've released funds, a late refund or dispute needs a transfer reversal. That fails if the vendor's balance is empty. Decide who covers it, and write that into the vendor terms.
9. **Webhooks and idempotency.**
   - Listen for `charge.dispute.created`, `charge.refunded`, `transfer.reversed`, `account.updated`, and `payout.failed`.
   - Put idempotency keys on every transfer, refund, and reversal.
   - Use `transfer_group` per order.
   - Make the day-45 release job re-check dispute, refund, and account status before it pays.
10. **Vendor eligibility gate.** Don't release if `payouts_enabled` is false or requirements are past due. Hold the funds and notify the vendor.
11. **Non-Stripe items to check.**
    - Tax: marketplace-facilitator and VAT obligations, probably via Stripe Tax.
    - Vendor ToS: disclose the 45-day hold and your refund and dispute rules.
    - Legal: have counsel confirm that deferred releases don't push you into money-transmission territory in your markets.

## 🎯 Recommended shape

1. Separate charges and transfers, with the platform as merchant of record.
2. A day-45 release job that rechecks dispute, refund, and account state.
3. A vendor refund request flow on top of your own refund endpoint.
4. A risk-tiered reserve to cover the dispute window.

## Questions that change the answer

- Which countries are your vendors and buyers in?
- What's the average ticket size? This decides whether fixed fees and the dispute fee matter.
- Are vendors already on Stripe? Full-Dashboard accounts can be attached to other platforms.