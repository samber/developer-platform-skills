# Corvanta `corvanta-js` label scheme (final)

**Next action:** read "Four changes to your draft" below. Then run the label script and merge the three config files. Total setup is about 45 minutes.

I didn't have your capacity numbers (hours per week, who may change tracker settings). Everything below assumes a small team with no scheduled triage. Where a number would change the answer, I say so.

## Four changes to your draft

Your draft has about 40 labels. With nobody triaging on a schedule, labels rot. A 40-label set that people apply "when they feel like it" will leave most of the 210 issues half-labeled. The scheme below has **19 labels**, and the cuts follow one rule: each label must carry information that no other GitHub field already holds.

1. **Versions become milestones, not labels.** Create milestones `v3.1`, `v3.2` and `v4.0`. An issue can have only one milestone, so it can't be tagged for two versions at once. Milestones also give you a progress bar for free. Rule of thumb: anything breaking goes in `v4.0`.
2. **Owners become the Assignee field, not labels.** `owner: priya` duplicates Assignee and goes stale the moment someone reassigns. Assignee also feeds "assigned to me" views and notifications, which a label does not.
3. **P3 is dropped, leaving three priority levels.** Four levels invite "everything is P1". No priority label means backlog, and the status labels below separate "backlog" from "not triaged yet".
4. **A status axis is added, and it's the most important one.** You had no way to tell untriaged from triaged-and-low-priority. Without it, "labels when they feel like it" can't be measured or fixed.

## The 19 labels

Use one separator everywhere (`axis: value`). Your draft mixed `P0`, `type: defect` and `area/auth`.

**Type** (one per item; `type: defect` replaces `bug`)

| Label | Meaning |
|---|---|
| `type: defect` | The SDK does something other than what the docs or types promise. |
| `type: enhancement` | New behavior or API. |
| `type: maintenance` | Refactors, deps, CI, tooling. Excluded from release notes. |

Questions don't get a label. Route them to GitHub Discussions (see "Intake").

**Priority** (defects only, set by a person; no priority label means backlog)

| Label | Defined by consequence |
|---|---|
| `priority: P0` | Data loss, or broken for most users with no workaround. Drop other work. |
| `priority: P1` | Broken for a real use case, with a workaround that hurts. Next release. |
| `priority: P2` | Real but tolerable. Scheduled, not urgent. |

**Status** (exactly one on every open issue)

| Label | Meaning |
|---|---|
| `status: needs-triage` | Applied automatically on creation. Removing it is the triage act. |
| `status: needs-info` | Waiting on the reporter. The only state the stale sweep may touch. |
| `status: blocked` | Waiting on something outside the issue (upstream, a decision). Never auto-closed. |

**Area** (one or more)

`area: auth`, `area: webhooks`, `area: retries`, `area: pagination`, `area: types`, `area: docs`

**Contributor-facing**

| Label | Use |
|---|---|
| `good first issue` | Exact GitHub spelling, because GitHub's contribute pages and search match that string. Apply only when the fix is well understood, the files are named in the issue, and a test shows how to verify it. "Looks small" is not enough: a small-looking issue with unclear scope is the worst first experience. |
| `help wanted` | Maintainers would welcome a PR but won't do it soon. |

**Release notes** (set on PRs; see below)

`breaking change`, `skip-changelog`

## Release notes: what the labels do

GitHub's auto-generated notes group by labels on **pull requests**, not on issues. So `type: defect` on an issue changes nothing in the notes. Put `type: defect`, `type: enhancement` and `breaking change` on the PR at merge time.

Add `.github/release.yml`:

```yaml
changelog:
  exclude:
    labels:
      - skip-changelog
      - "type: maintenance"
  categories:
    - title: Breaking changes
      labels:
        - breaking change
    - title: Bug fixes
      labels:
        - "type: defect"
    - title: Enhancements
      labels:
        - "type: enhancement"
    - title: Other changes
      labels:
        - "*"
```

A PR with no label lands in "Other changes", so nothing is lost. Add a line to the PR template: "Set a `type:` label before merging."

## Create the labels

This script **writes 19 labels to the repo**. `--force` makes it safe to re-run.

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO="corvanta/corvanta-js"

mk() { gh label create "$1" --repo "$REPO" --color "$2" --description "$3" --force; }

mk "type: defect"           d73a4a "SDK behaves differently from docs or types"
mk "type: enhancement"      a2eeef "New behavior or API"
mk "type: maintenance"      cfd3d7 "Refactor, deps, CI, tooling"

mk "priority: P0"           b60205 "Data loss or broken for most users, no workaround"
mk "priority: P1"           d93f0b "Broken real use case, painful workaround; next release"
mk "priority: P2"           fbca04 "Real but tolerable; scheduled"

mk "status: needs-triage"   ededed "New; remove this label to mark triaged"
mk "status: needs-info"     c5def5 "Waiting on reporter; stale sweep applies"
mk "status: blocked"        5319e7 "Waiting on something external; never auto-closed"

mk "area: auth"             0e8a16 "Authentication and credentials"
mk "area: webhooks"         0e8a16 "Webhook signing, delivery, parsing"
mk "area: retries"          0e8a16 "Retry and backoff behavior"
mk "area: pagination"       0e8a16 "Cursors, iterators, page helpers"
mk "area: types"            0e8a16 "TypeScript types and inference"
mk "area: docs"             0e8a16 "Documentation and examples"

mk "good first issue"       7057ff "Scoped, files named, verifiable by a test"
mk "help wanted"            008672 "Maintainers welcome a PR"

mk "breaking change"        b60205 "PR: breaks public API (release notes)"
mk "skip-changelog"         ffffff "PR: leave out of release notes"
```

Then create the three milestones in the UI (Issues, then Milestones): `v3.1`, `v3.2`, `v4.0`.

## Intake: make triage happen without a schedule

You have no triager, so make the tracker do the first step.

1. **Issue forms apply `status: needs-triage` automatically.** Add `.github/ISSUE_TEMPLATE/defect.yml`:

```yaml
name: Defect report
description: The SDK does something the docs or types say it shouldn't
labels: ["type: defect", "status: needs-triage"]
body:
  - type: input
    id: version
    attributes:
      label: corvanta-js version
    validations:
      required: true
  - type: textarea
    id: repro
    attributes:
      label: Minimal reproduction
      description: Smallest code that shows the problem
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected vs actual behavior
    validations:
      required: true
```

2. **Add a matching `enhancement.yml`** that applies `type: enhancement` and `status: needs-triage`.
3. **Add `config.yml`** with `blank_issues_enabled: false`. Add a contact link that sends usage questions to GitHub Discussions.
4. **Security reports leave the tracker.** Enable private vulnerability reporting and put it in the chooser. Never file `area: auth` vulnerabilities as public issues.

The queue "Open issues with `status: needs-triage`" is now your triage inbox. Anyone can open it and work from the top.

## Staleness rule

- A sweep may close **only** `status: needs-info` items, after 14 days of silence plus a warning, then 14 more days.
- Never auto-close confirmed or `status: blocked` issues.
- Every close states why and how to reopen.
- Run the first pass as a dry run to see what it would close.

## Backfilling the 210 open issues

At a planning placeholder of 3 minutes per issue, 210 issues is about 10.5 hours. Time your first 15-20 and replace that number with the real one. These steps cut the work:

1. **Bulk-apply `status: needs-triage` to all 210** with the CLI. Now untriaged is queryable. **This writes to 210 issues**, so confirm first:

```bash
gh issue list --repo corvanta/corvanta-js --state open --limit 300 --json number -q '.[].number' \
  | xargs -I{} gh issue edit {} --repo corvanta/corvanta-js --add-label "status: needs-triage"
```

2. **Look for clusters first.** On a 210-issue backlog, many issues usually share a root cause (for example, several pagination or webhook-signature reports). Group them under one tracking issue and close the rest as duplicates. This often clears more than labeling item by item.
3. **Label in this order:** defects (type, area, priority, milestone), then enhancements, then the rest. For enhancements, only `type`, `area` and milestone are needed.
4. **Time-box each session** to 45 minutes. Stop when the box ends, not when the inbox is empty.
5. **Assign in the Assignee field** (Priya or Marco), not with labels.

## Why this will survive without a triager

- Forms set the labels, so type and `needs-triage` never depend on memory.
- Three status labels and three priority levels are few enough to apply correctly.
- The one-line rule: **removing `status: needs-triage` is the only required act of triage.** Everything else is optional polish.
- Re-count `status: needs-triage` monthly. If it shrinks, the scheme works. If it grows, you need a rota, not more labels.

## Questions that would change this

1. How many hours per week can Priya and Marco give to triage? If it's under 2 hours each, drop the `area:` labels entirely and keep only type, status and priority.
2. Can you change repo settings (forms, Discussions, Actions), or does that need an admin?
3. Do you have a contractual response commitment to anyone? If so, publish a first-response target, which I can size from the answers above.

**Next:** run the label script, then reply with the answers to questions 1-3.