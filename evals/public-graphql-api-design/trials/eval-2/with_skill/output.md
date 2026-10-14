# Policy doc: persisted operations and abuse ceilings on the public GraphQL endpoint

I followed the `public-graphql-api-design` skill (steps 5 and 7 plus the audience split). I did not need the reference files for this question.

## Bottom line

Accept half of the mandate and reject the other half.

1. **Accept: closed allowlist for first-party traffic** (your iOS and Android apps). You know every operation at build time, so this is the strongest control you can run.
2. **Reject: allowlist for third-party traffic.** About 900 integrators write queries you have never seen and can't pre-approve. A blanket "no raw queries, no exceptions" rule rejects every legitimate integrator query on day one. graphql.org says trusted documents "can't be used for public APIs because the operations sent by third-party clients won't be known in advance."
3. **Reject: retiring the depth limit and complexity budget.** An allowlisted query is not a safe query. The ceilings stay mandatory on every traffic class.

If Security can't accept the third-party carve-out, the honest alternative is to move integrators to a fixed REST surface (step 1 of the skill). That surface is the "known operations" model Security wants, and it also gets URL-keyed CDN caching. Offer that as the choice. Don't write a policy that breaks the integrators.

## What goes in the doc

### 1. Purpose and scope
- State the incident in one line. If it can be shared, say what it exploited (open question 1 below).
- Name the two traffic classes: first-party apps and third-party integrators.
- Say the endpoint is one logical API with two policies, not one policy.

### 2. Traffic classification
- Define which credential or client identity is first-party. Use signed app credentials or attestation, never a client-supplied header alone.
- Spoofing the first-party label can only move an attacker into the stricter allowlist. It must never unlock the generous first-party budgets.
- Options: a separate first-party endpoint, or routing at the router by credential class. A separate endpoint is simpler to audit.

### 3. First-party policy: closed allowlist
- Extract every operation from the iOS and Android codebases at build time.
- Register the hashes in CI before the app release ships.
- Execute only registered hashes and reject raw query strings, with a documented error code.
- Retain hashes for every app version still in the field. Old mobile builds live for months, so define a minimum supported version and a hash-retention window.
- Review at registration time, and run the static cost check there as well, so a new operation can't land over budget.
- Name the owner of the registry and the emergency path for a hotfix operation.

### 4. Third-party policy: raw queries under ceilings
- Raw queries are allowed for authenticated integrators only.
- Anonymous production callers get no introspection. Integrators with credentials do.
- Protection comes from the ceilings in section 5, per-integrator credentials, and cost-based rate limiting (owned by the rate-limit policy).
- Optional persisted queries are allowed: an integrator registers its own hashes for bandwidth and CDN cacheability. Label this a performance feature, not a security control.

### 5. Ceilings, which apply to all classes
Each ceiling needs a value, an enforcement point, and the exact error a violating query receives. Publish all of them. An undocumented ceiling is discovered through production failures, and for an integrator that is the worst possible onboarding.

| Ceiling | Public (third-party) default |
|---|---|
| Depth | Low end: 5-7 levels. Each raise needs a written justification. |
| Page size | `first` clamped to a documented maximum, for example 100. |
| Aliases, root fields, batched operations per request | Capped. |
| Per-operation cost | Static admission control before execution. Mutations weighted about 10x reads. |

- First-party budgets may be more generous, tied to the credential, but they are not removed.
- Reject over-ceiling queries at parse or analysis time, before any resolver runs.

### 6. Why the ceilings stay (the rebuttal to Security's argument)
Put this in the doc so the argument isn't re-litigated next quarter.

- **Allowlisting is defense-in-depth, never a complete answer.** Apollo Router CVE-2025-32032 exhausted the query planner with recursive fragments before any per-operation guardrail applied. Allowlist bypass is itself a recurring vulnerability class. If the allowlist fails, the ceilings are the only thing left.
- **A reviewed document is not a bounded cost.** Cost depends on variables, not just document text. The same registered operation with `first: 100` on nested connections costs far more than with `first: 5`. Page-size caps and cost checks bound what review can't.
- **Third-party traffic never gets the allowlist,** so removing the ceilings would leave the 900 integrators with no protection at all.
- **N+1 resolvers and planner exhaustion are server-side defects.** An allowlist doesn't fix them. Batching loaders are a must-fix review item.

### 7. Federation boundary (if federated)
- Only the router is publicly reachable.
- Subgraphs expose `_service { sdl }` and `_entities`, which leak schema and bypass access control. Disabling introspection doesn't close that.
- Verify by probing every subgraph address from outside the private network. Expect a connection failure, not a GraphQL response.

### 8. Uniform null-versus-error behavior
An unauthorized field must behave identically whether or not the resource exists. Otherwise the response shape becomes an existence oracle.

### 9. Exceptions and change control
- The ceiling and allowlist policies change only through a written decision record.
- Do not accept "no exceptions" as a policy statement. Name the one deliberate carve-out (third-party raw queries) and its compensating controls.
- Record who may raise a ceiling and the review required.

### 10. Verification gates (binary)
- Every first-party operation is registered, and a raw string on a first-party credential is rejected with the documented error.
- Every operation type has a documented depth and page-size ceiling, and a violating query is rejected before execution.
- Zero subgraph endpoints are reachable from outside, verified by probing.
- Post-launch, track guardrail rejections per week and which ceilings integrators actually hit. This is for tuning, not a gate.

### 11. Rollout
1. Register all first-party hashes and run in report-only mode.
2. Enforce the allowlist on first-party credentials only.
3. Announce the third-party ceilings and error codes in the public docs before enforcing any tighter value.
4. Set a minimum app version and a deprecation date for builds that predate hash registration.

## Open questions for you

1. What did the incident exploit? Raw-string injection, an expensive query, or an unauthenticated caller each point to a different control.
2. Can first-party and third-party credentials be cleanly separated today?
3. Is the schema federated?
4. Do you already have a REST surface? That determines whether the REST fallback in the bottom line is real.
5. What is your oldest app version still in use? That sets the hash-retention window.

I can draft this as the actual document once you answer 1 and 2.