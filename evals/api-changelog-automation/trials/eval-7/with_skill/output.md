# Automated partner changelog for Corrigan Rail's gRPC and grpc-gateway setup

This follows the `api-changelog-automation` skill and its three references. I didn't run the skill's interview, so the assumptions I made are listed at the end. Please correct them.

## Summary

The current setup can't produce a partner changelog, for three reasons:

1. **`WIRE` is the wrong level for a JSON facade.** It misses breaks that only JSON clients see.
2. **Partners consume the REST/JSON facade, and `buf breaking` can't see it.** It ignores custom options such as `google.api.http`, so a change to a route, verb or body mapping passes every buf category. The facade needs its own diff, run on the generated OpenAPI.
3. **No changelog layer exists.** There is no release baseline, no declared-change channel for behavior changes, no approval record, no entry schema and no feed.

## 1. Change `buf.yaml`

`WIRE` ignores JSON field names, so renaming a field breaks every partner and still passes. The skill says to use at least `WIRE_JSON` whenever any client speaks JSON. That covers grpc-gateway.

```yaml
version: v2
breaking:
  use:
    - WIRE_JSON
```

- `WIRE_JSON` is stricter than `WIRE` only on JSON-visible items such as field renames. It is looser than `FILE` and `PACKAGE`, which is where the internal noise came from. You can tell the internal teams that the new level adds only what partners actually experience.
- Keep `except` and `ignore_unstable_packages` for beta packages, so stability gates them (see step 3).
- Treat `ignore_only` and `except` entries in `buf.yaml` like an oasdiff ignore file. Every one needs an acknowledgement row (step 5) and must not be hand-added.

## 2. Add a diff of the generated OpenAPI

This is the main change. The partner contract is the OpenAPI document generated from your annotations, so diff that.

- **Generate it from the protos in CI.** Use `protoc-gen-openapiv2` or `protoc-gen-openapi`, and pin the plugin version.
- **Make the output deterministic.** The skill requires:
  - stable `operationId`s;
  - `$ref` schemas rather than inline ones;
  - stable enum order.
  
  Otherwise phantom diffs teach the team to turn the gate off.
- **Only annotated RPCs reach the partner spec.** gRPC-only and internal methods stay out. Mark anything partner-visible but not GA with `x-stability-level`. Mark internal operations with `x-internal` and filter them with `--filter-extension x-internal`.
- **Diff it with a pinned oasdiff.** Use `oasdiff breaking` on the PR and `oasdiff changelog -f json` on release.
- **Commit the generated spec for each release.** It exists only at build time, so you need `specs/<release>.yaml` or an attachment on the release tag. The first release has no baseline. Write its entries by hand and diff from there.
- **Keep `buf breaking` as a second gate.** It covers the gRPC surface and wire compatibility. The OpenAPI diff covers the partner JSON contract. Neither replaces the other.

## 3. Use three baselines, one per job

`--against '.git#branch=main'` is one baseline doing everything. The skill calls reusing one baseline for all three jobs the most common design error.

| Job | Baseline | Your change |
| --- | --- | --- |
| PR gate | Merge base with `main` | Compare against the merge-base commit, not the tip of `main`, so changes merged earlier aren't blamed on the PR. For buf use `.git#ref=<merge-base-sha>`; check the exact syntax against your pinned buf version. For oasdiff use `$(git merge-base origin/main HEAD):api/openapi.yaml`. |
| Published changelog | Spec of the last **released** tag | Add a release job: `oasdiff changelog <last-tag>:api/openapi.yaml api/openapi.yaml -f json`. Run `buf breaking --against` the same tag too. |
| Drift alarm | The spec production serves, or live traffic validated against it | Schedule a job that diffs the served spec against the spec built from the deployed commit. If production serves none, validate sampled traffic against the spec. |

CI needs `fetch-depth: 0` for git-revision baselines.

## 4. Write the severity map from a written breaking-change policy

Tool defaults are not your policy:

- oasdiff and openapi-diff flag a new response enum value by default. GitHub's published policy calls it additive.
- oasdiff rates removed scopes and an added alternative auth requirement as INFO.
- Gateway-only auth rules are invisible to every diff.

Do this:

1. **Get the written definition.** If none exists, route it to `samber/developer-platform-skills@api-versioning-policy`. If you must ship a gate first, mark every severity-map row `provisional`.
2. **Create `severity-map.md`.** One row per check id, with the policy line it enforces, the level and the status.
3. **Generate the level file from it.** Generate `oasdiff-levels.txt` in CI. It accepts only `<check-id> <level>` lines, with no comments.
4. **Handle enums.** Pin the enum check to `info` only if the policy says every response enum is open. Otherwise mark the specific fields `x-extensible-enum`.
5. **Handle version bumps.** Raise the version-bump checks to `err` only if you use semver `info.version`. For URI-path or date versions, the per-version baselines do that job.
6. **Mark lifecycle.** Use `deprecated`, `x-sunset` and `--deprecation-days-stable=N` so removals are judged against the notice window.

For buf, the mapping is as follows:

- **Level:** buf has no level file. Keep the same table next to `buf.yaml`.
- **Fingerprints:** buf findings carry no stable id. Give each one `sha256("<id>:<operation>:<path>:<args>")[:12]`.
- **Hash inputs:** use element names, never the message text. A reworded message in a buf upgrade would orphan every acknowledgement.
- **Mapping:** keep the mapping script in the repo.

## 5. Gate and approvals

- **Fail on `ERR`.** Show `WARN` in the PR summary as "potentially breaking" and never drop it.
- **Name an approver.** Put the spec, `severity-map.md` and the acknowledgement file under one `CODEOWNERS` rule with required review. Without that, an author approves their own break.
- **Add an acknowledgement file.** Commit `api/acks.json` as `[]` and an empty `api/oasdiff-err-ignore.txt` at setup. oasdiff exits 121 if the ignore file is missing. Each accepted break gets a row with:
  - fingerprints or declared id;
  - check, operation, path and exact tool text;
  - approver, date and ticket;
  - reason class;
  - a notice link;
  - `behaving_since` for spec corrections.
- **Generate the ignore file from the rows.** `python3 tools/build-entries.py --acks api/acks.json --ignore-out api/oasdiff-err-ignore.txt` runs before the gate. Nobody edits the file by hand.
- **Audit existing ignore files first.** If you already have hand-edited `buf.yaml` ignores or an oasdiff ignore file, audit every line before going live and freeze new hand additions from that day:
  - Delete the lines that match nothing.
  - Give each remaining line a row, using `historic` when nobody knows why it was added.
  - Give any hidden break callers never saw announced a late-notice entry.

## 6. Open the declared-change channel

A structural diff can't see behavior. Several grpc-gateway behaviors never appear in a proto or in the generated OpenAPI. These are my inference about your stack, not the skill's text:

- how gRPC status codes map to HTTP status codes;
- error body shape;
- field-mask handling;
- default and zero-value emission.

Add this to the skill's own blind-spot categories (validation tightening, defaults, rate limits, pagination and ordering, error meanings):

1. **PR template block.** Add the "API contract" block from the skill, including "Behavior changed without a spec change → add a change fragment".
2. **Fragments.** Each fragment is one JSON file under `changes/` with `id`, `api_versions`, `area`, `operations`, `classification`, `kind`, `summary`, `action_required`, `sunset` and `links`.
3. **Approval.** A breaking fragment needs an acknowledgement row that lists its id.
4. **Review habit.** Reviewers ask for a fragment when the diff touches handlers or gateway config but not the spec.

## 7. Entries and the partner feed

1. **Build entries from structured output only.** The inputs are the release-baseline `oasdiff changelog -f json` output, the fragments and the acknowledgement rows. Run it once per spec. For buf findings, map them to the same fields (`id`, `level`, `path`, `operation`, `text`, `fingerprint`).

   ```
   python3 tools/build-entries.py --changelog changelog.json --api-version <version> \
     --date <date> --fragments changes/ --acks api/acks.json --out entries.json \
     --ignore-out api/oasdiff-err-ignore.txt
   ```

2. **Grouping.**
   - One entry per contract change, grouped by API version, then by area, breaking first.
   - A shared-schema finding is one entry covering all its fingerprints.
   - Exclude version-bump findings, documentation-only edits and operations the audience can't see.
3. **Gate publishing on the trace check.**

   ```
   python3 tools/check-entry-trace.py --diff changelog.json --entries entries.json \
     --fragments changes/ --api-version <version> --acks api/acks.json
   ```

   - It must pass before publishing. Exit 0 is a pass, 1 means findings to fix, 2 means unusable input.
   - Any breaking change with no entry, or any entry without a source, fails the build.
4. **Publish two artifacts.**
   - A JSON feed at a stable partner URL, with `feed_version`, `api`, `generated_at` and `entries`.
   - An Atom feed with tag-URI ids and `action_required` in the content.
   - A human page per version: Breaking, then Potentially breaking, then additions and deprecations.
5. **Hand off.** Give the traced entries to `developer-relations-skills@changelog-writing` for prose. Give breaking entries to `version-migration-guide` when partners need before/after code. Any model rewrite may not add a path, field, status code or consequence absent from the source, and the trace check reruns after it.

## 8. Order of work

The default is PR gate plus release diff plus declared channel. Add the approval record once the first accepted break lands. Add the feed next if partners' monitoring or agents will consume it.

1. Switch `buf.yaml` to `WIRE_JSON`. This takes minutes and needs sign-off from the internal teams.
2. Add deterministic OpenAPI generation and the oasdiff PR gate on the merge base. Start with a `provisional` severity map. This is one to two hours, mostly reviewing the map.
3. Commit a per-release spec, add the release job, the PR template block and fragments. This takes about half a day plus a habit.
4. Add the acknowledgement file and `CODEOWNERS`. This takes a few hours.
5. Add the feed and the human page, about a day.
6. Add the drift alarm.
7. Skip usage-aware classification unless you have per-operation telemetry from the last 30-90 days.

If you have a fixed first-gate date, ship step 2 alone first.

## Assumptions to confirm

1. **Policy.** Is there a written breaking-change definition? Without one, everything stays `provisional`.
2. **Versioning.** Do you use URI-major (`v1`), date versions or continuous deploy? This decides the per-version baselines and what "a release" means for the changelog.
3. **Audience.** How are internal and beta RPCs marked, and are any partner-only operations in the same protos?
4. **Spec validity.** Is the generated OpenAPI checked against the running gateway, for example by contract tests? If not, the diff describes a document, not the API. Add contract tests or traffic validation, and list it as the first gap.
5. **Where the feed goes.** Is it a human page, RSS, JSON for partner tooling or an email digest?
6. **Deadline and effort.** When must the first gate run, and how many engineer-days can you commit?

Escaped breaks are the success metric. A partner-reported break with no changelog entry should be zero, and each one means a missing blind-spot or severity-map row.