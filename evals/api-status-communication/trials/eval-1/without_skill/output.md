# Parcelforge status page: component and status model

I'd change all three of your starting choices. I couldn't see your API surface, so the component list below is an example to check against it.

## 1. Components: about 10 customer-facing ones, not 38

**Why not 38:**
- Integrators know your endpoints, not your service names. A red `rate-cache-svc` tells their on-call engineer nothing.
- One failing service usually breaks several capabilities. Customers would see a confusing mix of red rows instead of a clear answer.
- Every refactor or service split would change the public page. The incident commander would also have to map services to rows during an incident, and the mapping would go stale.

**Rule:** a component is something an integrator can name from their own integration code, such as an endpoint group or a delivery channel. Keep the service-to-component mapping internal, with one owner per component.

**Example set (adjust to your API):**

| Group | Component |
|---|---|
| Core API | Authentication and API keys |
| | Rates and quotes |
| | Shipment creation |
| | Labels and documents |
| | Tracking queries |
| | Address validation |
| Delivery channels | Webhooks and event delivery |
| | Carrier connectivity (sub-status per carrier, if upstream carriers are a common failure source) |
| Account | Billing and invoicing |
| | Developer dashboard and docs |
| | Sandbox |

**Where "exactly what's affected" lives:** in the incident text. Each update names the operations and scope, for example "`POST /shipments` returns 503 for carrier X". Prose carries that precision better than a 38-row grid does.

## 2. Lifecycle: use the standard four publicly, keep yours internally

Your vocabulary describes your response process, not the customer's situation. It also has gaps:
- "Patching" assumes a code fix. Failover and restore, like the Frankfurt outage, aren't patches.
- "Stable" doesn't say whether the incident is closed.
- Customers' tooling (Slack integrations, RSS readers, parsers) expects the standard states.

**Public states:** Investigating → Identified → Monitoring → Resolved. Scheduled maintenance is a separate flow: Scheduled → In progress → Completed.

**Mapping from your runbook vocabulary:**

| Internal | Public |
|---|---|
| Detected | Investigating (published only after a human confirms customer impact) |
| Diagnosing | Investigating |
| Patching | Identified (the cause is known and a fix or mitigation is under way) |
| Stable | Monitoring |
| (closure after an agreed quiet window) | Resolved |

Store your internal state as a hidden field on the incident, so runbooks and the public page can't drift apart. "Stable" maps to Monitoring and not Resolved because you need a defined confirmation window before closing. Pick that window, for example 30 minutes with no regression.

## 3. Severity: four levels plus maintenance, defined by metrics

Six colors would have two problems:
- **Inconsistent use.** Adjacent levels need crisp definitions, or two engineers will pick different levels for the same incident at 3 a.m.
- **Accessibility.** Color alone fails for color-blind readers. Always pair color with an icon and a text label.

Customers mostly want to know whether to act. Put the nuance in scope and text, not in extra levels.

| Level | Definition (starting thresholds, calibrate to your SLOs) |
|---|---|
| Operational | Within SLO |
| Degraded performance | Works but slow or flaky: p95 latency above 2× baseline, or 5xx errors between 1% and 5% |
| Partial outage | Part of the component is failing: 5xx between 5% and 50%, or one sub-capability, carrier, or region unavailable |
| Major outage | Unusable for the affected scope: 5xx above 50% or total failure |
| Under maintenance | Planned work. This is not a severity level, so it never counts against uptime |

Keep a finer internal SEV scale for paging if you want one. It is a separate field and never shown publicly.

## 4. Region: a second axis, which settles the Frankfurt argument

The argument was probably about whether to call it "a major outage" or "fine." Both are true for different audiences. The fix is to separate **severity** (how bad) from **scope** (for whom), instead of squeezing both into one color.

**Model:** status is stored per (component, region), not per component.

```
Component  { id, name, group, description, internal_services[] (hidden), owner }
Region     { id, name }                              // e.g. eu-frankfurt, us-east
Impact     { component_id, region_id, level }        // an incident has many
Incident   { id, title, public_state, internal_state (hidden),
             impacts[], started_at, resolved_at, updates[] }
Update     { timestamp, public_state, body }
Subscription { subscriber, components[], regions[], channel }
```

**Display rules:**
- If customers can see which region they use (for example through an `eu.` hostname), show a component-by-region matrix. Otherwise show one row per component with a scope label.
- The page banner shows the worst status for the viewer's selected region. The default view says something like "Major outage in EU (Frankfurt). Other regions operational," and never turns the whole page red.
- Compute and publish uptime per component per region. A global number would show a 40-minute single-region outage as almost nothing, which hides it from the customers it hurt.
- Notify subscribers by region, so customers in other regions aren't paged.

**Frankfurt, replayed under this model:**
- Impacts: every component in `eu-frankfurt` = Major outage, if there was no failover. Every other region = Operational.
- If part of the traffic failed over, use Degraded or Partial instead.
- The cause ("data center down") is internal detail. The customer-facing incident title is "EU (Frankfurt) region unavailable."
- Updates would have run Investigating → Identified (failover or restore in progress) → Monitoring → Resolved, with 40 minutes of downtime recorded against `eu-frankfurt` only.

## Decisions to confirm

1. **Region visibility.** Can customers tell which region they're on, or does routing hide it? Pinning for data residency matters, because pinned customers can't fail over.
2. **Detection gating.** Do monitors auto-publish "Investigating," or does a human confirm first? I recommend a human gate, since false public alarms cost trust.
3. **Carrier connectivity.** Are upstream carriers a frequent cause of incidents? If so, give each carrier its own sub-status.
4. **Thresholds.** Are the numbers in section 3 close to your SLOs?
5. **Machine-readable feed.** With 900 integrators, ship webhook, RSS, and JSON status feeds on day one.