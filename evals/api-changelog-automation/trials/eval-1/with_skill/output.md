# Quillbridge: oasdiff in GitHub Actions, plus an automated changelog

I read the `api-changelog-automation` skill, its three references and the `build-entries.py` header. I did not run the workflows or oasdiff here, so treat the YAML as untested until it runs on a throwaway PR.

## Four things to settle first

1. **Main-vs-PR output can't feed the public changelog.** That diff answers "what does this PR break?", and it blames a PR for nothing merged earlier. The changelog needs the spec of the last released version as its baseline, per API version. A PR-time diff would split one release into many small diffs and lose the total. So the plan has two jobs:
   - PR gate: merge base vs PR.
   - Release job: last release tag vs now, once per version.

   Both use the same oasdiff and the same severity map.

2. **Your GET /invoices assumption is right, and it's the dangerous part.** The ordering change isn't in the spec, so oasdiff will report nothing, and a green check would let it ship unannounced to ~400 integrations.
   - It goes through the declared-change channel: a PR checkbox plus a change fragment (below).
   - On a date-versioned API it must reach only callers on the new version. If it applies to pinned `2025-11-01` or `2026-03-01` callers, that is a policy exception, not a normal release.
   - Add a contract test on the ordering.

3. **Your ~60-line ignore file is a record of hidden breaks, so it needs an audit before the gate goes live.** Don't carry it over. See "Ignore-file audit" below.

4. **Open question: today is 2026-10-30, but you called 2026-07-01 the next version.** That date has already passed.
   - Is it a typo, or has it shipped?
   - I used `2026-07-01` below, as you wrote it. It lives in one `VERSIONS` variable and one fragment, so changing it is cheap.

## Questions that change the design

- **Written breaking-change policy?** I assumed none. Every severity-map row is then marked `provisional` until policy sign-off, and the policy itself belongs to `api-versioning-policy`.
- **How does one Kotlin codebase serve three dates?**
  - The workflow assumes a `scripts/generate-specs.sh` that writes `api/specs/<version>.yaml` for each supported version. Springdoc can do this with one group per version, or a version-aware export.
  - I don't know your setup, so that script is yours to write.
- **Are internal or beta operations in the same spec?** If so, how are they marked? The workflow has a commented `--filter-extension x-internal` line for this.
- **Do you have per-operation usage telemetry?** I assumed no, so there is no usage-aware classification.
- **Where does the public changelog live** (page, RSS, JSON feed)? The publish step is a stub until you say.
- **Is the spec validated against the running service** (contract tests or traffic validation)? Without it, a green diff describes a document, not your API. List this as your first gap.

## Rungs and order

| Order | Rung | Effort |
| --- | --- | --- |
| 1 | PR gate | 1-2 h, mostly reviewing the severity map |
| 2 | Release diff + declared channel | Half a day, plus a habit |
| 3 | Approval record | A few hours, then minutes per break |
| 4 | Feed (JSON + Atom) | About a day |

Ship rung 1 first if you have a deadline, because it stops accidental breaks before anything else exists. The skill's default is rungs 1 and 2, with the approval record added when the first break is accepted.

**This is not fully automatic.** `build-entries.py` writes skeleton entries and leaves `summary` and `action_required` blank. A human (or a model, followed by a trace check) fills them in, and publishing only happens after the trace check passes.

## Repo layout

```
api/
  specs/2025-11-01.yaml            # generated, committed
  specs/2026-03-01.yaml
  specs/2026-07-01.yaml
  severity-map.md                  # human table, source of truth
  oasdiff-levels.txt               # generated from the table in CI
  acks.json                        # starts as []
  oasdiff-err-ignore.txt           # generated from acks.json, starts empty, never hand-edited
  changes/                         # change fragments
tools/build-entries.py             # copied from the skill, pinned
tools/check-entry-trace.py
scripts/generate-specs.sh          # yours
.github/workflows/api-contract.yml
.github/workflows/api-release.yml
.github/CODEOWNERS
.github/pull_request_template.md
```

Committing a spec for each version is what gives you baselines at release tags. The PR job also checks that the committed specs match what the build generates, which doubles as your determinism check.

## Workflow 1: PR gate, `.github/workflows/api-contract.yml`

```yaml
name: api-contract
on:
  pull_request:

env:
  OASDIFF_VERSION: v1.34.1   # pinned from the skill's reference; verify it is current, bump deliberately, review rule diffs
  # Frozen: must not change at all. Evolving: additive only, breaking needs an ack.
  # Next: breaking allowed only with an ack, then listed in the changelog.
  FROZEN_VERSIONS: "2025-11-01"
  GATED_VERSIONS: "2026-03-01 2026-07-01"

jobs:
  contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0        # merge-base revisions need history

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "21"    # match your build

      - uses: actions/setup-go@v5
        with:
          go-version: stable

      - name: Install pinned oasdiff
        run: go install github.com/oasdiff/oasdiff@${OASDIFF_VERSION}

      - name: Generate specs and require them to be committed
        run: |
          ./scripts/generate-specs.sh          # writes api/specs/<version>.yaml
          git diff --exit-code -- api/specs || {
            echo "::error::Committed specs differ from generated ones. Run scripts/generate-specs.sh and commit."
            exit 1
          }

      - name: Regenerate level and ignore files from reviewed sources
        run: |
          awk -F'|' '$2 ~ /^ *[a-z0-9-]+ *$/ && $3 ~ /^ *(err|warn|info|none) *$/ {gsub(/ /,"",$2); gsub(/ /,"",$3); print $2, $3}' api/severity-map.md > api/oasdiff-levels.txt
          python3 tools/build-entries.py --acks api/acks.json --ignore-out api/oasdiff-err-ignore.txt

      - name: Frozen versions must not change
        run: |
          base="$(git merge-base origin/${{ github.base_ref }} HEAD)"
          for v in $FROZEN_VERSIONS; do
            oasdiff diff "$base:api/specs/$v.yaml" "api/specs/$v.yaml" --fail-on-diff
          done

      - name: Breaking-change gate
        run: |
          base="$(git merge-base origin/${{ github.base_ref }} HEAD)"
          status=0
          for v in $GATED_VERSIONS; do
            if ! git cat-file -e "$base:api/specs/$v.yaml" 2>/dev/null; then
              echo "::notice::$v has no spec on the merge base; nothing to compare."
              continue
            fi
            echo "== $v =="
            oasdiff breaking "$base:api/specs/$v.yaml" "api/specs/$v.yaml" \
              --severity-levels api/oasdiff-levels.txt \
              --err-ignore api/oasdiff-err-ignore.txt \
              --fail-on ERR -f githubactions \
              || status=1
            # --filter-extension x-internal    # uncomment once internal operations are marked
          done
          exit $status

      - name: Declared behavior change must come with a fragment
        run: |
          if grep -qE '^\- \[x\] Behavior changed' "$GITHUB_EVENT_PATH" 2>/dev/null; then :; fi
          # The PR body is not on disk. Enforce this in review via the template and CODEOWNERS (below).
          echo "Reviewers: handler changes without a spec change need a fragment in api/changes/."
```

Notes on the YAML:

- The last step is deliberately weak. A checkbox can't be machine-verified from here, so it is enforced by CODEOWNERS plus the review habit. If you want it enforced, add a step that fails when `src/**/controller/**` changes without `api/specs/**` or `api/changes/**`. That is a heuristic, so it needs your judgment.
- `oasdiff diff --fail-on-diff` on frozen versions is strict, and legitimate spec corrections to a frozen version will trip it. You need a decision on how those get through (for example, a reviewer-approved exception).
- Date, header and URI versions make oasdiff skip its version-bump checks, so the per-version baselines above replace them.
- Check the severity-map check ids against your pinned version before trusting them (`oasdiff checks`).

## Workflow 2: release changelog, `.github/workflows/api-release.yml`

```yaml
name: api-release
on:
  push:
    tags: ["v*"]            # whatever marks a release for you
  workflow_dispatch:

env:
  OASDIFF_VERSION: v1.34.1
  # version -> predecessor whose spec is the baseline when the version is brand new
  NEXT_VERSION: "2026-07-01"
  NEXT_PREDECESSOR: "2026-03-01"
  SUPPORTED_VERSIONS: "2025-11-01 2026-03-01 2026-07-01"

jobs:
  draft:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-go@v5
        with:
          go-version: stable
      - name: Install pinned oasdiff
        run: go install github.com/oasdiff/oasdiff@${OASDIFF_VERSION}

      - name: Build skeleton entries per version
        run: |
          set -euo pipefail
          prev_tag="$(git describe --tags --abbrev=0 "${GITHUB_REF_NAME}^" 2>/dev/null || true)"
          mkdir -p out
          for v in $SUPPORTED_VERSIONS; do
            if [ "$v" = "$NEXT_VERSION" ] && ! git cat-file -e "$prev_tag:api/specs/$v.yaml" 2>/dev/null; then
              baseline="$NEXT_PREDECESSOR"                    # new version vs its predecessor
              base_ref="HEAD:api/specs/$baseline.yaml"
            else
              base_ref="$prev_tag:api/specs/$v.yaml"          # same version at the last release
            fi
            oasdiff changelog "$base_ref" "api/specs/$v.yaml" -f json > "out/changelog-$v.json"
            # exit 1 = written with notices (breaks no acknowledgement covers); exit 2 = unusable input
            python3 tools/build-entries.py --changelog "out/changelog-$v.json" \
              --api-version "$v" --date "$(date -u +%F)" \
              --fragments api/changes/ --acks api/acks.json --out "out/entries-$v.json" \
              || [ $? -eq 1 ]
          done

      - uses: actions/upload-artifact@v4
        with:
          name: changelog-drafts
          path: out/

  publish:
    needs: draft
    runs-on: ubuntu-latest
    environment: api-changelog     # required reviewers = your human gate
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/download-artifact@v4
        with:
          name: changelog-drafts
          path: out/
      - name: Trace check on the reviewed entries
        run: |
          # Reviewed entries are committed in api/changelog/<version>.entries.json after a human fills summary/action_required.
          for v in $SUPPORTED_VERSIONS; do
            python3 tools/check-entry-trace.py --diff "out/changelog-$v.json" \
              --entries "api/changelog/$v.entries.json" \
              --fragments api/changes/ --api-version "$v" --acks api/acks.json
          done
      - name: Publish feed and pages
        run: echo "TODO: publish JSON + Atom feed and the per-version page once you choose a destination"
```

How to run it:

1. Tag a release.
2. `draft` produces skeleton entries as an artifact.
3. Someone writes `summary` and `action_required` into `api/changelog/<version>.entries.json`.
4. `publish` runs after environment approval, and only when the trace check passes.

Caveats:

- Run `build-entries.py` once per spec, because fingerprints carry no file name.
- A diff in a version that should be frozen is itself a defect.
- The first release has no baseline, so write its entries by hand and diff from the next release on.

## The GET /invoices change

Add the PR checkbox:

```markdown
### API contract
- [ ] No change to the published API
- [ ] Spec changed (the contract diff will classify it)
- [ ] Behavior changed without a spec change: defaults, validation, error codes or bodies,
      auth, rate limits, pagination, ordering, timing -> add a change fragment
```

Then add the fragment, `api/changes/invoice-list-order.json`:

```json
{
  "id": "declared-invoice-list-order",
  "api_versions": ["2026-07-01"],
  "area": "Invoices",
  "operations": ["GET /invoices"],
  "classification": "breaking",
  "kind": "changed",
  "summary": "TODO: human wording, e.g. invoices are now returned newest first by default.",
  "action_required": "TODO: the real opt-out, if one exists.",
  "sunset": null,
  "links": { "migration": null }
}
```

- **`api_versions` lists only `2026-07-01`**, on the assumption that you gate the new default by version in code. If it also changes order for `2025-11-01` or `2026-03-01` callers, list those too, and that triggers the policy exception path.
- **I left `action_required` as a TODO on purpose.** The skill's example uses `sort=created_asc`, but I don't know that Quillbridge has such a parameter.
  - If there is no way to request the old order, add one before this ships.
  - If there is one, declaring its default in the spec means oasdiff will see the default change.
- **A breaking fragment needs an acknowledgement row** in `acks.json` whose `covers` lists `declared-invoice-list-order`. The schema is in `references/entry-and-feed-format.md`.

## Ignore-file audit (before the gate goes live)

1. Freeze the file from today. No new hand-added lines.
2. Rerun the diff **without** the ignore file against the current release baseline. Delete every line that matches nothing.
3. Each remaining line becomes an acknowledgement row in `acks.json`:
   - Reason `historic` if nobody knows why it was added.
   - A ticket if one exists.
   - Approver `unknown - audited <date>` if nobody signed it.
4. Any line that hid a break partners never saw announced gets a changelog entry in the next release, as a spec correction or a late notice. That is the part your partners are complaining about.
5. From then on `oasdiff-err-ignore.txt` is generated from `acks.json` and never edited by hand. Commit `acks.json` as `[]` and an empty ignore file at setup, because oasdiff exits 121 if a passed ignore file is missing.

## CODEOWNERS (required, or approvals mean nothing)

```
/api/specs/                  @quillbridge/api-review
/api/severity-map.md         @quillbridge/api-review
/api/acks.json               @quillbridge/api-review
/api/changes/                @quillbridge/api-review
```

Turn on required review for code owners in branch protection. Without it, the author approves their own break in the same PR.

## Severity map starter, `api/severity-map.md`

```
| Check id                           | Level | Policy line                                   | Status      |
| ---------------------------------- | ----- | --------------------------------------------- | ----------- |
| response-property-enum-value-added | warn  | undecided: are response enums open?           | provisional |
| api-security-scope-removed         | err   | undecided: announce every auth change        | provisional |
```

- The two rows are illustrations, not recommendations, and they are `provisional` because there's no written policy yet.
- Pin only what your policy contradicts. Oasdiff's defaults apply to everything else.
- If you decide all response enums are open, annotate those fields `x-extensible-enum` and set the enum row to `info`.

## Setup order

1. Answer the open questions above, especially the `2026-07-01` date and how per-version specs are generated.
2. Write `scripts/generate-specs.sh`, commit `api/specs/*`, and make generation deterministic: stable `operationId`s, `$ref` schemas, stable enum order, and a pinned springdoc version. Noisy phantom diffs get the gate switched off.
3. Copy the two scripts into `tools/`, create the empty `acks.json` and ignore file, and add CODEOWNERS.
4. Merge workflow 1 and run the ignore-file audit.
5. Add the PR template, then the invoices fragment and its acknowledgement row.
6. Add workflow 2 and do a dry run on the next tag.

## Known gaps

- **Spec drift from the running service is not covered.** Add a scheduled job that diffs the served spec against the one built from the deployed commit.
- **Gateway-only auth rules and rate limits are invisible to any diff.** Use fragments for them.
- **Breaking-change policy is unsigned.** Every severity is a tool-author default until `api-versioning-policy` produces one.
- **oasdiff has no checks for parameters that use `content` instead of `schema`, and none for callbacks.**
- **Publishing destination and the entry-writing step are stubs.**