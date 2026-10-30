# Stock `oasdiff breaking --fail-on ERR` does not enforce your guidelines

**Verdict: no, stock settings are not fine.** I'm confident about the gaps below. The exact rule IDs and default levels come from my memory of oasdiff, and I did not run the tool against your specs. Treat the first step in "Rollout" as mandatory before you merge the gate.

## Where stock settings diverge from section 2

| Guideline | Stock behavior | Result |
|---|---|---|
| Response enums are open, so new values are fine | The default level for `response-property-enum-value-added` is below ERR as far as I recall. Confirm with `oasdiff checks`. | Probably OK, but pin it so a future oasdiff upgrade can't silently turn it into a CI failure. |
| Changing the scopes an endpoint requires is breaking | Scope and security changes map to several rules (`api-security-*`, `api-security-component-oauth-scope-*`). Several of these are WARN or INFO by default. | Likely a gap. Scope changes could pass. |
| Adding a regex `pattern` to an existing request parameter is breaking | I recall `request-parameter-pattern-added` and `request-property-pattern-added` defaulting to WARN. | Gap. `--fail-on ERR` passes it. |
| A breaking change must bump the major version | oasdiff does not compare `info.version` and has no semver check. | Gap. It is not enforced at all. |

This is not bikeshedding. The guidelines are your contract, and stock defaults encode oasdiff's opinion of breaking, not yours. The fix is a small severity-override file and a short script. You can still tell your lead that you run stock oasdiff, with 4 explicit overrides.

Also check these before rollout:
- **OpenAPI 3.1 support.** oasdiff's 3.1 coverage has been partial. Type arrays like `["string","null"]`, `const`, `webhooks` and `$ref` siblings may be ignored or mis-diffed. The fixtures below cover your 3.1 constructs, and any rule that never fires on them is a blind spot.
- **Deprecation handling.** oasdiff treats removal of a deprecated endpoint as non-breaking once its sunset window has passed. That window is configurable and defaults to 180 days for stable APIs. If your guidelines are stricter, set `--deprecation-days-stable`.
- **WARN-level findings stay visible.** The gate fails on ERR only, so the workflow below prints WARNs as annotations to keep them in review.

## Files

Assumed layout: `apis/<name>/openapi.yaml` for the three APIs. Replace `api-a`, `api-b` and `api-c` with the real names, and set `OASDIFF_VERSION` to a pinned release.

### `.oasdiff/severity-levels.txt`

Format is `<check-id> <level>`. Copy the exact IDs from `oasdiff checks`. The names below are from memory.

```text
# Guidelines §2: response enums are open and may gain values at any time.
response-property-enum-value-added info

# Guidelines §2: adding a regex pattern to an existing request input is breaking.
request-parameter-pattern-added err
request-property-pattern-added err

# Guidelines §2: any change to the scopes an endpoint requires is breaking.
# Replace with every api-security-* / *-oauth-scope-* ID that `oasdiff checks` lists.
api-security-updated err
api-security-component-oauth-scope-added err
api-security-component-oauth-scope-removed err
```

### `scripts/api-breaking-gate.sh`

```bash
#!/usr/bin/env bash
# Usage: api-breaking-gate.sh <base-spec> <head-spec>
# Fails when the diff has ERR-level changes and info.version's major did not increase.
set -euo pipefail

BASE="$1"
HEAD="$2"
SEVERITY_FILE=".oasdiff/severity-levels.txt"

# Exit codes this script relies on: 0 = no ERR findings, 1 = ERR findings.
# Anything else is a tool failure and must never read as "clean".
EXIT_CLEAN=0
EXIT_BREAKING=1

major() { yq -e '.info.version' "$1" | cut -d. -f1; }

# Show WARN/INFO findings in the log without gating on them.
oasdiff breaking "$BASE" "$HEAD" --severity-levels "$SEVERITY_FILE" --format githubactions || true

set +e
oasdiff breaking "$BASE" "$HEAD" --severity-levels "$SEVERITY_FILE" --fail-on ERR >/dev/null
rc=$?
set -e

if [ "$rc" -eq "$EXIT_CLEAN" ]; then
  echo "No breaking changes."
  exit 0
fi
if [ "$rc" -ne "$EXIT_BREAKING" ]; then
  echo "::error::oasdiff failed with exit code $rc (tool error, not a verdict)"
  exit "$rc"
fi

base_major=$(major "$BASE")
head_major=$(major "$HEAD")
if [ "$head_major" -gt "$base_major" ]; then
  echo "Breaking changes present and major bumped ($base_major -> $head_major)."
  exit 0
fi
echo "::error::Breaking changes require a major bump of info.version (still major $head_major)."
exit 1
```

### `.github/workflows/api-breaking-changes.yml`

```yaml
name: api-breaking-changes
on:
  pull_request:
    paths: ["apis/**"]

permissions:
  contents: read

env:
  # Pin and bump deliberately: new oasdiff releases can change rule levels.
  OASDIFF_VERSION: "X.Y.Z"

jobs:
  gate:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        api: [api-a, api-b, api-c]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install oasdiff
        run: |
          curl -sSfL "https://github.com/oasdiff/oasdiff/releases/download/v${OASDIFF_VERSION}/oasdiff_${OASDIFF_VERSION}_linux_amd64.tar.gz" \
            | tar -xz -C /usr/local/bin oasdiff
          oasdiff --version

      - name: Fixture self-test (gate must fail when it should)
        run: bash scripts/test-api-gate.sh

      - name: Diff against the PR's merge base
        run: |
          set -euo pipefail
          spec="apis/${{ matrix.api }}/openapi.yaml"
          base_ref=$(git merge-base "origin/${{ github.base_ref }}" HEAD)
          mkdir -p /tmp/api-gate
          if ! git cat-file -e "${base_ref}:${spec}" 2>/dev/null; then
            echo "New API, nothing to compare."; exit 0
          fi
          git show "${base_ref}:${spec}" > /tmp/api-gate/base.yaml
          bash scripts/api-breaking-gate.sh /tmp/api-gate/base.yaml "$spec"
```

Release branches (for example a 4.x backport) should diff against the latest released tag, not `main`. Add a second trigger for those if you maintain them.

### `scripts/test-api-gate.sh` (positive and negative controls)

Keep tiny specs under `testdata/api-gate/<case>/{base,head}.yaml`. Each case asserts the exit code of `api-breaking-gate.sh`:

| Case | Change | Expected |
|---|---|---|
| `enum-added-response` | New value in a response enum | pass |
| `pattern-added-param` | `pattern` added to an existing query parameter | fail |
| `scope-changed` | Different scope on one operation's `security` | fail |
| `scope-changed-major-bumped` | Same change, 4.2.0 to 5.0.0 | pass |
| `endpoint-removed` | Control: a plain breaking change | fail |
| `clean` | Description edit | pass |

Write the cases in 3.1 syntax, including one nullable `type: [string, "null"]` field. A fixture that unexpectedly passes is a rule that does not fire, and it means a gap remains.

## Rollout

1. Run `oasdiff checks` and replace the severity-file IDs with the real ones.
2. Run the fixtures. Any case that doesn't behave as expected shows a wrong ID or a 3.1 blind spot.
3. Run the gate against the last two real releases of each API to see what it would have flagged historically.
4. Add the workflow as a required check only after steps 1–3 are clean.

Two questions would sharpen this. What do the specs' `security` blocks look like, with operation-level or global scopes? And does your deprecation policy match oasdiff's sunset-date logic?