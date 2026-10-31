# Tidewick connector certification charter, draft v0.1, 2026-10-30

I read the skill and its three references. I made this one pass without an interview, so every answer I assumed is labelled in section 0.

Of your seven proposals, I rejected two, changed four, and adopted none as written. The details are in section 0b.

## 0. Inputs

| Question | Answer | Status |
|---|---|---|
| 1. What partners build | Source connectors on an analytics platform (a) | Stated: "partner-built source integrations" |
| 2. Install share | About 200 partner connectors. Share of installs unknown. | **Assumed:** at least a fifth of installs, or some top-installed connectors |
| 3. Who reads the badge | Buyers and enterprise procurement (a/b) | **Assumed** |
| 4. Per-connector measurement | Per-call telemetry with error codes, attributed per connector | Stated. The platform-vs-connector fault split is **unverified**. |
| 5. Platform changes and versioning | Unknown. I pin to the API/contract version. | **Assumed** |
| 6. Reviewer and engineering capacity | Unknown. I assume no manual review rung. | **Assumed** |
| 7. Existing tier | None. "New tier." | Stated, so there is no transition section |
| 8. Deadline | "So we can launch" implies a date. | **Assumed:** hard date. That promotes policy text, a kit, and telemetry criteria that switch on later. |
| 9. One-off or compounding | Compounding asset | **Assumed** |
| 10. Effort ceiling | Unknown | **Assumed:** low |
| 11. Partner fee | None | **Assumed** |

**Re-ranking:**
- **Hard date (8):** launch with policy text plus the kit. Telemetry criteria go live once the fault split is proven.
- **Low effort ceiling (10):** I deleted manual code review as a rung.
- **Fault split (4):** your error codes are the main asset. The split must exist before any telemetry criterion can fail a partner.

## 0b. Proposals evaluated

| # | Proposal | Verdict | Rule it meets or breaks |
|---|---|---|---|
| 1 | High-quality, well-structured code | **Rejected as written, replaced** | It is not measurable. "High quality" has no threshold, window, or measurer. A kit's contract and static layers replace it with pass/fail tests on behavior. |
| 2 | Responsive partner support | **Changed** | The idea is good but has no number. It becomes first response within 3 business days, over a trailing quarter, with at least 5 tickets, measured from your ticketing system. |
| 3 | Well documented | **Changed** | I made it a checkable list that the kit's static layer enforces: setup steps, auth scopes, field list, error-code reference, changelog. "Well" is not testable. |
| 4 | 99% uptime | **Changed** | A source connector is not a hosted service, so "uptime" is undefined for it. It becomes production success rate, with platform-caused errors excluded. 99% is a borrowed number, so I label it a starting value (see section 3). |
| 5 | Premier partner level | **Rejected** | A commercial criterion. It certifies the partner relationship, not the connector. Partner-program level belongs to the partner program and stays off the connector label. |
| 6 | At least 3 joint enterprise customers | **Rejected** | It is commercial. It is also a usage catch-22: a connector buyers are told not to deploy cannot gather customers. Real usage is handled by a minimum volume on the telemetry criteria. |
| 7 | Passes our review | **Changed** | Manual review is the costliest and slowest evidence. The default is an operator-run conformance kit. Manual review is kept only for restricted data scopes and handed to the marketplace-review skill. |

Criteria 5 and 6 together make a partner-company tier. Metal ladders, and tiers keyed on commercial status, are deleted in this skill's design. A badge built on "Premier plus 3 joint customers" reads as co-marketing.

## 1. Go/no-go

- **Outside reader:** buyers and procurement. Holds (assumed).
- **Partner share:** about 200 partner connectors. Holds if they carry at least a fifth of installs. **Verify this first.** If operator-built connectors carry nearly all installs, certifying partners is the wrong program.
- **Evidence:** conditional.
  - The kit is affordable but does not exist yet. You must build it, and the contract layer needs a sandbox.
  - Telemetry counts only once the platform-vs-connector fault split exists. Until then it is "not yet affordable".
- **Decision:** run the program, **starting on the kit**. Telemetry criteria are published now but enforced only after the fault-split check in section 3 passes. If the install-share check fails, ship ownership labels only and set a re-check date.

## 2. Labels

| Label | Meaning to a buyer | Maintained by | Earned by |
|---|---|---|---|
| Tidewick-maintained | Built and supported by Tidewick | Tidewick | n/a |
| Partner-maintained | Built by a partner, not certified | Partner | Listing bar |
| **Tidewick Certified** | Partner-built, passed a published test kit and meets published production criteria | Partner | Section 3 criteria |
| Community | Everyone else | Community | Listing bar |

**Listing bar** (kept apart from certification, so certification is never required to list):
- A valid manifest.
- A named support contact.
- No secrets in fixtures.
- The partner agreement is signed.

## 3. Criteria (Certified)

| Metric | Threshold | Window | Minimum volume | Measured by |
|---|---|---|---|---|
| Contract layer pass | All required tests pass; >90% overall | Per connector release | n/a | Operator CI kit |
| Platform-version currency | Passes the matrix on every supported version | Per platform release | n/a | Operator CI kit |
| Documentation completeness | Setup, auth scopes, field list, error-code reference and changelog all present | Per release | n/a | Kit static layer |
| Production success rate | ≥95% of calls (**starting value**) | Trailing 28 days | ≥200 calls | Operator telemetry; platform-attributed errors excluded |
| Support first response | ≤3 business days | Trailing quarter | ≥5 tickets | Operator ticketing |
| Release cadence | ≥1 release, or a signed no-change attestation | 6 months | n/a | Operator registry |
| Security contact | Named and reachable | Annual check | n/a | Operator |

**Baseline.** Every threshold above except the contract pass bar is a starting value. The 95% and 3-day figures echo another catalog's published bars. Recalibrate them before launch:
1. Compute the trailing-28-day success rate for all ~200 connectors from your telemetry.
2. Set the bar near what your best existing connectors already achieve.
3. If your top connectors already sit at 99%, then 99% is defensible. If they don't, 99% would exclude nearly all your partners.

At 200 calls, 99% allows only 2 failures. That makes a short window noisy, so keep the 28-day window and the volume floor.

**Fault split (a precondition for the success-rate row).** Use your error codes to classify every failure into one of four classes: platform fault, connector fault, source API outage, and customer configuration (expired credentials, revoked access). Only connector faults count against the partner.
- **Decision for you:** my default also excludes source-API outages and customer-config errors. Otherwise partners are blamed for failures they can't fix. Tell me if you disagree.
- **Activation test:** replay a known platform incident and confirm it is excluded from every affected connector's rate. Until that passes, the row reads "informational" and cannot fail anyone.

**Low volume.** A connector below the minimum volume reads "insufficient data" on telemetry rows. It holds the label on kit evidence alone, and the listing says "kit-verified, insufficient production data". Low volume never fails a criterion.

## 4. Kit

- **Version:** semver, starting at 1.0.0, with a changelog at a stable public location.
- **Layers run:**
  - Static on every submission.
  - Contract on every connector release, against a sandbox. Generate these tests from the connector's own manifest, not from partner-written tests.
  - Platform matrix on every contract-changing platform release.
  - Regression only above a usage threshold you set.
- **Required tests:** auth, discover, read, pagination, error mapping, rate-limit handling, and state/checkpointing. Pass bar: all required plus >90% overall.
- **Partner self-test:** partners run the same kit locally. Submission is blocked until required tests pass, and results are valid for 48 hours.
- **Exemptions:** destructive or paid operations may be exempted. Each needs a stated reason and replacement test, a named reviewer sign-off, and a published count.

## 5. Support routing

| Label | First contact | Who fixes | Response commitment | Sentence shown on listing |
|---|---|---|---|---|
| Certified | Tidewick | Partner | First response ≤3 business days; fix time **starting value**, set at launch | "Built and maintained by <partner>. Tidewick takes your first call, finds whether the fault is in the platform or the connector, and routes it. The partner fixes connector faults." |
| Partner-maintained, Community | Partner | Partner | Partner-stated | "Supported by <partner>, contact <channel>. Not supported by Tidewick." |
| Tidewick-maintained | Tidewick | Tidewick | Per your plan's SLA | "Supported by Tidewick." |

The label carries the Tidewick brand, so the support sentence must sit beside it. Buyers otherwise read "Tidewick Certified" as "Tidewick fixes it".

## 6. Renewal

- **Pin:** kit 1.x, Tidewick API/contract version (or release version if you publish one) and the date of the last matrix run, plus the lowest connector version covered. Older connector versions show the ownership label.
- **Triggers:**
  - A platform change to the contract connectors depend on.
  - A new kit major version.
  - A connector release, scaled to the change.
  - New scopes or endpoints.
- **Telemetry re-evaluation:** first business day of each month, over the trailing 28 days. Partners see their own values on a dashboard the same day.
- **Kit for a contract-changing platform release** ships to partners at platform beta, before general availability.
- **Calendar floor:** annual, for the security contact and support contact only.
- **Notice before new criteria apply to already-certified connectors:** 6 months (**starting value**).

## 7. Decertification ladder

| Rung | Trigger | Owner | Notice | Customer action |
|---|---|---|---|---|
| Warning | One failed monthly evaluation | Certification lead | Same day, via dashboard and email | None |
| Badge suspended | Two consecutive failed evaluations | Certification lead | 14 days | None. Listing and installs untouched. |
| New installs blocked | Suspended >90 days, or no release and no support response for 6 months, or the partner exits | Head of partnerships | 30 days | Notified |
| Existing installs disabled | Only after rung 3, with migration path | Head of partnerships | 60 days | Notified, with a migration path published before the date |

- **Ladder clock:** failures are counted at scheduled monthly evaluations, each reading a trailing 28 days.
- **Dispute route:** one route, decided by the certification lead's manager within 10 business days. The badge stays during the dispute, except on the security fast path.
- **Adoption before blocking:** offer an abandoned connector above the usage threshold to a new maintainer, or to Tidewick, before rung 3.
- **Security fast path:** an unpatched critical vulnerability goes straight to rung 3 within 3 days.

All numbers are starting defaults to confirm.

## 8. What the label buys

- A Certified filter in the catalog, a listing chip, and Tidewick triage.
- **No rank boost** until two quarters of telemetry exist. **No co-marketing slots**, which belong to the partner program.
- **Fee to partner:** none (assumed). If that changes, add a refund rule on revocation.
- **Badge use:** the listing and partner materials, for covered connector versions only. After suspension, the partner must stop using the badge.
- **Agreement clauses to add:** a revocation right, the partner's support obligation, where the badge may appear, and a liability disclaimer.

## 9. Transition

None. No tier exists today.

## 10. KPIs and review date

- Share of installs on Certified connectors.
- Certified vs non-certified production success rate. No gap means the criteria measure nothing.
- Time from submission to label.
- Renewal lapses per platform release.
- Tickets misrouted to Tidewick for partner-owned connectors.
- Decertifications per quarter, by rung.
- **Review date:** two quarters after launch.

## 11. Gate check

| Gate | Pass / fail | Evidence |
|---|---|---|
| Go/no-go recorded with each condition | **Pass, conditional** | Section 1. Install share and the fault split are unverified. |
| Every criterion has metric, threshold, window, volume, measurer | Pass | Section 3 |
| Every tier has a support sentence | Pass | Section 5 |
| Every badge names kit, platform/contract and connector versions | Pass | Section 6 |
| Every rung names trigger, owner, notice, customer action | Pass | Section 7 |

## What I need from you before launch

1. **Install share.** What percentage of installs run on partner-built connectors? If it is under a fifth and no top-installed connector is partner-built, switch to ownership labels only.
2. **Fault split.** Can your error codes separate platform faults from connector faults? And do you agree that source outages and customer-config errors are excluded?
3. **Baseline.** Run the 28-day success-rate query across all ~200 connectors and share the distribution. I will then set the 95% bar from your data instead of a borrowed number.
4. **Launch date.** Is it hard? Which of these, in order, ship by then: the kit, the dashboard, or the telemetry rows?
5. **Platform versioning.** Do you publish platform or API versions? If not, I pin to a contract hash.
6. **Reviewer hours.** How many per week? I assumed none for manual review.

Your product team's list was a good start. Criteria 1 to 4 describe real concerns and now have numbers. Criteria 5 and 6 are partner-program rules, so keep them there, off the connector label.