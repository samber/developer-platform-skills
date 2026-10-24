# Verdict: build the opt-in header, but change the other two parts

**Don't build the plan as written.** The header is fine. Putting beta operations in the main OpenAPI file with stable-only SDK releases is the real problem. The Beta note on the overview page is too weak to do its job.

## 1. Main OpenAPI file plus stable-only releases (biggest risk)

- Anything in the main spec ships to every SDK user in a stable release, and you can't unpublish from npm or PyPI.
- `usage.forecast` would become a typed field on the stable `Usage` model. Once its shape changes, as the argument suggests it will, that is a breaking change in a stable SDK.
- Timing may not work anyway. If the next regular release lands after next week, your 6 SDK accounts can't use the beta at enrollment.

**Do this instead:**
1. Keep beta operations out of the main spec. Use a separate beta spec or overlay, or tag operations `x-beta` and have the generator exclude them by default.
2. For the 6 SDK accounts, don't depend on a release. Give them a pinned beta build installed from a Git tag or a private index. A beta package with its own stable-looking version also works if you don't want prerelease tags. The other option is a documented raw-request path, such as the SDK's custom-header support plus its generic `request` method.
3. Move beta features into the main spec only at graduation, in a dated version, with a changelog entry.

## 2. One header for everything

- Alerts is a new additive surface and forecast is an unstable shape. Switching both on together means you can't graduate or break one without the other. Accounts that only want alerts also get forecast churn.
- Keep the comma-list format, since it's already per feature, but make each token an opt-in on its own and version it, for example `forecast-v0`. A reshaped forecast then becomes `forecast-v1`, and enrolled clients aren't broken silently.
- Echo what was honored in a response header, for example `Meterline-Beta-Active: forecast-v0`. Otherwise a typo is silently ignored and the client sees nothing.
- Add `Vary: X-Meterline-Beta` for caches and proxies, and allow the header in CORS.
- State how beta relates to `Meterline-Version`. Suggested rule: a beta is evaluated against the pinned date version, and beta shapes may change with notice until graduation.

## 3. A request header can't gate webhooks

Alert deliveries are outbound, so there is no request to carry the header. Gate alerts at creation: the API that creates alert rules or webhook endpoints requires the header. Pin the payload version on the endpoint, so a later reshaping doesn't hit receivers unannounced. Deliver only the event types the endpoint subscribed to.

## 4. The header alone doesn't enroll anyone

Anyone who reads the docs can send it. You then have more than 8 users and a bigger compatibility promise, and you can't tell the enrolled accounts when something changes. Use a server-side per-account allowlist as eligibility, with the header as the client's pin. Return a clear `403 beta_not_enabled` for non-enrolled accounts. Log beta usage per account so you know whom to warn.

## 5. The Beta note belongs on every beta page, with a contract

Readers land on reference pages from search and LLMs, not the overview.

- Put a "Beta" badge and banner on each affected operation and schema, driven by `x-beta` so it can't drift.
- Publish a short stability contract: what may change, the notice period, support level, "not for production-critical paths", and the graduation or sunset criteria.
- Link to how to request access.

## Check before enrolling (about a day of work)

1. Do both generated SDKs set custom default headers? Test the exact call the 6 accounts will make.
2. Does the Python SDK fail on unknown response fields? Pydantic models with `extra=forbid` would break on `usage.forecast`. Test against a real beta response.
3. When is the next regular SDK release? If it's after next week, the pinned beta build is mandatory.
4. Beta exit criteria: what decides forecast's shape, and by when?

## Order of work

1. Server: per-token flags, the allowlist, the echo header, and `Vary`.
2. Separate beta spec and pinned SDK build.
3. Operation-level docs and the stability contract.
4. Enroll the 2 non-SDK accounts first as a smoke test, then the 6 SDK accounts.

Say which of the four checks you can answer now. I can turn this into a build plan from there.