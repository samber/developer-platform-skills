# Policy doc: persisted operations on the public GraphQL endpoint

## 1. Position to take with Security

Security's two claims need separating.

- **Allowlist-only execution (the mandate): adopt it.** It removes arbitrary query shapes, shrinks the attack surface, and gives you a per-operation inventory.
- **"Allowlisted means safe, so retire depth and complexity limits": reject, in part.** An allowlist fixes the *document*. It does not fix *cost*, because cost depends on the variables and the data at execution time.

| Control | Does the allowlist cover it? | Recommendation |
|---|---|---|
| Depth limit | Yes. Depth is a static property of the document. | Move to registration time. Reject deep documents at registration, so there is no per-request cost. |
| Complexity budget | No. It depends on variables such as `first: 10000` or nested `first × first` connections. | Keep it at runtime, computed from the document's static cost model plus the actual variable values. |
| Pagination and list-argument caps | No. | Add or keep hard maxima on `first`/`last`, list-argument length, and ID-array size. |
| Rate limiting | No. | Keep it, preferably cost-weighted per client, since cost varies per call. |
| Timeouts and resolver limits | No. | Keep. |
| Authorization (object-level and field-level) | No. | Keep. A reviewed query still returns whatever the caller's token allows. |
| Introspection | Not applicable. | Disable in production, since introspection is a raw query. |

Three facts support this:

- **Reviewed does not mean cheap on every tenant.** A query that is fine for a 200-workflow tenant can be expensive for a 2M-workflow tenant. Review sees the document, not the data.
- **Hashes are not credentials.** Mobile hashes ship in public binaries and are trivially extractable. An attacker can replay any known hash with hostile variables. Variables are therefore untrusted input, and the cost cap has to act on them.
- **Registration becomes the new attack surface.** Whoever can register operations controls what the server will run.

Suggested wording for the doc: *"Persisted operations replace query-shape controls with registration-time controls. They do not replace controls that depend on request-time inputs or data."*

## 2. Scope and definitions

- **Scope:** the whole public endpoint, covering HTTP POST and GET, any batching, WebSocket or SSE subscriptions, and GraphiQL or playground tooling.
- **Persisted operation:** a document stored server-side, identified by a hash (SHA-256 of the normalized document is the usual choice).
- **Registry:** the server-side store mapping hash to document, owner, status, and computed costs.
- **Client classes:**
  - first-party mobile
  - third-party integrators (about 900)
  - internal tooling

## 3. Requirements (MUST / MUST NOT)

**Execution**
1. The server executes only operations whose hash is in the registry and active.
2. The server rejects any request carrying a raw query string, including requests that send both a document and a hash. The server never trusts a client-supplied document, even with a matching hash.
3. Automatic persisted queries (register-on-miss) are disabled. They defeat the mandate.
4. An unknown hash returns a uniform 4xx error (for example `PersistedOperationNotFound`) and logs the client identity. It reveals nothing about which hashes exist.
5. Introspection is off in production. Schema documentation is published through another channel (see §6).
6. Subscriptions and batched requests follow the same rule, per operation. Cap the batch size.

**Registration-time validation** (the registry rejects the operation if any check fails)
1. The document validates against the current schema.
2. Depth is at or below the maximum.
3. Static worst-case complexity (variable-independent part) is at or below a registration cap.
4. No unbounded list fields without pagination arguments.
5. It has a name, and each operation is single-purpose.
6. Per-owner quota on the number of active operations.

**Runtime (unchanged or tightened)**
1. Complexity is evaluated with the actual variables against the per-request budget.
2. Hard maxima apply to pagination and list arguments.
3. Variables are validated against declared types, with length and size caps.
4. Per-client rate limiting is cost-weighted, and timeouts apply.
5. Authorization is enforced per field and per object, independent of the operation.

**Registry integrity**
1. Registration requires authentication.
2. Every registration, approval, and revocation is audit-logged with who and when.
3. Registry writes are not reachable from the query endpoint.
4. Every operation has a kill switch for immediate revocation by hash.

## 4. Client-specific mechanics

### First-party mobile
- Extract operations at build time and register them in CI before release, with the hash manifest part of the release artifact.
- **Old app versions must keep working.** Operations stay active until the app versions that use them fall below the minimum supported version. Tie retention to that support policy.
- Release order: register first, then ship the app. Make this a release gate.
- Add a failure path: if the server rejects a hash, the app must degrade gracefully rather than crash-loop.

### Third-party integrators (the hard part)
Roughly 900 integrators build automations, so some of them compose queries dynamically. A hard "no raw queries, no exceptions" will break some of them.

- **Self-service registration API and CLI.** An integrator submits a document and gets a hash back. Registration runs the same automated validation as §3.
- **Tiered approval:**
  - Auto-approve when the operation is under the cost and depth caps.
  - Queue for manual review above the caps, with a published SLA.
- **Per-integrator namespace and quota**, so one integrator cannot flood the registry.
- **Dynamic needs without raw queries**, in order of preference:
  1. Parameterize through variables.
  2. Use `@include`/`@skip` with boolean variables for optional fields.
  3. Register a small set of precomposed variants.
  4. Offer a non-GraphQL path (webhooks, bulk export, or REST) for use cases that genuinely need open-ended shapes.
- **Developer experience:** the schema reference, an operation explorer in the sandbox environment, and clear registration errors. Without these, the mandate produces a support flood.

### Environments
- Raw queries are allowed in dev and staging only, with no production data and no route into production.
- Breaking even this is a Security decision (see §8).

## 5. Rollout plan (this quarter)

1. **Weeks 1–2 — Measure:** log raw versus persisted traffic per client, and per integrator for the top spenders. Establish the real percentage of raw-query traffic.
2. **Weeks 2–4 — Build and announce:** ship the registry, registration API, and CLI. Notify all integrators with the date and a migration guide. Give mobile a CI step.
3. **Weeks 4–8 — Shadow enforcement:** keep accepting raw queries, but log "would have been rejected" per client. Contact top offenders directly. Fix registration friction found along the way.
4. **Weeks 8–10 — Enforce for first-party and opted-in integrators.**
5. **Cutover date — Enforce for everyone**, with an instant rollback flag. Define rollback criteria up front (for example, error rate or support volume above a threshold).

The doc should state the cutover date and what "ready" means. Without that, "next quarter" slips, or breaks integrators.

## 6. Observability and operations

- Per-hash metrics: call count, p50/p95/p99 latency, computed cost, error rate, owner. This is a benefit of the mandate, and it makes expensive operations visible.
- Alerts: spikes in unknown-hash rejections (scanning or a broken release), registration spikes, per-hash cost drift.
- Lifecycle: operations unused for N days become flagged, then revoked. Schema deprecations trigger a re-validation of affected operations and notification of owners.
- Schema docs and changelog published for integrators, since introspection is off.

## 7. Risks to name explicitly

| Risk | Mitigation |
|---|---|
| Integrator breakage at cutover | Shadow mode, direct outreach, rollback flag |
| Registry flooded or abused | Quotas, auth, rate limits on registration |
| Expensive-but-valid operation hits large tenants | Runtime complexity budget, pagination caps, per-hash cost metrics |
| Mobile hash extraction and replay with hostile variables | Treat variables as untrusted, apply authz, rate limits, and cost caps |
| Review bottleneck | Auto-approve tier, with a manual queue only above the caps |
| Old mobile versions broken by revocation | Retention tied to minimum supported app version |
| Pressure to bypass via exceptions | Single documented break-glass path (§8) |

## 8. Decisions you need before publishing

1. **Break-glass.** "No exceptions" has a cost: during an incident, nobody can run an ad-hoc query. Propose a separate internal-only endpoint, behind VPN and authentication, not the public one. Security must accept or reject it explicitly.
2. **Depth limit.** Confirm with Security that moving it to registration time satisfies the intent. Retiring it entirely is not needed, and the doc should say why (§1).
3. **Complexity budget.** Keep it. Get Security's agreement in writing, with the argument that cost depends on variables and data.
4. **Integrator SLA.** Decide the manual review turnaround.
5. **Non-GraphQL fallback.** Decide whether to offer one for integrators who cannot work with registered operations.
6. **Cutover date and rollback criteria.**

## 9. Suggested one-paragraph summary for the top of the doc

> From [date], the public GraphQL endpoint executes only pre-registered operations. Raw query strings are rejected. Operations are validated at registration for schema conformance, depth, and static complexity. Request-time controls (variable-aware complexity budget, pagination caps, rate limiting, timeouts, and authorization) remain in force, because an allowlist fixes the query shape but not its cost or the caller's access.

I couldn't verify your current stack, your depth and complexity numbers, or the integrator traffic mix, so those need your data. The 900-integrator migration is the main schedule risk. I'd show Security the shadow-mode measurements before agreeing to a hard date.