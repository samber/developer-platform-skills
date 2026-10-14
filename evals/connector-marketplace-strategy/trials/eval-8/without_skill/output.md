**Do not build the marketplace now.** Close the 40-integration gap with a triage, a purchased connector layer, and a documented API. Revisit the marketplace on the reopen conditions at the end.

I did not see your CRM, API usage, or RFP data. Every number below is a default to argue with, not a benchmark.

## Why not a marketplace

1. **The math is wrong for it.** 40 integrations at 5 per year is 8 years of backlog, and the list grows as you build. The gap is too little capacity, not too few builders.
2. **Your builders will not show up.** Salesforce, HubSpot, Zendesk, Intercom, Stripe, and NetSuite will not build on your platform. That leaves agencies, ISVs, and customer internal teams. None of them has a business case yet, because you have no counted demand from them.
3. **The cost lands on your two engineers.** A developer program, partner tiers, security review, support, and a revenue share all need a standing team. Those same two engineers are your integration capacity today.
4. **Revenue share fits poorly.** Integrations here are a cost of sale, a checkbox that wins deals. Nobody pays per integration, so there is no revenue to share. A take-rate before liquidity also eats the partner's surplus.
5. **Tiers add process, not supply.** Two tiers is the most any ecosystem needs. At your scale zero is right.

## What to do instead

1. **Triage the 40 (about 1 day).** Pull from the CRM, per integration: RFPs mentioning it, deals won and lost, and ACV. Sort into three buckets:
   - **Must exist at signature.** Build or buy these.
   - **"Available via API or partner" is acceptable.** Ship docs only.
   - **Never decisive.** Drop them.
   Expect the top 8 to 12 to carry most of the value.
2. **Publish a documented API and webhooks, if you lack them.** This is the cheapest rung. It lets customers' internal teams and agencies build today, with no marketplace. Count who actually does.
3. **Buy the long tail.** Evaluate an embedded iPaaS or unified-API vendor (Workato, Tray, Paragon, Merge, Nango, and similar). CRM, ticketing, and billing categories are what these cover best.
   - Get quotes first. I have no price data.
   - Compare the annual cost against two engineers' fully loaded cost.
   - Ask about white-label, per-customer connection fees, and data residency.
4. **Spend your two engineers only on the top bucket.** These are the integrations RFP reviewers inspect, where depth matters more than a bought connector offers. Keep to about 5 a year.
5. **Seed partner-built supply by hand.** Ask 2 or 3 agencies already serving your customers to build one connector each. Offer referral flow and a listing page. Charge them nothing.

## Payout cadence and merchant of record

**Today, set up neither. No money flows through you.**
- Partners and agencies bill their own customers. Statlas is not the merchant of record.
- Listing is free.

**If you later pay referral fees to agencies:**
- **Cadence:** quarterly, in arrears, net-45 after quarter-end.
- **Condition:** pay only on cash you have collected, with a clawback for refunds or churn inside 90 days.
- **Minimum:** a payout threshold, for example $250, with the balance carried forward.
- **Rails:** Stripe Connect, Tipalti, or similar, with KYC and tax forms handled by the rail.
- **Reason:** quarterly in arrears matches your invoice collection and keeps reconciliation to four runs a year.

**If you later sell paid third-party apps through Statlas:**
- **Merchant of record:** use a third-party MoR or a Stripe Connect model where the platform is the seller of record. Avoid raw Statlas MoR in-house: VAT and sales tax, refunds, chargebacks, and 1099 or equivalent reporting become your job.
- **Cadence:** monthly, net-30 after month-end, with a clawback window.
- **Take-rate:** zero until a market exists. Then set it so the partner's net still beats their alternative.

Both later setups need your finance lead and tax counsel to sign off before you commit. I am not giving tax or legal advice.

## Reopen conditions for the marketplace

Reopen when all of these hold:
- Three or more external parties have shipped on your API unprompted.
- Ten or more inbound third-party build requests have come in over two quarters.
- Customers with at least one active third-party complement retain or expand measurably better than those without.
- A platform team of three or more is funded indefinitely, with a named security reviewer.

## Kill criteria for this plan

- If the top-bucket integrations do not move RFP win rate within two quarters, stop adding integrations and re-examine the buying criteria.
- If the bought connector layer costs more than 1.5 engineers' loaded cost, or fails a hands-on test of your top 5, drop it and build in-house.
- If no external party ships on the API in 12 months, the ecosystem has no demand. Stop investing in it.

**Next, in under 2 minutes:** export the 40 integrations from the CRM with RFP count and deal value per integration, then sort descending.