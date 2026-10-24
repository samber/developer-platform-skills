**Decision: use the engineer's `workflow_run` split, with four fixes. Drop the `pull_request_target` macro today.**

## Why

- **`pull_request_target` is unsafe.** It runs with base-repo secrets. Checking out `head.sha` runs fork code with them. GitHub blocks it by default in public repos from 2026-12-02. The skill says never recommend it for fork PRs.
- **The split is the right pattern.** The fork job runs with no credentials and only uploads an artifact. A separate `workflow_run` job posts the comment and never executes fork code.
- **Four fixes to the proposal:**
  1. **Do not read the PR number from the artifact.** A fork controls it. A malicious fork could name another PR and overwrite its comment. Resolve the PR from `workflow_run.head_sha` through the API. Require that PR's head SHA to equal it.
  2. **Replace `contents: write`.** Use `actions: read` plus `pull-requests: write`. Write on contents is a push-capable token for no reason.
  3. **Upsert one comment instead of a new one per push.** Find it by a hidden marker authored by the token's own identity. You said new comments are fine. I advise against it: a 20-push PR gets 20 comments. Say if you want to keep it.
  4. **Treat the report as data.** Cap its size and validate its schema. Escape every path before it goes into Markdown. The paths come from the fork's tree, so they are attacker-controlled text.
- **The uncovered-file list stays.** Customers like it. Cap it at 20 files, ranked by uncovered lines. Add "and N more" and put the full list in the job summary. GitHub rejects a comment body over 65,536 characters.

## Provisional assumptions

I have not seen the action's code. Interview answers are missing, so the plan is provisional on these:

| Assumption | Drives |
| --- | --- |
| The action can run without a token and emit a JSON report file. If not, add optional `post-comment: false` and `report-path` inputs in a **minor** release. | The contract (step 3) |
| Report shape is `{total, base, uncovered:[{path,lines}]}`. | Validation code below |
| Customers run github.com, not GHES. | Fork behavior (step 4) |

**Next step:** confirm the first assumption. Then ship the inputs in a minor release and publish the page below.

---

# Coverage comments on pull requests from forks

Fennwater's `coverage-action` posts a coverage-diff comment on pull requests. GitHub gives pull requests from forks a read-only token and no secrets. The comment cannot be posted from the same workflow. This page shows a two-workflow setup that works for forks.

If you accept pull requests only from branches in your own repository, the basic setup is enough. Use the split only for forks.

## Do not use `pull_request_target`

Do not switch the trigger to `pull_request_target`, and do not check out `github.event.pull_request.head.sha`. This runs untrusted fork code with your repository's secrets and a write token. GitHub blocks this trigger by default in public repositories from 2026-12-02. Remove it from your workflows if an older support answer told you to add it.

## How the split works

1. **Workflow 1** runs on `pull_request`. It has no credentials. It runs your tests and the action, then uploads the coverage report as an artifact.
2. **Workflow 2** runs on `workflow_run`, after workflow 1 succeeds. It downloads the artifact, checks it, finds the pull request, and posts one comment. It never checks out or runs fork code.

## Workflow 1: collect coverage

```yaml
name: Coverage
on: pull_request

permissions: {}

jobs:
  coverage:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<full-sha> # v5
        with:
          persist-credentials: false
      - name: Run tests
        run: make test-coverage
      - uses: fennwater/coverage-action@<full-sha> # vX.Y.Z
        with:
          post-comment: "false"
          report-path: coverage-report/report.json
      - uses: actions/upload-artifact@<full-sha> # v4
        with:
          name: coverage-report
          path: coverage-report/report.json
          retention-days: 1
```

## Workflow 2: post the comment

The workflow file must be on your default branch. GitHub runs `workflow_run` workflows from there, so a pull request cannot change them.

```yaml
name: Coverage comment
on:
  # zizmor: ignore[dangerous-triggers] reads the artifact as data and never runs fork code
  workflow_run:
    workflows: [Coverage]
    types: [completed]

permissions: {}

jobs:
  comment:
    if: github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    permissions:
      actions: read
      pull-requests: write
    steps:
      - uses: actions/download-artifact@<full-sha> # v5
        with:
          name: coverage-report
          run-id: ${{ github.event.workflow_run.id }}
          github-token: ${{ github.token }}
          path: report
      - uses: actions/github-script@<full-sha> # v8
        env:
          HEAD_SHA: ${{ github.event.workflow_run.head_sha }}
        with:
          script: |
            const fs = require('fs');
            const MARKER = '<!-- fennwater-coverage -->';
            const MAX_REPORT_BYTES = 1_000_000; // a report larger than this is not ours
            const MAX_FILES_SHOWN = 20; // keeps the comment far below GitHub's 65,536-character cap
            const SAFE_PATH = /^[\w.@+\/-]{1,300}$/; // rejects backticks, newlines and Markdown syntax

            const file = 'report/report.json';
            if (fs.statSync(file).size > MAX_REPORT_BYTES) throw new Error('report too large');
            const r = JSON.parse(fs.readFileSync(file, 'utf8'));
            if (![r.total, r.base].every(Number.isFinite) || !Array.isArray(r.uncovered)) {
              throw new Error('report does not match the expected schema');
            }

            // Never trust a PR number from the artifact. Resolve it from the commit.
            const { owner, repo } = context.repo;
            const { data: prs } = await github.rest.repos.listPullRequestsAssociatedWithCommit({
              owner, repo, commit_sha: process.env.HEAD_SHA,
            });
            const pr = prs.find((p) => p.state === 'open' && p.head.sha === process.env.HEAD_SHA);
            if (!pr) { core.warning('No open pull request has this head commit'); return; }

            const files = r.uncovered
              .filter((f) => typeof f.path === 'string' && SAFE_PATH.test(f.path) && Number.isInteger(f.lines))
              .sort((a, b) => b.lines - a.lines);
            const shown = files.slice(0, MAX_FILES_SHOWN);
            const lines = [
              MARKER,
              `**Coverage: ${r.total.toFixed(1)}%** (base ${r.base.toFixed(1)}%)`,
              '',
              ...shown.map((f) => `- \`${f.path}\`: ${f.lines} uncovered lines`),
            ];
            if (files.length > shown.length) lines.push(`- and ${files.length - shown.length} more files`);
            const body = lines.join('\n');

            // Update our own comment. Anyone can paste the marker, so match the author too.
            const comments = await github.paginate(github.rest.issues.listComments, {
              owner, repo, issue_number: pr.number,
            });
            const mine = comments.find((c) => c.user.login === 'github-actions[bot]' && c.body.includes(MARKER));
            if (mine) {
              await github.rest.issues.updateComment({ owner, repo, comment_id: mine.id, body });
            } else {
              await github.rest.issues.createComment({ owner, repo, issue_number: pr.number, body });
            }
```

## Permissions

| Workflow | Permissions | Why |
| --- | --- | --- |
| 1 | `contents: read` | Checkout only. No secrets, no write token. |
| 2 | `actions: read` | Download the artifact from workflow 1's run. |
| 2 | `pull-requests: write` | Post and update the comment. |

Do not grant `contents: write`. Nothing here needs it.

## What the comment shows

- Total coverage and the change against the base branch.
- Up to 20 files with the most uncovered lines, then a count of the rest.
- File paths come from the pull request's code. The workflow drops any path with unusual characters before posting.

## Limits

- The comment appears after workflow 1 finishes, not during it.
- Workflow 2 only runs when workflow 1 succeeds. Failed test runs get no comment.
- In public repositories the comment is public. It shows counts and file paths only.
- Pin every `uses:` by full commit SHA with a version comment, so Dependabot can update it.