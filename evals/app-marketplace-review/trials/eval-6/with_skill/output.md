**Reject the one-line rule.** Use the policy below. Two things could change it: your assumptions (next paragraph) and the SBOM dates (end of Part 2).

I skipped the skill's interview because you asked for a single deliverable. Assumptions:
- Listed apps reach read-write business records.
- Updates auto-propagate to installed tenants.
- You have no EU-specific obligations.
- There is no regulated data.

If the XSS app only reads metadata, drop its severity one level. If you serve EU business users, have counsel check statement-of-reasons and notice duties for suspensions and delistings.

## Why "delisted immediately" fails

- **Delisting protects no one already exposed.** It stops new installs. The 900 existing installs keep running the vulnerable app. Only a kill switch or token revocation protects them, and that is a different, costlier rung.
- **It has no rung behind it.** There is no owner, no notice, no evidence standard and no severity. A low-severity finding gets the same penalty as active exploitation. The skill calls that a preference, not a policy.
- **It punishes disclosure.** A publisher who fixes a Medium in two days is treated like one who goes silent. Publishers will stop reporting their own findings.
- **It keeps the head of security's real goal.** Some cases do warrant immediate action. Critical and actively exploited findings suspend new installs the same day (see the ladder).

## Part 1: Vulnerability enforcement policy

**Definitions**
- **Confirmed:** Marketplace Security reproduced the finding, or accepted the reporter's proof and the publisher did not dispute it within 3 business days.
- **Severity:** Marketplace Security assigns it at confirmation, based on the highest data grant the app holds.

| Severity | Meaning | Acknowledge | Fix or mitigation shipped |
|---|---|---|---|
| Critical | Active exploitation, cross-customer access, or exposed credentials | 1 business day | 72 hours |
| High | Exploitable flaw reaching customer data within the app's grant (includes stored XSS in an app with data scopes) | 3 business days | 14 days |
| Medium | Exploitable with limited impact | 5 business days | 45 days |
| Low | Hardening gap, no direct exploit path | 10 business days | 90 days |

Each deadline starts when the repro or confirmed finding reaches the publisher's security contact of record. The SLA values are defaults. Adjust them to your reviewer capacity.

**Enforcement ladder.** Every rung needs an owner, a written notice to the publisher, and the evidence that fires it.

| Rung | Action | Fires when | Owner | Notice to publisher |
|---|---|---|---|---|
| 1 | Finding raised | Confirmation | Marketplace Security | Same day, with severity and deadlines |
| 2 | Remediation SLA running | Rung 1 sent | Marketplace Security | Reminder at 50% of the deadline |
| 3 | Listing hidden (search and browse only, installs untouched, reversible) | Critical: no acknowledgement in 1 business day. High: no acknowledgement in 3 business days. Any severity: SLA missed. | Marketplace Security | 24 hours' written warning, except Critical |
| 4 | New installs suspended | Critical: at confirmation. High: still silent 3 business days after rung 3. Medium or Low: SLA missed by 14 days. | Head of Security | Same day |
| 5 | Kill switch (tokens revoked, app disabled for tenants) | Critical: no mitigation at 72 hours, or exploitation seen. High: no fix 7 days after the fix deadline. | Head of Security, with a named second approver | Customers get 72 hours' notice first, unless exploitation is active |
| 6 | Delisting, with notification to affected customers | Kill switch active 30 days with no fix, publisher unreachable, or bad faith shown | Head of Security | Written statement of reasons |

Rules that apply across rungs:
- Customer notices state the risk and the action to take. They never include exploit details.
- Reinstatement needs a verified fix and a Marketplace Security re-test.
- A publisher who ignores two or more findings gets partner-level consequences, separate from single-app action.
- Every partner must keep a security contact on file.
- Researchers get a status update at each rung. Ask the reporter for their disclosure deadline now. 90 days is a common convention, but I could not check what this researcher expects.

**Your XSS case, using this ladder**
1. **Today:** reproduce the stored XSS yourself, or get the researcher's repro. Rate it High.
2. **Today:** send the repro to the publisher's security contact with the High deadlines and the consequences in writing. The nine days of silence only count against the publisher if the repro already reached them. If the publisher asked for a repro and nobody sent it, the delay is yours.
3. **Today, if the repro was delivered:** hide the listing (rung 3).
4. **Three business days later, if still silent:** suspend new installs and send the customer advisory (rung 4).
5. **Fix deadline plus 7 days with no fix:** kill switch or disable the vulnerable surface (rung 5), after 72 hours' customer notice.
6. **Throughout:** keep the researcher informed.

## Part 2: SBOM enforcement policy

**Date problem.** Announcing in two weeks puts the announcement on about 2026-10-17, a Saturday, so plan for Monday 2026-10-19. 1 November 2026 is a Sunday, so use Monday 2026-11-02. That leaves a 14-day runway. The skill's benchmark (Atlassian) is at least six months before a new requirement applies to listed apps. A 14-day cutoff for 300 listed apps would produce mass non-compliance or a flood of exemptions.

**Recommended split.** Enforcement starts 2026-11-02 as you want. Consequences for existing apps arrive on a runway.

| Date | Applies to | What happens |
|---|---|---|
| 2026-10-19 | All | Announce. Publish the SBOM spec, a pre-check validator and a CI recipe. |
| 2026-11-02 | New submissions and major versions | Hard gate. An SBOM is part of completeness, and a missing or invalid one fails review with the policy cited. |
| 2026-11-02 | The 300 listed apps | Tracking starts. Each app shows its SBOM status in the publisher dashboard. A finding is raised only if an app's next update fails the gate. |
| 2027-02-01 and 2027-04-01 | Listed apps without an SBOM | Reminders. Contact restricted-scope and write-scope apps first. |
| 2027-05-01 | All listed apps | An SBOM is required for every release, and each app must have one current on file. |

The 2027-05-01 date is about six and a half months after the announcement. If your head of security insists on enforcement for everything on 2026-11-02, the compromise is that the ladder starts then for the 300 apps, but no rung above "finding raised" can fire before 2027-05-01.

**SBOM requirements**
- Machine-readable CycloneDX or SPDX.
- Generated by the publisher's CI for the exact release artifact, with the artifact hash recorded.
- Lists direct and transitive dependencies with versions.
- Attached to every release, so the SBOM travels with the update.

**Automated checks.** No human reviews a passing SBOM.
- Schema valid and non-empty.
- Artifact hash matches the release.
- Component list present.
- Optional, as a stretch goal: compare declared components against a scan of the artifact.

Only SBOMs that fail validation or the artifact match go to humans.

**Re-review trigger.** A release without a valid SBOM does not clear the fast path. Never block a security fix on a missing SBOM. Let the fix ship and raise the SBOM finding in parallel.

**Ladder for SBOM non-compliance after 2027-05-01.** This is a paperwork finding, so the sequence is slower than for vulnerabilities. Existing installs keep working throughout.

| Date | Action |
|---|---|
| 2027-05-01 | Finding raised against each non-compliant app. |
| 2027-05-31 | Listing hidden. |
| 2027-06-30 | New installs suspended. |
| 2027-08-01 | Delisting, with customer notice. |

There is no kill switch for a missing SBOM. Apps with an unreachable security contact skip straight to rung 3. Owner for all rungs: Marketplace Security, with a monthly report to the Head of Security. Evidence: failed automated check plus the dated notices.

**Why bother.** With 300 SBOMs on file, a new CVE becomes one query across all listed apps. That query feeds rung 1 of Part 1 automatically. It would not have caught your stored XSS, which is application code and not a dependency.

**Capacity.** Salesforce's own estimate is that roughly half of first submissions fail a strict gate. If that carries over, expect on the order of 150 of your 300 apps to need a second pass. That figure is an extrapolation from a different gate, so measure your own first-pass rate in the first month.

## Check against the skill's four gates
1. Escalation triggers a developer can self-assess: the severity table and the SBOM validator both qualify.
2. "Minor update" defined objectively: a valid SBOM is now one more condition for the fast path. Keep the existing list of no new scopes, no new endpoints, no data-handling change, no payment-model change and no new app type.
3. Every rung has an owner, a notice period and its firing evidence: both ladders do.
4. Publish channel: this policy does not cover phishing-resistant publisher 2FA, short-lived tokens or the 24 to 48 hour propagation hold. You need all of them, and the propagation hold is mandatory because updates auto-propagate.

**Next:** confirm today whether the researcher's repro ever reached the publisher.