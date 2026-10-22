# Velodrome Systems API versioning policy: version scheme section

I followed the `api-versioning-policy` skill and its three references. The skill asks for a one-question-at-a-time interview first. Your request needs one deliverable in one response, so I made the assumptions below explicit instead. Please correct any that are wrong.

**Assumptions to confirm:**
- The API is public REST with a `YYYY-MM` request header, and some consumers are mobile apps or enterprises. If so, the notice window is 24 months. If not, it is 12.
- "New API keys default to 2024-03" means a key is pinned to a version when it is created. I assumed the pin comes from the dashboard default, not from the account.
- You have not yet published a firm sunset date for 2024-03. If you have, tell me the date and I'll check it against the windows below.
- You have shipped fewer than about 2 breaking changes per year. More than that means the scheme or the compatibility discipline needs review, not just this section.

## Verdicts on your three questions

| # | Your current practice | Verdict | Required change |
|---|---|---|---|
| 1 | No header gets the latest version | ❌ Drop it | No header returns an error. Retire the old behavior through a staged window. |
| 2 | 2024-03 is deprecated but still the default for docs and new keys | ❌ Fix now | Move both defaults to the current version immediately. Existing keys do not move. |
| 3 | SDK 4.x speaks API 2025-04 and 5.x speaks the next version | ⚠️ Keep the mapping, drop the coupled numbering | SDKs use plain SemVer. Each release declares which API version it targets. |

**1. No header gets "latest".** It looks developer-friendly, but every new release silently changes behavior for every caller who omits the header. Those callers get a breaking change without ever choosing it.

The skill's rule is that unversioned access is never served as a fallback. Discord allowed it, and developers named it the anti-pattern. LinkedIn's choice is safer: a required version can never drift under a caller. Removing the fallback later is itself a breaking change, so it needs a notice window like any other.

**2. A deprecated version that is also the default.** This is the first named failure mode in the skill. Discord served v6 as both for about 1.5 years, then jumped the default to v10. The jump hurt callers who relied on the default.

Your risk reasoning is backwards. Changing the default only affects new keys and the docs, never existing integrations, so it is the safe move. Leaving it unchanged is what hurts you. Every new integrator starts on a version you have told them is dying, and each day adds another consumer you must migrate later.

**3. SDK numbers that track the API.** Stripe is the standard example of the opposite design: a date-versioned API next to SemVer SDKs. Its SDK major-bump trigger is stricter than its API rule, because a compiled library breaks in ways a tolerant HTTP caller does not.

Tying SDK majors to API versions would cause three problems:
- An SDK-only breaking change, such as a renamed method, would force a major bump with no API change. The label "5.x = next API" would then be false.
- An API-only change would force an SDK major even when the SDK surface is unchanged.
- Your cap of 2-3 live API versions would silently cap your supported SDK majors too.

Marketing still gets a simple story from a compatibility table instead. See § SDK relationship below.

---

## Version scheme (draft policy text)

### Scope

- Covered: the Velodrome logistics REST API, including webhook event schemas.
- Client SDKs are versioned separately under SemVer. Their policy is out of scope here, except for the compatibility statement in § SDK relationship.
- Not covered: [list any unversioned admin or beta endpoints that "may change at any time"]. State the carve-out up front or delete this line.

### Scheme

- **Mechanism:** the `Velodrome-Version: YYYY-MM` request header. Each version is identified by its release month.
- **Release cadence:** [as-needed | quarterly]. Pick one and publish it. A new version ships only when a breaking change ships. Non-breaking changes go into existing versions.
- **Concurrent versions:** at most 3 are supported at once. A new release that would exceed the cap triggers the deprecation of the oldest version.
- **Support window:** each version is supported for at least **24 months** [12 if the audience assumption above is wrong]. The clock starts when the **next** version is released, not when the version itself ships. Dates published in this policy are commitments and are not extended.

### Default when no version is given

- A request **without the version header returns `400`** with a descriptive error. The body names the header, lists the supported versions, and links to the migration guide.
- **Unversioned access is never served.** No request is ever resolved to "latest".
- A key's creation-time pin is stored on the key, so it never changes silently. The key's own pin, not an account or global setting, is what resolves a request.
- **New keys and the interactive docs always default to the current version.** A deprecated version is never offered as a default. Callers can still select a supported older version explicitly.

### Transition for existing behavior

Both changes below follow the standard stages: announce, deprecate, sunset, removal. Neither goes directly from announcement to removal.

**A. Retiring the "no header means latest" behavior** (a breaking change, so it needs the full window):
1. **Now:** announce the change in the changelog, the dashboard, and by email to the accounts that actually send header-less requests. Your logs identify them.
2. **Freeze immediately:** header-less requests resolve to the version that is current on the freeze date, and stay there. This stops the silent drift without breaking anyone.
3. **From the announcement:** responses to header-less requests carry a `Deprecation` header (RFC 9745) and a `Warning`-style message in the response payload. Add `Sunset` (RFC 8594) once the date is firm.
4. **At the sunset date:** header-less requests return `400`. Run a grace period of at least 30 days at the same status, then remove the fallback code.

**B. Retiring 2024-03:**
1. **Today:** move the interactive docs default and the new-key default to the current version. Existing keys keep their pin.
2. **Publish a firm sunset date** for 2024-03. If you promised no date at deprecation time, count the window from the date you publish, not from eight months ago. Date integrity matters more than shaving months.
3. **Attach the signals:** `Deprecation` header, `Sunset` header once the date is firm, `Link: rel="successor-version"`, and `deprecated: true` in the OpenAPI document. Headers alone reach almost no one, so also send targeted email and an in-response warning to accounts still calling 2024-03.
4. **Own the migration:** publish a migration guide with concrete steps and a support channel. Measure completion by traffic share, not by calendar.
5. **At sunset:** hard cutoff. Retired versions return `410 Gone` with a descriptive body and a successor link. Do not use fall-forward. Meta's fall-forward is the standing example of silent behavior drift that is documented but not noticed.

### SDK relationship

- SDKs follow plain SemVer, independent of the API's `YYYY-MM` versions.
- Every SDK release declares the API version it sends by default and the range of versions it supports. This is published in the README, the changelog, and a compatibility table, for example:

| SDK | Default API version | Supported API versions |
|---|---|---|
| 4.x | 2025-04 | 2025-04 only |
| 5.x | [next version] | [list] |

- Marketing keeps its simple story: "SDK 4.x speaks API 2025-04." The mapping is a documented property of each release. It is not encoded in the version number.
- An SDK major bump is triggered by a break in the SDK's own compiled surface, as in Stripe's rule. It is not triggered by an API release.

### Governance for this section

- An OpenAPI diff tool (such as oasdiff) runs in CI on every spec change and flags breaking changes mechanically.
- A named staff engineer signs off on anything flagged. No breaking change ships without that approval, including business-motivated ones.
- Changing a default (for keys, docs, or header-less requests) counts as a breaking-change-adjacent event and goes through the same sign-off.

### Measurement

- Breaking changes per year. The target is no more than 2.
- 2024-03 traffic share and header-less traffic share, reviewed monthly during the deprecation. A flat line after an email wave means that channel failed.
- Slipped sunset dates. The target is zero.

## Open questions

1. Is your audience public, with mobile or enterprise consumers? This decides 12 versus 24 months.
2. Do you have a published sunset date for 2024-03? If so, what is it?
3. What release cadence do you want: as-needed or quarterly?
4. How many breaking changes did you ship in the past year?

I haven't drafted the remaining policy sections (breaking-change definition, windows detail, enforcement, exceptions). The skill validates each one with you before the next, so tell me which to write next.