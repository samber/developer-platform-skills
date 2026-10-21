# Versioning, migration and deprecation

Source: docs.zapier.com integrations/manage (versions, version-lifecycle-states, planning-changes, migrate, automatic-migrations, deprecate) and its platform changelog.

## Classify the change

| Change | Class | Ship it as |
| --- | --- | --- |
| New trigger, action, search, optional field, label, help text, sample | non-breaking | minor or patch |
| Subscribe/unsubscribe internals, auth token request, test call | non-breaking | patch |
| Required input field added or changed | depends | default it, or additive step |
| Input field type | breaking, blocked at promotion | additive step, or new major |
| Perform function, perform list, middleware | depends | test against live Zaps first |
| Rename a step key, input key or output key | breaking | new step under new key, hide old |
| Change output structure or remove output keys | breaking | new step, or transform the new API shape back to the old one in code |
| Polling <-> REST hook | breaking | twin step under a new key, hide old |
| Polling sort order, page contents, or primary-key format | breaking in effect: old dedupe memory fires every unseen item | twin step under a new key, hide old |
| Auth scheme, auth field key, new required auth field | breaking | new major; ask Zapier about assisted connection migration first |

Promotion compares the new version's schema with the promoted one and blocks most breaking changes inside the same major. It does not catch renamed or removed output keys, changed response structure or changed perform behavior: diff those by hand.

## Lifecycle

- Private: editable, shareable, the default for every new version.
- Promoted: default for new Zaps, directory-visible, frozen. One at a time; the previous one becomes Available.
- Available: keeps working for its Zaps.
- Legacy: hidden from new Zaps, keeps working, never a migration target.
- Deprecating -> Deprecated: on the date, unmigrated Zaps pause, the version cannot be tested or turned on, users get a fixed "Zaps paused" email.

## Migration and push rules

- Migration only within one major: `1.4.0 -> 1.5.0` yes, `1.9.0 -> 2.0.0` never.
- Unlabelled versions push in sequence: no skipped predecessor, no version inserted behind a newer one on its line. Iterate on labelled versions (`1.3.0-beta`); those cannot be migrated to.

## Release procedure

1. Clone the promoted version; make the change; run validation.
2. Share the clone with internal or friendly accounts. CLI only: canary 5-10% of traffic for 30-60 minutes, non-breaking changes only, and stop if errors rise more than 5%.
3. Promote.
4. Migrate by percentage (5% first), watch the Monitoring logs for new errors, then migrate the rest. With automatic migrations on (the default, tied to the Integration Maintenance Program), promotion moves a subset, marking the old version legacy moves most, deprecation moves all.
5. Mark older Available versions legacy one at a time, oldest first, so users land on the promoted version.
6. Deprecate a version only when it must stop working: date 3 weeks to 1 year out, user email 14 days before, delete only at zero users including paused Zaps and connections.

## Keeping triggers alive through API changes

- Treat step keys, output keys and output shape as a public contract, separate from the API's own versioning.
- Pin the API version the integration calls; when the API changes shape, map the new response back to the old output in the perform code.
- Before sunsetting an API endpoint, find every step that calls it and ship the replacement step first. Near the sunset date, promote a version whose old step throws a clear error naming the replacement step.
- Drafts migrate only when published, so a user can republish an old draft onto an old version; keep old versions working until deprecation.

## Leaving Zapier

Revert the integration to private (via developer support), then deprecate every version except the latest still in use. Zaps calling shut-down endpoints error and eventually turn off.
