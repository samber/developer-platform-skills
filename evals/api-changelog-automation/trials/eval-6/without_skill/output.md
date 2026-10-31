# Fenmoor API breaking-change gate

I can't see Fenmoor's repo, so this is a drop-in kit with stated assumptions: GitHub Actions, spec at `openapi.yaml`, default branch `main`. I haven't run any of it. Fix those paths, pin the oasdiff version you tested, and run the self-test (step 4).

## Scope call: what fits in one engineer-day

| Ask | Verdict | Why |
|---|---|---|
| oasdiff gate, required in CI | ✅ Do now (about 3h) | This is the CTO's "now". |
| Written breaking-change policy | ✅ Do now (about 1h) | The gate enforces a policy, so it needs one. Today it enforces whatever oasdiff's defaults say. |
| Approvals flow | ✅ Minimal now (about 1h) | A label plus CODEOWNERS covers it. A real workflow is a later project. |
| Changelog | ⚠️ Per-PR summary now (about 30min). Feed later. | oasdiff generates the diff text. A published feed needs a release process. |
| Usage analytics | ❌ Not this week | It needs gateway or log data I can't see, and it's a project of its own. |

The first four rows fit in the day. Cutting analytics is the only way to get there.

⚠️ **The gate only sees the spec, not the code.** The spec is hand-written, so someone can rename a field in code, leave `openapi.yaml` untouched, and the gate passes. That may be exactly how your partner got burned. The fix is a contract check that validates real responses against the spec. For example, run schemathesis or a response validator in your integration tests. I'd put that at 1–2 days and schedule it next. Until then, say "blocks spec-visible breaks" to the CTO, not "blocks breaking changes".

## 1. Policy (draft for CTO sign-off)

Save this as `docs/api-compatibility-policy.md`. It's a draft that records what "everybody kind of knows". Get the CTO to confirm it in 30 minutes.

```markdown
# API compatibility policy

Applies to the public Fenmoor API described in `openapi.yaml`.

## Breaking (blocked in CI, needs approval)
- Remove or rename an endpoint, method, parameter, or response field.
- Change a field's type, format, or enum values (removing a value).
- Make an optional request field or parameter required.
- Add a required request field or parameter.
- Narrow accepted values (lower max, higher min, stricter pattern).
- Remove a response status code clients rely on.
- Change authentication or scopes required for an endpoint.

## Non-breaking (allowed)
- Add an endpoint.
- Add an optional request field or parameter.
- Add a response field.
- Add an enum value to a response (clients must tolerate unknown values).
- Loosen validation.

## Exceptions
- A breaking change ships only with the `breaking-change-approved` label, approved by `@fenmoor/api-owners`, and a deprecation notice period of [N days: CTO to set].
- Behavior changes invisible to the spec (semantics, defaults, rate limits) are not covered by the gate. Reviewers check them by hand.

Owner: [name]. Review this policy quarterly.
```

The "enum value added to a response" line is a judgment call. oasdiff treats it as a warning, not an error. Confirm it with the CTO.

## 2. The gate

`.github/workflows/api-breaking-change.yml`:

```yaml
name: api-breaking-change

on:
  pull_request:
    # No `paths:` filter. A required check that is skipped by a path filter
    # stays "pending" and blocks every unrelated PR. Skip inside the job instead.
    types: [opened, synchronize, reopened, labeled, unlabeled]

permissions:
  contents: read

env:
  SPEC_PATH: openapi.yaml
  # Pin the version you tested; do not use @latest in a gate.
  OASDIFF_VERSION: v1.0.0 # TODO: replace with the pinned release you verified

jobs:
  oasdiff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install oasdiff
        run: go install github.com/oasdiff/oasdiff@${OASDIFF_VERSION}

      - name: Self-test (gate must fail on a known rename)
        run: |
          if oasdiff breaking api-gate-fixtures/base.yaml api-gate-fixtures/renamed-field.yaml --fail-on ERR; then
            echo "::error::Self-test failed: oasdiff did not flag the renamed field. Gate is blind."
            exit 1
          fi

      - name: Compare against base branch
        id: diff
        env:
          BASE_REF: ${{ github.base_ref }}
          APPROVED: ${{ contains(github.event.pull_request.labels.*.name, 'breaking-change-approved') }}
        run: |
          set +e
          git show "origin/${BASE_REF}:${SPEC_PATH}" > /tmp/base.yaml || {
            echo "::error::Cannot read ${SPEC_PATH} on origin/${BASE_REF}"; exit 1; }

          oasdiff breaking /tmp/base.yaml "${SPEC_PATH}" --fail-on ERR > /tmp/breaking.txt
          breaking_rc=$?
          oasdiff changelog /tmp/base.yaml "${SPEC_PATH}" --format markdown > /tmp/changelog.md

          {
            echo "## API changes"; cat /tmp/changelog.md
            echo; echo "## Breaking-change check"; echo '```'; cat /tmp/breaking.txt; echo '```'
          } >> "$GITHUB_STEP_SUMMARY"

          if [ "$breaking_rc" -eq 0 ]; then
            echo "No breaking changes."; exit 0
          fi
          if [ "$APPROVED" = "true" ]; then
            echo "::warning::Breaking changes present but 'breaking-change-approved' label is set."
            exit 0
          fi
          echo "::error::Breaking API change. See docs/api-compatibility-policy.md. Needs the 'breaking-change-approved' label."
          exit 1
```

Fixtures, so the self-test can fail:

```yaml
# api-gate-fixtures/base.yaml
openapi: 3.0.3
info: {title: fixture, version: "1"}
paths:
  /widgets:
    get:
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                type: object
                properties:
                  customer_id: {type: string}
```

`api-gate-fixtures/renamed-field.yaml` is the same file with `customer_id` renamed to `customerId`.

Commands to run:

```bash
# Run the check locally before pushing the workflow
oasdiff breaking api-gate-fixtures/base.yaml api-gate-fixtures/renamed-field.yaml --fail-on ERR; echo "exit=$?"
```

The expected exit code is non-zero. If it's 0, stop. Check which severity oasdiff assigns to a response-property removal in your pinned version before trusting the gate.

## 3. Approvals (minimal)

1. `.github/CODEOWNERS`:
   ```
   /openapi.yaml  @fenmoor/api-owners
   /docs/api-compatibility-policy.md  @fenmoor/api-owners
   ```
2. Create the `breaking-change-approved` label.
3. Branch protection on `main` (**changes repo settings**):
   - Require status check `oasdiff`.
   - Require code-owner review.
   - Make the rule apply to admins too. Otherwise the CTO's "blocked" has a bypass.

Known limit: anyone with triage rights can add the label, so the label alone is not an approval. The CODEOWNERS review is the real approval, and the label only tells CI that review happened. A stricter version would be a check that verifies the labeler is in `api-owners`. Do it later.

## 4. Verify before announcing

1. Open a throwaway PR that renames a response field in `openapi.yaml`. Expected: red `oasdiff` check, merge blocked.
2. Add the label. Expected: the check goes green, but merge still needs the code-owner review.
3. Open a PR that only adds an optional response field. Expected: green, no label needed.
4. Open a PR that doesn't touch the spec. Expected: green, with the check present, not skipped.
5. Confirm oasdiff parses your real spec. A hand-written spec with `$ref` problems will fail loudly. Fix that first, since it can eat the afternoon.

## 5. Deferred, with sizing

- **Changelog feed (about half a day).** On tag push, run `oasdiff changelog <prev-tag-spec> <this-tag-spec> --format markdown` and append the output to `CHANGELOG.md` or a docs page. The per-PR summary above already gives you the content.
- **Contract testing against real responses (1–2 days).** This is the biggest remaining hole (see the warning above).
- **Usage analytics (about 3–5 days, depends on logging).** It answers "who calls this field?", which turns approvals from guesswork into a decision. It needs per-key request logs with endpoint, and ideally field-level data, which most gateways don't give you. Answer these first: what gateway or logs do you have, and do they carry the API key?
- **Stricter approvals (about half a day).** Add the check that verifies the labeler is in `api-owners`, or move to an oasdiff ignore-file reviewed by CODEOWNERS. Either gives you an audit trail of accepted breaks.

## Suggested day plan

| Time | Task |
|---|---|
| 0:00–0:45 | Run oasdiff locally on the real spec and fix any parse issues. |
| 0:45–1:45 | Workflow, fixtures, self-test. |
| 1:45–2:45 | Policy draft, CODEOWNERS, label. Send the policy to the CTO. |
| 2:45–3:45 | Run the five verification PRs above. |
| 3:45–4:15 | Turn on branch protection. |
| Rest | Buffer, since spec parse trouble is the usual overrun. Start the changelog step if time remains. |

## Questions that change this

1. Is CI really GitHub Actions? If not, the oasdiff commands carry over and the YAML doesn't.
2. Is `openapi.yaml` the only spec, or are there per-version specs?
3. Does any generated artifact (SDKs, docs) build from the spec? If so, they inherit spec drift.
4. Who is the named owner of the policy and the `api-owners` team?