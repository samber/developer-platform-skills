# Ledgerbird API Versioning and Deprecation Policy

**Status:** Draft v1 for CTO review. **Owner:** Platform team. **Review:** annually, each January.

## Note to the CTO: where this departs from the Stripe model

This policy adopts Stripe's date-stamped versions and per-account pinning. It does not adopt "pinned forever", for three reasons:

- **The cost is in the transform layer, not the version label.** Stripe can pin forever because it has a large team maintaining a chain of per-version request and response transformers. With 3 engineers, every version we keep alive is a permanent tax on every future change.
- **Our scale does not need it.** We have 40 integrators, all under contract with named technical contacts, and we ship about one breaking change a year. We can tell each of them directly when a version is ending. Stripe cannot, which is the problem pinning solves.
- **"Standing policy for years" and "forever" conflict.** After 5 years we would be maintaining 5 or more live behaviors. That would eventually force a policy rewrite, or an unannounced exception.

The policy therefore keeps what is cheap and valuable (date versions, pinning, no surprise changes) and replaces "forever" with a fixed support window. If Ledgerbird grows to thousands of self-serve integrators, revisit the window. Do not make that change before the transform layer exists.

## 1. Scope

This policy covers the public Ledgerbird REST API used by integrators. It does not cover the dashboard UI, webhooks' delivery infrastructure, or SDK internals. It does cover webhook payload shapes, because integrators parse them.

## 2. Version scheme

- **Format:** a date, `YYYY-MM-DD`, the day the version is released. Example: `2027-03-10`.
- **Dated versions mark only breaking releases.** Non-breaking changes ship to all versions continuously and do not create a new version.
- **Selection:** clients send `Ledgerbird-Version: 2027-03-10` on a request.
  - Without the header, the request uses the account's pinned version.
  - An account's pin is set to the latest version at its first live API call.
  - The header overrides the pin for a single request, so integrators can test a new version before moving.
- **Baseline:** the API as it exists today is version `<DATE-OF-LAST-BREAKING-CHANGE>`. Every existing integrator is pinned to it unless they have already moved.
- **Introspection:** every response includes `Ledgerbird-Version` with the version actually applied.
- **Upgrading is the integrator's action.** Integrators move their pin in the dashboard or via a support request. We never move a pin without notice, except at sunset (section 5).

## 3. What counts as breaking

**Breaking (requires a new dated version):**

- Removing or renaming an endpoint, field, query parameter, header, enum value, or webhook event.
- Changing a field's type, format, units, precision, or nullability.
- Making an optional request parameter required, or tightening validation so previously valid requests fail.
- Changing the meaning of existing values, such as reconciliation status semantics or matching rules that alter results for the same input.
- Changing authentication, authorization scopes, rate limits below published values, pagination behavior, or error codes that clients branch on.
- Changing idempotency or ordering guarantees.

**Non-breaking (ships to all versions, no notice period):**

- New endpoints, optional request parameters, response fields, webhook events, or enum values.
- Bug fixes that bring behavior in line with published documentation.
- Performance improvements and new error detail text.

**Consumer obligation, stated in the docs:** clients must ignore unknown response fields and handle unknown enum values gracefully. Without this rule, "non-breaking" is meaningless.

**Tie-breaker:** if reasonable people on the platform team disagree, treat the change as breaking.

## 4. Support window

- A version is supported for at least **18 months after the next version is released**. That is the sunset date.
- At our current cadence this means two live versions at a time, three at most. That is the cap the platform team must be able to sustain.
- We will not release a new breaking version while more than **3 versions** are live. If that would happen, the oldest version's sunset is the gating item, not the new release.
- During the support window, a version receives security fixes and critical bug fixes. It receives no new features.

## 5. Notice and deprecation terms

| Event | Minimum notice |
|---|---|
| New version announced (changes and migration guide published) | At least **90 days before GA** |
| Version deprecated (successor is GA) | Same day as successor GA |
| Version sunset (turned off) | At least **18 months after successor GA**, with reminders at 12, 6, 3, and 1 month |
| Endpoint or field removal within a version | Not allowed. Removals ship only in a new version |

**How we notify:**

1. Email to each integrator's named technical contact. Each notice states which pinned version they are on, what changes, and the date.
2. Public changelog and migration guide, one per version.
3. `Deprecation` and `Sunset` response headers on every response from a deprecated version (RFC 9745 and RFC 8594).
4. For the final 90 days before sunset, a named Ledgerbird contact reaches out directly to any integrator still pinned to the sunsetting version.

**At sunset:**

- Requests on the sunset version return `410 Gone` with a link to the migration guide. We do not silently upgrade pins, because that is a breaking change for the integrator.
- We may run short scheduled brownouts (up to 1 hour, announced 14 days ahead) in the last 60 days. Brownouts apply to integrators with significant remaining traffic on the version.

**Contracts take precedence.** If any signed contract promises longer notice or a longer support window, the contract wins. Legal and the platform team must verify the 40 contracts against this policy before publication. Any contract that promises "no breaking changes" or a fixed API version needs a separate decision.

## 6. Exceptions

We may shorten notice only for:

- **Security vulnerabilities** that cannot be fixed without a breaking change.
- **Legal or regulatory requirements** with a compliance date inside the notice period.

An exception requires CTO sign-off and notification to every affected contact within 24 hours. It must be documented in the changelog with the reason. Business convenience is not an exception.

## 7. Process

1. **Before building a breaking change:** the engineer proposes it in a short design note. The note must explain why it cannot be made non-breaking, for example by adding a field instead of changing one.
2. **Batch breaking changes into one version per year, normally.** A single annual cut is easier on integrators and on a 3-person team.
3. **Release checklist:** migration guide, changelog entry, contact emails sent, headers set, per-version usage dashboard live.
4. **Usage tracking:** log API version per account. Without that, we cannot tell whom to email and cannot decide whether a sunset date is safe.
5. **Sunset check:** two weeks before sunset, review remaining traffic by account. If a contracted integrator is still on the version, escalate to the CTO. Do not extend sunsets informally. Extensions are decisions recorded in the changelog.

## 8. First application: the Q1 breaking change

The queued change becomes the first dated version, `2027-0X-XX` (date to be set at GA).

- Announce at least 90 days before GA. If that date has already passed relative to the end-of-Q1 deadline, ship GA at the end of Q1 and treat the first 90 days as an opt-in period: existing pins do not move, and the sunset clock for the baseline starts at GA.
- Existing integrators stay pinned to the baseline. New accounts get the new version.
- The baseline sunsets 18 months after GA.

## 9. Engineering requirements

- Minimum viable build: a version-resolution step at the API edge, one per-account pin column, a per-version usage metric, and the response and deprecation headers. This is intended to be small enough for the platform team, and not a transformation chain.
- Each version's differences are implemented as explicit branching at known seams. The design note for any breaking change must say where the seams are and how they are removed at sunset.
- Version-specific code has a deletion date in the code comments (the sunset date). Removing sunset code is part of the sunset checklist.

## 10. Decisions needed before publication

1. **CTO:** accept the 18-month window in place of "forever". If not, state the maximum number of concurrently supported versions the team can sustain.
2. **Legal:** audit the 40 contracts for notice terms, API stability promises, and any conflict with sections 4 and 5.
3. **Platform:** confirm whether the account pin lives in a column on the existing account table. This is the minimum config surface we need.
4. **Platform:** confirm the date of the last shipped breaking change, which becomes the baseline version.
5. **Product:** confirm that the Q1 change cannot be made additive. If it can, it needs no version at all.