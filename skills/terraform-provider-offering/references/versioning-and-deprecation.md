# Provider versioning, deprecation and upgrade guides

Load at workflow step 8, and whenever a change touches an existing schema.

## Contents

- What forces which version bump
- Major-release cadence
- Deprecation then removal
- Rename recipes
- Changelog format
- Upgrade guides
- Running a major

## What forces which version bump

| Bump | Provider changes that require it |
| --- | --- |
| MAJOR | making an Optional attribute Computed-only; a validation stricter than the API; removing or renaming a resource, data source or attribute; changing authentication or configuration precedence; changing the import ID or resource ID format; an incompatible type change (List to Set or back, number to string); a format change (epoch to RFC 3339); changing a default incompatibly with existing state; adding a default that differs from the API default; removing a diff suppression or normalization |
| MINOR | deprecating anything; a new resource, data source, function or attribute; a new validation that rejects only values the API already rejects; an alias; a compatible type change (integer to float) |
| PATCH | fixing CRUD or drift detection; Required to Optional when the API does not need the field |

When unsure, ask: "Does an unchanged configuration plus existing state produce a non-empty plan, an error, or a different real object after upgrading?" Any yes is MAJOR.

## Major-release cadence

- Release majors at most once a year. Every major costs every user an upgrade project, and users stuck on an old major stop receiving fixes.
- Stage majors behind a feature flag or an opt-in beta channel (prerelease tags `vN.0.0-beta1`), and say whether the opt-in changes state irreversibly.
- A preview API surface can ship in a separate beta provider (`<name>-beta`) that allows breaking changes in minors, keeping the GA provider's promise intact.

## Deprecation then removal

1. Set `DeprecationMessage` on the attribute, resource or data source, phrased as the action to take: "Use `new_name` instead. `old_name` will be removed in v5."
2. Add a NOTES entry to the changelog and a line in the next upgrade guide.
3. Ship it in a MINOR.
4. Remove it only in the next MAJOR, with a BREAKING CHANGES entry.

Never remove in a minor, even for an attribute "nobody uses": the Registry cannot tell you who pins it.

## Rename recipes

- Required attribute: make the old one Optional, add the new one as Optional, deprecate the old one, add `ExactlyOneOf` on the new one pointing at the old path, handle both in Create and Update with null checks. Remove the old one at the next major.
- Optional attribute: add the new one, deprecate the old one, `ConflictsWith` between them, read whichever is set.
- Computed attribute: populate both from Read until the major.
- Resource or data source: ship the new type beside the old one, deprecate the old type, implement a state mover so users write a `moved` block instead of importing. Never force a wave of imports to stay on a supported major.

## Changelog format

`CHANGELOG.md` at the repo root:

```
## 3.4.0 (Unreleased)

NOTES:

* resource/acme_widget: `color` is deprecated, use `colour`. Removal in 4.0.0. [GH-412]

FEATURES:

* **New Resource:** `acme_widget_policy` [GH-405]

ENHANCEMENTS:

* resource/acme_widget: add `labels` attribute [GH-398]

BUG FIXES:

* data-source/acme_project: no longer errors when the project has no members [GH-401]
```

- Categories in order: BREAKING CHANGES (majors only), NOTES, FEATURES, ENHANCEMENTS, BUG FIXES.
- Entry shape: `* <subsystem>: <message> [GH-<number>]`, subsystem = `resource/<type>`, `data-source/<type>`, `provider`.
- Released headers read `## 3.4.0 (October 2, 2026)`.
- Busy repos collect per-PR changelog fragments and assemble them at release, which removes merge conflicts on one file.

## Upgrade guides

Publish `docs/guides/version-<N>-upgrade.md` with every major:

- One section per breaking change: what changed, why, before and after HCL, and the exact command when state is involved (`moved` block, `terraform state replace-provider`, import).
- Lead with the changes that produce a diff or an error on an unchanged configuration.
- Name the minimum Terraform and OpenTofu versions the major supports.

## Running a major

1. Land breaking changes on the default branch behind a feature flag or opt-in setting, never on a long-lived major branch that drifts from the releases users run.
2. Release a final minor of the old major that deprecates everything the new major removes.
3. Publish the upgrade guide with the first beta.
4. Run state-upgrade tests from the last release of every supported major.
5. Keep shipping security and critical fixes on the previous major for a stated window.
6. Track the share of downloads still on the old major; extend the window rather than abandon a large cohort.
