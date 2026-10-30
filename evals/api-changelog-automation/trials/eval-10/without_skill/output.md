Don't key on the element name. Mint an opaque id once per logical change, store it in a committed registry, and use the diff tools only to detect changes and look those ids up.

## Why name-keying fails

1. One element has many events. `Invoice.status` is added in 2026-04-15, deprecated in 2026-07-15, and removed later. Dedupe on the name collapses three entries into one.
2. A rename looks like a remove plus an add, so the name-keyed ids don't link.
3. Names collide across APIs. GraphQL `Invoice` and proto `ledger.v1.Invoice` are different elements.
4. A GraphQL argument and a proto field number are separate coordinates. Without them you can't tell a field change from a type change.
5. The security fix has no schema diff in the older versions. A patch to 2026-01-15 changes behavior, not the schema, so graphql-inspector and buf emit nothing for it.
6. buf breaking reports only breaking changes, so additive proto changes never show up. The proto side of the feed would be thinner than the GraphQL side unless you add your own diff for additions.

## Entry model

One entry per (logical change, version it applies to).

Fields:

- `change_id`: opaque and permanent. It groups the same change across versions.
  - Use the CVE or GHSA id for security fixes.
  - Otherwise mint `chg_` plus a ULID.
- `id`: `change_id@version`, for example `chg_01J…@2026-04-15`. This is the feed entry id and the dedupe key.
- `api`: `graphql` or `grpc`. A change spanning both gets one `change_id` and two entries.
- `version`: the date version the entry applies to.
- `kind`: `added`, `deprecated`, `removed`, `changed`, `behavior`, or `security`.
- `severity`: `breaking`, `dangerous`, or `safe`. Map graphql-inspector's criticality and buf's rule categories into this field.
- `coordinates[]`: for example `Invoice.status` or `Query.invoices(first)` for GraphQL, and `ledger.v1.Invoice.status#4` (field number included) for proto. These are metadata for display and search, not identity.
- `title`, `body`, `published_at`, `supersedes`, `migration_url`.

## Identity and dedupe

1. Compute a fingerprint for each tool finding: `sha256(api | normalized kind | coordinate | from_version | to_version)`.
2. Do not hash the message text, line numbers, or file paths. buf messages and positions shift without a real change.
3. Keep `feed/registry.yaml` in the repo, mapping each fingerprint to a `change_id`.
4. In CI, a known fingerprint reuses its `change_id`. An unknown fingerprint mints a new one and opens a PR to add it to the registry. A human reviews the title and body before anything publishes.
5. Handle renames by hand. Give the new entry `supersedes: <old change_id>`. Never recompute old ids.
6. Never change an id after publishing. You may edit content and bump `updated`.

## Feed formats

Generate both from the same entries.

- JSON Feed: `id` is the entry id. Add custom fields under an `_driftwood` extension: `change_id`, `api`, `version`, `kind`, `severity`, `coordinates`.
- Atom: `<id>` is the same value as a tag URI, `tag:driftwoodledger.com,2026:change/chg_01J…@2026-04-15`. Add `<category scheme="…/api" term="graphql"/>` and a matching category for the version.
- Per-version feeds, for example `/changes/2026-01-15.json`, are filtered views of the same entries. Pinned callers subscribe to their own version.

## Security fix to the two older versions

1. Treat it as one `change_id` with three entries: `@2026-01-15`, `@2026-04-15`, and `@2026-07-15`. The `@2026-07-15` entry exists if the fix lands in the next version too.
2. Author the entries by hand with `kind: security`. The tools can't see them. A registry entry with no fingerprint is fine.
3. Publish each version's entry when that version's fix ships, not before. Do not publish early, since early publication discloses the vulnerability.
4. Each backport entry gets its own `published_at`. Atom readers then see the fix as new for each pinned version.
5. Set `affected_versions` and `fixed_in` as a per-version patch marker, for example `2026-01-15.1`, alongside the date.
6. Treat dated versions as frozen apart from security patches. Say so in the feed docs, so pinned callers know the feed will carry these entries.
7. Link a `migration_url` only if the fix changes behavior.

## Example (JSON Feed item)

```json
{
  "id": "chg_01JABC…@2026-04-15",
  "url": "https://driftwoodledger.com/changes/chg_01JABC…#2026-04-15",
  "title": "Security fix: invoice export authorization",
  "date_published": "2026-11-20T09:00:00Z",
  "_driftwood": {
    "change_id": "GHSA-xxxx-xxxx-xxxx",
    "api": ["graphql", "grpc"],
    "version": "2026-04-15",
    "kind": "security",
    "severity": "dangerous",
    "fixed_in": "2026-04-15.1"
  }
}
```

## Effort

About 1 day for the registry, the fingerprint script, and the two serializers. Add about half a day for the proto additive-change diff. The security entries need no extra code.

## Next action

Decide whether the security `change_id` is a CVE or GHSA id or one you mint. Then I can draft the registry schema and the fingerprint script.