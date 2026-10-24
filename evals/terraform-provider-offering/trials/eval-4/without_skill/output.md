# No, 3.2.0 is not fine. Ship 4.0.0.

Terraform users pin with `~> 3.0`, so a minor release is expected to be safe to take. Every item except the `region` deprecation breaks existing configs or state, so a minor bump would break people who did nothing wrong.

## Why each change is breaking

| # | Change | Break |
|---|---|---|
| 1 | `colour` → `color` | Configs using `colour` fail with "unsupported argument". |
| 2 | `subjects` list → set | `subjects[0]` and other index references stop working. Duplicates collapse. State needs a schema version bump and an upgrader. |
| 3 | Drop `legacy_sync` | Anyone who does set it gets a hard error. Telemetry only shows users who report, so "nobody" is a guess, not a guarantee. |
| 4 | Split `larkspur_role` | Existing role resources lose attributes, and users must re-import. This alone requires a major. |
| 5 | `name` rejects spaces | Existing resources with spaces in state fail validation on the next plan, though the API accepts them. |

## Item 5 needs a second look

Rejecting spaces is a UI rule, not an API rule. Provider validation stricter than the API creates configs that the API accepts but Terraform refuses. It also locks out existing resources that already have spaces in the name. Prefer one of these:
- A warning diagnostic instead of an error.
- Validation applied on create only, never on existing state.

If you keep it as an error, list it as breaking.

## Region sunset

Do not remove `region` in this release.
- In 4.0.0, mark it `Deprecated` with a message that gives the sunset date.
- Remove it in 5.0.0, after the API actually drops it.
- Removing it early breaks users while the API still supports the field.

## Alternative: a softer path

If you want to avoid a major for now, 3.2.0 can carry only the non-breaking parts:
- Add `color` and deprecate `colour`. Keep both, with `ConflictsWith` between them.
- Deprecate `legacy_sync`.
- Add `larkspur_role_binding` alongside `larkspur_role`, and deprecate the binding fields on the role.
- Deprecate `region`.

Items 2, 4, and 5 have no soft form. The list-to-set change needs a state upgrade whichever way you ship it. So you would still need 4.0.0 for the removals and the type change. A single 4.0.0 is simpler unless you want a migration window.

## Changelog suggestion

Since you're writing the bullets under `## Changes`, prefix the breaking ones with `BREAKING:` so they stand out. Add an upgrade guide covering:
- The `colour` → `color` rename.
- Replacing index access on `subjects`.
- The role split, with the exact `terraform import` commands for `larkspur_role` and `larkspur_role_binding`.

Before release, test the 3.x → 4.0.0 state upgrade against a real state file that has a `subjects` list and an existing role.