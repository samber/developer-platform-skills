# Is an MCP server the right build for verdant-orm?

**No. Don't build the MCP server first.** It is the wrong tool for this problem and for your audience. Spend the six weeks on the plan below. I didn't have your repo, so the diagnosis rests on the symptoms you gave me, and I list the unknowns at the end.

## Why MCP doesn't fit

The skill ranks what to add beside a skill for coding-agent users with a shell:

| Option | Effort | Correct agent calls | Efficiency |
|---|---|---|---|
| MCP server | highest | third of four | worst |
| Bundled docs + agent-instructions pointer | middle | second | second |
| JSON output on the CLI | lowest of the three | best | best |

An MCP server is for audiences without a shell, or for hosted auth and remote state. Your users run Claude Code, Cursor or Codex in a terminal, so they have none of those needs.

Your failure is also not a missing-data problem. The SKILL.md already names the new APIs, and agents still write `findOne()`. An MCP server hits the same wall for two reasons:

- **It is also on-demand.** The model has to decide to call it. If it didn't load your skill, it won't query your server either.
- **Its tool definitions cost idle context** on every session, for every user, including sessions that never touch verdant-orm.

## What is probably going wrong

"Installed the skill" is not the same as "the skill loaded in that run." The skill cites one framework's published evals where the skill was never invoked in 56% of runs, while an always-loaded docs index scored 100%.

Three causes could produce your symptom, and they need different fixes:

1. **The skill never triggers.** This is a description problem, or the knowledge belongs in always-loaded docs.
2. **The skill drifted.** It shipped three months ago and v5 has moved since. The lockstep rule says it must be in the same repo, with `metadata.version` equal to the code version, and every tag must contain a matching skill.
3. **It loads but loses.** Training-data habits win over one paragraph in a skill.

## The plan (six weeks)

**Week 1: diagnose, and ship the cheapest fixes.**
- Collect three real bug reports. For each, record the verdant-orm version, the skill version and the agent.
- Run each task 5 times per agent (Claude Code, Cursor, Codex), with and without the skill, and log whether the skill loaded. This gives you a trigger rate and a pass rate before you change anything.
- Check the layout: the skill should be at `skills/verdant-orm/SKILL.md`, listed in the npm `files` array. A skill that exists only in git is invisible to registry users.
- Rewrite the description as "what + when", naming the tasks users type: `findOne`, `sync`, migrating from v3, writing a repository, querying.
- Add the two-sided version guard to the body. The agent reads the installed version from `node_modules/verdant-orm/package.json`, not from memory. If major or minor differs in either direction, it trusts the package's types and docs over the skill and tells the user which skill tag to install.
- Cut any flag-table-style content out of the skill. The package owns what exists; the skill owns when and why.

**Weeks 2–3: put always-needed facts where they are always loaded.**
- Bundle a short `docs/` folder in the npm package, with an index of current v5 APIs.
- Add a `verdant-orm init-agents` command that writes a short pointer block into `AGENTS.md`, with `CLAUDE.md` importing it. Cursor and Codex read `AGENTS.md`. Use an explicit command, not a postinstall script, because postinstall scripts get flagged by audits and disabled by pnpm.
- Put the removed-to-replacement table inline in that pointer, since it is tiny:
  ```
  verdant-orm v5. Read node_modules/verdant-orm/docs/index.md before writing verdant-orm code.
  Removed since v4: repo.findOne() -> <v5 equivalent>; Model.sync() -> <v5 equivalent>.
  ```
- Keep the skill for workflows only: v3-to-v5 migration, setup, schema changes.

**Weeks 3–4: make the tool correct the agent inside its own loop.** This goes beyond the skill, and I expect it to help most.
- Keep `findOne` and `Model.sync` as typed stubs marked `@deprecated`, with a message naming the replacement. `tsc` then fails with the fix in the error text.
- Make the stubs throw a runtime error with the same message: "`repo.findOne()` was removed in v4; use X."
- Agents run `tsc` and tests, so they self-correct on the next iteration. This also covers users who never installed anything. Whether this suits your semver and bundle-size policy is a maintainer call, so check it before shipping.

**Weeks 4–5: wire the skill to the release (the lockstep gates).**
- Use one version source of truth, and generate `metadata.version`, the body's `Skill version:` line and every plugin manifest from it. Bump them in the commit the tag points at.
- Copy `scripts/check-skill-version.py` into your repo. Run it on every pull request, before the tag exists, and once more on the tag as a backstop.
- Add a content check that runs `tsc --noEmit` over every TypeScript block in the skill, against the built release package. Add a stale-symbol check that fails if the skill names a removed API outside a labelled "removed" section.
- Add the changed-surface check: if the public API changed and `skills/` didn't, the pull request fails unless it carries a "skill unaffected" label.
- Add spec validation and a Snyk Agent Scan over `skills/`.
- Make sure the packaged tarball contains `skills/` (`npm pack --dry-run | grep skills/`).

**Week 6: golden agent tasks, then measure.**
- Promote golden tasks from deferred to built. Agents are a main user channel for you, and the issue is already traced to a wrong or unused skill.
- Use 5 tasks: the three real failures plus two more. Score each on a binary pass condition, such as `tsc` passing and no removed API in the output.
- Run them on a pinned agent and model, with the skill, the docs pointer, both, and neither. Record trigger rate and pass rate per release.
- Generate a tag-pinned install command into every release note (`gh skill install`, `npx skills add owner/repo#vX.Y.Z`, the plugin marketplace command). Print the same commands in the README with a `v<your-installed-version>` placeholder.

## How you'll know it worked

- A release with a deliberately stale `metadata.version` fails before its tag exists.
- A release where the skill names a removed symbol fails CI.
- Every manifest's `version` equals the tag on the last three releases.
- Golden-task pass rate with the pointer and stubs beats the baseline from week 1.
- Stale-API bug reports per release drop. Tag them "agent misuse" so you can count them.

Ignore install counts. They measure interest, not correctness.

## When MCP becomes the right call

Revisit it if you gain users without a shell, such as chat assistants or hosted agent fleets. Also revisit it if you want agents to read a user's live database schema.

On that second point, your proposal says "current schema and API surface." Those are two different things:

- **Your API surface** is static per version, so bundle it in the package.
- **A user's own schema** lives in their repo, in generated types or schema files, which agents can already read.

Only a live, remote-state need justifies a server.

## What I couldn't verify

These answers would change the plan:

1. Does verdant-orm ship a CLI binary, or is it library-only? If it has a CLI, add `--json` output and a drift notice. The `init-agents` command also needs a binary to live in.
2. How do you cut releases (release-please, changesets or manual tags), and where does the version live? This decides how the version bump is wired.
3. When did the skill ship relative to v4 and v5? A skill written for v4.0 that never got bumped would explain the symptom by itself.
4. What were the three real failures beyond `findOne` and `Model.sync`? They become the skill's first content and the golden tasks.
5. Does a community-written skill, AGENTS.md or Cursor rule for verdant-orm already exist? Agents may be loading it instead of yours.
6. Is the effort ceiling really six weeks of one engineer, and may the binary gain a subcommand?