I fixed the draft, but one request I could not do as asked. The job can't publish `changelog.json` on every merge to main, so it publishes when a release is cut instead (reasons after the YAML).

## Fixes to the draft

| Draft | Problem | Fix |
| --- | --- | --- |
| `actions/checkout` defaults | A shallow clone has no `origin/main:api/...` or merge base, so the diff fails. | `fetch-depth: 0`. |
| `oasdiff@latest` | Upgrades change classification with no spec change. | Pin `v1.34.1` and bump it deliberately. |
| `origin/main:` baseline | It blames the PR for changes merged to main earlier. | Use `git merge-base origin/<base> HEAD`. |
| Levels file with comment and "why" column | oasdiff accepts only `<check-id> <level>` per line and exits 106 otherwise. | Keep the human table in `api/severity-map.md` and generate the levels file from it on every run. |
| No `--fail-on` or ignore file | Warnings never fail, and accepted breaks have no record. | `--fail-on ERR`, plus an ignore file generated from `api/acks.json`. |
| Loop over four files | A file that is new in the PR has no base version and would crash the loop. | Skip files absent from the merge base. |

## Files to commit

- `api/severity-map.md`: your reviewer-friendly file. Put the header comment above the table, since only `|` rows with an id and a level are extracted. Keep your "why" column as `Policy line`:

  ```
  | Check id                           | Level | Policy line                                | Status      |
  | ---------------------------------- | ----- | ------------------------------------------ | ----------- |
  | response-property-enum-value-added | info  | every response enum is open                | provisional |
  | api-security-scope-removed         | err   | any auth change is announced               | provisional |
  ```

  Mark rows `provisional` until your breaking-change policy is signed.
- `api/acks.json` containing `[]`, and an empty `api/oasdiff-err-ignore.txt`. oasdiff exits 121 if the ignore file is missing.
- `tools/build-entries.py` and `tools/check-entry-trace.py`, copied from the skill so CI runs a reviewed copy.
- `.github/CODEOWNERS`: `/api/ @oakhollow/api-review`. This puts the specs, `severity-map.md` and `acks.json` under required review, so an author can't approve their own break.

## `.github/workflows/api-contract.yml` (PR gate)

```yaml
name: api-contract
on:
  pull_request:
    paths: ["api/**"]

permissions:
  contents: read

env:
  OASDIFF_VERSION: v1.34.1 # pinned; review the rule diff on every bump
  SPECS: "billing ledger payouts identity"

jobs:
  breaking:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # merge-base and git-revision baselines need history

      - uses: actions/setup-go@v5
        with:
          go-version: stable

      - name: Install pinned oasdiff
        run: go install "github.com/oasdiff/oasdiff@${OASDIFF_VERSION}"

      - name: Generate level and ignore files from the reviewed sources
        run: |
          awk -F'|' '$2 ~ /^ *[a-z0-9-]+ *$/ && $3 ~ /^ *(err|warn|info|none) *$/ {gsub(/ /,"",$2); gsub(/ /,"",$3); print $2, $3}' \
            api/severity-map.md > api/oasdiff-levels.txt
          test -s api/oasdiff-levels.txt   # an empty map would silently fall back to tool defaults
          python3 tools/build-entries.py --acks api/acks.json --ignore-out api/oasdiff-err-ignore.txt

      - name: Gate each spec against the merge base
        run: |
          base="$(git merge-base "origin/${{ github.base_ref }}" HEAD)"
          status=0
          for name in $SPECS; do
            if ! git cat-file -e "$base:api/$name.yaml" 2>/dev/null; then
              echo "::notice::api/$name.yaml is new in this PR, nothing to compare"
              continue
            fi
            echo "::group::$name"
            oasdiff breaking "$base:api/$name.yaml" "api/$name.yaml" \
              --severity-levels api/oasdiff-levels.txt \
              --err-ignore api/oasdiff-err-ignore.txt \
              --fail-on ERR -f githubactions || status=1
            echo "::endgroup::"
          done
          exit $status
```

## `.github/workflows/api-changelog-publish.yml` (release)

```yaml
name: api-changelog-publish
on:
  release:
    types: [published]

permissions:
  contents: read
  id-token: write # OIDC to the cloud provider; no stored bucket keys

env:
  OASDIFF_VERSION: v1.34.1
  SPECS: "billing ledger payouts identity"
  API_VERSION: ${{ github.event.release.tag_name }} # assumption: the tag is the API version

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # tags and history for the release baseline

      - uses: actions/setup-go@v5
        with:
          go-version: stable

      - name: Install pinned oasdiff
        run: go install "github.com/oasdiff/oasdiff@${OASDIFF_VERSION}"

      - name: Build and trace-check entries per spec
        run: |
          set -euo pipefail
          prev="$(git describe --tags --abbrev=0 "${GITHUB_REF_NAME}^")"   # last RELEASE, not main
          date="$(date -u +%F)"
          awk -F'|' '$2 ~ /^ *[a-z0-9-]+ *$/ && $3 ~ /^ *(err|warn|info|none) *$/ {gsub(/ /,"",$2); gsub(/ /,"",$3); print $2, $3}' \
            api/severity-map.md > api/oasdiff-levels.txt
          python3 tools/build-entries.py --acks api/acks.json --ignore-out api/oasdiff-err-ignore.txt
          mkdir -p out
          for name in $SPECS; do
            git cat-file -e "$prev:api/$name.yaml" 2>/dev/null || { echo "no baseline for $name, publish its entries by hand"; continue; }
            oasdiff changelog "$prev:api/$name.yaml" "api/$name.yaml" \
              --severity-levels api/oasdiff-levels.txt -f json > "out/$name.diff.json"
            # fingerprints carry no file name, so build and trace one spec at a time
            reviewed="changelog/$API_VERSION/$name.entries.json"   # human-completed summary/action_required
            if [ -f "$reviewed" ]; then cp "$reviewed" "out/$name.entries.json"; else
              python3 tools/build-entries.py --changelog "out/$name.diff.json" --api-version "$API_VERSION" \
                --date "$date" --fragments changes/ --acks api/acks.json --out "out/$name.entries.json" || true
            fi
            python3 tools/check-entry-trace.py --diff "out/$name.diff.json" --entries "out/$name.entries.json" \
              --fragments changes/ --api-version "$API_VERSION" --acks api/acks.json
          done
          jq -s --arg v "$API_VERSION" \
            '{feed_version: 1, api: "oakhollow-public-api", generated_at: (now | todate), entries: (map(.[]) | sort_by(.classification != "breaking"))}' \
            out/*.entries.json > changelog.json

      - uses: aws-actions/configure-aws-credentials@v4 # swap for your cloud's equivalent
        with:
          role-to-assume: ${{ vars.DOCS_PUBLISH_ROLE_ARN }}
          aws-region: ${{ vars.DOCS_BUCKET_REGION }}

      - name: Publish (only reached when every trace check passed)
        run: aws s3 cp changelog.json "s3://${{ vars.DOCS_BUCKET }}/changelog.json" --cache-control "max-age=300"
```

## Why publishing is on release, not on every merge

- **Baseline:** the published changelog must be diffed against the last released version, not main. Diffing against main splits one release into tiny diffs and loses the multi-PR total.
- **Human text:** `build-entries.py` leaves `summary` and `action_required` blank for a human. The trace check fails any breaking entry without an action, so an unattended publish on merge would either fail or publish empty entries.
- **Reviewed entries:** complete the entries and commit them as `changelog/<version>/<spec>.entries.json` before cutting the release. The job uses that file when it exists.
- **If you want a merge-time publish anyway:** I would publish a clearly labelled `unreleased/changelog.json` preview from main. It would not replace the released feed. Say so and I'll add the job.

## Assumptions to confirm

- **API version:** I assumed the release tag is the API version. If you use date or header versions, change `API_VERSION`.
- **Bucket:** I assumed an S3-style bucket reached through OIDC. Swap the credentials step if yours is GCS or another store.
- **Feed schema:** the `jq` step builds a simple feed (`feed_version`, `api`, `generated_at`, `entries`) that I wrote from the skill's description. Check it against your docs consumer.
- **Scripts:** I did not run the workflows or the two scripts. I only read the first 120 lines of `build-entries.py`.
- **Missing pieces:** the skill also wants a PR-template question for behavior changes (so they land in `changes/`) and a scheduled drift alarm against the served spec. Neither is in this YAML.