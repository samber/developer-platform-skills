# Marketplace plan review: tighten before shipping

⚠️ **The plan won't ship as written. Four of the five choices come from two incompatible Stripe Connect configurations.** Fix that first. The rest of this review depends on it.

## 1. Conflicts to resolve

Stripe Connect Accounts v2 has three independent dials: dashboard, fee collection, and loss liability. Only two combinations hang together:

| Your choice | Marketplace-shaped bundle | SaaS-shaped bundle |
|---|---|---|
| Destination charges | ✅ | ❌ (direct charges only) |
| `losses_collector: stripe` | ❌ blocked, platform must carry losses | ✅ |
| Full dashboard for vendors | ❌ (express) | ✅ |
| Your name on the statement | ✅ (platform is MoR) | ❌ (vendor's name) |
| 45-day hold | ✅ with separate charges and transfers | ❌ (vendor is paid directly) |
| Platform fee via `application_fee_amount` | ✅ | ✅ |

Your plan mixes columns, and each mix fails in a specific way:

- **Destination charges with `losses_collector: stripe`.** Any non-direct charge pattern requires the platform to carry losses, so this combination is blocked. The skill warns that near-miss combinations can silently leave you holding dispute losses you thought you had pushed to vendors. Destination charges also make you the merchant of record, so chargebacks are yours in practice.
- **Full dashboard with destination charges.** The full dashboard belongs to the SaaS-shaped bundle (direct charges). The charges here sit on your platform account, not the vendor's. I would not expect vendors to be able to self-serve refunds on those charges from their own dashboard. **Verify this on a test account.** It is the main reason your self-serve goal needs a different design.
- **45-day hold with destination charges.** Destination charges auto-pay the vendor on payment success. They are explicitly not for hold-and-release. A hold needs separate charges and transfers: charge the customer on the platform, then create the transfer yourself at day 45.
- **`application_fee_amount` under separate charges and transfers.** That parameter goes away. Your fee becomes the transfer amount, which is the charge minus your cut, and you compute and reconcile it yourself.

## 2. Recommended design

Choose which two of these you want to give up. I recommend keeping your name on the statement and the hold, because those two show up in the customer experience.

**Marketplace-billed (recommended):**

- **Charge pattern:** separate charges and transfers. The platform is MoR and the transfer is released at day 45.
- **Fee:** netted at source as charge minus transfer. Keep processing cost as a separate labeled line so your take rate isn't overstated.
- **Losses:** `losses_collector: application`. Chargebacks are yours. Price this into the fee and size the hold and reserve for it.
- **Dashboard:** express, plus a vendor-facing refund and reporting surface you build on your own API. Refunds go through your platform, with transfer reversal if the money has already moved.
- **Tax:** you are likely the party that collects it. See section 3.

**If you refuse chargeback exposure:** use direct charges and the SaaS bundle. Then the vendor is MoR, the vendor's name is on the statement, there is no platform hold, and tax and disputes move to each vendor. This conflicts with your stated goals. The skill's default is vendor-billed only while the take rate is zero, and you are charging a fee.

## 3. Things the plan doesn't mention

- **Hold sizing.** 45 days is inside the 30-60 day range of other marketplaces, but a card dispute can arrive after it. Check the dispute window for your card mix. If it is longer, add a rolling reserve instead of lengthening the hold.
- **Published sale-to-bank timeline.** A 45-day hold plus a monthly payout can mean about 75 days or more from sale to bank. Publish the real end-to-end number. Developers plan on the headline and then complain about the lag.
- **Tax by jurisdiction.** Destination or platform-billed charges usually make you liable. Marketplace-facilitator rules (US) and deemed-supplier rules (EU, B2C) can attach regardless of the billing posture. Publish a jurisdiction-by-jurisdiction split and have counsel review it.
- **Silent zero-tax failure.** Automatic tax with no active registration collects $0 and returns no error. You can't correct it retroactively. Monitor tax collection as its own system.
- **Unit economics.** Express accounts carry per-active-account and per-payout fees (about £1.60 per month plus 0.25% and £0.20 per payout, UK figures). Model the margin per active vendor, not per transaction. At low volume the flat fees can exceed your percentage.
- **Anti-circumvention rule.** You need a terms clause against routing billing around you, backed by delisting. Without it, the fee erodes as vendors reroute.
- **Fee-change notice.** Commit to six months' notice for fee changes and publish it with the fee schedule.
- **Waivers.** If you give small vendors a fee exemption, enroll them by default. Opt-in waivers silently charge qualifying vendors the full rate.
- **Pricing models.** Check that separate charges and transfers support every model you promise (flat, per-seat, usage-based, one-time) before you publish the menu. The rails cap what you can offer.
- **Entitlement and reporting.** Payment is one of three systems. Licensing and entitlement, and vendor revenue reporting, are separate builds.

## 4. Questions that could change this design

1. Is the take rate already decided, including tiers and whether any tier is zero? If not, settle that first. This design executes it and doesn't choose it.
2. Are chargebacks acceptable to carry (loss appetite)? This one decides between the two bundles.
3. Are any apps already billing customers directly that you can't migrate in one cycle? If so, you run both postures for a while.
4. Where are your buyers, and are any of them consumers? This sets the tax layer.
5. Which pricing models must vendors be able to offer?
6. Do you have a hard launch date, and how much billing engineering capacity do you have? A hard date favors the simplest posture.

I worked from the skill and its three reference files, so these points don't depend on your codebase. I didn't verify the dashboard and refund behavior against a live Stripe account, so test it before relying on it. Rates and thresholds in the references go stale, so re-check them before publishing.