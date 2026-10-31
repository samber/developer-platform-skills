# Design review: partner fields on `Employee`

**Verdict:** ⚠️ The flow is buildable, but three of its five assumptions are unsafe for HR and payroll data. Fix those before you build the portal flow. The shared cache is the most serious.

## ❌ Blockers

**1. A shared 60s cache will leak data.**
- **What breaks:** Employee data depends on tenant, caller, scope and role. A cache keyed on the query or the employee ID can serve tenant A's or app A's data to someone else.
- **Key the cache on:** `(tenant, partner app, employee, caller's effective scopes/role, field set)`. Never share across tenants.
- **Let partners set the TTL:** let each app declare a TTL, capped at a ceiling you choose. "Live" enrollment data may need less than 60s.
- **Add a purge API:** partners call it to purge by `(app, tenant, employee)`. It beats waiting for a TTL.
- **It won't protect partners:** hit rate is low when keys are per employee. A list query of 100 employees fans out to 100 partner lookups.
  - Batch per request, DataLoader-style, with one batched entity lookup per partner and a per-partner batch cap.
  - Add per-partner rate limits and concurrency pools. Don't rely on the cache.

**2. "Every tenant sees every app's fields" mixes discovery with authorization.**
- **Discovery is fine:** put it in a marketplace catalog.
- **Resolution needs three gates:** the tenant installed the app, an admin consented to specific scopes, and the caller is allowed to see that employee.
- **Check the caller's identity:** the caller is often another third-party app. App A's token must not receive App B's data on `Employee`. Define which token can read which app's fields.
- **Schema visibility:** I'd show only installed or listed apps in introspection. A global schema also exposes draft apps, delisted apps and partner field names to every tenant. If the gateway can't filter introspection per tenant, enforce at execution and null the field.
- **Sub-processors:** each partner becomes a sub-processor of your tenants' employee data. That needs a DPA, tenant consent and an audit log of every outbound call, plus a per-tenant and per-app kill switch. Check data-residency rules for EU employees going to non-EU endpoints.

**3. Registering an arbitrary URL and stitching in whatever it introspects is too open.**
- **SSRF:** an app can point the gateway at internal hosts.
  - Verify domain ownership, and allow HTTPS only.
  - Resolve DNS and block private ranges, and pin the resolved IP to stop rebinding.
  - Refuse redirects, and send outbound traffic through an egress proxy.
- **Schema takeover:** a stitched or federated remote schema can add types, `Query` and `Mutation` fields, directives, and entity lookups for any employee ID.
  - Don't introspect live. Have the app **submit SDL** and validate it. Accept only an extension of `Employee`, plus types prefixed with the app slug.
  - Reject everything else.
- **One bad schema must not break others:** composition runs at publish time against stored, validated SDL. The gateway config reloads atomically, and failures reject the publish.

## ⚠️ Design changes

- **Namespace the fields.** Don't put fields directly on `Employee`. Use `Employee.apps { benefits { … } }` with a type like `Benefits_EnrollmentSummary`. This avoids collisions across 40 apps, keeps core autocomplete clean, and lets you remove an app by deleting one branch.
- **Define the contract, don't accept any schema.**
  - **Pull (live):** the partner implements a Quarrytown-defined batched lookup, such as `employees(ids: [ID!]!)`, and returns the declared type.
  - **Push (not live):** the partner writes to a Quarrytown-hosted extension store. There is no runtime dependency, caching and authorization are trivial, and deletion requests are easy. This suits the self-serve long tail.
  - I'd offer both, with pull limited to vetted apps at first.
- **Make every partner field nullable.**
  - Set a hard timeout of about 1–2s per partner, plus a circuit breaker.
  - Return partial data with `errors[].extensions.app`. A failing partner must not fail the `Employee` query.
- **Count partner fields in query cost.** Add depth, complexity and response-size limits. Strip anything the partner returns outside its declared type, and never let it override core fields.
- **Authenticate Quarrytown to the partner.**
  - Send a short-lived JWT signed by Quarrytown (JWKS published) with `tenant`, `app` and employee IDs, or use mTLS.
  - Never forward the caller's token. That is a confused-deputy risk.
  - Rotate the secrets.
- **Version the schema and gate breaking changes.** Apps publish named versions. Check each change against observed field usage per tenant. Support deprecation windows, because `Employee` is public API and you carry the permanence.
- **Auto-disable unhealthy apps** after sustained errors or latency, and notify the owner. Monitor each app's SLO and show its status in the catalog.

## Portal flow I'd build

1. Create the app and **verify domain ownership**.
2. Submit SDL and run automated checks: allowed shape, lint, size limits, name prefix.
3. Run the contract test against the endpoint with synthetic employees in a **sandbox tenant**. Draft apps are visible only to the owner's tenants.
4. **Submit for listing.** Self-serve registration is fine, but listing needs at least an automated security check, a signed DPA and a declared data-use statement. Keep a human review for scopes that touch sensitive fields.
5. A tenant admin installs the app and sees **a consent screen with scopes**. The gateway enforces it.
6. Gateway config reloads. The audit log, kill switch and per-app dashboards are live.

## Open questions

1. **Which gateway** is this: Apollo Router/Federation, Cosmo, Hive, or graphql-tools stitching? Per-tenant schema filtering and contracts depend on it.
2. **Who are the callers?** Tenants' own integrations, third-party apps with their own tokens, or both?
3. **Which `Employee` fields does the partner need as input?** Just the ID, or also email or national ID? Minimize this.
4. **Is "live" really sub-minute** for both example apps? If not, push covers most of them.
5. **Do you have DPA/sub-processor commitments** to tenants that already limit who may receive employee data?

If you answer the first two, I can sketch the cache key, token model and the gateway config for the namespaced extension.