# Cost and pricing: Slatewave Snowflake share

## Answer for Finance

**Yes, it costs money per customer, but only for customers outside our region.** About 55% of target accounts are in eu-central-1 and ap-southeast-2, and we pay for them.

A Snowflake share only works inside one region and cloud. For the other regions we replicate the data into a Slatewave account there. Our provider account pays for that replication, and the customer pays only for their own queries.

This corrects the skill's "zero copies, zero egress" line. That line holds only for same-region recipients. The 45% remainder is assumed to be AWS us-east-1 and costs us near zero. I haven't verified that.

## Who pays what

| Cost line | Same-region (us-east-1) | Cross-region (EU, APAC) |
|---|---|---|
| Storage of the data | Us (already stored) | Us, for one extra replica per region |
| Data transfer (egress) | None | **Us.** Initial load plus every refresh |
| Replication compute | None | **Us.** Serverless credits per refresh |
| Customer query compute | Customer | Customer |
| Reader accounts (customer has no Snowflake) | Us | Us |
| Onboarding and support | Us | Us |

Rules:
- Storage and compute for replication scale with the number of regions, not the number of customers, if one tenant-partitioned replica serves everyone in that region.
- Transfer scales with bytes that change in each refresh. Mutable HR data (promotions, terminations, comp changes) rewrites micro-partitions, so changed bytes can far exceed logical changes.
- Reader accounts are outside scope. The 55% already have Snowflake.

## Per-customer formula

```
monthly cost per cross-region customer =
    D × storage_rate                           // replica storage
  + (D × churn × amplification × refreshes) × transfer_rate   // egress
  + refreshes × replication_compute            // serverless credits
  + fixed_regional_cost / customers_in_region  // standing floor
  + support_hours × loaded_rate
```

Inputs to pull, in this order:
1. `D`: GB per tenant, p50 and p90.
2. `churn`: share of rows changed per day.
3. `amplification`: bytes replicated per byte logically changed. Measure it, don't guess.
4. `refreshes`: per month (set by the cadence we choose).
5. Rates: Snowflake's service consumption table, and AWS inter-region transfer, per region pair.

### Illustrative example

These are my assumptions, not verified rates. Rates are placeholders; check them against Snowflake's current consumption table.

- `D` = 20 GB, 2% daily change, amplification 5×, daily refresh.
- Changed bytes: 20 GB × 0.02 × 5 × 30 = 60 GB per month.
- Transfer at an assumed $20/TB is about $1.20 per month. At an assumed $140/TB (APAC-style rate) it is about $8.40.
- Replica storage is about $0.50 per month.

At this size, variable cost is cents to single dollars per customer. The risks are elsewhere:
- **Fixed regional floor.** ap-southeast-2 holds 15% of accounts, so its standing cost spreads thinnest and its per-customer cost is highest.
- **Tail customers.** An enterprise with 50× the data and heavy churn can cost 50× as much.
- **Cadence.** Hourly refresh multiplies compute and transfer by 24 versus daily.
- **New regions.** Each region a customer demands adds a step cost.

## Residency changes the cost design

Employee data is EU personal data. If the primary copy sits in us-east-1, EU customers already face an SCC and TIA question before any share exists.

Two options:
- **Replicate to eu-central-1** (what leadership's plan implies). The us-east-1 primary stays an unresolved transfer, and we need SCC and TIA paperwork.
- **Make eu-central-1 the primary for EU tenants.** The EU share becomes same-region, with no replication cost for them. The cost moves to running a second primary.

Decide this before finalizing cost numbers. I need to know whether the source data is region-pinned today.

## Pricing: recommendation on "free in all three tiers"

**Don't commit publicly to unconditional free yet.** Gate on measured numbers first.

The skill's finding: every vendor studied gates bulk export (Stripe by subscription, Braze by enterprise contract, HubSpot by top tier). There is no free-tier precedent. Your two competitors charging fits that pattern. Leadership would be breaking precedent deliberately. The skill requires that to be an argued, recorded decision.

Leadership's differentiation argument is real. The margin argument against it is weaker than the skill implies, because variable cost may be small for people data. The stronger arguments against are:
- Free cannot be clawed back later.
- The fixed regional floor is a step cost.
- Tail customers are uncapped.

Options, ranked:

1. **Recommended: bundle in all tiers with guardrails.**
   - Fixed cadence, daily on lower tiers. A faster cadence is a paid or top-tier upgrade, because cadence is the cost driver.
   - Three supported regions only: us-east-1, eu-central-1, ap-southeast-2.
   - Other regions are a paid add-on at cost-plus.
   - Fair-use clause with a data-volume cap.
   - Reader accounts excluded.
   - Review at 90 days.
2. **Skill default: gate to the top tier, add-on for the rest.** Safest on margin. Gives up leadership's differentiator against competitors.
3. **Not recommended: unconditional free, any region, any cadence.** This is the skill's "free-tier giveaway" failure mode.

**Go/no-go test for option 1:** p90 modelled cost per cross-region customer-month must stay under 2% of the lowest tier's gross margin per customer. The 2% is self-set, not an industry figure. If it fails, gate cross-region to the top tier and keep same-region free.

Publish the freshness posture as **fixed cadence** (the Stripe pattern), not best-effort or SLA. A free feature with an SLA would be a penalty-backed promise on no revenue.

## Measurement gates

1. **Cost allocation named:** the table above covers it, including the cross-region case. ✅ Passes once Finance accepts it.
2. **Residency coverage:** ⚠️ open until the primary-region question is answered.
3. **Premium gating:** ✅ passes only if leadership's decision to break precedent is written down and argued, as above.
4. **After launch, track:** egress and replication cost per recipient per month, split by region.

## Next action

Run these in Snowflake (about 15 minutes) for the real baseline:
- `SNOWFLAKE.ACCOUNT_USAGE.DATA_TRANSFER_HISTORY` and `REPLICATION_USAGE_HISTORY`, if any replication already runs.
- Per-tenant row counts and bytes, to get p50 and p90 `D`.

Send me those two numbers and the answer on EU primary region. I'll replace the illustrative example with a real per-customer figure for Finance.