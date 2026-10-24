# Ship a rushmere skill by Friday (one afternoon, about 4 hours)

I haven't read the rushmere repo, so every API fact below is marked **[verify]**. Check those against your source before you publish.

## Decisions

- **Put the skill in your own repo.** Use `skills/rushmere/SKILL.md` in the rushmere repo, so it versions with the code.
- **Don't tag a release for it.** Your tag-push workflow publishes to PyPI. The skill installs from GitHub (`npx skills add <you>/rushmere`), so merge to main and stop.
- **Don't try to remove the community skill.** You can't from your side. Beat it by being the canonical one: link yours from the README, docs and `llms.txt`. Then leave a polite issue or comment on theirs pointing to the official one.
- **Don't copy from the community skill.** Skim it only to find its specific wrong claims. Each one becomes a "Do not" line in yours.
- **Keep it small.** Aim for under 120 lines. The skill covers the three failures and nothing else. Link to docs for the rest.

## Plan

### 1. Pull ground truth (30 min)
- Get the real `validate` signature and docstring. The correct order is presumably `validate(data, schema)` **[verify]**.
- Get the actual default for `strict` and what `strict=False` suppresses **[verify]**.
- From the 2.0 changelog or release notes, get the full list of what `rushmere.legacy` exposed and each replacement. This becomes a migration table.
- Note the minimum Python version and the exception types raised **[verify]**.

### 2. Reproduce the failures (30 min, do this before writing)
- Make a scratch dir outside the repo, with a venv and `pip install rushmere`.
- Start a fresh agent session there, with no skill installed.
- Run 6 prompts, 2 per failure, and save the outputs:
  - "Validate this dict against this schema."
  - "Port this 1.x script to current rushmere."
  - "Make this validation not blow up on bad rows."
- Count how often each failure appears. This is your baseline. Without it you can't show the skill helps.

### 3. Write SKILL.md (60 min)
Use this skeleton:

```markdown
---
name: rushmere
description: Use when writing or editing Python code that imports rushmere, calls rushmere.validate, builds rushmere schemas, handles rushmere ValidationError, or migrates from rushmere 1.x or rushmere.legacy.
---

# rushmere

## Before you write code
- Run `pip show rushmere` or read pyproject.toml. This skill assumes >= 2.0.

## Rules
1. Argument order: `rushmere.validate(data, schema)`. Data first. [verify]
2. Never import `rushmere.legacy`. It was deleted in 2.0. Use the table below.
3. Never pass `strict=False` unless the user asks for it by name.
   Leave the default. [verify the default and say what it does]
   If errors bother the user, catch `ValidationError` and report them.

## Wrong → right
(3 short before/after code blocks, one per failure)

## Legacy → 2.x migration
| rushmere.legacy.X | Use instead |
(fill from changelog)

## Verify your work
- Run the project's tests, or `python -c "import rushmere; ..."`.
- A passing run with `strict=False` proves nothing.

## Docs
(link to canonical docs)
```

Writing rules:
- Imperative, one rule per bullet.
- Put the three rules at the top, because that is where agents' attention is strongest.
- Make the description list trigger phrases and nothing else. Don't summarize the workflow in it.
- Build it with both skill-creator skills, per your standing rule.

### 4. Test it (60 min)
- Install the skill into the scratch environment.
- Re-run the same 6 prompts in fresh sessions.
- Pass criteria: zero swapped args, zero `legacy` imports, zero unrequested `strict=False`.
- If one still fails, fix the wording of that rule, not the whole file. Re-run only the failing prompt.
- Mutation check: delete one rule, re-run its prompts, and confirm the failure comes back. That shows the test can fail.

### 5. Stop it rotting (30 min)
- Add `tests/test_skill_examples.py`. It extracts every ```` ```python ```` block from SKILL.md and runs it against the installed rushmere.
- Add a CI step for it. The skill then breaks the build when the API changes.
- Add a line to your release checklist: "skill still accurate?"

### 6. Publish (15 min)
- Run `npx prettier --write skills/rushmere/SKILL.md`.
- Open a PR to main (draft, since it's open source) and merge it.
- Check that the install command works from a clean directory.
- Add the install line to the README.
- Check how skills.sh lists it. If it doesn't appear on its own, submit it however that site allows.

## Cut order if time runs short
1. Drop step 5, the CI example test, and do it next week.
2. Drop the migration table down to the most common 5 imports.
3. Never drop step 2 or step 4. Without them you are shipping an untested guess, which is what the community skill is.

## Risks
- **Wrong API facts.** An authoritative-sounding wrong skill is worse than none. The `[verify]` items exist for this reason.
- **Leaks in examples.** Use generic data in the code blocks. No real customer schemas or internal URLs.
- **Version skew.** Users on 1.x will get 2.x advice. The "check version first" line handles that. If 1.x users matter, add one line on what to do for them.

If you want, send me the three source facts from step 1 (signature, `strict` default, legacy map). I'll fill in the skeleton and write the 6 test prompts.