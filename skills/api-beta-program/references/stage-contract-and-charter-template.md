# Stage contract and program charter template

## Contents

1. Stage contract template
2. Worked example
3. Bad example
4. Program charter template
5. Backward timeline
6. Enrollment record
7. Launch checklist and sign-off
8. Existing-beta inventory

## 1. Stage contract template

Publish one table per company, not per feature; each beta's charter links to it.

```
| Row                 | Private preview | Public preview | GA |
|---------------------|-----------------|----------------|----|
| Access              |                 |                |    |
| Availability        |                 |                |    |
| Support             |                 |                |    |
| Breaking changes    |                 |                |    |
| Removal             |                 |                |    |
| Production use      |                 |                |    |
| Pricing             |                 |                |    |
| Data and compliance |                 |                |    |
| Limits              |                 |                |    |
| Marking             |                 |                |    |
| Discontinuation     |                 |                |    |
```

## 2. Worked example

Input: B2B API company, date-versioned API, enterprise DPA, new bulk export endpoint, two pre-GA stages.

Output:

| Row | Private preview | Public preview |
|---|---|---|
| Access | Invite; allowlisted per organization after signed preview terms | Self-opt-in in the dashboard on paid plans |
| Availability | No SLA; not on the status page | No SLA; incidents on the status page under "Preview" |
| Support | Shared channel with the product team, reply within 2 business days | Forum category, best effort |
| Breaking changes | Allowed, direct notice to each technical owner at least 2 weeks ahead | Only in a new preview version; previous preview version kept 90 days |
| Removal | 30 days notice; 90 days for accounts with a production exception | 90 days after notice |
| Production use | Unsupported, unless a signed production exception names the account | Discouraged; detected and contacted |
| Pricing | Free | GA price minus 50%; GA price published at public preview start |
| Data and compliance | No personal data; DPA processing terms, certifications and indemnity do not cover this preview; preview data deleted at the end of the overlap window; accounts with a production exception migrate it before then | Same until GA |
| Limits | 10 export jobs per day per organization | 50 export jobs per day per organization |
| Marking | `2026-11-01.preview` version enabled per organization; SDK pre-release channel; "Preview" badge on every operation | Same version, self-opt-in; same badges |
| Discontinuation | Export of job results for 30 days; enrolled accounts told privately first | Same, plus banner on docs and dashboard |

The figures are illustrative, set by this company; replace each with what your team will honour.

## 3. Bad example

```
// ✗ Bad - a label with no rows; every guarantee gets set later by the first escalation
Bulk export is in beta. Features may change. Use at your own risk.

// ✓ Good - one sentence per row a customer will ask about
Bulk export is in private preview: no SLA, breaking changes announced to your
technical owner two weeks ahead, not covered by our DPA (do not export personal
data), free until GA. Preview ends on or before 2027-03-31.
```

## 4. Program charter template

```
# <Feature> beta program charter

Owner: <name>          Backup: <name>         Exit review: <date>
Shape: <private preview | design partners | hybrid | public preview>
Stage contract: <link>
Wire mechanism: <version suffix | endpoint | header | subscription opt-in>; SDK: <channel or module>

## Problem statement
<one paragraph: the integrator problem this feature solves>

## Exit criteria
GA when: <all criteria>
Kill when: <any criteria>
Extension: one, at most half the time box, to <date>, with the failed criterion
Freeze: <date>

## Entry criteria
<the five criteria, cohort cap, composition and concentration rules>

## Cohort
| Account | Technical owner | Workflow | Enrolled | Terms version | Production exception | Activation met |

## Feedback cadence
<sessions, channel, owner, response time, activation event definition>

## Change rules
<notice per stage, changelog location>

## Outcome communication
<order: enrolled accounts, waitlist, public changelog; overlap window; kill notice rule>

## Sign-off
<see section 7>
```

## 5. Backward timeline

Derive every date from the GA target and check each lands on a working day.

| Milestone | Rule |
|---|---|
| GA | target date |
| Overlap ends | GA plus at least one partner release cycle, or the GA deprecation window if production traffic sits on the beta surface |
| Exit review | GA minus enough time to act on a kill or extension decision |
| Freeze | exit review minus at least one partner release cycle |
| Mid-point activation check | halfway between enrollment close and exit review |
| Enrollment closes | early enough for each account to reach activation before mid-point |
| Enrollment gate signed | before the first enrollment |
| Flag expiry alert | exit review date |

## 6. Enrollment record

```
| Field                | Value |
|----------------------|-------|
| Account or org id    |       |
| Approver             |       |
| Enrolled on          |       |
| Stage                |       |
| Technical owner      |       |
| Terms version        |       |
| Production exception | no / yes, signed <date> |
| Data addendum        | no / yes, signed <date> |
| Downstream accounts  | none / count (platform partners) |
| Activation event met | <date> |
| Planned exit date    |       |
```

## 7. Launch checklist and sign-off

- [ ] Owner and backup named.
- [ ] Stage contract published; data carve-out or addendum decided.
- [ ] Exit criteria, time box, freeze and extension rule written.
- [ ] Wire mechanism live; GA spec and GA SDKs exclude beta operations.
- [ ] SDK pre-release channel or module exists.
- [ ] Activation event instrumented; production-use detection running.
- [ ] Flags keyed per account, expiry alerts set.
- [ ] Changelog location for beta changes chosen.
- [ ] Waitlist and sales substitute replies written.
- [ ] Sign-off: program owner, design review (beta level), security review, legal, support.

## 8. Existing-beta inventory

| Surface | First shipped | Last shape change | Callers (90 days) | Accounts with production traffic | Owner | Decision | Date |
|---|---|---|---|---|---|---|---|
| | | | | | | GA as-is / next version / kill | |
