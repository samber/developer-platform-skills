**Don't ship the one-liner.** It sets a single number for two audiences, and it leaves the clock undefined. The draft below fixes both. The skill requires an interview and your sign-off before a policy is final, and I couldn't run the interview here. So this is a ready-to-approve draft with my assumptions marked, not a final policy.

## Problems with the one-liner

1. **6 months is far below the benchmarks for your public audience.**
   - Published floors for public APIs are at least 12 months (Google Cloud, Shopify).
   - Microsoft Graph, Meta, and GitHub give at least 24 months.
   - Your ~200 apps are public, self-serve, and embedded in iOS and Android apps. You can't list or contact them all. App-store release cycles and users who never update make them the slowest group to migrate. The skill's rule for mobile consumers is at least 24 months.
2. **The competitor's 3 months isn't a benchmark.** Being "twice as generous" as one provider doesn't tell you what's safe for your consumers. Twitter/X gave about 7 days' notice in 2023 and broke integrators who were willing to pay. Use the 12–24 month floors as your reference, and treat the 3-month competitor as a selling point you can beat.
3. **Internal services don't need a notice period.** The 9 services have owners you can reach. Use coordinated deploys and consumer-driven contract tests instead. A calendar window would slow your own teams down and protect no one.
4. **The clock matters, and "it doesn't really matter" is wrong.** An undefined clock is a named failure mode in the skill.
   - Release-based and announcement-based clocks can differ by years.
   - Meta starts its 2-year guarantee when the next version ships. GitHub's 24 months also runs from a newer version's release.
   - Tell sales the answer is not "either way." Give them the rule below.
5. **The one-liner is missing the rest of the policy.** It has no version scheme, breaking-change definition, communication plan, enforcement at the sunset date, or governance. Without a written breaking-change definition, every dispute becomes a judgment call.

## Candidate policies

| | A. URI major version (recommended) | B. Date-versioned, header, hard 410 | C. Stripe-style account pinning |
|---|---|---|---|
| Scheme | `/v1/`, `/v2/` | `YYYY-MM-DD` header, error if missing | Date versions pinned per account |
| Public window | At least 24 months from deprecation announcement | At least 24 months after the newer version ships | No forced sunset |
| Effort | An afternoon of routing | Medium | Highest: a transformer chain maintained forever |
| Fit | Works with a deadline and a small team | Works if you want calendar cadence | Only if you need breaking changes many times a year |

**Recommendation: A.** URI versioning is the efficient default and needs no header sophistication from 200 third-party developers. Candidate C is overkill unless you expect breaking changes many times a year. Candidate B is a reasonable alternative.

## Draft policy (candidate A)

# Trackpole API versioning and deprecation policy

### Scope
- Covers the versioned REST endpoints [and webhook event schemas, if any].
- Unversioned or experimental endpoints are not covered. List them here [decision: any?].
- Client SDKs version separately under SemVer.

### Version scheme
- The major version is in the URI path (`/v1/…`).
- Unversioned access is never served.
- A version is never both deprecated and the default for new integrators. Promote the successor to default before announcing deprecation of its predecessor.

### Breaking-change definition
- **Breaking (needs a new major version):**
  - removing or renaming a field or endpoint
  - changing a field's type
  - removing an enum value
  - adding a required request parameter
  - changing the status code or content type for the same scenario
- **Non-breaking (ships into the current version):**
  - new resources
  - new optional parameters
  - new response properties
  - property-order changes
  - changes to opaque ID formats
  - new webhook event types
  - new values in enums declared open
  - Declare open enums explicitly [list: e.g. activity type].
- **Not contractual:** error message text, field ordering, timing.
- **Security exception:** any version may be patched for critical security, privacy, or bug fixes, announced via the changelog and email.

### Support windows
| Audience | Rule |
|---|---|
| Public third-party apps | At least 24 months, counted from the **deprecation announcement date**. |
| Internal services | No calendar notice. Removal needs the owning team's contract tests passing on the successor. The platform team owns the migration work. |
| Future partner APIs | Windows go in the contract or SLA. |

- **Clock rule for sales:** the announcement can only happen after the successor is generally available.
- The announcement states an exact sunset date. Support runs until that date.
- The date is a commitment. It does not move.
- At most 2–3 versions are active at once.
- 24 months of support with at most 3 live versions means a new major roughly every 12 months. That is consistent with the health target of at most 2 breaking changes per year.
- "At least 24 months" is a floor.

### Deprecation process
Announce, then deprecate, then sunset, then remove. Never skip from announce to removed.
1. **Announce:** changelog, developer-dashboard banner, and email. The email goes to accounts still calling the version.
2. **Deprecate:**
   - Send the `Deprecation` header (RFC 9745) on every response from the deprecated version.
   - Add the `Sunset` header (RFC 8594) once the date is firm.
   - Add `Link: rel="successor-version"`.
   - Mark `deprecated: true` in the OpenAPI document.
3. **Targeted outreach:** at T-12, T-6, T-3, and T-1 months, email accounts still calling the version. Headers alone don't reach humans.
4. **Migration support:** a migration guide per transition, and a support channel.

### Enforcement at sunset
- Hard cutoff. Retired versions return `410 Gone` with a descriptive body and a successor link.
- The grace period is 30 days of `410 Gone` before full removal.
- No fall-forward. Mobile apps would silently change behavior.

### Governance
- Run oasdiff or Spectral in CI on every spec change.
- Any flagged breaking change needs sign-off from [named engineer].
- Business-driven changes (pricing, monetization) go through the same process.
- Revisit and add a review board once the API outgrows one reviewer.

### Measurement
- Breaking changes per year: at most 2.
- Deprecated-version traffic share, reviewed monthly during any deprecation. Flat traffic after an email wave means that channel failed.
- Remove a version only at zero traffic, or at residue you have explicitly accepted. A date passing proves nothing about migration.
- Slipped sunset dates: 0.

## Assumptions to confirm

- The API is REST only. GraphQL would use field-by-field evolution instead.
- Version scheme A (URI major version).
- No version is currently live and deprecated.
- No hard deadline is forcing a particular scheme.
- A named approver exists for breaking changes.
- You will carry 2–3 concurrent versions of maintenance cost for 24 months.

## Decisions for you

1. If 24 months is too long for your team, name the constraint and we'll weigh 12 months against the mobile guidance. Don't cut to 6 months silently.
2. Do you pick A, B, or C?
3. Which enums are open?
4. Who is the named approver for breaking changes?
5. Are there unversioned or experimental endpoints to carve out?

Once you confirm these, I can mark the policy final. Share the sales answer on the clock now: it is the announcement date, and 24 months is the floor.