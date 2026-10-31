**Verdict:** Half good. Ship `llms.txt`. Skip the A2A agent card. Neither fixes the real cause, so do the Context7 and v1-docs steps first.

## Why not the agent card

- A2A is a protocol for talking to a running agent service. The card advertises an endpoint, skills, and auth.
- Quiverlane is a library with no running agent, so there is nothing for the card to point at.
- No coding agent looks up `/.well-known/agent-card.json` when it writes code against a library.
- Cost is low, but so is the payoff, and a card that points at nothing is a misleading artifact.

## Why `llms.txt` is only a partial fix

- It helps only when an agent fetches it at runtime. I'm not aware of any confirmed evidence that major coding agents or model trainers use it.
- Coding agents suggest v1 for two reasons: v1 dominates their training data, and retrieval tools (Context7 here) serve whatever they indexed.
- You are less popular, so training data will lag for a long time. Retrieval is the lever you control.

## What to do, in order

1. **Claim the Context7 listing (about 30 min).**
   - Someone else listed your repo, so you don't control what it indexes.
   - I believe Context7 supports owner claiming and a `context7.json` in the repo root. Check their docs for the current fields.
   - Use it to exclude `docs/v1-reference` (`excludeFolders`), set the title and description, and add `rules` such as "Use v2 APIs only. Never suggest v1."
   - If it supports previous-version entries, list v1 there so v1 is not mixed into the default.
2. **Isolate v1 (about 1 hour).**
   - Add a banner to every v1 page: "Deprecated. Use v2: <link>".
   - Add `noindex` to the v1 pages, and disallow `/docs/v1-reference` in `robots.txt`.
   - Consider moving v1 to a clearly versioned path like `/docs/v1/` so the path itself says it is old.
3. **Add a v1-to-v2 detection table (about 1 hour).**
   - Make it a migration page. Put "if you see this v1 symbol, use this v2 equivalent" at the top.
   - Agents match on symbols, so a symbol-level mapping corrects them. Prose alone won't.
4. **Write `llms.txt` (about 30 min).**
   - Put it at the site root. Link only v2 docs: quickstart, API reference, migration.
   - Add one line near the top: "v1 is deprecated. Do not use."
   - Optionally add `llms-full.txt` with the v2 docs inlined.
5. **Add an agent-instructions block (about 15 min).**
   - Put a short "Using Quiverlane with AI coding agents" section in the README.
   - Include a snippet users paste into `AGENTS.md` or `CLAUDE.md`, such as "Quiverlane: use v2 only; imports/symbols X, not Y."
   - This is the only fix that works even when retrieval fails.
6. **Mark v1 deprecated at the registry.**
   - Use the registry's deprecation mechanism for the v1 versions (e.g. `npm deprecate`, Go `retract`, or a PyPI yank or notice).
   - Installs then show a warning pointing to v2.

## How to verify

Test before and after in a fresh session, with and without Context7. Use 5 to 10 prompts like "add a Quiverlane retry policy". Count how many outputs use v1 symbols.

Include one known v1-only symbol as a positive control, so you can tell "agent never suggests v1" from "my prompts never trigger it".

## Open questions

- What language and registry is Quiverlane in? Step 6 and the migration table depend on the answer.
- Did v2 rename symbols or change the import path? If the import path changed, the mapping is easy to make precise.

**Next (2 min):** open Context7, find the Quiverlane listing, and check whether it has a claim or owner option.