# Partner Subgraph Guide: design record and draft

I read the skill and its three references. I couldn't check the Composite Schemas spec's current stage, because the web fetch was denied. The skill's reference last recorded it at Stage 0 (Preliminary), so re-check it before this guide goes out.

## Part A: What changes in your draft outline

| Your draft | Verdict | Replace with |
|---|---|---|
| (1) Build against the Composite Schemas spec to be future-proof | ❌ Can't promise this | The spec was at Stage 0 when last recorded, and Stage 0 "can change before reaching Draft". Partners should build against the Apollo Federation 2 dialect, pinned by `@link` to a version range you set. State that the dialect may change, with notice under your versioning policy. |
| (2) Each partner gets a GraphOS key and runs `rover subgraph publish` from CI | ❌ Blocker | Partners get a check-only credential scoped to their own subgraph. They run `rover subgraph check` in their CI. Only you publish, after your own composition and policy checks. A key that can publish lets a partner push `@override` onto your `Dashboard` fields, and composition would accept it. |
| (3) Your subgraph composes into our main supergraph | ❌ Blocker | Partner subgraphs compose into an isolated partner variant, served by a separate router. They never compose into the first-party production supergraph. Every partner outage, hijack or composition break would otherwise land on your own traffic. |
| (4) Use any federation directive you need | ❌ Blocker | A published allow/deny directive table, enforced by a blocking check. See section 4. |

## Part B: Design record

**Assumptions.** I couldn't ask the interview questions, so I assumed the following. Correct me on any of them.
- Partners are 4 signed now and about 8 later, all under contract.
- Fields are visible only to tenants that installed the partner.
- No personal or regulated data is needed.
- You run Apollo GraphOS and the Apollo Router today.
- You can staff partner schema review as a standing job.

**Need classification.** Live computed metrics on `Dashboard`, `Dataset` and `Alert`, joined in one query, is the "live data computed by the partner" shape. That leaves rungs 3 to 5.

**Rungs 0 to 2 are out of scope here.** If any partner only wants to attach stored values or react to events, give them app-owned custom fields or webhooks instead. A partner subgraph is wrong for that.

**Ranking (live rungs only):**
- efficiency: `platform-operated connector > mediated extension field > isolated partner subgraph`
- effort, highest first: `isolated partner subgraph > mediated extension field > platform-operated connector`
- value: `isolated partner subgraph == mediated extension field > platform-operated connector`
- compliance cost, highest first: `isolated partner subgraph > mediated extension field > platform-operated connector`
- durability: `platform-operated connector > mediated extension field > isolated partner subgraph`

**Recommendation: rung 5, an isolated partner subgraph in a separate partner variant and router.**
- Few partners under contract does not demote rung 5, even at 8.
- Fields across several entities need joint planning, which promotes it from rung 4.
- Your answers moved nothing else. A hard launch date would favor rung 3 instead.

**Conditions on rung 5:**
- You must staff partner schema review as a standing job. If you can't, fall back to rung 4: a platform-owned `Dashboard.extension(app: ID!)` field behind a proxy. It gives the same live value with less exposure, and the router stays swappable.
- If a partner's metric needs no cross-entity planning, rung 3 (you map their existing API) is cheaper for both sides.

## Part C: The guide

### 1. What this program is

- Strategic partners contribute live computed fields to `Dashboard`, `Dataset` and `Alert`.
- Your subgraph runs on your infrastructure.
- Your fields are served from a partner router, separate from Cobaltine's own graph.
- Cobaltine owns the supergraph. You own your subgraph and its uptime.
- Your fields are not covered by the Cobaltine platform SLA, and their docstrings say so.

### 2. Dialect and tooling

- Build with an Apollo Federation 2 subgraph library, which is permissively licensed.
- Pin `@link` to the federation version range we publish. A newer version fails composition for everyone.
- We are not promising the GraphQL Composite Schemas spec. If it matures, we will announce a migration window under our versioning policy.
- You need a GraphOS account for check access. Composition, query planning and the router are ours and carry our license (Apollo's ELv2).

### 3. What you may extend

- Extendable entities are `Dashboard`, `Dataset` and `Alert`, each by its published `@key` and nothing else. All other types are closed.
- Prefix every type and root field with your namespace, for example `Acme_MetricSeries` or one `acme` root field returning `AcmeNamespace`. Unprefixed types are rejected.
- Every field you add to a platform type must be nullable. If your service is down, the client gets null plus an error, and the `Dashboard` still renders.
- Do not add arguments to platform fields. Do not add members to platform enums, unions or interfaces.
- Partner mutations live only under your namespace.

### 4. Directive policy

| Directive | Allowed? |
|---|---|
| `@key` on an allowlisted entity | Yes, using the published key fields. |
| `@requires` | Only fields on your data-clearance list (section 5). |
| `@shareable` | Only on types inside your own namespace. Never on Cobaltine types or fields. |
| `@inaccessible` | Only on your own namespaced fields. |
| `@tag` | Only the tag values we assign. |
| `@override` (including `label:`) | Never. |
| `@provides` | Never. |
| `@interfaceObject` | Never. |
| `@authenticated`, `@requiresScopes`, `@policy` | We review these but never rely on them. Authorization is ours. |

Cobaltine runs a blocking policy check on every publish and rejects any row marked "Never". It also rejects unprefixed types, non-null fields on platform types, and `@requires` fields off the clearance list. We also check that you don't redefine Cobaltine's own `@shareable` types.

### 5. Data you receive and credentials

**Data-clearance list.** Each call to your endpoint carries only the following, per entity:
- the `@key` fields for `Dashboard`, `Dataset` and `Alert`
- the fields listed in the clearance table we give you
- the arguments the client passed to your fields

A `@requires` field is sent to you even when the client didn't select it. On a list query it is sent once per row. If you need a sensitive input, we will expose a coarser derived field for you to require instead.

**Cobaltine to fill in before publishing:** the clearance list per entity, and the consent that covers each field. Any personal or regulated field needs recorded tenant consent, signed data-processing terms, and a residency check of your hosting region.

**Credentials:**
- We never forward end-user tokens, cookies or Cobaltine API keys to you.
- Each call carries a short-lived per-partner token. It is bound to your audience, the installing tenant and the consented scopes. A router extension or coprocessor mints it.
- Header propagation is an explicit allowlist, with no catch-all rule.
- Your endpoint must authenticate every call with mTLS or the signed platform token. Take tenant and scopes from the token, never from the entity representation.
- Answer `_service` and introspection only to Cobaltine. Your endpoint is a public URL, so without this anyone could post `_entities` keys and enumerate your data about every tenant.
- We treat everything you return as untrusted. Your error messages are masked to a platform code plus your partner ID, and your `extensions` are never passed to clients.

### 6. Performance and failure

- **Timeout:** the client latency SLA, minus the internal p95 up to your hop, minus a margin. Router defaults of 30 to 60 s are not used. Values go into the contract once we have the SLA.
- **Circuit breaker:** timeouts count as failures. Apollo Router has no native breaker, so partner calls go through an egress proxy with outlier detection.
- **Request deadline:** set above partner timeouts, so a slow partner degrades the result instead of failing the whole query. The router's request timeout defaults to the same 30 s as the subgraph timeout, so we raise it.
- **Cost and limits:** your fields are priced in our query cost model and rate-limited per partner.
- **Routing URL:** public HTTPS hosts only. It is re-validated on every DNS resolution and reached through a dedicated egress path. Private, loopback, link-local and metadata ranges are rejected, including after redirects.
- **Caching:** your responses are private-scoped, keyed by tenant, and excluded from shared caches and cross-request deduplication.

### 7. Who sees your fields

- Only tenants that installed your integration and consented to its data flow.
- The partner router serves an include-only schema (never an exclude filter), and per-tenant installs are enforced at request time by a platform-assigned scope.

### 8. Lifecycle

1. **Publish.**
   - Run `rover subgraph check` in your CI with the check-only credential.
   - Submit. Cobaltine re-runs composition and the policy check, then publishes. Partners hold no publish rights.
   - Where GraphOS can't scope the credential to one subgraph, checks go through a submission endpoint instead.
2. **Cobaltine changes.** If we break your composition, for example by removing a key field or renaming a clearance field, that is a breaking change with a notice window set by our versioning policy.
3. **Your changes.** A failing publish is yours to fix, and we never roll the graph forward around it. A publish that composes but removes or retypes a field clients query is the dangerous case. We run operation checks against client usage and hold your fields to our deprecation window.
4. **Monitoring.**
   - Latency, error rate, timeout rate and circuit state are tracked per partner.
   - Each partner has a named owner at Cobaltine and a status component.
   - The suspension threshold is how long an open circuit may last before you leave the variant. Cobaltine sets the number.
5. **Offboarding.**
   - We run a removal-impact check and pull per-field usage over the notice window.
   - We remove you from the partner variant first and the base graph second, and give clients the deprecation window.
   - Deleting the subgraph without that check is not allowed.

## Part D: Acceptance gates (canary partner endpoint)

- **Exposure:** no partner field on a platform type is non-null, unprefixed, or visible to tenants without the install.
- **Policy:** a test publish with `@override` on a `Dashboard` field is rejected. 100% of publishes go through the check.
- **Credentials:** a canary that echoes headers shows no client `Authorization`, `Cookie` or platform key.
- **Partner authentication:** calls with no platform credential, or another tenant's token, are rejected.
- **Blast radius:** with the canary stalled, a query returns platform data plus a partner-field error within the client SLA.
- **Lifecycle:** an offboarding drill runs the removal-impact check before removal.

## Questions for you before this ships

1. Is the join across entities computed on the partner side? If not, rung 4 or 3 is cheaper and safer.
2. Can you staff standing partner schema review?
3. What is the client latency SLA on these queries, and when must the first partner go live?
4. Do any of the metrics need personal or regulated fields?
5. Do you run Apollo Router Enterprise today? A separate router per variant needs it.