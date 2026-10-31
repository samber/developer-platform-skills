# Velmora API changelog: publishing-side design

Both problems have one root cause. Today the changelog is written from `openapi.yaml`, which holds public, beta and internal operations together, and nothing decides who may see a given change. This design adds that decision first, then builds the feed on top of it.

## Open interview answers and the assumptions I used

I had no answers to the skill's interview, so these are assumptions to confirm or correct.

| # | Question | Assumption | If wrong |
|---|---|---|---|
| 1 | Surfaces | One OpenAPI 3.x file. Webhooks are out of scope for now. | A webhook payload diff needs the AsyncAPI path in `tool-configuration.md`. |
| 2 | Spec source | Unknown, so I treat it as generated and not yet validated against the service. | If it is hand-written, drop the determinism work. If it is validated, drop gap 1. |
| 3 | Written breaking-change policy | None. | Every severity row below is **provisional**, and the policy goes to `api-versioning-policy`. |
| 4 | Release unit | Date versions (`2026-10-01`). Partners pin a version. | If one codebase serves all versions through transformers, produce one spec per version. See step 3. |
| 5 | Audiences | Internal, beta and public share one file. Marking is inconsistent: `x-internal` exists, and the beta marker is unknown. | |
| 6 | Usage data | Not assumed. | I deleted usage-aware classification from the plan. |
| 7 | Readers | Partner monitoring bots and their coding agents, plus humans. | |
| 8 | Deadline and effort | Unknown. | The effort in the build order is the skill's per-rung estimate. |

## Rungs, in build order

Your machine consumers move the feed above the approval record. You have no usage data, so usage-aware classification is out. The feed publishes a breaking entry only if the trace check finds its approval record, so the approval record becomes mandatory at the first accepted break.

| Order | Rung | Effort |
|---|---|---|
| 0 | Audience projection and leak gate (new, fixes your incident) | about half a day |
| 1 | PR gate | 1-2 hours, mostly reviewing the severity map |
| 2 | Release diff and declared-change channel | half a day, plus a habit |
| 3 | Feed (JSON and Atom) | about 1 day |
| 4 | Approval record | a few hours at setup, then minutes per break |

Total is about 3 engineer-days plus reviewer time. If you have a hard date, ship rungs 0 and 1 alone first.

I ranked these by efficiency, with the feed promoted because your consumers are machines. The version-derived changelog (breaks recorded in code at the change) is the rung that would win on value. It needs per-account versioning with response transformers. If Velmora already has that, promote it later, since entries are then written where the change is made and cannot be omitted.

## 0. Fix the leak: audience is a required field, and you publish from projections

**Why it leaked.** Filtering was optional and denylist-based, so any operation missing a marker was public. That fails open.

1. **Make audience mandatory.** Every operation in `openapi.yaml` carries `x-audience: public | partner | internal`.
   - Add a lint job that fails the PR when any operation lacks it.
   - Leave `x-internal` in place only until the migration is done.
   - Put beta operations at `partner` plus `x-stability-level: beta`. `/v1/payouts/instant` is the first.
   - Put the admin endpoints at `internal`.
2. **Build projections.** A small script in `tools/` writes `specs/<version>.public.yaml` (audience `public` only) and `specs/<version>.partner.yaml` (`public` plus `partner`).
   - Internal operations never enter either file.
   - Schemas reachable only from dropped operations are pruned.
3. **Diff and publish only from projections.** The raw file is used for nothing public.
   - The PR gate, the release diff and the feed all read projections.
   - This is the primary control. The oasdiff flags are a second layer.
4. **Add the second layer.** Pass `--filter-extension x-internal` and an explicit stability threshold to oasdiff.
   - The default `--stability-level` is `beta`, which excludes draft and alpha only. Beta operations stay in the diff.
   - Confirm on the pinned version which threshold excludes beta before relying on it.
5. **Add an output leak check.** After the entries are built, assert that every operation named in an entry exists in that audience's projection. Prove the check works:
   - A positive control: a known public operation must pass.
   - A negative control: a fixture entry naming `/v1/payouts/instant` or an admin path must **fail** the public run.
   - A check that cannot fail does not count. If the script errors out, the publish stops. It must not default to "no leaks".
6. **Know the one trap.** An operation that gains an audience marker disappears from the projected diff as a removal. If any caller could already see it, the removal stays breaking and goes through the normal approval.
   - The beta payout endpoint may have callers, because it appeared in public notes.
   - Check who calls it, using `integration-health-monitoring`, before you move it to `partner`.

**Past leak.** Audit the published HTML notes for the beta and `x-internal` mentions. Then decide what to do with them, with Legal and Support: correct, retract, or leave as is. That is an outward-facing action, so I haven't taken it.

## 1. Preconditions, listed as gaps

1. **Spec not validated against the service.** Add contract tests or traffic validation. Until then a green diff describes a document, not the API. This is the first gap.
2. **Generated spec.** Pin the generator version. Make the output deterministic: stable `operationId`s, `$ref` instead of inline schemas, `$ref`'d `oneOf` branches, stable enum order. Phantom diffs would teach the team to turn the gate off.
3. **Baselines.** Commit `specs/<version>.yaml` for every supported version, at each release tag. The first release has no baseline: write its entries by hand and diff from there.

## 2. Severity map

I wrote `api/severity-map.md` in the skill's table format. Every row is **provisional** until your policy is signed, which is where the table below is incomplete.

| Check id | Level | Policy line | Status |
|---|---|---|---|
| `response-property-enum-value-added` | warn | TBD: are response enums open? If yes, declare `x-extensible-enum` per field and pin to `info`. | provisional |
| `api-security-scope-removed` | err | Announce every auth change, even though this one widens access. | provisional |
| `response-required-property-removed` | err | Tool default. | provisional |
| `api-removed-without-deprecation` | err | Removals need a prior deprecation. | provisional |
| `api-major-version-not-bumped` | none | Date versions: oasdiff skips this check on non-semver versions anyway. | provisional |

- Verify every check id against the pinned oasdiff version. The skill's `tool-configuration.md` pins `v1.34.1` as an example.
- Generate `oasdiff-levels.txt` from this table in CI. Do not maintain it by hand, and do not put comments in it.
- Add `x-sunset` and `deprecated` to the lifecycle of every deprecated operation, so removals are judged correctly.
- Pin a level only where the policy contradicts the tool default. The skill gives the reason: pinning disables the tool's own downgrades for that check.
- Payments-specific rows to ask the policy owner: money-field precision, currency enums, idempotency semantics, webhook payload shape, error codes. Error codes and message meaning are invisible to the diff, so they live in the declared channel.

## 3. Baselines, one per job

| Job | Compare against |
|---|---|
| PR gate | merge base on `main`, on the **partner projection** |
| Published changelog | for version N, `specs/N.<audience>.yaml` at the previous release tag. A new version is also diffed against its predecessor. |
| Drift alarm | the spec the production service actually serves, diffed with `oasdiff diff --fail-on-diff` against the spec built from the deployed commit |

- A diff inside a version that is supposed to be frozen is a defect, not a changelog entry.
- A break that ships only in a new version appears under that version and nowhere else.
- Never publish "changes per deploy". Pinned callers would read changes that exist only in a later version.

## 4. PR gate

The workflow is the skill's GitHub Actions shape, run against the partner projection.

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
        with: { fetch-depth: 0 }
      - name: Install pinned oasdiff
        run: go install github.com/oasdiff/oasdiff@${OASDIFF_VERSION}
        env: { OASDIFF_VERSION: v1.34.1 }
      - name: Audience lint and projections
        run: python3 tools/project-audiences.py --spec api/openapi.yaml --out api/build/
      - name: Regenerate level and ignore files
        run: |
          awk -F'|' '$2 ~ /^ *[a-z0-9-]+ *$/ && $3 ~ /^ *(err|warn|info|none) *$/ {gsub(/ /,"",$2); gsub(/ /,"",$3); print $2, $3}' api/severity-map.md > api/oasdiff-levels.txt
          python3 tools/build-entries.py --acks api/acks.json --ignore-out api/oasdiff-err-ignore.txt
      - name: Gate
        run: |
          base="$(git merge-base origin/${{ github.base_ref }} HEAD)"
          git show "$base:api/openapi.yaml" > /tmp/base.yaml
          python3 tools/project-audiences.py --spec /tmp/base.yaml --out /tmp/base-build/
          oasdiff breaking /tmp/base-build/partner.yaml api/build/partner.yaml \
            --severity-levels api/oasdiff-levels.txt \
            --err-ignore api/oasdiff-err-ignore.txt \
            --fail-on ERR -f githubactions
```

- `tools/project-audiences.py` is the one new script. The skill does not ship it, so write and test it before wiring the gate.
- Commit `api/acks.json` as `[]` and an empty `api/oasdiff-err-ignore.txt` at setup. oasdiff exits 121 if the ignore file is missing.
- Show `warn` findings in the PR summary as "potentially breaking". Never drop them silently.
- Put `openapi.yaml`, `severity-map.md` and `acks.json` under one CODEOWNERS rule with required review from an `api-review` group. Without that rule, the `approver` field enforces nothing and an author can approve their own break.
- Copy the skill's two scripts into `tools/` so CI runs a reviewed, pinned copy.

## 5. Declared-change channel

A diff can't see behavior. Add this block to the PR template:

```
### API contract
- [ ] No change to the published API
- [ ] Spec changed (the contract diff will classify it)
- [ ] Behavior changed without a spec change: defaults, validation, error codes or bodies,
      auth, rate limits, pagination, ordering, timing -> add a change fragment
```

- Fragments are one JSON file per change in `api/changes/`. The format and the `kind` and `classification` values are in `blind-spots-and-declared-changes.md`.
- A fragment's `api_versions` lists every version whose callers see the change. More than the newest version means pinned partners are affected, so the versioning policy's exception path decides whether it may ship.
- A breaking fragment needs an acknowledgement row whose `covers` lists its `id`.
- Reviewers ask for a fragment whenever the diff touches handlers but not the spec.
- Fragments get an `audience` too. A fragment about an internal endpoint never reaches the public feed.

## 6. Approval record

- Each accepted break gets an `acks.json` row with these fields:
  - `covers`, `check`, `operation`, `path`, `text`
  - `reason` (`intended-break-new-version`, `spec-correction`, `security-exception`, `historic`)
  - `approver`, `date`, `ticket`, `notice` link
- `build-entries.py --acks acks.json --ignore-out ...` writes the ignore file. Never edit it by hand.
- A spec correction needs `behaving_since`. It still produces an entry.
- Delete a row whose change no longer appears.
- If someone has been hand-adding lines to an ignore file already, audit it before go-live. Freeze new hand-added lines from the day the audit starts. The procedure is in step 6 of the skill.

## 7. Entries and feed

Per audience (`public`, `partner`) and per `api_version`:

```
oasdiff changelog specs/<N>.<audience>.yaml@<prev-tag> specs/<N>.<audience>.yaml -f json > changelog.json
python3 tools/build-entries.py --changelog changelog.json --api-version <N> \
  --date <date> --fragments api/changes/ --acks api/acks.json --out entries.json \
  --ignore-out api/oasdiff-err-ignore.txt
```

That's the command shape. Adapt the baseline argument to `git show <tag>:path` or oasdiff's `ref:path` form.

- The script writes skeleton entries with `summary` and `action_required` blank. A human fills them from the PR or fragment narrative.
- Entry schema: use the skill's fields unchanged. They are `id` (`<api_version>/<first fingerprint or fragment id>`), `api_version`, `date`, `area`, `operations`, `kind`, `classification`, `source`, `covers`, `summary`, `tool_text`, `action_required`, `sunset`, `links`.
- Classification is `breaking`, `potentially-breaking` or `non-breaking`. Exclude documentation-only edits and version-bump findings.
- Fingerprints carry no file name, so run the build once per projection. The same change can then appear in both feeds with different audiences.

**Published artifacts**

| URL (placeholder domain) | Content |
|---|---|
| `https://docs.velmora.example/changelog/public/feed.json` | all public entries, newest version first, breaking first within a version |
| `https://docs.velmora.example/changelog/public/feed.atom` | same entries as Atom |
| `https://docs.velmora.example/changelog/partner/feed.json` and `.atom` | public plus beta, behind partner auth |
| `https://docs.velmora.example/changelog/public/<version>.json` | the entries for one version, a slice of the same data (my addition) |

The JSON feed is an object with `feed_version`, `api`, `generated_at`, `entries`. Rules for the pollers:

- Entry ids are stable and entries are immutable. A correction is a new entry, never an edit.
- Serve with `ETag` and `Last-Modified` so bots can poll cheaply.
- Put `action_required` in the feed, not only on the page.
- Atom `<id>` is a tag URI such as `tag:velmora.example,2026:payments/2026-10-01/a3f8c21b9d04`. Use `<category term="breaking"/>` plus one category per area. Agents and chat integrations drop links, so the action text goes in the content.
- Publish the feed file last, after every per-version file is in place. A poller then never sees an entry whose slice is missing.
- A consumer filters on `api_version` and `classification`. It parses no prose.

**Human page.** Render one page per version from the same entries: Breaking changes, then Potentially breaking, then additions and deprecations. Retire the hand-edited HTML. Marketing copy goes to a separate announcements stream and is not the contract record. Pass the traced entries to `changelog-writing` for prose, and each breaking entry to `version-migration-guide` if callers need before/after code.

## 8. Verification before every publish

```
python3 tools/check-entry-trace.py --diff changelog.json --entries entries.json \
  --fragments api/changes/ --api-version <N> --acks api/acks.json
```

Publish only if it exits 0, then run the output leak check from step 0.

- Trace check: no untraced entries, no classification changes, no missing actions, no breaking finding without an entry, no breaking entry without an approval covering every source.
- Leak check: every operation in the public feed exists in the public projection.
- An LLM may shorten or reword an entry. It may not add a path, field, status code, date or consequence the source lacks. Rerun the trace check after any rewrite.
- Do both checks on the final artifacts, not on intermediate files.

## Failure modes to watch

- **Gate switched off by noise.** Nondeterministic generated specs cause phantom diffs. Fix the generator, never the threshold.
- **Spec drift rewarded.** Engineers stop updating the spec to keep CI green. The drift alarm catches this. Without it the gate measures fiction.
- **Audience marker forgotten.** The mandatory lint in step 0 is what blocks this. Do not weaken it to make a PR pass.

## Measures

- **Leaks:** non-public operations in any public output. Target zero, enforced by the output check.
- **Escaped breaks:** breaking changes reported by partners or support with no entry. Target zero. Each one becomes a blind-spot row or a severity-map row.
- **Trace coverage:** 100% before any publish.
- **Acknowledgement hygiene:** rows lacking approver, ticket or link. Target zero.
- **Override rate:** accepted `err` findings per release. A rising rate means the severity map has drifted from the policy.

## Questions for you

1. Is there a written breaking-change policy? If not, should I route this to `api-versioning-policy` first? Until then everything stays provisional.
2. Is `openapi.yaml` generated or hand-written, and is it validated against the running service?
3. Does Velmora serve all dated versions from one codebase through transformers? If yes, I would promote the version-derived changelog.
4. Which marker identifies beta operations today? Does `/v1/payouts/instant` have real callers? Check this before moving it to `partner`.
5. What is the deadline? A hard date means shipping rungs 0 and 1 alone first.
6. What do you want done about the notes that already leaked: correct, retract or leave?