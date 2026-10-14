**Do not ship the 99.99% banner.** Ship the page below, which says 99.9% as a target and shows the measured numbers beside it. The incident history is also shown, so a reader can check the numbers.

Two things need your input first, and they are listed at the end. All thresholds below are proposals for engineering to confirm. I did not invent any measured numbers. The fields to fill from monitoring are marked `{…}`.

## Why 99.99% fails

- 99.99% allows about 4.3 minutes of downtime per month, or about 13 minutes per quarter.
- Last quarter's two 20-minute latency incidents total 40 minutes. That is about 3x the entire quarterly budget, before counting any outage.
- 99.9% allows about 43 minutes per month, or about 130 minutes per quarter. Those 40 minutes use about 31% of that budget, so 99.9% survives an honest count.
- Your contracts promise nothing today. A public 99.99% would be the first number a prospect's procurement team quotes back at you. Publishing a number you treat as aspirational is how SLA disputes start.
- The page must not be built on "latency doubled but 100% up". That is the silent-degraded failure mode. It also hides two real incidents behind a perfect percentage.

## Definitions to publish (write these before any number goes live)

Meterly runs a usage-metering API, so "working" includes accepting events and returning them correctly, not only responding.

**Probing.** Probes run every 60 seconds from at least 3 regions. They run outside Meterly's own infrastructure. Each probe runs the workflow check: ingest a test event, then read it back through the query API.

A minute counts as **Unavailable** when any of these is true:
1. At least 5% of probe requests to a component fail. Failure means a 5xx response, a timeout, or a response slower than 10 seconds.
2. The workflow probe fails, or the ingest-to-query lag exceeds `{5 minutes}`.

A minute counts as **Degraded** when:
- p50 latency is above 2x the trailing 30-day baseline for 5 consecutive minutes, and the minute is not Unavailable.
- This rule would have caught both of last quarter's incidents.

**Scope rules:**
- Availability is evaluated per component. A regional failure is a Partial Outage, scoped to that region.
- Planned maintenance is excluded from downtime arithmetic only if notice was given on time (see the maintenance section).
- Probe calibration is published. Interval and failure threshold are listed so readers can judge the number.

**What is published as two numbers:**
- **Availability** is the share of minutes not Unavailable.
- **Performance** is the share of minutes not Unavailable and not Degraded.

Degraded minutes do not count against Availability. They do count against Performance, and they appear in the incident list.

## Public page copy

> # Meterly reliability
>
> Current status: **{All systems operational}** · [Status page](/status) · Subscribe: email · RSS · webhook
>
> ## Last 90 days, by component
>
> | Component | Availability | Performance | Incidents |
> |---|---|---|---|
> | Ingestion API | {99.xx%} | {99.xx%} | {n} |
> | Usage query API | {99.xx%} | {99.xx%} | {n} |
> | Webhooks | {99.xx%} | {99.xx%} | {n} |
> | Dashboard | {99.xx%} | {99.xx%} | {n} |
> | Docs | {99.xx%} | {99.xx%} | {n} |
>
> ## Our reliability target
>
> Our internal target is **99.9% availability per month**. That is about 43 minutes of allowed downtime per month. This is a target, **not a contractual commitment**. Enterprise customers can discuss contractual terms with our sales team.
>
> ## How we measure
>
> - Probes run every 60 seconds from {3} regions, outside our own infrastructure.
> - A minute is **Unavailable** if at least 5% of requests fail (5xx, timeout, or slower than 10 seconds), or if a test event cannot be ingested and read back within {5 minutes}.
> - A minute is **Degraded** if median latency is more than 2x its 30-day baseline for 5 minutes. Degraded minutes do not count against Availability. They do count against Performance, and every one is listed below.
> - Planned maintenance is excluded only when we gave notice in advance.
>
> ## Incident history
>
> Every incident in the period, with start, end, affected components, impact, and a link to the summary.
>
> **{Date}: Increased API latency (Degraded Performance, 20 min)**
> {Component} response times were about twice normal for all customers. Requests completed successfully. {Cause and fix, 2 to 3 sentences.}
>
> **{Date}: Increased API latency (Degraded Performance, 20 min)**
> {Same structure.}
>
> The two entries above are last quarter's incidents, published retroactively. This is deliberate. A history that starts clean on launch day is less credible than one that admits the past.

## Status page behind it

This is a separate artifact from the uptime page. The uptime page shows history against a target. The status page shows what is happening now.

**Components.** Use five, named for what customers use: Ingestion API, Usage query API, Webhooks, Dashboard, Docs. Do not use internal service names.

**States.** Use four: operational, degraded, partial outage, major outage. State encodes breadth of impact, not how bad it feels. The top-level page state is the worst component state.

**Lifecycle.** Use Investigating, Identified, Monitoring, Resolved. Every update names the time of the next one.

**Monitoring drives the page.** This is the step that stops a repeat of the 35-minutes-green failure.
1. A failing probe auto-opens an Investigating incident. No human decides whether to disclose.
2. Humans then enrich the incident with scope and cadence.
3. The Degraded rule above also auto-opens an incident.
4. Track alert-fired-to-page-updated on every incident. Target: minutes.

**Severity mapping (internal to public):**

| Internal | Public state | First update |
|---|---|---|
| SEV1 | Major Outage | Immediately, auto-opened |
| SEV2 | Partial Outage | Immediately, auto-opened |
| SEV3 | Degraded Performance | Within the response window you set |
| SEV4 | No public incident | None |

**Escalation rule.**
1. Alerts become incidents.
2. Every incident is triaged.
3. Major problems trigger status updates.
4. Any SEV1 gets a published postmortem.

**Channels:**
1. Page with email and RSS subscription. Build first.
2. Webhook push. Build second, because your audience is developers.
3. SMS is deleted for now. You have no contracts that require it. Re-add it when the first contract specifies a notification channel.
4. Host the page off Meterly infrastructure: separate DNS, CDN, and cloud account. A status page that dies with the platform fails at the one moment it matters.

**Postmortems.** Publish a status-page summary for any incident customers felt: impact, cause, fix, prevention. Publish a full engineering-blog postmortem for SEV1. Never name an individual. Track completion of public action items, and keep it above 50%.

**Maintenance notices.**
- Give at least 24 hours for minor work and weeks for major work.
- Give enterprise customers a week or more.
- Include exact start and end times with a time zone, plus the exact scope.
- Post start and completion confirmations.
- Send through the page plus one push channel.
- Deprecations are a different communication, on a 6 to 12 month runway.

## What to tell marketing

- "99.99%" is not available. Contractual 99.9% is available after legal reviews it and the 12-month data supports it.
- Usable banner: **"Transparent reliability. Live status, measured uptime, and every incident published."**
- Fixing the slow-response blind spot is a stronger enterprise story than a bare number. Procurement teams distrust perfect percentages.
- Re-evaluate a higher published target after two quarters of data under the new definitions.

## Launch gates

Go live only when all three pass:
1. Detection-to-disclosure lag is in minutes, tested with a simulated failure.
2. Zero incidents where a third party reported before the page.
3. Every incident shows all four statuses with timestamps and kept next-update promises.

## Open items

1. Fill each `{…}` field. Pull the last 90 days from monitoring, including the two latency incidents, and recompute with the definitions above. Time: about 2 to 4 hours of engineering work.
2. Confirm the thresholds (5%, 10 seconds, 2x baseline, 5 minutes, ingest lag). If your metering SLAs depend on data freshness, the lag number matters most.
3. Answer these so I can re-rank the channels and hosting:
   - Does a status page already exist, and where is it hosted?
   - Do any enterprise deals or contracts demand a specific SLA or notification channel?

**Next:** reply with the answers to item 3, or paste your last 90 days of probe data and I will compute the numbers.