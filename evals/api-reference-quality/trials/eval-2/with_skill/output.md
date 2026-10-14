# Parcelry: docs-can't-regress plan

I read the skill and its three reference files. I haven't seen your spec or CI config, so some of this rests on assumptions, which I list at the end.

## Verdict

Your docs are already generated from the spec (Redocly), so drift from hand-edited pages isn't your problem. The two regressions happened because nothing checks the spec before merge. Redocly renders whatever it's given, and an endpoint with no description builds fine.

The fix is a **lint gate only**, built in 3 weeks. It's an afternoon of setup, plus the backfill time. Contract tests are out of this plan.

## Why lint-only

- **No safe environment.** Every call books real freight and costs money, and a sandbox is at least two quarters out. That puts it in April 2027 at the earliest.
- **Contract tests are deleted, not postponed.** The skill removes the rung when nothing can safely receive requests. "We'll add contract tests too" is the line that appears in every plan and never ships.
- **Schemathesis would be dangerous here.** Property-based tests fire generated requests at every operation. Against production, that means random `POST`s to book freight.
- **The deadline agrees.** Three weeks to the board favours the cheapest gate that closes the actual hole.

## Contract tests: what to tell your VP

"Later this year" isn't achievable. Two quarters from today is April 2027, so the earliest honest date is Q2 2027.

I'd put it in the plan as a dependency, not a date:

> **Contract tests: unlock trigger = sandbox exists.** Platform team owns the sandbox (est. Q2 2027+). When it ships, add Schemathesis against the sandbox and a breaking-change diff, and promote the gate on the same day.

That keeps the board slide honest and gives the platform team a visible reason to prioritise the sandbox.

## What the gate does and doesn't prove

- **It proves the spec is complete.** Every operation has a description, an operationId, and documented 4xx responses.
- **It doesn't prove the spec is true.** A spec can pass lint and still lie about the API. Only contract tests catch that, and they need the sandbox.
- **Wording for the board:** say "documentation completeness can't regress", not "docs are accurate". The 100% census and zero-lint-error gates below are your definition of done, not an industry standard.

## Tooling

You already use Redocly, so use **Redocly CLI** as the linter. That means no new vendor and one config file. Spectral and Vacuum are equivalent alternatives if you outgrow it.

`redocly.yaml` (check rule names against your CLI version):

```yaml
extends:
  - recommended
rules:
  operation-description: error
  operation-summary: error
  operation-operationId: error
  operation-operationId-unique: error
  operation-4xx-response: error
  no-invalid-media-type-examples: error
```

Add a custom assertion for error documentation: every 4xx/5xx response needs a description and an example. Use a shared `Error` schema with an enum of codes.

Lint can enforce that error docs exist. It can't judge whether the cause and fix are any good, so reviewers still check that.

CI (GitHub Actions or equivalent):

1. Run `redocly lint openapi.yaml --format=github-actions` on every PR touching the spec.
2. Mark it a **required status check** on the default branch.
3. Make the docs deploy depend on it, so a failing spec never publishes.
4. Add CODEOWNERS on the spec file and on any lint-ignore file. The ignore file is an escape hatch, and without an owner it becomes a way to defeat the gate.
5. Add a PR template line: "API change includes its spec and description changes."

Optional: **oasdiff** compares two spec versions and flags breaking changes. It never calls the API, so it's safe today. That's my addition, not part of the skill's tier, so treat it as a bonus.

## Three-week schedule

| Week | Work | Pass condition |
|---|---|---|
| 1 | Census all 38 operations (spec vs published pages, both directions). Confirm no page or description is edited outside the spec. Run lint in **warn** mode and record the baseline. | Coverage table done. You know your real gap count. |
| 2 | Backfill every gap, with undocumented operations and missing 4xx/error docs first. Add the custom error assertion. | Zero warnings at your ruleset. |
| 3 | Flip to **error**, make it a required check, add CODEOWNERS and the PR template. Write the board slide. | A deliberately bad PR (no description) is blocked. |

Test the gate in week 3. Open a PR with a description-less endpoint and confirm it can't merge. That is your proof that the regression can't happen again.

## Gates in scope

- **Census coverage 100%:** every operation, parameter, response (including one 4xx), and error code documented with cause and fix, and no documented-but-removed endpoints. In scope.
- **Lint: zero errors** at the ruleset above. In scope.
- **Contract gate:** out of scope at this tier. Report it as "out of scope until sandbox", not "failed".
- **Snippet parity:** out of scope. Measure the percentage per language and record it as a finding.

## Benchmarks for the board

- **Stripe:** reference generated from the spec, and documentation quality is part of engineering ladders. You have the first. Week 3 starts on the second by putting docs in PR review.
- **Twilio:** per-endpoint error tables and CI-tested snippets. Your error assertion starts on the first. The second is later work.

## After this ships

- **Quarterly re-audit** against support tickets and docs-search misses.
- **Trends to track, not gate:** time-to-first-call (target under 10 minutes), and the share of tickets caused by missing docs.
- **If "inconsistent docs" complaints persist:** assign a dedicated docs owner.

## Assumptions to confirm

I couldn't ask these, so the plan assumes the answers:

1. The published pages come only from the spec, with no hand-edited overrides. If that's wrong, week 1 expands.
2. You have a CI system that supports required checks.
3. You ship no SDKs, or snippet parity isn't a board concern.
4. Nothing else gates the spec today.
5. The deadline is firm, and you want a standing gate rather than a one-off cleanup.

Send me the spec and I'll run the real census and replace the placeholder numbers.