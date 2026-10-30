# Hallowmere postmortem: is "more oasdiff checks, fail-on WARN" the fix?

**No.** It tunes the one part of the pipeline that did nothing wrong. I haven't seen your spec or CI config, so the first part rests on what the three changes were and how oasdiff works. I've marked what to verify.

## Why the VP's proposal fails

`fail-on WARN` and extra checks only change the verdict on findings oasdiff already produces. All three incidents most likely produced no finding at all.

| Change | Did the diff see it? | Why |
| --- | --- | --- |
| Default page size on `GET /orders` went from 100 to 20 | Only if the spec declares `default: 100` and a PR edited it | A handler-side default is invisible. If the spec declared it and the changelog stayed silent, the spec was never updated. That is drift. |
| `note` strings over 500 chars rejected in the handler | Only if the spec has `maxLength` on `note` | A handler-only rule leaves no spec diff. If the spec already said 500, the service was lying before the PR. |
| Per-key rate limit went from 600 to 300 req/min | Never | OpenAPI has no standard place for it, and gateway config is outside the spec. |

Three more problems with the proposal:

- **Wrong layer.** Your changelog is generated from the same diff. Gate strictness doesn't touch it. A tighter gate would still publish a changelog missing these three entries.
- **Noise.** `WARN` findings are "cannot be decided from the definition". Failing on them without a signed severity map trains people to set `fail-on none`. The skill lists this as a named failure mode.
- **Defaults aren't your policy.** Tools disagree with each other and with provider policies on enums, auth and removals of deprecated elements. Switching on more checks adopts someone else's opinion of "breaking" at higher volume.

The underlying error is trusting the diff tool twice. You trusted it for what counts as breaking, and for what changed at all. It only sees declared structure. Your green check meant "the document didn't regress", not "the API didn't".

Verify these before the postmortem is final:

1. Does the spec declare `default`, `maxLength` and `maximum` for `/orders`?
2. Is the spec checked against the running service (contract tests or traffic validation)? If not, the green result describes a document, not the API.
3. Do you have a written breaking-change definition? If not, the whole pipeline below is provisional until one exists.

## What to automate, in order

I'm assuming a standing pipeline, a hand-written or generated OpenAPI spec, and no usage telemetry. Change the order if your constraints differ. A hard deadline would ship the PR gate alone first.

**1. PR gate with a severity map you own (hours).**
- Keep `severity-map.md` next to the spec: one row per check id, the policy line it enforces, the level, and `provisional` until the policy is signed.
- Generate oasdiff's `--severity-levels` file from that table in CI so the two can't drift.
- Pin the oasdiff version, and fail on `ERR`.
- Show `WARN` in the PR summary as "potentially breaking". Never drop it silently.
- Put the spec, severity map and acknowledgement file under one code-owners rule with required review.
- This stops accidental spec-visible breaks. It would not have caught your three incidents.

**2. Declared-change channel (half a day, plus a habit). This is the real fix for the incidents.**
- Add a PR template block: "Behavior changed without a spec change: defaults, validation, error codes, auth, rate limits, pagination, ordering → add a change fragment."
- A yes requires a JSON fragment in `changes/`. It carries the affected operations, `classification`, `kind`, `action_required` and `api_versions`.
- All three incidents are fragment cases. Page size and rate limit are `breaking` or `potentially-breaking` per your policy. The `note` limit is a validation tightening.
- Declared breaks go through the same approval as diff-detected ones.
- A template box is a habit, not a control. Add a CI check that flags PRs touching handler, validation or gateway-config paths with no spec change, no fragment and no "no API change" tick. A path-based check will have false positives, and that is acceptable. A human answers the question and the build blocks until they do.

**3. Move invisible behavior into visible structure.**
- Declare `default: 100`, `maximum` and `maxLength: 500` in the spec. Once `note` has `maxLength`, oasdiff flags a later decrease on its own (my recollection is `request-property-max-length-decreased` at `ERR`; confirm against your pinned version).
- Mirror server validation into the spec, or generate both from one source.
- Put the rate limits in a config file in the repo, or in an `x-rate-limit` extension, and diff that file in CI. Any change requires a fragment. If the limit lives only in a gateway UI, move it to code first.

**4. Release diff against the last released spec, merged with fragments (half a day).**
- The PR baseline is the merge base. The changelog baseline is the spec at the last release tag.
- Commit the spec of every release. Run `oasdiff changelog <last-tag>:api/openapi.yaml api/openapi.yaml -f json`.
- Merge the output with fragments and acknowledgement rows. The skill's `build-entries.py` does this. Publish only if `check-entry-trace.py` passes.
- Every breaking finding or fragment must map to an entry, and every entry must trace to a source. This is how an omission becomes a build failure.

**5. Behavior contract tests on the surfaces callers depend on (days).**
- `GET /orders` without a limit returns exactly 100 items.
- A 500-char `note` is accepted and a 501-char one is rejected with the documented error.
- A key allows exactly N requests per minute.
- When a test changes, the PR must carry a fragment. A test assertion edit is a strong signal that a contract changed.

**6. Drift alarm (a day).**
- On a schedule, diff the spec the production service serves, or sampled traffic validated against the spec, with the spec built from the deployed commit.
- Drift is a spec-correction candidate. It gets an acknowledgement row with `behaving_since` and a changelog entry, never a quiet ignore-file line.

**7. Approval record, then feed.**
- Once the first accepted break lands, add acknowledgement rows with fingerprint, approver, ticket, reason class and notice link. Generate the ignore file from them.
- Publish the feed (JSON plus Atom, `action_required` inside the feed) once partners or their monitoring want to subscribe. Your three partners are the obvious first subscribers.

**Skip for now:**
- Usage-aware classification, because you have no telemetry. Add it later if you can count calls per operation per client.
- Version-derived changelog, which fits only date-versioned APIs with response transformers.

## Do this week

1. Backfill the three changes as fragments or spec-correction entries in the changelog, with `behaving_since` dates. Callers were never told, and partners deserve the record.
2. Count these three as your first **escaped breaks**. This is the metric to track, and the target is zero.
3. Write the breaking-change definition if it doesn't exist (route it to `api-versioning-policy`). It should answer these questions:
   - Is lowering a default, a limit or a quota breaking?
   - Is tightening validation breaking?
   - What notice window applies?
   Mark every severity-map row `provisional` until it is signed.
4. Audit any hand-edited oasdiff ignore file line by line. Each line that still matches something needs an acknowledgement row, and each one that hid a break needs a changelog entry. Freeze new hand additions from today.

## Questions that would change the plan

- Is the spec contract-first or generated? If it is generated, determinism work (stable `operationId`s, `$ref` schemas) comes before the gate. Otherwise phantom diffs kill it.
- Are there date or header versions? If so, the baselines and per-version entries change.
- Where do rate limits live (gateway, code, vendor UI)?
- How many engineer-days and which reviewers can you commit? That sets how far down the list you get this quarter.

## Measures of success

- **Escaped breaks:** partner-reported breaks with no changelog entry. Target zero.
- **Trace coverage:** 100% of published entries linked to a source.
- **Acknowledgement hygiene:** zero rows missing an approver, ticket or link.
- **Override rate:** accepted `ERR` findings per release. A rising rate means the severity map has drifted from the policy.

## Bottom line

Don't spend the quarter turning dials on oasdiff. Make behavior changes declarable and visible (steps 2 and 3), build the changelog from the last release plus those declarations (step 4), and check the spec against the running service (steps 5 and 6). The gate is a sensible first step, but it only covers what the spec already says.