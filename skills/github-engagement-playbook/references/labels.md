# Labels for issues, pull requests and discussions

Contents:

1. Why labels matter for engagement
2. Starter scheme
3. Rules
4. What each surface needs
5. Automation
6. Keeping labels as code

## 1. Why labels matter for engagement

- `good first issue` feeds the repository's `/contribute` page and GitHub's good-first-issue recommendations [documented]. `help wanted` is the label newcomers filter search by [folklore]. They are the only labels with reach outside the repository.
- Labels drive automatically generated release notes: `.github/release.yml` groups merged PRs into sections by label [documented]. A PR labelled consistently writes its own changelog line.
- A visitor scanning the issue list reads labels before titles. A tracker where most issues carry a type and a status reads as maintained.

## 2. Starter scheme

Start with about 15 labels. Add one only when a weekly triage keeps reaching for it.

| Group         | Labels                                                          | Colour               | Applies to               |
| ------------- | --------------------------------------------------------------- | -------------------- | ------------------------ |
| Type          | `bug`, `enhancement`, `documentation`, `question`               | One colour per label | Issues, PRs              |
| Status        | `needs-triage`, `needs-reproduction`, `confirmed`, `blocked`    | One shared hue       | Issues                   |
| Resolution    | `duplicate`, `wontfix`, `invalid`                               | Grey                 | Issues, PRs              |
| Contributors  | `good first issue`, `help wanted`                               | Green                | Issues                   |
| Release notes | `breaking-change`, `dependencies`, `skip-changelog`             | Red, blue, grey      | PRs                      |
| Area          | `area/<component>`, one per component users name in bug reports | One shared hue       | Issues, PRs, discussions |

- Keep GitHub's default spellings for `bug`, `enhancement`, `documentation`, `question`, `duplicate`, `wontfix`, `invalid`, `good first issue` and `help wanted`. Contributors and tools already know them.
- If the organization uses issue types, use the type field instead of the Type labels, and keep the rest.
- Use a prefix (`area/`, `status/`) only for groups with more than four labels. Short schemes read faster without one.

## 3. Rules

**Do:**

- Give every label a description. GitHub shows it on hover and in the label picker.
- Apply exactly one Type and at most one Status to an issue.
- Label at triage, within the same weekly pass that answers Q&A.
- Remove `needs-triage` the moment someone has read the issue, so the filter `label:needs-triage` stays an honest inbox.
- Put `good first issue` only on issues with a written outline of the fix and a named file. A vague one wastes a newcomer's first visit.

**Don't:**

- Create priority labels without someone who reorders work by them. Unused priorities read as neglect.
- Encode a version or a person in a label (`v2.3`, `alice`). Use milestones and assignees.
- Rename a label that automation or release notes depend on without updating `.github/release.yml` and workflows in the same PR.

## 4. What each surface needs

- **Issues** - Type, Status, Area, plus the contributor labels where they fit.
- **Pull requests** - Type and the release-note group. Area only when the repository has several components.
- **Discussions** - categories do the typing; labels add Area, and `needs-maintainer` for a question the community could not answer.

## 5. Automation

- **Issue forms** - set `labels:` in each `.github/ISSUE_TEMPLATE/*.yml` form, so a bug report arrives as `bug` + `needs-triage` [documented].
- **Path-based PR labels** - a labeler workflow maps paths to `area/` and `documentation` labels.
- **Dependabot** - its PRs get `dependencies` plus an ecosystem label by default; override with `labels:` in `dependabot.yml` [documented].
- **Release notes** - map labels to sections in `.github/release.yml`:

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
    - title: Dependencies
      labels: [dependencies]
    - title: Other
      labels: ["*"]
```

## 6. Keeping labels as code

Keep the label list in a file in the repository (name, colour, description) and sync it with a label-sync action or script. Copying it across an organization's repositories gives contributors the same vocabulary everywhere, and a PR review catches a renamed label before it breaks release notes.
