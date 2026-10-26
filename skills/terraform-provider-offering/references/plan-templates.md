# Planning templates

Load before step 1. Fill these instead of describing them in prose; every empty cell is an open question to put back to the user.

## Contents

- Gate matrix
- Resource map
- Community-provider audit
- First-release plan

## Gate matrix

One column per API object, one row per check from step 2. Cell = `PASS`, `FAIL`, `UNKNOWN`, or `COMP` (provider-side compensation accepted). A resource ships only when its column holds no `FAIL` or `UNKNOWN`.

```
| Check                              | <object A> | <object B> | Owner | Due    |
| ---------------------------------- | ---------- | ---------- | ----- | ------ |
| Stable server-assigned ID          | PASS       | PASS       |       |        |
| GET returns writable fields        | COMP       | PASS       |       |        |
| In-place update                    | PASS       | FAIL       | API   | wk 4   |
| Idempotent create                  | UNKNOWN    | PASS       | API   | wk 2   |
| Bounded propagation (seconds)      | PASS (20s) | PASS       |       |        |
| Pollable async op, ID in 202 body  | n/a        | FAIL       | API   | wk 3   |
| Deterministic normalization/order  | COMP (set) | PASS       |       |        |
| Secrets identified                 | PASS       | PASS       |       |        |
| Documented rate limits             | UNKNOWN    | UNKNOWN    | API   | wk 1   |
```

Cut rule: an object whose `FAIL` is not fixed by the release cut moves to the next minor; never ship it with a known perpetual diff.

## Resource map

```
| API object | Construct | Type name | ID / import grammar | Mutable fields | Replace-only fields | Preserved fields (never returned) | Secrets (kind) | Collections (list/set) | Consistency class | Timeouts |
```

- Construct: resource, data source (singular/plural), ephemeral resource, list resource, action, or "left out" with the reason.
- Secrets kind: user-supplied input, API-generated once, short-lived token (see step 4).
- Collections: `list` only when the API keeps and means an order; otherwise `set`. This cannot change later without a major.
- Preserved fields: the `ImportStateVerifyIgnore` list for that resource comes from this column plus API-generated secrets, never from guesswork.
- Consistency class: none, not-yet-visible, temporarily-refused, async (see `references/resource-design-rules.md`).

## Community-provider audit

Run before choosing transfer-adopt, fork-adopt or a rewrite. Each "no" lowers the case for adopting.

1. The repo carries an OSI license file; without one it cannot be forked.
2. Attribute names follow the API's field names; no invented vocabulary you would want to rename.
3. Collections use sets where the API is unordered.
4. Import works for every resource, with a documented ID grammar.
5. Acceptance tests exist and pass against a sandbox.
6. Open issues: count those reporting a perpetual diff, "inconsistent result after apply" or 404 after create; a high share means schema or consistency rework.
7. Schema versions released so far, and whether state upgraders exist for them (you will owe them).
8. Plugin SDK in use. SDKv2 blocks the Partner badge until the resources migrate to the Plugin Framework; schedule it when Partner is a target.
9. Maintainer contact attempted, with a dated time box for a reply.

Decision: transfer-adopt when 1-5 mostly pass and the maintainer cooperates; fork-adopt when they pass and the maintainer stays silent past the time box; rewrite on the vendor-owned path when 2-4 fail, and publish a migration guide from the community address.

## First-release plan

```
Week  Track A (provider)                        Track B (API and release)                 Decision point
1     audit community provider, fill gate        API asks filed for every FAIL row          D1: path chosen (step 1)
      matrix and resource map
2     scaffold, provider config, first resource  signing key, GoReleaser, both registries
                                                 rehearsed with a snapshot build
3-4   remaining core resources, data sources     sandbox account, sweepers, nightly CI      D2: cut list - objects still FAIL move out
5     upgrade tests (from community address      docs generated, upgrade guide drafted
      if adopting), import config generation
6     prerelease tag, early-customer trial       OpenTofu provider and key submitted        D3: go / slip
7-8   fixes from trial                           1.0.0 or 0.x tag, announcement
```

- Pick `0.x` for the first release when the resource map is still moving; promise compatibility from `1.0.0`.
- Cut order when time runs out: actions and functions first, then list resources, then the least-used data sources. Never cut import support or upgrade tests.
