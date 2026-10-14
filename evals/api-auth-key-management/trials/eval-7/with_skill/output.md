**Ship scoped keys that default to restrictive, built on your existing RBAC. Do not ship the PM's "full-access default, untick in advanced panel".**

I read `SKILL.md` plus `vendor-key-format-census.md` and `rotation-runbook.md`. I could not ask the clarifying questions, so the assumptions are listed at the end.

## Why the PM proposal fails

- It is the fail-open default the skill names as an anti-pattern. SendGrid is the cited example: omit scopes and you get Full Access.
- Almost nobody unticks boxes in an advanced panel. Only the big customer gets read-only. Every other leaked key still carries meter reads, tariff writes, billing and user management.
- Billing changes and user management through a bare API key is the OWASP API2 weakness: a key as the sole credential for a sensitive operation.

## Model to ship

**1. Scope model: coarse presets on top of fine-grained RBAC.**
- Your 40-permission RBAC flips the effort ranking. Fine-grained scoping is nearly free, so don't stop at the "coarse read/write" rung.
- Show presets first: `Read-only`, `Meter ingest`, `Tariff manager`, `Admin`.
- Group the 40 permissions by product area × read/write behind a "Custom" option. Don't show 40 raw checkboxes.
- The big customer's ask becomes one click: `Read-only`.

**2. Don't expose RBAC permission names directly.**
- Define a stable public scope vocabulary (for example `meters:read`, `tariffs:write`) and map each scope to RBAC permissions internally.
- Reason: web-app permissions are UI-shaped and you will rename them. Customers store scope names in config, and a rename breaks their keys.
- Check that every RBAC permission you map to a scope is enforceable at the API layer, not only through a session.

**3. Effective permission is the intersection, never the union.**
- A key can hold only permissions its creator holds. This prevents privilege escalation.
- At request time, check key scopes ∩ owner's current RBAC. When the owner loses a role, the key loses that power without a manual revoke.

**4. No fail-open default.**
- Creation requires an explicit choice. Preselect `Read-only` or nothing, never `Admin`.
- `Admin` is allowed but explicit, labeled "full account access", restricted to admin-role creators, with a default expiry.
- Missing or empty scope returns an error. It never means "everything".

**5. Keep the dangerous scopes off keys in v1.**
- Billing changes and user management: not grantable to API keys. They stay in the dashboard (session + 2FA) or move to OAuth later.
- Tariff writes: allowed, but only as an explicit scope. Consider a short mandatory expiry.
- This follows the skill's rule that a key must not be the sole credential for a sensitive operation.

**6. Split by environment.**
- One key per service per environment.
- Encode type and environment in the prefix, for example `vm_live_` / `vm_test_`, plus a distinct restricted-key class, so scanners and humans can tell them apart.

**7. Enforcement and lifecycle.**
- Return `401` for an invalid key and `403` for a valid key that lacks the scope.
- Narrowing scopes in place is fine. Widening requires a new key through the atomic "roll" flow, with an audit log entry.
- Mandatory expiry on every key, with a default of 365 days. Record each key's name, owner, scopes and consuming service.
- Show scopes and `last_used_at` in the key list.
- Prefer service-account or org-owned keys for production, so keys don't depend on one employee.

## Existing single-key customers

- Do not break them. Relabel existing keys as `Legacy full-access` and show that badge in the dashboard.
- Notify customers and encourage a split: create scoped keys, cut over, then revoke the old one via the dual-key overlap in the rotation runbook (routine rotation: 24h-7d overlap, deactivate before delete, verify zero traffic).
- Stop issuing new unscoped keys on a set date.
- Look at how existing keys are stored. If any are plaintext, fix that in the same project: hash with SHA-256, show once, and keep a key prefix column for lookup.

## Rollout and estimates

These are rough, assuming RBAC enforcement can be called from the API layer.

1. **Phase 1, about 2-3 weeks:** public scope vocabulary, scope-to-RBAC mapping, enforcement middleware with the intersection rule, presets with `Read-only` first, `403` behavior, and legacy relabel. This satisfies the big customer.
2. **Phase 2, about 2 weeks:** custom picker, expiry and warnings, the roll flow, and the audit log.
3. **Later:** service accounts, and OAuth for billing and user management if customers need it.

## Success gates

- Every live key has an owner, scopes, and an expiry or a documented exemption.
- Share of new keys created non-`Admin`. Baseline it in month 1 and track it up.
- Share of keys that are `Legacy full-access`. This should trend down.
- One real key rolled end-to-end with zero downtime.

## Assumptions

- This is a retrofit. Today's storage is unknown, and I assumed plaintext is possible.
- Only first-party customers call the API, so no third-party OAuth is needed yet.
- No compliance regime is confirmed. If the big customer needs SOC 2, the audit log and expiry in Phase 2 become required.
- Your RBAC can be enforced at the API layer.

**Next (2 minutes):** write the list of 40 permissions and mark each one "safe for a key", "key with expiry", or "dashboard only". That list is the core of the scope vocabulary.