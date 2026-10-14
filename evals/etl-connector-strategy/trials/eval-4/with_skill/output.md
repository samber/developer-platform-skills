# Connector strategy: Veridian Labs, ELT source connector (draft for your approval)

**Next action, today:** ask the customer's data team which ELT tool they run and what "available" means in the contract. Everything below branches on those two answers.

I did not run the one-question-at-a-time interview, so I used your brief as the answers. Unanswered questions are flagged as assumptions.

## Recommendation

**Primary: the platform-managed listing, filed this week, with a dated tripwire to the vendor-SDK rung.**

- The platform builds and maintains the connector. Your cost is about 1 to 2 engineer-days of documentation and liaison work. That fits your 3 weeks and 4 h/month ceiling.
- The managed queue can reject you or run slow. So spend part of the 3 weeks now on API-readiness fixes, which help every path.
- Keep the rest of the 3 weeks as the SDK fallback budget. Python fluency makes that rung cheap.

**Tripwire:** if the platform has not accepted the request by **2026-11-20**, or rejects it, start the SDK build immediately.

## 1. Demand evidence (gate: pass for one deal)

| Evidence | Artifact to attach |
|---|---|
| Written contract condition, data team, 900k EUR renewal | The clause or email, verbatim |
| Procurement review closes about 2027-03 | Their stated date |

- **Build approved, scoped to this deal.** It is named, verifiable, and tied to a dated outcome.
- **Compounding value is unproven.** Your other 39 customers are not evidence. Send a 3-question survey: which ELT tool, which warehouse, would you use a connector. If 3 or more customers name the same tool, this becomes a standing distribution asset.
- **Business case:** retained 900k EUR renewal, plus support deflection and retention. Book **no revenue-share line**. No ELT platform pays source vendors.

## 2. Platform selection (blocking question)

You said "our ELT tool" but did not name it. The path depends on it:

| Customer's tool | Archetype | What changes |
|---|---|---|
| Fivetran | Curated, gates entry | Use By Request (Lite) first. Partner-Built is closed to new sources. The fallback is the Python Connector SDK. |
| Airbyte | Open contribution, gates labels | No entry gate, so there is no rejection risk. Python CDK or low-code manifest. The managed-queue rung becomes the no-code or low-code builder, which you own. |
| Singer, Meltano, or another open-source stack | Open spec, no gate or floor | You only have the custom path, with 100% of the maintenance tax. Your named owner is mandatory. |
| Other | Unknown | Re-verify the program tables first. My snapshot is dated 2026-08-30. |

Also ask what satisfies the condition: a catalog listing, or just a connector the customer can run. Ask whether Private Preview or Beta counts. Fivetran's release clock runs Private Preview, then Beta (within 6 months), then GA. If Preview is not enough, the 5-month window is tight.

Target one platform only. Add a second after you have measured the first one's maintenance load.

## 3. Build-path menu, re-ranked on your answers

| Answer | Effect |
|---|---|
| Deadline: 5 months, hard | Promotes the managed queue. |
| Effort ceiling: 3 weeks up front, 4 h/month after | Demotes custom to the bottom. Custom takes 100% of the tax. |
| Python daily on 2 of 4 engineers | The SDK rung gets cheap. Both the Fivetran Connector SDK and the Airbyte CDK are Python. |
| Schema barely changes | Fits the managed path (it needs a stable, non-dynamic schema). Also lowers the schema-drift maintenance cost. |
| One-off vs compounding: one deal for now | Do not over-invest. |

Three candidates:

| | A. Managed listing, SDK fallback (**recommended**) | B. SDK connector now | C. Custom or open-source tap |
|---|---|---|---|
| Time to catalog presence | Fivetran: 2 to 8 weeks of analysis, then about 30 days to build. Risk of slipping. | About 3 weeks of your time, then platform listing. | Fast to ship, no external gate. |
| Who owns the tax | Platform | Split: platform hosts, you fix and redeploy | You, 100% |
| Control | Low | High | High |
| Rejection risk | Yes | Low | None |
| Fits 3 weeks | Yes, with room to spare | Tight but plausible for a small resource scope | Eats the whole budget |
| Fits 4 h/month | Yes | Borderline | No |

**Why A:**
- It is the cheapest path and the only one that clearly fits 4 h/month.
- Your stable schema suits the managed queue.
- The tripwire turns its main weakness, timing risk, into a dated decision.

**Why not B first:** it spends your scarce hours on the maintenance tax before you know the queue fails.

You need to pick A, B, or C explicitly before I finalize steps 4 to 7.

## 4. Extraction-readiness audit

I have not seen your API, so this is the checklist to run, not findings. Time-box it to **about 1 week of the 3**. Grade each resource in scope pass/fail on:

1. Cursor-based pagination.
2. A cursor or `updated_at` that is stable across syncs.
3. A bulk or backfill endpoint, separate from UI-grade CRUD.
4. An explicit delete or change signal.
5. 429 with `Retry-After`.
6. A written per-resource extraction contract.
7. Additive versioning, with published deprecation dates.

**Fix order:**
1. Stable `updated_at` or cursor.
2. Delete signal. This is the most common gap. In clinical-trial ops, a missed hard delete in a customer's warehouse is also an audit-trail problem, not only a data-quality one.
3. Rate-limit signaling.
4. Bulk backfill.

A resource that cannot pass gets an explicit exclusion note.

**Scope question for security and legal:** decide whether patient-level or trial-subject data is in the connector's resource list. Exclude anything procurement would object to. I recommend starting with operational objects only.

## 5. CDC wording (customer-facing)

Ship it as **"incremental sync"**, never "CDC". Suggested text:

> Veridian syncs changes incrementally using a stable modification cursor on a [N]-hour interval, with eventual consistency. Changes made and overwritten within one interval are not captured. Deletions are captured via [the deletion feed / are not captured; a periodic full re-sync is available].

Upgrade path, in order: polling, then webhooks for freshness (never a backfill), then a vendor-side deletion feed, then periodic full re-import. Ship the deletion feed when customers report missed deletes, unless the customer's data team makes it a condition. Ask them.

## 6. Certification path

- **Listing is the bar for this deal.** Do not chase a badge now. No platform charges for one, but it costs engineering time.
- **Fivetran:** the SDK path lists as a community connector with no badge. Release-phase clock: Beta within 6 months of Private Preview.
- **Airbyte:** Marketplace inclusion only needs the test suite. Airbyte Certified is optional and comes later. Partner Certified is for destinations only.
- **Build in from day one:** integration tests for each sync mode, incremental wherever possible, and failures that are fast and actionable.
- **Adopt as your own SLOs:** at least 95% sync success, and first response within 3 business days.

## 7. Maintenance plan and budget

**The math:**
- Up-front build is about 120 hours (3 weeks).
- Annual upkeep at 15 to 30% is **18 to 36 hours/year, or about 1.5 to 3 h/month**. That fits your 4 h/month.
- At the 50% high-change ceiling it is 60 hours/year, or 5 h/month, which breaks the budget.
- Your stable schema makes the lower band plausible. Those percentages are vendor-published, so read them as an order of magnitude.

**Budget by path:**
- **Path A:** about 1 to 2 h/month, for liaison and monitoring.
- **Path B:** about 3 to 4 h/month, which is borderline.

**Owner:** name one Python engineer plus a backup before launch. A side-task with no owner is the documented decay path. This is your month-13 answer.

**Monitoring:**
- Alert on sync failures and schema-drift errors.
- Track the sync success rate against the 95% bar.
- Track connector-attributed support-ticket deflection.
- Track the share of new customers that connect through the platform instead of the raw API.

Upstream breaks usually arrive unannounced, and marketplace-tier listings carry no platform SLA.

## Timeline (today 2026-10-08, procurement closes about March 2027)

| When | Action |
|---|---|
| By 10-15 | Customer confirms their tool and what "available" means. Start the survey of the other customers. |
| By 10-15 | Submit the managed-queue request, or start the Airbyte builder. |
| 10-15 to 10-31 | Readiness audit (about 1 week) and the first fixes. |
| 11-20 | **Tripwire.** No acceptance, or rejected: start the SDK build (about 3 weeks). |
| By late Jan | Private Preview or listing live. Run an end-to-end test with the customer's data team. |
| Feb | Written confirmation from the customer that the condition is met, ahead of the procurement close. |

## Gates

- **Demand gate:** pass, with the contract clause attached.
- **Honesty gate:** pass. There is no revenue-share line, and "CDC" is not used unqualified.
- **Readiness gate:** not yet run. Every resource in scope needs a pass or an exclusion note.

## Open items (blocking)

1. Which ELT tool does the customer run?
2. What counts as "available": catalog listing, Preview, or Beta?
3. Which resources, and does any patient-level data need excluding?
4. Does your API have a delete signal and a stable `updated_at`?
5. Who is the named owner?
6. Your explicit pick: A, B, or C.

I will not finalize until you approve this draft section by section.