# Velmora changelog publishing design

**Decision:** Stop publishing from `openapi.yaml`. Publish from a filtered public spec and a fragment-based changelog that can only describe public operations. Machine feeds, the HTML page, and agent-readable Markdown are all rendered from that one source.

Both asks share one root cause: no explicit line between public and internal. Fix the line first. The feed comes second.

## 1. Fix the leak: allowlist, fail closed

`x-internal` is a denylist. A forgotten flag means the endpoint ships publicly, which is how `/v1/payouts/instant` leaked. Use an allowlist instead.

1. **Add a required `x-visibility` field** on every operation, webhook, top-level schema, and tag. Values:
   - `public`
   - `public-preview`: opt-in, public, no stability promise
   - `internal`
   - `private-beta`
2. **Lint rule in CI:** fail if any operation lacks `x-visibility`. Default is "not published".
3. **Build a public spec:** keep only `public` and `public-preview`, then prune what is left:
   - unreferenced components
   - orphan tags
   - examples and descriptions that name removed things
   - enum values that expose internal states
   - security schemes only internal operations use
   
   Redocly's `filter-in` and `remove-unused-components` decorators or `openapi-format` can do this. Verify the exact decorator names against current docs before committing. A 50-line script also works.
4. **Add a public surface lockfile.** `public-surface.lock` lists every public `operationId`.
   - Any PR that changes it needs approval from the API-platform owner through CODEOWNERS.
   - The PR diff then reads "this PR publishes X", so promoting a beta is a deliberate act.
5. **The public spec is the only input to everything downstream.**
   - The diff tool, fragment validator, renderers, and SDK docs never see the full spec.
   - Anything not in the public spec cannot leak.

### Leak gate (it must be able to fail)

- **Canary operation.** Keep `/v1/__canary_internal` with `x-visibility: internal` in the internal spec.
  - Positive control: assert it exists in the internal spec.
  - Negative control: assert it is absent from the public spec and from every generated artifact.
  - Self-test: run the same assertion against the unfiltered spec on every CI run. It must fail there. If it passes, the check is blind.
- **Text scan.** Check every generated file for:
  - `x-internal`, `x-visibility: internal`, `private-beta`
  - any path-like string (`/v\d+/[\w/{}-]+`) not in the public spec
  - a committed codename denylist
- **Fragment prose gate.** Each fragment must reference only `operationId`s present in the public spec. Prose that names a non-public path fails. This catches a PR author writing "we are testing instant payouts".

### Policy for betas (my recommendation)

- A **private beta** never appears in any public artifact. Partners in the beta get docs through their own channel.
- A **public preview** appears with `stability: preview`. It is excluded from breaking-change classification, and its changes are marked non-binding.
- If beta partners also want machine-readable notices, add an authenticated feed keyed to their API key. This is phase 2. Never mix it into the public file.

## 2. Source of truth: fragments plus a computed diff

Two inputs, cross-checked:

- **Human fragment.** Each PR that changes the public surface adds `changelog/entries/<slug>.yaml`. The author writes it in the PR, not weeks later.
- **Computed diff.** CI runs `oasdiff` (`changelog` and `breaking`, JSON output) between the last published public snapshot and the new public spec.

CI rules:

1. Every diff item classified breaking or deprecated must be covered by a fragment, referenced by `operationId` plus a change kind. Otherwise the build fails.
2. Every fragment must match a real diff item or an explicit `behavioral: true` flag. This covers changes the spec cannot show, such as defaults, limits, and error semantics.
3. Fragment schema validation passes.
4. A breaking entry needs `action`, `affected`, and `migration_url`.

Result: the changelog cannot silently omit a breaking change, and it cannot describe something that is not public.

## 3. Date-based versions

Velmora versions are dates, such as `2026-10-15`. Model them like this:

- **`api_version`** on an entry is the version where the change takes effect. It is `null` for additive changes that apply to all versions.
- **Breaking changes** exist only in a new dated version. Entries state "accounts pinned to an earlier version are unaffected until they upgrade".
- **Additive changes** carry `api_version: null`, so bots know no pin change is needed.
- **Snapshots are immutable.** Publish `specs/<version>.yaml` per version, plus `diffs/<from>..<to>.json` (the oasdiff output).
- **Runtime signals use the same entry IDs.** Add `Deprecation` and `Sunset` headers on affected responses. Include a `Link: rel="deprecation"` pointing at the entry permalink.

## 4. Published artifacts

Static files on a CDN, no origin server. Base: `https://docs.velmora.com/changelog/v1/`. Substitute the real docs domain.

| Path | Format | Audience |
|---|---|---|
| `index.json` | tiny JSON | pollers |
| `entries/YYYY-MM.json` | JSON, monthly page | pollers, backfill |
| `changelog.json` | JSON, last 100 entries | simple bots |
| `feed.atom` | Atom | RSS readers, generic tools |
| `changelog.md` | Markdown | coding agents, LLM context |
| `entries/<id>` (HTML) | permalink page | humans, deep links |
| `schema/changelog-v1.schema.json` | JSON Schema | consumers validating |
| `specs/<version>.yaml`, `diffs/<a>..<b>.json` | OpenAPI, oasdiff | tooling |
| `/changelog` (HTML) | rendered page | humans, replaces the marketing page |

All except the monthly pages and snapshots are regenerated on each publish. The HTML page renders from the same JSON. Nobody edits it by hand. Add an `llms.txt` pointer to `changelog.md` and the schema.

### `index.json`

```json
{
  "schema_version": 1,
  "updated_at": "2026-10-30T09:12:44Z",
  "latest_api_version": "2026-10-15",
  "latest_entry_id": "2026-10-28.payout-fee-field",
  "entry_count": 214,
  "pages": ["entries/2026-10.json", "entries/2026-09.json"],
  "signature_url": "index.json.sig"
}
```

### Entry

```json
{
  "id": "2026-10-28.payout-fee-field",
  "kind": "additive",
  "severity": "info",
  "stability": "stable",
  "published_at": "2026-10-28T14:03:00Z",
  "effective_at": "2026-10-28T14:03:00Z",
  "api_version": null,
  "title": "Payout objects include a fee field",
  "summary": "GET /v1/payouts and GET /v1/payouts/{id} now return fee in minor units. Existing fields are unchanged.",
  "affected": {
    "operations": [
      {"operation_id": "listPayouts", "method": "GET", "path": "/v1/payouts"},
      {"operation_id": "getPayout", "method": "GET", "path": "/v1/payouts/{id}"}
    ],
    "schemas": ["Payout"],
    "webhook_events": [],
    "sdks": []
  },
  "action_required": false,
  "action": null,
  "deadline": null,
  "migration_url": null,
  "supersedes": null,
  "spec_diff_ref": "diffs/2026-10-15..2026-10-28.json#/changes/4",
  "url": "https://docs.velmora.com/changelog/v1/entries/2026-10-28.payout-fee-field",
  "revisions": []
}
```

Field rules:

- **`kind`** is an enum: `breaking | deprecation | removal | additive | fix | security | behavior`. Bots branch on enums, not prose.
- **`summary`** is plain text, 280 characters or fewer, with no marketing adjectives. Prose is data to bots and may be fed to coding agents. Write no instructions in it, only facts. Actions go in the structured `action` and `deadline` fields.
- **IDs are stable and never reused.**
- **Entries are append-only.** Corrections add to `revisions[]` with `revised_at` and a reason. A mistaken entry gets `status: retracted`, never deletion, so a bot that already acted on it sees the correction.
- **Future-dated entries** (`status: scheduled`, `effective_at` in the future) announce deprecations and sunsets early.
- **Within `/v1/`, schema changes are additive only.** A breaking schema change moves to `/v2/` with a long overlap. Consumers should ignore unknown fields.

## 5. Polling contract

- **Poll `index.json`.** Send `If-None-Match` and `If-Modified-Since`.
  - A `304` means nothing changed. Compare `latest_entry_id` otherwise.
- **Cache headers:** `Cache-Control: public, max-age=300, stale-while-revalidate=3600`, with an `ETag` on every file.
- **Recommended interval:** 15 minutes. No auth, no rate-limit surprises, because it is CDN-served. Document this in one short docs page: `/docs/changelog-api`.
- **Fetching a gap:** read the monthly pages from the newest backward until you hit the last seen ID.
- **Integrity:** publish an Ed25519 detached signature (`index.json.sig`) and the public key at a fixed URL. Bots that auto-act on a deprecation should verify it. Optional for casual consumers, but cheap to add on day one.
- **Atomic publish:** upload all files to a versioned prefix, then flip a pointer. A poller never sees an index that references a page not yet uploaded.

### Consumer flows

- **Monitoring bot:** poll `index.json` → new entry → filter on `kind in (breaking, deprecation, removal, security)` and on `affected.operations` against the partner's own call list → alert with `deadline` and `migration_url`.
- **Coding agent:** read `changelog.md` or `changelog.json` plus `schema/` and `specs/<pinned-version>.yaml` → match `affected.operations` to the repo's API calls → open a migration PR using `action` and `migration_url`.

## 6. Pipeline and ownership

1. PR touches `openapi.yaml`:
   - lint (`x-visibility` required)
   - build the public spec
   - run the leak gate, the oasdiff check, and the fragment coverage check
   - show the lockfile diff
2. Merge to `main`. Nothing is published yet.
3. After the production deploy succeeds, the release job sets `published_at`, renders all artifacts, signs the index, and publishes atomically. The feed never announces an undeployed change.
4. Post-publish check: fetch the live `index.json`, confirm the new entry ID, and run the leak scan on the live files.

| Role | Owns |
|---|---|
| Engineers | write fragments in the PR |
| API-platform owner | `x-visibility`, `public-surface.lock` approvals |
| DevRel or tech writer | fragment review, wording, migration pages |
| Marketing | narrative announcements, linked via `announcement_url`. They cannot edit factual fields. |

This removes "updated whenever product remembers". The PR cannot merge without the fragment.

## 7. Rollout

1. **Day 1–2:** add `x-visibility` to all operations (default `internal`, then promote the approved public list). Build the public spec filter, the canary, and the leak gate.
2. **Day 2–3:** write the fragment schema and the oasdiff check. Run it on the last 3 releases to tune.
3. **Day 3–5:** renderers (JSON, Atom, Markdown, HTML), CDN publishing, signature, and the docs page.
4. **Day 5–6:** backfill the last 12 months from the marketing page into entries marked `source: backfill`. Use only information already public. Redirect the old page to `/changelog`.
5. **Day 6–7:** announce to partners, then run one live release through the pipeline.

Estimate: about 1 engineer-week for the core, plus 2–3 days for backfill and docs. One person executing could finish by mid-November.

## 8. Cleanup of the past leak

- Check whether the old release notes naming `/v1/payouts/instant` and the `x-internal` endpoints sit in CDN caches, a web archive, or partner copies. Retraction is best-effort.
- Decide whether anything exposed is a security concern. If an admin endpoint was reachable, treat it as an incident, separate from this design.
- Don't mention the leaked names in any public correction. Replace the page and move on.

## Decisions I need from you

1. **Beta policy:** confirm private beta stays invisible and public preview is opt-in (my recommendation), or do you want an authenticated beta feed in phase 1?
2. **Domain and path:** is `docs.velmora.com/changelog/v1/` right?
3. **Backfill depth:** 12 months, or only from the date-versioning start?
4. **Signing:** day one (my recommendation), or defer?

**Next:** answer decisions 1 and 2. Then the first concrete step is adding the `x-visibility` lint rule and the canary operation to `openapi.yaml`.