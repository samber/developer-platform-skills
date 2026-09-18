# Contributing

One person maintains this collection of developer-platform skills, so the fastest path depends on what you want to change.

## Open an issue first when

- You want to propose a new skill. Scope is the hard part, and agreeing on it costs less than writing the wrong skill. Say what job it does, who on a platform, API or DX team does that job, and what it produces at the end.
- You think a skill gives wrong advice. Bring the counter-evidence: a published source, a specification, or your own experience contradicting it. Claims about API lifecycle, versioning and deprecation are where a confident wrong answer breaks somebody's integration.
- You are not sure whether what you found is a defect.

## Open a pull request directly for

- Corrections to a skill's content: a wrong fact, a dead link, a stale figure, a claim no longer true.
- English rewrites of awkward phrasing.
- Formatting and typos.

## What a skill has to satisfy

Every skill here targets the open [Agent Skills specification](https://agentskills.io/specification), so it runs on any compatible host rather than one vendor's.

- One directory per skill, kebab-case, matching the `name` in its frontmatter, with `SKILL.md` inside it.
- Frontmatter carries `name`, `description`, `license: MIT` and `metadata`. Nothing else.
- `description` states what the skill does, then when to use it, in the third person. A host reads only this before deciding whether to load the skill, so it decides whether the skill ever triggers at all.
- Every skill ends in a decision or a shippable artifact: a design call, a written policy, a reviewed contract, a migration plan. A skill that ends in a list of best practices does not belong here.
- Skills here cover design and policy work, not code generation. A skill whose output is an implementation rather than a decision belongs somewhere else.
- Never hardcode a path belonging to one agent host. Gate anything host-dependent on the capability instead: "if you can browse the web...".
- Keep a skill as small as its job allows, and move detail into `references/` rather than growing `SKILL.md`. Whatever a skill loads is paid for on every turn afterwards, not once.

## What gets rejected

- A skill wrapped around one gateway's, portal vendor's or SDK generator's console. Scope to the decision, so the skill survives the reader switching tools. A skill whose subject genuinely is one registry's publishing or listing process is fine.
- A skill overlapping heavily with one already here. Name the existing skill it replaces.
- Content restating what the model already knows.
- Advice with no source behind it, presented as established practice.

## Writing style

- Imperative, verb first: `Audit`, `Rank`, `Reject`.
- Active voice. Short sentences. One idea per section.
- Turn anything enumerable into a list or a table. Prose answers why, never what or how.
- Name a concept once, then reuse that exact term.
- Run `npx prettier --write` over any Markdown you touch.

## Good first contributions

Check the issues labelled `good first issue`. When none are open, a correction to a skill you have actually applied to a real API or SDK is always welcome and always reviewed.
