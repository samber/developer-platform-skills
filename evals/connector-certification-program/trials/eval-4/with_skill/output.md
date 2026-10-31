**Next action: before anything else, send Brackenfield a 48-hour written notice and open the customer-notification draft. Details are in the "Today" list below.**

# Brackenfield ERP connector: what to do today

## The call

Your boss is half right. The instinct is correct, but "delete and disable everywhere today" skips the ladder rung that protects customers.

- **Today: yes.** Suspend the Certified badge, block new installs, and pull the connector from catalog search. This is rung 3 on the security fast path. Skill rule: an unpatched vulnerability skips to rung 3 in days, not weeks. Confluent and Tableau both do this.
- **Today: no.** Do not disable the 340 existing installs yet. Rung 4 requires customer notification and a published migration path before the date. A silent kill mid-payroll hurts customers more than a short, announced window.
- **Disabling today is justified in one case.** That case is evidence of active exploitation, or credentials leaving the customer's tenant to a third party. In that case disable now and handle payroll customers by phone. Answer the two questions below first.

Two facts push toward urgency:

- **The leak is live for 340 customers today.** Delisting does not fix it. Tell customers to rotate credentials now, whatever the removal date is.
- **Five weeks is already past the fast path.** You had no published ladder, so the delay is not a violation of your own policy. Say so plainly, and do not blame Brackenfield alone in customer messaging.

### Two questions to answer first (about 30 minutes, security lead)

1. **Where do the credentials leak?** Possible places are logs, URLs, error payloads, or a third party. How easily can someone exploit it?
2. **Is there any sign of abuse?** Check your own logs.

Decision rule:

- **Leak is local and unexploited:** use the 14-day disable window below.
- **Leak reaches third parties, or abuse is seen:** disable now. Notify payroll customers first and give them a manual-run fallback.

### Today (numbered; roughly 3 to 4 hours of work in total)

1. **Send Brackenfield a formal notice.** Cite the revocation and support clauses in your agreement; have counsel check them. Demand a fix or a named new maintainer within 48 hours. Say that the badge is suspended and new installs are blocked now regardless of their answer.
2. **Suspend the badge and block new installs.** The listing label reverts to "Partner-maintained", then to a "Delisted: security issue" notice. Existing installs keep running.
3. **Notify all 340 customers today.** Mention no exploit detail. Say what to do: rotate the ERP credentials the connector holds, and review ERP access logs. Give the disable date and the migration path.
4. **Flag payroll customers.** Query which installs run payroll syncs. Give each a named contact and a pay-cycle-aware plan.
5. **Offer adoption in parallel.** Put 340 installs above your usage threshold, so offer the connector to a new maintainer or to your own team. Do not let this delay steps 1 to 3.

### Customer notice (draft; one idea per sentence)

> The Brackenfield ERP connector has an unpatched vulnerability that can expose stored credentials. The maintainer has not responded. **Today, rotate the ERP credentials this connector uses.** We have blocked new installs. Existing installs keep running until **<date, 14 days out>**, after which we will disable them. Migration options: <link>. Payroll customers: contact <name>.

### Timeline

- **Day 0:** steps 1 to 5 above.
- **Day 2:** Brackenfield deadline. Record their response, or the silence.
- **Day 7:** reminder to customers who have not migrated.
- **Day 14:** disable existing installs. Extend only per customer, with a written risk acceptance from them.

Why 14 days: it covers at least one bi-weekly payroll cycle. It does not cover a monthly cycle. If payroll customers run monthly, move this date; that is your decision, not mine.

## Policy so this is not a scramble next time

I wrote this charter from the skill without the interview. I labeled every assumed answer. Correct them and the thresholds change.

### 0. Inputs

| Question | Answer | Status |
|---|---|---|
| Who reads the badge | Buyers and enterprise procurement | **Assumed** |
| Partner share of installs | At least a fifth; Brackenfield alone has 340 installs | **Partly known** |
| Per-connector telemetry | Sync success per connector, with fault split | **Assumed** (to confirm) |
| Existing tier | Running; "Certified" has no re-test and no ladder | **Inferred** from this incident |
| Deadline | Fast-path text today; kit within a quarter | **Assumed** |
| Fee to partner | None | **Assumed** |

Re-ranking: a running program with a broken certified connector (7c) adds the transition section. A security incident promotes the fast path, which needs only policy text and no tooling.

### 0b. Proposals evaluated

| Proposal | Verdict | Rule |
|---|---|---|
| "Delete from catalog today" (boss) | **Changed**: block new installs and delist; keep the record and the notice | Ladder rung 3; separate badge from installs |
| "Disable everywhere today" (boss) | **Changed**: disable after notice and migration path; today only if exploitation is shown | Ladder rung 4 needs notice and migration path first |
| Wait for Brackenfield to answer | **Rejected** | Fast path: days, not weeks; five weeks of silence is already abandonment |

### 1. Go/no-go

- Outside reader: buyers and procurement. Holds.
- Partner share: holds, per the 340 installs.
- Evidence: kit holds; telemetry holds only if the platform-vs-connector fault split exists. Start on the kit.
- **Decision: run a certification program.**

### 2. Labels

| Label | Meaning to a buyer | Maintained by | Earned by |
|---|---|---|---|
| Orrisdale-maintained | Built and supported by Orrisdale | Orrisdale | Built by Orrisdale |
| Partner-maintained | Built by a partner, not certified | Partner | Listing bar |
| Certified | Partner-built; passes the kit and live criteria | Partner | Section 3 |
| Community | Everyone else | Community | Listing bar |

Listing bar, kept apart from the labels: a named security contact, a support channel, no secrets in fixtures, and declared scopes.

Do not use an "Orrisdale Verified" name. A label with your brand reads as your support promise. The listing carries the support sentence in section 5.

### 3. Criteria (Certified)

| Metric | Threshold | Window | Minimum volume | Measured by |
|---|---|---|---|---|
| Contract layer | All required tests pass; over 90% overall | Per release | n/a | Operator CI |
| Production success rate | 95% or higher | Trailing 28 days | 200 runs or more | Operator telemetry |
| Release cadence | One release, or a signed no-change attestation | 6 months | n/a | Operator registry |
| Support response | First response within 3 business days | Trailing quarter | 5 tickets or more | Operator ticketing |
| Security contact | Named and reachable | Annual check | n/a | Operator |
| Open critical vulnerability | None unpatched past the fast-path period | Continuous | n/a | Operator security desk |

Baseline: all numbers are starting values. Recalibrate after one quarter, against your best existing connectors.

Low telemetry volume never fails a criterion. The listing reads "kit-verified, insufficient production data".

### 4. Kit

- Version: semver, with a changelog. Each badge records its kit version.
- Layers: static, contract, regression above the usage threshold, platform matrix.
- Required tests are split from optional tests. A single percentage lets partners skip the tests that matter.
- Partners run the same kit locally. Submission is blocked until required tests pass.
- Exemptions need a named reason and a reviewer sign-off, and the count is published.

### 5. Support routing

| Label | First contact | Who fixes | Commitment | Sentence on listing |
|---|---|---|---|---|
| Certified | Orrisdale | Partner | Partner fix within a stated time | "Orrisdale takes your first call and routes it. The partner fixes the connector." |
| Partner-maintained | Partner | Partner | Partner's own | "Supported by <partner>, contact <channel>." |
| Community | Community | Community | None | "Community-supported. No SLA." |

### 6. Renewal

- Pin each badge to the kit version, the platform or contract version, and the lowest connector version covered.
- Triggers: a platform release that changes the contract, a new kit major, a connector release, and new scopes or endpoints.
- Telemetry is evaluated on a fixed published date. Partners see their own values the same day.
- The kit for a contract-changing release ships at platform beta.
- Calendar floor: annual, for the security contact only.
- Notice before new criteria apply to already-certified connectors: 6 months.

### 7. Decertification ladder

| Rung | Trigger | Owner | Notice | Customer action |
|---|---|---|---|---|
| Warning | One failed scheduled evaluation | Partner program | Remediation until the next evaluation | None |
| Badge suspended | Two consecutive failed evaluations | Partner program | 14 days | None |
| New installs blocked | Suspended over 60 days; or no release and no support response for 6 months; or partner exit; or **security fast path** | Head of platform | **3 days on fast path** | Notified |
| Existing installs disabled | Rung 3 reached and no fix or adopter | Head of platform with CISO | **14 days on security fast path; 60 days otherwise.** Migration path published first | Notified; migration path; named contact for payroll or other critical flows |

- Ladder clock: scheduled evaluations monthly, each reading a trailing 28 days.
- Dispute: the partner contests a finding with the head of platform, decision within 5 business days. The badge stays during the dispute, except on the security fast path.
- **Security fast path:** an unpatched vulnerability reported to the partner and unfixed after 14 days skips straight to rung 3, which takes effect within 3 days. A critical vulnerability gets 7 days.
- Adoption before blocking: offer an abandoned connector above the usage threshold to a new maintainer, or to Orrisdale. Skip this wait on the fast path; run it in parallel.
- **Clock owner:** the security desk starts the clock the day a report is accepted. This is the gap that cost you five weeks.

### 8. What the label buys

- The label, a catalog filter, and operator triage for Certified.
- No search-rank weight and no co-marketing slots. Partner-program benefits stay out of the badge.
- Fee: none, so no refund rule.
- Badge use: only on listed connector versions; the partner removes it on suspension.
- Agreement clauses to add: a right to revoke, a support obligation, a vulnerability-fix deadline, a notification duty, and a liability disclaimer. Counsel should check every one.

### 9. Transition (running program)

| Old label | New label | Re-earn deadline | Buyer-facing sentence |
|---|---|---|---|
| Certified (no evidence) | Partner-maintained | 2 release cycles | "Certification now requires live evidence. This connector is being re-tested." |
| Certified (passes the kit) | Certified | n/a | None |

Revoke badges earned without the new evidence, even for important partners. Lengthen the notice instead of grandfathering.

### 10. KPIs and review date

- Share of installs on Certified connectors.
- Certified vs non-certified production success rate. No gap means the criteria measure nothing.
- Time from vulnerability report to rung 3. Target: 3 days.
- Decertifications per quarter, by rung.
- Tickets misrouted to Orrisdale for partner-owned connectors.
- Review date: one quarter after launch.

### 11. Gate check

| Gate | Pass / fail | Evidence |
|---|---|---|
| Go/no-go recorded with each condition | Pass | Section 1 |
| Every criterion has metric, threshold, window, volume, measurer | Pass | Section 3 |
| Every tier has one support sentence | Pass | Section 5 |
| Every badge names kit, platform or contract, and lowest connector version | Pass | Section 6 |
| Every rung has trigger, owner, notice, customer action | Pass | Section 7 |

## What to confirm before you publish

1. The agreement terms with Brackenfield. I have not read them, and the revocation right depends on them.
2. The nature of the leak and any exploitation evidence. This decides today's disable-or-wait call.
3. Your pay-cycle map for payroll customers. This sets the disable date.

**Next: answer the two security questions, then send the Brackenfield notice.**