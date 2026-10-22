# Connector strategy decision: Brightloom Analytics, Tomas's open-spec tap

## Verdict

⚠️ **Don't sign off as framed. Sign off on a one-week validation instead, then a gated build.**

"Strictly better" doesn't hold. The tap is the cheapest way to get listed and the most expensive to keep alive. The skill ranks this path last on efficiency because you carry 100% of the maintenance tax. The two-month wait you'd be avoiding is also a different decision, and one your customers may not need.

I haven't done the interview, so some points below are assumptions. I've flagged them.

## What the pitch gets wrong

1. **Cost is per year, not per build.** "Zero budget" covers only the build. Upkeep runs 15–30% of build cost every year, up to 50% in mature phases. These are vendor-published estimates, so treat them as an order of magnitude. If the tap takes about 15 Friday-days, that is roughly 2–5 days a year, and up to about 7.5 days at the high end. That's my arithmetic, not a quoted figure.
2. **A side-task on a Friday has no month-13 owner.** The skill names this the documented decay path. Taps lose maintainers, and the ecosystem's record is multiple breaking upstream changes a year and abandoned taps. A tap with no owner is that failure scheduled in advance.
3. **"Listed on the hub" is presence, not quality.** The open-spec ecosystem has no gate and no floor. Listing is cheap because it signals nothing. The curated platform's review is what gives buyers a quality signal.
4. **The comparison is probably wrong.** The two-month review is the managed-queue path on a curated platform. Your customers run open-source ELT, so that queue may not serve them at all. For open-source stacks, the real alternatives to a Singer-style tap are:
   - **Airbyte's no-code or low-code builder.** Marketplace inclusion only needs the standard test suite. It centralizes cursor logic, so some of the tax is shared.
   - **The Singer tap.** It stays the pick if your customers compose taps themselves.

   I can't choose between them without the stack evidence.
5. **No demand evidence is cited.** "Gets us listed" is the motive. The skill refuses builds on hypothesis, and a connector with no evidence still bills its upkeep every year.
6. **The API hasn't been checked.** If it only has UI-grade CRUD endpoints, the tap will have rate-limited backfills, missed deletes and flaky incremental syncs. Those problems come from the API, so no amount of tap code fixes them.

## What's in Tomas's favor

- ✅ The custom path triggers no external review and is fully reversible, so trying it is low-risk.
- ✅ A backend engineer who knows the API is well placed to run the readiness audit and fix the API. That is the highest-ROI work in the whole strategy, and it also helps every customer who hand-rolls pipelines.
- ✅ Zero cash outlay is real. No platform charges for listing or certification.

## Conditions for sign-off

Complete steps 1–3 within one week, before Tomas writes tap code.

1. **Demand gate.** Attach at least one named artifact to the decision:
   - support tickets asking for a named ELT platform;
   - lost-deal or churn notes citing data-stack mismatch;
   - API logs showing hand-rolled paginated scans from data-team service accounts.

   If you find none, stop. Reopen on a concrete signal, for example three named-platform tickets in a quarter or one lost deal citing the gap.
2. **Stack finding.** Among the 90 customers, count which extraction platform each data team runs. It decides between the Singer tap and an Airbyte connector, and whether the managed queue matters at all. If the count is unknown, nothing else proceeds.
3. **Extraction-readiness audit.** Grade each in-scope resource pass/fail on these items. Any resource that fails gets a written exclusion note, never a silent skip.
   - Stable cursor or reliable `updated_at`.
   - Separate bulk/backfill path.
   - Delete signal.
   - `429` with `Retry-After`.
   - Additive versioning with published sunset dates.
4. **Named owner, in writing.** Tomas plus a backup, with a recurring monthly hours allowance (a few hours a month at minimum). "Friday when free" doesn't count. If nobody owns it in month 13, don't ship it.
5. **Scope the sync wording up front.** Say "incremental sync, eventual consistency". State the poll interval. Name what it misses: intra-interval overwrites, and hard deletes unless a deletion feed exists. Never write "CDC support". A SaaS source can't offer log-based CDC. The platforms' own SaaS connectors are timestamp-cursor polling.
6. **Business case on deflection and retention.** Don't book a revenue line. No ETL platform pays source vendors. Airbyte's floated revenue share became flat $10–150 bounties.
7. **Monitoring.** Alert on sync failures and schema-drift errors from day one. 87.3% of breaking API versions ship with no deprecation notice (ICSME 2020), and marketplace-tier listings carry no platform SLA.
8. **SLOs.** Adopt the published certification bars (≥95% sync success, first response in 3 business days or less, update at least every 6 months) as targets. They are self-imposed, not required for listing.

## Questions I need answered

These are the interview questions the skill would gate on. Each one changes the recommendation.

1. What demand evidence exists? Options: tickets, lost deals, hand-rolled pipelines in API logs, or none yet.
2. Which ELT platforms do your customers run? Options: managed commercial, self-hosted or open-source, tap-composing, or unknown.
3. Does the API expose a stable cursor, a bulk path and a delete signal? Options: all three, cursor only, UI-grade CRUD only, or unsure.
4. Who owns the connector in month 13?
5. Is there a hard deadline, such as a deal or a competitive evaluation?
6. Is this a checkbox for one deal or a standing distribution asset?
7. What is the effort ceiling: weeks up front and hours per month afterward?

## What would change my answer

- **To yes now:** evidence of named demand, plus a named owner with a monthly hours allowance, plus a passing or fixable readiness audit.
- **To the managed queue:** customers turn out to be on a curated platform, or there's a hard deadline. The queue is the deadline-friendly path, but it can reject the source and takes weeks.
- **To the Airbyte SDK path:** the compounding mandate is real and Tomas has capacity. This is the usual promotion once demand is validated.
- **To no build:** no evidence turns up. Improve the raw API instead.

## Caveats

- The platform-program details come from a snapshot dated 2026-08-30. Check them again before committing.
- The final strategy document would need your approval section by section. I haven't drafted it past this decision memo, because the evidence behind the gates doesn't exist yet.