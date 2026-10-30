**Short answer: no. The plan targets the wrong layer.** The agent card is the wrong file for a library, and llms.txt isn't the fix for the v1 problem. The cause is most likely the Context7 entry someone else created, so claim it and exclude the v1 docs.

I haven't looked at your Context7 listing or your repo, so the cause is an inference. Step 1 below confirms it.

## Why the plan misses

- **Agent card:** it advertises an agent endpoint that other agents talk to. Quiverlane is a library with no agent endpoint, so there is nothing to advertise. Skip it.
- **llms.txt:** it belongs to `samber/developer-relations-skills@coding-agent-docs-optimization`, which I haven't run. It's cheap and harmless, but it doesn't fix the version problem. Agents that query Context7 never see it.
- **The likely cause:** anyone can add a public repo to Context7. The existing entry is a third-party index of your repo, built with someone else's parsing choices. Your `/docs/v1-reference` folder doesn't match Context7's default exclusion patterns (`*deprecated*`, `*legacy*`, `*archive*`, `old`). It is probably indexed as current docs, which would explain the v1 suggestions.
- **A limit on any fix:** agents that don't use Context7 still answer from their training data. This fix improves answers for the agents that do query it. It won't make every agent stop suggesting v1.

## Do this instead

1. **Confirm the cause (10 minutes).** Open your Context7 entry and query a v1-only API name. If v1 snippets come back as current, you've found it. Save the query and its output as your baseline.
2. **Claim the entry.** Commit one `context7.json` at the repo root on the default branch. It carries the generated public key, which unlocks version management and higher refresh limits.
3. **Configure the same file:**
   - `excludeFolders: ["docs/v1-reference"]`. This wins over `folders`.
   - `previousVersions`: your v1 git tags, so v1 stays queryable as v1 instead of leaking into current.
   - `projectTitle` (max 100 characters) and `description` (max 500). Plain facts only. Agent instructions and promotion are rejected.
   - `rules`: for example, "v2 is current; v1 APIs are removed."
   - Option: rename the folder to something like `docs/v1-legacy` so the default exclusions catch it too. It's optional, and it breaks existing links.
4. **Add a refresh call on push to the default branch.** Long-tail libraries refresh on request only once the docs are up to 45 days old. Without it, you serve stale docs for weeks.
5. **Re-run the step 1 query after the refresh.** If v1 snippets are gone, the fix worked. If they remain, check the exclusion path first.

## Plan, trimmed to your situation

Quiverlane is a library with docs, a repo and no signup, app or API. I haven't asked you the interview questions. These are the defaults I used, and you can overturn any of them:

- **Answers 8–10:** no hard date, a standing channel, and effort capped at config-only (a maintainer's time, not a quarter of engineering).
- **Class x surface:** the only surfaces that matter are docs and the repo. The default is allow for every class, and the training-crawler cell is your call. Nothing here needs enforcement beyond a quick check that your docs host isn't running a "block AI bots" preset.

| Rung | Verdict |
| --- | --- |
| A. Measurement | Keep, shrunk. Use the canary query before and after. Add docs-site referrer or analytics classification only if you already have it. |
| B. Docs markdown and Context7 claim | **Do first.** This is the fix above. |
| C. Credentials and delegation | Deleted: no API, so nothing for an agent to authenticate to. |
| D. Skill plus CLI | Deleted: no CLI. A config-only ceiling deletes it too. |
| E. MCP server | Deleted: no evidence of shell-less clients. Revisit if users ask for one. |
| F. Provision-then-claim | Deleted: no signup. |
| G. Agent card and api-catalog | Deleted: no agent endpoint and no OpenAPI spec. |

**Agent-safe API checklist:** not applicable, since there is no API.

## Questions I need answered

1. Does the Context7 entry actually serve v1 content? Paste what your v1-only query returns.
2. Is the docs site behind a CDN with an AI-bot preset? Ignore this if the docs are served only from GitHub.
3. Do you want v1 queryable as a labelled version through `previousVersions`, or gone entirely?