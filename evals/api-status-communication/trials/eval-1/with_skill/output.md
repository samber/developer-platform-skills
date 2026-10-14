# Parcelforge status page: component and status model

I applied the `api-status-communication` skill, steps 1 and 2 plus the regional and mapping material. I changed two of your three decisions and kept one with a mapping layer. Your Frankfurt outage is the test case, and it gets a worked answer below.

## Verdicts on your three plans

| Your plan | Verdict | Why |
|---|---|---|
| List all 38 microservices as components | ❌ Change | Components follow what an integrator sees, not your architecture. During an incident, 38 rows are unparseable, and nobody can tell which row means "my label calls fail". |
| Own lifecycle vocabulary (Detected, Diagnosing, Patching, Stable) | ⚠️ Keep internally, publish the standard four | Subscribers already read Investigating, Identified, Monitoring and Resolved. A custom set costs comprehension and buys nothing. Your runbooks keep their words, and a written map connects them (below). |
| Six-color severity scale | ❌ Change | The page takes four visual states. Six colors across seven components is a matrix nobody holds in their head mid-incident. Nuance goes in the scope tag and the update text, not in more colors. |

The state meanings must be defined by breadth of impact, not by how bad it feels. Your six colors almost certainly encode felt severity, and that is the axis that makes the Frankfurt argument unwinnable.

## 1. Components

I don't know your product surface, so these seven groups are a proposal. Correct them against your 900 integrators' vocabulary. The test for each one is "would an integrator name it in a support ticket?"

| # | Component | Integrator's mental model | Internal services rolled up (illustrative) |
|---|---|---|---|
| 1 | Shipment Creation & Labels | "I can book and print" | order intake, carrier allocation, label rendering, … |
| 2 | Tracking | "I can see where parcels are" | event ingest, tracking read, ETA, … |
| 3 | Rates & Address Validation | "I can quote and validate" | rating, geocoding, address validation, … |
| 4 | Webhooks | "I get my events" | event dispatch, retry queue, … |
| 5 | Authentication & API Keys | "I can log in and call the API" | identity, token issuance, key management, … |
| 6 | Dashboard | "The web console works" | console frontend, reporting, … |
| 7 | Sandbox & Docs | "I can build and test" | sandbox environment, docs site |

- Authentication is its own component on purpose. A locked-out integrator doesn't care that the other six are green.
- All 38 services map to one of these components in an internal dependency map. The map is not public. It is how monitoring computes component state.
- If one service genuinely maps to a distinct integrator action, promote it to its own component. Keep the total at 8 or fewer.

### Regions are a scope, not a component

Each component carries per-region sub-state. Frankfurt is not a component of its own. It is a region scope on components 1 to 4 (and 5, if auth is regional).

```
Shipment Creation & Labels      Operational
  ├ eu-central (Frankfurt)      Partial Outage
  ├ <region 2>                  Operational
  └ <region 3>                  Operational
```

Integrators can then subscribe by component and region. A Frankfurt incident reaches the Frankfurt integrators and doesn't alert the rest.

## 2. State model: four visual states, defined by breadth

| State | Definition | Color |
|---|---|---|
| Operational | Working normally | Green |
| Degraded Performance | Works, but slow or elevated errors for everyone in scope | Yellow |
| Partial Outage | Completely broken for a subset (a region, a customer segment, an endpoint class) | Orange |
| Major Outage | Unavailable for everyone | Red |

Rules to write down once, so they aren't re-argued per incident:

1. **State is breadth of impact.** "Broken for everyone in one region" is a Partial Outage, scoped to that region. Complete failure inside the scope doesn't promote it.
2. **Top-level page status is the worst component state.** Region scope doesn't dilute it. The page header reads "Partial Outage" with a scope tag, never "All Systems Operational".
3. **Major Outage requires global scope.** It also applies when the failing region is the only one the component runs in.
4. **Slow for everyone is an incident.** Degraded Performance exists so that "technically up" still gets posted.
5. **Nuance goes in text.** Each incident carries a plain-language title and a scope line, for example "All requests served from Frankfurt".

### Folding your six colors into four

I haven't seen your six levels, so this is a template. Fill in your own labels and keep the rule that the fold is deterministic: the same inputs give the same row.

| Your six levels (internal) | Public state |
|---|---|
| 1. Cosmetic / informational | No public incident (changelog note if relevant) |
| 2. Minor, some users slow | Degraded Performance |
| 3. Moderate, subset affected | Partial Outage |
| 4. Severe, subset fully down | Partial Outage |
| 5. Severe, most users | Major Outage |
| 6. Total | Major Outage |

Levels 3 and 4 collapse to the same public state because their difference is intensity, not breadth. The detail lives in the update text.

## 3. Lifecycle vocabulary

Publish four statuses and map your runbook words onto them. Responders flip the public status through the map and never debate wording mid-incident.

| Your runbook term | Public status | Rule |
|---|---|---|
| Detected | **Investigating** | Auto-opened from the monitoring alert, no human gate |
| Diagnosing | **Investigating** | Stays here until a cause or affected component is confirmed |
| Patching | **Identified** | Cause confirmed, fix in progress. Post the workaround here. |
| Stable | **Monitoring** | Fix deployed and holding, watched for a defined period |
| (no equivalent) | **Resolved** | Posted after the watch period. Quantifies impact and commits to a summary. |

"Stable" is not "Resolved". Closing on the first green minute and then reopening costs more trust than a visible monitoring period. If your runbook has no equivalent of Resolved, add the step. Choose the watch period yourself (a suggested starting point is 30 minutes).

## 4. Wiring state to monitoring

State is computed from probes. A human enriches it but never decides whether customers get told first.

- **Probes are workflow-level, per region.** Run synthetic journeys that mirror integrator actions: create a shipment and fetch its label, fetch tracking, validate an address, receive a webhook, mint a token. Service-level health feeds the internal dependency map but isn't the public signal.
- **Auto-open.** A failing probe in a scope opens an Investigating incident on the affected component and region.
- **Thresholds are yours to tune.** As a starting point to calibrate against your own traffic:
  - Degraded Performance when probe latency or error rate is over threshold in all regions of a component.
  - Partial Outage when a probe fails completely in one or more scopes but not all.
  - Major Outage when probes fail in all scopes.
- **Disclosure lag is the key metric.** Measure alert-fired to page-updated on every incident. Drive it to minutes.

## 5. The Frankfurt case: how to represent it

A full Frankfurt data-center outage for 40 minutes with everything else fine is a **Partial Outage, scoped to Frankfurt, on every component that has a Frankfurt footprint.** It is not Major Outage and not a blanket Degraded.

The disagreement had two sides, and each was half right:

- "It was total!" is true for the people served from Frankfurt, and the scope line says so: "All requests served from Frankfurt failed."
- "Everything else was fine!" is true for everyone else, and the Operational rows for the other regions show it.

The state encodes breadth and the text carries intensity, so the two sides no longer conflict.

How it would have read:

> **Shipment, Tracking, Webhooks: API unavailable for requests served from Frankfurt (eu-central)** - Investigating
> 14:02 UTC - All requests served from our Frankfurt data center are failing. Other regions are operating normally. If your integration can use another region, you can retry there. Next update by 14:20 UTC.
>
> 14:17 UTC (Identified) - Cause confirmed as loss of the Frankfurt site. We are restoring service. Other regions remain unaffected. Next update by 14:45 UTC.

Notes for that incident type:

- **Failover.** If traffic can fail over, check whether integrators outside Frankfurt see added latency. If so, those regions are Degraded Performance, not Operational. Say so, so you don't understate it.
- **Region pinning.** If some integrators are pinned to Frankfurt for data residency, they have no failover path. Say so in the scope line, because it is the information they need.
- **Posting early.** The 40 minutes should have opened from the first failing probe. Don't wait for a human to confirm Frankfurt is down.
- **SLA.** Decide in writing whether the SLA is evaluated per component and region or service-wide. This incident is the exact case that rule exists for. The status page and SLA text must agree.

## 6. Open questions

I made assumptions where you didn't give details. Each answer moves part of the design.

1. Is this greenfield, and what monitoring exists today? This decides whether the probes in section 4 are new work.
2. Who reads the page: integrating developers only, or business stakeholders and enterprise customers too? Mine assumes mostly developers, which keeps it to one public page.
3. Do any contracts carry SLAs with consequences or notification-channel clauses? This decides whether per-region SLA evaluation and push channels beyond email and RSS are needed.
4. Does the status page share DNS, CDN or cloud account with the platform? If so, hosting it elsewhere is the first task.
5. What are your actual six severity levels and your region list? Both fill the tables above.

## 7. Next steps

Remaining work, in the skill's order:

1. Channels: email and RSS first, then webhook push for integrators.
2. Update cadence, with a next-update time on every post.
3. Postmortem policy.
4. SLA reporting.
5. Maintenance windows.

Say the word and I'll take them on after you've answered the questions above.