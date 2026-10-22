# GitHub engagement templates

Replace every `<placeholder>`. Cut any line that would be false for this release or repository.

## 1. Release body

```markdown
## <one-line outcome a user gets, not the version number>

<two sentences: who should upgrade, and what changes for them>

### Breaking changes

- <change> - migrate with <link to migration guide>

### New

- <capability> (#<PR>) - thanks @<external contributor>

### Fixed

- <symptom the user saw> (#<issue>)

Install: `<package manager command pinned to this version>`
Questions: <link to the Q&A category>
```

## 2. Announcement discussion

```markdown
**<Project> <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

Tick "Create a discussion for this release" on the release form and paste this as the discussion body.

## 3. Start-here pinned post

```markdown
Welcome to <project> Discussions.

- **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.
```

## 4. Q&A answer

```markdown
<Direct answer in the first line.>

<Code or config, minimal and runnable.>

Docs for this: <deep link>. If this solved it, please mark it as the answer so others searching for "<their error text>" land here.
```

## 5. Issue-to-discussion redirect

```markdown
Thanks for the question. Converting this to a discussion in Q&A, where answers stay searchable and other users can help: <discussion URL>. Issues here track confirmed bugs. If this turns out to be one, we will reopen it with your reproduction.
```

## 6. Watch ask

Place it only where the reader already wants release news: the start-here post, the docs changelog page, or a solved support thread. Never in cold outreach. In off-GitHub content, use template 14 instead.

```markdown
Want release news without the issue noise? Click **Watch > Custom > Releases** on <repo URL>.
```

## 7. Star-for-star decline

```markdown
Thanks, but we don't trade stars: GitHub treats exchanged stars as rank abuse, and they would make our numbers meaningless to us too. If <project> solved something for you, a short note in Q&A on what you built helps more.
```

## 8. Leadership metric note

GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:

- Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
- Watchers (who receive release news)
- Dependents ("Used by") and <registry> downloads
- Q&A answered share and median time to answer, once Discussions has a month of history

Stars stay on the sheet as a trailing signal: <current> (<change> this quarter).

## 9. Pull request

```markdown
<One line: what this changes for a user, not how.>

Fixes #<issue> <!-- or "Part of #<tracking issue>" when it closes only one item -->

## Why

<The problem, or a link to the issue or discussion where it was agreed.>

## What changed

- <change>
- <change>

## How to check it

<Command, test name, or steps a reviewer runs to see it work.>

## Notes for reviewers

<Breaking change, migration, follow-up left out of scope, or delete this section.>
```

Use `Fixes`, `Closes` or `Resolves` only when merging the PR really ends the issue: GitHub closes it automatically on merge to the default branch.

## 10. Tracking issue for a large improvement

```markdown
<One paragraph: the outcome users get once every item below is done, and why it matters now.>

## Scope

- In: <what this covers>
- Out: <what it deliberately leaves to later, with the issue number if one exists>

## Progress

### <Phase or area 1>

- [ ] #<sub-issue>
- [ ] #<sub-issue>

### <Phase or area 2>

- [ ] #<sub-issue>
- [ ] <item without an issue yet - open one before starting it>

## How to help

Pick an unticked item without an assignee, comment on its sub-issue to claim it, and link your PR there. Questions about the plan itself go here.

## Done when

<The check that closes this issue, e.g. "all boxes ticked and released in <version>".>
```

- Write each item as `- [ ] #<number>`: GitHub renders the sub-issue's title and state, and the issue list shows "<done> of <total> tasks" from the boxes.
- Also attach each item as a native sub-issue where the repository has them, so the parent shows a progress bar and the children link back.
- Tick a box when its sub-issue closes, not when work starts, so the count measures delivered work.
- Pin the tracking issue while it is active.

## 11. New issue

```markdown
<One line: the symptom or the need, in the user's words.>

## Context

- Version: <project version>, <runtime and OS>
- Searched first: <issues, discussions or docs checked, with links, or "nothing found for <search terms>">

## What happens

<Minimal reproduction: code, config or steps. Expected versus actual.>

## Proposal

<What you would like to happen, or delete this section for a pure bug report.>

## Alternatives considered

<Workarounds tried, and why they fall short.>
```

## 12. Pointer to an existing open issue

```markdown
Thanks for opening this. The same topic is already tracked in #<issue><, and also discussed in #<issue> and #<issue>>.

Where it stands: <one or two lines summarising the decision so far, or the open question blocking it>.

To keep the history in one place, I'm closing this as a duplicate. Please add your use case to #<main issue>, especially <the detail that would help: reproduction, scale, constraint>. A 👍 on the first post there helps us size demand.
```

Choose "Close as duplicate" and pick the main issue, so GitHub links both and the closed one stays findable from search.

## 13. Pointer to a related but different issue

```markdown
Related: #<issue> covers <their topic>. This one is different because <the precise difference: scope, cause, platform, API surface>, so I'm keeping both open.

<If one blocks the other: "A fix for #<issue> may change the answer here; we'll revisit once it lands.">

If you think they are the same after reading #<issue>, say so here and we'll merge them.
```

Write the difference in one sentence. If you cannot, the issues are duplicates: use template 12.

## 14. Star ask for content published elsewhere

Close a blog post, newsletter, talk or video description with one line. Ask once, offer nothing in return.

```markdown
If <project> saved you time, a ⭐ on GitHub helps it grow and reach more people: <repo URL>
```
