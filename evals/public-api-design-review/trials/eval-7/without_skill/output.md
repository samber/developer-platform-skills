# Where to start: design review for REST, GraphQL and gRPC

**Recommendation:** don't run one consolidated review. Run one shared contract plus three separate reviews, in this order: GraphQL, then gRPC, then REST.

## Why not one review

The three surfaces are at different stages, so the same finding costs different amounts to fix.

| Surface | State | Cost to change | What the review does |
|---|---|---|---|
| GraphQL gateway | 6 weeks old, probably unreleased | Low, but rising weekly | Shape the design |
| gRPC via transcoding | Internal today, partner-facing later | Low now, high once partners integrate | Decide what becomes public |
| REST /v1 | Shipped, 28 endpoints | High (breaking changes) | Audit, then triage |

A single review would spend its time on REST nits that can't be fixed without a v2. Meanwhile the GraphQL schema would keep hardening.

Consistency still matters. You get it from a short shared contract, not from one meeting.

## Step 1: write a one-page shared contract (about 2 days, before any review)

Settle these once. Each protocol then implements them in its own idiom.

1. **Canonical resource and domain names.** Does an "account" in REST match the GraphQL `Account` type and the proto `Account` message? Keep a single glossary.
2. **IDs.** Format, opacity and stability. GraphQL global IDs are the usual trap.
3. **Timestamps, enums and money.** RFC 3339 UTC, enum unknown-value handling, and amount/currency representation.
4. **Error model.** One logical error taxonomy with stable machine codes. Map it explicitly: HTTP status and problem+json, gRPC status and `google.rpc.ErrorInfo`, and GraphQL `extensions.code`.
5. **Pagination.** Cursor-based everywhere. GraphQL Relay connections and REST cursors should wrap the same underlying token.
6. **Auth and authorization.** Where authz is enforced, and whether the gateways trust or re-check it. This is the highest-risk item for the GraphQL gateway.
7. **Idempotency, rate limits and partial failure.**
8. **Versioning and deprecation policy.** Deprecation windows, sunset headers, GraphQL `@deprecated`, and proto `reserved` and field-number rules.

Do not force REST conventions onto GraphQL or gRPC. Identical wire shapes would make the GraphQL gateway worse. Align semantics and names instead.

## Step 2: GraphQL gateway review (first, highest leverage)

Questions to answer before reading schema:
- Who are the consumers: first-party frontends, partners, or both?
- Does it wrap REST, call the gRPC services directly, or both? A GraphQL layer over REST inherits all of REST's inconsistencies.
- Is it a single schema or federated? Who owns schema changes?

Review checklist:
- **Schema design:** nullability defaults, Relay connections, mutation input/payload types, no leaking of internal or DB shapes, and enums that can evolve.
- **Errors:** typed errors in payloads for expected failures, and `extensions.code` aligned to the shared taxonomy.
- **Performance and abuse:** N+1 queries (dataloaders), depth and complexity limits, persisted queries, timeouts, and introspection policy.
- **Authz:** field-level and object-level checks, and how identity propagates downstream.
- **Evolution:** the deprecation process, and a schema linter and breaking-change check in CI.

## Step 3: gRPC review, scoped to the partner-reachable surface

Don't review every internal service. First list which services and RPCs partners will reach through the transcoder. That list is the review scope.

For each in-scope RPC, check:
- **Transcoding annotations:** `google.api.http` mappings, URL and verb choices, and body/field mapping. These become your public REST surface and must be consistent with /v1.
- **Proto hygiene:** naming per the Google API design guide, field-number stability, `reserved`, and wrapper and `optional` presence semantics. A field that is unset and a field set to its zero value look different through transcoding.
- **Error mapping:** gRPC code to HTTP status, and error details exposed to partners. Internal details must not leak.
- **Internal types leaking out:** internal-only fields, enums and error strings that would become a partner contract by accident.
- **Streaming:** transcoding handles it poorly, so decide explicitly which RPCs are exposed.
- **Pagination, field masks and long-running operations** (AIP-style).

The decision this review produces is a boundary. Either partner-facing protos get a separate public API package, or the internal protos are promoted to a public contract. Make that call before the first partner integrates.

## Step 4: REST /v1 audit (last, as triage)

The OpenAPI 3.1 file in the repo makes this mostly mechanical:

1. Run a linter (Spectral or Redocly) with a ruleset that encodes the shared contract. This gives an objective inconsistency list.
2. Compare the findings against the shared contract and sort each into three buckets:
   - **Non-breaking fix:** add a field, document, or add an error code.
   - **Fix in v2:** collect these in a v2 backlog.
   - **Accept:** record the decision and the reason.
3. Prioritize by partner usage, using traffic data per endpoint. Don't polish endpoints nobody calls.

Do not break /v1 to match the new surfaces. Where the new surfaces deviate from /v1 on purpose, document it.

## Suggested sequence

| When | What | Output |
|---|---|---|
| Days 1-2 | Pre-work: inventory, consumers, shared contract draft | 1-page contract, scope list |
| Week 1 | Review session 1: ratify the shared contract (about 60 min) | Signed-off contract |
| Week 1 | Review session 2: GraphQL | Findings, with blockers marked before launch |
| Week 2 | Review session 3: gRPC partner-facing subset | Findings, boundary decision |
| Week 2-3 | Review session 4: REST audit readout | Triage list, v2 backlog |
| After | Wrap-up: CI lint gates for all three | Enforced contract |

## Process rules for a first review

- **Findings need severity:** blocker (fix before release), should-fix, or note. A first review that returns 80 undifferentiated comments gets ignored.
- **Name an owner per surface and one tie-breaker** for cross-surface disputes, so the shared contract isn't relitigated each session.
- **Send written material 2 days ahead:** the schema, the proto list and the OpenAPI lint report. Use the meeting for decisions only.
- **Record decisions** as short ADRs. A written decision beats a repeated debate.
- **Automate afterward.** Spectral for OpenAPI, a GraphQL schema linter and breaking-change check, and `buf lint` plus `buf breaking` for proto. Once the review settles the rules, CI should enforce them.

## Questions that change this plan

1. Is the GraphQL gateway launching to partners, or only to your own clients? If partners, authz and complexity limits become blockers.
2. Does GraphQL sit on top of REST or on top of the gRPC services?
3. Do you have per-endpoint traffic data for /v1?
4. Is there a committed date for partner access to gRPC? It sets how urgent the boundary decision is.

If you answer those, I can draft the shared contract page and the Spectral ruleset as the first concrete artifacts. Doing so would **write files to the repo**, so tell me where you want them.