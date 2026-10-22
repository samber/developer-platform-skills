# Ruling and breaking-change policy

I didn't see your current API docs or any existing policy text, so the rulings assume the policy has never told clients to tolerate unknown enum values. If it already does, tell me, because that changes Dispute 1.

## Rulings

| Dispute | Ruling |
|---|---|
| Add `contractor` to `employment_type` | **Priya is right.** It is breaking for responses. |
| Add `benefits_class` to the employee response | **Marcus is right.** It is additive and non-breaking. |
| Rename `dept` to `department` and ship it | **Marcus is wrong.** It is breaking, and "the old name was ugly" is not a criterion. |
| Leave security patches out of the policy | **Security lead is wrong.** The policy must state them. |

### Dispute 1

**`contractor` enum value:**
- Clients that switch exhaustively on `employment_type` will crash or misroute on a value they've never seen. Generated clients with strict enums will fail deserialization.
- Those clients were built against a spec that listed the old values and never told them to expect more. The break is real even though no field was removed.

**Does it need `/v3`?** No. Priya is right about the break, but a break doesn't automatically mean a new major version. The options, in order of preference:
1. Ship `contractor` only to clients that opt in. Use an account-level flag or a version header, whichever you already have.
2. Batch it into the next major version.
3. Don't map contractors onto an existing value such as `part_time`. That corrupts data for every client.

**`benefits_class`:**
- Adding a response field is non-breaking. It ships now, without opt-in, even while `contractor` is gated.
- It must be documented as nullable if existing employees may lack a value.
- It becomes breaking only if you make it required on requests.

### Dispute 2

Renaming `dept` is breaking, and the failure is worse than an error. Most frameworks ignore unknown query parameters. A client sending `?dept=sales` after the rename would get the unfiltered employee list with a 200. In an HR API that is a data-exposure bug, not a cosmetic change.

**Correct path:**
1. Add `department` as an alias.
2. Keep `dept` working and mark it deprecated in the spec.
3. Send `Deprecation` and `Sunset` headers on responses to calls that use `dept`.
4. Remove `dept` only in the next major version, after the notice period.

If a request sends both and the values differ, return 400.

### Security patches

"Everyone understands" isn't true, because the unwritten questions have real answers:
- **Can a security fix break compatibility?** Sometimes it must. Examples are tightening validation or removing an unsafe parameter. Without an explicit exception, the compatibility promise forbids the fix, or engineers argue about it during an incident.
- **Which versions get patched?** "Any version" is unbounded. Does a sunset `/v1` get a patch? Customers and auditors will ask, and the answer has to be written down.

The section below answers both. The security lead should confirm the support window.

## Policy section: Breaking changes

### 1. Definition
A change is **breaking** if a correct client built against the published spec can fail or silently misbehave after it. When in doubt, treat it as breaking.

### 2. Non-breaking changes
These ship in any release, with a changelog entry:
- Adding an optional request parameter or field.
- Adding a response field.
- Adding a new endpoint.
- Adding a value to a request-side enum.
- Adding a value to a response enum declared **open** (see §4).
- Making validation more permissive.

### 3. Breaking changes
These require a new major version, or an opt-in mechanism plus the deprecation process (§5):
- Removing or renaming any endpoint, parameter, field, header, or enum value.
- Changing a field's type, format, nullability, or meaning.
- Adding a required request parameter or field.
- Adding a value to a response enum that is not declared open.
- Tightening validation or authorization on existing inputs.
- Changing the default value, sort order, or pagination behavior.
- Changing error codes or response shape.

A renamed parameter counts as a removal. The old name must keep working through the deprecation period.

### 4. Client obligations
These bind clients, and the API reference must state them:
- Ignore unknown response fields.
- Tolerate unknown values in any response enum marked `open`.

Every response enum created after [DATE] is open. Enums that exist today are closed. Adding a value to one is breaking until we publish [NOTICE PERIOD] notice that it is now open.

### 5. Deprecation process
1. Announce in the changelog and the developer newsletter, and mark the item deprecated in the spec.
2. Send `Deprecation` and `Sunset` headers on affected responses.
3. Keep the deprecated behavior working for at least **[12 months]** after announcement.
4. Email the owners of accounts still using it at 90 days and 30 days before removal.
5. Remove only in a major version.

### 6. Opt-in releases
A breaking addition that doesn't justify a new major version, such as a new response enum value, ships behind an explicit opt-in. Clients who haven't opted in see the old behavior.

### 7. Security exception
- Security fixes are exempt from the notice period in §5 and may ship as breaking changes.
- We give as much notice as the vulnerability allows. We state the change and its reason in the changelog once disclosure is safe.
- We backport security fixes to **every supported version**. A version is supported until **[12 months]** after its successor reaches general availability.
- Sunset versions get no patch commitment. Customers on them are told to migrate.
- A critical CVE in a sunset version may still be patched at our discretion. This is never a guarantee.

### 8. Ownership and ties
- An engineer proposing a change classifies it using §2 and §3 in the PR description.
- Disagreements go to the API owner, **[NAME/ROLE]**, who decides within two business days.
- The decision and its reasoning are recorded in the PR.

**Placeholders for you to set:** `[DATE]`, `[NOTICE PERIOD]`, both `[12 months]` values, and `[NAME/ROLE]`. The 12-month windows are my default for a public HR API. Enterprise customers may expect more.