# Blind spots and the declared-change channel

## What a structural diff cannot see

| Change | Diff sees it? | Cover it with |
| --- | --- | --- |
| Behavior change with the same schema | No | Declared fragment; contract test on the behavior |
| Default value change | Only if `default` is declared in the spec | Declare defaults in the spec; fragment for server-side fallbacks |
| Validation tightening | Only if declared (`pattern`, `maximum`, `maxLength`, `required`) | Mirror server validation into the spec; fragment otherwise |
| New error status code | Yes if documented | Document every status; fragment for changed error-body meaning |
| Error code or message meaning | No | Fragment; treat machine-readable error codes as contract |
| Rate limits, quotas | No | Fragment; link the rate-limit page |
| Pagination, ordering, page size | No | Fragment; contract test on ordering when callers rely on it |
| Auth requirement changed | In the spec, yes; oasdiff rates removed scopes and added alternative requirements INFO | Severity-map rows per the policy; fragment for gateway-only rules the spec never declares |
| `operationId` or schema rename | Not on the wire; yes for generated SDKs | Severity map row; SDK release notes for generator-caused breaks |
| Spec drift from the running service | No | Drift alarm against the served spec or live traffic |
| Transcoding annotations (gRPC → HTTP) | No under `buf breaking` | Diff the generated OpenAPI too |

Declared enums, nullability and `readOnly`/`writeOnly` are seen, but their direction decides the verdict: what the server sends follows response rules, what the client sends follows request rules.

## PR template block

```
### API contract
- [ ] No change to the published API
- [ ] Spec changed (the contract diff will classify it)
- [ ] Behavior changed without a spec change: defaults, validation, error codes or bodies,
      auth, rate limits, pagination, ordering, timing -> add a change fragment
```

The third box is the only route by which a behavior change reaches the changelog. Reviewers ask for a fragment when the diff touches handlers but not the spec.

## Change fragment format

One JSON file per change in the fragments directory, committed with the code, named after the PR or ticket.

```json
{
  "id": "declared-2026-0412-invoice-list-order",
  "api_versions": ["2026-05-01"],
  "area": "Billing",
  "operations": ["GET /v1/invoices"],
  "classification": "breaking",
  "kind": "changed",
  "summary": "Invoices are now returned newest first instead of oldest first.",
  "action_required": "Pass sort=created_asc to keep the previous order.",
  "sunset": null,
  "links": { "migration": null }
}
```

- `id`: the entry's `source` becomes `declared:<id>`; keep it unique across the repository.
- `api_versions`: every version whose callers see the change; omit only for unversioned APIs. More than the newest version on a date-versioned API means the change reaches pinned callers: the versioning policy's exception path decides.
- `classification`: exactly `breaking`, `potentially-breaking` or `non-breaking`; both scripts reject anything else. A breaking fragment needs an acknowledgement row whose `covers` lists this `id`.
- `kind`: exactly `added`, `changed`, `deprecated` or `removed`.

## Triage rule for "potentially breaking"

`warn` findings and unclassified items stay visible as `potentially-breaking` in the entry. Resolve one by:

- adding a severity-map row with the policy line that decides it, or
- an acknowledgement row whose `rationale` explains why it cannot break callers; the entry stays published as potentially breaking, with that rationale as its action text.

Never resolve it by deleting the entry.
