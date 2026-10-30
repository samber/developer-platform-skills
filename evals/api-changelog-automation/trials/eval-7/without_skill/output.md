# Automated partner API changelog: what to change

## Short answer

Your current `buf breaking` setup can't produce this changelog, for three reasons:

1. **`WIRE` checks the wrong contract.** Partners use JSON, and JSON depends on names, not field numbers.
2. **buf ignores `google.api.http` options.** It doesn't compare them, so route changes go unreported.
3. **buf reports only breaking changes.** A changelog also needs additions and deprecations.

The fix is to keep buf for the gRPC gate and add a second contract check on the generated OpenAPI spec for the JSON facade. The changelog is built from the OpenAPI diff.

## Why WIRE misses partner-visible breaks

These are all legal under WIRE and all break JSON clients:

| Change | Wire | JSON facade |
|---|---|---|
| Rename field `train_id` to `trainId` | OK | Key changes, so clients break |
| Rename an enum value | OK | The string changes, so clients break |
| Change `json_name` | OK | Key changes |
| `int32` to `int64` | OK | Number becomes a string (proto3 JSON) |
| Change `google.api.http` path, verb, `body` or `response_body` | Not checked | URL or shape changes |
| Move a field between path, query and body | Not checked | Request shape changes |
| Remove an RPC that has an HTTP binding | Probably not caught (see below) | Endpoint disappears |
| Change gateway marshaller options (`UseProtoNames`, `EmitUnpopulated`, enums as ints) | Not in the protos at all | Every response shape changes |

I'm recalling buf's rule categories from memory: I believe `WIRE` omits RPC/service deletion checks, which `FILE` includes. Confirm the exact membership with `buf config ls-breaking-rules`.

## Changes, in order

1. **Add an OpenAPI generation step.**
   - Use `protoc-gen-openapiv2` from grpc-gateway, or gnostic's `protoc-gen-openapi`.
   - Pass the same options your gateway runs with, so the spec matches real responses.
   - Pin the plugin version. A plugin upgrade can change the output and show up as a fake API change.
2. **Diff the specs with `oasdiff`.**
   - `oasdiff changelog` gives added, changed, deprecated and removed items, each with a severity level.
   - `oasdiff breaking` is the gate.
   - Both output JSON or Markdown.
   - This is the actual changelog source.
3. **Change the base of the comparison.**
   - `.git#branch=main` works for PR gating only. After merge it compares main to itself.
   - For release notes, diff the previous release tag against the new one, for example `.git#tag=v1.4.0`.
   - Use full git history in CI (`fetch-depth: 0`) so tags resolve.
4. **Tighten buf for the surface partners use.**
   - Switch from `WIRE` to `WIRE_JSON` at minimum. It adds field-name and JSON-name checks.
   - Add RPC and service deletion rules explicitly in `use`.
   - On the noise complaint: `FILE` is noisy mostly from file moves and package renames. Use `ignore_unstable_packages: true`, and `ignore_only` for specific paths, instead of dropping to a weak category.
   - If internal packages must stay on `WIRE`, split the partner-facing protos into their own buf module with stricter config.
5. **Mark what partners see.**
   - Internal RPCs and fields must not appear in the changelog.
   - Use a visibility annotation, for example OpenAPI visibility options or a custom option, and filter on it before diffing.
   - Otherwise internal changes leak into partner notes.
6. **Add a human step.**
   - A tool can't see behavior changes: new validation, default values, error-code mapping, rate limits.
   - Have the pipeline open a draft changelog PR. Reviewers edit it and add migration notes, then publish.
   - Deprecations need `deprecated = true` on RPCs and fields, plus a sunset date convention. Write that convention down.
7. **Publish.**
   - Store changelog entries as versioned files, one per release, and render them to the partner docs site or an RSS feed.
   - Keep the machine-readable JSON as well, for partner tooling.

## CI shape

- **On each PR:**
  - Run `buf lint` and `buf breaking` (internal gate).
  - Generate the OpenAPI spec and run `oasdiff breaking` against main.
  - Fail on partner-breaking changes unless the PR carries an explicit "approved breaking" label.
- **On release tag:**
  - Generate the spec at the previous tag and the new tag.
  - Run `oasdiff changelog`.
  - Open the draft changelog PR.

## Questions for you

1. Are partner-facing protos separable from internal ones, or does everything share packages?
2. Do you version via URL (`/v1/`) or only via proto package? That decides whether a breaking change is ever allowed in place.
3. Which marshaller options does the gateway run with today? I need them to configure the OpenAPI generator.

**Next action:** run `buf config ls-breaking-rules` to see exactly which rules `WIRE` covers, then decide on item 4.