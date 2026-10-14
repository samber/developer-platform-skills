# Versioning policy: scheme section

## Review of your three decisions

| # | Current choice | Verdict |
|---|---|---|
| 1 | Header-less requests get the latest version | ❌ Change. It's friendly for the first call and hostile in production. |
| 2 | Deprecated 2024-03 is still the default for docs and new keys | ❌ Change. Your policy contradicts itself, and the migration risk is smaller than it feels. |
| 3 | SDK major version equals API version | ⚠️ Keep the simple story, but not as an identity rule. |

**1. Latest by default.** Any client that omits the header silently changes behavior on every release you ship. That includes cron jobs, old scripts, and integrations nobody has touched in a year. Your breaking-change policy is only as strong as its weakest default. "Latest" is also a moving target no one can test against. The fix is to pin on first use, so a request without the header gets the version its API key is pinned to.

**2. Deprecated version as the default.** You are onboarding every new customer onto a version you've told people to leave, so migration debt grows daily. Eight months in with no sunset date means "deprecated" has no teeth. Changing the default for new keys and for the docs affects no existing integration, because existing keys keep their pins. The mid-year risk applies only to changing existing keys, and this policy never does that.

**3. SDK tracks API.** Pinning an SDK to one API version is legitimate, since typed response models change when the API version changes. But making SDK majors mirror API versions has three costs:
- SDK-only breaking changes (dropping a runtime, renaming a method) have no version number to land in.
- Customers must take an SDK major to adopt a new API version, even when they would be fine without it.
- If the cadences differ, one of the two numbering schemes gets distorted.

The better rule is that the SDK major changes whenever its default API version changes. It can also change for other breaking reasons. Publish the mapping as a table. Marketing keeps "4.x speaks 2025-04", and engineering keeps the freedom to ship 6.x without a new API version.

**⚠️ Needs your confirmation.** Your points 1 and 2 conflict. Header-less requests get "latest", yet new keys default to 2024-03. I've assumed the key's default is a pin that overrides "latest". Tell me if existing header-less traffic really floats on latest today, because those accounts then need a one-time grandfathering step (see Migration).

---

## Versioning policy: scheme

### 1. Version identifier
- A version is a calendar month, `YYYY-MM`, sent in the `API-Version` header. (Substitute your actual header name.)
- A new version is cut only for **breaking** changes: removed or renamed fields, changed types or semantics, new required parameters, changed error codes, or stricter validation.
- **Additive** changes (new optional fields, new endpoints, new enum values documented as open) ship to all supported versions without a new version.
- Each version is immutable once released. Bug fixes and security patches are backported, but behavior is never changed.

### 2. Version resolution
Apply these steps in order:
1. If the request carries an `API-Version` header with a supported version, serve that version.
2. Otherwise, serve the version **pinned to the API key**.
3. If the header names an unknown or sunset version, return `400` with an error body listing the supported versions. Never fall back silently.

Every response echoes the resolved version in `API-Version`. Requests resolved through the key pin also carry `API-Version-Source: key-default`, so developers can see when they are relying on it.

**No request resolves to "latest" implicitly.** Latest is available only by sending its explicit identifier.

### 3. Key pinning
- A new key is pinned at creation to the **current version**, the newest generally available one.
- A pin never changes unless the key owner changes it in the dashboard or API.
- The key owner may override the pin per request with the header. Upgrading means testing with the header, then moving the pin.
- Changing the default for newly created keys never affects existing keys.

### 4. Lifecycle

| State | Meaning | Rules |
|---|---|---|
| **Current** | Newest GA version | Default for new keys and docs |
| **Supported** | Older, fully maintained | Fixes and security patches backported |
| **Deprecated** | Sunset date announced | Cannot be the default for new keys or docs. Responses carry `Deprecation` and `Sunset` headers. Direct emails go to affected key owners. |
| **Sunset** | Removed | Requests return `410` with a migration link |

- Minimum window from deprecation notice to sunset: **[12 months, decide]**.
- **Every deprecation announcement must include a sunset date.** A deprecated version without one is a policy violation.
- Run brownouts (short scheduled `410` windows) at 90, 30, and 7 days before sunset. Announce them in advance.
- Keep the number of simultaneously supported versions below **[N, decide]**. Without a cap, the maintenance cost is unbounded.

### 5. Documentation and tooling defaults
- Docs, the interactive console, code samples, and generated snippets default to the **current** version.
- A visible version switcher lets readers view older versions. Pages for deprecated versions show a banner.
- The interactive console sends the version header explicitly and displays it.

### 6. SDK relationship
- SDKs follow their own semantic versioning, independent of API versions.
- Each SDK release pins a **default API version** and sends it explicitly on every request. SDK users therefore never depend on key pins.
- **The SDK major version increments whenever its default API version changes.** It may also increment for other breaking SDK changes.
- Publish a compatibility table. Several SDK majors may map to the same API version.

| SDK | Default API version |
|---|---|
| 4.x | 2025-04 |
| 5.x | [next version, when released] |

- Users may override the version per client instance. The SDK warns when the override differs from its typed models' version.

### 7. Migration (one-time, for this policy's rollout)
1. Switch the default for **new** keys and the docs to the current version. This affects no existing customer.
2. Announce the 2024-03 sunset date now. Count the window from this announcement, not from the original deprecation.
3. Pin every existing key to the version it effectively uses today. For keys that send no header, that is whatever "latest" resolves to now. Do this before turning off implicit latest, so nobody's behavior changes.
4. Disable implicit-latest resolution. From then on, resolution follows section 2.
5. Email owners of keys still pinned to 2024-03 at 12 months, 6 months, and 90 days before sunset.

### Open decisions for you
- Header name.
- Sunset window length (section 4).
- Maximum number of concurrently supported versions.
- Which version is "current" today (I used 2025-04 per your SDK mapping).
- The sunset date for 2024-03.