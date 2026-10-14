**Next action (today, 10 min):** Ask the VP Sales two things. Which catalog is it? What is the board date? The timeline below depends on both.

## Recommendation

Don't commit November engineering yet. Spend 2 weeks proving demand, then decide on Oct 22.

You have no counted demand. Zero support requests and nothing in renewals is a real signal, but it is a weak one. Customers may ask sales or their CSM, or they may script around you. A competitor's listing proves the competitor wants the channel. It doesn't prove your 320 customers do.

The rung to pick is a **vendor-built connector** that you list yourselves. It is the only path where you control delivery.

The ecosystem hypothesis is: "Mid-market logistics data teams need Northwind data in their warehouse, we will build the connector, they get telematics next to TMS/ERP data, and that lowers churn and wins competitive deals." Every blank is unproven today.

## Plan

**1. Oct 8–22: demand check (about 8 hours total)**
1. Ask CSMs and AEs for named customers who requested a warehouse export, an ELT sync, or BI access. Include lost deals and "do you have a Snowflake/BigQuery connector" questions.
2. Query API logs for heavy bulk-pull keys and scheduled export jobs. These are unofficial glue and the best evidence.
3. Send a 3-question survey to the data/ops contact at your top 40 accounts. Ask whether they have a warehouse and an ELT tool, and whether they would use a Northwind connector.
4. Run 5 customer calls of 20 minutes each.
5. Ask the VP for the lost-deal list and check how many cite this.

**Gate, passing:** at least 5 named customers use a warehouse and an ELT tool and would sync Northwind, or at least 2 lost deals cite it. These are my defaults, not industry benchmarks. Change them if you have better data.

**2. Oct 8–22 (parallel): technical readiness, 2–3 eng days**
- Does the public API cover the objects the connector needs (vehicles, trips, events, drivers, DVIR)?
- Does it offer incremental sync (an `updated_at` cursor or equivalent), pagination, stable IDs and tolerable rate limits?
- If not, the API work is the real cost. That could eat November, so re-estimate before you promise anything.

**3. Oct 22: go / no-go**
- **Pass:** build in November.
- **Fail or unknown:** write a one-page decline memo with reopen conditions (for example, 5 requests logged). Give the board the data instead of a listing. A documented "no" stops the question coming back every two quarters.

**4. November (only on pass): build**
- 1–2 engineers, with a first connector covering the top 3–5 requested objects. I don't know your API, so I can't estimate the effort until step 2 finishes.
- Check the catalog's current build path and review terms before you start. I haven't verified them, and terms and review times change.
- Dogfood it by syncing your own account.

**5. December: submit, then list**
- Catalog review is on their schedule, not yours. A listing live before the board meeting is only plausible if the board is in December or later.
- If the board is earlier, the honest board line is "demand validated, connector built, in review". Ask for the date to confirm.

**6. Q1: seed**
- Hand-pick 5 customers from the demand list and onboard them personally.
- Add a docs page, a CSM talk track, and a one-line mention in your onboarding.

## Obligations you sign by listing
- Someone owns the connector forever. It breaks when your API changes or the catalog changes its rules.
- A support runbook for "my sync failed". That arrives as your ticket, not the catalog's.
- A deprecation policy for the API fields the connector depends on.
- Do this as an owner-and-quarter commitment, not a one-off.

## Measure
- Baseline today: 0 logged requests, 0 syncing accounts.
- Target, 90 days after listing: at least 5 accounts with an active sync (self-set default).
- Also track: retention of syncing accounts vs. non-syncing accounts, and deals where the connector was cited.

## Kill criteria
- Fewer than 3 active syncing accounts 90 days after listing: freeze to security fixes only and review delisting.
- Gate fails on Oct 22: stop, send the decline memo.

## Open questions (I need these)
1. Which catalog, and what is the Q4 board date?
2. Does your public API support incremental sync?
3. Does the VP have lost-deal evidence?