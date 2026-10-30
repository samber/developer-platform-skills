# Ferrowisp Kotlin SDK: coroutines umbrella issue, duplicate closes, and PR template

I read `github-engagement-playbook` and its `references/templates.md` and `references/labels.md`. I filled templates 10, 12, 13 and 9. I changed two of your plans, and the reasons are below.

## What I changed from your plan

1. **Umbrella issue: use one sub-issue per item, not plain bullet text.**
   - Plain bullets can't be claimed and carry no state or "n of 9 tasks" count. Nobody can follow or help on a bullet.
   - Open the 9 sub-issues first, then list them as `- [ ] #<number>`. GitHub renders each title and state and shows the "done of total" count on the issue list.
   - Also attach them as native sub-issues if your repo has them, so the parent shows a progress bar.
   - Pin the issue while it's active.
2. **Tick when the sub-issue closes, not when someone starts.**
   - A box ticked at start makes the count measure intent, not delivered work.
   - To show "someone's on it", use the assignee on the sub-issue.
3. **Don't close the three duplicates with only "duplicate, see #412".**
   - Use template 12 and choose **Close as duplicate** in the UI, so GitHub links both issues. The reporters get a summary and a concrete ask, and #412 collects reproductions instead of silence.
4. **#431 (retries on 503) is probably not a duplicate of #412 (429).**
   - Per the playbook, if you can state the difference in one sentence, keep both open (template 13). The trigger differs here: 503 vs 429.
   - If both come from the same code path and one fix covers both, say so and close it with template 12 instead.
   - Check that path in the retry code before you decide.
5. **PR template: `Fixes #` is the wrong default.** Partial PRs should say `Part of #<tracking issue>`, which links without closing.

## 1. Umbrella issue (template 10)

**Title:** `Migrate the SDK to coroutines`

Open the 9 sub-issues first. You didn't send the list, so the area names below are placeholders.

```markdown
Once every item below is done, <outcome users get, e.g. "all public Ferrowisp calls are suspend functions with structured cancellation">. This matters now because <reason: e.g. blocking calls on Dispatchers.Main, or next major release>.

## Scope

- In: <the 9 areas, one line>
- Out: <what stays blocking or deferred, with the issue number if one exists>

## Progress

### <Phase or area group 1>

- [ ] #<sub-issue 1> <area 1>
- [ ] #<sub-issue 2> <area 2>
- [ ] #<sub-issue 3> <area 3>

### <Phase or area group 2>

- [ ] #<sub-issue 4> <area 4>
- [ ] #<sub-issue 5> <area 5>
- [ ] #<sub-issue 6> <area 6>

### <Phase or area group 3>

- [ ] #<sub-issue 7> <area 7>
- [ ] #<sub-issue 8> <area 8>
- [ ] #<sub-issue 9> <area 9>

## How to help

Pick an unticked item without an assignee, comment on its sub-issue to claim it, and link your PR there. Use `Part of #<sub-issue>` in your PR unless it finishes that sub-issue. Questions about the plan itself go here.

## Done when

All boxes ticked and released in <version>.
```

**Labels** (from `references/labels.md`):
- Put `enhancement` and an `area/coroutines`-style label on the parent.
- Put `good first issue` only on sub-issues that have a written fix outline and a named file.

## 2. Close as duplicate of #412 (template 12)

Post this on each of the three new issues, then **Close as duplicate** and pick #412. Before posting, confirm each one really is "retry config ignored on 429". Delete the "also discussed" clause if it doesn't apply.

```markdown
Thanks for opening this. The same topic is already tracked in #412<, and also discussed in #<other issue>>.

Where it stands: <one or two lines: current decision, suspected cause, or the open question blocking the fix>.

To keep the history in one place, I'm closing this as a duplicate. Please add your use case to #412, especially <the detail that would help: your retry config values, whether the 429 carries a Retry-After header, SDK version, Kotlin and runtime>. A 👍 on the first post there helps us size demand.
```

## 3. #431: keep open, link to #412 (template 13)

Post on #431, with no close:

```markdown
Related: #412 covers retry config being ignored on 429. This one is different because <the precise difference in one sentence: e.g. "the 503 path <does/doesn't> go through the same retry policy, so the cause may differ">, so I'm keeping both open.

A fix for #412 may change the answer here; we'll revisit once it lands.

If you think they are the same after reading #412, say so here and we'll merge them.
```

If you can't fill the "different because" sentence from the code, they are duplicates. Use the section 2 text instead.

## 4. Pull request template (template 9)

Save as `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
<One line: what this changes for a user, not how.>

<!-- Pick ONE and delete the other:
Fixes #<issue>              closes the issue on merge. Use only when this PR fully resolves it.
Part of #<tracking issue>   links without closing. Use for every partial PR, including coroutine-migration items.
-->

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

Rule for authors: use `Fixes`, `Closes` or `Resolves` only when merging the PR really ends the issue. GitHub closes the issue automatically on merge to the default branch.

For existing open PRs that say `Fixes #` on partial work, edit them to `Part of #` before merging. Otherwise the merge closes the issue early, and with sub-issues it ticks the umbrella count falsely.

## Open items for you

- The 9 area names, the outcome sentence, and the "Done when" version are placeholders, so I invented nothing.
- I couldn't see the repo, so I did not check whether #412 and the new issues are the same bug, or whether #431 shares a code path. Those checks decide sections 2 and 3.
- Optional: the playbook suggests running the final text through your humanizer skill before posting.