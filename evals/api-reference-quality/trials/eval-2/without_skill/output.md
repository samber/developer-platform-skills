# Plan: make undocumented endpoints unmergeable

## Do this first

1. **Reframe the VP's promise.** "Docs can't regress again" can't be fully guaranteed. A linter checks that a description and error responses *exist and have the right shape*. It can't check that they're *true*. Promise this to the board: "No endpoint can merge without a description, documented errors, and examples. Enforced by CI, not by reviewers."
2. **Replay test (day 1, about 2 hours).** Run the new lint config against the two merge commits that regressed. If both fail, you have a demo for the board.

## Why this fits

Pages regenerate on merge, so the gate must sit *before* merge. You already run Redocly, so use **Redocly CLI `lint`**. Spectral would add a second ruleset language and a second tool for no gain. Everything below stays on the spec and never calls the API, so it costs nothing and can't book freight.

## Tooling

### 1. `redocly lint` with a strict `redocly.yaml`

```yaml
extends:
  - recommended
rules:
  operation-summary: error
  operation-operationId: error
  operation-operationId-unique: error
  operation-2xx-response: error
  operation-4xx-response: error
  tag-description: error
  no-invalid-media-type-examples: error   # examples must match their schema
  security-defined: error

# Custom rules. Syntax is from memory, so verify it against your CLI version
# during the replay test.
assert/operation-has-description:
  subject: { type: Operation, property: description }
  assertions: { defined: true, minLength: 40 }
  message: Every operation needs a real description (40+ chars).
  severity: error

assert/operation-documents-errors:
  subject: { type: Operation, property: responses }
  assertions: { required: ['400', '401', '403', '500'] }
  message: Document at least 400, 401, 403 and 500.
  severity: error

assert/errors-use-shared-schema:
  subject: { type: MediaType, property: schema, filterInParentKeys: ['400', '401', '403', '404', '409', '422', '500'] }
  assertions: { ref: '#/components/schemas/Error' }
  message: Error responses must use the shared Error schema.
  severity: error

assert/parameter-has-description:
  subject: { type: Parameter, property: description }
  assertions: { defined: true }
  severity: error
```

The 404-on-path-param rule and "409 on booking POSTs" need a small custom plugin. Put them in phase 2, not before the board.

### 2. Baseline so day-one adoption isn't a wall of red

- Run `redocly lint --generate-ignore-file`. This writes `.redocly.lint-ignore.yaml` and grandfathers existing violations by location.
- Any *new* endpoint, or any existing one that's touched, has no entry in that file, so it must pass in full.
- Burn the ignore file down in week 3 and report the count to the board. Make it shrink-only. A CODEOWNERS rule on that file should require docs-owner approval.

### 3. CI and merge protection (this is what actually makes it unbypassable)

- GitHub Actions job: `redocly lint` plus `redocly build-docs`. A docs build that fails to render also blocks the merge.
- Mark the job a **required status check** with **"include administrators"** on. The two regressions most likely got through because the gate was optional.
- Don't use path filters on the required job. A skipped required check stays "pending" and either blocks every PR or gets bypassed. Let it run on every PR, since it takes seconds.
- Lint the **bundled** root spec, not the split files.
- Add `CODEOWNERS` on `openapi/` requiring one docs reviewer. The linter checks shape, and a person checks that the text is correct.
- Optional: a PR comment with the Redocly preview link, so reviewers read the rendered page.
- Add `pre-commit` or an npm script running the same command, so authors see failures before CI does.

### 4. Add `oasdiff` (cheap, phase 2)

`oasdiff breaking` against `main` catches removed fields and changed types in the spec. It's also spec-only, so it's free and safe.

## Timeline (3 weeks)

| Week | Work | Done when |
|---|---|---|
| 1 | Write the config, run it in `warn` mode, replay the two regressions, generate the baseline | Both bad PRs fail locally |
| 2 | Flip to `error`, add the required check with admins included, CODEOWNERS, PR template | A deliberately bad PR is blocked and the board demo is ready |
| 3 | Burn down the ignore file (prioritise endpoints missing errors entirely), publish the metrics | Ignore file trending to 0 |

**Board metrics:**
- % of the 38 operations with a description and full error docs.
- Grandfathered violations remaining.
- PRs blocked by the gate.

## Contract tests: push back on "later this year"

The plan is sound, but the usual form of contract testing breaks your constraint. Schemathesis, Dredd and most Pact provider verification **fire real requests**. Against production, that books real freight. Pointing them at prod with "just be careful" isn't acceptable.

Also, contract tests catch a *different* problem. They catch spec-vs-behavior drift. Your two regressions were missing documentation, which the lint gate fixes. So contract tests aren't needed for the board deadline.

Here's a safe ladder for later this year, in order:

1. **Passive response validation (Q4, no cost, no risk).** Sample real production responses from gateway logs and validate them against the spec offline. Any validator will do, for example `openapi-response-validator` or Schemathesis's offline checks over recorded cases. It catches drift with zero new calls.
2. **Read-only contract tests (Q4/Q1).** Run Schemathesis against **GET endpoints only**, using an API key scoped read-only *at the auth layer*. A CLI flag like `--include-method GET` isn't enough, because a flag can be changed and key permissions can't.
3. **Full contract tests, including POST booking endpoints.** Two ways to get there:
   - Wait for the sandbox, which is more than two quarters out, so probably next year.
   - Ask the platform team for something smaller: a **test mode in the service's own CI** with the carrier adapters stubbed. That's a fraction of a full sandbox, and it may land this year. It's worth requesting now, since it unblocks both this and general testing.

Put 1 and 2 on the roadmap for this year. Put 3 on the roadmap *conditional on* the stubbed test mode or the sandbox.

## Risks

- **False confidence.** A description of "TODO TODO TODO …" passes `minLength`. That's why the human reviewer in CODEOWNERS stays.
- **Rule friction.** Requiring 403 and 500 on every operation may force boilerplate. Check the replay results, and loosen the list rather than let people add junk.
- **Two sources of truth.** If any docs content lives outside the spec, the gate doesn't cover it. Confirm that before the board meeting.

## Questions for you

1. Is the spec one file or split? That affects the bundling step.
2. Is CI on GitHub Actions? I assumed so.
3. Which Redocly CLI version are you on? I'd confirm the assertion syntax against it.