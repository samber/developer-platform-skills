# Ferrowell connector certification charter, v1 draft, 2026-10-30

I ran the connector-certification-program skill. You asked for the whole charter in one pass, so the interview answers below are marked asked or assumed. Please correct the assumed ones, because several thresholds depend on them.

**Short version for your VP:** neither proposal fixes what went wrong.

- The v5 breakage came from a badge that never re-tested against a new platform version. Usage had nothing to do with it.
- The tickets came from customers reading "Ferrowell Verified" as "Ferrowell supports it". No criterion addresses that, and a written support sentence does.
- The 1,000 MAU gate blocks the tier customers need in order to start using a connector. Mandatory Verified shrinks the catalog to what your reviewers can process.

## 0. Inputs

| Interview question | Answer | Asked or assumed |
|---|---|---|
| 1. What partners build | (a) data connectors on an iPaaS catalog | Assumed from "iPaaS" and "connectors" |
| 2. Who builds what buyers install | 85 partner-built connectors, about 50% of installs | Asked (your message) |
| 3. Who reads the badge | (a) buyers, plus (c) your support team routing tickets. Customers opened tickets citing it. | Assumed from the tickets. Is procurement asking for it too? |
| 4. Per-connector production telemetry | Unknown. Treated as "not yet with a platform-vs-connector fault split". | Assumed |
| 5. Platform change cadence | Ships versioned APIs (v5 last month). Cadence unknown. | Partly asked |
| 6. Reviewer and engineering capacity | Solutions team does review calls today. Hours unknown. Kit build treated as affordable. | Assumed |
| 7. Existing tier | (c) running, revisiting after two broken Verified connectors | Asked |
| 8. Deadline | Open-ended | Assumed |
| 9. One-off or compounding | Compounding | Assumed |
| 10. Effort ceiling | Moderate: one kit, one quarterly-style evaluation cadence | Assumed |
| 11. Partner fee | None | Assumed. A fee would need a refund rule on revocation. |

**Re-ranking**

- Q7 (c) adds the transition section (§9).
- Q4 unknown makes the operator-run kit the day-one evidence. Telemetry criteria go live once attribution and the fault split exist.
- Q5 (versioned API) means badges pin to the API version and the date of the last matrix run.
- Q9 compounding keeps the kit as the default and rejects manual review per release.

## 0b. Proposals evaluated

| Proposal (who) | Verdict | Rule it meets or breaks |
|---|---|---|
| Require 1,000 MAU before GA (VP) | **Rejected as stated. Replaced by usage-scaled evidence.** | Breaks "never put a usage minimum on the tier that unlocks production use". Partners cannot gather users on a connector customers are told not to deploy. Power Platform's publishers called its usage recommendation a catch-22. MAU measures popularity, not compatibility with API v5. |
| Make Verified mandatory for every connector (VP) | **Rejected. Replaced by a mandatory listing bar.** | Breaks "certification as admission". 85 connectors through a reviewer-limited process throttles the catalog. Listing and certification stay separate bars. |
| Gold partners get Verified automatically (current practice) | **Rejected. Badges revert.** | Breaks "tiers keyed on partner commercial status are deleted". It certifies the partner relationship, not the connector. |
| Verified granted after a one-time review call (current practice) | **Changed to kit evidence, pinned and renewed on triggers.** | Breaks "certified once, trusted forever". The badge certified the platform version it was earned on, and nothing after it. |

If the VP wants a usage signal, the charter allows it in one place only: the regression layer is required above a usage threshold (§3). It scales the evidence and never gates GA.

## 1. Go/no-go

- **Outside reader:** customers reading the catalog chip and filing tickets on it (assumed). Holds.
- **Partner share:** about 50% of installs are partner-built. Holds.
- **Evidence:** the operator-run conformance kit is affordable. Telemetry is not yet, because there is no fault split. Holds on the kit alone.
- **Decision:** run the certification program, kit-first. Add telemetry criteria when per-connector attribution and the fault split exist (target: set at the §10 review).

## 2. Labels

| Label | Meaning to a buyer | Maintained by | Earned by |
|---|---|---|---|
| Ferrowell-maintained | Built and supported by Ferrowell | Ferrowell | Ownership |
| Verified | A partner-built connector that passes Ferrowell's test kit for the current API version | Partner | §3 criteria |
| Partner-maintained | Listed, built by a partner, not tested by Ferrowell | Partner | Listing bar |
| Community | Built by individuals, no commitments | Community | Listing bar |

**Label name:** drop "Ferrowell" from the chip and call it "Verified". A label carrying the operator's brand reads as an operator support promise. If you keep "Ferrowell Verified", the support sentence from §5 must sit directly next to it.

**Listing bar (mandatory for every connector, kept apart from labels):**

- manifest passes the kit's static layer
- an ownership label is set
- a support contact is published
- a named security contact exists
- no secrets in fixtures

A connector that fails the listing bar is not listed. Everything else in this charter is optional and earned.

## 3. Criteria (Verified)

| Metric | Threshold | Window | Minimum volume | Measured by | Label |
|---|---|---|---|---|---|
| Contract layer pass | all required tests pass, >90% overall | per connector release | not applicable | Ferrowell CI | Verified |
| Platform-version currency | contract layer passes on every supported API version (v4 and v5 now) | per platform release | not applicable | Ferrowell CI | Verified |
| Regression layer pass (usage-scaled) | no unexplained output diff vs the current version | per release | required only above the usage threshold | Ferrowell CI | Verified, high-usage connectors only |
| Production success rate | ≥95% of syncs | trailing 28 days | ≥200 syncs | operator telemetry, platform-outage errors excluded | Verified, activates with the fault split |
| Support response | first response ≤3 business days | trailing quarter | ≥5 tickets | Ferrowell ticketing | Verified |
| Release cadence | one release, or a signed no-change attestation | 6 months | not applicable | operator registry | Verified |
| Security contact | named and reachable | annual check | not applicable | Ferrowell | Verified |

- **Low volume never fails a criterion.** A connector whose telemetry rows all read "insufficient data" keeps Verified on kit evidence alone. Its listing says "kit-verified, insufficient production data".
- **Baseline:** all thresholds are starting values borrowed from published programs (≥95% success, 3-business-day response). Recalibrate after one quarter against what your best existing connectors achieve.
- **Usage threshold for the regression layer:** starting value is the top 20 connectors by active installs. Replace it with a number from your install distribution before launch.

## 4. Kit

- **Version:** 1.0.0, semver, changelog published with the kit.
- **Layers run:**
  - static, on every submission
  - contract, on every connector release, run against a sandbox
  - regression, above the usage threshold
  - platform matrix, re-running the contract layer on every supported API version
- **Contract tests:** generated from each connector's declared spec, not from partner-written tests.
- **Required tests:** auth, discover, read, write, pagination, error mapping, rate limits, state and checkpointing. Overall pass bar is 90%, and required tests must pass or be acknowledged as unsupported on the listing.
- **Partner self-test:** partners run the same kit locally. Submission is blocked until required tests pass, with results no older than 48 hours.
- **Exemptions:** for operations that cannot be generically tested (destructive writes, paid actions). Each needs a reason, a replacement check, and sign-off by the partner ecosystem lead. The count is published with the results.
- **Results:** published per connector.

## 5. Support routing

| Label | First contact | Who fixes | Response commitment | Sentence shown on listing |
|---|---|---|---|---|
| Ferrowell-maintained | Ferrowell | Ferrowell | per your plan | "Built and supported by Ferrowell." |
| Verified | Ferrowell triages, isolates, routes | Partner | Ferrowell first reply ≤1 business day (starting value); partner ≤3 business days | "Built and maintained by <partner>. Ferrowell tests it against each API version and will take your first call to find the cause. Fixes and ongoing support come from <partner>." |
| Partner-maintained | Partner | Partner | none | "Supported by <partner>, contact <channel>. Not tested or supported by Ferrowell." |
| Community | Community | Community | none | "Community-built. No support from Ferrowell or a partner." |

## 6. Renewal

- **Pin:** each badge records kit v1.x, API version (v5) with the date of the last platform-matrix run, and the lowest connector version it covers. Older connector versions show the Partner-maintained label.
- **Triggers that re-run the kit:**
  - an API release that changes the contract connectors depend on
  - a new kit major version
  - a connector release (full contract layer for behavior changes, a static check for cosmetic ones)
  - new data scopes or endpoints
- **Telemetry re-evaluation:** first business day of each month over a trailing 28 days. Each partner sees its own values on a dashboard the same day. This starts when telemetry criteria go live.
- **Kit for the next contract-changing API release (v6):** ships to partners at API beta, with at least 60 days (starting value) before general availability. The v5 failure was this step missing.
- **Calendar floor:** annual, for security contact and support contact only.
- **Notice before a new criterion applies to existing Verified connectors:** 6 months. Re-running existing criteria on a new API version is renewal and earns no extra runway beyond the beta lead time.

## 7. Decertification ladder

| Rung | Trigger | Owner | Notice | Customer action |
|---|---|---|---|---|
| Warning | one criterion fails at one monthly evaluation | partner ecosystem lead | partner emailed same day; remediation runs to the next evaluation | none |
| Badge suspended | two consecutive failed evaluations | partner ecosystem lead | 14 days | none; label reverts to Partner-maintained, listing and installs untouched |
| New installs blocked | suspended >90 days, or no release and no support response for 6 months, or partner exit | head of partnerships | 30 days | affected customers notified |
| Existing installs disabled | connector remains abandoned or unsafe after rung 3 | VP-level approval | 60 days | customers notified, migration path published before the date |

- **Ladder clock:** failures counted at monthly evaluations, each reading a trailing 28 days.
- **Adoption before blocking:** an abandoned connector above the usage threshold is offered to a new maintainer, or to Ferrowell, before rung 3.
- **Dispute route:** the head of partnerships decides within 10 business days. The badge stays during a dispute, except on the security fast path.
- **Security fast path:** an unpatched critical vulnerability goes to rung 3 within 3 days.
- **Agreement clauses to add or confirm with legal:** Ferrowell's right to revoke, the partner's support obligation, where and for which versions the badge may appear, and a liability disclaimer.

## 8. What the label buys

- A catalog filter and a listing chip.
- Operator triage for Verified connectors.
- No search-rank weight until two quarters of telemetry exist.
- No co-marketing slots. Those belong to the partner program, so Gold status keeps its commercial benefits and loses its badge shortcut.
- **Fee to partner:** none (assumed).
- **Badge use:** only on listings and partner materials for connector versions inside the pin. After suspension the partner may not claim Verified.

## 9. Transition from the current program

| Old label | New label | Re-earn deadline | Buyer-facing sentence |
|---|---|---|---|
| Verified via Gold auto-grant | Partner-maintained | kit GA + 120 days | "Verification now requires passing Ferrowell's test kit for the current API version." |
| Verified via one-time review call | Partner-maintained | kit GA + 120 days | same |
| The two connectors that broke on v5 | Partner-maintained now, with a listing note until they pass | run the kit first; target the kit beta window | "This connector is being re-tested against API v5." |

**Sequence**

1. **Day 0:** announce the new charter, the support sentences and the revert date. Put the sentences on all 85 listings immediately. This alone should stop most of the misrouted tickets.
2. **Day 0 to 30:** kit in beta, open to all partners. Run the contract layer against v5 for every connector, so you learn how many other Verified connectors are broken.
3. **Kit GA:** partners re-earn within 120 days (one release cycle).
4. **Kit GA + 120 days:** any unpassed old badge becomes Partner-maintained.

Gold partners get the same notice and the same kit access as everyone else. Do not grandfather them: a grandfather clause keeps the old meaning of the badge alive. If their sensitivity is the worry, lengthen the notice instead.

## 10. KPIs and review date

- Share of installs on Verified connectors.
- Verified vs non-Verified production success rate once telemetry is live. No gap means the criteria measure nothing.
- Time from submission to label.
- Renewal lapse rate per API release.
- Tickets misrouted to Ferrowell for partner-owned connectors. This is the headline KPI for your VP's original complaint.
- Decertifications per quarter, by rung.
- **Review date:** 2027-01-31. Recalibrate thresholds, decide whether telemetry criteria are live, and re-check the usage threshold.

## 11. Gate check

| Gate | Pass / fail | Evidence in this charter |
|---|---|---|
| 1. Go/no-go recorded with each condition | Pass | §1 |
| 2. Every criterion has metric, threshold, window, minimum volume, measurer | Pass | §3 |
| 3. Every tier carries one support sentence | Pass | §5 |
| 4. Every badge names kit version, platform or contract version, lowest connector version | Pass | §6 pin |
| 5. Every rung names trigger, owner, notice, customer action | Pass | §7 |

**Open items for you**

- Confirm the assumed answers in §0, especially Q3 (do procurement teams ask for the badge?), Q4 (what telemetry exists), Q6 (reviewer hours) and Q11 (no fee).
- Decide the label name: "Verified", or "Ferrowell Verified" with the support sentence next to it.
- Replace the three starting values with real numbers: the usage threshold, the notice periods and the 1-business-day triage reply.
- Have legal review the agreement clauses in §7 and the badge-use terms in §8.

I did not write anything to memory. Tell me whether these decisions belong in CLAUDE.md, AGENTS.md or memory, and I'll record them there.