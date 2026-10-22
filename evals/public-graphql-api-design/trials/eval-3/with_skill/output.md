# Orrinbank partner access to the payments subgraph: do not sign off

**Verdict: ❌ No.** Giving a partner direct access to the payments subgraph is the critical finding in this skill's federation checklist. Neither the introspection switch nor the VPC reading changes that. Fix the latency by other means, which are listed below.

## 1. Why "introspection off" doesn't protect you

Federation needs two coordination fields on every subgraph, and neither can be turned off without breaking composition:

- **`Query._service { sdl }`** returns the subgraph's full schema. That is an introspection dump under another name, and the partner can call it with their API key.
- **`Query._entities`** resolves any `@key` entity directly from its key fields. It bypasses the access-control logic in your normal resolvers, and its resolver is auto-generated, so you can't lock it down selectively.

For a B2B payments graph, the second one matters most. Subgraphs usually take tenant scoping and authorization context from the router. A partner talking straight to payments skips that step. With a valid key and a guessable or leaked ID, they could ask `_entities` for payment records belonging to other tenants. Apollo's position (2026) is that subgraph isolation "is fundamental to Federation's security model."

The separate API key is a lock on a door that should not exist. It is also your only control on that path, because the router's depth, page-size and cost ceilings would not apply.

## 2. The `@key` tagging makes it worse

Tagging every new type with `@key` "for flexibility" turns every type into something `_entities` can resolve.

- The default should be plain value types. Promote a type to `@key` only when another subgraph truly needs to extend it.
- **Action:** audit the tagged types. Remove `@key` from any type that no other subgraph extends. Use `@inaccessible` to keep internal-only fields out of the public supergraph.

## 3. "Internal VPC" is a claim, not evidence

I haven't seen your config, so the following is inferred from your description.

- Your own summary has a contradiction. The subgraphs are on an internal VPC, but each has its own ingress. The partner's direct-access request only makes sense if that ingress is reachable from outside.
- If the partner can reach the subgraph, the VPC claim is wrong. If they can't, the request is really asking you to open a path.
- The skill's gate is empirical: probe every subgraph address from outside the private network and expect a connection failure, not a GraphQL response. Reading deployment config doesn't count.

## 4. What to do instead (the real problem is latency)

1. **Measure first.** Find out where the router time goes: query planning, subgraph fan-out, or an N+1 resolver. An un-batched relationship resolver is a must-fix finding. Overnight jobs often hit this.
2. **Fix the partner's query shape.**
   - Use cursor connections with `first` clamped to a documented maximum (for example 100).
   - Ask for fewer nested levels per query.
   - Offer optional persisted queries, so the partner registers their own hashes. That helps bandwidth and caching but is not a security control.
3. **Isolate the load, not the trust boundary.** Run a dedicated router instance or ingress for partner batch traffic, with its own scaling and rate limits. The router stays the only public component and the subgraphs stay private.
4. **Question the fit.** Overnight bulk reporting doesn't match any of GraphQL's three triggers: different client shapes, nested variable data, or high-latency clients. A REST or bulk-export endpoint, with cached cursor-paged files, may serve it better. Step 1 of the skill defaults to REST for this reason.
5. **Don't use an allowlist for this partner.** Allowlisting only works when you control both client and server. The partner is third-party, so protect them with the router's depth, page-size and alias ceilings. Document each ceiling and its exact error message.

## 5. Conditions for sign-off

I'd approve partner access when all of these hold:

- [ ] Partner traffic goes through a router, either the main one or a dedicated instance.
- [ ] An outside-network probe of all four subgraphs (accounts, payments, ledger, notifications) fails to connect. Record the result.
- [ ] `@key` is removed from types that no other subgraph extends.
- [ ] Router ceilings are set and documented: depth (low end, around 7), page size, aliases, and root fields per operation.
- [ ] Introspection is off for anonymous production callers and on only for authenticated tooling.
- [ ] N+1 resolvers on the partner's reporting queries are batched.

## 6. Open questions for you

- Can you actually reach any subgraph's ingress from outside the VPC right now? Please run the probe.
- Does payments rely on router-injected tenant context for authorization?
- Which part of the router's latency is the problem? A trace of the partner's slowest query would answer that.
- Is the partner's job really GraphQL-shaped, or a bulk export?

## Message for the staff engineer

"Turning off introspection and adding an API key don't close `_service` or `_entities`. The subgraph has to be unreachable from outside. Let's get the partner onto a dedicated router path and fix the query shape."

I read only `SKILL.md`. None of its reference files were needed for this answer.