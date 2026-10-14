# Is our downside bounded? No, not by the 10-minute timeout.

Finance shouldn't sign off on the next 20 accounts yet. The timeout caps how long one statement runs. It doesn't cap how many statements run, how long the warehouse stays awake, how many clusters it scales to, or how much credit it burns per month. The revenue is fixed at $2,000 per customer, but compute is billed to us, so the margin is open-ended.

## Why the timeout doesn't bound spend

1. **Compute cost is warehouse uptime, not per-query.** Cost is credits per hour × size × clusters × hours awake. A killed query still bills the ten minutes it ran.
2. **A timed-out dashboard query repeats forever.** With a 15-minute refresh, a query that always hits the timeout runs 10 of every 15 minutes, about 67% duty cycle, indefinitely. Nothing stops it, and the customer may not notice.
3. **Two dashboards may already keep the warehouse always on.** With the common 10-minute auto-suspend, one 15-minute refresh keeps it awake roughly 10+ of every 15 minutes. Two dashboards at different offsets leave it awake close to 24/7, even if every query is fast. With a 60-second auto-suspend, the floor is much lower (about 96 resumes/day, billed at 60 seconds minimum each).
4. **One customer can consume the whole fee.** At an assumed $3/credit, $2,000 is about 667 credits. That is one XS warehouse running continuously, or about 2.8 hours a day on a Large.
5. **The warehouse is shared.** Today we can't attribute cost to a customer, and one heavy customer's load lands on everyone's bill.
6. **The timeout may not cover everything.** I don't know whether reader-account admins can create their own warehouses. If they can, they bypass the timeout, and that compute is also billed to us. This needs checking.

## Worst-case ceiling for one always-on warehouse

This assumes $3/credit and 720 hours a month. Please substitute our contract rate, which I don't have.

| Size | Credits/hr | Monthly ceiling, 1 cluster |
|---|---|---|
| XS | 1 | ~$2,160 |
| S | 2 | ~$4,320 |
| M | 4 | ~$8,640 |
| L | 8 | ~$17,280 |
| XL | 16 | ~$34,560 |

- **Multi-cluster multiplies this.** A Large with max 4 clusters tops out near $69k a month. That is more than the $64k we'd bill at 32 customers.
- **One bad dashboard is enough.** A single always-timing-out dashboard query on a Large costs about 480 hours × 8 credits, roughly $11.5k a month. That is about 5.8× that customer's fee.
- **For comparison:** 12 customers bring in $24k a month today, and 32 would bring in $64k.

The real ceiling is therefore the warehouse's size, max clusters and auto-suspend setting, plus any resource monitor. Whether that ceiling is below revenue depends on facts I don't have.

## What I need from you

1. The warehouse size.
2. The max cluster count.
3. The auto-suspend setting.
4. Whether a resource monitor exists, and its quota and action.
5. Whether reader-account admins can create warehouses.
6. Our credit price.
7. Last month's actual credits for this warehouse, from `WAREHOUSE_METERING_HISTORY`.

Item 7 is the fastest sanity check. If actual spend is already near $2,000 × the number of active customers, the answer is clearly no.

## Fixes that would make it bounded

Do these before the next 20 accounts.

1. **Add a resource monitor** with a monthly credit quota that suspends immediately at 100%, with notifications at 50%, 75% and 90%. This is the only hard dollar cap. Check whether it can be set per reader account.
2. **Give each customer their own XS warehouse and monitor.** This caps each customer's worst case near their fee and makes the cost attributable. Billing is per-second with a 60-second minimum per resume, so idle warehouses are cheap.
3. **Set auto-suspend to 60 seconds** and keep max clusters at 1, or 2 at most.
4. **Cut the statement timeout** from 10 minutes to something like 60–120 seconds for dashboards. Keep a separate, tighter-capped warehouse for ad-hoc work if it's needed.
5. **Block warehouse creation** in the reader accounts, or confirm it's already blocked.
6. **Alert on spend per account** using the `READER_ACCOUNT_USAGE` views, so a runaway dashboard shows up in days, not at month end.
7. **Add contract terms.** A fair-use clause, a stated compute allowance per customer, and an overage rate or the right to throttle would turn the flat fee into a bounded exposure.

If you can send me the answers to the list above, I can put a real number on the worst case. I haven't verified Snowflake's current credit pricing or reader-account behavior against documentation, so check those points with Snowflake or your account team.