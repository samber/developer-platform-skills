**Next action (5 min):** Paste the `description:` line of the oak skill and the prompts of 3 runs where it didn't load. Don't rewrite the body yet.

I went through all three plans against the skill's rules.

## 1. Headline 2,300 installs: don't

- Installs measure interest, and they can be inflated. The skill says to measure correctness, not reach.
- 2,300 installs says nothing about whether agents call `oak` correctly.
- A planning review can't act on it, and one skeptic can pick it apart.
- Headline these instead, per release, with and without the skill:
  - Trigger rate.
  - Pass rate.
  - Issues tagged "agent misuse".
- Show installs as a labeled secondary "interest" number.
- You already have a trigger rate (about 33%). Show it honestly. It is the real finding.

## 2. CI: wrong order, wrong strictness

**Order.** The skill ranks agent-in-the-loop tasks (gate 5) as the highest effort and the lowest efficiency of the six gates. Run the cheap ones first:

| Where | Gates |
| --- | --- |
| Every PR | 1 spec validation, 2 version equality, 3 content check, 4 changed-surface, 6 security scan |
| Nightly | 5 golden agent tasks |
| Release job, before tag | 1, 2, 3, 6, and 5 once stable |

Gates 2 and 3 are deterministic and catch stale flags and versions. Twenty live Claude Code runs per PR cost money and minutes, and catch less.

**"Block when the pass rate drops at all."** Don't, for now.
- The skill says to treat a drop as a release blocker only once the suite is stable. Until then, report it.
- Agent runs are noisy. With 20 tasks, one flaky task moves the rate 5 points.
- A gate that blocks on noise gets rerun until green, then ignored.
- Published benchmarks also show small, noisy skill gains on software-engineering tasks.

**Do this instead (my suggestion, not from the skill):**
1. Run the suite 5 times on `main`. Record the spread.
2. Set the block threshold outside that spread.
3. Pin the agent and model.
4. Use 3-10 tasks from real `oak` failures, each with a binary pass condition. Twenty is not required.
5. Report until the suite is stable, then block at the release job.

## 3. Rewrite the body for a 1/3 load rate: wrong lever

- **The body loads after the skill triggers.** Trigger is decided by the `description`, so a new body can't raise the trigger rate.
- The skill names two causes for low trigger rate:
  1. A description problem. Fix: write it as what + when, with `oak` and the tasks users type, plus "even if they never say CLI".
  2. Knowledge that belongs in always-loaded docs. Evidence: one framework's skill went uninvoked in 56% of runs, while an always-loaded docs index scored 100%.
- A mass rewrite also has costs:
  - It risks the pass rate on runs where the skill does load.
  - It forces a version bump of `metadata.version` and the `Skill version:` line. Gates 2 and 3 must pass again.
  - It breaks your before/after comparison.

**Order:**
1. Check the 2/3 non-loading runs. Did they pass anyway? If yes, those tasks don't need the skill, and that is not a defect.
2. Rewrite the description. Re-run. Compare trigger rate.
3. If it is still low, add bundled docs plus an agent-instructions pointer for the facts every call needs. Keep the skill for workflows.
4. Edit only the body sections tied to tasks that failed while the skill was loaded.

## What I need from you

The skill's interview is unanswered. Five answers change the plan:
1. What `oak` ships: CLI only, or CLI plus library?
2. How releases are cut (tag, release-please, goreleaser) and where the version lives.
3. Your three worst real agent failures with `oak`.
4. Whether agents use it locally with a shell.
5. Your effort ceiling (an afternoon, or pipeline work).

**Next:** paste the description line and the 3 non-loading prompts.