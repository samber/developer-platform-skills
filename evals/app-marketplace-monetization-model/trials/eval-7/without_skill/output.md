# Fee schedule and billing bypass: recommendation

I'm not a lawyer, so have counsel review the amendment language before it goes out. I also assumed card-processing rates of about 2.9% + $0.30, since I don't have your real ones.

## Do first (about 1 week, before any partner contact)

1. Pull every document the partner has accepted: the partner agreement, marketplace terms, developer policy, API terms, brand rules. Search them for "billing", "payment", "steering", and "circumvent". The agreement may be silent while another document isn't.
2. Check the amendment clause in the partner agreement. It sets your notice period and whether you can change terms unilaterally.
3. Capture evidence of the link: screenshots, dates, and which onboarding step shows it.
4. Size the damage. Estimate the share of that app's revenue now bypassing you and the exposure across its 190 installs. This number sets how hard you push.
5. Check whether any other partner does the same. If one does, others will follow, so write a general rule rather than a one-off.

## Part 1: the 18% all-in fee

**Keep the single headline number.** The risk is what "all-in" hides.

Margin by ticket size, with processing at 2.9% + $0.30:

| Sale | Fee at 18% | Processing | Your net |
|---|---|---|---|
| $100 | $18.00 | $3.20 | $14.80 (14.8%) |
| $10 | $1.80 | $0.59 | $1.21 (12.1%) |

Your net falls further on international cards, FX, and AmEx, and processors don't return fees on refunds. Chargebacks add dispute fees on top.

**Define "all-in" tightly in the agreement:**
- 18% covers standard card processing only.
- It excludes taxes and VAT. Say whether the base is gross or net of tax.
- It excludes chargeback and dispute fees, passed through at cost.
- Refunded sales return the partner's share pro rata, and you keep nothing extra for lost processing fees.
- It excludes FX and cross-border surcharges, or caps them.

Then check your margin by cohort (ticket size, region, refund rate). If small-ticket apps are underwater, add a per-transaction minimum or exclude micro-transactions. Don't change the headline.

**The $2,500 submission fee needs a precise definition:**
- What counts as a "submission"? Recommended: initial listing and major-version reviews. Patch updates are free.
- Rejected submissions get free resubmission within 60 days.
- The fee is due at review start and refundable only if you cancel the review.
- Option: credit the fee against the first 12 months of commission. This makes it a commitment signal instead of a pure toll, and it softens the combined cost.

**Rollout:**
- Existing partners get 60–90 days' written notice, or whatever the amendment clause requires.
- The new fee applies to new submissions and renewals only. No retroactive charges.

## Part 2: the "pay here instead" link

**Posture:** it isn't a breach today, so don't accuse the partner of one. Don't delist or throttle them: it's your second-largest app, and acting without contractual grounds invites a dispute you could lose.

**Why this probably happens:** under 18% all-in, the partner can buy processing alone for roughly 3%, so bypassing saves them about 15 points. That is rational behavior, and a rule alone won't fix it.

**Recommended structure:**

1. **Fee on customers you sourced, wherever they pay.** Define "marketplace-sourced customer" (installed via the marketplace, with an attribution window such as 24 months). Commission applies to their revenue regardless of checkout.
2. **Require marketplace billing for in-app purchases by those customers.** This is the anti-circumvention clause.
3. **Add reporting and audit rights.** Partners report off-platform revenue from sourced customers quarterly, and you can audit.
4. **Lower the rate on partner-sourced customers.** Offer something like 5–8% for customers the partner brought themselves. This is the key lever: 18% on customers they already owned is hard to defend, and the discount removes most of the incentive to leak.
5. **Grandfather period.** Existing customers keep their current terms for 90 days, and the new rules apply from the renewal date.

Apply this to all partners via the same amendment as Part 1. A single v2 partner agreement avoids singling out one app, though they will notice the timing.

## Sequence

| When | Action |
|---|---|
| Week 1 | Document review, evidence, revenue sizing (above) |
| Week 2 | Call the partner. Ask why they added the link, and don't lead with threats. Their answer tells you whether it's price, UX, or control. |
| Weeks 2–3 | Counsel drafts v2: fee definitions, sourced-customer clause, audit rights |
| Week 4 | Send v2 to all partners with notice |
| Day 60–90 | v2 takes effect. Review compliance on the large apps first. |

## Open questions for you

1. What share of the bypassing partner's revenue was marketplace-sourced versus their own customers? This decides how much the lower partner-sourced rate (point 4) is worth.
2. What are your real processing rates and refund rate? The margin table above depends on them.
3. Is the partner's behavior covered by any other document you've accepted? Step 1 answers this.