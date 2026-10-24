# Decision

**Go with the `workflow_run` split, with four changes to the engineer's design. Retire the `pull_request_target` macro today.**

## Why not `pull_request_target` + `head.sha`

That setup runs fork-authored code (tests, build scripts, `package.json` hooks) with a write token and the base repo's secrets. It is the "pwn request" pattern. Any drive-by PR can then exfiltrate secrets or push to the repo. The macro trades a missing comment for a repo takeover. It also reaches the people least able to audit it, small maintainers who copy the snippet.

Do two things alongside the retirement:
- Publish a short advisory telling past macro recipients to remove that trigger and rotate secrets the workflow could see.
- Make the action detect a fork PR with a read-only token and emit a `::notice::` plus a `$GITHUB_STEP_SUMMARY` table instead of skipping silently. Much of the "does nothing" complaint is the silence.

## Changes to the engineer's design

1. **Use `pull-requests: write` and `actions: read`, not `contents: write`.** Commenting does not need `contents: write`. Granting it lets a bug in the comment job push code.
2. **Do not trust the PR number in the artifact.** The `pull_request` run executes fork code, so the fork controls everything in the artifact. A hostile PR could write another PR's number and make the bot comment there. Resolve the PR from the trusted `workflow_run` event instead:
   - `workflow_run.pull_requests` is empty for fork PRs, so look the PR up by `head_sha` with `GET /repos/{owner}/{repo}/commits/{sha}/pulls`.
   - Accept it only if the PR is open and its head SHA and head repo match `workflow_run.head_sha` and `head_repository`.
   - I have not tested this lookup on a real fork PR. Do that before shipping.
3. **Treat the artifact as hostile data.**
   - Never `checkout` or execute anything from it.
   - Never put its contents in `${{ }}` inside `run:` steps.
   - Validate it against a strict schema and cap its size.
   - Coerce coverage numbers to numbers in the range 0–100.
   - Render paths inside a fenced block, with a fence longer than any backtick run in the path. Strip newlines and control characters. This stops markdown, HTML, and `@mention` injection.
4. **Keep the uncovered-file list, but bound it.** The list is a good feature, with two problems:
   - A big repo can exceed GitHub's 65,536-character comment limit, and the post then fails.
   - With one new comment per push, a full list repeated every push is noisy.

   Put the list in a collapsed `<details>`, cap it (suggest 200 paths, then "and N more"), and sort the files touched by the PR first. The paths are fork-reported, so label them that way.

**One-comment-per-push:** that is your call and it keeps permissions minimal, because the job never has to list or edit comments. The cost is PR clutter on active PRs. Updating one comment in place via a hidden marker is a small follow-up if maintainers complain.

**Interface caveat:** the docs below use `mode: collect` and `mode: comment` inputs. I invented those names to make the page concrete. Engineering must confirm or replace them.

---

# Docs page: Coverage comments on pull requests from forks

*Applies to `fennwater/coverage-action` v2 and later.*

## Why fork PRs get no comment

GitHub gives workflows triggered by `pull_request` from a fork a read-only `GITHUB_TOKEN` and no secrets. This is deliberate, since fork code is untrusted. The action cannot post a comment with a read-only token. It writes the coverage report to the job summary instead.

## Do not use `pull_request_target` to work around this

`pull_request_target` gives the workflow a write token and secrets. If it also checks out `github.event.pull_request.head.sha`, it runs the fork's code with those privileges. Any contributor can then steal your secrets or modify your repository.

**If you followed earlier Fennwater guidance to do this, remove it now.** Review the workflow runs from that period and rotate any secret that workflow could access.

## Recommended setup: two workflows

The first workflow runs the tests on the PR and uploads the coverage data. It has no write access. The second runs in the base repository, downloads that data, and posts the comment. It never runs PR code.

### 1. Collect coverage on `pull_request`

`.github/workflows/coverage.yml`:

```yaml
name: Coverage
on:
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test-coverage # your test command
      - uses: fennwater/coverage-action@v2 # pin to a full commit SHA
        with:
          mode: collect
          coverage-file: coverage.out
```

`collect` mode uploads an artifact named `fennwater-coverage`. It needs no token.

### 2. Comment from `workflow_run`

`.github/workflows/coverage-comment.yml`:

```yaml
name: Coverage comment
on:
  workflow_run:
    workflows: ["Coverage"] # must match the name in step 1
    types: [completed]

permissions:
  actions: read # download the artifact
  pull-requests: write # post the comment

jobs:
  comment:
    if: >
      github.event.workflow_run.event == 'pull_request' &&
      github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: fennwater/coverage-action@v2 # pin to a full commit SHA
        with:
          mode: comment
```

Do not add a `checkout` step and do not grant `contents: write`. The job needs neither.

`workflow_run` workflows only run from the default branch. The first PR that adds this file will not get a comment. Merge it, then open a new PR.

## What the comment contains

- Overall coverage and the change against the base branch.
- Coverage for files changed in the PR.
- A collapsed list of uncovered files, with PR-touched files first. It shows at most 200 paths, then "and N more".

Each push to the PR posts a new comment.

## How it stays safe

The artifact comes from the PR build, so the fork controls it. The comment job treats it as data only:

- It finds the PR from the `workflow_run` event, by head SHA and head repository. It ignores any PR number inside the artifact.
- It validates the artifact against a fixed schema and enforces size limits.
- It renders file paths in code blocks, so they cannot inject links, HTML, or mentions.
- It never executes artifact contents.

Because fork code produces the numbers, a malicious PR can report false coverage. **Treat the comment as informational. Do not use it as a required check or merge gate for fork PRs.**

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| No comment on a fork PR, only a job summary | You are on the single-workflow setup. Add the `workflow_run` workflow above. |
| Comment workflow never runs | The file is not on the default branch yet, or `workflows:` does not match the first workflow's `name:`. |
| `Resource not accessible by integration` | The comment job lacks `pull-requests: write`, or an org policy restricts the default token. |
| Artifact not found | The collect step did not run, or tests failed before it. The comment job runs only after a successful run. |
| No comment, "could not match a pull request" in the log | The head SHA no longer matches an open PR, usually because of a force-push or a closed PR. Push again. |
| Same-repo PRs also use two workflows now | Expected. One setup serves both. |

## Support macro replacement

> Fork PRs get a read-only token, so the action can't comment directly. Please don't switch to `pull_request_target` with a head checkout, which hands fork code your secrets. Use the two-workflow setup in our docs ("Coverage comments on pull requests from forks"). It runs tests with no privileges and posts the comment from a separate, trusted workflow.