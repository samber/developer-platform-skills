# Pathvine marketplace: the honest read

**Verdict: neither of you is right. Don't build a marketplace now. Don't kill the integration work either.** Build a curated partner catalog on top of better bilateral integrations. Set written criteria for promoting it to a marketplace later.

I couldn't run the skill's interview, so the demand and supply answers below are assumptions. Section 4 lists what would change the verdict.

## 1. The two arguments are different business cases

The skill separates two cases for a marketplace. A one-pager that blends them can't be falsified.

| Case | What it claims | Verdict at Pathvine |
|---|---|---|
| **A. Ecosystem flywheel** | More apps attract customers, more customers attract apps, and it compounds | **The CEO is right.** It doesn't hold at 240 customers. |
| **B. Retention/expansion** | Customers with several integrations churn less and buy more | **Plausible, but unproven here.** It needs no third-party builders. |

**Why the VP's flywheel fails today.**
- The flywheel needs a hard side, which is the builders. The skill's own cold-start framing says the hard side fails first.
- A third-party developer building on a 240-customer platform has little audience to reach. The VP's one-pager doesn't name who those builders are or why they would show up.
- The CEO's phrasing, "nobody builds a *business* on us," is also the wrong test. Builders don't have to build a business. The real question is whether established vendors will ship a connector because your customers ask for it. In vet software that means lab and diagnostics systems, payments, accounting, pet insurance, client messaging and telehealth. That is bilateral integration work, not a flywheel.

**Why the CEO's "distraction" claim overreaches.**
- It treats "no flywheel" as "no value." Case B doesn't depend on scale in the same way. If clinic groups that run 4 or more connected tools churn measurably less, integrations are worth funding.
- The skill says a platform can act on case B even where case A doesn't apply. At $9M ARR across 240 groups, a few retained accounts matter.

## 2. The gate: build, join, or buy

The skill allows "build" only if all four triggers hold, each with cited evidence.

| Trigger | Status | Evidence needed |
|---|---|---|
| 1. Customer pull (lost deals, support requests, or procurement friction) | **Unknown** | Count of deals lost or stalled over integrations in the last 12 months, and ranked integration requests |
| 2. Supply signal (partners asking to build, or unofficial integrations) | **Likely absent** | Named partners who have asked, or third-party integrations that already exist |
| 3. Repeated procurement friction from one-off requests | **Unknown** | Number of one-off integration requests that sales or support had to handle |
| 4. Staffing for the full partner lifecycle as a standing commitment (API, docs, sandbox, review, support) | **Probably no** | A named owner and headcount |

A build recommendation with an unevidenced trigger fails the skill's own check. At minimum, trigger 2 is probably missing. The skill warns that building without confirmed supply and demand produces "little more than an expensive partner directory."

**Recommendation:** go to the intermediate step.
1. Build a **curated partner catalog**. It's a hand-picked list of integrations, with no open admission, no self-serve review pipeline and no billing flow.
2. Improve the **bilateral integrations** your customers ask for most.
3. If the real problem turns out to be "we need many integrations fast," consider **buying embedded iPaaS** instead of building.
4. **Join** the ecosystems your customers already trust, and list there first.

**Promotion criteria for revisiting "build":** all four triggers hold, with evidence. In particular:
- Partners ask to build on you without being recruited.
- Integration gaps show up repeatedly in lost deals.
- You can staff the lifecycle permanently.

Review these criteria at a fixed date, for example every two quarters. Don't leave them open-ended.

## 3. What to measure in year one

This is the plan if you go ahead with the catalog and bilateral path. It follows the skill's metric categories. There are no industry thresholds at this scale, so **baseline everything in your own first quarter** and judge direction against yourself. The 91% AppExchange figure is a mature-platform anchor, not a target.

**Lead with supply, because it fails first.**
- Active partners with a live integration.
- Time from partner agreement to first live integration.
- Share of the catalog updated in the last two quarters. A stale catalog is the "expensive directory" failure becoming visible.
- Inbound partner requests, separate from partners you recruited. This is the real flywheel signal. If it stays at zero after a year of effort, the CEO is right and you stop.

**Demand**
- Share of the 240 customers with at least one installed connector.
- Integrations per account, watching the 4+ cluster the skill cites as the switching-cost threshold.
- Retention and expansion for accounts above versus below that cluster. This is the direct test of case B.

**Coupling**
- Deals where integration capability was cited in a win, and churn saves attributed to integrations. This attribution is soft, and the document should say so rather than invent precision.

**Caveats to state upfront.**
- With 240 accounts, splitting by integration count gives small cohorts. Treat the retention delta as directional. It will not be statistically conclusive in year one.
- Integration-heavy accounts may simply be your healthiest customers. Correlation here isn't causation, so write that into the plan before the numbers arrive.

**Pre-registered stop conditions.** Write these down now, before the data exists.
- "Case B is dead if accounts with 4+ integrations show no retention advantage after four quarters."
- "Case A is dead if no unsolicited partner requests arrive by month twelve."

## 4. What would change this verdict

Please confirm or correct these. The skill would ask them one at a time.

1. Evidence of lost or stalled deals over integrations. A meaningful number would strengthen the case for building.
2. Whether partners are already asking to build on Pathvine.
3. Whether you can staff the partner lifecycle permanently.
4. What the marketplace is *for*: revenue, retention, or ecosystem. I assumed retention.
5. Data sensitivity. Vet clinic data includes client PII and payments. I assumed medium. If it's high, any future marketplace needs a hard security gate, not an open one.
6. Whether a hard deadline or a budget ceiling exists.

## 5. If you later graduate to a marketplace

These are the skill's defaults, so the operating model isn't a surprise later. They are not a decision for now.
- **Curation:** hybrid, meaning open listing plus a certified tier. Step up to a hard review gate if data sensitivity is high.
- **Take rate:** zero while seeding.
- **Seeding:** first-party complements first, since the hard side won't show up unaided.
- **Governance:** write down admission, value split and conflict resolution (including delisting) with named owners before launch.

## Bottom line for the CEO and VP

- The flywheel claim doesn't hold at your size, so the VP's one-pager shouldn't drive the decision.
- The "distraction" claim also doesn't hold, because integrations may be a retention lever. The data to test that is cheap to collect.
- Spend a small, bounded effort on the catalog and bilateral path with the stop conditions above. Revisit "marketplace" only when the four triggers show evidence.