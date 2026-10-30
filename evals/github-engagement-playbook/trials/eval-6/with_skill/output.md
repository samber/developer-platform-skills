# Label scheme for corvanta/corvanta-js

I read the `github-engagement-playbook` skill and its `references/labels.md` and `references/templates.md`, and applied them to your draft. I haven't seen the repo, so everything below is based on what you told me.

**Short version:** keep 19 labels, not about 40. Version and owner move out of labels into milestones and assignees. `type: defect` goes back to `bug`. Priority labels wait until someone is assigned to reorder by them. Your area labels and `good first issue` stay, with one rule added for `good first issue`.

## What changed from your draft

| Your draft | Final | Why |
|---|---|---|
| `P0`–`P3` | Dropped for now | Priority labels nobody reorders work by read as neglect. Nobody does scheduled triage today, so they would go stale. |
| `type: defect` | `bug` | Keep GitHub's default spellings. Contributors, issue forms and tools already know `bug`. Your `release.yml` can also use the defaults. |
| `v3.1` / `v3.2` / `v4.0` | Milestones `v3.1`, `v3.2`, `v4.0` | Don't encode a version in a label. A milestone gives you a progress bar and a due date, and closing it ends the version. |
| `owner: priya` / `owner: marco` | Assignees | Don't encode a person in a label. An assignee shows up in "Assigned to me" and in notifications. |
| `area/docs` | Dropped, use `documentation` | It overlaps the type label. |
| `good first issue` on "anything small" | Kept, with a rule | Only issues with a written outline of the fix and a named file qualify. Small alone is not enough. |
| About 40 labels | 19 | Start around 15 and add one only when a weekly triage keeps reaching for it. |

If you want priority, the cheapest way is a **Priority field in a GitHub Project**. That is my suggestion, not from the skill. It keeps the label list short and you can drop it without touching releases. Add it only once Priya or Marco actually reorders by it, and review that at the end of the quarter.

## The 19 labels

Give every label a description. GitHub shows it on hover and in the label picker.

| Group | Label | Description | Colour |
|---|---|---|---|
| Type | `bug` | Something in the SDK does not work as documented | `d73a4a` |
| Type | `enhancement` | New capability or improvement | `a2eeef` |
| Type | `documentation` | Docs, README or code-sample change | `0075ca` |
| Type | `question` | Usage question. Move to Discussions Q&A | `d876e3` |
| Status | `needs-triage` | Not read by a maintainer yet | `fbca04` |
| Status | `needs-reproduction` | Waiting for a minimal reproduction from the reporter | `f9d0c4` |
| Status | `blocked` | Waiting on something outside this issue | `fef2c0` |
| Resolution | `duplicate` | Already tracked in another issue | `cfd3d7` |
| Resolution | `wontfix` | Out of scope or declined | `cfd3d7` |
| Contributors | `good first issue` | Outline and file named in the issue. Suitable for a newcomer | `0e8a16` |
| Contributors | `help wanted` | Maintainers welcome an outside PR | `2ea44f` |
| Release notes | `breaking-change` | Needs a major bump and a migration note | `b60205` |
| Release notes | `dependencies` | Dependency update | `0366d6` |
| Release notes | `skip-changelog` | Leave out of generated release notes | `cfd3d7` |
| Area | `area/auth` | Authentication and credentials | `1d76db` |
| Area | `area/webhooks` | Webhook signature checking and event handling | `1d76db` |
| Area | `area/retries` | Retry and backoff behaviour | `1d76db` |
| Area | `area/pagination` | Cursor and list iteration | `1d76db` |
| Area | `area/types` | TypeScript typings and generics | `1d76db` |

Rules:

- Every issue gets exactly one Type and at most one Status.
- Remove `needs-triage` as soon as someone has read the issue. Then `label:needs-triage` stays an honest inbox.
- Pull requests get a Type plus a release-note label. Add an Area only if the PR clearly belongs to one.
- `area/` stays as a prefix because you have more than four areas.

## Version and owner without labels

1. Create milestones `v3.1`, `v3.2` and `v4.0`, each with a due date if you have one.
2. Put an issue in a milestone only when a maintainer has agreed to ship it in that version. Anything undecided stays without a milestone.
3. Use the assignee field for Priya and Marco. Assign only when that person has said yes.
4. For `v4.0`, open one tracking issue with sub-issue checkboxes (template 10 in `references/templates.md`) and pin it while it is active.

## Release notes

The labels above are what auto-generated notes use. GitHub groups merged PRs, not issues, by label [documented]. A PR with no label lands in "Other", so label every PR before merge.

Create `.github/release.yml`:

```yaml
changelog:
  exclude:
    labels: [skip-changelog]
  categories:
    - title: Breaking changes
      labels: [breaking-change]
    - title: New
      labels: [enhancement]
    - title: Fixed
      labels: [bug]
    - title: Docs
      labels: [documentation]
    - title: Dependencies
      labels: [dependencies]
    - title: Other
      labels: ["*"]
```

Never rename a label this file uses without editing `release.yml` in the same PR.

For each release, paste the generated list into the body in the shape of template 1: a one-line outcome, who should upgrade, then the sections. The skill says a release body with no explanation is a wasted feed event. A release is also a notification to watchers [documented].

## Automation, because nobody labels on a schedule

1. **Issue forms.** Set `labels: ["bug", "needs-triage"]` in the bug form and `["enhancement", "needs-triage"]` in the feature form, in `.github/ISSUE_TEMPLATE/*.yml`. Every new issue then arrives typed and in the inbox [documented].
2. **Question redirect.** Add a `contact_links` entry in `.github/ISSUE_TEMPLATE/config.yml` that points questions to Discussions Q&A. This only helps if someone answers there; if nobody will, skip Discussions.
3. **Path-based PR labels.** A labeler workflow maps paths such as `src/auth/**` to `area/auth`, and `docs/**` to `documentation`.
4. **Dependabot.** Its PRs get `dependencies` by default [documented].

## Triage routine

Right now people label when they feel like it, so any scheme will decay. The skill's cadence puts labelling in one weekly pass.

1. Pick one named owner and one backup. Suggested: Priya owns it, Marco covers.
2. Block one weekly slot of 30–45 minutes (my estimate).
3. In the slot, open `label:needs-triage`, read each issue, set Type and Area, remove `needs-triage`, and move usage questions to Q&A with template 5.
4. Add `good first issue` only if you can write the outline and name the file in a comment right then.
5. Check at the end of the quarter which labels were never used, and delete them.

## The 210 existing issues

Don't label all 210 by hand up front.

1. Create the 19 labels with the script below.
2. Add `needs-triage` to all 210 open issues, so the inbox starts full and honest. The script paces itself well under GitHub's content-creation limit of about 80 requests per minute [documented].
3. Work the backlog oldest-first inside the weekly slot, 20–30 issues per pass. That is about 7–10 weeks (my estimate). Answer usage questions first and close what is clearly stale or duplicate with template 12.
4. Don't promise a `v3.1`/`v3.2`/`v4.0` milestone to anything until it has passed triage.

### Scripts

Both **write to corvanta/corvanta-js**: the first creates or overwrites labels, the second edits 210 issues. Run them yourself, with push access, from any directory.

```bash
#!/usr/bin/env bash
# Create or update the 19 labels. --force overwrites an existing label with the same name.
set -euo pipefail
REPO="corvanta/corvanta-js"

label() { gh label create "$1" --description "$2" --color "$3" --force -R "$REPO"; }

label "bug"                "Something in the SDK does not work as documented" d73a4a
label "enhancement"        "New capability or improvement" a2eeef
label "documentation"      "Docs, README or code-sample change" 0075ca
label "question"           "Usage question. Move to Discussions Q&A" d876e3
label "needs-triage"       "Not read by a maintainer yet" fbca04
label "needs-reproduction" "Waiting for a minimal reproduction from the reporter" f9d0c4
label "blocked"            "Waiting on something outside this issue" fef2c0
label "duplicate"          "Already tracked in another issue" cfd3d7
label "wontfix"           "Out of scope or declined" cfd3d7
label "good first issue"   "Outline and file named in the issue. Suitable for a newcomer" 0e8a16
label "help wanted"        "Maintainers welcome an outside PR" 2ea44f
label "breaking-change"    "Needs a major bump and a migration note" b60205
label "dependencies"       "Dependency update" 0366d6
label "skip-changelog"     "Leave out of generated release notes" cfd3d7
label "area/auth"          "Authentication and credentials" 1d76db
label "area/webhooks"      "Webhook signature checking and event handling" 1d76db
label "area/retries"       "Retry and backoff behaviour" 1d76db
label "area/pagination"    "Cursor and list iteration" 1d76db
label "area/types"         "TypeScript typings and generics" 1d76db
```

```bash
#!/usr/bin/env bash
# Add needs-triage to every open issue. Sleeps 2 s between edits (about 7 minutes for 210).
set -euo pipefail
REPO="corvanta/corvanta-js"

gh issue list -R "$REPO" --state open --limit 500 --json number --jq '.[].number' |
while read -r n; do
  gh issue edit "$n" -R "$REPO" --add-label "needs-triage"
  sleep 2
done
```

Check first that the repo has no leftover labels: `gh label list -R corvanta/corvanta-js`. You said zero, but confirm before running.

Keep the label list as a file in the repo (name, colour, description) and sync it with a label-sync action. A PR review then catches a rename before it breaks release notes.

## Questions for you

1. Who is the triage owner and backup? Without a name, the weekly pass is not real.
2. Do usage questions arrive as issues today? If yes, Discussions Q&A is worth opening. If nobody will answer there, skip it.
3. Do Priya and Marco actually reorder work by urgency? If yes, add the Project priority field.
4. Do you have push access? The traffic archive and the scripts above need it.