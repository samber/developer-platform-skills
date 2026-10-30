# oasdiff in CI for Quillbridge: workflows, setup, and three problems to fix first

**Read this first:** three things in your plan need changing. The YAML is below.

1. **The `GET /invoices` sort flip is the exact "surprise" you want to prevent, and oasdiff can't see it.** Your assumption is right: the diff will be empty. But the changelog is built from that diff, so it won't mention the change either. I've added a manual changelog path and a PR gate for this (section 4).
2. **PR-vs-main output is the wrong source for the public changelog.** It includes changes that get reverted, never ship, or ship later. Use PR-vs-main as a draft comment on each PR. Publish from a release-to-release diff, using the same command so the wording matches (section 3).
3. **Your 60-line ignore file is a permanent suppression list.** Each line is keyed by path and message, not by PR, so it silences that class of change forever. It also hides real breaks from the public changelog if you reuse it there (section 2).

One date to check: you said the next version is `2026-07-01`, but today is 2026-10-30. Confirm that isn't a typo.

## Assumptions

- The generated spec describes the current version only. If you serve every date version from one spec, or keep snapshots per version, say so. The baseline in section 5 changes.
- The build is Gradle and Kotlin, and the app can boot without external services under a dedicated profile.
- All PRs come from branches in the same repo. The workflows use `pull_request`, not `pull_request_target`, because they build untrusted code.

## 1. Setup, in order

1. **Land spec generation in its own PR first.** The workflow builds the base ref with base code. If the PR that adds the Gradle task also adds the workflow, the base build has no task and fails.
2. **Add the springdoc Gradle plugin** (`build.gradle.kts`). Adjust it to your project:
   ```kotlin
   plugins { id("org.springdoc.openapi-gradle-plugin") version "1.9.0" }

   openApi {
       apiDocsUrl.set("http://localhost:8080/v3/api-docs.yaml")
       outputDir.set(layout.buildDirectory)
       outputFileName.set("openapi.yaml")
       customBootRun { args.set(listOf("--spring.profiles.active=openapi")) }
   }
   ```
   Create `application-openapi.yml` with an in-memory DB and no external calls. Add `springdoc.writer-with-order-by-keys: true` to it. Without that, key order can jitter between builds and produce phantom diffs.
3. **Make the spec deterministic and public-only.** The spec must contain no environment-specific `servers` URL and no internal endpoints (`@Hidden`). The changelog is public, so whatever is in the spec is what partners will read.
4. **Create the files:**
   - `.oasdiff/err-ignore.txt` and `.oasdiff/warn-ignore.txt`. Start them empty (see section 2).
   - `changelog/pending/` for manual entries, with a `.gitkeep`.
   - `.github/CODEOWNERS`:
     ```
     /.oasdiff/        @quillbridge/platform
     /changelog/       @quillbridge/platform
     ```
5. **Create the labels** `api-ignore-approved` and `api-new-version`. Restrict who can apply them with repo permissions. They are an honor system, so treat them as a review trigger.
6. **Add a PR template** with this line:
   `- [ ] No partner-visible behavior change outside the OpenAPI spec (sorting, defaults, limits, error codes, rate limits), or I added a file in changelog/pending/`
7. **Set branch protection.** Require the `spec`, `contract`, and `behavior-gate` checks on `main`.

## 2. The ignore file

Don't carry the 60 lines over. The diff is PR versus `main`, so any change those lines once covered is already in `main`. Most lines can only fire again if a PR re-touches the same thing, which is when you don't want them silent.

1. **Move the old file aside.** Run **`git mv .oasdiff/err-ignore.txt docs/legacy-oasdiff-ignore.txt`** and start the new files empty.
2. **Triage the first PRs.** Anything that fires is a real signal or a generator-noise bug. Fix noise at the source (springdoc config), not with an ignore line.
3. **Re-add an entry only with a reason.** Each entry needs a PR link, an owner, and an expiry. Check that your oasdiff version accepts `#` comments in ignore files. If it doesn't, keep the reasons in a sidecar file.
4. **Never use the ignore files for the changelog.** The changelog step below deliberately runs without them.

The workflow also fails any PR that grows the ignore files unless it carries the `api-ignore-approved` label. That stops the "add a line to go green" habit.

## 3. `.github/workflows/api-contract.yml` (every PR)

```yaml
name: api-contract

on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened, labeled, unlabeled, edited]

permissions:
  contents: read

concurrency:
  group: api-contract-${{ github.event.pull_request.number }}
  cancel-in-progress: true

env:
  SPEC_FILE: build/openapi.yaml

jobs:
  spec:
    name: spec (${{ matrix.side }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: true
      matrix:
        side: [base, head]
    steps:
      # base = current tip of main; head = default merge ref (PR merged into main),
      # so the diff is exactly what merging would change.
      - uses: actions/checkout@v4 # pin to a commit SHA
        with:
          ref: ${{ matrix.side == 'base' && github.event.pull_request.base.sha || github.sha }}
      - uses: actions/setup-java@v4 # pin to a commit SHA
        with:
          distribution: temurin
          java-version: "21"
          cache: gradle
      - name: Generate OpenAPI spec
        run: ./gradlew generateOpenApiDocs --no-daemon
      - name: Fail if spec is empty
        run: test -s "$SPEC_FILE" && grep -q '^openapi:' "$SPEC_FILE"
      - uses: actions/upload-artifact@v4 # pin to a commit SHA
        with:
          name: spec-${{ matrix.side }}
          path: ${{ env.SPEC_FILE }}
          if-no-files-found: error

  contract:
    needs: spec
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    env:
      GH_TOKEN: ${{ github.token }}
      PR: ${{ github.event.pull_request.number }}
    steps:
      - uses: actions/checkout@v4 # pin to a commit SHA
        with:
          fetch-depth: 0
      - uses: actions/download-artifact@v4 # pin to a commit SHA
        with:
          pattern: spec-*
          path: specs
      # Check the latest release tag and pin to a SHA before merging.
      - uses: oasdiff/oasdiff-action/setup@v0.0.21

      - name: Ignore files must not grow without approval
        if: ${{ !contains(github.event.pull_request.labels.*.name, 'api-ignore-approved') }}
        run: |
          added=$(git diff --numstat "${{ github.event.pull_request.base.sha }}" HEAD -- .oasdiff/ \
                  | awk '{s+=$1} END {print s+0}')
          if [ "$added" -gt 0 ]; then
            echo "::error::PR adds $added line(s) to .oasdiff/. Needs the api-ignore-approved label and platform review."
            exit 1
          fi

      # Changelog first, WITHOUT ignore files: the public record must show everything.
      - name: Draft changelog (no ignore files)
        run: |
          oasdiff changelog specs/spec-base/openapi.yaml specs/spec-head/openapi.yaml \
            --format markdown > changelog.md
          oasdiff changelog specs/spec-base/openapi.yaml specs/spec-head/openapi.yaml \
            --format json > changelog.json
          { echo "## API changelog draft"; echo; cat changelog.md; } >> "$GITHUB_STEP_SUMMARY"
      - uses: actions/upload-artifact@v4 # pin to a commit SHA
        with:
          name: changelog-draft
          path: |
            changelog.md
            changelog.json

      - name: Comment on PR
        run: |
          { echo "### API changes in this PR (draft changelog)"; echo
            if [ -s changelog.md ]; then cat changelog.md; else echo "_No spec-visible changes._"; fi
            echo; echo "_Behavior changes the spec cannot show (sorting, defaults, limits) need a file in \`changelog/pending/\`._"
          } > comment.md
          gh pr comment "$PR" --edit-last --create-if-none --body-file comment.md

      # Gate last. api-new-version makes it report-only for the PR that cuts a new date version.
      - name: Fail on breaking changes
        continue-on-error: ${{ contains(github.event.pull_request.labels.*.name, 'api-new-version') }}
        run: |
          oasdiff breaking specs/spec-base/openapi.yaml specs/spec-head/openapi.yaml \
            --fail-on ERR \
            --err-ignore .oasdiff/err-ignore.txt \
            --warn-ignore .oasdiff/warn-ignore.txt \
            --format githubactions

  behavior-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4 # pin to a commit SHA
        with:
          fetch-depth: 0
      - name: Require an explicit answer on non-spec behavior changes
        env:
          BODY: ${{ github.event.pull_request.body }}
          BASE: ${{ github.event.pull_request.base.sha }}
        run: |
          if printf '%s' "$BODY" | grep -qiE '^- \[x\] No partner-visible behavior change'; then exit 0; fi
          if git diff --name-only --diff-filter=A "$BASE" HEAD -- 'changelog/pending/*.md' | grep -q .; then exit 0; fi
          echo "::error::Tick the 'no partner-visible behavior change' box or add changelog/pending/<slug>.md"
          exit 1
```

Two things to verify against your oasdiff version: the `--format markdown` option for `changelog`, and the `githubactions` format for `breaking`. Check with `oasdiff changelog --help` and `oasdiff breaking --help`.

To tighten the gate later, change `--fail-on ERR` to `--fail-on WARN`. If your deprecation policy is longer than oasdiff's default, set the deprecation-days flags too, so "removed without deprecation" matches your real policy.

## 4. The `GET /invoices` sort flip

oasdiff only compares the spec. Make the change visible to it and to partners in five ways:

1. **Gate it by `Quillbridge-Version`.** Old versions keep oldest-first. Only requests on the new version get newest-first. An unversioned flip is a breaking change, whatever the spec says.
2. **Put the sort in the spec.** Add an explicit `sort` query parameter with an enum and a documented default. Then oasdiff sees a default change on the parameter (check the rule name with `oasdiff checks`). A description-only change shows up as an info-level diff.
3. **Write a manual entry** in `changelog/pending/invoices-default-sort.md`:
   ```markdown
   ---
   affects: GET /invoices
   since: <new version date>
   breaking: true
   ---
   Default order of `GET /invoices` is now newest first (`created_at` descending).
   To keep the previous order, send `sort=created_at:asc`.
   Cursors issued before the change stay valid only on the old version.
   ```
4. **Add a contract test per version** that asserts the order for each `Quillbridge-Version` value. It runs in Gradle and fails if the order drifts.
5. **Email the 400 partners directly.** A changelog entry alone won't stop the surprises.

## 5. `.github/workflows/api-changelog.yml` (publish)

This runs when you publish a release. It diffs the previous release's spec against the new one, merges the manual entries, and opens a PR for review. It publishes nothing automatically.

```yaml
name: api-changelog

on:
  release:
    types: [published]

permissions:
  contents: read

jobs:
  refs:
    runs-on: ubuntu-latest
    outputs:
      new: ${{ steps.r.outputs.new }}
      prev: ${{ steps.r.outputs.prev }}
    steps:
      - uses: actions/checkout@v4 # pin to a commit SHA
        with:
          fetch-depth: 0
      - id: r
        env:
          NEW: ${{ github.event.release.tag_name }}
        run: |
          echo "new=$NEW" >> "$GITHUB_OUTPUT"
          echo "prev=$(git describe --tags --abbrev=0 "$NEW^")" >> "$GITHUB_OUTPUT"

  spec:
    needs: refs
    runs-on: ubuntu-latest
    strategy:
      matrix:
        side: [prev, new]
    steps:
      - uses: actions/checkout@v4 # pin to a commit SHA
        with:
          ref: ${{ matrix.side == 'prev' && needs.refs.outputs.prev || needs.refs.outputs.new }}
      - uses: actions/setup-java@v4 # pin to a commit SHA
        with: { distribution: temurin, java-version: "21", cache: gradle }
      - run: ./gradlew generateOpenApiDocs --no-daemon
      - uses: actions/upload-artifact@v4 # pin to a commit SHA
        with:
          name: spec-${{ matrix.side }}
          path: build/openapi.yaml
          if-no-files-found: error

  publish:
    needs: [refs, spec]
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    env:
      GH_TOKEN: ${{ github.token }}
      NEW: ${{ needs.refs.outputs.new }}
      PREV: ${{ needs.refs.outputs.prev }}
    steps:
      - uses: actions/checkout@v4 # pin to a commit SHA
        with:
          ref: ${{ needs.refs.outputs.new }}
      - uses: actions/download-artifact@v4 # pin to a commit SHA
        with: { pattern: spec-*, path: specs }
      - uses: oasdiff/oasdiff-action/setup@v0.0.21
      - name: Build changelog file
        run: |
          out="changelog/releases/${NEW}.md"
          mkdir -p changelog/releases
          {
            echo "# API changes in ${NEW} (since ${PREV})"; echo
            if ls changelog/pending/*.md >/dev/null 2>&1; then
              echo "## Behavior changes"; echo
              for f in changelog/pending/*.md; do sed '1,/^---$/{/^---$/!d}; /^---$/d' "$f"; echo; done
            fi
            echo "## Spec changes"; echo
            oasdiff changelog specs/spec-prev/openapi.yaml specs/spec-new/openapi.yaml --format markdown
          } > "$out"
          git mv changelog/pending/*.md changelog/releases/ 2>/dev/null || true
      - name: Open review PR
        run: |
          git config user.name  "api-changelog-bot"
          git config user.email "api-changelog-bot@users.noreply.github.com"
          branch="changelog-${NEW}"
          git switch -c "$branch"
          git add changelog/
          git commit -m "docs(changelog): api changes for ${NEW}"
          git push origin "$branch"
          gh pr create --base main --head "$branch" \
            --title "docs(changelog): api changes for ${NEW}" \
            --body "Generated from the ${PREV} to ${NEW} spec diff plus changelog/pending entries. Review wording, then merge to publish."
```

The `sed` line that strips front matter is rough. Replace it with your docs pipeline's front-matter handling once you know how the changelog is rendered.

Your docs site then publishes from `changelog/releases/` on merge. Because a human reviews the PR, oasdiff's raw wording ("response-property-removed") becomes partner-readable prose before it goes public.

## 6. What this setup does not catch

- Behavior changes not in the spec: sorting, rate limits, validation strictness, error-body details. These need the PR-template box, the `changelog/pending` file, and contract tests.
- Which partners are affected. oasdiff has no usage data. Cross-check breaking entries against your API logs before sending partner emails.
- A first-ever run of the base build, if the Gradle task isn't on `main` yet (setup step 1).

## Questions that would change this design

1. Do you ship one spec for the latest version, or one per date version? If per version, the baseline should be the immutable released snapshot of each version, not `main`, and every released version must show zero breaking diff.
2. Does the app boot with no external dependencies under a test profile? If not, generate the spec from a MockMvc test instead of the plugin.
3. Where does the public changelog live (docs repo, Mintlify, Docusaurus)? The `publish` job should open its PR there.