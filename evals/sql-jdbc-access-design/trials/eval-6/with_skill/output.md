**Verdict: the model fails as written. Not "free for everyone" at Business+, and not "charge later by passing through credits."** Fix both before roadmap lock.

## Why it fails

1. **Free feature, per-byte cost, 2,250x size spread.**
   - Smallest account is 4 GB, largest is 9 TB.
   - Cost per account scales with bytes scanned, but revenue per account is flat or zero.
   - Your stickiest feature then costs most at your biggest, best accounts.
   - The skill says: package SQL access as a paid tier or add-on, never a free feature (step 8).

2. **Illustrative scan math.** The $6.25/TB rate is an assumption, so plug in your real rate. The scans are an upper bound: full-table scans, before partition pruning.

   | Account | Scans/day | Scanned/day | Cost/month |
   |---|---|---|---|
   | 4 GB | 20 | 80 GB | about $15 |
   | 9 TB | 20 | 180 TB | about $34k |

   - 20 scans/day is the dashboard line from the skill's tipping heuristic: one practitioner's rule of thumb, not a benchmark.
   - One 40-viewer dashboard at 20 refreshes/day puts one account past 20 scans/day.
   - Business plan price is unknown. Check it against this line.

3. **"Charge later" is a repricing, not a launch decision.**
   - Retrofitting a meter under a shipped free feature takes something away from customers.
   - The skill says a compounding-asset mandate promotes the consumption rung early. Leadership asked for a durable asset, so this applies.
   - You have no ship date, so you have no excuse to skip the meter.
   - Stripe Sigma changed its own metric after shipping (2025-09-30). It is possible but painful.

4. **Pass-through on warehouse credits is the wrong meter.**
   - The skill says to meter on a business unit the buyer understands, never on credits a non-technical buyer can't predict.
   - A BI dashboard on auto-refresh turns credit billing into bill shock.
   - A markup on raw cost invites comparison. A 9 TB customer will ask for a share and pay its own warehouse.
   - Your bill is per byte scanned, so "credits" may be the wrong unit. Meter what you actually pay for.

5. **Caps do the work a price would have done.**
   - Without a price, caps are your only governance (step 6).
   - Enforce all three per tenant before the first customer connects:
     - statement timeout
     - concurrency cap
     - spend cap, which here means a bytes-scanned quota
   - Also set a max bytes per query.
   - If your warehouse can't enforce a per-tenant spend cap, that blocks launch, because the cost gate is pass/fail.

## What holds up

- The tier gate at Business+ is the skill's default rung. Heap Connect uses the same shape.
- It is acceptable only with the step 6 caps in place.
- The retention thesis is plausible. Customers pay for this capability (Sigma, Heap, Mixpanel, HubSpot). That argues for charging, not for giving it away.

## Recommended model

1. **Include an allowance at Business+, not unlimited.**
   - The quota is bytes scanned per month, sized to cover your median account.
   - Put fair-use language in the contract on day one, so a later charge is not a repricing.
   - Hard caps stay on regardless.
2. **Price overage or higher volume tiers on a buyer-visible unit.**
   - For fleet telemetry, candidates are connected vehicles or data-volume tier. Pick one the buyer already tracks.
   - Bytes scanned stays your internal cost metric.
   - Publish the unit at launch.
3. **Meter from day one, even if you bill nothing.**
   - Track per-tenant query cost against price paid (a trend to baseline from month one).
   - Show customers their own usage. This avoids surprise later.
4. **Offer consumer-pays for the large accounts.**
   - Use a zero-copy share into the customer's own warehouse, as HubSpot does.
   - Your compute cost for the 9 TB tail drops to near zero.
   - Hosted endpoint stays for small and mid accounts.
5. **Cut bytes at the source.**
   - Serve a curated, partitioned, pre-aggregated mart layer, not raw telemetry (step 4).
   - It lowers scan cost and also gives you the schema-stability contract.
   - A replicated copy only helps if the replica's engine isn't also billed per byte scanned. Check that before choosing it.

## Re-rank against your constraints

- **No ship date:** removes the only reason to hold the flat rung. Build the meter.
- **Durable asset:** promotes consumption pricing. Consider per-tenant compute isolation too if customers run dashboards or agents at high frequency.
- **Effort ceiling:** unknown, which changes whether isolation is affordable.

## Assumptions to confirm (they change the numbers, not the verdict)

1. Which warehouse is it, and is the per-byte rate $6.25/TB or something else?
2. What is the Business plan price, and how many accounts sit above 1 TB?
3. Are the consumers dashboards (Tableau, Power BI), notebooks, or agents?
4. Is the data live in the warehouse today, or does it need replication?
5. Can your warehouse enforce a per-tenant bytes quota?

**Next, in 2 minutes:** pull the top 10 accounts by data size and multiply each by 20 scans/day at your real rate. If the top 10 cost more than their plan price, kill "free."