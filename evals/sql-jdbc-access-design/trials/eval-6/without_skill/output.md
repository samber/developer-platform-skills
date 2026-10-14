# Sanity check: SQL access, "free on Business+ now, meter on warehouse credits later"

**Verdict:** ⚠️ Don't ship it as described. The core risk is that you'd launch a feature with unbounded variable cost, free to everyone, and every later fix would be a retroactive paywall.

## 1. Free launch plus "meter later" is a one-way door

- Pricing guidance for devtools says never move an existing capability from free to paid. A published free limit is close to permanent. At most you can shrink it for new accounts, and you must say so.
- "If we ever decide to charge" therefore means taking away something Business customers already depend on. That is the pattern that produces churn and angry threads.
- You said leadership wants a durable asset. A durable asset needs a revenue mechanism built in at launch, even if it is priced at zero for the first year.

**Fix:** launch with a published, explicitly revisable allowance and a meter that is live from day one. A limit that already exists can be raised later, whereas a free feature with no limit can't be given one without taking something away.

## 2. Your cost curve punishes "free"

You pay per byte scanned, and your accounts span roughly 2,000x (4 GB to 9 TB). Cost per query scales with the customer's data size, not with their plan price.

Illustrative arithmetic only. I'm assuming about $6/TB scanned, so swap in your real rate:

| Account | One full scan | A dashboard refreshing every 5 min, unpruned |
|---|---|---|
| 4 GB | about $0.02 | about $7/day |
| 9 TB | about $55 | about $16,000/day |

- Free SQL means a single bad `SELECT *`, a BI tool on auto-refresh, or an agent in a retry loop can cost more than the account's annual plan fee.
- Your retention thesis makes this worse. The feature works if customers wire it into dashboards, notebooks and agents, and those are the heaviest scanners. The stickier it gets, the more it costs you.
- Price the floor at the 90th-percentile account, not the average. The free surface's total cost should be a number you've agreed to, expressed as a share of paid gross profit. Today it is unbounded.

## 3. Metering on warehouse credits is the wrong unit

1. **It isn't your cost unit.** You are billed per byte scanned. Credits are an abstraction layered on top, and credits-to-bytes depends on engine, caching and concurrency. You'd be passing through a number you don't pay.
2. **Customers can't forecast it.** They can't estimate credits before running a query. A target customer should be able to estimate their bill from public material in about two minutes, within ±20%. Credits fail that test.
3. **It's a vendor-invented unit.** Credits with no clean published conversion read as obfuscation, whatever the intent.
4. **The incentives invert.** A markup on consumption means you earn more when customers write inefficient queries. Sophisticated buyers will notice, and they'll compute your unit economics themselves.
5. **Cost-plus has a ceiling.** Your margin is a fixed percentage of your own cost. The upside is capped, and you absorb every upstream warehouse price change. Cost-plus isn't tied to the value of the feature. Value shows up as retention and expansion, not credits.
6. **It's the highest-effort metric.** It needs a metering pipeline, caps, alerts, a forecasting tool and a dispute path behind every invoice. Don't start that for a unit you'll then have to defend.

## 4. What I'd do instead

**Metric.** Meter on bytes scanned, because it is your actual cost and engineers already know it from other warehouses. Because accounts differ 2,000x, set the allowance relative to their data. For example, "N full-scan equivalents per month" scaled to stored volume, rather than a flat TB figure. A flat figure either gives away 9 TB accounts or strangles 4 GB ones.

**Shape (hybrid).**
- Business+ includes an allowance, free, on the same axis as the eventual paid meter.
- Overage is priced per TB scanned, publicly, with a calculator.
- Hard cap by default for dev and ad-hoc use, soft cap with alerts for production.
- Itemized invoices, usage alerts at fixed thresholds, an anomaly alert, and a pre-approved credit policy for runaway queries.

**Cost guardrails.** These are cheap and apply whatever you charge.
- Dry-run byte estimates before execution.
- Per-query scan limits and timeouts.
- Partition and filter requirements on the largest tables.
- Result caching, and sample or materialized views for dashboards.
- Per-tenant concurrency limits.

**Ladder.** Enterprise tiers can raise the allowance, add dedicated capacity and add committed-spend discounts. That gives you a compounding expansion path, as opposed to a one-off feature win.

## 5. The retention claim is unvalidated

"Stickiest feature we could add" is the CRO's belief. Nothing you've told me measures it.
- Run it with design partners or a staged rollout and measure retention lift against a control before committing the cost structure.
- Because there's no hard ship date, you have room to do this. Use it.
- The retention thesis and the cost curve interact. If lift comes only from heavy scanners, you've bought retention at a variable cost you haven't capped.

## 6. Checks before committing

| Check | Source |
|---|---|
| Usage-only pricing models run about a 62% median gross margin versus about 80% for software overall | Sourced, cited in the pricing skill's evidence base. Direction is reliable, and your exact margin is not implied. |
| Model the 90th-percentile account, not the average | Self-set baseline, not an industry benchmark |
| Bill estimable in 2 minutes within ±20% on three real usage profiles | Self-set baseline |
| Never move free to paid, and shrink free limits for new accounts only | Sourced from the documented pricing-change cases |

## 7. Questions that would change the answer

1. What is your actual per-byte warehouse rate, and what does one typical query scan per account size?
2. What do the 9 TB and the median accounts pay per year? Does the plan fee cover a heavy-scan month?
3. Do customers query via BI tools or agents, which auto-repeat, or ad hoc?
4. Is there a materialized or sampled layer you can serve most queries from?
5. Is your goal to cover cost, or to price on value? The first points to a scan meter, and the second to tiers and committed spend.

**Bottom line:** keep the instinct to give SQL access to Business+. Replace "free, unlimited, charge on credits later" with a published and revisable bytes-scanned allowance, a live meter, guardrails, and a retention test before launch.