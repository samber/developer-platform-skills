# Plan check: corvane-action 2.4.0 is not a minor

**Verdict: do not cut this as 2.4.0 and move `v2`.** Five of the seven items are breaking changes under the skill's contract rules. The plan would push them to about 900 repos on `@v2` with no edit on their side.

## Item by item

| # | Change | Class | Why |
| --- | --- | --- | --- |
| 1 | Rename `api_key` to `api-key` | ❌ major as written | Every `@v2` workflow still sends `api_key`. The action ignores it and runs with no key. |
| 2 | `severity-threshold` default `high` to `medium` | ❌ major | Pinned workflows change behaviour with no edit. More findings also means more failures once item 3 lands. |
| 3 | `license-findings` goes from warn to fail | ❌ major | Green pipelines turn red with no change on the customer side. |
| 4 | `runs.using: node24` | ❌ major | It raises the runtime floor. GHES and old self-hosted runners fail. Checkout v5, auth v3, build-push v7, configure-aws v6 and codecov v6 all shipped it as a major. |
| 5 | CLI 4.x to 5.0 | ⚠️ major unless proven otherwise | The action's contract includes what the CLI does. "We never call `--format table`" only covers flags you pass. See the questions below. |
| 6 | Drop the `verbose` input | ❌ major | Removing an input is a major. "Nobody sets it" is a claim to verify (see below). |
| 7 | New `output-file` input, default empty | ✅ minor | It adds an optional input and keeps the old behaviour. |

Items 2, 3 and 4 combine badly. A customer on a self-hosted runner without Node 24 breaks on the runtime. Everyone else gets a lower threshold and a hard failure on licence findings.

## Why moving `v2` is the wrong delivery

- `v2` is a plain tag with no GitHub release. Moving it pushes all of this to every floating pinner at once.
- SHA pinners, lockfile users and Dependabot users never see a moved `v2`. They only follow new `vX.Y.Z` tags. Your bundle splits into people who break silently and people who never get the fix.
- Node 20 was removed on 2026-09-23. Your action already runs on Node 24 with a job warning. That helps the "deprecation banners" complaint, but it doesn't make the explicit `node24` change safe. The floor still excludes GHES and old runners.

## Recommended plan

You have two options. Both keep `v2` safe.

**Option A (simplest): ship the whole changelog as `v3.0.0` on Thursday.**
- The changelog is a coherent major. Renaming it costs nothing.
- Create a new `v3` tag. Leave `v2` where it is, at the last 2.x release.
- Write a migration guide: old input to new, default changes, the licence failure, the runner floor, the CLI bump.
- Keep patching `v2` while customers on GHES or old runners can't run Node 24.

**Option B: ship a safe 2.4.0 Thursday, and the breaking set later as 3.0.0.**

2.4.0 contains only these changes:
1. Add `api-key`. Keep `api_key` working as an alias with `deprecationMessage: "api_key is deprecated; use api-key. Removed in v3."`. Prefer the new name when both are set, and mask both.
2. Add `output-file`, default empty.
3. Keep `verbose` accepted, with a `deprecationMessage` and no effect. This also collects real usage evidence.
4. Add opt-in inputs for the new behaviour. `fail-on-license-findings` defaults to `false`. `severity-threshold` keeps `high`, and `medium` is accepted as a value.
5. Stay on `node20` and on CLI 4.x. Take only CLI 4.x patches.

3.0.0 then holds: `node24`, default `medium`, licence failure by default (with the `fail-on-license-findings: false` downgrade), removal of `api_key` and `verbose`, and CLI 5.0.

I'd pick A if Thursday is a hard date and the migration guide can be ready. Pick B if the three customers asking for kebab-case can't wait.

## Questions that change the plan

1. **CLI 5.0:** does the action pass through user arguments, expose a `format` input, or parse CLI output or exit codes? Does 5.0 change SARIF or JSON output, exit codes, or finding IDs? If any answer is yes, the bump is breaking regardless of `--format table`.
2. **`verbose` telemetry:** does it come from the action's `User-Agent` or deprecated-input flag, or from CLI telemetry? Runs that fail before reaching the API wouldn't show up. A flag-based count over a full release cycle is the evidence you need.
3. **GHES and runners:** which GHES releases do customers run, and do they ship a Node 24-capable runner (v2.328.0 or later)? That sets the floor you document for v3.
4. **Auth:** does the backend accept OIDC yet? If it does, add an `auth` input (`auto`, `oidc`, `key`) with the same release, so OIDC later is a minor.

## Release mechanics, whichever option you pick

1. Gate checks, all green:
   - contract diff against `v2.3.1` (clean for 2.4.0, or a major);
   - check-dist;
   - integration matrix on every README OS, the oldest supported self-hosted runner, and GHES, against a real sandbox account;
   - zizmor at medium or above, plus actionlint;
   - every nested `uses:` SHA-pinned and every downloaded binary verified.
2. Create an immutable GitHub release `vX.Y.Z` from a protected environment, with attested `dist/`.
3. Release notes state the full commit SHA and the line `uses: corvane/corvane-action@<sha> # vX.Y.Z`. They also list deprecations with their removal major and the minimum runner version.
4. Move only the matching major tag, after the release exists. Push it as `refs/tags/vX`, one tag at a time, never `--tags`.
5. Keep major tags release-free. A `v2` that carries a release can't be moved once immutable releases are on.
6. Add a contract check to CI that fails on any input or output removal or rename outside a major branch. It would have caught items 1 and 6.

Three items in the changelog are good and just need to go in a major, or behind aliases and opt-ins: the kebab-case rename, the Node 24 move, and the dropped `verbose` input.