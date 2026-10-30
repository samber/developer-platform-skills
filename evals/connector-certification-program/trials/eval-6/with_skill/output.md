**Answer: don't announce "fully supported by Glimmerdeck".** Certified connectors get **Glimmerdeck triage, then the partner fixes**. This is a draft charter, and I assumed the interview answers marked below.

A "fully supported" announcement is a joint SLA. The skill ranks that as the starved option, to use only when certified connectors are sold inside a paid plan. Yours are free, so you would answer for partner code with no revenue behind it. It would also turn the 30% of tickets that are partner bugs into 100% yours.

## 0. Inputs

| Question | Answer | Status |
|---|---|---|
| Q1 What partners build | Metadata connectors on a catalog | Given |
| Q3 Who reads the badge | Buyers choosing connectors, plus your support team | **Assumed** |
| Q4 Per-connector telemetry | Unknown | **Assumed: partial**. The fault split does not exist yet |
| Q7 Existing tier | Running. Certified connectors exist, and the support load shows a gap | Given, inferred |
| Q11 Fee | None, since certified connectors are free | Given |
| Q2, Q5, Q6, Q8 to Q10 | Partner install share, release cadence, reviewer hours, deadline, effort ceiling | **Unknown** |

Re-ranking from the answers:
- **Q11 (free):** moved the joint SLA out of reach. There is no revenue to fund it.
- **30% partner-bug tickets:** moved triage and the fault split to the top. They are the cheapest way to cut the load.

## 0b. Proposals evaluated

| Proposal (who) | Verdict | Rule |
|---|---|---|
| "Certified = fully supported by Glimmerdeck" (head of partnerships) | **Rejected** | Joint SLA is promoted only for paid plans (section 3). The platform answers for code it does not control. |
| Keep silence on support, let customers assume (status quo) | **Rejected** | This is the "silent support promise" failure mode. It causes the 30% misrouted tickets. |
| Make the badge worth more | **Changed** | Make it worth more through evidence and a clear support sentence, not an unfunded promise. |

## 1. Go/no-go

- **Outside reader:** buyers read the label. Holds (assumed).
- **Partner share:** unknown. **Check before launch.** If Glimmerdeck builds the connectors buyers actually use, fail the gate and ship ownership labels only.
- **Evidence:** the kit is affordable. Telemetry criteria wait until the platform-versus-connector fault split exists. Holds for the kit.
- **Decision:** run the program, kit first, telemetry later.

## 2. Labels and support per tier

| Label | Maintained by | Earned by |
|---|---|---|
| Glimmerdeck-maintained | Glimmerdeck | Built by us |
| **Certified** | Partner | Kit pass, plus telemetry once it exists |
| Partner-maintained | Partner | Listed only |
| Community | Contributors | Listed only |

**Listing bar**, kept apart from the labels: valid manifest, no secrets in fixtures, security contact named, support channel named.

**Brand rule:** the label reads "Certified", never "Glimmerdeck Certified" or "Verified by Glimmerdeck". If the brand appears, the support sentence goes right next to it.

## 3. Support routing per tier

| Label | First contact | Who fixes | Response commitment (starting values) | Sentence shown on the listing |
|---|---|---|---|---|
| Glimmerdeck-maintained | Glimmerdeck | Glimmerdeck | Your normal support SLA | "Built and supported by Glimmerdeck." |
| **Certified** | **Glimmerdeck** | **Partner** | Glimmerdeck isolates and routes within 1 business day. Partner first response ≤3 business days. | "Certified by Glimmerdeck against a public test kit. Glimmerdeck triages issues and routes connector bugs to <partner>, who fixes them. Fixes are the partner's responsibility, not a Glimmerdeck SLA." |
| Partner-maintained | Partner | Partner | Partner's own | "Supported by <partner>, contact <channel>. Not covered by Glimmerdeck support." |
| Community | Contributors | Contributors | None | "Community-maintained. No support from Glimmerdeck or a partner." |

How the Certified route works:
1. **Auto-attach the connector ID and version to every ticket.** Use a ticket-form field filled from the connector, so support never asks.
2. **Isolate once.** Support runs one runbook step to decide platform fault or connector fault. If it is the platform, Glimmerdeck fixes it. If it is the connector, support routes it.
3. **Route with evidence.** Send the partner the logs, the version and the repro. Tell the customer the owner and the channel, in one message.
4. **Escalate silence.** If the partner misses the 3-business-day first response, that feeds the support-response criterion (section 7).

This turns partner bugs from "ours to fix" into "ours to route". Triage still costs you something. Routing with evidence is much cheaper than debugging partner code.

## 4. Criteria for Certified

| Metric | Threshold | Window | Minimum volume | Measured by |
|---|---|---|---|---|
| Contract layer pass | All required tests, >90% overall | Per release | n/a | Operator CI |
| Production sync success | ≥95%, platform-outage errors excluded | Trailing 28 days | ≥200 syncs | Operator telemetry (after the fault split exists) |
| Support response | First response ≤3 business days | Trailing quarter | ≥5 tickets | Operator ticketing |
| Security contact | Named and reachable | Annual check | n/a | Operator |

- **Baseline:** these are starting values borrowed from other catalogs. Recalibrate against your best connectors after one quarter.
- Below the minimum volume, a criterion reads "insufficient data", never fail.

## 5. Kit

- Versioned with semver, with a changelog. Open to partners for self-testing. Submission is blocked until required tests pass.
- Layers: static, contract, then regression for high-usage connectors, then a platform matrix.
- Required tests are separate from the overall pass bar. Exemptions need reviewer sign-off, and their count is published.

## 6. Renewal

- Each badge is pinned to the kit version, the platform version, and the lowest connector version it covers. Older connector versions show the "Partner-maintained" label.
- Re-run the kit on a contract-changing platform release, a new kit major, a behavior-changing connector release, and new scopes.
- Ship the kit for platform releases to partners at your beta, before general availability.
- Telemetry is re-evaluated on a published monthly date, and each partner sees its own values the same day.
- Notice before new criteria apply: 6 months.

## 7. Decertification ladder

| Rung | Trigger | Owner | Notice | Customer action |
|---|---|---|---|---|
| Warning | One failed monthly evaluation, or a missed first response | Partnerships | 30-day remediation | None |
| Badge suspended | Two consecutive failed evaluations | Partnerships | 14 days | None. The listing reverts to Partner-maintained. |
| New installs blocked | Suspended 90 days, or abandoned (no release and no support response for 6 months) | Platform lead | 30 days | Notified |
| Existing installs disabled | Only after rung 3 | Platform lead | 60 days | Notified, with a migration path |

- **Adoption first:** offer an abandoned connector above the usage threshold to a new maintainer before rung 3.
- **Security fast path:** an unpatched critical vulnerability blocks new installs within 3 days.
- **Dispute:** the partner contests a finding to the platform lead, who decides within 10 business days. The badge stays during the dispute, except on the security fast path.
- **Agreement clauses:** the revocation right, the partner's support obligation, and a liability disclaimer.

## 8. What the label buys

- A catalog filter, the label, and Glimmerdeck triage. No rank boost until telemetry criteria exist.
- No fee to partners, so no refund rule.
- Co-marketing slots stay in the partner program, not the badge.

## 9. Transition (a program already runs)

1. Publish the support sentence on every Certified listing now. It costs nothing and removes the silent promise first.
2. Any badge granted without kit evidence reverts to Partner-maintained on a published date, with a re-earn deadline of one release cycle.
3. One sentence for buyers on affected listings: "Certified means tested against Glimmerdeck's public kit. Support comes from the partner, with Glimmerdeck triage."

## 10. KPIs

- **Tickets misrouted to Glimmerdeck for partner-owned connectors.** Baseline is today's 30%. Set the target after two quarters of data.
- Certified versus non-certified production success rate. No gap means the criteria measure nothing.
- Partner first-response time, and time from submission to label.
- Renewal lapses per platform release, and decertifications per quarter by rung.

Review date: 2 quarters after launch. Revisit the joint SLA only if Certified connectors move into a paid plan.

## 11. Gate check

| Gate | Pass | Evidence |
|---|---|---|
| Go/no-go recorded | Pass, with partner share unverified | Section 1 |
| Every criterion has all five fields | Pass | Section 4 |
| Every tier has one support sentence | Pass | Section 3 |
| Every badge names kit, platform and connector pins | Pass | Section 6 |
| Every rung has trigger, owner, notice, customer action | Pass | Section 7 |

## What to tell the head of partnerships

The badge gains value from what it proves, not from a support promise you cannot fund. "Tested against a public kit, kept current, with Glimmerdeck triage" is a claim you can keep. "Fully supported" is not, because the partner's code is outside your control.

## Next step

Decide whether Glimmerdeck built the connectors buyers use most. Partner installs under about a fifth of the total fail the go/no-go gate. If you tell me the partner share, whether per-connector telemetry exists, and whether the program is already live, I will rerun this with real numbers.