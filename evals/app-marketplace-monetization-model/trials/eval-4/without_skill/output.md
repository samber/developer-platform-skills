# Verdict: don't send the deck as written

The deck promises four pricing models and the checkout supports two. The trial mandate and the variants layout are fixable, but both need small changes before Monday.

## 1. Pricing models: deck vs. checkout

| Deck promise | Checkout today | Status |
|---|---|---|
| Flat subscription | Native | ✅ |
| One-time add-on | Native one-time purchase | ✅ |
| Per-seat | Not listed. It works only if the subscription supports quantity, mid-cycle seat changes and proration | ⚠️ Unverified |
| Metered usage | Not listed. It needs usage ingestion, rating and billing in arrears, which a subscription-plus-one-time checkout doesn't do | ❌ Gap |

**Next action:** ask the commerce vendor two yes/no questions today. Does a subscription support a quantity with proration? Is there any usage-reporting API?

Options for metered usage, in order of preference:
1. **Cut it from the deck** and say "usage-based pricing: roadmap". Don't give a date until engineering commits to one.
2. **Offer substitutes now**: flat tiers with included usage caps, or prepaid credit packs sold as one-time purchases.
3. **Don't let vendors bill usage off-platform.** It breaks your revenue share and creates payout disputes.

If per-seat fails the check, treat it the same way. Offer fixed seat bundles (5, 10, 25) as separate plans, and keep it in the deck only if you can build that by launch.

## 2. Forced 14-day trial for every vendor

I'd push back on the mandate as written:
- **A trial is meaningless on one-time add-ons.** There is nothing to convert to, and it is a free product giveaway.
- **Usage and COGS-heavy products pay for the trial themselves.** Vendors with real per-user cost, such as compute, API calls or human onboarding, will refuse or leave.
- **Sales-led and enterprise vendors don't self-serve.** A forced trial hurts their funnel.
- **Abuse is on you.** Repeat sign-ups with new emails, trial plus coupon stacking, and chargebacks after the first charge all land on the marketplace. Decide whether a card is required up front.
- **Imposing it on partners in a Monday launch deck** invites pushback before they've seen the product.

**Better:**
- Make the trial **a default-on option per subscription plan**, with vendor opt-out.
- Never apply it to one-time add-ons.
- Fix the length at 14 days, so buyers get a consistent experience.
- Block repeat trials per buyer per product.
- Decide who funds coupons and trials, and whether the marketplace takes revenue on a trial that never converts.

## 3. Price variants under a single product

Tidy catalog, but several things break when everything is a variant:
- **Trials and coupons usually attach to the product or price.** One 14-day trial could apply to the one-time variant too, which makes no sense.
- **Mixed billing models under one product** blur entitlements, renewals, refunds and vendor payout reporting. "Which plan is this customer on?" gets harder to answer.
- **Price changes need a new variant.** Existing subscribers must stay grandfathered, so variants accumulate. Check for variant-count and option limits in your vendor's catalog model.
- **Per-seat and metered don't fit a variant at all.** They need quantity or usage, not a fixed price.

**Better structure:**
- One product per vendor offering.
- Variants only for **tiers and billing periods of the same model** (Basic / Pro, monthly / annual).
- Add-ons as **separate products** linked to the parent.
- Get tidiness from collections or categories, not variant packing.

## Before Monday

1. Get answers from the commerce vendor on seat quantity, usage API, trial configuration level (product, price or plan) and coupon scope.
2. Run a one-hour spike: one product with monthly and annual variants, plus a separate add-on. Walk through buy, trial, coupon, renewal, refund and payout. This takes out the guessing.
3. Revise the deck: drop or relabel metered, mark per-seat per the answer, change the trial to default-on opt-out for subscriptions only.
4. Tell the head of partnerships the trial rule needs refining, using the one-time and COGS arguments above.

## Open questions I couldn't check

- Whether the checkout handles multi-vendor payouts and tax. I only know what you described.
- Which commerce vendor it is, so the catalog limits above are unverified.

I didn't look at any code or files for this. It's based only on your description.