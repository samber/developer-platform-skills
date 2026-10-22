Run this before you commit headcount: count what the 600 customers use. It takes about 2 weeks and costs less than one connector. ⏳

## Biggest hole

You have no demand evidence for the plan. The six-platform list comes from market share, not from your customers. "Biggest ELT platform" and "platform our customers run" can differ a lot. Kestrel sells compliance software, so many customers may have no ELT stack at all, or may run something niche, or something home-built.

Your own one-sentence hypothesis is also missing blanks. It has no named complement, no named builder, and no named buyer.

## Holes, ranked

1. **Stalled-deal claim is unverified.** You don't know that connectors stall deals. Compliance deals more often stall on security review, SOC 2, residency, or procurement. Pull lost and stalled deals from CRM and count how many cite an integration. If it's under about 5 deals, the premise is weak.
2. **You picked the lowest-leverage option.** Vendor-built connectors mean you build and maintain every one forever. Each ELT vendor changes its SDK on its own schedule. 2 FTE × 4 quarters is 8 FTE-quarters. Six connectors plus on-call, upgrades, and support will eat the team by year two. Nothing compounds.
3. **There is a cheaper path that covers all six at once.** First check whether your API can feed an ELT tool already.
   - Does it have stable pagination and incremental cursors?
   - Does it expose deletes?
   - Can it do a bulk export to S3 or a warehouse share?
   - Most ELT tools ingest from a generic REST source or from files. Several have low-code connector builders, which take days.

   If your API is weak, six connectors will just wrap that weakness six times. Fix the API first.
4. **Vendor gatekeeping is a dependency you don't control.** Partner programs have their own review queues, listing rules, and timelines. A vendor may also build a connector for you if enough of their customers ask. Check each vendor's partner terms before you plan dates. I did not verify those terms here.
5. **Wrong buyer risk.** Compliance buyers are not data engineers. The person who needs a connector is a data team member who may not control the purchase. You need to know whether that person blocks deals or only complains after the sale.

## Smaller holes

- **No success metric or kill rule.** Pick a number and a date. Example: "by Q2, 40% of accounts that asked for a connector have it live, or we stop."
- **"Cover the data ecosystem" is wider than connectors.** It could also mean warehouses, BI tools, dbt packages, reverse ETL, or a better API. You spent the whole budget on one answer before researching.
- **Security and data-handling cost.** Compliance data (evidence, audit logs, PII) leaves your boundary through a third-party pipe. Expect questions on residency, per-tenant permissions, and who sees credentials. This adds review work to every connector.
- **Ownership.** Name who is on call when a connector breaks at a customer.

## Do this in 2 weeks

1. **Mine existing data (2–3 days).**
   - CRM lost and stalled deals that cite integrations.
   - Support tickets and sales call notes that mention Fivetran, Airbyte, dbt, Snowflake, or similar.
   - Your API logs: user agents and IPs of customers already pulling data. Existing scripts are the best demand signal.
2. **Ask the customers (1 week, in parallel).** Send one question to all 600, and call your top 20 by revenue.
   - "How do you move our data into your warehouse today?"
   - Offer these options: ELT tool (which?), custom script, CSV export, none.
3. **Check your API against ELT needs (1 day).** Look at pagination, incremental sync, deletes, rate limits, bulk export.
4. **Rank the results.** Keep any platform that at least 15% of accounts use, or that blocked a named deal. Drop the rest.
5. **Write the plan with a kill rule.** Choose between a documented API plus a bulk export, one or two connectors, or a partner-built route. Add a metric and a date.

## Likely outcome

I expect the data to say something like: 2–3 platforms matter, some demand is already served by scripts against your API, and the first FTE-quarter belongs on API and export quality. That's a guess until you have the counts. It would still leave most of the 8 FTE-quarters unspent for the other ecosystem work.

**Next action:** query CRM for lost and stalled deals that mention "integration" or "connector", and paste me the count.