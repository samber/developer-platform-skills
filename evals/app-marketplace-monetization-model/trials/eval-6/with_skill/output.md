## Verdict

❌ **Don't ship the "most partners get paid within 30 days" line.** Your own pipeline makes it false for nearly every sale.
ℹ️ **The $10 minimum is fine to ship, but it won't fix cash flow.**

The skill's central point (§7) is that developers feel the hold window and batch timing, not the payout minimum. Comparable platforms set minimums of $50–$150, so active partners already clear $25 every cycle.

## The real timeline

I read your process as: month closes, 30-day refund window runs after close, then the batch goes out on the 15th of the month after the window ends. Example for March sales:

| Step | Date |
|---|---|
| Month closes | Mar 31 |
| Refund window ends | ~Apr 30 |
| Finance batch | May 15 |
| International wire lands | ~May 18–20 (+3–5 days) |

Sale-to-bank, by when in the month the sale happened:

| Sale date | To batch | To bank (international) |
|---|---|---|
| Mar 1 | 75 days | 78–80 days |
| Mar 16 (mid-month) | 60 days | 63–65 days |
| Mar 31 | 45 days | 48–50 days |

- ⚠️ The best case is ~45 days and a mid-month sale takes ~2 months. No sale clears 30 days.
- ⚠️ If your batch really runs on the 15th of the month right after close, it would pay sales still inside the refund window. That reading doesn't fit your process, so confirm with finance which one is true.
- The skill names this failure mode: "Modeling cash flow on headline language." It says to publish and plan on the real number.

## What to ship

**1. Replace the docs line with the honest timeline.** Draft:

> **Payouts.** We pay partners once a month, on the 15th. Each month's sales are paid on the 15th of the second month after the sale month, once the 30-day refund window has closed. Example: March sales are paid on May 15.
> International wires add 3–5 days. From sale to bank, expect roughly 45–80 days, about two months for a mid-month sale.
> Balances under $10 (USD equivalent) roll forward to the next payout.
> [Payout currency and FX: finance to fill in, see below.]

**2. The $10 minimum is optional. Check the economics first.**
- International wires carry fixed costs: sender, intermediary and receiving fees. If they're anywhere near $10, a $10 payout nets to roughly nothing for the partner and costs you a wire. The skill warns that flat per-payout fees can outweigh the money moved. Ask finance for your cost per wire.
- You bill in seven currencies, so define the threshold's currency. Either "USD equivalent at payout date" or a per-currency floor. Without that, partners in weaker currencies hit it at different real amounts.
- Say that sub-threshold balances roll forward.

**3. If you want to fix cash flow, change the schedule.** Candidates, cheapest first:

1. **Release each sale 30 days after it happens** instead of by monthly close, so the lag becomes ~33–35 days including the wire. Plan for a payout system that tracks per-sale eligibility, and don't promise "30 days" until finance confirms.
2. **Pay twice a month** (the 15th and the 30th), which cuts the average lag by about 15 days.
3. **Instant payout for a fee**, as an opt-in layer on top of the slower default. This is the skill's option for small partners whose cash flow is the constraint, and it carries the highest cost and risk to you.

Keep the 30-day hold itself. It matches your refund exposure and sits at the low end of the 30–60 day norm.

## Gaps the skill's publish checklist flags

- **Tax split is missing.** You're merchant of record in seven currencies, so you likely collect and remit tax in several places. The docs should say which tax, which jurisdiction and whose obligation. Counsel should review it. This is not tax advice.
- **FX policy is missing.** Under merchant-of-record billing you own currency conversion and rail choice. Publish the payout currency, who bears the conversion cost, and the rate source.
- **Silent tax failure risk.** Seven currencies means many jurisdictions. Monitor tax collection separately from payouts, because registration gaps return no error.

## Open questions for finance

1. Does the refund window start at month close or at each sale? (This should match the reading above.)
2. Are the "3 to 5 days" business days or calendar days? Do domestic partners get a faster rail?
3. What is the all-in cost per international wire?
4. What are the payout currency and FX rules today?

I skipped the skill's one-question-at-a-time interview and worked from the facts you gave. Those four answers could shift the timeline numbers.