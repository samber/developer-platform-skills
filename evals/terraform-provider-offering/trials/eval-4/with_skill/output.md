# Larkspur provider: is 3.2.0 fine?

**No.** Four of your five changes need a major release (4.0.0). Shipping them in 3.2.0 breaks the "unchanged config plus existing state" rule. The skill's test is whether an unchanged configuration plus existing state gives a diff, an error, or a different object after upgrading. Any yes means major.

The fifth change, the `region` sunset, is a deprecation and does belong in a minor.

## Verdict per change

| # | Change | Bump | Why |
|---|---|---|---|
| 1 | `colour` → `color` | **MAJOR** as written | A rename is a removal. Old configs still say `colour`. |
| 2 | `subjects` list → set | **MAJOR** | List-to-set is an incompatible type change. It needs a schema version bump and a state upgrader. `subjects[0]` references also break. |
| 3 | Drop `legacy_sync` | **MAJOR** | Removal. Telemetry cannot see everyone, because the Registry cannot tell you who pins an old config. Never remove in a minor, even for an attribute "nobody uses". |
| 4 | Split `larkspur_role` + `larkspur_role_binding`, "users just re-import" | **MAJOR** as written | Removing attributes from `larkspur_role` is a removal. A forced re-import is the mass-import failure the skill warns about. |
| 5 | `name` rejects spaces | **MAJOR** | The API still accepts spaces, so this is validation stricter than the API. Existing objects with spaces would error at plan. |
| 6 | `region` sunset in 6 months | **MINOR** (deprecation) | Deprecate it one minor ahead of the API sunset. Remove it in the next major. |

## Plan: two releases

### 3.2.0 (minor, now): additive and deprecating only

1. **`color`**: add `color` as Optional, with `ConflictsWith` against `colour`. Deprecate `colour` with the message "Use `color` instead. `colour` will be removed in v4." Read whichever one is set. Do not populate both on Read, or `-generate-config-out` produces invalid HCL.
2. **`legacy_sync`**: set a `DeprecationMessage`. Keep the attribute working.
3. **`region`**: set a `DeprecationMessage` that names the API sunset date. This is the "one minor ahead" alignment with the API team's sunset.
4. **`larkspur_role_binding`**: ship the new resource beside the old one, with import support. Deprecate the inline binding attributes on `larkspur_role`.
   - Add a conflict warning in both docs pages. Offering an inline list and an attachment resource for the same collection makes them fight on every apply.
   - Ship a state mover on `larkspur_role_binding` so users write `moved` blocks (Terraform 1.8+, OpenTofu 1.10+). Nobody has to re-import.
5. **`subjects` and `name`**: no change in 3.2.0.
   - Document that `subjects` becomes a set in 4.0.0.
   - Document that `name` will reject spaces in 4.0.0, if you still want that rule (see decisions below).

### 4.0.0 (major, later): everything breaking, once

- Remove `colour`, `legacy_sync` and `region`, and the inline binding attributes on `larkspur_role`.
- Switch `subjects` to a set. Bump the schema `Version` and write a state upgrader from every released schema version straight to the current one. The framework does not chain them.
- Add the `name` validator, if you keep it.
- Publish `docs/guides/version-4-upgrade.md`. Cover each change with before and after HCL, and the exact commands for state (`moved`, no import). Lead with the changes that error on an unchanged config.
- Stage it as `v4.0.0-beta1` behind an opt-in. State upgrade tests: apply with the last 3.x, plan with the 4.0 build, expect no changes.
- Timing: one major per year at most, so batch all of the above. Land it at or after the API's `region` sunset, which is about 2027-04-24 if the six months run from today. Keep security fixes flowing on 3.x for a stated window.

## Decisions for you

1. **`name` validation.** The UI forbids spaces but the API accepts them, so this is a UI rule rather than an API contract. Existing objects with spaces would fail at plan. Options:
   - Ship it in 4.0.0 and list it under BREAKING CHANGES.
   - Drop it and fix the UI/API instead.
   - I lean toward dropping it unless the API team will reject spaces. Once the API rejects them, the provider rule becomes a minor.
2. **`subjects` as a set.** Confirm with the API team that order never matters. The skill says the choice is permanent. If any ordered meaning exists, ask for a position field instead.
3. **`larkspur_role_binding` semantics.**
   - Confirm it has a stable server-assigned ID, and decide its import grammar.
   - Decide whether the split is a state mover or an upgrade inside `larkspur_role`. Either way, no user should re-import.

## Changelog

Your plan is a bulleted list under `## Changes`. The skill's format is `CHANGELOG.md` with a versioned header and ordered categories, and entries shaped `* <subsystem>: <message> [GH-n]`. BREAKING CHANGES appear in majors only. Draft for 3.2.0:

```
## 3.2.0 (Unreleased)

NOTES:

* resource/larkspur_policy: `colour` is deprecated, use `color`. Removal in 4.0.0. [GH-xxx]
* resource/larkspur_policy: `subjects` becomes a set in 4.0.0. Review any `subjects[N]` references. [GH-xxx]
* resource/larkspur_group: `legacy_sync` is deprecated. Removal in 4.0.0. [GH-xxx]
* resource/larkspur_role: inline binding attributes are deprecated, use `larkspur_role_binding`. Removal in 4.0.0. [GH-xxx]
* provider: `region` is deprecated ahead of the API sunset on <date>. Removal in 4.0.0. [GH-xxx]

FEATURES:

* **New Resource:** `larkspur_role_binding` [GH-xxx]

ENHANCEMENTS:

* resource/larkspur_policy: add `color` attribute [GH-xxx]
```

I assumed the current release is 3.1.x. I also assumed your minimum Terraform and OpenTofu versions are at least 1.10, for the `moved` state mover. If either assumption is wrong, the mover step changes. Record the chosen path, the resource map and this deprecation schedule in your `developer-platform-context.md` memory file, so 4.0.0 checks against it instead of re-deciding.