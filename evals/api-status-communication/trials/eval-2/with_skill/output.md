# Quotable status communication: tightened incident process

I followed `api-status-communication` and its incident-update-templates reference. I couldn't ask the skill's clarifying questions, so the assumptions I made are listed at the end.

## Diagnosis

Your monitoring worked. The page stayed green for 45 of 60 minutes because **two human gates sit between the alert and the first public word**. The on-call engineer confirms, then the support lead reviews the wording. That is status theater, the skill's first failure mode. The Reddit thread beating your page is the second. The skill's own anti-benchmark is a page that stayed green for 35 of 54 minutes because a human had to flip it.

The review step was added to prevent false alarms and typos. Those are real concerns, but a human gate on first disclosure is the wrong tool for either:
- **False alarms** are a detection-quality problem. Fix them in the alert rules.
- **Typos** are a wording problem. Fix them by pre-approving the wording.

## New process

**Principle: humans enrich the incident. They never gate the first disclosure.**

| # | Step | Owner | Target |
|---|---|---|---|
| 1 | Monitoring alert fires and passes the confirmation rule (below) | Automation | t=0 |
| 2 | **Auto-opens an "Investigating" incident** on the affected component, using a pre-approved template with a fixed next-update time | Automation | t+≤5 min |
| 3 | On-call is paged and confirms or adds scope. They set the component state (see mapping) and edit the title and body | On-call | t+≤10 min |
| 4 | Updates follow the lifecycle: Investigating, Identified, Monitoring, Resolved. Each names the next update time | On-call | Every 20–30 min |
| 5 | Support lead reviews after publication and fixes wording. Corrections are posted as an edit or follow-up | Support lead | Within 30 min, never blocking |
| 6 | Resolved note and postmortem (see below) | On-call, then support lead | See below |

### Replacing the old gates

**Engineer confirmation (false alarms).** Move it into the alert rule, so the automation does the confirming:
- Require N consecutive failed probes, for example 3 at 1-minute intervals.
- Require failures from at least 2 probe locations, or from an endpoint class rather than a single endpoint.
- Add at least one **workflow-level probe**, a real multi-step user journey such as authenticate, then fetch a price, then verify the payload. The skill flags this as the way to catch "infrastructure green, product broken".
- Page the on-call for every alert that passes the rule.
- If the on-call decides it was a false alarm, resolve the incident as "Resolved: monitoring anomaly, no customer impact". Do not delete it. A few honest false alarms cost less trust than one 45-minute green lie. The skill's own point is that openly admitting failure builds trust.

**Support-lead review (typos and embarrassment).** Replace it with pre-approved templates:
- Write the Investigating, Identified, Monitoring and Resolved templates once, with the support lead approving them in advance. Use the skeleton: acknowledge impact, state only what is confirmed, give a workaround ("none at this time" if none), and name the next update time.
- Auto-publish only the template. Free-form text is added by the on-call afterwards.
- Titles are plain language ("Elevated error rates on the Quotes API"). They never use internal names or severity labels.
- Publish nothing speculative, and never blame an upstream vendor.

### Severity-to-state mapping (decide once, in writing)

| Internal severity | Public state | First public update |
|---|---|---|
| SEV1: down for everyone | Major Outage | Auto, immediately |
| SEV2: many users affected, or one region down | Partial Outage (scoped to the region or endpoint) | Auto, immediately |
| SEV3: slow for everyone, or minor impact | Degraded Performance | Auto after the response window |
| SEV4: cosmetic | No public incident | None |

Severity reflects **breadth of impact, not how bad it feels**. Silent degradation is also an incident: if latency doubles for everyone, post it as Degraded Performance even though the API is "up".

### Page structure
- Use 4 to 6 consumer-recognizable components, for example Quotes API, Historical data, Auth, Webhooks, Dashboard and Docs. Do not mirror internal services.
- Top-level status is the worst component state, and you document that rule once.

## Channels

- **Default:** status page with email and RSS subscription. This is cheap and reduces inbound tickets.
- **Promote webhook push:** your audience is developers who integrate pricing data into their own systems. A status webhook lets them wire it into their alerting.
- **Posting where customers already look:** the Reddit thread shows people go to a third party first. Post the same text to your X or social account at the same time. Consistency across channels matters, because divergence reads as dishonesty.
- **SMS:** skip it unless you have contractual SLAs that specify notification. It returns as a rung when the first contract does.
- **Host the status page off your own infrastructure** (separate DNS, CDN and cloud account). If it shares infrastructure with Quotable, this becomes the first task rather than the last.

## Postmortems

- **Default:** a status-page summary for any consumer-visible incident, covering impact, cause, fix and prevention.
- **Full engineering-blog postmortem** for major incidents and for any case where trust was visibly shaken. Your last outage, with a Reddit thread, qualifies.
- Keep it blameless and name no individuals.
- **Publish the action items and track their completion.** Below about 50% completion, postmortems become theater.
- For the last outage, publish a postmortem addressing the 45-minute disclosure gap directly. That is where trust is rebuilt.

## SLA edge cases

If you publish uptime numbers, define in writing:
- The latency threshold at which a slow response counts as down.
- Whether the SLA is measured service-wide or per component.
- That planned maintenance is excluded only when adequate notice was given.

Show incident history next to the uptime percentage. Degraded Performance counts as 0% downtime in the usual arithmetic, so the percentage alone can hide real incidents.

## Gates and measurement

These three are pass/fail. Iterate the process until all three pass:
1. **Detection-to-disclosure lag** is under 5 minutes, measured per incident as alert fired to page updated. Tens of minutes means a human gate is still in the loop.
2. **Third-party-first disclosures** is zero. No Reddit, DownDetector or social post may beat the page.
3. **Lifecycle completeness:** every incident shows all four statuses with timestamps, and every "next update by" promise was kept.

These two are trends, not pass thresholds:
- Postmortem action-item completion, targeted above 50%.
- Support tickets during incidents, falling as subscribers grow. Baseline this at your next incident.

## First actions

1. Remove the support-lead gate from the first disclosure.
2. Write and approve the four templates and the severity mapping.
3. Wire the auto-open from the confirmed alert to the status-page API.
4. Add the workflow probe and the N-consecutive-failures rule.
5. Run a game-day drill and measure the lag against the 5-minute gate.
6. Publish the postmortem for the last outage.

## Assumptions to correct me on

- **Page hosting:** I assumed the status page may share infrastructure with Quotable. If it does, off-platform hosting moves to the top.
- **SLAs:** I assumed you have no contractual SLAs with notification terms. If you do, SMS or phone push and maintenance-notice floors come back.
- **Audience:** I assumed the readers are mostly integrating developers, so one public developer-facing page with webhook push is enough.
- **Effort:** I assumed a compounding practice rather than a one-off fix. If you are under a hard deadline, do steps 1 to 3 first and hold postmortems at the summary level.
- **Last outage:** I don't know whether the 45 minutes was mostly waiting for the engineer or for the support lead. Check the timestamps. If it was mostly the lead, the fix is the same, but the evidence for dropping that gate gets stronger.