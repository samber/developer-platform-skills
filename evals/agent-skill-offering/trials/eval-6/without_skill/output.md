**No. Don't build the MCP server first.** Spend week 1 finding out why the skill fails. Then ship fixes that put the correction inside the agent's edit-and-test loop. The MCP server has the same failure mode as the skill you already shipped.

Next action: pull 5 bug reports where the user confirmed the skill was installed. For each, check whether the agent transcript shows the skill loaded (about 1 hour).

## Why MCP likely fails the same way

I have not seen your SKILL.md or any transcripts. This is a hypothesis, and the week-1 test below checks it.

1. **MCP is also opt-in at runtime.** The model must decide to call the tool. A skill loads only when its description matches the task. Both depend on the model first doubting its own memory. `repo.findOne()` comes from training-data habit, so the model has no reason to doubt it. A tool the model skips fixes nothing.
2. **"Installed" does not mean "loaded".** Cursor and Codex do not read Claude Code's skill layout. Cursor reads rules files and Codex reads `AGENTS.md`. A SKILL.md that lives in your repo is not in the user's project at all. The description may also not match prompts like "add a query for orders".
3. **Most of the surface is already local.** Your API surface ships as `.d.ts` files in `node_modules`. The user's own schema is local too, so a hosted server cannot see it. You would need a local stdio server per agent, with per-agent config for Claude Code, Cursor and Codex. That is real setup friction for terminal users, plus schema tokens on every session.
4. **It does not verify anything.** Even with a correct tool result, the model can still write `findOne`.

## What to build instead

Order is by value per hour, with the cheapest first.

1. **Make the stale call fail with a fix in the error (about 3 days).**
   - Keep `findOne` and `Model.sync` as stubs in v5.
   - Type them so `tsc` prints the replacement, for example `(...args: never) => "removed in v4: use repo.<new>()"`.
   - Add `@deprecated` TSDoc naming the replacement.
   - Make them throw at runtime with the same exact text, for JS users.
   - Terminal agents run `tsc` and tests, so they read the message and self-correct. This is the strongest fix because it needs no trigger.
2. **Ship docs inside the npm package (about 2 days).**
   - Add `AGENTS.md`, an `llms.txt`, and a v3→v5 mapping table with before/after code and the exact error strings.
   - Agents reading `node_modules/verdant-orm` find them offline, at the installed version.
3. **Add `npx verdant-orm init-agent` (about 3 days).**
   - It writes a short always-on rule into the user's project: `AGENTS.md` (Codex, Cursor), a `CLAUDE.md` snippet, and a Cursor rules file.
   - It also installs the skill into the right directory for each agent.
   - Rule text: "Never use `findOne` or `Model.sync`. Use X and Y." An always-loaded negative rule beats an on-demand skill.
4. **Ship a lint rule or codemod (about 1 week).**
   - An ESLint rule or ast-grep rule that flags the v3 patterns and autofixes where it can.
   - Wire it into `init-agent` so the agent's lint step catches what the model emits.
5. **Rewrite the SKILL.md description (about 2 hours).**
   - Use trigger phrases such as "query", "repository", "sync schema", "migrate", "verdant-orm".
   - Lead the body with the "do not use" list.

## Six-week plan

| Weeks | Work |
|---|---|
| 1 | Diagnose. Run a cold test of 8 to 10 common tasks (find one, sync schema, insert, transaction) in Claude Code, Cursor and Codex, with and without the skill. Record whether the skill loaded and which stale calls appeared. This is your baseline. |
| 1–2 | Items 1 and 5 above. Release as a v5 minor or patch. |
| 2–4 | Items 2, 3 and 4. |
| 4 | Re-run the same task set. Compare to the baseline. |
| 5 | Decision gate for MCP (see below). |
| 6 | Buffer, docs, and tracking stale-call reports per release. |

**Success target:** stale calls on the top tasks fall to near zero, and stale-call bug reports drop release over release. Set the exact number from your week-1 baseline.

## When MCP becomes right

Build it only if the week-4 re-run still fails on things a tool can fix. The likely case is the agent inventing columns or relations from the user's own schema. Even then, scope it to a **local stdio server** started with `npx verdant-orm mcp` that introspects the project's actual schema and the installed version's API. A hosted server serving docs is not worth building. That is about 2 to 3 weeks, and the gate decides it.

## Open questions only you can answer

- Do the transcripts show the skill loaded at all? This decides whether the problem is triggering or the model's prior.
- Can you ship throwing stubs in v5 without confusing the v4 migration story? Users upgrading from v3 would see the message instead of a plain missing-property error, which should help.
- Who maintains the lint rule after the six weeks? If nobody, drop item 4.