# Portfolio register and strategy document template

Load this file in step 1 to build the register, and again when assembling the strategy document.

## Contents

- Register columns
- Worked example
- Strategy document template

## Register columns

One row per repo or top-level sample directory. Fill every cell or write `unknown`; an `unknown` owner or CI cell is a finding.

| Column | Values |
| --- | --- |
| ID | one per repo or top-level sample directory |
| Scenario ID | shared across languages of the same scenario |
| Type | tiny quickstart, flagship quickstart, scenario, reference app, deploy template, hosted collection, playground, mobile or device app, agent context |
| Job | evaluate, first call, integrate, production pattern, start a project, mobile or device, coding agent |
| Languages / frameworks | one entry per language actually present |
| SDK major pinned | per language; flag any outside the SDK support window |
| Owner | named person or queue with a named person |
| Last green CI | date, or `never` |
| Dependency PRs open | count, oldest age |
| Usage signal | invocations, docs traffic, `measured zero`, or `not measured` (never read as zero) |
| Tickets naming it | count over the last two quarters |
| Inbound links | docs pages, gallery, CLI list, external |
| Upkeep estimate | order of magnitude per quarter, self-set |
| Verdict | keep, fix, fix then merge, merge into `<repo>`, rebuild, archive → `<successor>`, community label |
| Tier after decision | supported, community, archived |

## Worked example

Input: a payments API with 23 sample repos across 8 languages (one checkout repo per language, per-language subscription and webhook repos, a 14-month-stale marketplace reference app, two device apps, a deploy-button starter, a 3DS flow, an API-v1 samples repo, a hackathon demo, a hosted collection); 12 red, one with no CI. SDK tier 1: Node, Python, Java, Go, Android. 40 upkeep hours per quarter, 6-week deadline, standing policy.

Output, condensed:

| Verdict | Rows | Why |
| --- | --- | --- |
| Archive with redirect | API-v1 samples, hackathon demo | retired API version; no owner, red, no usage |
| Archive with redirect | checkout in Ruby, PHP, .NET, Elixir; PHP subscriptions | tier 2 or no SDK, red, deadline near; tickets and links checked because per-language usage was unmeasured |
| Archive with redirect | deploy-button starter, iOS device app | red, usage unmeasured and no tickets; successor named or "none" |
| Archive with redirect (sales notified) | marketplace reference app | red, cut first by the capacity cap; sales deck link swapped first |
| Merge | Node and Python subscriptions, payouts, Node and Python webhooks | single-concern samples into one scenarios repo |
| Fix then merge | Go webhooks, Java 3DS | top-ticket scenarios on the adoption path |
| Merge into flagship | 4 tier-1 checkout repos | one repo with per-language folders, one CI harness |
| Keep | Android device app, hosted collection | green, tier-1 mobile SDK; collection gains a contract test |

Not served: "start a project", until tickets or API traffic show developers starting new projects on one framework.

Capacity: steady-state upkeep about 32 of 40 hours (self-set estimates). Cleanup about 25 one-off hours, sequenced scans and archives first, payouts scenario before the launch, remaining fixes after.

## Strategy document template

```markdown
# Sample portfolio strategy - <platform>, <date>

## 1. Inventory and baseline
Register summary: <N> artifacts by type and language, <N> without owner, <N> red, <N> unknown CI.

## 2. Portfolio shape
Chosen shape, rejected shapes and why.

## 3. Artifact types and coverage
Job-to-artifact table, "not served" jobs with their trigger. Language tier table (supported, community, absent). Capacity sum vs available hours; one-off cleanup hours and sequence.

## 4. Triage
Counts per verdict. Table of rows changed, with rule matched, verdict and successor.

## 5. Freshness contract
CI target and schedule, dependency bot cadence, red-build SLA numbers (self-set), supported version pins.

## 6. Archive rules
Triggers, sequence, banner, redirect registry location, who decides when the owner is absent.

## 7. Discoverability
Canonical index location and schema, surfaces it drives, CLI scaffold, agent index.

## 8. Measurement
Four signals per artifact, baseline quarter, review cadence. Pass gate status.
```
