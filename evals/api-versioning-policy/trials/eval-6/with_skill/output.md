# Ruling on the two disputes, and the breaking-change section of the Bramblewick API policy

I read the `api-versioning-policy` skill and its references and followed its breaking-change rules (step 2). I skipped its interview and section-by-section validation because you asked for one deliverable. The assumptions that could change the rulings are listed at the end. Treat the policy as a draft until you approve it.

## Rulings

### Dispute 1: `contractor` enum value and `benefits_class` field

**Neither change needs a /v3. Marcus is right on the outcome. Priya is right about a risk Marcus skipped.**

- **`benefits_class` on the employee response.** This is a new response property, which is explicitly non-breaking. It ships into the current version.
  - It would be breaking only if you made it a required request parameter, or if clients reject unknown fields. The second case is the client's bug, and the policy says so.
- **`contractor` in `employment_type`.**
  - Adding a value is not on the breaking list. Removing a value is.
  - It is safe only if the enum is declared open. A client with an exhaustive switch over `full_time`, `part_time` and so on will fail on a value it has never seen. If you never told clients that could happen, that failure is a legitimate complaint.
  - **Rule:** declare `employment_type` an open enum in the published policy, then ship the value. The declaration comes first. Don't emit `contractor` in responses until it has been published for a notice period. I suggest 30 days, which is my number, not the skill's.
  - Accepting `contractor` on writes carries no such risk.

### Dispute 2: renaming `dept` to `department`

**Marcus cannot just ship it. "The old name was ugly" is not a criterion.**

- The skill's test is whether any change makes a previously working client fail. A client sending `?dept=engineering` stops working the moment the name disappears.
  - It either gets an error, or the filter is silently ignored and the client receives every employee. The second outcome is worse.
  - Renaming a field or endpoint is on the breaking list, and a renamed query parameter is the same operation.
- **What Marcus can do now:**
  1. Add `department` as a new optional parameter. That is non-breaking and ships today.
  2. Keep `dept` working as an alias.
  3. Mark `dept` deprecated with the `Deprecation` header and an OpenAPI `deprecated: true` entry.
  4. Remove `dept` only in the next major version, after the notice window.
- Don't cut a major version for one ugly name. Batch it with other breaking changes. If you need more than about two breaking changes a year, your compatibility discipline is the problem.

### Security patches: your security lead is wrong to leave them out

"Everyone understands" is not a policy.

- Without a written exception, the policy promises that a supported version doesn't change for [24] months. The first CVE fix that alters behavior is then a breach of your own promise, and a customer can say so.
- LinkedIn's policy reserves the right to patch any version "for any critical security, privacy issues, or bug fixes." The skill's rule is: write the exception down, narrowly, and never invoke an unwritten one.
- The security lead's instinct to patch any version is right. It belongs in the policy, with limits and a notice duty, so it can't grow into a loophole.

## Policy section: Breaking changes

```markdown
## Breaking-change definition

### Test

A change is breaking if a client that worked before the change can fail after it,
while using the API as documented. This test settles disputes. Opinion about naming,
taste or effort does not.

### Breaking changes (require a new major version)

- Removing or renaming an endpoint, a response field, a request field or a query parameter.
- Changing a field's type, format constraints or meaning.
- Removing an enum value.
- Adding a required request parameter or making an optional one required.
- Changing the status code or content type for the same scenario.
- Changing the default value of a parameter, including filters and pagination.
- Tightening validation so previously accepted requests are rejected.

### Non-breaking changes (ship into the current version, no new version)

- Adding resources or endpoints.
- Adding optional request parameters, including a new name for an existing one while
  the old name keeps working.
- Adding response properties.
- Changing property order.
- Changing the length or format of opaque strings, including ID prefixes.
- Adding webhook event types.
- Adding values to an open enum (below).

Clients MUST ignore unknown response properties and handle unknown values of open enums.

### Open enums

These enum fields may gain new values without a version bump:

- `employment_type`
- [list every other open enum]

Every enum not listed is closed. Adding a value to a closed enum is breaking.
We publish a new value in the changelog at least [30 days] before the API first returns it.

### Not contractual (may change without notice)

- Error message and detail text. Match on error codes.
- Ordering of array results when no sort is requested.
- Response timing and rate-limit headroom.
- [other items]

### Deprecation of a renamed element

When we rename an element, we add the new name and keep the old name working.
The old name is deprecated, not removed. It is removed only in the next major
version, after the notice window in "Support windows."
Deprecated elements carry the `Deprecation` header (RFC 9745) and `deprecated: true`
in the OpenAPI document.

### Security, privacy and bug-fix exception

We may change any supported version, with no major version, to fix a critical
security or privacy issue. We may also fix a bug that makes the API behave
differently from its documentation. In every case:

- The change is the smallest one that closes the problem.
- We announce it via [changelog + email to affected accounts] at the time it ships,
  or as soon as disclosure is safe.
- It does not restart or shorten any published sunset date.

This exception covers no other kind of change. Product, pricing or business reasons
never qualify.

### Governance

- Every spec change runs through [oasdiff / Spectral] in CI, which flags breaking
  changes mechanically.
- No breaking change ships without sign-off from [named staff engineer].
- Disputes over whether a change is breaking go to that approver, who applies the
  test above. The ruling is recorded in the changelog.
- Target: at most [2] breaking changes per year. A higher rate triggers a review of
  this policy.
```

## Assumptions to confirm

I couldn't ask the interview questions, so these are guesses.

1. **Scheme.** I assumed URI major versions (`/v1`, `/v2`), since you mention `/v3`. If you use headers or dates, the "new major version" wording changes.
2. **Audience.** I assumed a fully public API with enterprise consumers such as payroll and HRIS integrations. That puts the support window at 24 months rather than 12. Confirm it.
3. **`employment_type` state.** If the enum was never documented as open, existing clients are entitled to assume it is closed. That is why the declaration comes before the value.
4. **Windows and clock.** The policy section above covers only breaking changes, so the "Support windows" numbers and clock definition still need to be written.