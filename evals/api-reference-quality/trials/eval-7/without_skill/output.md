# What to verify, and with what

## Why the current gate doesn't cover this

The docs build proves one thing: the spec parses and renders. Docs generated from the spec can't disagree with the spec, so that gate can't catch a spec that disagrees with the API. Your two problems are separate:

- **Problem A: the spec may not match the running API.** Nobody has tested it, so "honest" is unproven.
- **Problem B: the assistant calls endpoints that don't exist.** This may have nothing to do with spec accuracy. Models guess neighbours of real endpoints. If `GET /employees/{id}` exists, they try `DELETE /employees/{id}/archive`.

Optic is the right tool for one slice of this (breaking-change diffs) and not for the rest.

## Do first: get ground truth on problem B (about an hour)

Before building anything, pull the gateway or API 404 and 405 logs for the prospect's API key. Bucket each bad call into one of these:

1. **Wrong verb on a real path** (405). Docs likely don't say what's unsupported.
2. **Plausible sibling that doesn't exist** (404), such as a missing CRUD operation. This is guessing from naming patterns.
3. **Renamed or deprecated endpoint.** Old training data, or an old spec still indexed somewhere.
4. **Another vendor's endpoint.** Nothing you can fix.

The mix tells you which fix below matters. If you can't get these logs, ask the prospect for the failing requests.

## Verification layers

| # | Check | Direction | Tool | Where |
|---|---|---|---|---|
| 1 | Spec lint: operationIds, descriptions, examples, auth, error schemas | spec quality | Spectral or Redocly CLI | PR, blocking |
| 2 | **Route-set diff**: every spec `method+path` has a real route, and every real route is in the spec | spec ⇄ code | Small script: dump the router or gateway route table, diff against the spec | PR or post-deploy, blocking |
| 3 | **Conformance against staging**: status codes, response schemas, content types, no 5xx on valid input | spec → running API | Schemathesis | Post-deploy to staging |
| 4 | **Breaking-change diff** against the last release | spec vs. previous spec | oasdiff, or Optic | PR, blocking |
| 5 | Doc code samples and quickstart actually execute | docs → API | Run them as a smoke test against staging | Nightly |
| 6 | **Agent hallucination rate**: do assistants call non-existent endpoints? | docs → agents | Small eval harness (below) | Weekly, tracked |

**Layer 2 is cheap and probably the most valuable.** With 74 endpoints it's a set comparison. It catches both phantom endpoints (documented, not real) and shadow endpoints (real, undocumented). Schemathesis only tests what the spec declares, so it can't find shadow endpoints.

**Layer 3** is the missing "tested against the running API" step.
- Schemathesis generates property-based requests from the spec. It checks that responses match the declared schemas and status codes, flags undeclared status codes, and flags 5xx errors.
- Expect a noisy first run, probably dozens of findings. Baseline it, then ratchet. Start as a non-blocking nightly job and promote it to a gate once the findings are triaged.
- It needs a running API, so it can't gate the merge the way the docs build does. Run it right after the staging deploy and block promotion to prod. Gating the PR itself needs an ephemeral environment.
- Since this is HR-tech, staging must hold synthetic data only. Stateful fuzzing writes and deletes, so use a dedicated test tenant, auth fixtures, and rate limits that won't trip alerts.

**Layer 4, Optic or oasdiff.**
- Optic does diffing well, and its capture mode can check recorded traffic against the spec.
- Check its maintenance status first. After the Atlassian acquisition the open-source project's future was uncertain, and I can't confirm its current state. Look at recent commits and releases before adopting it.
- `oasdiff` covers the same breaking-change diff, is actively maintained, and is a single binary: `oasdiff breaking base.yaml head.yaml --fail-on ERR`.
- Either is fine. Pick whichever you can confirm is maintained.

**Layer 6, agent eval.**
- Write 20–30 realistic tasks, such as "list all employees hired last month and export them".
- Run a couple of popular coding assistants against them with your docs available.
- Extract every URL and method from the output and match it against the spec's path templates. The metric is the percentage of calls that don't exist.
- It tells you whether the fixes below work. Without it you're guessing.

## Fixes for problem B

Prioritise by the bucket mix from the logs.

1. **Make the 404 and 405 responses self-correcting.** Return a structured body with the nearest valid paths, the allowed methods (`Allow` header on 405), and a link to the spec. An agent in a loop recovers from this on its own. It's the highest-leverage fix and doesn't depend on the agent reading your docs.
2. **Publish the spec at a stable, crawlable URL** (`/openapi.json`) and add `llms.txt`, plus a markdown version of each reference page. Many docs sites render client-side, which agents can't read.
3. **Add a flat index of all 74 operations** on one page, one line each (`METHOD /path: purpose`).
4. **State what doesn't exist.** For example: "There is no bulk delete. Use X." Guessing is concentrated where an expected sibling is missing.
5. **Check operationIds and summaries.** Vague or inconsistent names invite invented siblings.
6. **Consider an MCP server** generated from the spec. This is later work, once the basics are done.

None of this guarantees zero hallucinated calls. The layer-6 metric tells you how far you've got.

## Order of work

1. **Day 1:** pull the 404 and 405 logs, bucket the bad calls, and write the route-set diff (layer 2).
2. **Week 1:** add Spectral (layer 1) and oasdiff or Optic (layer 4) on PRs. Run Schemathesis nightly against staging, non-blocking.
3. **Week 2:** ship the self-correcting 404 body, `llms.txt`, and the flat index. Build the eval harness and record a baseline.
4. **Week 3 onward:** triage the Schemathesis findings, then block promotion to prod on conformance. Re-run the eval after each docs change.

## Two questions that change the plan

- **Is the spec hand-written or generated from code annotations?** Hand-written specs drift more. Code-first specs still drift on nullability, required fields, and error responses.
- **Does the staging deploy run the same build as prod?** If staging lags or differs, conformance results mean little.