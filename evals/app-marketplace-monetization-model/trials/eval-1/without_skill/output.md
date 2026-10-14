# Calvetta paid apps: monetization design

⚠️ Everything beyond "paid apps by Q2" and "20–25% take rate" is my assumption. I list the assumptions in section 1. Please confirm or correct them before anyone builds.

**Next action this week:** get answers to the 5 questions in section 11. They set the design for merchant of record, scope, and the date by which you must fix the take rate.

---

## 1. What's decided and what isn't

| Item | Status |
|---|---|
| Paid apps live by Q2 | ✅ Decided |
| Take rate 20–25% | ⚠️ Range only |
| Who sells (third-party publishers or Calvetta) | ❌ Not decided. I assume third-party publishers, with Calvetta able to publish too. |
| Fate of the 310 free connectors | ❌ Not decided. I assume they stay free and nothing is retroactively charged. |
| Merchant of record, pricing models, payouts, refunds | ❌ Not decided. Proposed below. |

Assumptions to confirm:
- Q2 means Apr–Jun 2027, about 26 weeks from today (2026-10-03).
- Customers already pay Calvetta through some billing system.
- Many of the 310 connectors are built by the vendors whose products they connect to.

## 2. Core recommendation

1. **Build take rate as configuration, not code.** "We'll land on it later" is safe only if the rate is versioned data.
2. **Fix the rate before the first publisher signs.** That is about week 8, not "later". Publishers need the number in their agreement.
3. **Launch at 20%.** Raising a rate later breaks trust, and cutting it is easy. The difference between 20% and 25% is small (section 3), and supply of paid apps is your real constraint.
4. **Make Calvetta the merchant of record.** Customers get one Calvetta invoice with app add-on line items. This suits mid-market procurement.
5. **Buy, don't build, the money movement.** Use a marketplace-payments product such as Stripe Connect, or whatever your current billing vendor offers. Build only the catalog, entitlements, and ledger on top.
6. **Keep the 310 free connectors free.** Paid apps are a new listing class. Publishers can opt in to a paid tier on an existing connector.

## 3. What 20% vs 25% is worth

⚠️ These numbers are illustrative. My assumptions are one paid app per paying customer at $100/month. Replace them with your real attach data.

| Customers buying a paid app | Subscriptions | Annual GMV | Take at 20% | Take at 25% | Gap |
|---|---|---|---|---|---|
| 5% | 45 | $54k | $10.8k | $13.5k | $2.7k |
| 10% | 90 | $108k | $21.6k | $27k | $5.4k |
| 20% | 180 | $216k | $43.2k | $54k | $10.8k |

At 900 customers, the five-point gap is worth roughly $3–11k a year. The case for this program is retention, ecosystem depth, and growing the customer base over time. Fees alone won't pay for it. Don't spend a month debating the rate; spend it recruiting publishers.

Check before you sign off: ask leadership whether the revenue target assumes this base or a much larger one.

## 4. Take-rate mechanics

**Fee base.** The fee applies to the price excluding tax. Calvetta absorbs payment processing costs out of its take, so the publisher sees one clean number.

**Rate card.** Rates are versioned rows, resolved in this order:
1. App-level override
2. Publisher-level override
3. Global default

Each row has an effective date.

**Snapshot at charge time.** Every ledger entry stores the rate that applied when it was created. A later rate change affects only future charges.

**Launch incentives.**
- Discounted rate (for example 10%) for the first 10 publishers for 12 months, written into their agreements as a dated term.
- No exclusivity required.

**Refunds and chargebacks.** The fee reverses in proportion to the refund. Chargeback losses are carried by the publisher, as set out in the agreement.

⚠️ Do not add tiered or volume-based rates at launch. They add complexity and have no data behind them yet.

## 5. Pricing models publishers can use

At launch:
- Flat per workspace, monthly or annual
- Per Calvetta seat
- Free trial (7–30 days, set by the publisher)
- Free tier plus paid upgrade

Phase 2 (after GA):
- Usage-metered pricing, billed in arrears
- Promo codes and coupons

Rules:
- The publisher sets prices, within Calvetta's minimum price floor (suggest $10/month so fees don't eat the sale).
- Annual plans have no mid-term refunds except under the refund policy.
- Price changes apply to new subscriptions immediately. Existing subscribers get 60 days' notice.
- Calvetta shows the final price including tax in the checkout flow.

## 6. Billing architecture

**Entities.**
- Publisher
- App
- Plan
- Price
- Subscription (customer × app)
- Entitlement
- Usage event (phase 2)
- Invoice line
- Ledger entry
- Payout

**Ledger.** Double-entry. Each sale produces:
1. Customer charge
2. Tax collected
3. Calvetta fee (with the rate snapshot)
4. Publisher payable

Refunds and chargebacks post as reversing entries. Never edit a past entry.

**Customer-facing flow.**
1. The customer clicks Install on a paid app.
2. They see price, trial terms, and who gets billed.
3. They confirm on the existing Calvetta payment method.
4. The entitlement is granted immediately.
5. The charge appears as an add-on line on the next Calvetta invoice, or immediately if the plan is prorated.

**Entitlements.**
- Apps check entitlement through a Calvetta API and receive webhook events: `granted`, `renewed`, `past_due`, `revoked`.
- Failed payment: 14-day grace period with dunning emails, then revoke. Data is kept 30 days after revoke.
- Cancel takes effect at period end.
- Mid-term upgrades are prorated. Downgrades apply at the next renewal.

**Payouts.**
- Monthly, net 30 after month-end.
- Minimum payout threshold (suggest $100, carried forward).
- Publishers must complete tax onboarding first (for example W-9/W-8 for US payees, and any required EU reporting).
- Publishers get a statement with every payout: gross, tax, fee, refunds, net.

**Buy vs build.** Use a vendor for payments, tax calculation, KYC, and payouts. Build the catalog, entitlement service, ledger views, and reporting. If your current billing system can't carry third-party line items, that is the first technical question to answer.

## 7. Existing 310 connectors

1. Audit the 310 and label each one: vendor-built, Calvetta-built, or community-built.
2. Keep all of them free by default, labelled "Free".
3. Calvetta-built connectors: do not move existing functionality behind a paywall. Customers who got it free will see it as a bait-and-switch.
4. Vendor-built connectors: the vendor decides if they want a paid tier. Many vendors give their connectors away to drive their own product, so expect most to stay free.
5. New paid listings must offer something the free connectors don't, such as deeper workflows, support, or SLAs.

## 8. Marketplace policy and trust

- **Publisher agreement:** revenue share, payout terms, refund policy, data handling, takedown rights. Needs legal review.
- **Review bar:** raise it for paid apps. Money changes the risk, so add a security review and a support-contact requirement.
- **Support ownership:** the publisher is level 1, Calvetta is level 2 for billing issues. Define response times.
- **Refund policy:** 14 days on first purchase (suggest), at Calvetta's discretion, charged back to the publisher.
- **No off-platform billing:** forbid publishers from steering Calvetta customers to pay outside the marketplace, with a narrow carve-out for existing contracts. Enforcement is hard, so keep the clause simple.
- **Disclosure:** show a clear "Paid" badge and price on every listing.

## 9. Timeline (about 26 weeks)

| Weeks | Phase | Output |
|---|---|---|
| 1–4 | Decisions | Answers to section 11, merchant-of-record call, vendor choice, legal engaged |
| 5–8 | Foundations | Rate card config, ledger design, publisher agreement draft, **take rate fixed** |
| 9–16 | Billing core | Catalog, checkout, entitlements, invoices, payouts in test mode |
| 17–20 | Closed beta | 3–5 publishers, a handful of friendly customers, real money, small volume |
| 21–24 | Hardening | Refunds, dunning, tax edge cases, publisher dashboard, support runbook |
| 25–26 | GA prep | Docs, listing UI, announcement |
| Q2 | GA | Paid apps live |

⏳ The schedule is tight. The usual slip is legal and tax setup, not code. Start that in week 1.

## 10. Metrics and guardrails

Track from beta:
- Paid-app attach rate (% of customers with at least one)
- GMV and net take
- Paying publishers (apps live vs apps with at least one sale)
- Refund rate, failed-payment rate, involuntary churn
- Support tickets per 100 subscriptions
- Effect on retention of customers who install paid apps vs those who don't

Review after 90 days of GA. Adjust the rate, incentives, or price floor from real data. Don't change the take rate retroactively.

## 11. Decisions I need from you

1. **Who builds the 310?** Mostly vendors, mostly Calvetta, or community? This decides whether paid apps will have enough supply.
2. **Fiscal calendar:** does Q2 mean Apr–Jun 2027?
3. **Current billing stack:** what bills customers today, and can it carry third-party line items?
4. **Merchant of record:** do you agree Calvetta takes this role? It brings tax and compliance duties, so finance and legal must sign off.
5. **Revenue expectation:** has leadership attached a number to this? Section 3 suggests direct fees will be modest at 900 customers, so it's worth confirming the goal.

Once you answer these, I can turn this into a build plan with tickets, a publisher agreement outline, and the ledger schema.