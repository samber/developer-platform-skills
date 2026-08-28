# Policy document template

The skill's deliverable is one written policy document integrators and internal teams can both read. Draft it section by section, validating each with the user before moving on. Every bracketed value is a decision the interview and workflow steps produced - nothing here is a default to copy blind.

## Skeleton

```markdown
# [Product] API versioning and deprecation policy

## Scope

- Surfaces covered: [REST API vX endpoints / GraphQL schema / webhooks event schemas].
- Surfaces explicitly NOT covered and why: [e.g. unversioned admin endpoints "may change
  at any time" - state the carve-out up front, as Shopify does].
- Client SDKs/libraries version separately under SemVer; see [SDK policy location].

## Version scheme

- Scheme: [URI major version /v1/ | header YYYY-MM-DD | date-based account-pinned | none:
  additive-only evolution].
- Default when no version is specified: [error (LinkedIn-style, recommended) | pinned
  account version (Stripe-style)]. Unversioned access is never served.
- Release cadence: [as-needed | quarterly | ...].

## Breaking-change definition

- Breaking (new version required): removing/renaming a field or endpoint, changing a
  field's type, removing an enum value, adding a required request parameter, changing
  the status code or content type for the same scenario, [domain-specific additions].
- Non-breaking (ships into the current version): new resources, new optional request
  parameters, new response properties, property-order changes, opaque-string format
  changes, new webhook event types, new values in enums declared open: [list of open enums].
- Not contractual (may change without notice): message/detail text, field ordering,
  timing, [others].
- Security exception: any version may be patched for critical security or privacy fixes,
  with notice via [channel].

## Support windows

- Each version is supported for at least [12 | 24] months from [its release | the next
  version's release | deprecation announcement] - the clock definition is part of the policy.
- At most [2-3] versions are active concurrently.
- Sunset dates, once announced, are firm. [Partner-specific windows live in the SLA.]

## Deprecation process

Stages: announce → deprecate → sunset → removal. Never announce-to-removed directly.

- Announce: [changelog + dashboard + email], at least [window] before sunset.
- Deprecate: `Deprecation` header (RFC 9745) on all deprecated-version responses;
  `Sunset` header (RFC 8594) once the date is firm; `Link: rel="successor-version"`;
  `deprecated: true` in the OpenAPI document.
- Targeted outreach: [email to accounts still calling the version | in-response warnings]
  at [T-6mo, T-3mo, T-1mo].
- Migration support: a migration guide per version transition, [tooling/codemods where
  feasible], [support channel].

## Enforcement at sunset

- [Hard cutoff: requests to a retired version return `410 Gone` with a descriptive error
  body and a successor link | Fall-forward: requests are served by the oldest accessible
  version - documented here loudly because it is silent at call time].
- Grace period: [30 days] of `410 Gone` before any full removal.

## Governance

- Breaking-change detection: [linter/diff tool] in CI on every spec change.
- Approval: no breaking change ships without [named approver | review board] sign-off.
- [Board charter location, meeting/office-hours cadence, escalation path.]

## Measurement

- Breaking-change count per year (target: ≤ [2]).
- Deprecated-version traffic share, reviewed [monthly] during any active deprecation.
- Versions removed only at [zero | accepted-residue] observed traffic.
- Slipped sunset dates (target: 0).
```

## Validation order

Present and confirm sections in this order - each depends on the ones before it: scope → scheme → breaking-change definition → windows → process → enforcement → governance → measurement. A user who changes the scheme after approving the windows invalidates the windows; walking backward is normal, silently reconciling is not.

## GraphQL variant

For a continuous-evolution policy, replace "Version scheme" and "Support windows" with:

- **Evolution rules:** all changes additive; fields are individually deprecated via `@deprecated(reason: "...")` naming the replacement field.
- **Field-rollover strategy** (Apollo's term - write it down, don't improvise per field): deprecation marker → usage telemetry per deprecated field → removal only at zero observed consumers → [minimum time floor, if any].
- Everything else - breaking-change definition (applied field-level), communication channels, governance, measurement - keeps the same shape.
