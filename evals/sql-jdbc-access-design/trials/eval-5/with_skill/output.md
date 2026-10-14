**No. Your downside is not bounded.** Do not sign off on the next 20 accounts yet.

A 10-minute timeout limits one query. It does not limit how many queries run or how long the warehouse stays on. The SKILL.md reader-account trap says provider-billed reader-account warehouses can burn unlimited credits on your bill unless a resource monitor caps them. You haven't mentioned one. Without a monitor, the monthly ceiling is the warehouse running 24/7.

## Worst-case math

All numbers below are illustrative. I assume $3 per credit, so replace that with your contract rate. I don't know your warehouse size.

| Case | Calculation | Cost per account per month |
|---|---|---|
| One dashboard where every refresh hits the timeout (X-Small) | 96 refreshes/day × 30 = 2,880 refreshes × 10 min = 480 h × 1 credit/h | ~$1,440 |
| Same dashboard on Medium | 480 h × 4 credits/h | ~$5,760 |
| Warehouse always on (X-Small) | 720 h × 1 credit/h | ~$2,160 |
| Warehouse always on (Large) | 720 h × 8 credits/h | ~$17,300 |

- Each of these ignores multi-cluster scaling and dashboards with several tiles per refresh, which multiply the cost.
- Two dashboards are already live. At the worst case, one customer can cost more than its $2,000 fee.
- Adding 20 accounts adds 20 uncapped exposures, each with its own warehouse.
- These are worst cases, not forecasts. Typical dashboard queries run seconds, so real spend is likely far lower. I have no measurement, and you need one before finance signs.

## Why the design doesn't protect you yet

1. **Spend cap missing.** The timeout bounds one query. A resource monitor bounds the month. SKILL.md step 6 calls a monitor on every reader account the single most important cost control on this surface.
2. **Scan frequency is past the default rung.** Zero-copy share is the default only while scans are infrequent. A dashboard refreshing every 15 minutes means 96 scans a day. The rule of thumb in SKILL.md (Alex Merced, ~20 scans/day on a ~200 GB table) puts you past the point where a replicated copy is cheaper. It is one practitioner's heuristic, and your table size decides it.
3. **Flat price meets provider-pays compute.** A flat add-on is the default pricing rung. It is acceptable only with the step 6 caps in place. The unbounded heavy user is its known risk, and your two dashboard customers fit that description.
4. **Other step 6 controls are unconfirmed.** You told me about the timeout only. I can't tell whether you have a queued-statement timeout, a concurrency cap per account, or auto-suspend tuned below the 15-minute refresh interval.
5. **Isolation is not in your message.** Cost is not the only asymmetric risk. A leak returns another customer's rows. Confirm the share uses secure views keyed on `current_account()`, not `CURRENT_ROLE()` or `CURRENT_USER()`, which return NULL across a share. Confirm you have run probe queries as a second tenant and got zero foreign rows. SKILL.md says these two gates must pass before any customer gets a handle.

## What makes it bounded

1. **Put a resource monitor on every reader account, current and future.**
   - Set the credit quota so worst-case spend stays below the fee. Finance picks the margin.
   - Add notify thresholds at 50/75/90%.
   - Use suspend-immediate at 100% so in-flight queries stop. Plain suspend lets them finish.
   - Script it. With 32 accounts you will skip one by hand.
2. **Tighten the other controls.**
   - Cut the statement timeout to just above the measured slowest legitimate dashboard query. 10 minutes is the ceiling, not a target.
   - Add a queued-statement timeout.
   - Cap concurrency per account.
   - Keep multi-cluster maximum at 1.
   - Set auto-suspend short.
3. **Measure the two live dashboards.**
   - Pull their last month of warehouse credits and query durations from the reader-account usage views.
   - Compare credits × your rate against the $2,000 fee.
   - This tells finance the real run rate, which the worst-case table cannot.
4. **Decide the dashboard architecture from that measurement.**
   - If scans are heavy, move dashboard customers to a replicated curated mart (rung 2). It costs staleness plus a second copy of the data to govern.
   - Never point the replica at the live operational schema.
5. **Revisit pricing if per-account cost is wide.**
   - If measured cost varies a lot across customers, a flat $2,000 loses money on the heavy ones.
   - SKILL.md says to promote to a consumption or volume-tiered shape when your cost exposure is consumption-based. Meter on a business unit the buyer understands, not on credits.
   - Otherwise keep flat, with monitors in place.
6. **Run the isolation probe as a second tenant** and record the pass.

## Sign-off rule for finance

Cost gate: every reader account has a statement timeout, a concurrency cap, and a spend cap, audited pass/fail per account. With that in place, the worst loss per account per month is the monitor quota plus any overshoot. Until then, the answer is no.

Beyond the gates, track three trends from month one: per-account compute cost against the $2,000 paid, connectivity tickets per new connection, and freshness against the refresh SLA.

## Open facts I need

- Warehouse size, and whether it is multi-cluster.
- Your credit rate.
- Whether resource monitors exist today on the 12 accounts.
- Table sizes the dashboards scan.
- Queries per dashboard refresh.
- Auto-suspend setting.
- Whether the isolation probe was run.

**Next (2 minutes):** run `SHOW RESOURCE MONITORS` in each of the 12 reader accounts and tell me which return empty.