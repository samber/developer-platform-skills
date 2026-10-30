**Stock settings are not fine.** Four rows of your own guidelines (§2) contradict or are missed by `oasdiff breaking --fail-on ERR`. Pinning them is about 1 to 2 hours of work, mostly review, and it is not bikeshedding. The defaults are oasdiff's opinion, not your policy. The gate must enforce what your guidelines say, or the team will switch it off.

I did not run oasdiff or the skill's Python scripts, because the sandbox blocked my shell check. The CI below follows the skill's reference workflow. Confirm the two check ids marked "verify" before merging.

## Stock behavior against §2

| §2 line | Stock oasdiff | Result | Fix |
| --- | --- | --- | --- |
| Response enums are open | Adding a response enum value (`response-property-enum-value-added`) is flagged | False alarms on changes you allow. Noise is how gates get set to `fail-on none`. | Pin to `info`. Add `x-extensible-enum` on those fields. |
| Auth scope changes are breaking | Added scopes: `ERR`. Removed scopes (`api-security-scope-removed`): `INFO`. An added alternative (OR) requirement: `INFO`. | Half of "changing scopes" passes silently. | Pin `api-security-scope-removed` to `err`. Find the id for alternative requirements with `oasdiff checks` and pin it too (verify). |
| Adding a regex pattern to an existing request parameter is breaking | Probably `WARN`: `request-parameter-pattern-added` (verify id and level on the pinned version) | `--fail-on ERR` ignores `WARN`, so it passes. | Pin to `err`. |
| A breaking change must bump the major version | `api-major-version-not-bumped` defaults to `INFO` and never fails | Nothing enforces the rule. | Pin to `err`. Your semver `info.version` (4.2.0) activates the check. |

Pinning disables oasdiff's own downgrades for that check, so pin only these rows.

## Caveats

1. **The major-bump check fights the PR gate.** A PR gate diffs against the merge base. Once PR #1 bumps `info.version` to 5.0.0 and merges, PR #2 (also breaking) compares 5.0.0 with 5.0.0 and fails. My reading of the skill's baseline rules is that bump checks belong in the release job, against the last release tag. The workflow below does this: the PR job uses a PR-only copy of the levels with the bump check at `info`, and the release job uses the full map.
2. **`oasdiff` sees declared structure only.** Behavior changes, gateway-only auth rules, and validation not mirrored in the spec pass green. Add the PR-template block and change-fragment channel next. That is the rung after this gate.
3. **Spec must match the service.** If nobody validates the three specs against the running services, a green check describes a document. Treat that as the first gap, and add a drift alarm later.
4. **Fingerprints carry no file name.** Run once per spec and keep acknowledgements per API, as the layout below does.

## Files to commit

Layout:

```
api/severity-map.md            # shared policy table, one row per pinned check
api/<api>/openapi.yaml         # x3
api/<api>/acks.json            # commit as []
api/<api>/oasdiff-err-ignore.txt   # commit empty
tools/build-entries.py         # copy from the skill's scripts/
.github/CODEOWNERS
.github/workflows/api-contract.yml
```

`api/severity-map.md`:

```
| Check id                           | Level | Policy line                                          | Status |
| ---------------------------------- | ----- | ---------------------------------------------------- | ------ |
| response-property-enum-value-added | info  | Guidelines 2 - response enums are open               | signed |
| api-security-scope-removed         | err   | Guidelines 2 - any change to required scopes         | signed |
| request-parameter-pattern-added    | err   | Guidelines 2 - new pattern on a request parameter    | signed |
| api-major-version-not-bumped       | err   | Guidelines 2 - breaking change needs a major bump   | signed |
```

Mark a row `provisional` until your lead signs it. Add the alternative-requirement id as a fifth row once verified.

`.github/CODEOWNERS` (replace the team name). Without it, an author can approve their own break in the same PR:

```
/api/ @ternwick/api-approvers
```

`.github/workflows/api-contract.yml`:

```yaml
name: api-contract
on:
  pull_request:
    paths: ["api/**"]
env:
  OASDIFF_VERSION: v1.34.1   # pinned; bump deliberately and review rule changes
jobs:
  breaking:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        api: [api-one, api-two, api-three]   # replace with the three API directory names
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # merge-base baselines need history
      - uses: actions/setup-go@v5
        with:
          go-version: stable
      - name: Install pinned oasdiff
        run: go install github.com/oasdiff/oasdiff@${OASDIFF_VERSION}
      - name: Build level and ignore files from reviewed sources
        run: |
          awk -F'|' '$2 ~ /^ *[a-z0-9-]+ *$/ && $3 ~ /^ *(err|warn|info|none) *$/ {gsub(/ /,"",$2); gsub(/ /,"",$3); print $2, $3}' api/severity-map.md > levels.txt
          # Bump check runs in the release job: a merge-base diff would fail every breaking PR after the first.
          sed 's/^api-major-version-not-bumped .*/api-major-version-not-bumped info/' levels.txt > pr-levels.txt
          python3 tools/build-entries.py --acks api/${{ matrix.api }}/acks.json --ignore-out api/${{ matrix.api }}/oasdiff-err-ignore.txt
      - name: Gate
        run: |
          base="$(git merge-base origin/${{ github.base_ref }} HEAD)"
          oasdiff breaking "$base:api/${{ matrix.api }}/openapi.yaml" api/${{ matrix.api }}/openapi.yaml \
            --severity-levels pr-levels.txt \
            --err-ignore api/${{ matrix.api }}/oasdiff-err-ignore.txt \
            --fail-on ERR -f githubactions

  version-bump:   # same pinned tool, full severity map, against the last release tag
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        api: [api-one, api-two, api-three]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-go@v5
        with:
          go-version: stable
      - run: go install github.com/oasdiff/oasdiff@${OASDIFF_VERSION}
      - name: Compare with last release
        run: |
          awk -F'|' '$2 ~ /^ *[a-z0-9-]+ *$/ && $3 ~ /^ *(err|warn|info|none) *$/ {gsub(/ /,"",$2); gsub(/ /,"",$3); print $2, $3}' api/severity-map.md > levels.txt
          last="$(git describe --tags --abbrev=0 origin/${{ github.base_ref }})"
          oasdiff breaking "$last:api/${{ matrix.api }}/openapi.yaml" api/${{ matrix.api }}/openapi.yaml \
            --severity-levels levels.txt --fail-on ERR -f githubactions
```

If you tag releases per API, replace the `git describe` line with that API's tag pattern. If the three APIs share one tag, it works as written. The `version-bump` job also fails on breaking changes that an acknowledgement covers, because it doesn't pass the ignore file. If you want accepted breaks to pass there, add `--err-ignore`.

Spec edits for the enum row: add `x-extensible-enum` to each response enum field.

## Order of work

1. Pin the four rows in `api/severity-map.md` and get your lead to sign them. Pitch to the lead: "defaults flag what we allow and miss what we forbid."
2. Run `oasdiff checks` on `v1.34.1` to verify the pattern and alternative-requirement ids.
3. Commit the empty `acks.json` and ignore files, `CODEOWNERS`, and the workflow.
4. Dry-run the gate on a branch with one injected change per row: a response enum value, a removed scope, a new pattern, and a breaking change without a major bump. Each of the four must fail or pass as the map says. A gate that never failed on a known bad change proves nothing.
5. Add the PR-template block and change fragments for behavior changes. Add the approval record once the first break is accepted.

## Questions for you

1. What are the three API directory names, and do they share one tag or one version number?
2. Do internal, beta, or partner-only operations live in the same specs? That decides the `--stability-level` and `--filter-extension` filters.
3. Does §2's pattern rule cover request body properties too? If so, pin `request-property-pattern-added` as well.
4. Are the specs hand-written or generated, and are they checked against the running services?
5. Is there a hard date for the first gate run? A fixed date means shipping this PR gate alone first.

Next action: ask your lead to sign the four-row table in `api/severity-map.md`. The review is about 15 minutes.