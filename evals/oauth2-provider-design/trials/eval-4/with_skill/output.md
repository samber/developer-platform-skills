# Orrery OAuth scope taxonomy (draft v1)

I followed `oauth2-provider-design` (step 2, scope taxonomy and consent) plus its scope-archetypes and consent-screen references. I did not read the other references (protocol baseline, app verification program). I also did not ask the skill's clarifying questions, because the task needs a single deliverable. My assumptions are at the end.

## Decision up front: don't redefine `full_access`

Your plan has two parts. I'd keep `full_write` out and not redefine `full_access` as read-only. Both break rules this skill treats as non-negotiable:

- **Scopes are additive-only.** Changing what `full_access` means silently changes what ~120 existing consents authorize. Every write-capable app breaks on the day you flip it.
- **Old and new grants become indistinguishable.** Your grant store and audit logs would hold the same string with two meanings. You could no longer tell what a given `full_access` grant meant when it was issued.
- **`full_access` meaning "read-only" is a trap.** Every new developer will assume the name is true.
- **`full_write` is a second catch-all.** The skill deletes that pattern. One broad scope per direction is the same failure mode as GitHub's classic `repo`.

Your real goal is to avoid touching the 120 registrations. You can still meet it:

- **Freeze `full_access`.** It keeps today's exact meaning, which is everything the token can do across the four current resources.
- **Close it to new requests.** New registrations and new authorization requests can't ask for it.
- **Add the granular scopes below next to it.**
- **Migrate on a schedule, below.** Existing apps keep working untouched until you choose to sunset it.

## Scope list

The pattern is `resource:action`, using the same nouns as the API.

- `read` means read only.
- `write` means create and update. It never includes delete.
- `delete` is its own scope. Splitting it out of `write` later would narrow an existing scope, which breaks the additive-only rule. So decide now.

That gives 12 scopes plus the frozen legacy one.

| Scope | Meaning |
|---|---|
| `projects:read` / `projects:write` / `projects:delete` | Read, create or update, delete projects |
| `tasks:read` / `tasks:write` / `tasks:delete` | Same for tasks |
| `comments:read` / `comments:write` / `comments:delete` | Same for comments |
| `timesheets:read` / `timesheets:write` / `timesheets:delete` | Same for time entries |
| `full_access` (legacy) | Frozen. All 12 scopes above that are valid for the token's flavour. Never grows to cover new resources. Not requestable by new apps. |

Rules to put in the scope registry:

- **Immutable definitions.** Each scope has one definition, a creation date, and a change log. A definition is never edited.
- **Read is the default.** Registration and consent flows start read-only.
- **New resources get new scopes.** `full_access` never extends to them.

## Token-flavour binding (decide now)

You proposed deciding this after seeing usage. I'd decide it now, for two reasons:

- **Slack's migration guidance.** Changing a scope's token-type binding later "requires reauthorization from every user".
- **Usage can't answer it.** With every app holding `full_access`, scope usage tells you nothing about which flavour a scope belongs to.

You can narrow now and widen later, because adding a binding is additive. You can't narrow after launch. So start conservative.

Terms: *user token* means an app acting as a signed-in person. *Integration token* means an app acting as itself.

| Scope | User token | Integration token |
|---|---|---|
| `projects:read`, `tasks:read`, `comments:read` | ✅ | ✅ |
| `projects:write`, `tasks:write`, `comments:write` | ✅ | ✅ |
| `tasks:delete`, `comments:delete` | ✅ | ✅ |
| `projects:delete` | ✅ | ❌ |
| `timesheets:read` | ✅ | ✅ |
| `timesheets:write`, `timesheets:delete` | ✅ | ❌ |

Semantics that must be written into each scope's definition:

- **User tokens never exceed the person.** A user token can only do what that person can do in the Orrery UI. Delegated access is bounded by the user.
- **Same name, different actor.** `comments:write` posts as the person on a user token and as the app on an integration token. This is Slack's `chat:write` pattern. Record the actor in the audit log.
- **Integration tokens are org-wide.** Every integration-token scope requires an org admin to install. A single user's "yes" is not enough. This is Microsoft's application-permission model.
- **Timesheets stay narrow.** `timesheets:read` on an integration token reads everyone's hours and needs admin consent. Writing time for other people is a different action, so it gets its own scope later, for example `timesheets:write_for_others`. Adding that is additive. Don't overload `timesheets:write`.
- **Integration deletes are limited to sync cases.** `tasks:delete` and `comments:delete` are allowed on integration tokens for sync tools. `projects:delete` is not.

## Consent copy (one sentence per scope)

The consent screen shows the plain sentence, never the raw string. Write the copy when the scope is created. A scope you can't explain in one sentence is a design smell.

| Scope | User consent screen | Admin install screen |
|---|---|---|
| `projects:read` | View the projects you can access | View all projects in your workspace |
| `projects:write` | Create and edit projects as you | Create and edit projects as the app |
| `projects:delete` | Delete projects as you | (not offered) |
| `tasks:read` | View tasks you can access | View all tasks in your workspace |
| `tasks:write` | Create and edit tasks as you | Create and edit tasks as the app |
| `tasks:delete` | Delete tasks as you | Delete tasks as the app |
| `comments:read` | Read comments you can access | Read all comments in your workspace |
| `comments:write` | Post and edit comments as you | Post and edit comments as the app |
| `comments:delete` | Delete comments as you | Delete comments as the app |
| `timesheets:read` | View time entries you can access | View every member's time entries |
| `timesheets:write` | Log and edit time entries as you | (not offered) |
| `timesheets:delete` | Delete time entries as you | (not offered) |

Consent mechanics:

- **Partial grants.** Users can approve some scopes and decline others.
- **Server-side diff.** Return the granted set explicitly and diff it against the request. Never assume they match.
- **Net-new only on re-consent.** Incremental requests show only the new scope, not everything already granted. Test this explicitly.
- **No conversion numbers.** Don't cite consent drop-off percentages. No rigorous study exists.

## Review tiers per scope (proposal)

This is a proposal, because the data-sensitivity answer is open (question 3 below).

| Tier | Applies to | Requirement |
|---|---|---|
| 1 | Every listed app | Publisher identity verification |
| 2 | Any `:write` or `:delete` scope | Tier 1 plus self-attestation |
| 3 | `timesheets:read` on an integration token (bulk, other people's hours) | Tier 2 plus third-party security assessment |

Other review rules:

- **Runtime enforcement.** Reject any scope request that isn't a subset of what the app declared and had approved at registration.
- **Legacy apps.** Their declaration is `full_access` until they migrate.
- **Badges.** Keep identity, attestation, and assessment visually distinct. Don't show one combined checkmark.

## Migrating the 120 apps

1. **Freeze first.** Close `full_access` to new requests and mark it deprecated in the docs.
2. **Derive a suggested scope set per app.** Use API logs of HTTP method by endpoint for each app, not scope telemetry. Apps that only issue GETs map to read scopes, and apps that mutate map to the matching write scopes.
3. **Notify app owners** with their suggested set. Set the notice window and sunset signalling under your API versioning policy. I'd allow at least 6 months, but that's your call.
4. **Stage the cutover.** Let apps re-consent to the granular scopes voluntarily, and track the share migrated. Then pick a sunset date and enforce it.
5. **Expect re-consent.** Changing an app's scope set invalidates its refresh tokens and sends users through consent again. Batch the changes so users aren't prompted twice.

## Assumptions and open questions

Please confirm these. Each one changes the design:

1. **Greenfield or retrofit?** I assumed retrofit: ~120 live apps and unknown refresh rotation. Is rotation on?
2. **Do today's 120 apps hold user tokens, integration tokens, or both?** This determines how `full_access` maps per flavour.
3. **Do timesheets carry rates, pay data, or regulated working-time records?** If yes, Tier 3 may cover more than `timesheets:read`.
4. **Who approves an install today?** I assumed users only, with admins newly gating integration tokens. If admins already approve apps, the admin screen is a refinement, not new.
5. **Is `delete` as its own scope acceptable?** If you'd rather fold it into `write`, say so now. It can't be split out later.