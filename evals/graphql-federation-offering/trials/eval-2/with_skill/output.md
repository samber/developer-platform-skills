# Router review: partners variant, Brackwater go-live Nov 18

**Verdict: not ready.** The `router.yaml` has three blockers. Brackwater's SDL has three more. Two decisions are missing. There are 19 days left, and everything below fits in that time.

Assumptions (correct me if wrong):
- Your interview answers cover the need, partner count, Apollo Router 2.x, and the 800 ms SLA.
- The need is live partner-computed quotes, so the ladder leaves rungs 3-5 standing.
- Brackwater's endpoint is a public HTTPS URL.
- The partners router carries the first-party subgraphs plus the four insurers.
- I don't have your internal p95 to the `@requires` hop, so the timeout below is a formula with a placeholder.

## Blockers

### 1. Catch-all header propagation (step 4)

`propagate: matching: ".*"` forwards every client header to every subgraph. That includes `Authorization` and `Cookie`. The extra `named: Authorization` rule changes nothing.

- **Impact:** Brackwater's resolver receives fleet managers' end-user bearer tokens on every call.
- **Inheritance:** `headers.all` applies to every subgraph, so insurers 2-4 would inherit it.
- **Fix:**
  - Empty `all`.
  - Move any header an internal subgraph really needs to `headers.subgraphs.<internal>` as named rules.
  - Give Brackwater no propagate rule at all.
- **Why not `remove`:** a `remove` can't undo an `all` catch-all. Rule order decides, and an explicit allowlist leaves nothing to order.
- **Token:** Brackwater gets a per-partner token that is short-lived, bound to Brackwater's audience, the installing tenant, and consented scopes.
  - A static `insert` can't carry a per-tenant token.
  - Mint it per request in a coprocessor at the SubgraphService stage, conditioned on the subgraph name, or in the egress proxy.
  - Count the coprocessor hop in your latency margin.

### 2. Cross-request deduplication on partner traffic (step 5)

`traffic_shaping.all.deduplicate_query: true` collapses identical in-flight requests from different callers into one. Today the callers' credentials are forwarded as well (blocker 1).

- **Impact:** one tenant's insurance quote can be served to another caller.
- **Fix:** set `false` for Brackwater, and make `false` the default in `all` so new insurers inherit it. Re-enable it per internal subgraph if you want it back.

### 3. No partner timeout, circuit breaker, or request deadline (step 5)

You rely on defaults. The subgraph timeout is 30 s and the router timeout is 30 s. The 800 ms p95 on the fleet dashboard query is not protected at all. A stalled Brackwater holds the dashboard for 30 s.

- **Partner timeout:** 800 ms minus internal p95 to the `@requires` hop, minus a margin.
  - The `@requires` hop runs after the platform has fetched `dateOfBirth` and `licenseClass`.
  - Example only: if the internal p95 is 250 ms and the margin is 100 ms, the timeout is 450 ms. Measure your real number.
- **Router deadline:** set above the partner timeout, never below. If it fires first, the whole query fails instead of returning platform data plus a partner-field error. Roughly 1 s clears the example.
- **Circuit breaker:** Apollo Router has no documented native one. Put an egress proxy with outlier detection in front of every insurer, counting timeouts as failures.
  - The same proxy can pin egress to a host allowlist.
  - It can enforce public-HTTPS and SSRF checks on each resolution, even for a platform-set URL.
- **Retries:** confirm no retry setting multiplies the budget.
- **Rate limit:** limit per partner and size it from peak dashboard QPS times entities per query.

Target `router.yaml`. Key names are from memory, so verify them against your 2.x version:

```yaml
headers:
  all:
    request: []                # nothing forwarded by default
  subgraphs:
    # <internal-subgraph>:     # named allowlist per internal subgraph, only what it needs
    #   request:
    #     - propagate: { named: Authorization }
    brackwater:
      request: []              # token minted by coprocessor / egress proxy
traffic_shaping:
  router:
    timeout: 1000ms            # backstop above partner timeout
  all:
    deduplicate_query: false
  subgraphs:
    brackwater:
      timeout: 450ms           # 800 - internal p95 - margin; measure, don't copy
      deduplicate_query: false
      global_rate_limit: { capacity: <from peak QPS>, interval: 1s }
include_subgraph_errors:
  subgraphs:
    brackwater: false          # mask message and extensions; add platform code + partner ID in the coprocessor
supergraph:
  introspection: false         # keep
```

### 4. Brackwater SDL fails the partner policy (step 3)

The snippet has two violations.

- **Unprefixed, non-null type:** `brackwaterQuote: Quote!`
  - The type must be `Brackwater_Quote`.
  - The field must be nullable.
  - A Brackwater timeout would otherwise null the whole `Driver`. On the dashboard list, that can blank rows or the list.
  - The same applies to the Vehicle field.
- **Missing `@external` declaration:** `licenseClass` isn't declared `@external` in the snippet. Composition will tell you if that's real.

`Driver @key(fields: "id")` is acceptable only if `Driver` and `Vehicle` are on a written extendable-entity allowlist.

### 5. `@requires(dateOfBirth)` ships regulated data (step 4)

The router sends `dateOfBirth` to Brackwater whenever the field resolves, even if the client never selected it. On the dashboard list it ships once per driver row.

- **Option A (preferred):** minimize. Brackwater needs age to price. Expose a derived platform field such as `ageBand`, hidden from the public schema, and have Brackwater `@requires` that. Check whether `licenseClass` can be coarsened too.
- **Option B:** put `dateOfBirth` and `licenseClass` on the Driver clearance list. That needs all three of these first:
  - tenant consent recorded at install,
  - signed data-processing terms with Brackwater,
  - a residency check of Brackwater's hosting region.

  Without all three, don't ship them.

### 6. Partner endpoint authentication is unverified (step 4)

Brackwater's URL is public. Without mTLS or signed-token checks, anyone can post `_entities` keys and enumerate driver data.

- **Required:** mTLS or token verification on every call.
- **Required:** tenant and scopes taken from the token, never from the entity representation.
- **Required:** `_service` and introspection answered only to the platform.
- **Router side:** configure the subgraph TLS client certificate for Brackwater.

## Decisions to make

1. **Who reaches the partners router?** Fleet managers get the quote in the same query as the vehicle. If every tenant's traffic hits this router, first-party queries share Brackwater's blast radius and the isolation is nominal.
   - Recommended: route only tenants that installed an insurer to it.
   - Enforce the per-tenant install at request time with a platform-assigned scope. For example, the policy step stamps `@requiresScopes` on each Brackwater field at publish.
   - Use an include-only contract filter, never an exclude filter.
   - Mark each field's docstring "Provided by Brackwater Mutual, not covered by the platform SLA."
2. **Rung 5 itself (finding, not a blocker).** The ladder would pick rung 3 for a few contracted partners with existing APIs, so rung 5 is not the default.
   - **Approved rung 5 stays valid if:** the partner set is small and contractual (met: 4), fields need joint planning across several platform entities, and review is a standing, staffed job. Confirm the last two.
   - **Hard date:** Nov 18 would favor rung 3 (platform-operated mapping). Keep it as the fallback for Brackwater if blockers 4-6 don't close in time.
   - **Router licensing:** Apollo Router is ELv2, so it doesn't lower rung 5's effort.

Ranking lines for the standing rungs (3 = connector, 4 = mediated field, 5 = partner subgraph):
- **Efficiency:** `connector > mediated field > partner subgraph`
- **Effort, highest first:** `partner subgraph > mediated field > connector`
- **Value:** `partner subgraph == mediated field > connector`
- **Compliance cost, highest first:** `partner subgraph > mediated field > connector`
- **Durability:** `connector > mediated field > partner subgraph`

## Also check before launch

- **Caching:**
  - Confirm no shared response cache or entity cache covers Brackwater.
  - If one does, scope it private and include the tenant in the cache key.
- **Error masking:** partner `extensions` must not reach clients. The `include_subgraph_errors` entry above masks Brackwater errors; the coprocessor replaces them with a platform code plus the partner ID.
- **Cost model:** price partner fields in the query cost model, and cap pagination on the dashboard query. The platform sets the cost, not Brackwater's SDL.
- **Router version:** confirm you are at or above the fixes for these CVEs, and still reject `@interfaceObject`.
  - CVE-2025-64173: 2.8.1.
  - CVE-2025-32034: 2.1.1.
  - CVE-2024-43414: planner 2.8.5, triggered when a partner co-resolves a `@shareable` field.
- **Directive policy:** the blocking check must reject these (see `partner-sdl-policy.md`). Audit the platform's own `@shareable` fields too, since a partner could redefine those types.
  - `@override`,
  - `@shareable` on platform types,
  - `@provides`,
  - `@interfaceObject`,
  - `@inaccessible` outside the partner namespace,
  - partner-chosen `@tag` values.
- **Publish path:**
  - Only the platform publishes to the variant.
  - Brackwater gets a check-only credential scoped to its own subgraph.
  - If GraphOS can't scope one, run checks through a submission endpoint.
  - Run operation checks against client usage on every publish.
- **Operations:** name an owner per partner, add per-partner dashboards (latency, errors, timeouts, circuit state), a status component, and a suspension threshold.

## Go-live gates (all must pass before Nov 18)

1. A test publish with `@override` on a platform field is rejected.
2. A canary endpoint that echoes headers shows no `Authorization`, `Cookie`, or platform key.
3. A canary call with no platform credential, or with another tenant's token, is rejected.
4. With the canary stalled, the dashboard query returns platform data plus a Brackwater error within 800 ms.
5. No Brackwater field is non-null, unprefixed, or visible to a tenant without the install.
6. An offboarding drill runs the removal-impact check, then removes Brackwater from the partners variant first and the base graph second.

## Suggested order

1. Fix the three `router.yaml` blockers (headers, dedup, timeouts), then add the egress proxy. About 1 day for the config, plus the proxy and coprocessor build.
2. Decide the `dateOfBirth` question and the router traffic question. Both need legal or leadership input, so start them first.
3. Send Brackwater the SDL corrections, then run the policy check on their re-publish.
4. Run the gates on a canary, then go live.