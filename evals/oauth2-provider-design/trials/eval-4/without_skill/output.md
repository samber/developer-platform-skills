# Orrery OAuth scope taxonomy (draft)

## 1. Two decisions to change before the taxonomy

### Don't redefine `full_access` as read-only

- **It silently breaks writers.** Any of the ~120 apps that create tasks or log time today gets 403s on its next call. Their registrations stay untouched, but their behavior doesn't.
- **Existing tokens change meaning in place.** Refresh tokens and long-lived integration tokens stay valid, so the break shows up as runtime failures, not at consent time.
- **The name now lies.** "full_access = read-only" will be misread by future engineers, security reviewers, and customer admins looking at an installed-apps screen. Customer admins will see "full access" and believe the app is dangerous. They will also trust old docs that say it can write.

**Do this instead:**

- Freeze `full_access` as a legacy alias with exactly today's semantics (read, write, delete on every resource).
- Block new registrations from requesting it.
- Keep the 120 registrations untouched, with zero behavior change.
- Add the granular scopes below.
- Narrow legacy apps later, using per-app telemetry on which scopes each one actually exercises. Notify each owner, then convert their grant to the matching granular set.

If you still want a coarse "read everything" scope, give it a new honest name, `read_all`. Don't reuse `full_access`.

### Decide the flavour matrix now, not after usage data

- **Tightening later is a breaking change.** Adding a scope is free. Restricting a scope to one flavour after apps depend on it breaks those apps.
- **Usage data can't answer this.** It shows what apps do under the current all-powerful scope. It can't show what they should be allowed to do.
- **Pick conservative defaults now.** Loosening later is non-breaking.

## 2. Naming and semantics

Format: `<resource>:<action>`.

| Action | Grants |
|---|---|
| `read` | Get and list. |
| `write` | Create and update. Implies `read` on the same resource. |
| `delete` | Delete and archive. Granted separately and implies nothing. An app needing delete requests `write` too. |

Resources: `projects`, `tasks`, `comments`, `timesheets`. That gives 12 scopes.

Rules:
- A scope never grants access to a resource not in its name, so `tasks:read` doesn't expose comments embedded in a task response unless `comments:read` is also held.
- The API checks the scope on every sub-resource it returns, and redacts or omits what the token can't see.
- `full_write` is optional sugar. Define it as all `:read` + `:write`, with no `delete`, and mark it "coarse, discouraged for new apps". If you don't need the shorthand, skip it.
- `full_write` and `read_all` expand to granular scopes at token issue time, so the stored grant is always auditable.

## 3. Flavour semantics

The scope names are the same across both flavours. What differs is what bounds the scope.

| | Integration (app acts as itself) | User (app acts as signed-in person) |
|---|---|---|
| Effective access | Scope ∩ what the workspace admin granted at install | Scope ∩ that user's own permissions |
| Who consents | Workspace admin | The user (admin consent required for sensitive scopes if workspace policy says so) |
| Actor in audit log and `created_by` | The app | The user, with the app as `via` |

## 4. Scope × flavour matrix

✅ = allowed. ⚠️ = allowed with a restriction. ❌ = not issuable to this flavour.

| Scope | Integration | User | Notes |
|---|---|---|---|
| `projects:read` | ✅ | ✅ | Integration sees only projects it's been added to or granted workspace-wide. |
| `projects:write` | ✅ | ✅ | |
| `projects:delete` | ⚠️ | ✅ | Integration needs explicit admin opt-in at install. |
| `tasks:read` | ✅ | ✅ | |
| `tasks:write` | ✅ | ✅ | |
| `tasks:delete` | ⚠️ | ✅ | Same as `projects:delete`. |
| `comments:read` | ✅ | ✅ | |
| `comments:write` | ✅ | ✅ | Integration comments are labelled as the app. |
| `comments:delete` | ⚠️ | ⚠️ | User tokens can delete only their own comments unless the user holds moderator rights. |
| `timesheets:read` | ⚠️ | ✅ | Sensitive tier (see below). User tokens see only what the user may see. |
| `timesheets:write` | ⚠️ | ✅ | A user token writes entries for the user. An integration must pass an explicit `user_id` and needs admin consent. |
| `timesheets:delete` | ❌ | ⚠️ | Integrations can't delete time records. A user token can delete only the user's own unlocked entries. |

Sensitive tier (`timesheets:*`):
- Timesheets are personal work-hours data and often feed payroll and billing.
- Requires workspace-admin consent for integrations.
- Consent screen shows a distinct warning.
- Mutations on locked or approved periods are rejected regardless of scope.

## 5. Rollout

1. **Ship the granular scopes.** `full_access` is untouched and behaves as before. Nothing breaks.
2. **Close `full_access` to new registrations.** Docs mark it deprecated, with the expansion table above.
3. **Instrument.** Log, per app, which scope each request would have needed. This is cheap because the check already exists.
4. **Notify and narrow.** For each legacy app, propose a granular set from observed usage. Apps that never wrote get a read-only grant, and writers get the matching `:write` scopes. Give owners a fixed window to object.
5. **Sunset.** Set a date for removing `full_access` from the grantable list. Existing grants have all been converted by then.

## 6. Open questions

- Does the API return embedded cross-resource data today, such as comments inside a task payload? That determines how much response redaction work the "no scope bleed" rule costs.
- Do you want admin-consent policy to be per-workspace configurable for user tokens, or fixed?
- Is there a payroll or billing export that reads timesheets? It may need its own approved-integration path rather than the generic sensitive tier.