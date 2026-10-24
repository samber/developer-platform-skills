**Short version:** each of the three plans is aimed at the wrong target. Here is what I'd do instead.

## 1. Headline: don't lead with 2,300 installs

Installs show that people tried the skill. They don't show it works, and your own suite says it loads in about a third of runs.

- Planning-review readers will ask "so what?", and installs can't answer that.
- Installs also include reinstalls, CI and bot installs, and people who never used it again.
- Lead with outcomes, and put installs second as reach.

Suggested slide:

1. **Lift:** pass rate with the skill versus without it, on the same tasks.
2. **Activation:** the share of relevant tasks where the skill loads (about 33% today, with a target).
3. **Reach:** 2,300 installs, plus 7-day and 30-day retention if skills.sh exposes it.

A lift number together with a known activation gap is more credible than a bare install count. It also sets up the next two points.

## 2. CI: the agent suite should not be the first gate

Order the checks cheapest first.

**Why 20 runs with "block on any drop" fails**
- At a 70% pass rate with 20 runs, one standard deviation is about ±10 points.
- Blocking on any drop will fail PRs on noise alone.
- Within a few weeks people will rerun until green or disable the gate.
- The suite is also slow and costs tokens on every PR.

**Proposed order**
1. **Deterministic gates, every PR (seconds, free):**
   - frontmatter and description lint
   - references resolve
   - bundled scripts run
   - security scan if the skill ships scripts
2. **Trigger test, every PR touching the skill (cheap):**
   - a labeled set of prompts that should and shouldn't load the skill
   - single-turn, load/no-load only
3. **Agent-in-the-loop suite, only when `skills/**` changes, or nightly:**
   - at least 3 runs per task
   - a paired comparison against `main`
   - **block** on a drop beyond the noise band (for example more than 15 points, or statistically significant)
   - **comment without blocking** on smaller drops

**Split the metric.** One pass rate mixes two things: whether the skill triggers, and whether it helps once loaded. Track these separately:
- trigger rate
- pass rate when loaded
- lift versus a no-skill baseline

## 3. Don't rewrite the body yet

The body isn't read until the skill loads. Whether it loads depends on the frontmatter `name` and `description`. A rewritten body can't fix a third-of-runs load rate.

Do this first:
1. **Run a positive control.** Prompt "use the oak skill" explicitly. It should load about 100% of the time. If it doesn't, your harness is mis-measuring loads, so fix that before anything else.
2. **Check the denominator.** Are all 20 tasks ones where the skill should fire? If some don't need it, 33% may be better than it looks.
3. **Rewrite the description and test it.** Use a labeled should-trigger and should-not-trigger set, and measure the trigger rate before and after.
4. **Then look at the body.** Compare pass rate when loaded against the no-skill baseline. Rewrite the body only if the lift is weak. Change one thing at a time so you can see what moved the numbers.

A "rewrite most of the body" change touches everything at once. You couldn't tell whether any improvement came from the body, and you'd risk regressing the parts that work.

## Next step

Do the positive control and the description-only trigger test this week. They take hours, and they decide whether the rewrite is needed at all. I can draft the trigger prompt set or the tiered CI workflow if you want either.