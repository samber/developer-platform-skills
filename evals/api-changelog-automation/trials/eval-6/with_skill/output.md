# Fenmoor breaking-change gate: ship the PR gate by Friday, stage the rest

I haven't touched the Fenmoor repo. This is the design, with files you can paste in. I treated your answers as Interview Q2 (hand-written spec), Q3 (no policy) and Q8 (Friday, about one engineer-day). Q1, Q4, Q5, Q6 and Q7 are still unanswered.

## What I'm not building this week

You asked for the full thing. One engineer-day buys the PR gate, plus the two cheap files that make overrides auditable. The skill's rule for a fixed date is to ship the PR gate alone first. It also says a standing mandate promotes the other rungs afterward.

| Rung | This week | Why |
| --- | --- | --- |
| PR gate (oasdiff, fail on ERR) | ✅ Ship | Stops the "renamed field" class of accident |
| Approver rule (CODEOWNERS) and empty `acks.json` | ✅ Ship | About 30 minutes. Without them, an author approves their own break |
| PR template question | ✅ Ship | 10 minutes. Starts the habit that feeds the next rung |
| Release diff and declared-change channel | ⏳ Next week | Half a day plus a habit |
| Approval record (full) | ⏳ At the first accepted break | A few hours, then minutes per break |
| Changelog feed (JSON and Atom) | ⏳ Week 3 | About a day. Move it up if partners' monitoring or agents need it (Q7) |
| Usage analytics | ❌ Deleted until you have per-operation telemetry | The skill says to delete this rung when there's no usage data. Say so if you do have it (Q6) |

## ⚠️ The gate cannot promise "breaking changes are blocked"

The CTO's wording needs a correction before Friday. oasdiff compares two copies of a document. It sees only what the spec declares.

- **Your spec is hand-written and not validated against the service.** If last week's rename happened in code and nobody updated `openapi.yaml`, the gate would have been green. Check the post-mortem. Did the rename PR change the spec?
- **If it did, the gate would have caught it.** Even then, oasdiff rates a removed optional response property as WARN, not ERR, so I pin that check below.
- **If it didn't, you need the drift alarm.** That means a scheduled diff against the spec production serves, or contract tests. Put it first in the week-2 plan, ahead of the feed.

Tell the CTO this on Friday: "PR gate blocks spec-level breaks. Code-only breaks need the drift alarm and the PR-template fragment, which come next."

## No written policy, so every severity is provisional

Every severity here is my choice or the tool's default, not Fenmoor's rule. Mark the map `provisional`. Get the CTO or API owner to sign the one-line policy below, or route a real one to `api-versioning-policy`.

The strict starting policy to sign: "Any change that makes a conforming existing client fail is breaking. That covers removing or renaming anything, narrowing types, and adding required inputs. Additions are not breaking."

Then pin only the checks that policy contradicts, and leave everything else at oasdiff's defaults.

## Files to add

Paths assume the spec lives at `api/openapi.yaml`. Change them if it doesn't.

**`api/severity-map.md`**

```
| Check id                            | Level | Policy line                                   | Status      |
| ----------------------------------- | ----- | --------------------------------------------- | ----------- |
| response-optional-property-removed  | err   | Rename or removal of a response field breaks  | provisional |
```

Before merging, run `oasdiff checks` on the pinned version and confirm the check ids exist. oasdiff rejects an unknown id in the level file. Also look for the request-side equivalents, such as a renamed request property or parameter, and add them as rows if they default to WARN.

**`api/acks.json`**: commit it containing exactly `[]`.

**`api/oasdiff-err-ignore.txt`**: commit it empty. oasdiff exits 121 if a passed ignore file doesn't exist.

**`tools/build-entries.py`**: copy it from the skill's `scripts/` folder, so CI runs a reviewed copy. I couldn't list that folder in this session, so confirm the script is there. It regenerates the ignore file from `acks.json`, so nobody hand-edits it.

**`.github/workflows/api-contract.yml`**

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
          fetch-depth: 0            # merge-base baseline needs history
      - name: Install pinned oasdiff
        run: go install github.com/oasdiff/oasdiff@${OASDIFF_VERSION}
        env:
          OASDIFF_VERSION: v1.34.1  # confirm this tag exists; bump deliberately
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

The gate diffs against the merge base, not the last release. A PR is therefore blamed only for its own changes. WARN findings still show in the PR output.

**`.github/CODEOWNERS`**

```
/api/openapi.yaml       @fenmoor/api-review
/api/severity-map.md    @fenmoor/api-review
/api/acks.json          @fenmoor/api-review
```

Then turn on branch protection with "Require review from Code Owners" and make the `api-contract` check required. Without both, the gate is advisory and an author can approve their own break.

**PR template block** (from the skill's blind-spots reference)

```
### API contract
- [ ] No change to the published API
- [ ] Spec changed (the contract diff will classify it)
- [ ] Behavior changed without a spec change: defaults, validation, error codes or bodies,
      auth, rate limits, pagination, ordering, timing -> add a change fragment
```

The third box doesn't produce changelog entries yet. It starts the habit and tells reviewers to ask for the spec update when handlers change but the spec doesn't.

## One-day plan

1. **Hour 0-0.5:** Read the last-week post-mortem and answer the spec-or-code question above.
2. **Hour 0.5-1.5:** Run `oasdiff breaking <last-release-tag>:api/openapi.yaml api/openapi.yaml` locally. This shows how noisy the spec is. Note that a hand-written spec may contain old inconsistencies. If an old ignore file exists, don't carry it over. Audit it per step 6 of the skill, and freeze new hand-added lines now.
3. **Hour 1.5-3:** Write the severity map, workflow, CODEOWNERS and template. Run `oasdiff checks` and fix ids.
4. **Hour 3-4.5:** Open a test PR that renames a response field in `openapi.yaml`. **The gate must go red.** If it stays green, the check level or id is wrong. A gate you've never seen fail proves nothing.
5. **Hour 4.5-5.5:** Open a second test PR that adds an optional field. It must pass. Then merge the real PR with required checks on.
6. **Hour 5.5-6.5:** Write the one-paragraph policy for sign-off, and a note for the CTO on what the gate does not cover.

## After Friday

1. **Week 2:** Drift alarm (served spec diffed against the commit's spec, on a schedule). Then the release diff, declared-change fragments, and `acks.json` rows with approver, ticket and notice link.
2. **Week 3:** Entry generation, trace check and the JSON and Atom feed, if partners or agents will consume it.
3. **Later:** Usage-aware classification, only once per-operation telemetry exists.

## Questions that change the plan

- Was the spec updated in the rename PR? If not, the drift alarm moves ahead of everything else.
- Does the spec contain internal or beta operations? They need `--filter-extension` or `--stability-level` before the gate can fail on them.
- Is `info.version` semver? If so, raise `api-major-version-not-bumped` to `err`. Otherwise skip it.
- Can you count calls per operation per client over 30-90 days? Without that, usage analytics stays deleted.