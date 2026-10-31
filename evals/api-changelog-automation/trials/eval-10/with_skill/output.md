# Entry and id design for the Driftwood Ledger change feed

**Don't key entries on the field or element name.** Key them on a fingerprint hashed from the tool's structured output, and prefix it with the API version. The security fix is a declared change in the same feed, with one entry per affected version.

I read the skill and its three references. I ran no tools against your repo. The schema below follows the skill's reference format, and the surface and backport details are my adaptation of it.

## 1. Why name-keyed dedupe breaks

A name identifies a thing. It doesn't identify a change to that thing. Dedupe on name and these cases collapse or collide:

- **Several changes to one field.** `Shipment.legacyTrackingCode` is deprecated in 2026-04-15 and removed in 2026-07-15. Both share a key, so the second is dropped as a duplicate. The removal is the break callers care about.
- **Several changes in the same version.** A field's type changes and one of its arguments is removed. Both are real entries.
- **Same change, several versions.** The security fix reaches three versions. Deduping on name leaves one entry, so callers pinned to the other two never see it.
- **A name that exists on both surfaces.** `Shipment` or `trackingCode` can appear in the GraphQL schema and in a proto message. The key must say which surface it came from.

## 2. Fingerprint

graphql-inspector and buf emit no change id, so you build one. The skill's mapping (`tool-configuration.md`, "Fingerprints for tools that emit none"):

| Field | GraphQL (graphql-inspector) | gRPC (buf breaking) |
| --- | --- | --- |
| `id` | change type, e.g. `FIELD_REMOVED` | rule id, e.g. `FIELD_NO_DELETE` |
| `path` | schema coordinate, e.g. `Shipment.legacyTrackingCode` | `file:element`, e.g. `ledger/v1/shipment.proto:Shipment.tracking_code` |
| `operation` | root operation, else empty | RPC when one applies, else empty |
| `args` | the change's structured `meta` values | element names or before/after values |
| `level` | `3` breaking, `2` dangerous, `1` non-breaking | the same, from your severity map |

```
fingerprint = first 12 hex of sha256("<id>:<operation>:<path>:<args>")
```

- **Never hash the message text.** A tool upgrade that rewords a message would re-key every finding and orphan every acknowledgement.
- **Never hash line numbers or file offsets from buf.** They shift with unrelated edits.
- **Keep the mapping script in the repo, with the tool versions pinned.** That keeps fingerprints stable across runs.
- **Add a `surface` field (`graphql` or `grpc`) to every entry.** This is my addition, not in the skill's schema. Rule ids already differ between the two tools, so it's a readability and filtering aid. Hashing the surface into `path` is cheap insurance against collisions.

## 3. Entry ids

```
id = <api_version>/<first covered fingerprint or fragment id>
```

- **The version prefix is required.** Fingerprints carry no version, and one change can ship in several. The prefix keeps ids unique across a multi-version feed, so consumers can dedupe on `id` safely.
- **Dedupe on `id` only.** Never dedupe on name, path or summary.
- **One entry per contract change, grouped by API version.** Where one change touches a shared type, it's one entry with several fingerprints in `covers`. Identical wording on unrelated elements stays separate.
- **Never reuse or reissue an id.** To correct an entry, edit it in place and bump `updated`. Don't mint a new id.

Illustrative GraphQL entry. The hex values are placeholders, not real hashes:

```json
{
  "id": "2026-07-15/5d1e90c7a3b2",
  "api_version": "2026-07-15",
  "surface": "graphql",
  "date": "2026-07-15",
  "area": "Shipments",
  "operations": ["Query.shipment"],
  "kind": "removed",
  "classification": "breaking",
  "source": "diff:FIELD_REMOVED",
  "covers": ["5d1e90c7a3b2"],
  "summary": "Shipment.legacyTrackingCode is removed.",
  "tool_text": "<verbatim graphql-inspector message>",
  "action_required": "Read Shipment.tracking.code instead.",
  "sunset": "2026-07-15",
  "links": { "migration": "<url>", "approval": "ack-2026-0007" }
}
```

## 4. Baselines per version

The skill's rule is one baseline per job, and for date-versioned APIs you diff per version.

1. **Snapshot a contract per version.** Commit `specs/2026-01-15.graphql`, `specs/2026-04-15.graphql` and the proto equivalents. Generate them per version if one codebase serves all of them.
2. **The new version's entries** come from diffing its snapshot against its predecessor's. 2026-04-15 against 2026-01-15, then later 2026-07-15 against 2026-04-15.
3. **A frozen version's entries** come from diffing its snapshot against its own previous release tag. That diff should be empty. A diff in a frozen version is a defect, or a deliberate backport like the security fix.
4. **2026-01-15 has no baseline.** Publish its entries by hand and start diffing from it.
5. **Write nothing for 2026-07-15 yet.** It gets entries at its release.
6. **The PR gate uses a different baseline.** It diffs against the merge base, not the release tag.
7. **Run the diff once per tool per snapshot, then merge into one feed.**

Two buf points:

- **Category:** use `WIRE_JSON` at least if any client speaks JSON.
- **Blind spot:** buf can't see `google.api.http` changes. If you transcode gRPC to HTTP, diff the generated OpenAPI as well.

## 5. Security fix for 2026-01-15 and 2026-04-15

This is the declared-change channel. Whether it may reach pinned callers at all is decided by your versioning policy's exception path (`api-versioning-policy`), not by this pipeline.

1. **One fragment, all three versions.** Commit it with the fix:

   ```json
   {
     "id": "declared-2026-11-sec-tracking-authz",
     "api_versions": ["2026-01-15", "2026-04-15", "2026-07-15"],
     "area": "Shipments",
     "operations": ["Query.shipment", "ShipmentService.GetShipment"],
     "classification": "breaking",
     "kind": "changed",
     "summary": "<what callers observe, with no exploit detail>",
     "action_required": "<what callers must do, or 'none' with the reason>",
     "sunset": null,
     "links": { "migration": null }
   }
   ```

   Set `classification` honestly. If a compliant caller sees no change, it's `non-breaking`. If any caller's behavior changes, it's `breaking` or `potentially-breaking`.

2. **It produces three entries, one per version.** They are `2026-01-15/declared-2026-11-sec-tracking-authz`, `2026-04-15/…` and `2026-07-15/…`. Each has `covers` set to exactly the fragment id and `source` set to `declared:<id>`.

3. **Set `date` to the day the fix ships, not the version's release date.** In Atom, `<updated>` follows `date`, so readers surface it as new even though the version is old.

4. **A breaking fragment needs an acknowledgement row.**
   - `reason`: `security-exception`.
   - `covers`: the fragment id.
   - Also needed: approver, ticket, and a notice link.
   - Approval: put the spec, severity map and acks file under one code-owners rule, so the author can't self-approve.

5. **If the fix also changes a frozen snapshot, you get a second signal.** The diff will show it under that version. I'd keep one entry per version, not two. Cover both the fingerprint and the fragment id in one ack row, and use the fragment's narrative. This reconciliation is my judgment. The skill says declared breaks go through the same approval as diff-detected ones, but doesn't spell out the overlap.

6. **Handle disclosure.** The feed is public.
   - Write the summary and action text so they don't disclose the vulnerability before callers can patch.
   - Publish at the fix's release, not at merge.
   - Rerun the trace check after any rewording.

## 6. One feed, both surfaces

- **JSON:** `{feed_version, api, generated_at, entries[]}`. Newest version first, breaking first within a version. Consumers filter on `api_version`, `surface` and `classification`.
- **Atom:** one `<entry>` per feed entry.
  - `<id>` must be an IRI, so use a tag URI: `tag:driftwoodledger.example,2026:changes/2026-04-15/<fp>`. Substitute your real domain.
  - `<category>` carries the classification, the surface and the area.
  - `action_required` goes in the entry content, not only on the web page.
- **Human page:** one per version, with `Breaking changes` first.

## 7. Verify before publishing

Run the skill's two scripts. They need Python 3.8 or later and the standard library only. Both map graphql-inspector and buf output to the skill's fields first:

```
python3 scripts/build-entries.py --changelog changelog.json --api-version <v> \
  --date <ship-date> --fragments changes/ --acks acks.json --out entries.json \
  --ignore-out <ignore-file>
python3 scripts/check-entry-trace.py --diff changelog.json --entries entries.json \
  --fragments changes/ --api-version <v> --acks acks.json
```

Publish only on a pass. The trace check fails when an entry has no source, a break has no entry, a classification changed, or a breaking entry lacks full approval.

## Open questions

These change the design:

1. **Does gRPC have a date-pinning mechanism?** Is it a header, metadata or a per-account setting? If gRPC isn't actually pinned by date, per-version proto snapshots mean something different. Ask this first.
2. **Do GraphQL and gRPC share one version label?** I assumed yes.
3. **Is there a written breaking-change policy?** If not, mark every severity-map row `provisional`.
4. **Do you have usage data per field and per RPC?** It enables usage-aware classification (`considerUsage`), and it helps size how many pinned callers the security fix reaches.
5. **If you plan per-account version transformers, consider the version-derived changelog.** The skill's rung order promotes it for platforms that run date-based, per-account versioning. Entries are then written where the change is made, so they can't be omitted.