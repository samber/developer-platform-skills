The YAML is below. I haven't run it, and I didn't read your repo, so the levels path and bucket details are assumptions (listed after the YAML).

```yaml
name: api

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

env:
  # Pin it. `@latest` lets an upstream release change what counts as breaking
  # in a PR that touched nothing. I couldn't verify a release tag from here:
  # set this to the version you tested locally.
  OASDIFF_VERSION: v1.11.7
  # Reviewer-facing file: header comment plus a third "why" column.
  LEVELS_FILE: api/oasdiff-levels.txt

jobs:
  breaking-changes:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          # The default is a depth-1 checkout with no origin/<base> ref, so
          # `origin/main:api/billing.yaml` cannot resolve.
          fetch-depth: 0

      - uses: actions/setup-go@v5
        with:
          go-version: stable

      - name: Install oasdiff
        run: go install "github.com/oasdiff/oasdiff@${OASDIFF_VERSION}"

      - name: Check breaking changes
        env:
          BASE_REF: ${{ github.base_ref }}
        run: |
          set -uo pipefail

          # oasdiff parses one "<check-id> <level>" pair per line. Strip the
          # comment header and the "why" column so the file stays readable
          # for reviewers. Fail on any malformed line.
          levels="$RUNNER_TEMP/levels.txt"
          awk '
            /^[[:space:]]*(#|$)/ { next }
            NF < 2 { printf "%s:%d: expected \"<id> <level> [why]\"\n", FILENAME, NR > "/dev/stderr"; bad = 1; next }
            { print $1, $2 }
            END { exit bad }
          ' "$LEVELS_FILE" > "$levels" || exit 1

          status=0
          for name in billing ledger payouts identity; do
            spec="api/${name}.yaml"
            base="$RUNNER_TEMP/base-${name}.yaml"
            if ! git cat-file -e "origin/${BASE_REF}:${spec}" 2>/dev/null; then
              echo "::notice file=${spec}::new on this branch, nothing to compare"
              continue
            fi
            git show "origin/${BASE_REF}:${spec}" > "$base"
            # No early exit: report all four specs in one run.
            "$(go env GOPATH)/bin/oasdiff" breaking "$base" "$spec" \
              --severity-levels "$levels" \
              --fail-on ERR \
              --format githubactions || status=1
          done
          exit $status

  publish-changelog:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    # Cloud credentials live only here. PR runs, including forks, never get them.
    permissions:
      contents: read
      id-token: write
    # Merges publish in order; never cancel a publish half-way.
    concurrency:
      group: publish-changelog
      cancel-in-progress: false
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-go@v5
        with:
          go-version: stable

      - name: Install oasdiff
        run: go install "github.com/oasdiff/oasdiff@${OASDIFF_VERSION}"

      - name: Build changelog.json
        env:
          BEFORE_SHA: ${{ github.event.before }}
        run: |
          set -euo pipefail

          levels="$RUNNER_TEMP/levels.txt"
          awk '
            /^[[:space:]]*(#|$)/ { next }
            NF < 2 { printf "%s:%d: expected \"<id> <level> [why]\"\n", FILENAME, NR > "/dev/stderr"; bad = 1; next }
            { print $1, $2 }
            END { exit bad }
          ' "$LEVELS_FILE" > "$levels"

          out="$RUNNER_TEMP/changelog.json"
          echo '{}' > "$out"
          for name in billing ledger payouts identity; do
            spec="api/${name}.yaml"
            base="$RUNNER_TEMP/base-${name}.yaml"
            changes='[]'
            # A new spec, or the first push on a branch (all-zero BEFORE_SHA),
            # has no base: publish an empty list for it.
            if git cat-file -e "${BEFORE_SHA}:${spec}" 2>/dev/null; then
              git show "${BEFORE_SHA}:${spec}" > "$base"
              changes="$("$(go env GOPATH)/bin/oasdiff" changelog "$base" "$spec" \
                --severity-levels "$levels" --format json | jq -c '. // []')"
            fi
            jq --arg svc "$name" --argjson c "$changes" '. + {($svc): $c}' "$out" > "$out.tmp"
            mv "$out.tmp" "$out"
          done
          jq --arg sha "$GITHUB_SHA" '{commit: $sha, services: .}' "$out" > "$out.tmp"
          mv "$out.tmp" "$out"
          jq . "$out"

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.DOCS_PUBLISH_ROLE_ARN }}
          aws-region: ${{ vars.DOCS_BUCKET_REGION }}

      - name: Publish
        env:
          BUCKET: ${{ vars.DOCS_BUCKET }}
        run: |
          set -euo pipefail
          src="$RUNNER_TEMP/changelog.json"
          # Immutable per-commit copy keeps history; `latest` is what the docs read.
          aws s3 cp "$src" "s3://${BUCKET}/changelog/${GITHUB_SHA}.json" \
            --content-type application/json
          aws s3 cp "$src" "s3://${BUCKET}/changelog/latest.json" \
            --content-type application/json --cache-control "max-age=60"
```

**What changed from the draft**
- **Checkout:** the default depth-1 checkout has no `origin/main`, so every `oasdiff` call would fail. The workflow now uses `fetch-depth: 0` and the PR's real base branch instead of a hard-coded `main`.
- **oasdiff version:** `@latest` is pinned through `OASDIFF_VERSION`.
- **Exit code:** `oasdiff breaking` exits 0 by default, so the draft could never fail a PR. It now uses `--fail-on ERR`.
- **All four specs:** all four files are checked in every run and the job fails at the end, so one bad spec doesn't hide the others. A spec that's new on the branch is skipped, since it has nothing to compare against.
- **Levels file:** I don't believe `--severity-levels` accepts comments or a third column, though I haven't confirmed this against oasdiff's parser. The job strips both into a temp file and rejects malformed lines. Reviewers keep the annotated file either way.
- **Publish job:** it is separate from the PR check and runs only on pushes to `main`. This keeps cloud credentials away from PR runs, including forks. It authenticates with OIDC, so there are no stored keys.

**Assumptions to confirm**
- **Levels path:** `api/oasdiff-levels.txt` is a guess. Change `LEVELS_FILE` to the real path.
- **Bucket type:** I assumed S3. For GCS, swap the last two steps for `google-github-actions/auth` and `gcloud storage cp`.
- **Repo variables:** the S3 steps need `DOCS_PUBLISH_ROLE_ARN`, `DOCS_BUCKET_REGION` and `DOCS_BUCKET` set as repo variables.
- **Changelog scope:** each publish holds only that merge's changes, not the full history. I write one file per commit under `changelog/<sha>.json` and overwrite `changelog/latest.json`. If the docs need a cumulative changelog, tell me and I'll merge each new entry into the existing file.
- **Action pinning:** actions are on major tags. Pin them to commit SHAs if your policy requires it.