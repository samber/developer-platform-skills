# Entry schema, feed shapes and examples

Contents:

- [Entry schema](#entry-schema)
- [Acknowledgement record](#acknowledgement-record)
- [JSON feed](#json-feed)
- [Atom feed](#atom-feed)
- [Human page per version](#human-page-per-version)
- [Good and bad entries](#good-and-bad-entries)
- [Rewriting with a model](#rewriting-with-a-model)

## Entry schema

```json
{
  "id": "2026-05-01/a3f8c21b9d04",
  "api_version": "2026-05-01",
  "date": "2026-05-01",
  "area": "Billing",
  "operations": ["GET /v1/invoices/{id}", "GET /v1/quotes/{id}"],
  "shared_schema": "Money",
  "kind": "removed",
  "classification": "breaking",
  "source": "diff:response-required-property-removed",
  "covers": ["a3f8c21b9d04", "77c0e1a9b2d4"],
  "summary": "Amounts no longer carry `legacy_total`.",
  "tool_text": "removed the required property `total/legacy_total` from the response with the `200` status",
  "action_required": "Read `total.amount` instead; it carries the same value in minor units.",
  "sunset": null,
  "links": {
    "migration": "https://docs.example.com/upgrade/2026-05-01#money",
    "approval": "ack-2026-0398"
  }
}
```

- `links.approval`: one acknowledgement id, or a list when several rows together cover every fingerprint in `covers`.
- `id`: `<api_version>/<first covered fingerprint or fragment id>`. Fingerprints carry no version, and one change can ship in several versions; the version prefix keeps ids unique across a multi-version feed, so readers deduplicate safely.
- `covers`: every finding fingerprint (or, for a declared entry, exactly its fragment id) the entry stands for. A change oasdiff reports for one shared schema (`sharedSchema` in its JSON) is one entry with several fingerprints; identical text on unrelated operations stays separate entries, merged only in the human page's wording.
- `classification`: `breaking`, `potentially-breaking` (tool `warn`, unclassified, or declared as uncertain), `non-breaking`. Must equal the classification of every source it covers.
- `source`: `diff:<check-id>` or `declared:<fragment-id>`.
- `tool_text`: the tool's own sentence, kept verbatim beside the human `summary`.
- `action_required`: empty only for `non-breaking` entries.

## Acknowledgement record

```json
{
  "id": "ack-2026-0398",
  "covers": ["a3f8c21b9d04", "77c0e1a9b2d4"],
  "check": "response-required-property-removed",
  "operation": "GET",
  "path": "/v1/invoices/{id}",
  "text": "removed the required property `total/legacy_total` from the response with the `200` status",
  "reason": "intended-break-new-version",
  "approver": "api-review",
  "date": "2026-04-22",
  "ticket": "API-1187",
  "notice": "https://docs.example.com/changelog/2026-05-01",
  "behaving_since": null,
  "rationale": null
}
```

- `covers`: fingerprints and fragment ids. A PR-time fingerprint can differ from the release-time one for the same change; `build-entries.py` re-matches on `check` + `operation` + `path` + exact `text`, only when one finding has that location, and asks for the release fingerprint to be added.
- `text`: the tool's sentence (`-f singleline` or JSON `text`). `build-entries.py --acks acks.json --ignore-out <file>` turns `operation`, `path` and `text` into the tool's ignore line; run it in the PR job before the gate, so the ignore file is never edited by hand.
- `reason`: `intended-break-new-version`, `spec-correction`, `security-exception`, or `historic` for rows created by auditing an old hand-edited ignore file (approver `unknown - audited <date>`).
- `behaving_since`: required for `spec-correction`; the date the live service started behaving as the corrected spec says.
- `rationale`: required when the row resolves a `potentially-breaking` finding as harmless; say why it cannot break callers.

## JSON feed

An object with `feed_version`, `api`, `generated_at` and `entries` (newest version first, breaking first within a version), published at a stable URL per audience (public, partner). A consumer polling it filters on `api_version` and `classification` without parsing prose.

## Atom feed

- One `<entry>` per changelog entry.
- `<id>` must be an IRI (RFC 4287): use a tag URI built from the entry id, e.g. `tag:example.com,2026:payments/2026-05-01/a3f8c21b9d04`.
- `<updated>` = date; `<category term="breaking"/>` plus one category per area.
- Put `action_required` in the content, not only on the web page: feed readers and chat integrations drop links readers never follow.

## Human page per version

One page per version: `### Breaking changes`, then `### Potentially breaking`, then additions and deprecations; each line names the area, the operations, what callers observe and the action, with the upgrade-guide link. Prose polish is for `samber/developer-relations-skills@changelog-writing`; this structure is what it receives.

## Good and bad entries

```
// ✓ Good - names the operations, what callers observe, the action, and the version
Billing - GET /v1/invoices/{id}, GET /v1/quotes/{id} (2026-05-01): `legacy_total` is no longer returned. Read `total.amount`.

// ✗ Bad - raw tool text per property and per operation, no grouping, no action
removed the required property `total/legacy_total` from the response with the `200` status
removed the required property `total/legacy_total` from the response with the `200` status

// ✓ Good - declared behavior change the diff could never show
Billing - GET /v1/invoices (2026-05-01): results now sorted newest first. Pass sort=created_asc for the old order.
```

## Rewriting with a model

Allowed: shorten, reorder, merge entries that share a schema, translate tool text into plain words.

Rejected, by rerunning the trace check and a reviewer reading the source next to the sentence:

- any path, field, parameter, status code or enum value absent from the entry's source;
- any consequence ("faster", "more secure", "no action needed") the source does not state;
- changing the classification or dropping `action_required` (the trace check fails both).
