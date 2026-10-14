# Brightfold first design review: where to start

**Start with the REST /v1 review. Don't write one consolidated checklist for all three surfaces.** The review skill I followed covers REST only. It tells reviewers to send GraphQL and gRPC surfaces to sibling skills because "their conventions differ enough that this checklist misleads." A REST checklist applied to a GraphQL schema would flag the wrong things, such as verbs in URIs and status codes. It would also miss the issues that matter there, such as nullability, depth limits and the federation boundary.

Consistency across the three surfaces does matter. It comes from one shared contract that each paradigm review checks against (see Order of work, step 2).

I have not seen your spec or your code. Everything below is plan and process, not findings.

## Order of work

1. **REST /v1 first.**
   - It is the only surface with a machine-readable spec, and it is probably the one clients depend on.
   - Run a spec linter first (Spectral, or Zally for Zalando's ruleset). Linters own the mechanical findings and the human review owns the semantic ones.
   - Then walk all 8 dimensions in order:
     1. Resource modeling and URI naming
     2. HTTP method semantics
     3. Status-code correctness
     4. Field-naming consistency
     5. Pagination
     6. Filtering, sorting and field selection
     7. Error shape consistency
     8. Backward compatibility
   - Add the five one-line checks for versioning, idempotency, auth, rate limits and docs coverage.
   - Pull 5–10 real production responses as well as the spec. A spec can claim a consistency that production traffic doesn't have.
2. **Write a shared cross-surface contract (about one page) before reviewing the other two surfaces.** The three reviews check against it, so consistency is a rule you can cite. It fixes:
   - one ID strategy, so a GraphQL `Node` ID, a REST `{id}` and a proto resource name refer to the same object
   - one name per concept, and one casing rule per surface (REST and JSON can differ from proto; the same concept must keep the same name)
   - one error taxonomy, with its mapping to REST problem details (RFC 9457), GraphQL result types and `google.rpc.Status`
   - one auth model
   - one versioning story
   - the pagination mapping (REST cursor ↔ Relay connections ↔ AIP page tokens)
   
   Without a written rule, a cross-surface finding is only an Improvement. The Must-change bucket needs a cited rule or precedent.
3. **GraphQL gateway: run the "GraphQL or not" gate before reviewing the schema.**
   - The GraphQL sibling skill defaults a public API to REST, and it asks teams to re-ask the question even if they are already committed. Six weeks of work is a reason to ask it, not a reason to skip it.
   - Gate question: do multiple client types need different shapes of the same data?
   - If the gate passes, review the schema against the GraphQL design skill. Its steps cover naming and nullability, Relay pagination, typed errors, depth and complexity limits, the federation trust boundary and persisted queries.
   - Review at design time, on the SDL and a few real queries. Six weeks in, a late review risks "start over" feedback.
4. **gRPC: do two things now and one later.**
   - Now: check the transcoding architecture and the exposure audit. Internal protos usually carry admin and debug RPCs nobody designed for partners.
   - Now: set up a `buf` breaking-change gate. Its blind spot is the `google.api.http` annotations, because changing a transcoded route is a breaking change that `buf` may miss.
   - Later: review the transcoded REST-shaped surface (the `google.api.http` mappings) with the REST checklist, once it exists.
   - Partners "eventually" means this is not a blocking review yet. Treat it as an advisory design pass.

## Severity by surface

The review's severity depends on who consumes the surface and what stage it is at. The review skill uses the same split.

| Surface | Likely posture | Condition |
|---|---|---|
| REST /v1 | Full blocking checklist if external and beta or GA | Depends on answers 1 and 4 below |
| GraphQL gateway | Advisory for an internal alpha; blocking at beta | Depends on answers 4 and 5 below |
| gRPC (internal) | Advisory only | Becomes a REST-style review once the gateway exists |

## Rules for the findings

- **Must-change** needs a cited rule. Use your own guidelines, or the review skill's checklist if you have none (the report must say so).
- **Improvement** is anything without a cited rule. Taste never blocks.
- **A team may deviate** from a cited rule by recording a rationale. The deviation becomes precedent, and the next review cites it instead of re-litigating.
- **Shipped REST behavior**: a Must-change against something clients already observe is a breaking change. Route it through your versioning and deprecation policy; don't ask for a silent in-place fix.
- **Ship gate**: zero open Must-change items at beta or GA, or a documented deviation for each.

## Questions to answer before the review starts

1. Is /v1 already in production, or still a proposal? A shipped surface makes every fix a Hyrum's-Law question.
2. Is the OpenAPI 3.1 file current with production? Can you send 5–10 real responses across endpoints?
3. Is this a one-off audit, or do you also want a standing review program? If a program: how many teams ship APIs, by when must it run, and how much effort can you spend on it?
4. Who consumes each surface (internal only, named partners, or anyone), and what stage is each at (alpha, beta, GA)?
5. Which rule corpus do you follow: your own guidelines, Zalando, Microsoft, Google AIPs, JSON:API, or none?
6. Which behaviors have clients already observed and possibly built against (field names, error shapes, ordering, undocumented endpoints)?
7. GraphQL: can I see the SDL, 5–10 real queries, and whether federation is in place? Which client types is it for?
8. gRPC: can I see the proto layout? Which gateway is planned (Envoy, grpc-gateway or Connect-RPC), and do browsers need to call it directly?

## Standing program (only if you answer "yes" to question 3)

The default shape is a **linter plus two named reviewers**. It is the shape Zalando documents, and it takes days to set up from a forked public corpus. Triggers are keyed to audience and lifecycle stage, not to the calendar. Publish the escalation path and a named override authority up front.

Move up to a federated reviewer pool only when a third team ships its own API surface or median review turnaround passes about 2 weeks. If one or two teams own all three surfaces, the federated pool is the wrong option, because there are no separate domains to put reviewers in. If you have a near-term deadline or a tight effort limit, drop to a linter-only CI gate and keep the semantic conversation in ordinary code review.

## Next step

Send me the OpenAPI file, 5–10 real responses, the GraphQL SDL with some real queries, and the proto layout, plus your answers to the questions above. I'll run the REST review first and deliver it in the standard report: scope header, pass/fail per dimension, findings table (finding, dimension, bucket, cited rule, fix), then accepted deviations.