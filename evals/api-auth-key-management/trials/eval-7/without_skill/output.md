# Recommended scoping model for Voltmesh API keys

**Ship coarse, resource-level scopes with three presets. Make new keys least-privilege or force an explicit choice. Don't copy the 40-permission web RBAC, but reuse its enforcement layer.** Reject the PM's "full-access by default, untick in an advanced panel" design.

## 1. Why the PM's default is the wrong call

- Most customers never open an advanced panel. In practice every new key would stay a root key, so the read-only customer gets a feature the rest of your base never uses.
- A leaked full-access key can rewrite tariffs, change billing and manage users. A leaked meter-read key can only leak readings.
- Defaults are your real security posture. Opt-out scoping gives you opt-in security.
- The big customer's request is a procurement signal. Others will follow, and a hidden checkbox panel is weak evidence in a security review.

The PM is right about one thing: the simple path must stay simple. Presets deliver that without making root the default.

## 2. Scope model

Use `resource:action` strings, with `read` and `write` as the only actions at first.

| Scope | Covers |
|---|---|
| `meters:read` | Meter and reading queries, usage, exports |
| `meters:write` | Register, update and retire meters, push readings (for ingest) |
| `tariffs:read` / `tariffs:write` | Tariff schedules |
| `billing:read` / `billing:write` | Invoices, plan and payment changes |
| `users:read` / `users:write` | Account members, invites and roles |
| `keys:write` | Create and revoke other keys |

**Presets** (what 95% of customers will pick):

- **Read-only**: every `*:read` except possibly `billing:read` and `users:read`. Decide whether billing data counts as "read-only safe". I'd exclude both by default, since "read-only" usually means "meter data".
- **Metering integration**: `meters:read` plus `meters:write`. This fits a data pipeline pushing or pulling readings.
- **Full access**: all scopes. It exists but is never pre-selected.

An "Advanced / custom" picker shows the individual scopes. The presets are the primary path and the picker is the escape hatch.

Rules:

- **Write does not imply read.** Keep the two explicit, and let the UI auto-tick read when write is ticked.
- **`users:*`, `billing:write` and `keys:write` never appear in a preset except Full access.** A key that can mint keys can escalate itself.
- **The key's effective permissions can't exceed its creator's.** Intersect with the creator's web RBAC role at creation. Re-check at request time if the creator is demoted or removed, or the key will outlive the access of the person who made it.

## 3. Why not expose the 40 RBAC permissions

- **They model people, not integrations.** They are built for UI actions and roles, and are probably coupled to screens and workflows. Customers shouldn't have to learn them to create a key.
- **They would freeze your internals into a public contract.** Renaming or splitting a web permission would become a breaking API change.
- **40 checkboxes produce misconfigured keys.** People will either tick everything or break their integration and tick everything afterwards.

Where RBAC does help is enforcement. Don't build a second authorization engine. Map each public scope to a bundle of internal permissions, for example `tariffs:write` → `{tariff.create, tariff.update, tariff.delete, ...}`, and let the key authorize through the same check the web app uses. You keep one policy engine and a stable public vocabulary on top.

## 4. Enforcement requirements

1. **Deny by default.** Every endpoint declares its required scope. For scoped keys, an endpoint with no declaration returns 403. Otherwise any endpoint added later is silently open to every key.
2. **Derive the scope from the endpoint, not only the HTTP verb.** Check for GET-style endpoints that cause side effects, such as report generation, exports that email, or "recompute" calls. These should need a write scope.
3. **Return a useful 403.** Use `insufficient_scope` and name the required scope. That is a support-ticket killer for read-only keys.
4. **Show scopes everywhere.** Show them in the key list and in audit logs, and record the scope used on each denied call.

## 5. Migration and compatibility

- **Existing keys stay full-access.** Grandfather them, label them "Legacy: full access" in the UI, and offer a "restrict this key" action. Never silently narrow keys already in production.
- **Dashboard:** the creation flow forces a preset choice, with no pre-selected radio button. If you must pre-select one, make it Read-only.
- **API-created keys:** if `scopes` is omitted, you have a breaking-change dilemma. Treat omitted scopes as full access for a fixed deprecation window (say 6 months) with a warning header and email to key owners. Then require an explicit `scopes` field.
- **Tell customers rotation is the fix.** To get a read-only key, they create a new one and revoke the old one.

## 6. Add alongside, because the big customer will ask next

- **Expiry and rotation:** an optional expiry date and an overlap period for rotation.
- **Last-used timestamp and an audit log** for key actions.
- **Per-site or per-meter restrictions.** Design the scope grammar to allow `meters:read:site=<id>` later. Don't build it now, but don't paint yourself into a corner.
- **IP allowlists**, as an optional restriction on the key.

## 7. Open questions to confirm before building

1. Is `billing:read` safe for "read-only"? Check with the requesting customer.
2. Do any "read" endpoints in your API actually mutate state? This needs an audit before you declare scopes.
3. Can ingest keys (devices pushing readings) be a distinct key type? Meter gateways are a typical high-volume, low-privilege case, and `meters:write`-only keys are worth supporting.
4. How are today's keys tied to users? Whether keys are account-owned or user-owned decides how to handle the creator-ceiling rule when someone leaves.

## Summary

Ship about 8 coarse scopes and 3 presets. Make creation least-privilege or an explicit choice, leave existing keys as legacy full-access, and enforce deny-by-default through your existing RBAC engine. You get the read-only keys the customer asked for, without making every new key a root key or committing your web permission model to a public API.