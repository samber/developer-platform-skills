**Next action:** stop calling these one thing. Replace "the connector strategy" in the board deck with three line items (below). Time: about 10 minutes to edit the slide.

# Corvid: three asks, three different bets

## Verdict

The three asks have different buyers, owners, risks and reversibility. A single roadmap line would hide all of that.

| | A. Parquet to customer S3 | B. Tableau live query | C. Partner connectors in app directory |
|---|---|---|---|
| What it is | Data **delivery** (push) | Data **access** (pull, live) | Integration **ecosystem** (partners build) |
| Who asks | 2 customer data teams | 1 prospect analyst | 2 integration partners |
| Counted demand | 2 named customers | 1 prospect, not a customer | 2 supply-side asks, unknown demand-side |
| Who builds | Corvid | Corvid (or nobody yet) | Partners |
| Decision | **Build, productized** | **Defer, give a cheap answer now** | **Proceed narrow, gated** |
| Reversibility | Medium: a published schema is a contract | Low if you open a query endpoint | Lowest: partner revenue rides on you |

Only A has demand you can name. B has one data point from someone who hasn't bought. C has supply but unproven pull.

## A. Nightly Parquet export: build it as a product

Do not build two bespoke pipelines. Build one export feature that two customers happen to use first.

1. **Scope v1:**
   - Fixed, versioned Parquet schemas for a small set of tables (shipments, events/milestones, locations).
   - Daily partitioned by date, with a manifest file per run.
   - Incremental plus a documented late-arriving-update rule. Logistics data gets corrected after the fact.
2. **Delivery:**
   - The customer creates a write-only IAM role in their account.
   - Corvid assumes it with a per-customer external ID.
   - Never hold long-lived customer keys.
3. **Contract:** publish the schema and a deprecation policy (default: 90 days' notice, additive changes only inside a major version). The schema is the real commitment. The files are not.
4. **Gate before building:** confirm Corvid has the right to re-export every field. Shipment data often carries carrier, shipper and consignee data from other parties. Check customer contracts and your data terms first. If rights are unclear, scope v1 to the customer's own shipments only.
5. **Effort guess (verify with engineering):** about 4 to 6 engineer-weeks for one team, plus a small standing cost: monitoring, failed-delivery alerts, schema versioning.

Pass condition: both customers consume the files in production within 60 days of go-live.

## B. Tableau live query: defer, answer cheaply

Live query is the most expensive request here. It means:
- A query surface that must isolate tenants.
- Cost and performance control, since one analyst's dashboard can hammer the system.
- A support burden for dashboards you didn't write.

Evidence is one prospect. That is a logo, not demand.

1. **Answer for the analyst now:** "We deliver Parquet to your S3 nightly. Tableau reads it through Athena or your warehouse." No build needed, and it uses A.
2. **Ask the analyst:** how fresh must the data be? Nightly may be enough. If they truly need minutes-fresh data, that is a different, bigger product.
3. **Reopen condition:** at least 3 customers or qualified prospects independently ask for live query, and the answer is still "nightly is too stale". Then compare the options: a warehouse-share model (for example Delta Sharing or a Snowflake share), a read-only SQL endpoint, or a Tableau-specific connector.
4. **Do not promise live query** to the prospect or in the deck.

## C. Partner connectors in the app directory: proceed narrow

This is the ecosystem bet. It is the only item where outsiders do the engineering and the only item that creates obligations to third parties.

**Hypothesis:** because joint customers need data flowing between Corvid and *[partner category]* and we won't build both connectors, the two partners will build on our public API and listing, earning *[their return, to be confirmed]*, which makes Corvid stickier to *[buyer]* by *[mechanism, to be confirmed]*. Four blanks are unfilled. Fill them before committing.

1. **Count demand first (about 1 week):** list the last 5 integration requests with customers attached, and how many joint customers each partner has. If fewer than 5 are real, run it as a pilot, not a program.
2. **Ask each partner:** "If we don't do this, what changes for you?" A lost certification or a deal at risk is a reason to build. "Nothing really" means a logo, not a complementor.
3. **Check readiness:** does the app directory run on a documented, versioned public API that Corvid's own integrations also use? If partners need a private path, stop and fix that first.
4. **Terms:** zero take-rate and no revenue share until there is a market worth taxing. The listing is free. Corvid owns review, security and an escalation path.
5. **Seed:** build or co-build the first connector with one partner, so the pattern exists. Route your own sales and onboarding conversations at the listing.

**Obligations you sign (assign an owner to each before launch):**
- Deprecation policy for the API partners use (same 90-day default).
- Security review and revocation for each listing.
- Support path when a partner bug looks like a Corvid outage.
- Roadmap line: which connectors Corvid will never build itself, and notice before that changes.
- Wind-down terms: notice, data export, written now.

## How the three connect

- A's published schema is the base for C. Partners and Tableau users read the same data model. Design it once.
- B depends on A today and may get its own product later.
- Sequence: A first, C's demand count in parallel, B parked.

## Timeline (today is 2026-10-08)

| When | What | Owner |
|---|---|---|
| By 10-15 | Data-rights check on A; reply to Tableau prospect; fill C's four blanks | Product + Legal |
| By 10-22 | A scope and schema draft agreed with both customers | Engineering lead |
| By 10-31 | C go/no-go on counted demand and partner answers | Head of partnerships |
| Mid-Dec (default, adjust to capacity) | A live for both customers | Engineering |

These dates are defaults I set. Replace them with your real capacity.

## Metrics

Targets are my defaults, not industry benchmarks. Replace them with your own baselines.

- A: customers consuming successfully (target 2 of 2 within 60 days); failed-delivery rate; schema-change incidents (target 0 breaking in the first year).
- B: number of independent live-query requests logged (reopen at 3).
- C: connectors live; joint customers with at least one active connector; share of usage on the top partner (high means one partnership, not an ecosystem).

## Kill and stop criteria

- **A:** a customer isn't consuming 90 days after go-live. Investigate before building a third export.
- **C:** fewer than 2 active joint customers per connector 6 months after listing, or a partner stops maintaining their connector. De-list under the written wind-down terms.
- **C:** support tickets from third-party code exceed what one named person can carry. Pause new listings.

## Suggested board-deck wording

"Data strategy has three tracks: (1) **Data delivery:** productized nightly exports, launching Q4 for two customers. (2) **Live analytics access:** under evaluation, gated on demand. (3) **Partner integrations:** pilot with two partners, gated on customer demand."

## Open questions (answers could change the verdict)

1. Does Corvid have contractual rights to re-export carrier and consignee data? **Biggest risk to A.**
2. Do you already have a stable public API that your app directory uses?
3. How many joint customers does each partner share with Corvid?
4. Is there a security review function for partner listings, and who runs it?
5. What does the Tableau analyst's company pay or plan to pay? That decides whether B is a sales exception or a roadmap item.

I didn't have your numbers, so every effort and date above is an assumption to check.

**Next:** answer question 1 (data rights), which gates the whole of A. Send the data terms to Legal today.