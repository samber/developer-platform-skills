Two of your plans need changing: #431 shouldn't be closed as a duplicate, and ticking items when work starts will mislead followers. I've written drafts for all three pieces below.

## 1. Umbrella issue

I don't have your 9 areas, so the list uses placeholders.

**Title:** `Migrate to Kotlin coroutines (tracking)`

```markdown
## Goal

Move the SDK's public and internal async APIs to Kotlin coroutines.
<one or two sentences: what users gain, and what stays supported, e.g. callback APIs deprecated but kept until vX>

## Areas

- [ ] <area 1>
- [ ] <area 2>
- [ ] <area 3>
- [ ] <area 4>
- [ ] <area 5>
- [ ] <area 6>
- [ ] <area 7>
- [ ] <area 8>
- [ ] <area 9>

A box is ticked when the work is merged. In-progress work is noted next to the item as `(in progress: @user, #PR)`.

## How to help

Comment on this issue to claim an area, then open a PR that says `Part of #<this issue>`.
Open a separate issue per area if the area needs design discussion.

## Out of scope

<anything explicitly not migrated>
```

- **Tick on merge, not on start.** A ticked box reads as "done" to anyone following, and GitHub's progress bar counts it that way. Put "in progress" in the item text. Adding an `(in progress: @user)` note takes the same effort as ticking.
- **Optional upgrade:** if an area needs its own discussion, make each item a child issue (`- [ ] #NNN`). GitHub then ticks the box when that issue closes, and you stop maintaining the list by hand.

## 2. Duplicates

**The three #412 duplicates:** close each as "Closed as duplicate" and post this first:

```markdown
Thanks for the report. This is the same problem as #412 (retry config ignored on 429), so I'm closing this one to keep the discussion in one place.

If your case differs, for example a different status code or a different client setup, comment here or on #412 with the details and we'll reopen.
```

**#431 (retries on 503):** don't close it as a duplicate.
- **Different trigger:** it reports a different status code. If the root cause in the retry path is the same, fixing #412 may not cover 503, and the report disappears from the tracker.
- **Check the code first:** if retry config is ignored for every status, make #431 a linked sibling. If only 429 is mishandled, it's a separate bug.
- **Either way:** keep it open, link it to #412, and relabel or retitle it.
- **If you close it anyway:** do so only after a fix for 503 has shipped and been checked.

Comment for #431:

```markdown
Related to #412 (retry config ignored on 429). This one covers 503, so I'm keeping it open as a separate issue. If the root cause turns out to be the same, we'll fix both together.
```

## 3. PR description template

Save as `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## What and why

<What changes, and why. Link design discussion if any.>

## Related issues

<!--
Pick ONE line and delete the other. GitHub closes the issue on merge only for these keywords:
close(s/d), fix(es/ed), resolve(s/d).

- Fully resolves the issue:  Fixes #123
- Partial work or part of a migration (does NOT close):  Part of #123
-->

Fixes #
Part of #

## Breaking changes

<None, or describe the break and the migration path.>
```

- **Why `Part of #`:** it is plain text, so GitHub links the issue but does not close it. `Refs #123` works the same way. Use `Part of #<umbrella>` for every coroutine-migration PR. That also gives you a backlink list on the umbrella.
- **One line left in:** the template says "pick one line". Contributors who leave `Fixes #` empty are harmless, but a stale `Fixes #<umbrella>` would close your tracking issue on the first merge.
- **Keyword scope:** closing keywords only fire when the PR merges into the default branch. PRs into a feature branch won't auto-close anything.
- **No test-plan checklist:** I left it out, following your open-source PR rule.

## Open questions

1. **The 9 areas:** send them and I'll fill in the list, with an owner column if you want one.
2. **Migration scope:** should I add a short deprecation or compatibility policy line to the umbrella, for example whether callback APIs stay?
3. **#431:** do you want me to check whether it shares a root cause with #412? That needs the retry-path source, which I haven't looked at.