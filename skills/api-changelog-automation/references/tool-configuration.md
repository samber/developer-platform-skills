# Tool configuration per paradigm

Contents:

- [Severity map and level file](#severity-map-and-level-file)
- [OpenAPI: oasdiff](#openapi-oasdiff)
- [OpenAPI: OpenAPITools openapi-diff](#openapi-openapitools-openapi-diff)
- [GraphQL: graphql-inspector and registry checks](#graphql-graphql-inspector-and-registry-checks)
- [Protobuf: buf breaking](#protobuf-buf-breaking)
- [AsyncAPI](#asyncapi)
- [Fingerprints for tools that emit none](#fingerprints-for-tools-that-emit-none)
- [CI workflow](#ci-workflow)
- [Drift alarm](#drift-alarm)

Names, flags and defaults are the tools' own; verify them against the pinned version. An archived tool is never a new choice.

## Severity map and level file

Keep the human table and the machine file apart. The table cites the policy line each row enforces, so a reviewer can tell an intended deviation from a forgotten default.

`severity-map.md`:

```
| Check id                          | Level | Policy line                                         | Status      |
| --------------------------------- | ----- | --------------------------------------------------- | ----------- |
| api-security-scope-removed        | err   | 1.9 - widening auth changes are announced too       | signed      |
| api-major-version-not-bumped      | err   | 3.1 - semver info.version; breaking needs a major   | signed      |
| response-property-enum-value-added| info  | 2.3 - every response enum is open                   | provisional |
```

`api-security-scope-removed` widens access, so no conforming client breaks; pinning it to `err` is a policy choice to announce every auth change, not a correction of the tool.

`oasdiff-levels.txt` holds only `<check-id> <level>` lines (oasdiff rejects comments and extra columns, exit code 106). The CI workflow below extracts it from the table on every run, so the two files cannot drift. For tools without a level file, keep the same table beside their rule configuration.

## OpenAPI: oasdiff

- Commands: `breaking` (ERR + WARN), `changelog` (all levels at or above `--level`, docs-only edits excluded), `diff` (everything). Multi-spec repositories: `breaking-files` checks each changed spec against its version at a git ref.
- Levels: `ERR` definite, `WARN` cannot be decided from the definition, `INFO` non-breaking. Gate with `--fail-on ERR`.
- Direction-aware: a response becoming nullable is `err`, a request becoming nullable is `info`.
- Auth: added scopes, added global scopes, removed anonymous access and removed security are ERR; removed scopes and an added alternative security requirement (alternatives are OR'd, so access widens) are INFO.
- `allOf` changes without `--flatten-allof` are compared branch by branch and downgraded to WARN; flatten to get the exact verdict.
- Baselines by git revision: `oasdiff breaking origin/main:openapi.yaml openapi.yaml`, `oasdiff changelog v2.3.0:api/openapi.yaml api/openapi.yaml`. Needs full git history in CI.
- Output: `-f json|githubactions|singleline|markdown|...`; `--attributes x-audience` copies an extension value onto each JSON entry.
- Ignore files: `--err-ignore` / `--warn-ignore`, one line per change as `METHOD /path <change text>` or `components <change text>`; extra text (a date, an acknowledgement id) is allowed. They match on text, not fingerprints, so a stale line can match a future change with the same wording.
- Fingerprint: 12 hex chars from check id, operation, path and the message arguments; stable across commits in a PR; changes when the base moves (renames, `oneOf` positions, shared-schema anchor).
- Lifecycle:
  - `deprecated: true` then removal is accepted; with `x-sunset: "YYYY-MM-DD"`, removal before that date is `err`, and moving the date earlier is `err`.
  - `--deprecation-days-stable=N` / `--deprecation-days-beta=N` make `x-sunset` mandatory with a minimum grace period.
  - Full deprecation flow applies to operations and parameters. Check the pinned version's handling of deprecated properties before relying on it.
- Stability: `x-stability-level` = `draft` → `alpha` → `beta` → `stable`; `--stability-level` sets the threshold (default `beta` excludes draft and alpha); no level counts as stable; a decrease is reported.
- Audience: `--filter-extension <regex>` excludes paths and operations carrying a matching extension name; `--match-path` / `--unmatch-path` filter by path regex. An element marked in only one of the two specs shows up as added or removed.
- Version bumps: `api-version-not-bumped`, `api-version-decreased`, `api-major-version-not-bumped`; skipped for non-semver versions.
- Shared schemas: one finding per check per operation; within one payload, one finding names the shared schema and counts the properties it reaches.
- Stated gaps: no checks for parameters using `content` instead of `schema`, none for callbacks.

## OpenAPI: OpenAPITools openapi-diff

- Outcomes: no change, compatible, incompatible. Flags `--fail-on-incompatible`, `--fail-on-changed`.
- Per-rule switches as config properties, e.g. `incompatible.response.enum.increased=false` turns off its default of treating a growing response enum as incompatible.
- Path matching ignores parameter names and fails on ambiguous paths.

## GraphQL: graphql-inspector and registry checks

- `graphql-inspector diff OLD NEW`: breaking, dangerous, non-breaking; exits non-zero on breaking.
- Rules:
  - `dangerousBreaking` - every dangerous change fails (choose when the policy treats enum additions or default changes as breaking).
  - `suppressRemovalOfDeprecatedField` - removing a `@deprecated` field becomes dangerous. Pair it with a usage rule, never alone.
  - `safeUnreachable` - changes to types unreachable from root types pass.
  - `considerUsage --onUsage <module>` - your module answers, per type/field/argument, whether it was used in your window.
- Registry checks with recorded operations (e.g. Apollo GraphOS, GraphQL Hive) mark operations broken or potentially affected. Apollo's default window is the last week; raise it to the longest client cycle, since clients with no traffic in the window are invisible.

## Protobuf: buf breaking

- `buf breaking --against '.git#branch=main'` (PR gate) or `--against` a release tag or registry module (changelog baseline).
- Categories, strictest first: `FILE` (default) ⊃ `PACKAGE` ⊃ `WIRE_JSON` ⊃ `WIRE`. Use at least `WIRE_JSON` whenever any client speaks JSON (Connect, grpc-gateway, gRPC JSON): `WIRE` alone misses field renames that break JSON clients.
- `except`, `ignore`, `ignore_unstable_packages` in `buf.yaml`.
- Blind to custom options such as `google.api.http`: an HTTP transcoding change passes every breaking check. Diff the generated OpenAPI of the transcoded surface as well.

## AsyncAPI

- `@asyncapi/diff` (and the `asyncapi diff` CLI): breaking, non-breaking, unclassified, with per-JSON-pointer overrides for `add`/`remove`/`edit`.
- Decide unclassified once, in the severity map: `warn` (shown, not failing) is the usual choice; `err` when consumers are unreachable.

## Fingerprints for tools that emit none

graphql-inspector, buf and `@asyncapi/diff` output carries no stable change id. Map each finding to the scripts' fields before building entries:

- `id`: the tool's change type or rule (`FIELD_REMOVED`, `FIELD_SAME_JSON_NAME`, a `@asyncapi/diff` action plus pointer kind).
- `level`: `3` breaking, `2` dangerous / unclassified, `1` non-breaking.
- `path`: the coordinate - GraphQL schema coordinate (`Shipment.legacyTrackingCode`), proto `file:element`, AsyncAPI JSON pointer.
- `operation`: the root operation or RPC when one applies, else empty.
- `text`: the tool's message.
- `fingerprint`: the first 12 hex characters of `sha256("<id>:<operation>:<path>:<args>")`, where `args` are the structured values of the change (graphql-inspector `meta` values, buf element names, `@asyncapi/diff` before/after values). Never hash the message text: a reworded message in a tool upgrade would re-key every finding and orphan every acknowledgement.

Keep the mapping in the repo so fingerprints stay stable across runs.

## CI workflow

GitHub Actions shape for the PR gate (other CI systems: same steps):

```yaml
name: api-contract
on:
  pull_request:
    paths: ["api/**"]
jobs:
  breaking:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0            # git-revision baselines need history
      - name: Install pinned oasdiff
        run: go install github.com/oasdiff/oasdiff@${OASDIFF_VERSION}
        env:
          OASDIFF_VERSION: v1.34.1  # pinned; bump deliberately and review rule changes
      - name: Regenerate level and ignore files from the reviewed sources
        run: |
          awk -F'|' '$2 ~ /^ *[a-z0-9-]+ *$/ && $3 ~ /^ *(err|warn|info|none) *$/ {gsub(/ /,"",$2); gsub(/ /,"",$3); print $2, $3}' api/severity-map.md > api/oasdiff-levels.txt
          python3 tools/build-entries.py --acks api/acks.json --ignore-out api/oasdiff-err-ignore.txt
      - name: Gate
        run: |
          base="$(git merge-base origin/${{ github.base_ref }} HEAD)"
          oasdiff breaking "$base:api/openapi.yaml" api/openapi.yaml \
            --severity-levels api/oasdiff-levels.txt \
            --err-ignore api/oasdiff-err-ignore.txt \
            --fail-on ERR -f githubactions
```

Commit `api/acks.json` as `[]` and an empty `api/oasdiff-err-ignore.txt` at setup: oasdiff exits 121 when an ignore file passed to it does not exist. Copy the skill's scripts into the repository (here `tools/`) so CI runs a reviewed, pinned copy.

The release job runs `oasdiff changelog <last-release-tag>:api/openapi.yaml api/openapi.yaml -f json`, then `build-entries.py` and `check-entry-trace.py`, and publishes only on a passing trace check.

## Drift alarm

- Served spec: on a schedule, fetch the spec the production service exposes and diff it with `oasdiff diff --fail-on-diff` against the spec built from the commit that is deployed (the build artifact). With continuous deployment that is the default branch, not the last release tag; comparing against the tag fires on every merge.
- No served spec: validate sampled production requests and responses against the spec with a validation proxy or middleware, and alert on violations.
- A drift finding is a spec correction candidate: it goes through step 6, never straight into the ignore file.
