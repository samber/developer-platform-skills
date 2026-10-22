# Orrery OAuth scope taxonomy (draft v1)

## Decisions to make before building

1. **Don't redefine `full_access` as read-only.**
   - Today it grants everything, so any of the ~120 apps that mutate would start getting 403s at cutover. You'd be changing the 120 registrations' behavior without touching them.
   - If you exempt existing apps to avoid the breakage, the same string means two things (read-only for new apps, read-write for old ones). That makes audits and consent screens unreliable.
   - Instead, freeze `full_access` as a deprecated alias for "every `:read` and `:write` scope". Behavior stays identical, the 120 registrations stay untouched, and you stop issuing it to new apps.
   - If you still want the redefinition, first measure how many of the 120 have called a mutating endpoint in the last 90 days. Those apps are your breakage list.

2. **Don't defer the flavour mapping.**
   - Scopes are the authorization boundary, and the two flavours have different ceilings:
     - A user-delegated token is capped by scope and by what that user can do.
     - An integration token has no human ceiling, so its scope is the only limit.
   - Adding permissions later is cheap. Revoking permissions people already hold is expensive. So ship the conservative default below and loosen it when usage data supports that.
   - Usage data from an unrestricted launch would also tell you little about what apps need, because apps request whatever is allowed.

## Scopes

Format: `<resource>:<action>`. There are four resources and two actions, so eight scopes. Actions:
- `read` is get and list.
- `write` is create, update, and delete.

| Scope | Grants |
|---|---|
| `projects:read` | View projects, including membership and metadata |
| `projects:write` | Create, edit, archive, and delete projects, and change membership |
| `tasks:read` | View tasks |
| `tasks:write` | Create, edit, assign, and delete tasks |
| `comments:read` | View comments |
| `comments:write` | Post, edit, and delete comments |
| `timesheets:read` | View time entries |
| `timesheets:write` | Create, edit, and delete time entries |

**Rules**
- `X:write` implies `X:read`. Registration and consent screens show only the stronger one.
- There are no cross-resource implications. A token with `tasks:read` doesn't get `projects:read`. Expanded or embedded project objects need `projects:read`, and otherwise return only the ID.
- Comments inherit visibility from their parent. A comment on a task or project is visible only if the app could also read that parent, so a token with `comments:read` but not `tasks:read` can't read task comments.
- Delete stays inside `write` for v1. If you later need a destructive tier, add `projects:admin` rather than splitting every resource.

## Bundles (convenience, not primitives)

| Bundle | Expands to |
|---|---|
| `read_all` | The four `:read` scopes |
| `write_all` | The four `:write` scopes, which imply the `:read` scopes |
| `full_access` (legacy) | Same as `write_all`. Frozen, no new grants, and shown as deprecated in the developer console |

This replaces your `full_write` idea. `read_all` and `write_all` mean what their names say, and nothing is named "full" while meaning less than everything.

## Flavour matrix (conservative default)

| Scope | Integration (app as itself) | User-delegated (app as a person) |
|---|---|---|
| `projects:read` / `:write` | ✅ | ✅ |
| `tasks:read` / `:write` | ✅ | ✅ |
| `comments:read` | ✅ | ✅ |
| `comments:write` | ✅ authored as the app | ✅ authored as the user |
| `timesheets:read` | ✅ org-wide, needs workspace-admin consent | ✅ the user's own entries only |
| `timesheets:write` | ❌ not at launch | ✅ the user's own entries only |

**Why timesheets differ**
- Time entries belong to a person. An integration has no identity to book time against.
- Allowing integration writes would mean "write for anyone". That is a payroll-fraud surface and shouldn't ship by default.
- If a real use case appears, add `timesheets:write_any` as a separate scope with admin consent. Don't widen `timesheets:write`.

**Consent**
- Integrations are installed by a workspace admin.
- User-delegated tokens are approved by the individual user.
- For user tokens, the effective permission is the scope intersected with the user's own permissions.

## Migration for the ~120 existing apps

1. **Instrument now.** Log per token which scopes' endpoints are actually called. This gives you the usage data you wanted, without opening the scope space first.
2. **Classify at 90 days.**
   - Apps with zero mutations are candidates for server-side narrowing to `read_all`.
   - Mixed apps get a suggested minimal scope set.
3. **Notify the app owners** with a dated deadline for the read-only candidates, and offer opt-out.
4. **Narrow server-side** for the apps that didn't object. No re-registration is needed, since you map `full_access` to a reduced grant per app.
5. **Sunset `full_access`** on a published date, and keep it working until then.

## Open questions

- Is there a separate permission for webhooks or event subscriptions? They aren't covered above.
- Should deletes of user-owned resources stay in `write`, given your soft-delete convention?
- What share of the 120 apps are integrations versus user-delegated? That decides how disruptive the timesheet restriction is.