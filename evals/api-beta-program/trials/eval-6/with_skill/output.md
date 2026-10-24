# Quayfield /v1beta: correct sequence

**Do not post "/v1beta is now GA" on Tuesday. Do not delete the two dead endpoints the same day.** Both steps skip the work that makes them safe. The skill (`api-beta-program`) calls this case an existing-beta rescue, with six undefined betas, production callers and no owner. Tuesday is 2026-10-27, and you can still ship something useful that day (see step 5).

## Why the CTO plan fails

- **GA by relabel promises things nobody reviewed.** GA means GA deprecation windows and enterprise buyers' expectations. No design review has run on these shapes. Any Must-change finding after the relabel costs a new version and a migration for ~30 customers.
- **"Let the versioning policy take it from there" is the wrong handoff.** `api-versioning-policy` owns the stable lifecycle. The beta program hands over at GA, after a decision per surface, not before.
- **"No calls in 90 days" is a belief, not proof of no users.** Freight has seasonal, quarterly and annual jobs. 90 days can miss them. A silent 404 breaks integrations you never knew about.
- **Pacific Crate is ~40% of /v1beta calls.** If they learn about a path change or a removal from a public changelog, you lose the relationship and the revenue concentration risk becomes an incident. Production callers hear first and privately.
- **No terms exist, so customers hold you to what you never wrote.** Any "all services" SLA or DPA clause in enterprise contracts may already apply by default. Legal must look before you write anything.

## Sequence

**Step 1. This week: name an owner.** Name one person and a backup. A beta with no owner is a perpetual beta. Nothing else starts until this is done.

**Step 2. Freeze and grandfather (immediately, no announcement needed).**
- Nothing that production callers use on any of the six endpoints changes until that endpoint has a decision.
- Do not delete, rename or reshape anything yet.

**Step 3. Inventory the six endpoints (about 1 to 2 days).**

| Surface | First shipped | Last shape change | Callers (90 days) | Accounts with production traffic | Owner | Decision | Date |
|---|---|---|---|---|---|---|---|
| A to D (live) | from git/changelog | from git | from logs | live keys, sustained volume | name | pending | |
| E, F (zero calls) | from git | from git | 0 | none seen | name | pending | |

- For E and F, extend the log window to 12 months or the full retention you have.
- Also check for callers logs miss: SDK usage, docs hits, partner or platform integrations, sandbox or test-key traffic, other regions or gateways.
- For A to D, list every account per endpoint, not only the top caller.

**Step 4. Publish a retroactive stage contract (about 1 week with legal).**
- The docs word "beta" is an undefined label. Retire it. Do not adopt it as a stage.
- Fill every row of the stage contract for the stage these endpoints sit in: access, availability/SLA, support, breaking changes, removal, production use, pricing, data and compliance, limits, marking, discontinuation. An empty row is a promise you will be held to anyway.
- Data and compliance: freight tracking carries shipment and consignee data, which can be personal data. Counsel must check what the ~30 customers' MSA/DPA already promise and write the precedence clause. Terms written now cannot strip rights customers already hold.
- Production use: the ~30 callers run production today. Grant them a production exception by default and record it per account, since you tolerated that use.
- Pricing: say whether the endpoints are free or billed, and when GA pricing is announced.

**Step 5. Decide per surface (about 2 to 3 weeks; each with an owner and a date).**

| Surface | Test | Outcome |
|---|---|---|
| A to D (live) | Run `public-api-design-review` at GA level. Shape stable for a long time, production callers exist, **zero Must-change findings** | **GA as-is**: relabel, hand to `api-versioning-policy` |
| A to D, if any Must-change | Findings need breaking fixes | **Next version with migration**: run the beta program steps for the new version |
| E, F (zero use) | Zero callers confirmed over the long window, no hidden callers | **Kill**, with a notice (see step 7) |

Expect mixed outcomes. Four endpoints shipped across 2022 to 2023 by an ownerless team will rarely all pass.

**Step 6. Tell production callers privately before any public post.**
- Order: Pacific Crate first (a call from the owner, not an email), then the other ~30 accounts, then the public changelog.
- Say what changes, per account, for the operations that account calls.
- Ask Pacific Crate whether they resell or embed the API. If they do, their downstream accounts need a notice path through them.

**Step 7. Execute.**
- **GA surfaces:**
  - Publish the GA path or version and the migration, or a relabel notice if the shape does not change.
  - Keep the `/v1beta` path working through an overlap window. Production callers exist, so use the GA deprecation window from `api-versioning-policy`, not a short one.
  - Then hand the surface over. Do not drop the beta path early.
- **Dead endpoints E and F:**
  - Announce the removal with a date. Send `Deprecation`/`Sunset`-style headers and a docs banner on the pages.
  - Serve a clear error pointing to the notice, never a silent 404. Watch for any caller appearing.
  - Remove only on the date, if the logs still show no callers. If a caller appears, they become a production caller and get the full kill terms: months of notice, data export, named alternative.
  - The skill sets the rule "months, not weeks, once anyone runs production on it". For zero confirmed callers it gives no number. A 30 to 90 day window is my judgment, not the skill's. Ask legal.

**Step 8. Retire the old label publicly** once every surface has a decision.

## What to ship Tuesday instead

A changelog entry that says what is true:

> **State of /v1beta (2026-10-27).** All six /v1beta endpoints are under review. Nothing you call today changes while the review runs. Terms for pre-GA endpoints are published here: *(link to the stage contract)*. Each endpoint gets a decision by *(date)*: GA, new version with migration, or removal. Two endpoints with no recorded use are proposed for removal on *(date)*; if you call them, tell us at *(channel)*. Named owner: *(name)*.

Publish only after Pacific Crate and the other production accounts hear from you privately. If steps 1 to 4 are not ready by Tuesday, post later. A late honest entry costs less than a wrong GA.

## Risks to flag to the CTO

- A GA relabel is hard to undo. A review finding after the relabel means a breaking change on a GA surface.
- A deletion based on 90 days of logs is irreversible. Customers see it as breakage.
- Concentration: 40% of traffic from one account is above the roughly one-third guideline. Pacific Crate's needs may have shaped the endpoints. The design review should check that the shapes fit the other ~29 accounts too.
- The skill's measurements to track from now: silent breaking changes (target zero), migration completion at GA (100%), and time in stage against the exit date.

## Open questions I could not answer from your message

1. Who owns this in practice, by name?
2. Do any enterprise contracts promise SLA or DPA coverage on "all services"? Does /v1beta carry personal data?
3. Does Pacific Crate resell or embed the API for their own customers?
4. How do versions surface today (path, header, date), and do SDKs cover /v1beta endpoints?
5. Is there a GA target date from sales or the CTO beyond "Tuesday"?

**Next action (under 2 minutes):** name the owner and backup for /v1beta, then start the step 3 inventory with a log query over the full retention for endpoints E and F.