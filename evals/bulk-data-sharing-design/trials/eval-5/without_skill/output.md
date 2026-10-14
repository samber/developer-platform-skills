# Cost and pricing: native Snowflake share

## Answer for Finance

Yes, it costs something per customer, but only for customers outside our region, and probably not much.

- **Same-region customers (us-east-1):** about $0 marginal cost to us. They query the share with their own compute. Nothing is copied.
- **eu-central-1 (~40%) and ap-southeast-2 (~15%):** Snowflake can't share across regions directly. We must replicate the data into a Snowflake account in each target region and share from there. We pay for that replica.
- **The other ~45%:** we haven't established that they all sit in us-east-1. Any account in another region (for example us-west-2) costs the same as the two named regions. This is the first thing to confirm.

I don't have your data volumes or your contract rates. The numbers below are a model with assumed inputs, not a quote. A measurement spike (below) replaces the assumptions with real figures.

## What we pay for

Direct shares only work inside one cloud and one region. Everything below follows from that.

| # | Cost | Driver | Scales with |
|---|------|--------|-------------|
| 1 | Replica storage in each target region | Bytes stored, plus Time Travel and Fail-safe on the replica | Customer data volume |
| 2 | Cross-region data transfer | Bytes of changed micro-partitions per refresh | Data volume × change rate |
| 3 | Replication compute (serverless credits) | Each refresh, plus a per-refresh overhead | Refresh cadence and bytes changed |
| 4 | Reader accounts (only if a customer has no Snowflake account) | Their query compute, billed to us | Their usage, uncapped |

What we do not pay for:

- Consumer query compute. The customer pays it.
- Consumer storage of shared data. There is none.
- Any consumer-side egress for same-region shares.

### Cost-structure points that matter

- **Cost is per region, not per customer, at the fixed layer.** Each region needs one replication pipeline and one receiving account. That cost is paid once, as soon as the region has a customer. Variable cost is per byte after that.
- **Full reloads multiply transfer cost.** Replication ships changed micro-partitions. A truncate-and-reload pipeline for HR tables rewrites every partition, so the whole table crosses regions on every refresh. Merge or incremental loads keep transfer near the true change rate. This is the largest risk factor in the model.
- **Refresh cadence is a cost knob.** Hourly refresh costs far more than daily. It also drives how fresh the customer's data feels.
- **Time Travel and Fail-safe apply to replicas.** Set retention on replicas to the minimum, 1 day. Storage is otherwise inflated.
- **Churned customers leave replicas behind.** We need a decommission step that drops the share and the per-customer data from the regional replica.
- **Reader accounts are the one uncapped cost.** The launch scope should be "customer has a Snowflake account". Reader accounts should be excluded or priced separately.

## Cost model

Per customer, per month, in a replicated region:

```
cost = (GB_stored × storage_rate)
     + (GB_changed_per_month × transfer_rate)
     + replication_compute(GB_changed, refreshes)
```

Region fixed cost: `refresh_overhead × refreshes_per_month`, shared across all customers in that region.

Blended cost per customer across the base: `replicated_fraction (~0.55 or higher) × cost above`.

### Illustrative sensitivity

Assumptions, all to be replaced with real values:

- Storage at $25/TB-month.
- Transfer at $20/TB. This is the Snowflake same-cloud inter-region rate as I recall it. Verify it against our rate card, especially for ap-southeast-2.
- Replication compute guessed equal to transfer cost.
- Customer data of 10 GB, and again at 100 GB.

| Scenario | 10 GB customer | 100 GB customer |
|----------|----------------|-----------------|
| Incremental loads, ~10% monthly change | ~$0.30/mo | ~$3/mo |
| Heavy churn, ~100% monthly change | ~$0.80/mo | ~$8/mo |
| Daily full reload (worst realistic case) | ~$12/mo | ~$120/mo |

How to read the table:

- With incremental loads, cost is negligible next to any paid tier.
- Pipeline design moves cost by about 40×. A customer's size matters less than whether we full-reload.
- At a 100 GB customer with daily full reload, cost could matter on the lowest tier.

## Measurement spike (before pricing is final)

Run for two weeks in one EU region, with 3 to 5 real customers of different sizes:

1. Replicate to a test account in eu-central-1.
2. Record actual cost from `REPLICATION_GROUP_USAGE_HISTORY` and `DATABASE_REPLICATION_USAGE_HISTORY` (replication credits and bytes) and `DATA_TRANSFER_HISTORY` (transfer bytes). Both are in `ACCOUNT_USAGE`.
3. Record replica storage from `TABLE_STORAGE_METRICS`.
4. Tag or isolate databases per customer so cost is attributable.
5. Repeat the test once with a full-reload table to confirm the multiplier.
6. Get our real transfer rates for eu-central-1 and ap-southeast-2 from the Snowflake contract.

Output: measured $/customer/month by size band, and fixed $/region/month.

## Pricing recommendation

**Bundle free in all three tiers, with fair-use limits and a cost-metering trigger. Do not charge by region.**

Reasoning:

- Modeled cost is small relative to a paid subscription when loads are incremental. Competitors charging for the share is a differentiator we can afford to give away.
- Charging EU and APAC customers more punishes the customers who are already the most expensive to serve. They are the ones most likely to compare us with a competitor.
- An uncapped "free" feature has a tail risk. The tail comes from large customers, full reloads and reader accounts.

### Proposed terms

- Include the share up to a fair-use limit per tier. Examples to set with Finance: data volume per customer, and a minimum refresh interval such as 1 hour on the top tier and 24 hours on the lowest.
- Exclude reader accounts from the bundle. Offer them as a paid add-on or not at all at launch.
- Above the limits, offer a paid add-on priced at cost plus margin.
- Keep the bundle decision reversible for new customers. Grandfather existing customers if terms change.

### Guardrail

Alert when attributable share cost for any customer exceeds a set percentage of that customer's subscription revenue. I suggest starting at 2%, to be agreed with Finance. Review the rule after the first quarter of real data.

## Compliance flag (non-cost, but it gates design)

This is HR data, so it is personal data.

- **Do not replicate everyone's data everywhere.** Each regional replica should hold only the customers who need it. A multi-tenant replica copies US customers' employee data into the EU and Sydney for no reason.
- **The primary stays in us-east-1.** An EU replica does not make the data EU-resident. If any EU customer's contract or DPA promises EU residency, the share doesn't change that. Check with Legal.
- **Erasure must reach replicas.** A GDPR deletion in the primary reaches the replica only at the next refresh, and Time Travel retention extends the window. Document the delay.

## Open questions

1. Where do the other ~45% of customers' accounts sit? Are any outside us-east-1, or not on AWS?
2. How is the HR data loaded today, incrementally or by full reload? How big is the median and largest customer?
3. Do any customers lack a Snowflake account (the reader-account question)?
4. What refresh freshness do customers expect?
5. What are our actual Snowflake transfer and credit rates?
6. What gross-margin floor does Finance want per tier?

## Decisions needed

1. Approve the two-week measurement spike.
2. Choose fair-use limits and refresh cadence per tier once real numbers exist.
3. Decide reader-account scope at launch.
4. Confirm with Legal the residency promises and the erasure window.