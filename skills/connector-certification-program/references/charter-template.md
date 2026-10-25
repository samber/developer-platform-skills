# Certification charter: template, worked example, negative example

Read when writing the deliverable. Keep every section; write "none" rather than dropping one. Add sections only after section 11. The company in the worked example is fictional.

## Template

```markdown
# <Platform> connector certification charter - v<n>, <date>

## 0. Inputs

| Interview question | Answer | Asked or assumed |

- Re-ranking: <which answer moved which rung, one line each>

## 0b. Proposals evaluated

| Proposal (who) | Verdict: adopted / changed / rejected | Rule it meets or breaks |

## 1. Go/no-go

- Outside reader: <who reads the label> - holds / fails
- Partner share: <share of installs on partner-built connectors> - holds / fails
- Evidence: <kit, telemetry, or both> - holds / fails
- Decision: certification program | ownership labels only, re-check <date>

## 2. Labels

| Label | Meaning to a buyer | Maintained by | Earned by |

- Listing bar (what any connector needs to appear at all, kept apart from labels): <list>

## 3. Criteria

| Metric | Threshold | Window | Minimum volume | Measured by | Label |

- Baseline: <measured value from best existing connectors, or "starting value, recalibrate after <period>">

## 4. Kit

- Version: <semver>, changelog at <location>
- Layers run: static / contract / regression / platform matrix
- Required tests: <list or pointer>; overall pass bar: <n>%
- Partner self-test: <how>; submission blocked until required tests pass: yes / no
- Exemptions: reviewer sign-off by <role>, count published

## 5. Support routing

| Label | First contact | Who fixes | Response commitment | Sentence shown on listing |

## 6. Renewal

- Pin: kit v<x>, platform v<y> (or contract version and last matrix-run date), connector versions >= <z>
- Triggers: <platform contract change, kit major, connector release, new scopes or endpoints>
- Telemetry re-evaluation cadence: <period, published date>; partners see their own values: <where, how often>
- Kit for a contract-changing platform release ships to partners at: <platform beta milestone>
- Calendar floor: <criteria it applies to, or none>
- Notice before new criteria apply: <period>

## 7. Decertification ladder

| Rung | Trigger | Owner | Notice | Customer action |
| Warning | | | | none |
| Badge suspended | | | | none |
| New installs blocked | | | | notified |
| Existing installs disabled | | | | notified, migration path |

- Ladder clock: failures counted at scheduled evaluations every <period>, each reading a trailing <window>
- Dispute route: <decider>, <decision time>; badge stays during dispute except on the security fast path
- Security fast path: <trigger>, <days>

## 8. What the label buys

- <filter, label, triage, rank weight, slots: only what section 3 criteria justify>
- Fee to partner: <none, or amount and refund rule on revocation>
- Badge use: where it may appear, which connector versions it applies to, what the partner may say after suspension
- Agreement clauses backing the ladder: <revocation right, partner support obligation, liability disclaimer>

## 9. Transition (running programs only)

| Old label | New label | Re-earn deadline | Buyer-facing sentence |

## 10. KPIs and review date

## 11. Gate check

| Gate | Pass / fail | Evidence in this charter |
```

## Worked example (abridged)

Input: Lumenrow runs an ELT catalog with 140 partner-built source connectors, about 60% of installs. Enterprise buyers ask which connectors are "supported". Per-connector sync telemetry exists. There are two certification reviewers, part-time. The platform ships a contract-changing release twice a year.

Output, key sections:

- **Go/no-go:** all three conditions hold. Decision: run the program.
- **Labels:**
  - Lumenrow-maintained: operator-built.
  - Partner-maintained: partner-built, not certified.
  - Certified: partner-built, earned.
  - Community: everyone else.
- **Criteria (Certified):**
  - Contract layer: all required tests pass, >90% overall, per release.
  - Sync success: ≥95%, trailing 28 days, ≥200 syncs, operator telemetry, platform-outage errors excluded.
  - First response: ≤3 business days, trailing quarter, ≥5 tickets.
- **Support:** Lumenrow takes the first call on Certified connectors, isolates, and routes to the partner. Partner-maintained and Community listings show "Supported by <partner>, contact <channel>".
- **Renewal:** each badge is pinned to kit 2.x, platform 2026.2 and connector versions from the certified release onward. The kit re-runs on every behavior-changing connector release and every contract-changing platform release. Telemetry is evaluated on the first business day of each month over a trailing 28-day window; partners see their values on a dashboard the same day.
- **Ladder:**
  - Warning after one failed monthly evaluation; remediation runs until the next one.
  - Badge suspended after two consecutive failed evaluations; the listing stays.
  - New installs blocked after 90 days unmaintained.
  - Existing installs disabled only with 60 days' customer notice and a migration path.
  - Security fast path: unpatched critical vulnerability, new installs blocked within 3 days.
- **Label buys:** Certified filter, listing chip, operator triage. No rank boost until two quarters of telemetry exist.

## Negative example

```
// ✗ Bad - certifies the relationship, never re-tests, promises support nobody owns
Gold:     Premier partner, 3 joint customers, passed review once. Certified forever.
Silver:   Passed review once.
Bronze:   Listed.
Support:  "Certified connectors are fully supported."
Removal:  At our discretion.

// ✓ Good - one earned label over ownership labels, measured, pinned, routed
Certified: contract kit required tests pass; >=95% sync success, 28 days, >=200 syncs;
           pinned to kit 2.x, platform 2026.2; operator triages, partner fixes.
Removal:   four-rung ladder, notice per rung, 3-day security fast path.
```
