**Verdict: don't build the portal flow yet.** The sketch puts partner-authored schemas into your production graph. That is the one thing the extension ladder refuses by name. Rung 4 below delivers the same marketplace without the risk.

I read the skill and its three references. Your interview answers are only partly known, so I state my assumptions where I make them. Answers to the questions at the end could change some of this.

## 1. Need classification

- Both examples (benefits enrollment, course progress) are live data computed on the partner's side. That leaves rungs 3-5 on the ladder.
- ⚠️ Ask yourself if you need live data at all. You already accept 60s staleness from the cache. If minutes of lag are fine for most of the 40 apps, rung 1 (app-owned extension data) or rung 2 (platform-ingested connector) removes partner code from the request path.
  - Rung 1 means apps push values by API when data changes, and you store them.
  - Rung 2 means apps sync into canonical platform types.
  - Both are cheaper and safer, and I'd rank them above everything below. Keep the live design only for apps that truly need it.

## 2. Ladder position

Your plan is not rung 3. At rung 3 the platform writes the mapping to the partner's API. Here each partner authors its own schema, and the gateway adds that schema as a remote schema with its fields on `Employee`. That is partner-owned schema in the first-party production graph.

Ranking for the live rungs that remain:

- Efficiency: `mediated extension field > platform-operated connector > isolated partner subgraph`
- Effort, highest first: `isolated partner subgraph > mediated extension field > platform-operated connector`
- Value: `isolated partner subgraph == mediated extension field > platform-operated connector`
- Compliance cost, highest first: `isolated partner subgraph > mediated extension field > platform-operated connector`
- Durability: `platform-operated connector > mediated extension field > isolated partner subgraph`

Interview answer 2 moved the ranking. 40 self-serve apps demote rung 3 (you'd write 40 mappings) and rung 5 (you'd review 40 schemas). Rung 4 builds its contract and proxy once.

**Recommendation: rung 4, a mediated extension field.** It is one platform-owned field that your proxy resolves:

```graphql
type Employee {
  # nullable: a partner failure yields null plus an error, never a blanked Employee
  app(id: ID!): AppExtension
}
```

- The return shape is a platform-defined envelope: display fields, a link and a status that you type. It also carries a payload validated against a JSON Schema the partner registers.
- Partners register an endpoint and a payload schema. They submit no SDL.
- If you already run a sandboxed function runtime, prefer the hosted variant. It only removes partner egress if the sandbox has no outbound network.

## 3. Blockers in the current plan

1. **Partner schemas in the production graph.** Every partner failure, field hijack and composition break lands on first-party traffic. Composition checks only that a schema is valid. It never checks what the partner may claim, such as `@override` on a platform field. Rung 4 removes the problem because there is no partner SDL.
2. **The shared 60s gateway cache.** A partner response without a private scope can be served to a different tenant, and this is employee data. Key the cache by partner, tenant, employee and arguments, and mark it private. Turn off cross-request deduplication for partner calls. You keep the load protection for partners without the leak. Let partners declare a TTL within bounds you set.
3. **Every tenant sees every app's fields.** Tenants never chose those partners. With one `Employee.app(id:)` field the schema is identical for everyone, so discovery moves to the marketplace catalog. Enforce visibility at request time, with a per-install scope the router or proxy checks. A tenant that hasn't installed app X gets "not installed", not X's data. Contract-style schema filtering must be include-only, and one variant per install combination doesn't scale past a few partners.
4. **Self-serve endpoint registration is an SSRF door.** Anyone can submit a URL that your servers will call. Require HTTPS on public addresses only, and re-check on every DNS resolution. Reject private, loopback, link-local and cloud-metadata ranges, including after redirects. Route partner calls through a dedicated egress proxy with an allowlist of registered hosts.
5. **No data-clearance list.** HR and payroll data is regulated. See section 4.

## 4. What the partner receives

- Start the clearance list for `Employee` at opaque identifiers only: a per-app employee ID and the tenant ID. Nothing else by default.
- The partner then maps the ID to its own records, which a benefits or learning app already does.
- Add any personal or regulated field only with all three of:
  - tenant consent recorded at install
  - signed partner data-processing terms
  - a residency check of the partner's hosting region
- Otherwise expose a coarser derived field instead (an age band, a region). The portal install screen must show the tenant admin exactly what flows to the app.

Credentials toward partners:

- Forward no client token, cookie or platform API key. Use no catch-all header propagation. List the allowed headers by name.
- Mint a per-partner token per request, short-lived, audience-bound to that partner, and scoped to the installing tenant and the consented scopes. The standard shape is OAuth 2.0 Token Exchange (RFC 8693). A static header insert can't do this, so you need proxy or router code.
- The partner endpoint must verify the platform token (mTLS or a signature). It takes tenant and scopes from the token, never from the request body.
- Treat partner output as untrusted input. Mask partner error text to a platform error code plus the partner ID. Never pass partner `extensions` to clients.

## 5. Blast radius

- **Timeout per partner** = client SLA − internal p95 up to the partner hop − margin. Router defaults of 30-60s are far too high. Illustration only: with an 800ms SLA, 200ms internal and 100ms margin, the partner timeout is 500ms.
- **Circuit breaker per partner**, with timeouts counted as failures. If your gateway has none, use an egress proxy with outlier detection.
- **Request deadline** above the partner timeouts, never below. Otherwise a partner failure fails the whole query instead of returning platform data plus an error.
- **Fan-out cap.** 40 apps × a list of employees can become thousands of partner calls.
  - Make clients name apps explicitly in the query, and cap apps per query.
  - Batch employee IDs into one call per partner per query, so the partner endpoint must accept batches.
  - Price `Employee.app` in your query cost model and rate-limit per partner.
- **Self-serve suspension rule.** State up front how long an open circuit lasts before an app is suspended. Give each app a status component and name an owner.

## 6. Lifecycle for the portal flow

1. **Register.** The portal validates the endpoint (section 3, item 4), the payload JSON Schema and the declared data needs. A platform-owned check blocks the registration. Partners never hold a credential that changes the platform's config.
2. **Install.** A tenant admin consents to the exact data flow. The install creates the per-tenant scope.
3. **Platform changes.** A change that breaks partners, such as a removed clearance field, goes through your versioning policy's notice window.
4. **Partner changes.** A payload schema change that removes or retypes a field clients query needs an operation check against real client usage. Apply your usual deprecation window to partner fields.
5. **Observe.** Track latency, error rate, timeout rate and circuit state per partner, attributable in response extensions.
6. **Offboard.** Run an impact check and pull per-field usage first. Give clients the notice window, then remove the app. Define uninstall semantics now, for example "definitions deleted, values retained N days".

## 7. Gates before launch

Use a canary partner endpoint that echoes what it receives. Every gate is binary.

- It never sees a client `Authorization`, `Cookie` or platform key.
- A call with no platform credential, or another tenant's token, is rejected.
- A tenant without the app installed gets no partner data.
- With the canary stalled, the query returns platform data plus a partner-field error within the SLA.
- An offboarding drill runs the impact check before removal.
- A response cached for tenant A is never served to tenant B.

## Open questions

These can still change the design, so answer them before you commit:

1. Can most apps live with minutes of staleness? If yes, rung 1 or 2 may replace most of this.
2. What is the client latency SLA on queries that would include partner fields?
3. Which `Employee` fields would partners need to compute theirs? Name them and flag the personal ones.
4. What is your gateway and registry stack, and under which license?
5. When must the first app go live, and how many platform engineering weeks can you spend? I can't size the build without this.

Next, in 5 minutes: send me answers to questions 1 and 3. They decide whether this is rung 1, rung 2 or rung 4, and which fields enter the clearance list.