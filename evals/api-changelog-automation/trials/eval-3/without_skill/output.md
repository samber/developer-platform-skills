# Is "more oasdiff checks, fail-on WARN" the fix?

**No.** It helps with one of the three incidents at best, and only if the spec changed in that PR. Do it anyway because it's cheap, but it isn't the fix.

## Why the gate stayed green

oasdiff compares spec to spec. It never looks at the running service. The changelog is generated from the same spec diff, so it has the same blind spot.

| Change | Visible to oasdiff? | Why |
|---|---|---|
| Default page size 100 → 20 | Only if `default: 100` was declared on the parameter and changed in the same PR | oasdiff has a default-value-changed check. Verify its level in the oasdiff checks docs, because that decides whether `fail-on WARN` would catch it. If the default lived only in code or prose, it is invisible. |
| `note` rejected above 500 chars in the handler | No | The handler enforces a limit the spec never states. If the spec had `maxLength`, oasdiff would flag a decrease as an error. The code and the spec had silently drifted apart. |
| Rate limit 600 → 300 req/min | No | OpenAPI has no native rate-limit model. The limit lives in gateway or app config. |

Check this against your three PRs: did each one touch the spec, and what did the spec say before? I'm inferring the above from your description, not from your repo. The answer tells you which gap each incident fell into.

**Root cause:** you gated spec changes, but partners depend on behavior. Defaults, limits, quotas and validation rules are all client-observable. Only some of them are written in the spec.

## What to automate

Ordered by value per effort.

### 1. Make the spec the single source of truth for client-observable limits

- Declare the page size `default` and `maximum`, and `maxLength: 500` on `note`, in the spec.
- Declare rate limits per operation, for example an `x-ratelimit` extension, and emit `RateLimit-Policy` response headers.
- Generate the handler validation from the spec, using request-validation middleware driven by the spec file. The code then cannot enforce a rule the spec doesn't state.
- Once limits are in the spec, oasdiff can see changes to them. This is what makes the oasdiff upgrade worth doing.

### 2. Test the running service against the spec in CI

- Run a conformance test (Schemathesis or similar) against the PR build. It catches code that rejects what the spec allows.
- Add boundary tests for each declared limit: exactly at the limit, and one over.
- Add a response-diff test. Replay a recorded corpus of real partner requests, with anonymised or synthetic bodies, against `main` and against the PR. Diff status codes and item counts. A page-size change from 100 to 20 shows up immediately as a diff.
- If your biggest partners can supply consumer contracts, such as Pact bi-directional contracts with OpenAPI, include them.

### 3. Put rate limits and other gateway config in code, and diff them

- Keep gateway policy in the repo.
- Add a CI rule that any decrease in a limit, a default or a max requires an `api-behavior: tightening` label. Applying that label forces a changelog entry and the notice process in step 5.
- Add CODEOWNERS on three paths: the spec, the gateway config, and the validation code. API governance reviews all three.

### 4. Shadow-mode every tightening before enforcement (biggest prevention lever)

- For a new validation rule or a lower limit, ship it log-only first. Emit a "would reject" or "would throttle" metric per API key.
- Gate enforcement on that metric. For example, enforce only when no key above a set traffic share would be affected, or when affected partners have been notified.
- This would have shown the three partners hitting `note` > 500 and the 300 req/min ceiling before anything broke.

### 5. Close the changelog gap by process plus automation

- Generate the changelog from several sources: `oasdiff changelog`, the gateway config diff, and a required `changelog.d/` entry (changesets style).
- Add a PR template question, "Does a client-visible behavior change?", and a CI check that the label matches the presence of a changelog entry. Code can't reliably detect semantic change, so this human-judgment gate is the backstop for what automation misses.
- Treat tightening as breaking in your policy: minimum notice window, `Deprecation`/`Sunset` headers where applicable, and an email to the owners of keys that are actually affected (from step 4's metric).

### 6. Detect fast after deploy

- Alert on per-partner 4xx, 422 and 429 rates against a baseline, with a deploy marker on the dashboard.
- Roll out behavior changes behind a flag, staged by key: internal first, then a small percentage, then everyone.
- Even with all of the above, this shortens "broke three partners for a month" to hours.

## The VP's proposal, scoped correctly

Do it, with these caveats:

- Set `--fail-on WARN` and enable the optional checks you care about. Check the levels in the oasdiff docs rather than assuming.
- Use oasdiff's ignore files for accepted warnings. Require a written reason for each entry, reviewed by API governance, or people will bulk-ignore the noise.
- Confirm the baseline spec is the one you actually published (the last release or tag), not just the previous commit.
- State clearly in the postmortem that this closes the spec-visible gap only.

## Suggested sequence

1. **This week:** classify the three incidents into the three gaps above, switch on `fail-on WARN` with a reviewed ignore file, and add the PR label and changelog check.
2. **Next two weeks:** move limits and defaults into the spec, add CODEOWNERS, and put the gateway config under diff.
3. **Next month:** add spec-driven validation, conformance and boundary tests, and the replay diff.
4. **Next quarter:** shadow mode, staged rollout and per-partner alerts.

Success metric: zero client-observable behavior changes that ship without a changelog entry, and time-to-detect on a partner-facing regression under one hour.