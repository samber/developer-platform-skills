# Connector strategy: Northwind Fleet as an ETL/ELT source

**Status: build not approved yet.** The demand gate (step 1) fails today. The plan below gets you evidence fast, then spends November on work that pays off whatever the evidence says.

I followed the skill's workflow in order. The skill wants a one-question-at-a-time interview and section-by-section sign-off. I couldn't do that here, so the assumptions are flagged and the questions you need to answer are at the end.

## 1. Demand evidence

| Driver | Evidence today | Verdict |
|---|---|---|
| Support tickets naming a platform | None logged (your read) | ❌ |
| Lost deals or churn citing data-stack mismatch | Nothing in renewals this year | ❌ |
| Customers hand-rolling pipelines | Not checked | ⏳ unknown |
| Procurement or security questionnaires asking about warehouse sync | Not checked | ⏳ unknown |
| Competitor is in a major catalog | Yes, one observation | ℹ️ a signal, not evidence |

- **Interview answer 1 is (d), an internal hypothesis only.** The skill says to approve no build on hypothesis.
- **"Competitor is listed" is the competitive-table-stakes driver.** It needs a verifiable artifact. Without one, the board slide would rest on a feeling.
- **Your customer base makes weak demand plausible.** 320 mid-market logistics customers often have no data team, and only customers with a warehouse extract anything. Zero tickets and zero renewal mentions fits that profile.
- **Check one thing before assuming no demand.** Telematics customers may be pulling data through the raw API or CSV exports. That demand would never show up as a ticket naming a platform.

**Reopen signal (the skill's threshold):** three tickets naming a platform within a quarter, or one lost deal citing the gap. Add one more qualifying artifact: sustained paginated API scans from a customer service account.

### Validation sprint (2 weeks, Oct 12-23)

Each task should produce a named artifact, or a documented "none found".

1. **Sales:** ask the VP Sales for the names of deals where a data-stack or integration gap came up. Their trigger was a competitor sighting, so ask whether a prospect said anything. Get deal names and dates.
2. **Support and CRM:** search tickets, call notes and CS notes, including closed ones, for platform names, "warehouse", "BI", "export", "data lake" and "API pull". Include renewal notes, since "nothing came up" often means nobody searched.
3. **API logs:** look for high-frequency paginated scans from single service accounts, and count customers. This is the strongest hidden-demand signal.
4. **Security and procurement questionnaires:** grep this year's for warehouse or ETL sync questions.
5. **Top accounts:** ask CSMs to put one question to your top ~20 logistics accounts: "Do you pull our data into a warehouse or BI tool? With what?" This also answers the stack question (interview answer 2).
6. **Catalog check:** confirm which catalog the competitor is in and which connector tier they're on (managed, SDK/community, or marketplace). A community listing carries very different weight than a platform-managed one.

**Gate on Oct 26:** attach the artifacts, or write "no demand found" and stop. Don't build.

## 2. Platform selection

- **Not selectable yet (answer 2 is "unknown").** The skill says to suspend platform choice until the stack finding lands. Sprint tasks 3 and 5 produce it.
- **The competitor's catalog is not the selection criterion.** Build where your customers' data teams run, one platform first.
- **Reference snapshot (2026-08-30; re-verify before committing).** Use it to set expectations:
  - **Fivetran** (curated): Partner-Built is closed to new sources. By Request is open. The Connector SDK is open.
  - **Airbyte** (open contribution): listing is a low bar, and Certified is the differentiator.
  - **Singer/Meltano** (open spec): no gate, no floor.

## 3. Build-path menu

I re-ranked the default menu against answers 5-7 (all inferred):
- **Deadline (answer 5):** the Q4 board. It's soft, because you're optimizing a slide, not unblocking a deal. That promotes the platform-managed queue only mildly.
- **Compounding or one-off (answer 6):** unknown. Your VP frames it as parity, so it reads as a checkbox.
- **Effort ceiling (answer 7):** engineering exists in November, but nobody is named for month 13. That demotes everything except the queue and "not yet".

| | A. Validate first, then queue (recommended) | B. Vendor-SDK connector in November | C. Custom open-spec tap |
|---|---|---|---|
| What | Sprint, then submit to the platform-managed program if the gate passes | Your engineers write and maintain a connector on the platform SDK | Bespoke tap or pipeline |
| Time to presence | Review gate of 2-8 weeks, then ~30 days. Listing likely lands after the board. | November build, then a listing. Fastest to a live badge, if you build. | Fast, no gate |
| Who owns the tax | Platform | Split: platform hosts, you fix | 100% you |
| Control | Lowest | High | Highest |
| Risk | Can reject the source. A dense time-series schema may be steered to the SDK. | Pays 15-30% a year on a connector with zero measured demand | Decay failure mode |

**Recommendation: A.**
- **Evidence:** zero demand evidence makes B and C a build on hypothesis. B's only advantage is shipping before the board, and that's not a business reason.
- **Fix the board slide, not the catalog:** a decision with evidence reads better than a listing nobody uses.
- **Fallback if the VP insists on a visible artifact:** submit to the managed queue, or file the platform's request, the same day the gate passes. A submitted request is a real milestone you can show.

**What you can show the board by Q4 (adjust to the real date):**
- Competitor-catalog audit.
- Demand sprint results.
- Decision (go/no-go) with named evidence.
- A queue submission date, if go.

Don't promise a live listing by the board. The review gate alone is weeks, and a rejection is possible.

I need an explicit pick from you before the plan locks. See the questions at the end.

## 4. Extraction-readiness audit (the November work)

This is the no-regret investment. It cuts cost on every path and for every customer hand-rolling a pipeline. Engineering's November capacity goes here regardless of the sprint result.

Grade each resource you'd expose (vehicles, trips, drivers, events/positions, alerts, maintenance, geofences) pass/fail on the nine checks. A resource that can't pass gets an explicit exclusion note, never a silent skip.

1. Cursor-based pagination, not offset.
2. A cursor or `updated_at` that's guaranteed stable across syncs.
3. An overlap and reconciliation story (re-query a small window, upsert by stable key, periodic full reconcile).
4. A bulk or incremental export endpoint, separate from the UI CRUD endpoints.
5. Webhooks as a freshness supplement, never a backfill.
6. 429 with `Retry-After` (and 304 where feasible).
7. **An explicit delete/change signal.** This is the most common gap.
8. A per-resource extraction contract: strategy, expected volume, whether hard deletes matter, freshness.
9. Versioning discipline: additive changes, published sunset dates.

**Telematics-specific flag (my inference, not from your data):** position and event streams are high-volume time series. Paginated REST backfill on those is slow and rate-limit-prone. A bulk or async export is likely the right first fix, and it's the one most likely to matter for a platform's By Request fit.

**Fix sequence for November:**
1. Run the audit (week 1).
2. Fix the cursor stability and delete signal gaps (weeks 2-3).
3. Add the bulk export if it's missing (weeks 3-4).
4. Publish the extraction contract as docs.

If the sprint finds no demand, this is still a customer-facing API improvement.

## 5. CDC scoping: the language customers will see

Don't put "CDC support" on any page, slide or questionnaire answer. Log-based CDC reads a database's transaction log. A multi-tenant SaaS can't expose that to an external platform, so the honest ceiling is pseudo-CDC.

Approved wording:

> Northwind Fleet data syncs incrementally on a [N]-hour interval using record update timestamps. Changes made and overwritten within a single interval are not captured. Records deleted in Northwind Fleet are [not reflected / reflected via the deletions feed] in your warehouse. A periodic full refresh is recommended for reconciliation.

Rollout order:
1. Timestamp/cursor incremental polling.
2. Webhooks for freshness.
3. A deletion/change feed, shipped when customers report missed deletes (not a launch-day promise).
4. Periodic full re-import as a backstop.

## 6. Certification path

- **Listing and certification are different bars.** Passing the test suite gets you listed. Certification is optional and earned after real syncs hold.
- **Fivetran:** the Partner-Built badge is closed, so there's no source-vendor badge to chase.
- **Airbyte:** "Certified" is the differentiator. Partner Certified is destination-only.
- **Clock to plan for:** release phases are Private Preview → Beta → GA. Fivetran requires promotion to Beta within six months of entering Private Preview.
- **Cost:** no platform charges or pays for the badge. The cost is engineering time.
- **Behaviors to build in from day one:** integration tests for every sync mode, incremental wherever possible, and fast, actionable failures.
- **Adopt these SLOs even if not required:** ≥95% sync success, first response ≤3 business days, and an update at least every 6 months.

## 7. Maintenance plan

- **Budget:** 15-30% of build cost per year, up to 50% in high-change phases. Use the ratio, not the figures. The sources are vendor estimates ($10-50k for a moderate integration, $50-150k+ for an advanced one).
- **Worked example for the SDK path** (my illustration): a $30k build means roughly $4.5-9k a year. Replace with your real engineering cost.
- **Cost drivers to plan against:** authentication changes, schema drift, rate-limit shifts, compliance overhead.
- **Monitoring:** alert on sync failure and schema-drift errors. Don't wait for tickets. Marketplace-tier listings carry no platform SLA.
- **Owner:** **unassigned.** The skill treats a side-task owner as the documented decay path. Name a team and a standing budget before any build starts. If you can't, that's another reason for path A.
- **Business case:** support deflection and retention only. **No revenue line.** No ETL/ELT platform pays source vendors. Airbyte shipped flat bounties of $10-150, not revenue share.
- **Honest current baseline:** deflection is zero today because there are zero tickets. The case only exists if the sprint finds hidden demand.

## Timeline

| When | What | Gate |
|---|---|---|
| Oct 12-23 | Validation sprint (6 tasks above) | Artifacts attached |
| Oct 26 | Go/no-go decision meeting | Named evidence, or stop |
| Oct 27 | If go: submit to the platform queue. If no-go: record the reopen signal. | |
| Nov | Extraction-readiness audit and fixes (engineering) | Readiness gate |
| Dec | If submitted: respond to the platform's API-doc analysis. If SDK promoted: build starts after the owner is named. | Owner named |

Adjust to the real board date.

## Measurement gates

- **Demand gate:** no build approval without named evidence attached.
- **Honesty gates:** no revenue-share line in the case, and no "CDC" without the incremental/eventual-consistency scoping.
- **Readiness gate:** every resource in scope passes the checklist or carries an exclusion note.
- **After launch** (baseline from the first quarter):
  - Connector-attributed ticket deflection.
  - Sync success against the 95% bar.
  - Share of new customers connecting via the platform versus the raw API.

## Questions to answer before this locks

1. **Which catalog and tier is the competitor in?** (Managed, SDK/community, or marketplace; Fivetran, Airbyte, or other.)
2. **When exactly is the Q4 board meeting?** This decides whether "submitted" is shown or "decided".
3. **Strategy pick:** A (recommended), B or C?
4. **Who would own the connector in month 13?** A named team and budget, a side-task, or nobody yet?
5. **Does your API already expose a stable cursor, a bulk path and a delete signal?** If you don't know, the November audit answers it.
6. **Engineering weeks available in November, and sustainable hours per month afterwards?**

Once you answer question 3, I'll write up the chosen path section by section for sign-off.