# Partner Subgraph Guide: outline review and draft

## Part A. Four changes to your outline

Your outline has two internal conflicts and two risks. I changed the draft below to fix them. The Apollo-specific claims come from my own knowledge of GraphOS and Apollo Federation, which I haven't verified against current docs. Have your platform lead confirm items 2 and 4 before you send the guide.

1. **Composite Schemas and GraphOS don't compose together.**
   - Your steps (2) and (3) use `rover subgraph publish` and GraphOS composition. That pipeline composes **Apollo Federation 2** subgraphs, which use `@key`, `@requires`, `@external` and `@shareable`.
   - The GraphQL Composite Schemas spec is a separate, still-evolving working-group spec. It uses `@lookup`, `@is` and `@require`, and GraphOS won't compose it.
   - A partner who follows step (1) would fail composition at step (3).
   - The draft tells partners to write Federation 2. It says only that the concepts map to the newer spec, and it makes no future-proofing promise.
   - If you want the Composite Schemas spec, you need a different composition stack. That is a bigger decision than a guide.

2. **A GraphOS API key per partner is the riskiest part.**
   - As far as I know, a graph API key is scoped to the graph, not to a subgraph name. A partner holding a production-graph key could publish or overwrite any subgraph, including yours, and change a routing URL to point your router at their server.
   - The draft gives each partner a key to a **separate sandbox graph**. You run the production publish from your own CI after review.
   - If Apollo offers narrower per-subgraph scoping on your plan, that would let you relax this.

3. **"Use any federation directive you need" lets a partner take over your schema.** `@override` can take fields from your subgraphs. `@requires` makes your router send your entity data to their server. The draft replaces this with an allowlist.

4. **Eight partners adding live metrics to the same three types will collide.** The draft requires one namespaced field per partner per entity, and a type-name prefix.

### Decisions I assumed (change them if wrong)

- **Visibility:** partner fields are hidden from the public graph by default. You enable them for specific consumers, using `@tag` plus GraphOS contracts. I assumed "public graph" means anonymous or self-serve developers, not only the partners.
- **Network:** partner subgraphs are reachable only from your router (allowlisted IPs or mTLS).
- **Support:** partner SLOs are contractual. Your agreements need to say what happens when a partner subgraph is slow.
- **Placeholders:** bracketed values (`[...]`) are yours to fill in.

---

# Part B. Partner Subgraph Guide (draft v0.1)

## 1. What you are building

You will add computed, live metrics to our **Dashboard**, **Dataset** and **Alert** types. Your service is a GraphQL **subgraph**. Our router sends it only the part of a query that concerns your fields, then merges the result with data from our own services. Clients see one graph.

You own your fields and your service's uptime. We own the core types, the router and the supergraph.

## 2. Schema standard: Apollo Federation 2

Write your subgraph against **Apollo Federation 2, version [PINNED_VERSION]**. We pin this version and announce changes at least [90] days ahead.

Federation 2 is not the GraphQL Composite Schemas spec. The two share concepts, such as entity keys and cross-subgraph field dependencies, but they use different directives. A Composite Schemas subgraph will not compose here. If we move to that spec later, we will publish a migration guide. We make no commitment on timing.

Your service must implement the federation subgraph interface (`_service { sdl }` and `_entities`). Apollo's subgraph libraries do this for you.

## 3. Schema contract

### 3.1 Referencing our entities

Declare our entities as non-resolvable stubs. You reference them but never serve them.

```graphql
extend schema
  @link(url: "https://specs.apollo.dev/federation/v2.9",
        import: ["@key", "@tag"])

type Dashboard @key(fields: "id", resolvable: false) {
  id: ID!
  acmeMetrics: AcmeDashboardMetrics @tag(name: "partner-acme")
}

type Dataset @key(fields: "id", resolvable: false) {
  id: ID!
  acmeMetrics: AcmeDatasetMetrics @tag(name: "partner-acme")
}

type Alert @key(fields: "id", resolvable: false) {
  id: ID!
  acmeMetrics: AcmeAlertMetrics @tag(name: "partner-acme")
}

type AcmeDashboardMetrics {
  p95LoadMs: Float
  activeViewers: Int
  # ...
}
```

Rules:

- Use the key fields we publish for each entity: `id` only, unless we tell you otherwise.
- Add **one** field per entity, named `<partner>Metrics`. Put everything else inside that object type.
- Prefix every type you define with your partner name (`Acme...`). Type names are global in the supergraph, and an unprefixed name will collide with another partner's.
- Make every field nullable unless it is always computable. A partial result is better than a failed query (see 4.3).
- Document every field with a description. We review them.

### 3.2 Federation directives

| Status | Directives |
|---|---|
| Allowed | `@link`, `@key` (non-resolvable on our types), `@tag`, `@shareable` on your own value types only, `@authenticated` and `@requiresScopes` on your own fields |
| Needs written approval | `@requires` and `@external` (these send our data to your server), `@provides`, `@key` on entities you introduce, `@composeDirective`, `@interfaceObject` |
| Not allowed | `@override`, `@extends`, redefining or adding fields to our types beyond 3.1, and any directive that changes ownership of our fields |

If you need a computed metric to depend on one of our fields, for example a dataset's row count, request `@requires` approval and name the field. We will tell you what data your server will receive and under what terms.

### 3.3 Naming and change rules

- Never remove or change the type of a field without our check passing (see section 5) and [60] days' notice.
- Deprecate with `@deprecated(reason: "...")` first.
- Do not use `@shareable` on a field we or another partner also defines.

## 4. Runtime requirements

### 4.1 Network and authentication

- Serve over HTTPS. Allow traffic only from our router: [mTLS / IP allowlist / shared-secret header].
- Our router forwards end-user identity as [signed JWT claims in a header]. Validate the signature and **do not trust unsigned headers**. Enforce your own authorization on top of ours.
- Do not expose your subgraph endpoint publicly.

### 4.2 Performance

- Our router times out subgraph requests at **[X] ms**. Aim for p95 under **[Y] ms**.
- Implement `_entities` as a **batched** resolver. One query can ask for hundreds of dashboards. A per-entity database call will miss the timeout.
- Metrics are "live computed", so cap your own cost. Reject or truncate expensive computations rather than blocking.

### 4.3 Errors and availability

- If a metric can't be computed, return `null` for that field plus an entry in `errors`. Do not fail the whole `_entities` call.
- Don't put internal details in error messages. Clients can see them.
- Target availability: **[99.x]%**, measured at our router.
- If your subgraph exceeds the timeout or error budget, we may disable your fields in the supergraph without notice until it recovers.

## 5. Workflow: from first commit to production

1. **Onboarding.** We create a sandbox graph for you in GraphOS. It contains a copy of our schema and mock data, and nothing from production. We send you one API key, scoped to the sandbox.
2. **Develop.** Store the key in your CI secrets as `APOLLO_KEY`. Never commit it. Locally, compose against the sandbox:

   ```
   rover subgraph check [GRAPH]@sandbox --name acme --schema ./schema.graphql
   ```

3. **CI check on every PR.** The check detects composition errors and breaking changes against recorded query traffic.
4. **Publish to the sandbox** from your CI after merge:

   ```
   rover subgraph publish [GRAPH]@sandbox --name acme \
     --schema ./schema.graphql --routing-url https://[your-endpoint]
   ```

5. **Request production.** Open a pull request on [our partner repo] with your `schema.graphql` and a short description of each new field, its source data, and its cost. Our graph team reviews it against sections 3 and 4 within [N] business days.
6. **We publish to production.** We run the production publish from our own CI. You never hold production credentials. Routing-URL changes go through the same review.
7. **Staged rollout.** New fields are first visible to your own test consumers only (contract tag `partner-acme`), then to the audience we agree.

## 6. Security and data handling

- The sandbox key is secret. Rotate it every [90] days, and immediately if exposed. Tell us at [security contact].
- Our router sends your server the entity key (`id`) and any `@requires` fields we approved. Treat everything the router sends as **[confidential]**. Don't log it beyond [N] days.
- Query traffic reveals our customers' usage patterns. Do not use it for any purpose other than serving the request.
- We may ask for a security review before approving production.

## 7. Onboarding checklist

- [ ] Federation 2 subgraph passes `rover subgraph check` in the sandbox
- [ ] One `<partner>Metrics` field per entity, all types prefixed
- [ ] All fields nullable where a failure is possible, with descriptions
- [ ] `_entities` batched; p95 under target in load test
- [ ] JWT validation implemented; endpoint not publicly reachable
- [ ] CI uses secret-stored `APOLLO_KEY`
- [ ] Contact, on-call and incident process shared with us
- [ ] Production PR opened

## 8. Support

Contact: [partner-engineering email / Slack channel]. Planned changes to our entities will be announced at [changelog URL] at least [30] days ahead.

---

## Open items before you send this

1. Confirm with Apollo whether your plan supports narrower key scoping. If it does, the sandbox-graph design may be simpler.
2. Fill in the pinned Federation version, timeouts, SLOs and notice periods.
3. Align legal on section 6 and on the SLO clause in each partner agreement.
4. Decide whether partner fields are public or gated. The guide assumes gated.

I can turn Part B into a Markdown file, or draft the partner-facing PR template for step 5, if you want.